# gibplay.com

The GibPlay Studios website and the pages for Bitz, served by GitHub Pages from `main` (custom domain in
`CNAME`, delivered through Cloudflare).

| URL | File | Source |
| --- | --- | --- |
| https://gibplay.com/ | `index.html` | `src/pages/home.en.html` |
| https://gibplay.com/tr/ | `tr/index.html` | `src/pages/home.tr.html` |
| https://gibplay.com/Bitz/ | `Bitz/index.html` | `src/pages/bitz.en.html` |
| https://gibplay.com/Bitz/tr/ | `Bitz/tr/index.html` | `src/pages/bitz.tr.html` |
| https://gibplay.com/Bitz/support/ (Turkish at `#tr`) | `Bitz/support/index.html` | imported, see below |
| https://gibplay.com/Bitz/privacy/ (Turkish at `#tr`) | `Bitz/privacy/index.html` | imported, see below |
| any missing page | `404.html` | `src/pages/404.html` |

Paths are case-sensitive on GitHub Pages: Bitz pages live under `/Bitz/`. The 404 page forwards
`/bitz/...` to the right address when JavaScript is on, and links there when it isn't.

## Editing

The published HTML is generated; edit `src/pages/`, then rebuild:

```sh
python3 tools/build.py
```

`tools/build.py` (standard library only) adds the shared head, header and footer, the release call to action
from `config/release.json`, and writes `sitemap.xml`. Commit the source and the generated files together.

**Support and privacy wording belongs to the Bitz repository** (`docs/site/support.html` and
`docs/site/privacy.html`, checked against the app's code). Re-import it verbatim, then rebuild:

```sh
python3 tools/import_bitz_docs.py ../Bitz
python3 tools/build.py
```

The importer only changes layout (links, anchors, table of contents) and adds the site's
"Charging Room and StandBy" section, written from the app's own strings. `config/bitz-docs-source.json` records
which source file versions were imported.

## Release button

`config/release.json` holds Bitz's App Store status. See [docs/RELEASE_BUTTON.md](docs/RELEASE_BUTTON.md).

## Art

All Bitz art is exported from the app's own pixel renderer by `tools/bitz-art` and optimized losslessly by
`tools/optimize_png.py`. Sources and licensing: [docs/ASSETS.md](docs/ASSETS.md).

## Rules for this site

- No analytics, ads, cookies, tracking pixels, third-party embeds, web fonts or external scripts. The Bitz
  privacy policy promises this for the Bitz pages; each page also sets a Content-Security-Policy that only
  allows this site's own files.
- Essential content works without JavaScript; the interactive stage falls back to a still picture.
- Cloudflare's Email Address Obfuscation is on for the domain. Each page body is wrapped in
  `<!--email_off-->` so addresses stay plain `mailto:` links without a script.
- `src/`, `tools/`, `config/` and `docs/` are excluded from the published site by `_config.yml`.
