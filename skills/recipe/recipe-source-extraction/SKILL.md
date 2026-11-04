---
name: recipe-source-extraction
description: "Use when saving a recipe: pull real ingredients + method."
version: 1.0.0
author: chef_pierre
license: MIT
platforms: [linux, macos]
---

# Recipe Source Extraction

Saving a ballot winner to the recipe vault requires the source's **real
quantities and full method**, not the abbreviated blurb that appeared on the
ballot. `web_extract` does not handle the household's two primary sources, so
fetch them directly. `recipe-vote-poll` governs the poll itself; this skill
covers *getting the text and writing the file*.

## The extraction ladder (cheapest first)

```
1. web_extract            — try it; for NYT/EatingWell it returns "Website Not Supported"
2. curl + browser UA      — works for cooking.nytimes.com (HTTP 200, recipe in the HTML)
3. browser_navigate       — NOT installed on a headless server (no browser, to save RAM)
```

**On a headless machine there is no browser.** For a Cloudflare-blocked site (EatingWell and
similar), find the same dish from a source curl or web_extract can read, or ask the
user to paste the recipe. Never reconstruct quantities from memory.

Run `scripts/extract_recipe_text.py <url>` to do steps 2–3's parsing in one
shot; if it comes back thin, fall through to the manual routes below.

### NYT Cooking — curl works

```bash
curl -sL -A "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36" \
  --max-time 25 "$URL" -o /tmp/nyt.html
```

Then strip tags and slice around the body. Two things that cost time if
assumed wrongly:

- **There is no `application/ld+json` Recipe block** on these pages — don't
  write the parse to depend on it, and don't conclude the fetch failed when
  zero blocks come back.
- The recipe lives partway through a ~500 KB page in plain HTML. Locate it by
  searching for the section anchors (`Yield:`, `Ingredients`, `Preparation`)
  and printing a window around the hit rather than dumping the whole file:

```python
import re, html
h = open('/tmp/nyt.html', encoding='utf-8', errors='ignore').read()
i = h.find('Preparation')
seg = h[i-2500:i+3000]
print(html.unescape(re.sub(r'\n\s*\n+', '\n', re.sub(r'<[^>]+>', '\n', seg))))
```

Step text is chunked as `Step \n 1 \n ...`; read the window in two passes if
the last steps fall outside it. The nutrition line, yield and any `Tip`
(ingredient substitutions) sit in the same window and belong in the saved file.

<<<<<<< Updated upstream
### EatingWell (and other Cloudflare sites) — curl is blocked (browser route: not on the agent host)
=======
### EatingWell (and other Cloudflare sites) — curl is blocked (browser route: not on the droplet)
>>>>>>> Stashed changes

`curl` returns **403 + a JS interstitial**. Use `browser_navigate` instead: it
renders the page and the accessibility snapshot contains the full Ingredients
list and the numbered Directions. Long snapshots are **truncated in the tool
result with the complete text saved to a cache file** — the result says so:

> `[... truncated — full snapshot: read_file path="/.../cache/web/browser-snapshot-<hash>.txt" offset=289 limit=200]`

Continue with `read_file(path=<that file>, offset=<given>, limit=200)` to read
the remaining steps. That cache file is the reliable route for the back half of
a long recipe; don't re-navigate or screenshot to find it.

### Sunset (sunset.com) — curl works, and it hands you JSON-LD

`web_extract` on sunset.com returns the **Cloudflare Turnstile interstitial**
("Checking your Browser… / Verification failed") — but the recipe body often
trails along in the same content blob, so it *looks* like it worked. Don't trust
it; get the real HTML instead:

```bash
curl -sL -A "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36" \
  --max-time 30 "$URL" -o /tmp/sunset.html -w "HTTP:%{http_code} BYTES:%{size_download}\n"
```

HTTP 200 with the whole page (~150 KB), and — unlike NYT — it **does** carry a
full `application/ld+json` Recipe block: `recipeIngredient`, `recipeInstructions`
(HowToStep), `recipeYield`, `prepTime`/`cookTime`/`totalTime`, `nutrition`.
Confirm you got the real page by grepping an ingredient you expect
(`grep -o -m1 "3/4 cup low-fat Greek yogurt" /tmp/sunset.html`), then parse the
JSON-LD rather than stripping tags. Escaped em dashes appear as `\u2014`.

Page quirk: Sunset renders the steps **twice** — a "How to Make It" block and a
"Directions" block with identical text. Duplication, not two variants: extract
once.

## Writing the vault file

