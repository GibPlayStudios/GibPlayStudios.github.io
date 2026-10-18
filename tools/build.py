#!/usr/bin/env python3
"""Builds gibplay.com's static pages (standard library only).

Page bodies live in src/pages/. This script wraps each one in the shared
<head>, header and footer, fills in the release call to action from
config/release.json, and writes plain HTML to the published routes
(/, /tr/, /Bitz/, /Bitz/tr/, /Bitz/support/, /Bitz/privacy/, /404.html) plus
sitemap.xml. GitHub Pages then serves those files as they are.

Usage: python3 tools/build.py
"""
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = "https://gibplay.com"
EMAIL = "info@gibplay.com"
YEAR = "2026"
RELEASE = json.loads((ROOT / "config/release.json").read_text())
ASSET_VERSION = "8"
# The studio homepage has its own version, so homepage-only changes never touch the Bitz pages.
STUDIO_ASSET_VERSION = "s2"

PAGES = [
    {"src": "home.en.html", "out": "index.html", "path": "/", "lang": "en", "section": "home",
     "alternates": {"en": "/", "tr": "/tr/"}, "theme": "studio",
     "title": "GibPlay Studios: thoughtful games, distinctive worlds",
     "description": "GibPlay Studios is an independent game studio making games for iPhone and iPad. Our first game is Bitz."},
    {"src": "home.tr.html", "out": "tr/index.html", "path": "/tr/", "lang": "tr", "section": "home",
     "alternates": {"en": "/", "tr": "/tr/"}, "theme": "studio",
     "title": "GibPlay Studios: özenli oyunlar, kendine özgü dünyalar",
     "description": "GibPlay Studios, iPhone ve iPad için oyunlar yapan bağımsız bir oyun stüdyosu. İlk oyunumuz Bitz."},
    {"src": "bitz.en.html", "out": "Bitz/index.html", "path": "/Bitz/", "lang": "en", "section": "bitz",
     "alternates": {"en": "/Bitz/", "tr": "/Bitz/tr/"}, "icon": "bitz", "scripts": ["stage", "carousel"],
     "title": "Bitz: a cozy pixel cat for iPhone and iPad",
     "description": "Bitz is a tiny pixel cat who moves into your iPhone and iPad. Care, play, five rooms, seasons, widgets and the Charging Room. No ads, no accounts, no tracking."},
    {"src": "bitz.tr.html", "out": "Bitz/tr/index.html", "path": "/Bitz/tr/", "lang": "tr", "section": "bitz",
     "alternates": {"en": "/Bitz/", "tr": "/Bitz/tr/"}, "icon": "bitz", "scripts": ["stage", "carousel"],
     "title": "Bitz: iPhone ve iPad için sevimli bir piksel kedi",
     "description": "Bitz, iPhone ve iPad'ine taşınan minik bir piksel kedi. Bakım, oyun, beş oda, mevsimler, widget'lar ve Şarj Odası. Reklam yok, hesap yok, takip yok."},
    {"src": "support.html", "out": "Bitz/support/index.html", "path": "/Bitz/support/", "lang": "en", "section": "support",
     "alternates": {"en": "/Bitz/support/", "tr": "/Bitz/support/#tr"}, "bilingual": True, "icon": "bitz",
     "title": "Bitz Support",
     "description": "Help and contact for Bitz: purchases, restoring packs, your cat's save, widgets, the Charging Room, Health and Nearby Friends. Türkçe destek de bu sayfada."},
    {"src": "privacy.html", "out": "Bitz/privacy/index.html", "path": "/Bitz/privacy/", "lang": "en", "section": "privacy",
     "alternates": {"en": "/Bitz/privacy/", "tr": "/Bitz/privacy/#tr"}, "bilingual": True, "icon": "bitz",
     "title": "Bitz Privacy Policy",
     "description": "How the Bitz app, its widgets and the Bitz web pages handle information. Türkçe gizlilik politikası da bu sayfada."},
    {"src": "404.html", "out": "404.html", "path": "/404.html", "lang": "en", "section": "404", "noindex": True,
     "alternates": {}, "scripts": ["notfound"],
     "title": "Page not found · GibPlay Studios",
     "description": "This page doesn't exist on gibplay.com."},
]

