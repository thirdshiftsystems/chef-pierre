# Restaurant Dish Recreation (no label exists)

Depth notes for the menu-spec path. Read when the user names a restaurant or
food-truck dish and wants it recreated at home.

## Source ladder (in order — stop at the first that gives a real build spec)

1. **The restaurant's own website menu page.** Independently owned places
   frequently publish the entire component list in the item blurb. This is the
   single highest-value source: it names the base, protein, vegetables,
   garnish, the signature sauce options, and any stated claims (gluten free,
   dairy free, zero refined sugar) that constrain the reconstruction.
2. **Delivery-platform listings** — Grubhub, DoorDash, order.online, tryotter,
   CaterCow. Good for itemization, portion size, sauce names/variants, and side
   items. Their pages usually render fine to `web_extract` even when search
   engines bot-block.
3. **Review sites / aggregators** (Yelp, ClassPass, catering menus) — mostly
   for confirming sauce names and popular variants, not for build specs.
4. Wayback only if the menu page has been changed or removed since.

Difference from packaged products: there is no ingredient statement and no
label image, so `vision_analyze` on a label is not part of this path.

## Turning the blurb into a recipe

Parse the description into ordered layers:
- **base** (grain / cabbage / greens) and how it is seasoned
- **protein** and its cooking method — read the words: "slow cooked" and
  "hand-pulled" mean braise, not sear; that single choice drives the timeline
- **vegetables** and their texture role (steamed soft vs raw crunch)
- **crunch / aromatic elements** (nuts, fried shallot, water chestnuts)
- **sauce** — usually named, rarely formulated

Then identify the **personality element** — the one component the reviews keep
raving about (often an oil, crisp, or sauce). Build that one first and in batch
quantity; it is what makes or breaks the copycat.

Sauce names are a strong signal but not a formula. Reconstruct each from the
cuisine's technique library (`culinary-techniques/`) and offer them as separate
small mixes so the household can pick.

## Worked example — Umami Express (Sacramento) wagyu rice & cabbage bowl

Their own menu page gave the full spec: shredded cabbage + heirloom forbidden &
brown rice (shiitake-garlic seasoned) + slow-cooked hand-pulled wagyu +
water chestnuts + steamed broccoli/cauliflower/carrots + green onion + sesame +
house Sichuan chili oil crunch + a choice of three signature sauces, plus the
claims gluten-free / dairy-free / zero refined sugar.

Delivery listings supplied the sauce names (Lemon Garlic Soy, Spicy Orange
Sesame, Garlic Sesame Soy) and the ¼ lb-per-bowl portion.

Reconstruction decisions:
- The "peppered crunchy oil" the user loved = chili crisp with **ground Sichuan
  peppercorn** for the numbing note + fried garlic/shallot + sesame + crushed
  nuts. Batch component, jarred, keeps about a month.
- "Hand-pulled / slow cooked" ⇒ braise, don't sear: low oven, pull-apart
  internal 195–203 °F — state the number with its source, verified
  before cooking.
- "Zero refined sugar" ⇒ honey, matching the label claim.
- User picked the Lemon Garlic Soy variant → recorded as the house default in
  the recipe file.

## Honesty framing (do not skip)

Say plainly: reconstructed from the restaurant's published menu spec plus
standard technique — "how I'd build it", a copycat, not their formula. Do not
imply the restaurant's actual recipe was obtained. If the user frames it as
"steal the recipe", answer in the same playful register but land the caveat in
the same breath.

## Handoff

End at the standard pipeline: safety-critical numbers → verify before cooking;
pantry diff → shopping list (missing only); save the recipe so it is
pantry-matchable next time; log the cook and date the rating once it is made.
