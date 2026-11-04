---
name: packaged-recipe-recreation
description: "Recreate a packaged product's or restaurant dish's recipe."
version: 1.0.1
author: curator
license: MIT
platforms: [linux, macos]
tags: [recipe, recreation, label-research, wayback, restaurant, menu-spec]
related_skills: [pierre-kitchen, receipt-to-pantry]
---

# Packaged Recipe Recreation

## When to Use

Use when the user asks to "match", "recreate", or "copy" the sauce/recipe of a
store-bought product (Rana fettuccine kit, frozen meal, restaurant signature).
Also use when the user names a packaged product and you need its real
ingredient list (e.g. for dietary/allergen reasoning).
Complements `pierre-kitchen` routines: this skill covers the research + recipe
construction; pantry matching and shopping lists follow pierre-kitchen rules.

Two distinct source paths — pick before you start searching:
- **Packaged product** (has a printed label) → steps 1–8 below; get the
  ingredient statement via retailer back-image + `vision_analyze` (primary)
  or Wayback (fallback).
- **Restaurant dish** (no label exists) → the menu-spec path; see
  "Restaurant dishes (no label to read)" and
  `references/restaurant-dish-recreation.md`.

A third, lighter path exists when the kit is **already bought** and the cook
just wants to elevate it tonight — no label research needed. See
"Doctoring a kit you already have" below.

## Doctoring a kit you already have

When the household already owns the packaged kit (or any creamy pasta kit) and
asks to "doctor it up" / "upgrade" it, do NOT relaunch the from-scratch
recreation machinery — the goal is a richer in-pan result from what's on hand.

**The validated playbook (order matters — cream → parmesan → garnish):**
1. **Heavy whipping cream** — start ¼ cup, stir into the hot sauce, add more
   only if you want it looser; cap at ½ cup. Splash it in right before
   serving, **off the heat**, so it warms through without separating. You are
   *velouté*-ing (velveting) the existing sauce, not building a cream sauce
   from scratch — over-creaming drowns the sausage/mushroom flavor.
2. **Parmesan** — ¼ cup shredded, folded in off the heat after the cream;
   up to ⅓ cup if indulgent, but NOT past that or it clumps gluey.
3. **Green onions** — thinly sliced over the top at the end for a fresh, sharp
   finish that cuts the richness.

Extents that were dialed in by the cook: 38 oz kit (serves two hungry) took
¼–½ cup cream and ¼–⅓ cup parm; the same treatment lifted the kit from a
6/10 to a keeper (a household cream-and-cheese trick). The playbook generalizes to
ANY creamy pasta kit — reuse it whenever the household buys one again.

## Workflow

1. **Identify the exact product.** If the brand makes several varieties, use
   the `clarify` tool to ask which one — sauce profiles differ dramatically
   (Alfredo vs. four-cheese vs. sausage-mushroom).
2. **Find the REAL ingredient list first. Never guess from memory.** Two paths,
   pick by what loads fastest:
   a. **Retailer back-of-package image** (Kroger, Safeway, Whole Foods) —
      these pages carry high-res `front/` and `back/` image URLs keyed by
      UPC (e.g. `kroger.com/product/images/large/back/<UPC>`). Grab the back
      URL and extract the full ingredient statement with `vision_analyze`
      directly — often faster than the manufacturer site, which 403s on both
      curl and browser.
   b. **Wayback Machine CDX** — fallback when retailer images aren't live.
      Exact commands in `references/label-research-wayback.md`.
3. **Extract the full ingredient statement** from the label image with
   `vision_analyze`. Note whether the label splits pasta vs. sauce ingredients
   (they usually do).
4. **Decompose the label into sauce structure:** base liquid, fat, protein,
   aromatics, cheese/umami, thickener, seasoning, commercial additives.
   Read the ingredient ORDER (by weight, descending) as a proportion guide:
   the first 2–3 ingredients are the bulk; the last 3 are flavor accents.
   Trap to watch for: the product description promises a sauce (e.g. "béchamel")
   but the ingredient list has no separate sauce component. When that happens,
   the sauce is not a distinct layer — it is the dairy + cheese folded into
   the crust or base. Map accordingly.
5. **Build the recreation with real-ingredient substitutes** (label it
   "Pierre original"):
   - yeast extract / autolyzed yeast / corn maltodextrin → ½ tsp fish sauce
     (undetectable umami depth)
   - modified food starch → natural reduction, or finish with pasta water
   - dried cane syrup / sugar → omit or a pinch, rarely needed
   - "natural flavors" → the actual spices implied by the product name
   - **commercial compound ingredients** (e.g. "Lemon Yeast",
     "Natural Butter Type Flavor", "Smoke Flavor") → decompose into the real
     ingredients they mimic (e.g. lemon zest + a pinch of active dry yeast;
     or butter + a drop of vanilla; or smoked paprika + liquid smoke).
     Treat them as multi-ingredient shortcuts, not magic.
