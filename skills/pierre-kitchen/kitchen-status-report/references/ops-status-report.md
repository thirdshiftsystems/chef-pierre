# Ops Status Report — section-by-section detail

Companion to `kitchen-status-report` SKILL.md. Load when actually assembling the
report.

## Section 1 — The vault

**Count.** `ls kb/recipes/*.md | wc -l` gives the file total, which includes
non-mains. Subtract them, and **reconcile**: tagged mains + untagged mains +
non-mains must equal the file total. A card can be missing its `Category:` line,
so the grep tally can undercount by several; find the untagged files with
`grep -L 'Category:' kb/recipes/*.md`, classify each by its H1 title, and report
the reconciled number plus the non-main names.

**Grouping buckets that read well:**

- **Beef** — Burgers; Steaks; Beef mains (braises, bowls, tacos, salads)
- **Pork** — Chops; Tenderloin; Other pork (adobo, carnitas, meatballs, schnitzel);
  Sausage; Bacon/prosciutto-forward
- **Chicken** — cutlets, thighs, sheet-pan, stir-fry
- **Seafood** — shrimp, fish, scallops
- **Eggs & Meatless** — eggs, paneer, tofu, halloumi, chickpeas, polenta, pizza

Flag in the heading any banked dish that is currently out of rotation (e.g. a
snoozed dish, or one inside the 10-day no-repeat window) so the numbers don't
imply it's pitchable today.

## Section 2 — Pantry

Walk `kb/pantry.md` section by section (Proteins / Fridge / Freezer / Pantry &
Dry Goods / Spices / Sauces / Baking / Snacks / Wine / Appliances). Keep it
readable: list the items, but let the **flags** carry the analysis.

Flags worth raising, in priority order:

1. **Rule violations** — anything that trips a standing hard NO. Offer to remove;
   never remove unilaterally.
2. **Expiring leftovers** — read `kb/leftovers.md` and compute the expiry against
   the current timestamp. Say "eat it tonight or bin it" with the clock time.
3. **The aged `*soon*` cluster** — group the `*soon*` items by the date they were
   added; those at 4–5 days are past it. Present as "use-now or gone".
4. **Staples worth noting** — an absent herb or aromatics the pending dishes need.

Always state the pantry file's `_Last updated_` date so the reader knows how
fresh the picture is.

## Section 3 — Suggested cart

Sources, in order: (a) the dated receipt batches in `kb/pantry.md`, (b) the
household's regulars, (c) the gaps the week's dishes need, (d) any accommodation
constraint.

Aisles that work on Slack: **Meat & Seafood / Dairy / Produce / Pantry / Snacks &
treats / One-arm kit** (or the relevant accommodation). Snacks and treats belong
on the list like anything else — this household always lists them — but keep them
in their own block so the real restock items stay visible.

Two content rules that catch people out:

- **Never list milk.** Any dairy-liquid in a recipe is heavy cream. Check the list
  before sending; milk must not appear.
- **Work snacks are a standing line** (sliced roast beef + sliced cheese wraps,
  crackers, string cheese) and stay on every list.

Close with the confirm-first offer: the cart is not touched until the user says
yes, and they pay in the app.

## Section 4 — Accommodation shortlist

Only present when a constraint is active. If one is, make it concrete and
one-handed — a short bullet list of things the person can eat or open alone,
plus the dinner-shape note for whoever is cooking.

## Tone

Executive means *checkable*, not *short for its own sake*. Counts in headings,
names in full, flags bolded. French flavour is fine — glossed inline, always.
