# Chef Pierre — your AI household chef for Hermes

Chef Pierre is a fully-configured kitchen agent personality for
[Hermes Agent](https://hermes-agent.nousresearch.com). Install these skills
and your Hermes becomes a chef who plans dinners, runs recipe programs,
maintains a living pantry, builds Kroger grocery carts, teaches cooking
technique, and runs his own weekly pantry-hygiene schedule.

He works for **the whole household**: he honors each family member's dietary
restrictions and preferences, and he lives in your Slack or Discord so every
family member can talk to him directly — including the weekly recipe vote,
where everyone scores the proposed dinners and he tallies the winners.

## What Chef Pierre can do

**Core kitchen (pierre-kitchen)**
- Match ingredients you have to recipes; suggest diverse dinners
  (protein + cooking format varied) with a rotation system so nothing repeats
- Maintain a `kb/` knowledge base: pantry, recipes, feedback log, leftovers
- Produce a kitchen ops/status report on demand (kitchen-status-report)

**Pantry intelligence (pantry-depreciation)**
- Every pantry item gets a shelf-life window by category (bread 7d, produce 7d,
  dairy 14d, eggs 21d, root veg 21d, hard cheese 30d, freezer = never, etc.)
- Perishables past their window are flagged "assumed OUT" — but never silently
  dropped: recipes list a Confirm/Replace tag for any questionable ingredient
- Flagged items are auto-deleted 30 days after flagging (fridge items only —
  shelf-stable goods stay forever)
- Multipacks decay by consumption-rate projection (e.g. an 8-pack of sparkling
  water ≈ 4 days for two adults)

**Shopping (kroger-cart)**
- The "grill me" shopping session: instead of waiting for a list, the chef
  interviews you — cravings, recipe prompts, restock gaps, and a full-store
  sweep of every Kroger department including household, cleaning, and pharmacy
- Recipe-first carts: he proposes 5 diverse recipes, you pick, he diffs the
  pantry, and only the missing items go in the cart
- Adds items to your real Kroger/Ralphs cart via the public Kroger API.
  Add-only and confirm-first — checkout is always yours, in the app

**Multi-member household support**
- Honors each family member's dietary restrictions and preferences — he
  maintains per-person notes (allergies, intolerances, hard NOs, favorites)
  in `kb/house_rules.md` and flags any recipe that conflicts before it ever
  reaches a ballot or a plate
- Interacts with the entire household, not just one admin — via Slack or
  Discord, every family member can talk to him, and the recipe-vote program
  lets everyone score the week's proposed dinners; he tallies the votes and
  saves the winners (he'll even confirm voter identity if two people share
  an account)

**Recipes (recipe)**
- Save recipes from any URL with real ingredients + method extracted
  (recipe-source-extraction)
- Reverse-engineer packaged products and restaurant dishes, including using
  Wayback Machine label research (packaged-recipe-recreation)
- Run a household recipe-vote program: research candidates, poll the family,
  auto-save winners (recipe-vote-poll / recipe-vote-schedule)
- **Recipe Blitz onboarding (recipe-blitz, new in v1.2):** when a new
  household's recipe vault has fewer than 50 cards, Pierre offers a blitz of
  frequent family votes (3 recipes per vote, twice a week by default). He asks
  how many cards to collect (50 suggested) and how often to vote, saves every
  recipe that scores 8/10 or higher, and stops on his own when the vault is full
- Skillet egg-in-a-hole technique card (toad-in-a-hole)

**Cooking technique (culinary-techniques)**
- 18 deep technique + pantry cards across 8 cuisines: Chinese, Indian,
  Japanese, Korean, Mexican, Middle Eastern, Peruvian, Thai — covering wok
  hei, tadka, dashi, ssam, moles, baharat, ceviche, curry pastes, and more

**Utility (productivity)**
- Scan grocery receipts with vision/OCR and update the pantry automatically
  (receipt-to-pantry)

**Automation (cron — recreate yourself, spec included)**
- `pantry-depreciation-sweep`: every Sunday 9 AM the chef flags expired
  perishables, deletes 30-day-old flags, and posts a summary to your chat

## Sample recipes

The `sample-recipes/` folder holds four starter recipes in the exact format
the recipe tools expect (copy them into your `kb/recipes/` to use them):
**Çılbır** (Turkish poached eggs with garlic yogurt & chili butter),
**Saganaki** (Greek flaming pan cheese — a Detroit classic),
**Detroit-style Coney Dogs**, and **Detroit-style Deep Dish Pizza**.  Whatupdoe.

## Installation

### 1. Install the skills
Copy the skill folders into your Hermes skills directory (per-profile:
`~/.hermes/profiles/<profile>/skills/`, or default `~/.hermes/skills/`):

```
cp -r skills/* ~/.hermes/skills/
```

Each folder is a standard Hermes skill (a `SKILL.md` plus optional scripts).
Hermes picks them up automatically.

### 2. Create the knowledge base (`kb/`)
The skills expect a per-household `kb/` folder next to your agent workspace:

- `kb/pantry.md` — the pantry truth (what's on hand, with dates). Start it
  with a simple list by section: Proteins / Fridge / Freezer / Pantry /
  Spices / Snacks. Date every entry.
- `kb/house_rules.md` — your household's food rules (dietary restrictions,
  dislikes, hard NOs, how you like to be talked to)
- `kb/recipes/` — one markdown file per recipe (the vote program and
  recipe-first carts draw from here)
- `kb/feedback_log.md` — dated notes on what the household liked/disliked
- Optional: `kb/snoozed.md` (recipes on pause), `kb/leftovers.md`

These stay private to your household — that's why they're not in this package.

### 3. (Optional) Set up the Kroger cart
Only needed if you want cart-building. Free, no payment access ever —
the API is add-to-cart only.

1. Create a developer account at https://developer.kroger.com and create a
   client app (product.compact + cart access).
2. Copy `scripts/kroger.py` somewhere stable, e.g.
   `~/.hermes/scripts/kroger/`, then create `creds.json` next to it
   (chmod 600):
   ```json
   {
     "client_id": "…",
     "client_secret": "…",
     "redirect_uri": "http://localhost:8787/callback",
     "scope": "product.compact",
     "location_id": "",
     "zip_code": "your zip"
   }
   ```
3. Find your store: `python3 kroger.py stores --zip <your zip>` — put the
   returned `location_id` into creds.json.
4. Authorize: `python3 kroger.py authorize` — open the printed URL in a
   browser that can reach the agent host's port 8787 (if your browser is on
   another machine, use an SSH tunnel:
   `ssh <user>@<agent-host> -L 8787:127.0.0.1:8787`). This writes
   `tokens.json` (chmod 600).
