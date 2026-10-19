# gibplay.com handoff to the Bitz release session

From the website session, updated 2026-10-18 after the second deployment. Answers the five questions in Bitz
`docs/WEBSITE_HANDOFF.md`.

## 1. Commit and deployment

| | |
| --- | --- |
| Repository | `GibPlayStudios/GibPlayStudios.github.io`, branch `main`, GitHub Pages (Jekyll build from `main` /) |
| Live commit | `3924cb6` ("Add files via upload"; Pages build `built`, 2026-10-18 14:01 UTC). Its site files are identical to the website session's commit `2607292`. |
| How it was deployed | The owner uploaded the files on github.com; the `berkay-yilmaz` account has read-only access, so `git push` from this Mac is refused (403). |
| Verified live | Every route below returns 200 over HTTPS; the live HTML matches the local build byte for byte, except the `<!--email_off-->` markers that Cloudflare consumes as intended. |

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
- `https://www.gibplay.com/` → 301 → `https://gibplay.com/` (verified again after deployment).
- Each page's `<link rel="canonical">` is the https apex URL with a trailing slash.
- `/bitz/` (lowercase) is a 404 on GitHub Pages; the 404 page forwards it to `/Bitz/` with JavaScript and links
  there without it.

## 3. English / Turkish

- Marketing pages use separate URLs: `/` ↔ `/tr/`, `/Bitz/` ↔ `/Bitz/tr/` (with `hreflang` alternates).
- **Support and privacy keep the app's scheme: one page each, English first, Turkish in the section with
  `id="tr"` and `lang="tr"`.** The app's links (`…/Bitz/support/`, `…/Bitz/privacy/`, plus `#tr` on Turkish
  phones) work as planned.
- Stable anchors on support: `#contact #purchases #packs #seasonal #restore #save #refunds #health #widgets
  #charging #nearby #data`, Turkish the same with `tr-` (`#tr-restore` …). Privacy: `#short #who #device
  #nearby #purchases #apple #web #rights #children #changes`, Turkish with `tr-`. Unchanged by the redesign.

## 4. Support and privacy text

- Imported **verbatim** from the Bitz repo's `docs/site/support.html` and `docs/site/privacy.html` by
  `tools/import_bitz_docs.py` (word-for-word comparison: identical). SHA-256 of the published sources is in
  `config/bitz-docs-source.json`. On 2026-10-18 the corrected privacy and support text (support email, website,
  retention, legal bases, rights) was written into the Bitz repo's `docs/site/` files (not yet committed there)
  and re-imported; the importer reproduces these pages exactly from those files. If the text changes again:
  edit it in Bitz `docs/site/`, re-run the importer and `tools/build.py`, then deploy.
- Layout-only changes: relative links became `/Bitz/`, `/Bitz/support/`, `/Bitz/privacy/` (`#tr` kept);
  headings got anchors; a table of contents was added.
- **One addition on support** (both languages): "Charging Room and StandBy" / "Şarj Odası ve StandBy", built
  from the app's own strings (`chargingRoomStandByNote`, `guideInApp`, `guideClosed`,
  `chargingRoomAwakeFooter`, `chargingRoomLayoutFooter`, `guideUnlockNote` and their Turkish catalog values). It
  refers to "Settings › Charging Room". It is now part of Bitz `docs/site/support.html`.
- The homepage redesign did not touch support or privacy content.
- Email: Cloudflare Email Address Obfuscation is on for the domain; every page body is wrapped in
  `<!--email_off-->`, and live pages serve plain `mailto:info@gibplay.com` links (verified).

## 5. Release button

`config/release.json`: `status: "coming-soon"`, App Store ID `6824056606`, future URL
`https://apps.apple.com/app/id6824056606`. Not public on 2026-10-18 (lookup API: 0 results; app URL 404). The
homepage's Bitz card and the Bitz pages read the same setting. Switching, including Apple's official badge:
`docs/RELEASE_BUTTON.md`.

## What changed in the second deployment

**Bitz interactive preview (root cause).** On the first deployment the preview never showed. The fallback
picture (the autumn room with Bitz baked in) got the `hidden` attribute when the preview started, but the CSS
rule `.stage-frame img { display: block }` overrode it, so the picture stayed in the frame and pushed the live
canvas below the frame's clipped edge. Visitors only ever saw the static autumn picture while the buttons and
status text changed, which explains "Spring selected but a pumpkin is visible" and "Pet does nothing". The
exported scene art was correct (only autumn has the pumpkin; spring has a watering can, summer a fan, winter a
stove).

