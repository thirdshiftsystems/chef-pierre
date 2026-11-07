---
name: recipe-blitz
version: 1.2.0
description: "New-household tutorial: when the recipe vault (kb/recipes/) has fewer than 50 cards, offer a Recipe Blitz of frequent family recipe votes to fill it fast, then stop at the family's chosen target."
author: Chef Pierre
license: MIT
---

# Recipe Blitz (Chef Pierre v1.2)

A new household's recipe vault starts nearly empty, so Chef Pierre can't plan
meals well yet. Recipe Blitz fills it fast: the family runs frequent recipe
votes, every recipe that scores 8.0/10 or higher becomes a recipe card, and when
the vault reaches the number the family chose, the blitz stops and Pierre moves
to his normal routine.

Families who fill their vault this way in the first few weeks get useful meal
plans much sooner. v1.2 makes it the built-in onboarding for new households.

All state is **per household**. A household is one Slack channel and has its own
`kb/` folder. Never mix the counts, settings or schedules of two households.

## Where things live

- Recipe vault: `kb/recipes/` in the household's profile folder. **The card count
  is the number of `.md` files in that folder.**
- Blitz state: `kb/recipe_blitz.json` (section 5).
- Household rules and constraints: the household's memory, `kb/house_rules.md`
  and the `pierre-kitchen` skill. Every blitz recipe must respect them.
- Voting mechanics: the `recipe-vote-poll` skill. Use it exactly as the weekly
  vote jobs do. Do not invent a different voting method.

---

## 1. When to offer it

At the start of a conversation in a household channel, and whenever you are
about to plan meals, count the cards in `kb/recipes/` and read
`kb/recipe_blitz.json` (treat a missing file as `status: never_offered`).

Offer Recipe Blitz when ALL of these are true:
- the vault has **fewer than 50** cards
- `status` is `never_offered`, or it is `declined` and `last_offered` is more
  than 30 days ago
- no blitz is `active` or `paused`

Do not interrupt an unrelated task. Answer the question first, then make the
offer in a short paragraph at the end of the reply.

A household with 50 or more cards never sees the offer unless someone asks for
a "recipe blitz" by name.

### The offer (Pierre's voice, short)

> Bonjour! Your recipe vault only has {count} cards so far. I do my best work
> once I know at least 50 dishes your family loves. Shall we do a **Recipe
> Blitz**? A couple of times a week I'll send the family a few recipes to score,
> and every one that scores 8 or higher goes into the vault. Most families are
> fully stocked in a few weeks. Shall we begin?

- **Yes:** go to section 2.
- **No / not now:** write `status: declined` and today's date as `last_offered`.
  Tell them they can start any time by saying "start a recipe blitz". Do not
  bring it up again for 30 days.

---

## 2. Setup questions

Ask these **one at a time** and wait for each answer. Always state the
suggested default so the family can just say "yes".

**Q1. Target size**
> How many recipe cards would you like in the vault before we stop the blitz?
> I suggest **50**. That's enough variety that I rarely repeat myself.

- Accept a whole number from 10 to 300. "Yes", "sure" or "sounds good" means 50.
- If the number is at or below the current count, say the vault already has that
  many and ask whether they want a higher target or to skip the blitz.

**Q2. Vote frequency**
> How often should the family vote? I suggest **twice a week** to start. We'll
> keep going until the vault reaches {target} cards.

- Accept once, twice or three times a week, or every N days (minimum every 2
  days). "Yes" means twice a week.

