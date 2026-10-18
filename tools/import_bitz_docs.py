#!/usr/bin/env python3
"""Imports Bitz's approved support and privacy text into src/pages/.

The app's release session owns the wording in the Bitz repository
(docs/site/support.html and docs/site/privacy.html, English first, Turkish in a
section after <hr id="tr">). This script copies that text verbatim into the
site's layout: it rewrites the old relative links to gibplay.com routes, gives
every heading an anchor, builds the page's table of contents, and (support
only) adds the "Charging Room and StandBy" section written for the site from
the app's own strings. Then run tools/build.py.

Usage: python3 tools/import_bitz_docs.py [PATH_TO_BITZ_REPO]   (default: ../Bitz)
"""
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BITZ = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT.parent / "Bitz"

# Written for gibplay.com from the app's own strings (Shared/L10n.swift: chargingRoomStandByNote,
# guideInApp, guideClosed, chargingRoomAwakeFooter, chargingRoomLayoutFooter, guideUnlockNote).
CHARGING = {
    "en": """<h2 id="charging">Charging Room and StandBy</h2>
<p>The Charging Room is a cozy bedside clock inside Bitz. While Bitz is open, plug in your iPhone and turn
it sideways: the Charging Room opens by itself. No automation is needed. In Settings › Charging Room you can
choose whether it opens when you turn your iPhone sideways or on power however you hold it. The screen stays
on only while the Charging Room is showing and your iPhone is charging. Brightness is never changed.</p>
<p>An app can't open itself just because your iPhone starts charging. Personal automations in Shortcuts can
keep Bitz up to date, and can open the Charging Room if you like; Settings › Charging Room has a step-by-step
guide. Opening an app from an automation may need your iPhone to be unlocked, and iOS may ask first or not
open it at all.</p>
<p>The Charging Room isn't StandBy. For StandBy, add the Bitz widget there.</p>
""",
    "tr": """<h2 id="tr-charging">Şarj Odası ve StandBy</h2>
<p>Şarj Odası, Bitz'in içindeki sıcacık bir başucu saatidir. Bitz açıkken iPhone'unu şarja tak ve yan çevir:
Şarj Odası kendiliğinden açılır. Otomasyon gerekmez. Ayarlar › Şarj Odası bölümünden, iPhone'unu yan
çevirdiğinde mi yoksa telefonu nasıl tutarsan tut şarja taktığında mı açılacağını seçebilirsin. Ekran yalnızca
Şarj Odası açıkken ve iPhone'un şarj olurken açık kalır. Parlaklık asla değiştirilmez.</p>
<p>Bir uygulama, iPhone'un şarj olmaya başladı diye kendiliğinden açılamaz. Kestirmeler'deki kişisel
otomasyonlar Bitz'i güncel tutabilir ve istersen Şarj Odası'nı açabilir; Ayarlar › Şarj Odası'nda adım adım
bir rehber var. Bir uygulamayı otomasyonla açmak iPhone'unun kilidinin açık olmasını gerektirebilir; iOS önce
sorabilir ya da hiç açmayabilir.</p>
<p>Şarj Odası StandBy değildir. StandBy için Bitz widget'ını oraya ekle.</p>
""",
}

