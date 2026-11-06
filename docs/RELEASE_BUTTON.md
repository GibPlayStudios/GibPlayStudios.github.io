# Bitz release state

Bitz is on the App Store. `config/release.json` holds what the site says about it.

```json
{
  "status": "available",
  "appStoreId": "6824056606",
  "appStoreUrl": "https://apps.apple.com/us/app/bitz-pixel-cat/id6824056606",
  "appStoreUrlTr": "https://apps.apple.com/tr/app/bitz-piksel-kedi/id6824056606?l=tr",
  "devices": "iPhone and iPad",
  "devicesTr": "iPhone ve iPad",
  "minimumOS": "iOS or iPadOS 17",
  "minimumOSTr": "iOS veya iPadOS 17"
}
```

- English pages link to the US listing and Turkish pages to the Turkish listing. `?l=tr` shows the listing's Turkish
  text in a web browser; without it the Turkish storefront's web page is in English. Neither URL redirects or carries
  tracking parameters.
- `tools/build.py` puts the badge on `/`, `/tr/`, `/Bitz/` and `/Bitz/tr/` (hero and end of page on the Bitz pages), a
  text link in the studio hero, and an App Store link in every footer. It refuses any status other than `available`
  and stops if a badge file is missing.
- If the minimum OS or the devices change, compare them with the public listing, then edit this file and rebuild.

## Badges

`assets/img/app-store-badge-en.svg` and `assets/img/app-store-badge-tr.svg` are Apple's black "Download on the App
Store" badges, unmodified, from Apple's marketing tools (linked from
https://developer.apple.com/app-store/marketing/guidelines/):

- `https://toolbox.marketingtools.apple.com/api/v2/badges/download-on-the-app-store/black/en-us`
- `https://toolbox.marketingtools.apple.com/api/v2/badges/download-on-the-app-store/black/tr-tr`

Apple's rules used here: the badge is at least 40px high on screen (the site uses 48px), with clear space of a quarter
of its height (12px). Don't recolour, crop, animate or translate it. Every footer carries Apple's credit line.

## What the site doesn't claim

No page or structured data states a price in currency, a rating or a download count; keep it that way. The site says
"free to download, with optional in-app purchases". The listing also shows Mac and Apple Vision compatibility
("Designed for iPad. Not verified for macOS."), but the site only names iPhone and iPad.
