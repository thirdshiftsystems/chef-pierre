---
name: recipe-vote-schedule
description: "Use when running the household recipe-vote program."
version: 1.0.0
author: chef_pierre
license: MIT
platforms: [linux, macos]
---

# Recipe Vote Schedule (ongoing bank-toward-50 program)

Operates the household's persistent recipe-vote setup established by the
household in 2026-09. This is the *program-level* orchestration layer; per-ballot recipe
research/dispatch lives in the `recipe-vote-poll` skill. Keep the two straight:
this skill is about the running schedule, the scoring rule, and delivery routing.

## The live cron jobs (see `cronjob list` for actual IDs/state)

| Job | Schedule | Format | Target state |
|---|---|---|---|
| Daily Recipe Vote Accelerator | daily 8am | full 5-recipe ballot | present only while bank <50; auto-pauses when target met |
| Tuesday Cooks Illustrated Vote | 9am Tue | ONE Cooks-style single | permanent |
| Wednesday Appetizer/Side Vote | 9am Wed | ONE app or side | permanent |
| Thursday NYT Vote | 9am Thu | ONE NYT-style single | permanent |
| Weekly Friday Recipe Vote | 2:30pm Fri | original 5-recipe ballot | permanent |

All five deliver ballots to the household's **dedicated vote Slack channel**, NOT
the general kitchen thread — so votes stay untangled from meal chat. When the
user asks to move vote delivery, update each job's `deliver` to the channel id.

## CRITICAL SCORING RULE — withhold the bank until BOTH voters score

**Never bank a recipe on ONE voter's score, even provisionally.** A provisional
bank gets walked back (and the file deleted) the instant the second voter's real
score drops the average below the 8.0 threshold. This burned the household in
2026-08/09 (salmon un-banked when the second voter's 7 pulled 8.0 → 7.5).

Correct flow: collect BOTH voters' real scores → average → only then save any
≥8.0 recipe to the vault. When a second voter hasn't scored yet, say so and hold
— don't assume a default for them. (Exception: a single vote stands ONLY if the
other voter is explicitly not going to score that round.)

Record each voter's score **as given** — never round, clamp or normalize it — and
average the raw values exactly (a 9 and a 9.9 average to **9.45**, not 9.5).
Voters do use decimals; the vault's score line and the feedback log must match the
computed average to two decimals so a later re-count reproduces it.