Fixes: the layers are stacked absolutely and `[hidden]` always wins; scene requests are versioned so quick
clicks can't leave an older scene on screen; failed loads retry and the buttons fall back to the scene shown;
petting uses the app's own "just petted" frames (celebrate pose, hearts, purr lines) with one reaction at a
time; at night Bitz keeps sleeping with the app's heart sprite; reduced motion shows still reactions; a visible
"Interactive preview" label and a scene tag ("Spring · Night") that changes only once that scene is drawn.

**Studio homepage.** `/` and `/tr/` now use a neutral studio identity (`assets/css/studio.css`: off-white or
charcoal, muted teal accent, system typography, a short transform-only entrance rise). Structure: header
(Games, About, Contact, language), introduction ("Thoughtful games, distinctive worlds." / "Özenli oyunlar,
kendine özgü dünyalar."), a featured Bitz card in Bitz's own colours with real art, release status and
"Explore Bitz", a modest "More to come" note (no names, dates or placeholder cards), About, Contact, footer.
Bitz pages keep their pixel style.

**Studio homepage, light redesign (third change).** `/` and `/tr/` are now light in every system theme:
warm off-white, charcoal text and the logo's pink, coral, peach and warm yellow, with geometric hero artwork
based on the logo, subtle hover/focus transitions and drifting shapes that stop under reduced motion. The
homepage has its own stylesheet version (`STUDIO_ASSET_VERSION` in `tools/build.py`); all 98 Bitz files
(pages, demo, art, support, privacy, 404) were checked byte-identical before and after.

## Tests

Local and again on the live site after deployment (headless Chrome driven through the DevTools protocol,
cache disabled, with screenshots of what is actually rendered):

- Preview, English and Turkish: idle sprite animation; Pet by button, by clicking Bitz, by keyboard (Enter) and
  by touch on a 390 px phone; 8 rapid pets settle back to idle; all 8 season × day/night scenes, with the
  rendered room, pressed buttons and scene tag all matching; 9 rapid clicks end on the last choice; a swipe that
  starts on the preview still scrolls the page; reduced motion shows still idle and still reactions.
- No-JavaScript: the still picture shows and no controls appear (checked locally).
- Homepage: desktop 1280, tablet 820 and phone 390, light and dark, English and Turkish.
- No horizontal overflow on any page at 320, 375, 430, 768, 1024 and 1440 px; every internal link, anchor and
  asset resolves with exact case.
- Console: no errors from the site. See Cloudflare Web Analytics below.

## Unresolved (owner)

1. **Delete the `upload-2607292/` folder from the repository** (github.com: open the folder, "…" menu,
   **Delete directory**, commit). It is no longer published (`_config.yml` excludes `upload-*`), but the copy is
   still public in the repository.
2. Domain verification: GitHub (GibPlayStudios › Settings › Pages › Verified domains) has generated the TXT
   record `_github-pages-challenge-GibPlayStudios.gibplay.com`; add it in Cloudflare DNS with the value shown on
   that GitHub page, then click Verify there. Until then another GitHub account could claim gibplay.com if
   Pages were ever switched off.
3. Push access: grant `berkay-yilmaz` Write access to the repository (or push from the GibPlayStudios account) so
   future deployments are exact commits instead of web uploads.

Resolved since the first handoff: `http://` now redirects to `https://` (Cloudflare "Always Use HTTPS"; GitHub
"Enforce HTTPS" turned on 2026-10-18 with Cloudflare SSL mode Full (strict), checked without redirect loops;
edge certificate for gibplay.com and *.gibplay.com valid until 2026-12-12); Cloudflare Web Analytics is off (no script injected, checked 2026-10-18); the
legal texts use the studio name **GibPlay Studios**; support and privacy now describe the support-email route
(Cloudflare Email Routing, Gmail, Brevo), retention, legal bases and KVKK rights. The Bitz repository's
`docs/site` sources carry the same text (local changes there must be committed with the app).

## Notes for the owner

- **Studio name:** "GibPlay Studios" is used everywhere on the website; the App Store copyright still says
  "Gibplay Game Studio" and should be aligned by the app session.
- **Email:** the website uses only `info@gibplay.com`.

The old pages at `https://berkay-yilmaz.github.io/bitz-app/` were not touched.
