#!/usr/bin/env python3
"""Losslessly shrink PNG files in place (standard library only).

Pixel art has few colours, so images with at most 256 distinct RGBA values are
rewritten as indexed PNGs (palette + tRNS); others are re-filtered and
recompressed. Every pixel is checked to round-trip unchanged before a file is
replaced, and a file is only replaced when the result is smaller.

Usage: python3 tools/optimize_png.py FILE_OR_DIR [...]
"""
import struct
import sys
import zlib
from pathlib import Path

SIGNATURE = b"\x89PNG\r\n\x1a\n"


def chunks(data):
    pos = 8
    while pos < len(data):
        length, kind = struct.unpack(">I4s", data[pos:pos + 8])
        yield kind, data[pos + 8:pos + 8 + length]
        pos += 12 + length


def paeth(a, b, c):
    p = a + b - c
    pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
    if pa <= pb and pa <= pc:
        return a
    return b if pb <= pc else c


def unfilter(raw, width, height, bpp):
    stride = width * bpp
    rows, prev, pos = [], bytearray(stride), 0
    for _ in range(height):
        kind = raw[pos]
        line = bytearray(raw[pos + 1:pos + 1 + stride])
        pos += 1 + stride
        for i in range(stride):
            a = line[i - bpp] if i >= bpp else 0
            b = prev[i]
            c = prev[i - bpp] if i >= bpp else 0
            if kind == 1:
                line[i] = (line[i] + a) & 255
            elif kind == 2:
                line[i] = (line[i] + b) & 255
            elif kind == 3:
                line[i] = (line[i] + ((a + b) >> 1)) & 255
            elif kind == 4:
                line[i] = (line[i] + paeth(a, b, c)) & 255
        rows.append(bytes(line))
        prev = line
    return rows


def decode(data):
    """Returns (width, height, list of RGBA tuples) for 8-bit RGB/RGBA/indexed PNGs."""
    if data[:8] != SIGNATURE:
        raise ValueError("not a PNG")
    idat, palette, trns = b"", None, None
    for kind, body in chunks(data):
        if kind == b"IHDR":
            width, height, depth, color, _, _, interlace = struct.unpack(">IIBBBBB", body)
        elif kind == b"PLTE":
            palette = [tuple(body[i:i + 3]) for i in range(0, len(body), 3)]
        elif kind == b"tRNS":
            trns = body
        elif kind == b"IDAT":
            idat += body
    if depth != 8 or interlace or color not in (2, 3, 6):
        raise ValueError("unsupported PNG layout")
    bpp = {2: 3, 3: 1, 6: 4}[color]
    rows = unfilter(zlib.decompress(idat), width, height, bpp)
    pixels = []
    for row in rows:
        if color == 6:
            pixels += [tuple(row[i:i + 4]) for i in range(0, len(row), 4)]
        elif color == 2:
            pixels += [tuple(row[i:i + 3]) + (255,) for i in range(0, len(row), 3)]
        else:
            for index in row:
                alpha = trns[index] if trns and index < len(trns) else 255
                pixels.append(palette[index] + (alpha,))
    return width, height, pixels


def chunk(kind, body):
    return struct.pack(">I", len(body)) + kind + body + struct.pack(">I", zlib.crc32(kind + body) & 0xFFFFFFFF)


def best_filtered(rows, bpp):
    """Per-row filter choice by the minimum-sum-of-absolute-differences heuristic."""
    out, prev = bytearray(), bytes(len(rows[0]))
    for row in rows:
        candidates = []
        for kind in range(5):
            line = bytearray(len(row))
            for i in range(len(row)):
                a = row[i - bpp] if i >= bpp else 0
                b = prev[i]
                c = prev[i - bpp] if i >= bpp else 0
                predictor = (0, a, b, (a + b) >> 1, paeth(a, b, c))[kind]
                line[i] = (row[i] - predictor) & 255
            score = sum(v if v < 128 else 256 - v for v in line)
            candidates.append((score, kind, line))
        _, kind, line = min(candidates, key=lambda c: c[0])
        out.append(kind)
        out += line
        prev = row
    return bytes(out)


def encode(width, height, pixels):
    colors = list(dict.fromkeys(pixels))
    if len(colors) <= 256:
        # Opaque colours last keeps the tRNS chunk short.
        colors.sort(key=lambda c: c[3] == 255)
        index = {c: i for i, c in enumerate(colors)}
        rows = [bytes(index[p] for p in pixels[y * width:(y + 1) * width]) for y in range(height)]
        header = struct.pack(">IIBBBBB", width, height, 8, 3, 0, 0, 0)
        body = chunk(b"PLTE", bytes(v for c in colors for v in c[:3]))
        alphas = bytes(c[3] for c in colors if c[3] != 255)
        if alphas:
            body += chunk(b"tRNS", alphas)
        filtered = b"".join(b"\x00" + r for r in rows)  # indexed data compresses best unfiltered
    else:
        opaque = all(p[3] == 255 for p in pixels)
        bpp = 3 if opaque else 4
        rows = [bytes(v for p in pixels[y * width:(y + 1) * width] for v in p[:bpp]) for y in range(height)]
        header = struct.pack(">IIBBBBB", width, height, 8, 2 if opaque else 6, 0, 0, 0)
        body = b""
        filtered = best_filtered(rows, bpp)
    return SIGNATURE + chunk(b"IHDR", header) + body + chunk(b"IDAT", zlib.compress(filtered, 9)) + chunk(b"IEND", b"")


def optimize(path):
    original = path.read_bytes()
    width, height, pixels = decode(original)
    smaller = encode(width, height, pixels)
    check = decode(smaller)
    # Fully transparent pixels may differ only in their (invisible) colour.
    same = check[:2] == (width, height) and all(
        a == b or (a[3] == 0 and b[3] == 0) for a, b in zip(check[2], pixels))
    if not same:
        raise ValueError("round trip changed pixels")
    if len(smaller) < len(original):
        path.write_bytes(smaller)
    return len(original), min(len(original), len(smaller))


def main(args):
    files = []
    for arg in args:
        p = Path(arg)
        files += sorted(p.rglob("*.png")) if p.is_dir() else [p]
    total_before = total_after = 0
    for f in files:
        before, after = optimize(f)
        total_before += before
        total_after += after
        print(f"{f}: {before} -> {after}")
    print(f"total: {total_before} -> {total_after} bytes")


if __name__ == "__main__":
    main(sys.argv[1:])