Path: `~/.hermes/profiles/<profile>/kb/recipes/<slug>.md` (the vault is NOT at
`~/kb/`). Follow the existing house format:

```
# Title

**Pierre original** — cooked YYYY-MM-DD, **X/10 (household rating)**.
One-line hook describing the dish — what makes it sing, what it uses up.

- **Time:** ~N min active | **Serves:** N | **Skillet:** stainless (tomatoes are acidic — NOT cast iron)
- **Dietary:** check `kb/house_rules.md` for the household's dietary restrictions

## Ingredients (all on hand)
## Method (cook live)
## Notes & history
```

### Save-when-suggested (household rule)
The household holds Pierre to having a card ready for any dish he proposed:
**"You suggested it, you should have it saved."** A dish Pierre previously
pitched and the household cooked or adopted — even one shared only as a food
photo of a recognizable classic (e.g. Soboro Don / そぼろ丼) — gets its vault
card written **directly from the dish name + Pierre's knowledge of the classic**
plus what the photo confirms. `Source:` then reads "Pierre original" or the
classic's standard lineage, not a URL. Do **not** treat a home-cooked classic
shared as a photo like a ballot winner that requires live web extraction; only
a “ballot blurb with no quantities” case must wait for a fetched source or a
paste.

Notes must cover, every time:
- **Dietary check** — name the ingredients and confirm they meet the household's
  dietary rules (`kb/house_rules.md`).
- **No-microwave** handling (toaster oven / stovetop / cold).
- **Internal temp safety** as a number, and "with a 3-minute rest" for whole cuts.
- **House swaps** already in play for this dish (cookware restriction, veggie
  swap, breaded-protein bake-then-air-fry rule, tri tip/ribeye preference).
- Carry the source's own `Tip` (e.g. lamb subs for beef) into Notes.

After writing each file: verify it on disk, then append a dated entry to
`kb/feedback_log.md` under `## Recent` with every item's scores, average,
banked-or-not, and the recounted bank total.

## Pitfalls

- **Sweep the SOURCE's ingredient list against the household hard-NOs before
  pitching or saving it — line by line, not by vibe.** Outside recipes are where
  the banned items hide, and they hide as *flavor* rather than as the featured
  ingredient: raisins / currants / sultanas are non-citrus dried fruit,
  pomegranate molasses is a fruit reduction, apricot-peach-mango preserves are
  a fruit product restricted in many households (check `kb/house_rules.md`). A
  headline that reads clean
  (`smashed beef kebab with cucumber yogurt`) can carry raisins and molasses two
  lines down. When one is found, offer the documented sub in the pitch rather
  than silently dropping the dish — pomegranate molasses → red-wine vinegar plus
  a pinch of sugar; raisins → omit. This sweep applies to a dish you are only
  *proposing*, not just to one being written into the vault.
- **Slice time into buckets, and say the count when the shelf is thin.** A
  protein-scoped request ("give me some ground beef recipes") wants: zero-shop
  now / *missing only X and Y* for a stop on the way home / one new sourced
  candidate / a plain number when the vault holds few cards for it. Anchor with
  `cd $HERMES_HOME/kb/recipes && grep -rilE "<ingredient>" . | sort` — titles
  mislead in both directions (a build-your-own *house burger* card is a
  ground-beef workhorse; *coconut beef curry* is not ground beef), so never build
  the shortlist from filenames.
- **Never write a vault file from the ballot blurb alone.** The ballot lists key
  ingredients with no quantities; a file cooked from it produces an unusable
  recipe. If extraction fails for a winner, tell the voters the source is
  fetch-blocked and ask for a paste — do not fill gaps with invented quantities.
- **Count the bank from disk.** The running count in the log drifts. Recount with
<<<<<<< Updated upstream
  `ls ~/.hermes/profiles/<profile>/kb/recipes/*.md | wc -l` and subtract the
=======
  `ls ~/.hermes/profiles/chef_pierre/kb/recipes/*.md | wc -l` and subtract the
>>>>>>> Stashed changes
  non-mains (grep `Category:` — sides and appetizers live in the same directory).
  Report mains-only and say so.
- **Hold the tally until both voters score.** One voter's numbers (even a 9)
  never bank a winner on their own; the two palates diverge often. Compute the
  average with a tool — decimal scores (`7.5`) decide bank-vs-bench.
- **Don't re-do a successful extract on a re-run.** Save winners as soon as both
  votes are in; re-voting or re-fetching the same ballot wastes the budget and
  risks drifting numbers.
