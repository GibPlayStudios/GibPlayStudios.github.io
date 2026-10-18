# gibplay.com handoff to the Bitz release session

From the website session, 2026-10-18. Answers the five questions in Bitz `docs/WEBSITE_HANDOFF.md`.

## 1. Commit and deployment

| | |
| --- | --- |
| Repository | `GibPlayStudios/GibPlayStudios.github.io`, branch `main`, GitHub Pages (legacy Jekyll build from `main` /) |
| Website commit | see `git log` (status below) |
| Deployment | **PENDING** — see "Unresolved" |

## 2. URLs, canonical and www

| Page | Canonical URL |
| --- | --- |
| Studio (EN) | https://gibplay.com/ |
| Studio (TR) | https://gibplay.com/tr/ |
| Bitz (EN) | https://gibplay.com/Bitz/ |
| Bitz (TR) | https://gibplay.com/Bitz/tr/ |
| Support (EN + TR) | https://gibplay.com/Bitz/support/ |
| Privacy (EN + TR) | https://gibplay.com/Bitz/privacy/ |

- `CNAME` unchanged: `gibplay.com`. DNS is on Cloudflare (proxied); GitHub's certificate covers `gibplay.com`
  and `www.gibplay.com`.
- `https://www.gibplay.com/` → 301 → `https://gibplay.com/` (Cloudflare, verified 2026-10-18 before this deploy).
- Each page's `<link rel="canonical">` is the https apex URL with a trailing slash.
- `http://gibplay.com/` is served over plain HTTP (200), not redirected; see "Unresolved".

## 3. English / Turkish

- Marketing pages use separate URLs: `/` ↔ `/tr/`, `/Bitz/` ↔ `/Bitz/tr/` (with `hreflang` alternates).
- **Support and privacy keep the app's scheme: one page each, English first, Turkish in the section with
  `id="tr"` and `lang="tr"`.** The app's links (`…/Bitz/support/`, `…/Bitz/privacy/`, plus `#tr` on Turkish
  phones) work as planned; no separate Turkish URLs to wire up.
- Stable anchors on support: `#contact #purchases #packs #seasonal #restore #save #refunds #health #widgets
  #charging #nearby #data`, Turkish the same with `tr-` (`#tr-restore` …). Privacy: `#short #who #device
  #nearby #purchases #apple #web #rights #children #changes`, Turkish with `tr-`.

## 4. Support and privacy text

- Imported **verbatim** from the Bitz repo's `docs/site/support.html` and `docs/site/privacy.html` by
  `tools/import_bitz_docs.py` (word-for-word comparison: identical). Imported file versions (SHA-256) are in
  `config/bitz-docs-source.json`. **These were the working-tree versions on 2026-10-18, which include the
  uncommitted build 6 changes** (Nearby Friends shares only the cat's look until an invitation; Report; the
  "Bitz 1.0, build 6 and later" effective line). If that text changes again, re-run the importer and the build.
- Layout-only changes: relative links became `/Bitz/`, `/Bitz/support/`, `/Bitz/privacy/` (`#tr` kept);
  headings got anchors; a table of contents was added.
- **One addition on support** (both languages): "Charging Room and StandBy" / "Şarj Odası ve StandBy", built
  from the app's own strings (`chargingRoomStandByNote`, `guideInApp`, `guideClosed`,
  `chargingRoomAwakeFooter`, `chargingRoomLayoutFooter`, `guideUnlockNote` and their Turkish catalog values). It
  refers to "Settings › Charging Room" (`SettingsView.swift`). Please check it and copy it into
  `docs/site/support.html` if you agree, or tell the website session to change it.
- The privacy promise for web pages holds: no cookies, analytics, ads, third-party fonts or scripts; every page
  sets a Content-Security-Policy limited to its own origin. Hosting remains GitHub Pages behind Cloudflare.
  Cloudflare adds a Network Error Logging header (`nel`/`report-to`, reports to `a.nel.cloudflare.com`), which
  falls under "delivered through Cloudflare".
- Cloudflare **Email Address Obfuscation is on** for gibplay.com; it would rewrite addresses into
  "[email protected]" plus a script. Every page body is wrapped in `<!--email_off-->`, so `info@gibplay.com`
  stays a plain `mailto:` link.

## 5. Release button

`config/release.json`: `status: "coming-soon"`, App Store ID `6824056606`, future URL
`https://apps.apple.com/app/id6824056606`. Verified not public on 2026-10-18 (lookup API: 0 results; app URL
404). Steps to switch, including Apple's official badge: `docs/RELEASE_BUTTON.md`.

## Inconsistencies for the owner

- **Studio name:** the website uses "GibPlay Studios" (as requested for the site); the app, privacy policy and
  App Store copyright use "Gibplay Game Studio"; the old site used "GIB Play Studios". Support/privacy text keeps
  "Gibplay Game Studio" as written. Pick one and tell both sessions.
- **Email:** the old site footer used `hello@gibplay.com`; the app and App Store Connect use
  `info@gibplay.com`. The site uses only `info@gibplay.com`. No test email was sent.
- The old site said "Istanbul / Kocaeli"; the new site states no location.

## Tests (local, 2026-10-18)

- Rendered with Chrome (headless and the in-app browser) at 320, 375, 430, 768, 1024, 1280 and 1440 px:
  no horizontal overflow or broken images on any page; light and dark mode.
- English and Turkish pages; keyboard: skip link, visible focus ring, stage buttons by keyboard.
- Stage: pet (hearts + live status text), day/night, four seasons, idle walking; pauses offscreen and in
  hidden tabs; with reduced motion Bitz is shown still and petting shows a still reaction; without JavaScript a
  still picture shows and no dead controls appear.
- Link crawl: every internal link, image and anchor resolves with exact case; only external links are
  `reportaproblem.apple.com` and Apple's privacy policies. Network: same-origin requests only. Console: no errors.

## Unresolved

- Deployment status: see section 1.
- `http://` is not redirected to `https://`. GitHub's "Enforce HTTPS" is off and Cloudflare serves HTTP. Turn on
  Cloudflare "Always Use HTTPS" (or GitHub "Enforce HTTPS") — an account setting this session didn't change.
- The old pages at `https://berkay-yilmaz.github.io/bitz-app/` were not touched and keep working.