**Q3. Days and time** (only if they haven't said)
> Which days and time suit you? For twice a week I suggest **Tuesday and
> Saturday at 10 am**.

**Q4. Who votes** (skip if the channel members are obviously the family)
> Should everyone in this channel vote, or only certain people?

Then confirm in one message and wait for a yes:

> Parfait! Here is the plan:
> - Goal: {target} recipe cards (you have {count}, so {target - count} to go)
> - Votes: {frequency}, {days} at {time}, 3 recipes per vote
> - Voters: {voters}
> - Any recipe averaging 8/10 or higher goes into the vault
> - I'll stop automatically when we reach {target}
> Shall I start?

On yes: write the state file, create the schedule (section 4), and say when the
first vote arrives. If that is more than 2 days away, offer to run one now.

---

## 3. Running a blitz round

1. **Count first.** If the vault already has `target` or more cards, do not
   vote. Go to section 6.
2. **Pick 3 recipes** the household has never made:
   - not already in `kb/recipes/`
   - not in `kb/feedback_log.md`
   - not in `rejected` in the state file
   - within every household rule and constraint
   - varied: different proteins (or vegetarian), different cuisines, and at
     least one quick weeknight dish
   - from free, reliable sources only. Never log into paywalled sites.
3. **Post the ballot** in the household's channel using `recipe-vote-poll`,
   numbered 1 to 3. For each recipe give: name and source tag, a two-line
   description, key ingredients (no quantities), total time and appliance, why
   it fits the household, one or two source URLs, and any swap flags. Keep the
   whole post under about 700 words.
4. **Voting instructions:** each voter scores every recipe from 1 to 10 in one
   reply, for example `1: 8, 2: 6, 3: 9`. Say when voting closes (default 24
   hours).
5. **When voting closes,** average each recipe's scores across the people who
   voted.
   - **8.0 or higher:** save it to `kb/recipes/<slug>.md` in the existing card
     format (title; "Pierre-saved classic (voted X/10 by {voters}, DATE)";
     serves and time; source URL; ingredients; steps; Notes with the
     household's safety, appliance and swap notes). Confirm each save with
     read_file.
   - **Below 8.0:** add the recipe name to `rejected`.
   - **Nobody voted:** don't count the round. Post one friendly reminder and
     re-run the same ballot at the next scheduled time.
6. **Post the result:**
   > This round's winners: {list or "none this time"}. The vault now has
   > {count} of {target} cards. Next vote: {next_run}.
7. Update `rounds_completed` and `last_round` in the state file. If the count
   has reached the target, go to section 6.

---

## 4. Scheduling

Create one scheduled job per household with the cron tool:

- name: `recipe-blitz-{household_id}`
- schedule: the chosen days and time
- deliver: `slack:{household channel id}`
- skills: `recipe-blitz`, `recipe-vote-poll`, `pierre-kitchen`
- model: use the same model as the household's other scheduled jobs. A stable
  paid model is recommended: free models can be rate limited at busy times,
  and a missed vote stalls the blitz.
- prompt: `Run a Recipe Blitz round for household {household_id} using the recipe-blitz skill.`

Save the job id in `schedule_job_id`.

If the family changes the frequency, days, time or target mid-blitz, update both
the state file and the job, then confirm the new plan in one line.

The family can say:
- "pause the blitz": set `status: paused` and pause the job
- "resume the blitz": set `status: active` and resume the job
- "stop the blitz": set `status: stopped` and delete the job

---

## 5. State file (`kb/recipe_blitz.json`)

```json
{
  "household_id": "C0123EXAMPLE",
  "status": "never_offered | declined | active | paused | stopped | completed",
  "last_offered": "2026-11-06",
  "target": 50,
  "frequency": "twice_weekly",
  "days": ["tue", "sat"],
  "time": "10:00",
  "timezone": "America/Los_Angeles",
  "voters": ["@alex", "@sam"],
  "recipes_per_round": 3,
  "vote_window_hours": 24,
  "pass_score": 8.0,
  "schedule_job_id": null,
  "started": "2026-11-06",
  "starting_count": 12,
  "rounds_completed": 0,
  "last_round": null,
  "rejected": []
}
```

Use the Slack workspace's timezone, or ask once if it's unknown.

---

## 6. Finishing

When the vault reaches the target:

1. Delete the scheduled job and set `status: completed`.
2. Celebrate briefly:
   > Magnifique! The vault now has {count} recipe cards, so the blitz is done.
   > From now on I'll plan your meals from your family's favourites. You can
   > still add recipes any time, and if you want another blitz later, just say
   > "start a recipe blitz".
3. Return to normal meal planning and the household's regular vote jobs.

Never restart a completed blitz unless the family asks.

---

## Rules

- Ask setup questions one at a time, always with the default.
- Never post a ballot in another household's channel.
- During a blitz, only recipes that scored 8.0 or higher go into the vault.
- If `kb/recipes/` can't be read, say so and don't start or run a round.
- Don't nag: one offer, then wait 30 days after a "no".
