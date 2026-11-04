# Cron job: pantry-depreciation-sweep
schedule: every sunday 9am
skills: [pantry-depreciation]
deliver: origin
prompt: |
  Weekly pantry depreciation sweep. Read the pantry-depreciation skill and follow
  it exactly against your kb/pantry.md (today's date = run date):
  1. FLAG: strike `- Item` → `~~Item~~ — **assumed OUT (window elapsed; last confirmed DATE)**`
     for perishables past their window (windows in the skill). Undated perishables:
     'assumed OUT (undated perishable)'. Never strike shelf-stable or freezer lines.
  2. DELETE: struck assumed-OUT lines flagged 30+ days ago — perishable/fridge only,
     never shelf-stable or freezer. Silent routine hygiene.
  3. Do not un-strike, re-stamp, or otherwise edit.
  Deliver a short Slack summary: counts flagged/deleted by category, Chef Pierre voice.
  (Recreate in Hermes with: cronjob_manage action=create — schedule 'every sunday 9am',
  skills [pantry-depreciation], deliver origin.)