T = {
    "en": {
        "skip": "Skip to content", "home": "/", "bitz": "/Bitz/", "support": "/Bitz/support/", "privacy": "/Bitz/privacy/",
        "nav_label": "Main", "nav_bitz": "Bitz", "nav_support": "Support", "nav_privacy": "Privacy",
        "switch_label": "Türkçe", "switch_lang": "tr", "switch_title": "Bu sayfayı Türkçe oku",
        "brand_label": "GibPlay Studios home",
        "footer_about": "An independent game studio making games for iPhone and iPad.",
        "footer_game": "Bitz", "footer_contact": "Contact", "footer_language": "Language",
        "footer_support_text": "Questions about Bitz? Start with", "footer_support_link": "Bitz Support",
        "legal": "iPhone and iPad are trademarks of Apple Inc., registered in the U.S. and other countries.",
        "home_name": "Studio",
    },
    "tr": {
        "skip": "İçeriğe geç", "home": "/tr/", "bitz": "/Bitz/tr/", "support": "/Bitz/support/#tr", "privacy": "/Bitz/privacy/#tr",
        "nav_label": "Ana menü", "nav_bitz": "Bitz", "nav_support": "Destek", "nav_privacy": "Gizlilik",
        "switch_label": "English", "switch_lang": "en", "switch_title": "Read this page in English",
        "brand_label": "GibPlay Studios ana sayfa",
        "footer_about": "iPhone ve iPad için oyunlar yapan bağımsız bir oyun stüdyosu.",
        "footer_game": "Bitz", "footer_contact": "İletişim", "footer_language": "Dil",
        "footer_support_text": "Bitz hakkında bir sorun mu var? Önce şuraya bak:", "footer_support_link": "Bitz Destek",
        "legal": "iPhone ve iPad, Apple Inc.'in ABD'de ve diğer ülkelerde tescilli ticari markalarıdır.",
        "home_name": "Stüdyo",
    },
}


def email_link(address=EMAIL, label=None):
    return f'<a href="mailto:{address}">{html.escape(label or address)}</a>'


def release_block(lang):
    """The call to action that depends on whether Bitz is on the App Store yet."""
    r = RELEASE
    devices = r["devices"] if lang == "en" else r["devicesTr"]
    if r["status"] == "available":
        badge = f"/assets/img/app-store-badge-{lang}.svg"
        if not (ROOT / badge.lstrip("/")).exists():
            raise SystemExit(f"Release status is 'available' but {badge} is missing. "
                             "Add Apple's official badge first (docs/RELEASE_BUTTON.md).")
        alt = "Download on the App Store" if lang == "en" else "App Store'dan İndirin"
        note = (f"Free on the App Store for {devices}, {r['minimumOS']} or later." if lang == "en"
                else f"App Store'da ücretsiz: {devices}, {r['minimumOS']} veya sonrası.")
        return (f'<div class="release release--live"><a class="store-badge" href="{r["appStoreUrl"]}">'
                f'<img src="{badge}" alt="{alt}" width="120" height="40"></a>'
                f'<p class="release-note">{note}</p></div>')
    if lang == "en":
        return ('<div class="release"><p class="release-pill"><span class="dot" aria-hidden="true"></span>'
                '<strong>Coming soon</strong> to the App Store</p>'
                f'<p class="release-note">For {devices}, {r["minimumOS"]} or later. Not available to download yet; '
                'this page will link to the App Store once Bitz is released.</p></div>')
    return ('<div class="release"><p class="release-pill"><span class="dot" aria-hidden="true"></span>'
            "<strong>Çok yakında</strong> App Store'da</p>"
            f'<p class="release-note">{devices} için, {r["minimumOS"]} veya sonrası. Henüz indirilemiyor; '
            "Bitz yayımlandığında bu sayfa App Store'a bağlantı verecek.</p></div>")