### The "mirror my scores" exception — how to apply it
A voter may authorize a proxy card (e.g. a voter away on vacation: "just
mirror the other voter's scores for mine and close the votes out, then if I don't like them
later we'll cull later"). That is a valid explicit not-scoring statement, so it
closes the ballot. Mechanics that matter:
- Mirroring runs **one direction only**: the absent voter's score is copied from
the voter who DID score. So a ballot can be closed this way **only where the
other voter has a card on file.** A ballot where the absent voter's counterpart
hasn't voted stays OPEN — there is nothing to mirror onto — and you must say so
instead of inventing a score.
- Record the authorization verbatim in the ballot ledger and the feedback log,
  so a later cull can be traced to it.
- **A proxy is ONE-SHOT and scoped to the ballots named — never a standing
  grant.** One voter clarified right after using it: the mirror was only for the
  backlog; they kept their voting rights going forward. So a mirror
  authorization discharges the backlog it was given for and EXPIRES; on every
  later ballot, collect that voter's real card and hold as normal. Never
  extrapolate "let me mirror once" into auto-filling their scores — ask, and
  re-ask each time.
- Note the scope correction in the ledger alongside the authorization, so a
  future reader doesn't read the one-time proxy as a permanent permission.
- Bank at the mirrored average, then re-count files on disk.

## After a bulk close, check the accelerator's target
When a burst of closings blows past the program's bank target, the Daily
Accelerator does NOT always self-pause. Re-count (`ls kb/recipes/*.md | wc -l`,
minus non-mains) and if the count has reached the target, `cronjob action=pause`
the accelerator (job named "Daily Recipe Vote Accelerator") and tell the
household it is paused and reversible — leave the four permanent weekly singles
running.

## Bank math & bookkeeping

- Bank count = dinner mains = `ls *.md | wc -l` **minus the non-mains**. Do NOT
  derive the non-main count by grepping for `Category: **Dinner main**` — the
  older Pierre-original card template omits that line entirely (house classics
  and copycat originals), so a `grep -L` for it over-reports non-mains and
  silently discounts real dinner mains. Classify every unmatched file by reading
  its header (`head -8`): sides/appetizers/sauces carry an explicit `Category:`
  line naming them, while a header with a Status/Rating/Source line and no
  Category at all is a main.
  - Two tag formats coexist: YAML frontmatter (`category: Side`) and markdown
    body (`- Category: **Side**`). A case-sensitive `grep 'Category:'` misses
    YAML-frontmatter cards — grep case-insensitively or `head -8` each file.
- The last logged bank/non-main tally is stale by construction — re-derive both
  numbers on disk before announcing progress. The cron header and your running
  total can drift apart; whenever there's a discrepancy, trust the on-disk file
  count, not the announced number.
- The daily accelerator self-checks the count each run and pauses itself when it
touches 50 (`cronjob action=pause`), leaving only the 4 permanent weekly votes.
- Log every vote result (banked + below-threshold) in `kb/feedback_log.md` with
dates, kept in the "Recent (last 10 days)" rollup. Banked-but-uncooked recipes do
NOT count toward the 10-day rotation until actually cooked.

## Ballot-building preferences that constantly resurface (err toward these)

- **Instant Pot slot (household rule):** every dinner ballot must include ONE
  dish built for the household's new Instant Pot (electric pressure cooker) —
  a pressure-braised/quick-braise main (chile verde, carnitas, barbacoa,
  birria-style beef, pressure ragù, sausage-and-beans). Instant Pot turns a
  long braise into a ~30–40 min weeknight dish (incl. come-up + natural
  release); novelty from the IDEA/technique, not from labor. Not curry-heavy.
  Wired into the Daily Accelerator + Weekly Friday prompts and the household
  walk-through; keep it there until the household says otherwise.
- **Format variety, not just protein variety.** The household got tired of
  skillet/glaze-repetitive ballots. Mix in protein salads, grain/power bowls,
  cold noodle plates, handhelds — not the same template with different meat.
- **Avoid curry-heavy dishes** entirely (lingering kitchen odor — household
  preference). Downvote/bench high-odor curries; don't keep retrying the theme.
- **Shrimp before salmon.** If the household dislikes a protein (e.g. salmon),
  suggest it rarely; prefer the proteins and seafood they do enjoy.
- **Traeger chicken skin won't crisp** — skip or flag crispy-skin-on-the-smoker
  recipes (the bake-then-air-fry finish in the Ninja Foodi XL is the workaround).
- Keep honoring the dietary screens in `kb/house_rules.md` (e.g. citrus-only
  fruit and NO fruit preserves/glazes — apricot/peach/mango preserve glazes are a
  hard NO under the house fruit rule; onions/garlic/honey are OK there),
  no brothy soups, no microwave (toaster oven/stovetop), low-fuss one-pan,
  Traeger + Ninja Foodi XL available, chicken-thigh-fatigue, personality dishes.
- **Vet ballots for hidden fruit**: the house dietary screen must catch fruit
  *preserves/glazes* (apricot-chipotle, peach-jalapeño, mango-habanero), not
  just fresh-fruit wording. A fruit-preserve glaze slipping onto a ballot can
  score a hard 1 — screen every pick.

## Bulk-banking many winners at once
When several ballots close together (a vacation backlog), 10–15 cards need
writing at once. Fan out `delegate_task` children (3–4 cards each, one child per
source cluster) with the exact card template and the household constraints
inline — children have no chat context. Then **verify every claimed file
yourself**: `ls kb/recipes/*.md | wc -l` for the count, and a per-file check that
each has the H1, `- Category: **Dinner main**`, `## Ingredients`, `## Steps`,
`## Notes`, a source URL, and the right `voted N/10` line. Child summaries are
self-reports, not proof. Spot-check one card against its live source (browser if
web_extract is blocked for the domain) to confirm the quantities are real — a
"6 shrimp for 2 servings" looked like a typo and was the source's actual text.
Fix cosmetic format drift (e.g. an em dash outside the italic score line) with a
quick patch rather than a rewrite.
- **Never put angle-bracket placeholders in a `delegate_task` goal or context.**
  A goal containing a template marker like `<one-line hook>` is rejected outright
  ("goal contains an unexpanded template marker") — children cannot resolve
  placeholders, so the guard refuses the whole batch. Describe the card layout in
  prose instead: name each line position and what it holds ("line 1 is an H1 with
  the dish title; line 5 is an italic score line …"), and put each child's actual
  score value in its own file bullet. Re-issuing the identical text without the
  brackets then dispatches first try.
- **Score values go in the goal, not in the template.** Since children can't
  infer per-recipe numbers from a shared template, list the score next to each
  filename in its task (e.g. "greek_chicken_souvlaki_bowls.md — Score 9.0").

## Cater pantry swaps proactively
Propose the known swap/fit up front (e.g. bulgogi Korean-pear → citrus+honey;
snap peas → French green beans; paneer where to buy) instead of flagging after votes.

## Wednesday Single-Recipe Verification Checklist

Before presenting a Wednesday app/side single for voting, vet it through these
steps so the voter sees a recipe that is already pre-screened:

1. **Source verification** — `web_extract` the recipe URL (or Wayback snapshot for
   paywalled NYT/ATK) to confirm ingredients and method match the cron delivery's
   claims. Do not trust the cron preamble's "vetted" tag blindly.
2. **Hard-NO screen** — no fruit preserves or non-citrus glazes, no curry-heavy,
   no brothy soups, no microwave step, no bone-in chicken except thighs, no
   salmon-as-main.
3. **Dietary/flag+swap screen** — screen against the household's dietary
   restrictions in `kb/house_rules.md` (e.g. fruit rules, HFCS, flagged
   vegetables: hard NOs per the house rules). For any "sometimes-bothersome"
   item flagged in the house rules, propose a documented swap rather than
   dropping the dish. Do not assume two similar items share a restriction —
   check the recorded list, not family resemblance.
4. **10-day ring** — search `kb/feedback_log.md` for the dish name; if it was
   cooked or eaten in the last 10 days, do NOT suggest it.
5. **Disk duplicate check** — grep `kb/recipes/` by keyword and read headers, not
   just the `apps_sides_bank.md` index (which can drift). A dish with "Brussels
   sprouts" in the title may actually be a chicken recipe with Brussels as a
   component.
6. **Bank alternation** — read `apps_sides_bank.md` to confirm the app/side split
   and that the alternation rule selects the right slot this week.
7. **Create ballot ledger** — write `tmp/ballot_<YYYY-MM-DD>.md` with roster,
   incoming vote, provisional average marked NOT banked, and
   `STATUS: awaiting <other voter>` before responding to the voter.

## Banking NYT/ATK cards when the source is paywalled
A ballot pick's real quantities must come from the source, never from guessing at the title. For subscriber-only NYT Cooking pages, recover the page text from a Wayback snapshot instead of logging in (never log in to a paywalled site):
- Fetch `https://web.archive.org/web/<year-or-ts>/<full-recipe-url>` through `web_extract`. A capture that lands on the NYT bot-wall renders as a short "Not Authorized" body — **try an earlier timestamp** (2024–2025 captures of NYT recipe pages usually have the full ingredient list and steps; 2026 captures are more often blocked).
- Verify the slug before fetching: NYT URLs are `<id>-<slug>` and the slug is not always the dish name. Recipe 8218 is `8218-slow-roasted-pork-for-tacos` (not `-slow-roasted-pork-tacos`), and a wrong slug returns "has not archived that URL" rather than an error. If a slug fails, `web_search` the id to read the canonical URL off the SERP.
- The `archive.org/wayback/available` API and filtered CDX queries both 429/403 quickly — don't hammer them; go straight to the `/web/<timestamp>/` redirect form and space the attempts out.
- NYT cards carry a **provenance note** in `## Notes`: built from a Wayback snapshot (with capture date) because NYT Cooking is subscriber-only. Say the quantities were transcribed from the snapshot, not reconstructed.

## Pitfalls

- **The live KB is `$HERMES_HOME/kb/` — NOT an install template's `kb/`.**
  The distributable *template* package (install.sh, MANIFEST,
  SOUL.md, config.yaml, plus a seed kb holding starter recipes and
  `_(awaiting intake)_` copies of household.md/pantry.md) is not the live store.
  Writing a bank card or a
  bank/log entry there changes nothing live and leaves the template dirty. If a
  card "saves" but the bank count doesn't move, `ls`/`readlink -f` the kb before
  reporting success: the live kb holds the real recipe bank plus its own
  `.kb_index/`,
  `tmp/`, `images/` and `snoozed.md`; the template has none of those.
- **Match votes to the RIGHT ballot before recording — keep a per-ballot ledger.**
  Several ballots can sit open at once (a daily-accelerator run plus a lost/rerun
  one plus the weekly singles), and a voter's bare `1: X, 2: X...` carries no
  recipe names — misattributing it to the wrong roster confuses the household and
  corrupts the log.
  - Attribute by the THREAD the scores arrived in: the ballot whose roster is the
    thread parent is the ballot being scored. Then say the attribution out loud in
    your reply ("I've put these on the <date> ballot — tell me if you meant a
    different roster") so the voter can correct it in one word. Don't silently assume.
  - Write `tmp/ballot_<YYYY-MM-DD>.md` for every ballot you post: roster (name,
    protein, format, source), one `## Votes` line per voter with their raw scores
    and the date, a provisional-averages line marked NOT banked, and a final
    `STATUS: awaiting <voter>` line. Re-read that file before recording anything —
    it is the only reliable record of which rosters are still open.
  - A ballot posted by a cron job does not always leave a ledger behind. If a
    vote arrives for a ballot with no `tmp/ballot_<date>.md`, write the ledger
    retroactively BEFORE recording anything: roster, the incoming vote, the
    provisional average explicitly marked NOT banked, and
    `STATUS: awaiting <other voter>`. The ledger is the only thing that stops the
    second score set from being misattributed to some other open roster later.
  - End that file with an "other ballots still in flight" list (date, roster,
    who has scored, who is still owed). That one block is what stops a score set
    from landing twice on a closed ballot and stops you telling a voter you're
    waiting on them when their card is already in.
  - Before recording, check the target ballot isn't already fully voted/banked —
    never re-record an extra score set for a closed ballot.
- **Tersely formatted scores with high-decimal precision are still one voter's card.** A voter may reply in shorthand (`1-9 2-7` with hyphens instead of `1: 9, 2: 7,`) and may give unusually precise decimals (7.894, 7.7734443) that look computed. Do NOT treat precision as proof of a finished average — hold as one voter's card until the second voter submits theirs. Ask explicitly before banking.
- **Confirm voter identity when the session label may be wrong.** Household
  members sometimes message from each other's Slack accounts, so the 'User:'
  label may not reflect who typed. When scores arrive without explicit ID and
  open ballots already hold one voter's card, ask which voter is scoring before
  attributing.
- **Create ledger stubs for every cron-posted ballot, even singles.** Weekly singles fire on different days and can accumulate 7+ open ballots before votes land. After each cron post, create `tmp/ballot_<date>.md` with the roster and `STATUS: awaiting both voters` — don't wait for a vote to trigger retroactive creation.
- **Don't stop at "waiting on the other voter" — collect the cards you're owed.**
  When a voter writes in with their scores, they are live in front of you: list the
  other open ballots still awaiting THEM with their recipe names so they can fire
  off several cards at once. Votes that arrive one ballot at a time leave rosters
  open for days, and an open roster is a ballot whose winners stay unbaked.
- When asked to rerun a lost ballot, serve a fresh five: research them again with
  the hard-nos from `kb/house_rules.md` applied (dietary hard NOs, no
  salmon-as-main, no bone-in chicken except thighs, no curry-heavy) and post a new roster; the pantry is irrelevant for fresh
  ballot picks.
- **When a ballot cron run errors with "restart-safe systemd scope … systemd-run
  --user --scope is unavailable", it is an INFRA failure, not a recipe/prompt
  one — no ballot was built.** This is the gateway service running as a
  system-level unit that never set `XDG_RUNTIME_DIR` / `DBUS_SESSION_BUS_ADDRESS`,
  so the restart-safe worker probe can't reach the user D-Bus bus. Never invent a
  ballot to paper over a failed delivery. Immediate workaround for today's ballot:
  build it directly from the chat (not gated by the systemd env).
  Durable fix: add a systemd drop-in setting both env vars on the gateway
  service, `systemctl daemon-reload`, then restart the service — the env is
  read at process launch, so the running gateway keeps failing until restarted.
  Confirm with a live probe after exporting the vars:
  `systemd-run --user --scope /bin/true`.
- Do NOT write to the user-owned `recipe-vote-poll` skill — it's protected.
  If it needs edits, recommend `hermes curator adopt recipe-vote-poll`.
- Deliver to the dedicated vote channel, not the kitchen thread (household
  preference). A channel mention like `slack:<channel_id>` is the delivery form.
- When a ballot says one thing and the file count says another, the file count
  wins — re-count before announcing progress.
- **The `apps_sides_bank.md` parallel index can drift from the recipe files on
  disk.** Sides or appetizers banked as Pierre originals (written during a
  dinner cook, not via the Wednesday vote flow) are sometimes missing from the
  index. Always cross-check by grepping the recipe vault directly rather than
  trusting the index file's counts alone.
- **`kb/feedback_log.md`'s "HARD-NO preferences" header goes stale; trust current
  rules, then fix it.** That header was written from one early feedback round and
  keeps superseded bans alive ("no bone-in chicken at all", "shakshuka permanently
  banned") after the household revised them (bone-in thighs are fine; shakshuka is
  snoozed, not banned). Reconcile the header against current rules whenever you
  open the log for a vote write — a future ballot built from that header alone
  would drop legal recipes and re-pitch tired ones.