# Stable anchors for headings that other pages (and the app) link to.
ANCHORS = {
    "Contact": "contact", "Purchases": "purchases", "Health and steps": "health", "Widgets": "widgets",
    "Nearby Friends": "nearby", "Your data": "data", "Who we are": "who", "On your device only": "device",
    "Purchases (Apple)": "purchases", "Information Apple shares with developers": "apple",
    "Email and these web pages": "web", "Your choices and rights": "rights", "Children": "children",
    "Changes": "changes", "How do I restore packs I bought?": "restore",
    "Does Restore Purchases bring back my cat?": "save", "Refunds and payment problems": "refunds",
    "Satın alımlar": "purchases", "Sağlık ve adımlar": "health", "Widget'lar": "widgets",
    "Yakındaki Arkadaşlar": "nearby", "Verilerin": "data", "Biz kimiz": "who", "Yalnızca cihazında": "device",
    "Satın alımlar (Apple)": "purchases", "Apple'ın geliştiricilerle paylaştığı bilgiler": "apple",
    "E-posta ve bu web sayfaları": "web", "Seçeneklerin ve hakların": "rights", "Çocuklar": "children",
    "Değişiklikler": "changes", "Aldığım paketleri nasıl geri yüklerim?": "restore",
    "Satın alımları geri yüklemek kedimi de geri getirir mi?": "save", "İadeler ve ödeme sorunları": "refunds",
    "Nearby Friends (optional, off by default)": "nearby",
    "Yakındaki Arkadaşlar (isteğe bağlı, varsayılan olarak kapalı)": "nearby",
    "What do I get when I buy a pack?": "packs", "Bir paket alınca ne alırım?": "packs",
    "Why can't I see a pack in the Shop?": "seasonal", "Bir paketi Dükkân'da neden göremiyorum?": "seasonal",
}
TOC_LABELS = {"Purchases (Apple)": "Purchases (Apple)", "Information Apple shares with developers": "Information Apple shares",
              "Does Restore Purchases bring back my cat?": "Your cat's save", "How do I restore packs I bought?": "Restoring packs",
              "Refunds and payment problems": "Refunds"}


def plain(fragment):
    return re.sub(r"<[^>]+>", "", fragment).strip()