def release_compact(lang):
    """A one-line status for game cards (the homepage)."""
    r = RELEASE
    devices = r["devices"] if lang == "en" else r["devicesTr"]
    if r["status"] == "available":
        badge = f"/assets/img/app-store-badge-{lang}.svg"
        alt = "Download on the App Store" if lang == "en" else "App Store'dan İndirin"
        return (f'<a class="store-badge" href="{r["appStoreUrl"]}"><img src="{badge}" alt="{alt}" width="120" height="40"></a>'
                f'<p class="game-status-note">{devices}, {r["minimumOS"]}+</p>')
    if lang == "en":
        return ('<p class="game-status"><span class="dot" aria-hidden="true"></span>Coming soon to the App Store</p>'
                f'<p class="game-status-note">For {devices}, {r["minimumOS"]} or later. Not available to download yet.</p>')
    return ("<p class=\"game-status\"><span class=\"dot\" aria-hidden=\"true\"></span>Çok yakında App Store'da</p>"
            f'<p class="game-status-note">{devices} için, {r["minimumOS"]} veya sonrası. Henüz indirilemiyor.</p>')


def release_short(lang):
    if RELEASE["status"] == "available":
        return "Available on the App Store" if lang == "en" else "App Store'da"
    return "Coming soon to the App Store" if lang == "en" else "Çok yakında App Store'da"


def head(page):
    lang, t = page["lang"], T[page["lang"]]
    url = SITE + page["path"]
    bitz_icon = page.get("icon") == "bitz"
    studio = page.get("theme") == "studio"
    light_bg, dark_bg = ("#fdfbf8", "#fdfbf8") if studio else ("#f9efe1", "#211820")
    lines = [
        "<!doctype html>",
        f'<html lang="{lang}">',
        "<head>",
        '<meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        "<meta http-equiv=\"Content-Security-Policy\" content=\"default-src 'self'; img-src 'self'; "
        "style-src 'self'; script-src 'self'; font-src 'self'; connect-src 'self'; base-uri 'self'; "
        "form-action 'none'; object-src 'none'\">",
        '<meta name="referrer" content="strict-origin-when-cross-origin">',
        f"<title>{html.escape(page['title'])}</title>",
        f'<meta name="description" content="{html.escape(page["description"])}">',
        f'<meta name="color-scheme" content="{"light" if studio else "light dark"}">',
        f'<meta name="theme-color" content="{light_bg}" media="(prefers-color-scheme: light)">',
        f'<meta name="theme-color" content="{dark_bg}" media="(prefers-color-scheme: dark)">',
    ]
    if page.get("noindex"):
        lines.append('<meta name="robots" content="noindex">')
    else:
        lines.append(f'<link rel="canonical" href="{url}">')
        for alt_lang, alt_path in page["alternates"].items():
            if "#" in alt_path:
                continue  # one bilingual page: no separate alternate URL
            lines.append(f'<link rel="alternate" hreflang="{alt_lang}" href="{SITE + alt_path}">')
        if "en" in page["alternates"] and "#" not in page["alternates"].get("tr", ""):
            lines.append(f'<link rel="alternate" hreflang="x-default" href="{SITE + page["alternates"]["en"]}">')
    og_image = SITE + "/assets/bitz/art/og-bitz.png"
    lines += [
        f'<meta property="og:type" content="website">',
        f'<meta property="og:site_name" content="GibPlay Studios">',
        f'<meta property="og:title" content="{html.escape(page["title"])}">',
        f'<meta property="og:description" content="{html.escape(page["description"])}">',
        f'<meta property="og:url" content="{url}">',
        f'<meta property="og:locale" content="{"en_US" if lang == "en" else "tr_TR"}">',
        f'<meta property="og:image" content="{og_image}">',
        '<meta property="og:image:width" content="1200">',
        '<meta property="og:image:height" content="630">',
        f'<meta property="og:image:alt" content="{"Bitz the pixel cat sitting on the rug in a cozy autumn living room" if lang == "en" else "Bitz adlı piksel kedi, sonbahar renklerindeki sıcacık salonda halının üstünde oturuyor"}">',
        '<meta name="twitter:card" content="summary_large_image">',
    ]
    if bitz_icon:
        lines += ['<link rel="icon" type="image/png" sizes="64x64" href="/assets/bitz/art/icon-64.png">',
                  '<link rel="apple-touch-icon" href="/assets/bitz/art/icon-192.png">']
    else:
        lines += ['<link rel="icon" href="/favicon.ico" sizes="32x32 48x48">',
                  '<link rel="icon" type="image/png" sizes="160x160" href="/assets/img/gibplay-logo-160.png">',
                  '<link rel="apple-touch-icon" href="/assets/img/apple-touch-icon.png">']
    if page.get("theme") == "studio":
        lines.append(f'<link rel="stylesheet" href="/assets/css/studio.css?v={STUDIO_ASSET_VERSION}">')
    else:
        lines.append(f'<link rel="stylesheet" href="/assets/css/site.css?v={ASSET_VERSION}">')
    if page["section"] == "home" and lang == "en":
        lines.append('<script type="application/ld+json">' + json.dumps({
            "@context": "https://schema.org", "@type": "Organization", "name": "GibPlay Studios",
            "url": SITE + "/", "logo": SITE + "/assets/img/gibplay-logo-512.png", "email": EMAIL,
        }) + "</script>")
    for script in page.get("scripts", []):
        if script == "stage":
            lines.append(f'<script src="/assets/bitz/art/stage.js?v={ASSET_VERSION}" defer></script>')
        lines.append(f'<script src="/assets/js/{script}.js?v={ASSET_VERSION}" defer></script>')

    theme = page.get("theme", "bitz")
    lines += ["</head>", f'<body class="theme-{theme} page-{page["section"]}">']
    return "\n".join(lines)


