---
name: recipe-vote-poll
description: "Recipe vote poll: research 5 recipes, vote, save 8/10+ winners."
version: 1.0.0
author: chef_pierre
license: MIT
platforms: [linux, macos]
---

# Recipe Vote Poll

The weekly Friday evening poll that keeps the household's dinner rotation
diverse. Pierre researches 5 recipes himself, the household votes 1–10, and anything
averaging **8.0/10 or higher** gets saved to `kb/recipes/`.

## When to use
- The scheduled cron job `Weekly Friday Recipe Vote` fires (see `cronjob list`).
- A household member asks for a recipe poll / vote / "new recipes to try".

## Workflow

### 1. Research the candidates yourself
Use `web_search` + `web_extract`; open each candidate's page before pitching it
and cite only pages you opened. Read `kb/house_rules.md`, `kb/recipes/` and
`kb/feedback_log.md` first. The picks must satisfy:

- EXACTLY 5 recipes (scheduled job) or 6–8 (one-off), diverse proteins —
  beef, chicken, pork, seafood, eggs, and at least one vegetarian/plant-based.
- Do NOT restrict to what's in the pantry — open protein selection.
- Household constraints: **read `kb/house_rules.md` for the household's dietary
  restrictions and hard NOs** (fruit rules, flagged vegetables, preservatives —
  whatever the house rules record);
  no brothy soups (only thick/hearty); no microwave (toaster oven or stovetop);
  low-fuss, one-pan/sheet-pan preferred; Traeger smoker + Ninja Foodi XL
 available; include one quick ~20 min solo meal.
 - Source preferences: prioritize NYT Cooking and America's Test Kitchen (ATK)
 free content; other reliable outlets (USDA, Mayo Clinic, EatingWell,
 Serious Eats) acceptable. Salmon/seafood only occasionally.
 - HARD NOs (never offer):
 - **Bone-in chicken EXCEPT thighs** (breasts, drumsticks, whole) — not liked;
   bone-in *thighs* ARE fine.
 - **Salmon** — not liked; suggest rarely/minimally, prefer shrimp or other
   seafood (cod, shrimp, scallops) when a seafood dish is needed.
 - **Shakshuka is NOT banned** — it was over-suggested and fatigued the
   household; snoozed 60 days until 2026-11-05. Never list it as a hard NO.
- Output format: numbered list with name, 2-line description, key ingredients
  (no quantities), cook time, why it's healthy, 1–2 source URLs.

Paywalled pages (NYT, Cook's Illustrated): no logins; use the free version or an
equivalent reliable recipe and say so.

### 2. Present the ballot
Post a numbered ballot with recipe name, protein tag, 2-line description,
cook time, and source. End with clear voting instructions: reply with scores
like `1: 8, 2: 6...` — both voters score, we average, 8.0+ gets saved.

Flag any recipe ingredients that conflict with the household's flagged
sometimes-bothersome items (see `kb/house_rules.md`) and offer swaps. Hard-NO
items in the house rules are not swaps — they disqualify the pick.

### 3. Collect votes & average
- Track each voter's scores. If a recipe gets only one vote, that vote stands.
- Average = sum of scores / number of voters for that recipe.
- Threshold: **≥ 8.0** saves; below stays on the bench (may be re-pitched).

### 4. Save winners
Write a markdown file to `kb/recipes/<slug>.md` following the existing recipe
format: title, "Pierre-saved classic (voted X/10 by the household, DATE)",
serves/time, source URL, ingredients, steps, and Notes covering: dietary-check
flags (per `kb/house_rules.md`), no-microwave workaround, internal temp safety, household-favorite swaps
(tri tip/ribeye, Traeger options).

Verify the file landed with `read_file` after writing.

## Pitfalls
- **VET EVERY BALLOT AGAINST HARD-NOs BEFORE POSTING — never after votes arrive.** Screen each of your 5 picks against the HARD NOs in `kb/house_rules.md` (dietary restrictions, protein preferences, snoozed dishes) plus the sometimes-bothersome list. Any banned item = regenerate that slot and re-vet. A posted ballot must contain ZERO banned dishes. If one slips through (scheduler hiccup, etc.), the ballot is VOID and must be scrapped and re-run rather than tallied — do not "save the good ones" off a tainted ballot.
- Never handle user passwords or log into paywalled sites (Cook's Illustrated,
  NYT) — crawl only free tiers; users paste subscriber-only recipes manually.
- Never invent pantry contents — diff shopping lists against `kb/pantry.md`.
- Salmon/seafood: occasional only.
- Check memory before finalizing: preferences evolve — re-read `kb/house_rules.md`
  rather than trusting old blanket bans.
- HARD NOs from household feedback (never re-pitch): apply the current list in
  `kb/house_rules.md` (e.g. **bone-in chicken EXCEPT thighs** if recorded —
  thighs ARE fine; disliked proteins are suggest-rarely). **Shakshuka is NOT a
  hard NO** — an over-suggested dish is snoozed, not banned (see `kb/snoozed.md`).
