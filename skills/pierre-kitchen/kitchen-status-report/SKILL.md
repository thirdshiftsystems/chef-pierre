---
name: kitchen-status-report
description: "Use when the user asks for a kitchen status or ops update."
version: 1.0.0
author: chef_pierre
license: MIT
platforms: [linux, macos]
---

# Kitchen Status Report

Pierre's routine for the recurring "give me a full executive status update of
your operation" request: recipe-bank numbers and titles, current pantry
contents, and a suggested next cart. Distinct from the everyday routines in
`pierre-kitchen` (ingredient matching, list building, receipt parsing) — this
skill is the *reporting* layer that reads those same files and presents them.

`pierre-kitchen` is the companion: consult it for the underlying filing rules,
pantry-truth rules, the French-gloss rule, and the hard NOs. Never restate
those here; just honour them.

## Report shape — one message, four sections, in this order

Slack renders **no tables** — headings, bold labels, and bullets only. Put the
count in the heading so the reader can check the arithmetic without counting.

1. **The vault** — dinner-main count, then every title grouped by protein.
2. **Pantry** — current contents by section, with freshness and compliance flags.
3. **Suggested cart** — missing/consumed items only, grouped by aisle.
4. **Accommodation shortlist** — any active household constraint (see below).

Per-section detail and the full bucket taxonomy: `references/ops-status-report.md`.

## Standing rules

- **Kitchen talk lives in the household's chat channel** (e.g. Slack `#kitchen` —
  whatever channel the household uses; see `kb/house_rules.md`). When a household
  member says something is "in Kitchen", asks whether you saw a comment, or shares
  a meal photo for the record, read that channel first. Recipe ballots post to the
  voting channel.

- **Main count = file count MINUS non-mains — and reconcile it, don't just
  `grep Category`.** Some cards are missing their `Category:` line entirely, so a
  tally of `Category: **Dinner main**` UNDERCOUNTS. Tagged mains + untagged main
  files + non-mains must sum to the file total; if it doesn't, list the files with
  no `Category:` line, classify each by its title, then report the number. State
  the count, the file total, and the non-main names so the arithmetic is visible.
- **Report the count from disk, not from the cron header.** The announced running
  total and the files drift apart; the file count wins.
- **Group titles by protein** with sub-buckets (burgers, sausage, bacon-cured,
  chops vs tenderloin). Report the apps/sides parallel bank separately and say it
  does NOT count toward the main total.
- **Age the `*soon*` tags.** `*soon*` flags carry the date the item was added;
  anything tagged 4–5 days ago is past its window. Surface that cluster as
  "use-now or gone" and offer to strike it, rather than presenting stale items as
  on hand.
- **Compliance sweep every time.** Name any pantry item that violates a standing
  rule (non-citrus fruit preserves are a hard NO) and offer to remove it. The
  user's pantry list is truth — never silently delete a line from it.
- **"Receipts in the vault" = the dated order batches in `kb/pantry.md`.** There is
  no separate receipt archive in the profile; the `added YYYY-MM-DD` clusters ARE
  the receipt record. Build the restock list by grouping those batches and
  re-listing their consumables. Receipt images pasted in chat live outside the
  profile. If the pantry holds fewer dated batches than the user's phrasing implies,
  name the batches you used and offer to redo from a different one.
- **Say your source reading out loud, then proceed.** When the request is
  ambiguous, state the reading you chose in one clause and deliver the report — do
  not stall the whole thing on a clarifying question.
- **Never add to the Kroger cart without an explicit yes.** End the report
  with the offer; the confirm-first rule in the `kroger-cart` skill governs.
- **French still gets glossed inline**, same as everywhere else.

## Limited-mobility mode (injury / surgery recovery)

When a household member is temporarily down an arm or on restricted activity,
adapt the suggestions, not the tone. Ask for — or infer — the affected week, and
apply all three:

- **Food must need no knife, no can opener, no two-handed jar.** Prefer pull-tab
  pouches over cans, deli sliced meat + sliced cheese roll-ups, string cheese,
  single-serve yogurt / cottage cheese / rice-pudding cups, pre-peeled hard-cooked
  eggs, tuna pouches + crackers, rotisserie chicken, protein shakes, electrolyte
  packets.
- **Route everything through the Ninja Foodi XL / toaster oven / Traeger** rather
  than the stove — press-a-button beats a pan, and there is no microwave to fall
  back on.
- **Keep dinners one-pan / sheet-pan / Instant Pot** so the *other* household
  member isn't stuck at the stove — and say that as the reason, naming banked
  dishes that fit.
- **Add a one-arm kit to the cart:** silicone jar opener, pre-cut veg tray,
  squeeze-bottle condiments, disposable plates.
- **Restate the dairy rule** on any recovery/comfort list: cooking dairy is
  **heavy cream, never milk** — milk is off the household list entirely.

## Pitfalls

- **Don't let the report become a wall of undifferentiated text.** The value is in
  the grouping and the flags; a flat list of 85 titles reads as noise.
- **Don't offer a cart that re-buys what the pantry already shows.** Diff first;
  missing/consumed items only.
- **Don't present the bank as growing while ballots are still open.** Name the
  rosters still awaiting a voter, and who owes what.