def header(page):
    lang, t = page["lang"], T[page["lang"]]
    section = page["section"]
    switch = page["alternates"].get(t["switch_lang"])
    if page.get("bilingual"):
        switch = "#tr"

    def link(key, label):
        current = ' aria-current="page"' if key == section else ""
        return f'<li><a href="{t[key]}"{current}>{label}</a></li>'

    if page.get("theme") == "studio":
        items = [("#games", "Games" if lang == "en" else "Oyunlar"), ("#about", "About" if lang == "en" else "Hakkında"),
                 ("#contact", "Contact" if lang == "en" else "İletişim")]
        nav_items = "\n        ".join(f'<li><a href="{href}">{label}</a></li>' for href, label in items)
    else:
        nav_items = "\n        ".join([link('bitz', t['nav_bitz']), link('support', t['nav_support']), link('privacy', t['nav_privacy'])])
    switch_html = ""
    if switch:
        switch_html = (f'<a class="lang-switch" href="{switch}" hreflang="{t["switch_lang"]}" lang="{t["switch_lang"]}" '
                       f'title="{t["switch_title"]}">{t["switch_label"]}</a>')
    return f"""<a class="skip" href="#main">{t['skip']}</a>
<header class="site-header">
  <div class="wrap header-row">
    <a class="brand" href="{t['home']}" aria-label="{t['brand_label']}">
      <img src="/assets/img/gibplay-logo-160.png" alt="" width="40" height="40">
      <span class="brand-name">GibPlay <span>Studios</span></span>
    </a>
    <nav class="site-nav" aria-label="{t['nav_label']}">
      <ul>
        {nav_items}
      </ul>
      {switch_html}
    </nav>
  </div>
</header>"""


def footer(page):
    lang, t = page["lang"], T[page["lang"]]
    other = "tr" if lang == "en" else "en"
    en_url = page["alternates"].get("en", "/")
    tr_url = page["alternates"].get("tr", "/tr/")
    return f"""<footer class="site-footer">
  <div class="wrap footer-grid">
    <div class="footer-brand">
      <a class="brand" href="{t['home']}" aria-label="{t['brand_label']}">
        <img src="/assets/img/gibplay-logo-160.png" alt="" width="40" height="40">
        <span class="brand-name">GibPlay <span>Studios</span></span>
      </a>
      <p>{t['footer_about']}</p>
    </div>
    <div>
      <h2 class="footer-title">{t['footer_game']}</h2>
      <ul class="footer-links">
        <li><a href="{t['bitz']}">{"Bitz, the pixel cat" if lang == "en" else "Bitz, piksel kedi"}</a></li>
        <li><a href="{t['support']}">{t['nav_support']}</a></li>
        <li><a href="{t['privacy']}">{"Privacy policy" if lang == "en" else "Gizlilik politikası"}</a></li>
      </ul>
    </div>
    <div>
      <h2 class="footer-title">{t['footer_contact']}</h2>
      <ul class="footer-links">
        <li>{email_link()}</li>
        <li>{t['footer_support_text']} <a href="{t['support']}">{t['footer_support_link']}</a></li>
      </ul>
    </div>
    <div>
      <h2 class="footer-title">{t['footer_language']}</h2>
      <ul class="footer-links">
        <li><a href="{en_url}" hreflang="en" lang="en"{' aria-current="true"' if lang == 'en' else ''}>English</a></li>
        <li><a href="{tr_url}" hreflang="tr" lang="tr"{' aria-current="true"' if lang == 'tr' else ''}>Türkçe</a></li>
      </ul>
    </div>
  </div>
  <div class="wrap footer-legal">
    <p>© {YEAR} GibPlay Studios. {t['legal']}</p>
  </div>
</footer>"""


