# Asset sources and licensing

Everything the site shows is first-party: no stock images, icon sets, web fonts or third-party code.

## Bitz art (`assets/bitz/art/`)

Exported from the Bitz app's own pixel renderer (`Sources/BitzShared/Render` in the Bitz repository) by
`tools/bitz-art`, a small Swift package that depends on the Bitz package read-only. Bitz's art is original and
drawn in code (Bitz `docs/STORE_LISTING.md`: "Does not use third-party content"); it belongs to the Bitz
developer, Berkay Yilmaz (Gibplay Game Studio). Exported from Bitz commit `1e92ef4`, via a `git archive` copy so
the app repository's working tree was not touched.

| Files | What |
| --- | --- |
| `stage-<season>-<day/night>-bg.png`, `-fg.png`, `-cat.png`, `stage.js` | The interactive stage: the main room behind Bitz, in front of Bitz, and Bitz's frames cut from the renderer's lit cat layer; `stage.js` lists the frame sequences. |
| `scene-autumn-day.png`, `scene-autumn-night.png`, `scene-winter-day.png` | Whole scenes (no-JavaScript hero, homepage, 404). |
| `room-*.png`, `theme-*.png` | The five rooms (classic look, autumn day) and ten room themes. |
| `stage-kitten/young/adult.png`, `wear-*.png` | Growth stages and six clothing packs. |
| `widget-*.png` | Widget crops made with the app's `WidgetFraming`. |
| `charging-room.png` | The main room at 21:30 while charging (Bitz sipping milk). |
| `visit-55.png` | A Nearby Friends visit from the app's `VisitRenderer` (demo cats, no player names shown). |
| `memory-*.png`, `souvenir-*.png` | Scrapbook Polaroids and souvenirs. |
| `heart.png` | The heart sprite the app draws when Bitz is petted. |
| `icon-64.png`, `icon-192.png` | The Bitz app icon (`Portraits.appIcon()`), favicon and touch icon on Bitz pages. |
| `og-bitz.png` | 1200×630 sharing image: the autumn main room on Bitz plum. |

Files are written at native pixel size (one art pixel per image pixel) and scaled by the browser with
`image-rendering: pixelated`, so they stay sharp at any size. Transparency is preserved.

To re-export:

```sh
git -C ../Bitz archive HEAD Package.swift Sources Tools Tests | tar -x -C /tmp/bitz-src
cd tools/bitz-art && BITZ_SRC=/tmp/bitz-src swift run bitz-art /tmp/bitz-art-out
python3 tools/optimize_png.py /tmp/bitz-art-out && cp /tmp/bitz-art-out/* assets/bitz/art/
```

## Screenshots (`assets/bitz/screens/`)

Resized copies (JPEG, quality ~78) of Bitz's App Store screenshots in the Bitz repository,
`docs/store/screenshots/` (`iphone69-{en,tr}-1-day`, `-2-cuddle`, `ipad13-{en,tr}-4-cabin`). They are demo
launches: the pet names are demo names (Bitz, Mochi), the status bar shows Apple's 09:41, and there are no
personal names, device identifiers, notifications or development UI. (The English iPad capture shows a
Turkish date in its status bar, as in the App Store set.)

The `docs/store/iap-review/` images were inspected but not used: they show prices and Buy buttons.

## GibPlay Studios logo (`assets/img/`, `favicon.ico`)

Resized from the studio's existing `logo.png` (kept at the repository root). `apple-touch-icon.png` places it on
the site's cream background; `favicon.ico` holds 32 and 48 px versions.

## Fonts and icons

System fonts only (`system-ui`, `ui-rounded`, `ui-monospace`). No icon fonts.

## App Store badge

Not included while Bitz is unreleased. When it is, use Apple's official badge from Apple's marketing
resources under Apple's guidelines (see `RELEASE_BUTTON.md`).