def slug(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def convert(part, lang, page):
    prefix = "" if lang == "en" else "tr-"
    # Drop the old page chrome: header, page title and the old page nav.
    part = re.sub(r"<header>.*?</header>\s*", "", part, flags=re.S)
    part = re.sub(r"<h1>[^<]*</h1>\s*", "", part)
    part = re.sub(r"<nav[^>]*>.*?</nav>\s*", "", part, flags=re.S)
    part = part.replace('<p class="soft">', '<p class="meta">')
    part = part.replace('<div class="card">', '<div class="callout">')
    # Links: the old site's relative pages become gibplay.com routes.
    home = "/Bitz/" if lang == "en" else "/Bitz/tr/"
    part = part.replace('href="index.html"', f'href="{home}"')
    part = part.replace('href="support.html#tr"', 'href="/Bitz/support/#tr"').replace('href="support.html"', 'href="/Bitz/support/"')
    part = part.replace('href="privacy.html#tr"', 'href="/Bitz/privacy/#tr"').replace('href="privacy.html"', 'href="/Bitz/privacy/"')
    if re.search(r'href="(?!https?:|mailto:|/|#)', part):
        raise SystemExit(f"{page}: unexpected relative link left: " + re.search(r'href="(?!https?:|mailto:|/|#)[^"]*"', part).group(0))

    toc = []

    def anchor(match):
        level, attrs, inner = match.group(1), match.group(2), match.group(3)
        if "id=" in attrs:
            return match.group(0)
        text = plain(inner)
        key = ANCHORS.get(text) or slug(text)
        if level == "2":
            toc.append((prefix + key, TOC_LABELS.get(text, re.sub(r" \(.*\)$", "", text))))
        return f'<h{level} id="{prefix}{key}"{attrs}>{inner}</h{level}>'

    part = re.sub(r"<h([23])([^>]*)>(.*?)</h\1>", anchor, part, flags=re.S)
    # The contact card on the support page gets its own anchor.
    if page == "support":
        part = part.replace('<div class="callout">', f'<div class="callout" id="{prefix}contact">', 1)
        toc.insert(0, (prefix + "contact", "Contact" if lang == "en" else "İletişim"))
        # The site's extra section goes after Widgets.
        marker = f'<h2 id="{prefix}nearby">'
        if marker not in part:
            raise SystemExit("support: Nearby Friends heading not found; cannot place the Charging Room section")
        part = part.replace(marker, CHARGING[lang] + "\n" + marker)
        toc.insert([t[0] for t in toc].index(prefix + "nearby"),
                   (prefix + "charging", "Charging Room and StandBy" if lang == "en" else "Şarj Odası ve StandBy"))
    if page == "privacy":
        part = part.replace('<div class="callout">', f'<div class="callout" id="{prefix}short">', 1)
        toc.insert(0, (prefix + "short", "In short" if lang == "en" else "Kısaca"))
    return part.strip(), toc


def import_page(page):
    source = BITZ / "docs/site" / f"{page}.html"
    text = source.read_text()
    body = text.split("<main>", 1)[1].split("</main>", 1)[0]
    en, tr = body.split('<hr id="tr">', 1)
    tr = re.sub(r'^\s*<div lang="tr">', "", tr)
    tr = re.sub(r"</div>\s*$", "", tr.strip())
    en_html, en_toc = convert(en, "en", page)
    tr_html, _ = convert(tr, "tr", page)

    title_en = {"support": "Support", "privacy": "Privacy Policy"}[page]
    title_tr = {"support": "Destek", "privacy": "Gizlilik Politikası"}[page]
    kicker = {"support": "Help and contact", "privacy": "Privacy policy"}[page]
    other_en = ('<a href="/Bitz/privacy/">Privacy</a>' if page == "support" else '<a href="/Bitz/support/">Support</a>')
    other_tr = ('<a href="/Bitz/privacy/#tr">Gizlilik</a>' if page == "support" else '<a href="/Bitz/support/#tr">Destek</a>')
    toc_items = "\n".join(f'      <li><a href="#{a}">{label}</a></li>' for a, label in en_toc)
    tr_link = "Türkçe destek →" if page == "support" else "Türkçe gizlilik politikası →"
    digest = hashlib.sha256(text.encode()).hexdigest()[:16]

    out = f"""<!-- Imported from Bitz docs/site/{page}.html (sha256 {digest}) by tools/import_bitz_docs.py. Edit the
     wording in the Bitz repository and re-import; only the layout lives here. -->
<section class="doc-hero" aria-labelledby="{page}-heading">
  <div class="wrap">
    <div class="bitz-title">
      <img class="pixel" src="/assets/bitz/art/icon-192.png" alt="" width="64" height="64">
      <p><strong>Bitz</strong>{kicker}</p>
    </div>
    <h1 id="{page}-heading">{title_en}</h1>
    <nav class="lang-nav" aria-label="Pages"><a href="/Bitz/">Bitz</a>{other_en}<a href="#tr" hreflang="tr" lang="tr">Türkçe</a></nav>
  </div>
</section>

<div class="wrap doc">
  <nav class="toc" aria-label="On this page">
    <h2>On this page</h2>
    <ol>
{toc_items}
    </ol>
    <p class="toc-lang"><a href="#tr" hreflang="tr" lang="tr">{tr_link}</a></p>
  </nav>

  <article class="prose" aria-labelledby="{page}-heading">
{en_html}

    <section class="section-lang" id="tr" lang="tr" aria-labelledby="{page}-tr-heading">
      <h1 id="{page}-tr-heading">{title_tr}</h1>
      <nav class="lang-nav" aria-label="Sayfalar"><a href="/Bitz/tr/">Bitz</a>{other_tr}<a href="#main" hreflang="en" lang="en">English</a></nav>
{tr_html}
    </section>
  </article>
</div>
"""
    (ROOT / "src/pages" / f"{page}.html").write_text(out)
    return {"file": f"docs/site/{page}.html", "sha256": hashlib.sha256(text.encode()).hexdigest()}


if __name__ == "__main__":
    sources = [import_page(p) for p in ("support", "privacy")]
    (ROOT / "config/bitz-docs-source.json").write_text(json.dumps({"bitzRepo": "../" + BITZ.resolve().name, "sources": sources}, indent=2) + "\n")
    for s in sources:
        print("imported", s["file"], s["sha256"][:16])