# Decorative hero artwork for the studio homepage: the logo's play shape, a warm
# circle and a few small forms in the logo's pink, coral, peach and yellow.
STUDIO_ART = """<svg class="hero-art" viewBox="0 0 520 480" aria-hidden="true" focusable="false">
  <defs>
    <linearGradient id="g-play" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#ef7ba5"/><stop offset="1" stop-color="#f2867f"/></linearGradient>
    <linearGradient id="g-sun" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#f6a57a"/><stop offset="1" stop-color="#f7c46a"/></linearGradient>
    <pattern id="g-dots" width="18" height="18" patternUnits="userSpaceOnUse"><circle cx="3" cy="3" r="2.2" fill="#2a2523" opacity=".16"/></pattern>
  </defs>
  <rect class="shape s-dots" x="350" y="300" width="126" height="108" fill="url(#g-dots)"/>
  <g class="shape s-play"><path d="M120 92 L120 388 L392 240 Z" fill="url(#g-play)" stroke="url(#g-play)" stroke-width="56" stroke-linejoin="round"/></g>
  <circle class="shape s-sun" cx="372" cy="318" r="84" fill="url(#g-sun)" opacity=".92"/>
  <rect class="shape s-square" x="398" y="74" width="48" height="48" rx="12" fill="#f7c46a" transform="rotate(14 422 98)"/>
  <circle class="shape s-dot" cx="78" cy="426" r="15" fill="#ef7ba5"/>
  <circle class="shape s-ring" cx="456" cy="196" r="20" fill="none" stroke="#f2867f" stroke-width="7"/>
  <g class="shape s-badge"><circle cx="214" cy="240" r="74" fill="#fffdfa"/><image href="/assets/img/gibplay-logo-160.png" x="166" y="192" width="96" height="96"/></g>
</svg>"""


def fill(text, page):
    lang = page["lang"]
    replacements = {
        "{{studio_art}}": STUDIO_ART,
        "{{release}}": release_block(lang),
        "{{release_short}}": release_short(lang),
        "{{release_compact}}": release_compact(lang),
        "{{email}}": email_link(),
        "{{devices}}": RELEASE["devices"] if lang == "en" else RELEASE["devicesTr"],
        "{{min_os}}": RELEASE["minimumOS"],
    }
    for key, value in replacements.items():
        text = text.replace(key, value)
    if "{{" in text:
        raise SystemExit(f"Unknown placeholder in {page['src']}: " + text[text.index("{{"):text.index("{{") + 40])
    return text


def build():
    for page in PAGES:
        body = fill((ROOT / "src/pages" / page["src"]).read_text(), page)
        out = ROOT / page["out"]
        out.parent.mkdir(parents=True, exist_ok=True)
        # Cloudflare's Email Address Obfuscation (on for gibplay.com) would turn every
        # address into "[email protected]" plus a script; email_off keeps them readable.
        out.write_text("\n".join([head(page), "<!--email_off-->", header(page),
                                  f'<main id="main">\n{body.strip()}\n</main>', footer(page),
                                  "<!--/email_off-->", "</body>", "</html>", ""]))
        print("wrote", page["out"])

    urls = []
    for page in PAGES:
        if page.get("noindex"):
            continue
        alts = "".join(f'\n    <xhtml:link rel="alternate" hreflang="{l}" href="{SITE + p}"/>'
                       for l, p in page["alternates"].items() if "#" not in p)
        urls.append(f"  <url>\n    <loc>{SITE + page['path']}</loc>{alts}\n  </url>")
    (ROOT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
        + "\n".join(urls) + "\n</urlset>\n")
    print("wrote sitemap.xml")


if __name__ == "__main__":
    build()
