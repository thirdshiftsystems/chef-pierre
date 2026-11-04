---
name: kroger-cart
description: "Push a generated shopping list into a household Kroger cart via the public Cart API — search, OAuth, add-to-cart."
version: 1.1.0
license: MIT
platforms: [linux]
---

# Kroger Cart (shopping list → cart)

Use when the user asks to put a shopping list (or part of one) into the
Kroger cart so it's waiting for them in the app. Also the reference for any
Kroger API / OAuth question.

**Scope:** cart additions are not limited to food/kitchen items — if the user
asks for something Kroger stocks (cleaning supplies, paper goods, etc.), search
and add it the same way. The only gate is the user's explicit approval of each
item before adding.

## Preconditions (set up once)

Tool: `kroger.py` (stdlib only, run with `python3`). State files live next
to it:

- `creds.json` (chmod 600) — `client_id`, `client_secret`, `redirect_uri`,
  `scope`, `location_id`, `zip_code`. Created during setup (see README).
- `tokens.json` (chmod 600) — user OAuth tokens for the household's Kroger
  account.

Sanity check anytime: `python3 kroger.py config`

## Flow

0. **RECIPE-FIRST — always.** A cart is never built from pantry gaps alone.
   Sequence:
   1. **Suggest 5 diverse recipes from the vault** — pull from the
      household's recipe collection, and make them *diverse*: vary the
      protein AND the format (beef / pork / chicken / seafood / vegetarian;
      skillet / sheet-pan / grill / pressure cooker / salad / bowl). Respect
      any rotation ring, hard NOs, and snooze list the household keeps.
      Show each one's name, protein, format, and time.
   2. **Let the household choose** — wait for their picks before touching
      the pantry or the cart. Do not pre-select for them.
   3. **Survey the pantry against the chosen recipes only** — diff the real
      ingredient lists against on-hand stock plus any leftovers log.
   4. **Then build the missing-items list** and add it to the cart.
   Standing add-ons that ride along regardless: any regular staples the
   household keeps (work snacks, drinks), staples that are actually out,
   and whatever treats they've asked for.

1. Produce the shopping list (missing items only, grouped, with quantities).
   Confirm the list with the user BEFORE touching the cart — adding to the
   cart is a state change on their account.

## GRILL-ME SHOPPING SESSION (default opening)

When the household sits down to shop, do NOT wait for a list — drive the
session as a rapid-fire interview. People forget what they want in the
moment; the job is to make them *react*, not remember.

1. **Cravings round** — pointed questions: which protein is calling
   (beef/pork/seafood/surprise)? Any travel-food itch? Anything they wished
   they'd bought last week?
2. **Recipe prompts** — offer 4-5 diverse recipes (protein AND format
   varied; respect rotation, NOs, snoozes) as *prompts, not a menu* —
   "does this spark something else?"
3. **Gap probe** — come armed with: depreciated pantry staples that need
   restock (see the pantry-depreciation skill), anything the recent
   depreciation sweep flagged worth confirming, and standing staples.
4. **Category grill — FULL STORE:** hit every department Kroger sells, not
   just food: produce, meat/seafood, bakery, dairy, frozen, pantry/snacks,
   drinks, treats, AND household — paper goods (towels, TP, tissues),
   cleaning supplies, laundry/dish, health & beauty, pharmacy/OTC
   (reminders to check prescriptions, vitamins), pet, baby, floral. Nothing
   is out of scope: if Kroger stocks it, the grill covers it. Quick yes/no
   per department, linger where the answer is yes.
5. **Compile → confirm → cart** — present the full list, get the yes, then
   add per the steps below.

This replaces waiting for a dictated list. If the user just dictates items,
fill the gaps with a quick grill (2-3 questions max) before confirming.

## Adding items

2. Per item, resolve the Kroger product:
   `python3 kroger.py search "<item>" --json`
   - Parse the JSON, take the best `productId` by description match (exact
     description or closest name; prefer the entry whose size matches the
     list, e.g. 1 gal vs 1/2 gal). Never invent a productId — only use one
     returned by the API.
   - If nothing sensible comes back, skip the item and tell the user it
     couldn't be found (they can add it in the app).
3. Add it:
   `python3 kroger.py add --product-id <id> --qty <n>`
   (or `add "<term>" --qty <n>` for the top match, but prefer the explicit
   productId path so the choice is visible).
4. Report a running list of what was added. Offer `show` to dump the cart
   (best effort — the public tier is add-only, so the app is the source of
   truth).

## Rules (hard)

- **The cart is add-only and checkout is impossible via API.** Public Cart
  API = `PUT /v1/cart/add` only, 5,000 calls/day. The household reviews and
  pays in the Kroger app — never touch payment. No spend risk, but still:
  never add items the user did not approve in the list.
- **Confirm before adding** — one message listing the items + quantities,
  get a yes, then add. If the user asked for a big list, batch the adds and
  show progress.
- **The token is bound to the Kroger account that authorized it.** If
  another household member wants their own cart, re-run the authorize flow
  as them.
- If `add` fails with `invalid credentials` → creds.json is wrong. If the
  refresh fails → re-run authorize. If a product search 404s, try a shorter
  or different term before giving up.
- **Missing `scope` in creds.json causes HTTP 403 on every product search.**
  If `kroger.py config` KeyErrors on `scope`, add `"scope": "product.compact"`
  to `creds.json` before searching products.
- Product search must use the client-credentials scope `product.compact`
  (not `product.compact:read`), and add-to-cart must send `upc`, not
  `productId` (the Cart API returns CART-2012 "UPC is required" otherwise).
  kroger.py already does both — don't revert them.

## Auth commands (only if asked)

- `kroger.py authorize` — OAuth consent (the user must click the URL and
  log in).
- **TUNNEL REQUIREMENT (remote box):** the registered redirect URI is
  `http://localhost:8787/callback`, so the browser that finishes the
  consent MUST reach the box's :8787. If the user's browser is on a
  different machine than the agent host, they need an SSH tunnel:
  `ssh <user>@<agent-host> -L 8787:127.0.0.1:8787`
  If they're at the agent host's console instead, no tunnel is needed.
- `kroger.py stores --zip <zip>` — find stores, save `location_id` to
  creds.json.
- `kroger.py token` — print/refresh the user access token.

## Verification

- Each `add` returns HTTP 200 with a body (or `--json` for the raw response).
- Tell the user the cart now holds X items — they can verify in the app.

## Bulk-loading a whole list (proven pattern)
For a large cart (40+ items) drive `kroger.py` from a small Python script rather
than one shell command per item — see `scripts/bulk_load_cart.py` in this
skill, edit its `ITEMS` list, and run it. Two phases, always:
1. **Dry run first** and eyeball every pick. Keyword search WILL return wrong
   products: a bare `popcorn` matched SkinnyPop bags, `baby gold potatoes`
   matched a Happy Baby *baby-food pouch*, `bacon` matched **beef** bacon, and
   `bubly sparkling water` matched a Sangria flavor. Re-search with a tighter
   term and re-run the dry run until every line reads right. Never commit a
   pick you haven't read.
2. **Then commit** with the same selection, and re-count the successes.

If a search term finds nothing at the user's store, tell them to grab it in
the app rather than silently dropping it.
