# Label Research via Wayback Machine — worked technique

Goal: get the FULL ingredient statement of a packaged product when the
manufacturer site blocks scraping. Validated on Giovanni Rana Fettuccine
Mushroom Sauce with Italian Sausage (2026-08).

## Why the direct routes fail

- DuckDuckGo HTML (`html.duckduckgo.com`) → captcha wall
- Google → `/sorry` block page
- Mojeek → 403
- Walmart search → "Robot or human?" hold-button challenge
- Target search → hangs on a loading dialog
- Instacart search URL → 404
- Manufacturer site (giovanniranausa.com) → `AccessDenied` XML via curl AND
  empty `<div>` via browser (JS-gated + CDN-blocked)
- Bing → misreads brand context ("Giovanni Rana fettuccine" → NASA results)

## The working path

### 1. Discover archived product URLs with the CDX API

```bash
# list archived URLs on the domain matching a pattern (collapse dupes)
curl -s "https://web.archive.org/cdx/search/cdx?url=giovanniranausa.com*&output=text&fl=original&collapse=urlkey&limit=200&filter=original:.*fettuccine.*"
```

Real result: found `https://www.giovanniranausa.com/products/fettuccine-sausage-mushrooms.html`
(not the guessed `/fettuccine-with-sausage-and-mushroom/` slug — guessing slugs wastes time).

### 2. Pick a snapshot and fetch the archived page

```bash
# list snapshots (timestamp, status, digest)
curl -s "https://web.archive.org/cdx/search/cdx?url=giovanniranausa.com/products/fettuccine-sausage-mushrooms.html&output=text&fl=timestamp,statuscode,digest&limit=20"
# fetch a specific snapshot (20250520071400 worked; used the raw page text)
curl -s -L "https://web.archive.org/web/20250520071400/https://www.giovanniranausa.com/products/fettuccine-sausage-mushrooms.html" -o /tmp/page.html
# strip tags to read product description
sed 's/<[^>]*>//g' /tmp/page.html | grep -v '^\s*$' | grep -iE 'sauce|cream|ingredient|mushroom'
```

Product description extracted: "Fettuccine tossed in an earthy creamy Portobello
and Cremini Mushroom-Parm sauce with Sausage crumbles." Good, but description
≠ ingredient statement. Need the nutrition label image.

### 3. Find the nutrition-label image in the archived page source

Nutrition facts load in a Bootstrap-style modal; the `<img>` inside
`id="nutrition-modal"` holds the label. **Pitfall:** in the 2025 snapshot the
modal pointed at a meatball-kit image (site bug). The 2022 snapshot had the
correct one:

```python
# python one-liner: find img src inside the nutrition-modal block
idx = html.find('nutrition-modal')
# grep the block for src="..."
```

### 4. Fetch the label image — original CDN beats the Wayback proxy

Wayback `im_/` proxy URLs for images often 404 (asset not archived). The
ORIGINAL CDN URL is frequently still live:

```bash
# wayback proxy: 404
curl -s -L "https://web.archive.org/web/20221007160316im_/https://images.ctfassets.net/..." -o /tmp/label.jpg
# direct CDN: 200, real JPEG (1275x1650)
curl -s -L "https://images.ctfassets.net/xhwawwjr0s5c/.../500929_Sausage___Mushroom_Kit_38oz_NFIL_V4_page-0001.jpg" -o /tmp/rana_label.jpg
file /tmp/rana_label.jpg   # confirm JPEG, not HTML error body
```

### 5. Read the label with vision_analyze

```python
vision_analyze(image_url="/tmp/rana_label.jpg",
  question="Read the FULL ingredient list ... I need every ingredient ...")
```

Ask specifically whether the label splits pasta vs. sauce ingredients (Rana's
does — separate statements).

## Extracted reference data (Rana Sausage & Mushroom fettuccine, 38 oz)

Sauce: WATER, MUSHROOMS, HEAVY CREAM (CREAM, MILK), ITALIAN SAUSAGE (PORK,
WATER, SPICES, SEA SALT, DRIED CANE SYRUP, RED BELL PEPPER POWDER, DRIED
GARLIC, SALT, NATURAL FLAVORS), ONIONS, PARMESAN CHEESE, ≤2% SUNFLOWER OIL,
MODIFIED FOOD STARCH, NATURAL FLAVORS, AUTOLYZED YEAST EXTRACT, GARLIC, SPICE,
SALT, BLACK PEPPER, CORN MALTODEXTRIN, NONFAT DRY MILK.
Pasta: DURUM WHEAT FLOUR, EGGS, WATER.
Allergens: EGG, MILK, WHEAT. ~320 cal/serving, 6 servings.

Recreation mapping used in the delivered recipe:
- autolyzed yeast extract + corn maltodextrin → ½ tsp fish sauce
- modified food starch → natural reduction + pasta water finish
- dried cane syrup → omitted
- heavy cream + parmesan + onions + garlic + pepper + oregano + red pepper
  flakes = the visible flavor skeleton
