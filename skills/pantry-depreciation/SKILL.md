---
name: pantry-depreciation
version: 1.0.0
description: "Expire kb/pantry.md items past category shelf-life windows."
author: Chef Pierre
license: MIT
---

# Pantry Depreciation (household-approved)

## When to Use

Load whenever reading, writing, or consulting `kb/pantry.md` — recipe
matching, shopping lists, snack suggestions, or pantry updates.

When reading or writing `kb/pantry.md`, treat items as GONE once their
category window has elapsed since the last confirmed date (added / used /
confirmed note on the line). Today's context date minus that date > window =
depreciated. Never assume a depreciated item is still there.

## Shelf-life windows (days since last confirmation)

- **Shelf-stable, unopened**: indefinite — pasta, rice, canned goods, sauces,
  oils, spices, flour, sugar, honey, unopened drinks.
- **Crackers & chips (opened or bagged snack formats)**: **14 days** — they go
  stale. Same for pretzels, snack mixes, popcorn bags.
- **Bread & bakery**: 7 — bread, buns, croissants, English muffins, tortillas,
  doughnut muffins.
- **Fresh veg, fruit & herbs**: 7 — peppers, greens, tomatoes, avocados,
  mushrooms, berries, lemons/limes. Root veg (potatoes, onions, garlic,
  shallots, ginger): **21**.
- **Eggs**: 21.
- **Dairy & opened fridge items**: 14 — cream, milk, yogurt cups, sliced/
  shredded cheese, dips, cream cheese, sour cream, deli salads.
- **Hard cheese & butter**: 30 — parmesan wedge, cheddar blocks, butter.
- **Deli & fresh meat (fridge)**: 7 — salami packs, sliced roast beef,
  opened bacon/sausage. **Freezer proteins: never decay.**
- **Protein shakes & opened/ready drinks**: 14 per bottle; multipacks decay
  by consumption rate (below).
- **Cooked leftovers**: 4.
- Unknown product: default 14, ask once.

## Consumption-rate projection (multipacks)

Assume normal household eating pace for 2 adults — project, don't wait for
confirmation:

- Sparkling water (bubly/LaCroix/Waterloo 8 pk): ~1 can/adult/day → an 8 pk
  lasts ~4 days; a 12 pk ~1 week.
- Protein shakes (Bolthouse/Core Power 14–15 oz): ~1/day combined → a 3-pack
  lasts ~3–4 days.
- Protein/granola bars, rice pudding cups, yogurt cups: ~1–2/day combined →
  a 4–5 pack lasts ~3 days.
- Bags of chips/crackers (once the pack is opened): assume finished within
  ~10–14 days regardless of size.
- Deli packs (salami, roast beef, sliced cheese): finished in ~5–7 days.

If projected depletion beats the category window, the earlier date wins.

## Lifecycle: flag → 30 days → delete (household rule)

- Applies to **fridge/perishable items only** — never to shelf-stable items
  (pantry dry goods, canned/jarred, spices, oils, sauces, unopened drinks),
  which stay on the list indefinitely once struck or not.
- Perishable item lifecycle: **purchased/confirmed → flagged assumed-OUT on
  its category window (table above) → 30 days after flagging, the line is
  deleted from the file by default.** No further confirmation needed to
  delete; deletion is routine hygiene, not a judgment.
- The struck line is the grace record: keep the last-confirmed date in the
  strike note so the 30-day delete date is computable.
- A user confirmation during the grace window un-strikes the line and
  re-stamps the clock instead.

## Mechanics

1. On each pantry consult, flag depreciated items as **assumed OUT** (strike
   the line with `~~item~~ — **assumed OUT (<reason/date)>**`).
2. **Never silently exclude a depreciated item (household rule).** When
   proposing recipes or plans, list every recipe as normal, but append a
   **Confirm/Replace** note for each recipe calling out any ingredient whose
   pantry line is depreciated. Do not pre-filter the recipe list — let the
   household decide. A confirmation re-stamps the date → fresh window.
3. New entries get their date stamped on add; pick the category at entry.
5. In pantry accounting (counts, diffs, cart lists) a depreciated item is
   not counted as on hand — but recipe *suggestions* follow rule 2: show
   the recipe and flag the ingredient for confirm/replace instead of
   dropping it.
6. Depreciated staples (work snacks, shakes, crackers, sparkling water):
   surface as restock suggestions in the next shopping conversation.
