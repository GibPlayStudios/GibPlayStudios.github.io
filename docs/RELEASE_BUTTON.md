# Bitz release button

`config/release.json` decides what the site says about availability.

```json
{
  "status": "coming-soon",
  "appStoreId": "6824056606",
  "appStoreUrl": "https://apps.apple.com/app/id6824056606",
  "devices": "iPhone and iPad",
  "devicesTr": "iPhone ve iPad",
  "minimumOS": "iOS 17"
}
```

- `coming-soon` (now): every Bitz call to action says "Coming soon to the App Store" / "Çok yakında App
  Store'da", for iPhone and iPad, iOS 17 or later, with no download link. Nothing links to `#`.
- `available`: the official badge links to `appStoreUrl` on `/`, `/tr/`, `/Bitz/` and `/Bitz/tr/`.

## Switching to `available`

1. Confirm Bitz is publicly on the App Store: `https://apps.apple.com/app/id6824056606` loads the product page,
   and `https://itunes.apple.com/lookup?id=6824056606` returns one result. (On 2026-10-18 the page returned 404
   and the lookup returned no results.)
2. Download Apple's official "Download on the App Store" badges (black, English and Turkish) from Apple's
   marketing resources (https://developer.apple.com/app-store/marketing/guidelines/ links to them). Save them
   unmodified as `assets/img/app-store-badge-en.svg` and `assets/img/app-store-badge-tr.svg`. Follow Apple's
   guidelines: don't recolour, crop or animate the badge, keep clear space around it, and keep it at least as
   prominent as any other call to action. Note Apple's legal line if required ("App Store is a service mark of
   Apple Inc.").
3. Set `"status": "available"` (and the final `appStoreUrl` if Apple's URL differs, for example with the app
   name slug), then run `python3 tools/build.py`. The build refuses to publish `available` without both badge
   files.
4. Review the purchase wording on `/Bitz/` ("Bitz will be free to download") and change it to present tense if
   the price is still Free.
5. Commit, push, and check the live pages.

No structured data claims availability, ratings or prices; keep it that way.