5. Sanity check: `python3 kroger.py config`

### 4. Recreate the weekly sweep (cron)
In Hermes, create one cron job (via `cronjob_manage` or your scheduler):

- **Schedule:** `every sunday 9am`
- **Skills:** `pantry-depreciation`
- **Deliver:** your chat
- **Prompt:** see `cron/pantry-depreciation-sweep.md` in this package

Then add your weekly recipe votes the same way: one job per vote day, with the
skills, schedule and prompt from `cron/recipe-vote.md`. Give scheduled jobs a
stable paid model; free models get rate limited at busy times, and a vote that
fails to post is a missed week.

### Settings (`config.yaml`)
`config.example.yaml` shows a setup that holds up well: a free main chat
model, several free backups from different vendors, a cheap paid model as the
last resort, and a separate vision model for photos. Free model catalogs
rotate, so check what your provider currently offers before copying the names.

### 5. Give him a soul (recommended)
Chef Pierre behaves best with a persona/system prompt defining: warm brief
Slack-style voice, kitchen-only scope, food-safety numbers only from cited
USDA/FDA sources, never spending money or checking out, and reading
`kb/house_rules.md` before suggesting anything. Start from `SOUL.example.md`:
copy it to `SOUL.md` in your Hermes profile folder and fill in the
`{{PLACEHOLDERS}}`. Household details (diets, appliances, dislikes) go in
`kb/house_rules.md`, not in the soul.

To turn on Recipe Blitz onboarding (v1.2), add a short paragraph to the soul
telling Pierre to check the recipe vault at the start of a conversation and,
when the `recipe-blitz` skill says so, offer the blitz once at the end of his
reply. The skill handles the rest: the setup questions, the vote schedule and
stopping at the target.

## Notes

- Everything is markdown + stdlib Python. No dependencies beyond Hermes and
  (optionally) a Kroger developer account.


