---
name: receipt-to-pantry
description: "Use vision/OCR to scan receipts and update pantry items."
---

## When to Use
Use this whenever the user shares a photo of a receipt or grocery list to "add to pantry".

**Target file: `$HERMES_HOME/kb/pantry.md`** (e.g. `~/.hermes/profiles/<profile>/kb/pantry.md`).
Note: any `kb/pantry.md` copies inside an install template / share directory are
the empty *install template* — never edit those; the live pantry is under the
profile home. Confirm with a quick `find ~ -iname "pantry*.md"` if unsure, and
pick the one with real content.

If the user says "add these", just do it — do NOT stop to ask "shall I add them?"
that is only for ambiguous extractions.

Read `pierre-kitchen` §3 for the pantry conventions (receipt parsing, `*soon*`
flags, snack-duplicate rule) before editing.

## Step 2: Verification & Aggregation
Aggregate the lists from all images into one summary.
- Present the categorized list to the user.
- **Ask**: "I've extracted these items. Shall I add them all to the pantry?"

## Step 3: Pantry Update (edit the file, not memory)
- Patch `kb/pantry.md` in place: append new items to the right section
  (Proteins / Fridge / Freezer / Pantry-Dry Goods / Snacks), tagging
  `— added YYYY-MM-DD`. Tag fresh produce, herbs, dairy and leafy greens `*soon*`.
- **Restock vs. duplicate:** if the line is already there and no cook consuming it
  was logged, bump it in place (`— +1 pack added DATE (2 packs)`) rather than
  adding a second line. If the panty line already says **USED UP**, treat the new
  purchase as a fresh restock and rewrite the line.
- **Snacks/crackers/chips**: if the SKU already appears, leave it alone (no bump,
  no question) — exact snack counts don't matter (household rule).
- Update the `_Last updated: YYYY-MM-DD_` line.
- Do NOT write receipt items into durable long-term memory; the pantry file is
  the record.
- Re-read the sections you touched to verify the lines landed, then report a
  short summary: N items added, M perishable (*soon*), anything skipped.
- Flag storage guesses honestly (e.g. "assumed frozen — confirm") instead of
  silently deciding; never invent quantities the screenshot didn't show.