6. **Diff against the profile pantry** (`$HERMES_HOME/kb/pantry.md`) and emit a
   shopping list with **missing items only**, per pierre-kitchen conventions.
   When the user asks for a straight recreation (not a dinner suggestion), keep
   this lightweight — list the 2–3 items they don't have, don't open with a
   full inventory read-through unless they ask for one.
7. **Save the finished recipe** to `$HERMES_HOME/kb/recipes/<name>.md` so it
   becomes pantry-matchable next time.
8. Any safety-critical numbers (meat temps etc.) → look up and cite per
   pierre-kitchen §5.

## Restaurant dishes (no label to read)

A restaurant has no ingredient statement to copy — but many publish a full
build spec in their own menu copy. Reconstruct from those, and frame the
result honestly as a **copycat**, never as their recipe.

1. **Restaurant's own website menu page first.** Small/independent places often
   list the complete component breakdown (base, protein, garnish, sauce,
   crunch) in the item description — that is the build sheet.
2. **Delivery-platform listings second**, for itemization, sauce names, and
   variants: Grubhub, DoorDash, order.online, tryotter, CaterCow. Platform
   pages extract cleanly even when the restaurant's own site is thin.
3. **Get the sauce names, then build each.** Sauces are usually named but not
   formulated; reconstruct them from cuisine technique (see the
   `culinary-techniques/` self-study skills for the relevant cuisine).
4. **Decompose the blurb into architecture** — base, protein, aromatics, veg,
   crunch element, sauce — and note the ONE element carrying the dish's
   personality. Build that element as a keepable batch component.
5. **Label it a copycat** in the saved recipe header: reconstructed from
   published menu specs + cuisine technique, explicitly not the restaurant's
   trade-secret formula. Never imply you extracted their actual recipe.
6. **Respect household rules** in the reconstruction (dietary swaps,
   no-microwave method, cast-iron/acid, protein hard-NOs) — a copycat still
   has to fit this kitchen.
7. Save to `$HERMES_HOME/kb/recipes/<name>.md`, then run the pantry diff /
   shopping-list step as usual. When the user approves a variant (e.g. one of
   several signature sauces), record the chosen option in the recipe file as a
   house default rather than leaving the choice open.

## Pitfalls

- **Search engines bot-block hard:** DuckDuckGo HTML throws a captcha, Google
  serves /sorry, Mojeek 403s, Walmart shows "Robot or human?", Target hangs on a
  loading dialog, Instacart search 404s. Don't burn time cycling engines — go
  straight to the Wayback Machine.
- **Bing misreads brand context:** "Giovanni Rana fettuccine" returned NASA and
  cosmetics results. Add product-y keywords ("ingredients", "sauce") and prefer
  retailer/product-page queries, or skip Bing.
- **Manufacturer sites 403 curl AND browser** with an `AccessDenied` XML body.
  Wayback is the fallback, not the last resort.
- **Archived product pages load nutrition facts in a modal** whose image URL can
  point at the WRONG product (Rana's modal showed a meatball-kit image). Verify
  the ctfassets image URL in the page source, don't trust the modal.
- **Wayback `im_/` image URLs 404 when the asset wasn't archived** — fetch the
  ORIGINAL `images.ctfassets.net` URL directly; the CDN is often still live
  even when the main site blocks.
- **Don't oversell the result:** a restaurant copycat is a reconstruction, not
  their formula. Say "copycat / how I'd build it", not "I got their recipe".
- **Dietary check:** state explicitly which ingredients meet the household's
  dietary rules (`kb/house_rules.md`) — e.g. cream, mushrooms, cheese, and pork
  sausage are broadly fine for many diets, but confirm against the house rules.
- **Retailer back-image beats Wayback for ingredient lists:** Kroger/Safeway
  product pages carry `back/` image URLs with the full ingredient statement.
  `vision_analyze` reads them cleanly — faster than CDX when the image is live.
  Try this first before reaching for the Wayback Machine.
- **Ingredient order is a proportion map, not just a list:** the first 3
  ingredients are the bulk; the last 3 are flavor accent. "Lemon Yeast"
  appearing 10th means it's a whisper of lemon + yeast, not a 1:1 ratio.
- **Sauce in the description, absent from the ingredients:** when the product
  copy promises "béchamel sauce" but the ingredient list has no separate sauce
  components, the sauce is the dairy + cheese folded into the base — don't build
  a separate sauce layer.

## Support files

- `references/label-research-wayback.md` — CDX API discovery, archived-page
  fetch, label-image extraction; worked example (Rana sausage-mushroom fettuccine).
- `references/restaurant-dish-recreation.md` — sourcing a restaurant dish with
  no label (own-site menu spec → delivery platforms), the source ladder, and a
  worked example.
