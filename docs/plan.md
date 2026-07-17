# Plan: Score every candidate and measure in all 39 WA counties

**Goal.** Bring scored, cited candidate dossiers and real measure analysis to
all 39 Washington counties for the August 4, 2026 primary — the same depth
King County already has — so every Washington voter gets alignment scores, not
just a correct ballot. Do it **in importance-ordered batches of ~50 dossiers**
so the site can be re-released after any batch with more of the ballot scored.

**Status today.** Ballot *coverage* is done: all 39 counties resolve the right
contests/measures for any address (28 full, 11 partial). But **only King County
(142 candidates) and the statewide Supreme Court races (14 candidates) are
scored.** The other 38 counties carry candidates as `official-ballot-only`:
name, party, pamphlet link, empty `scores: {}`. The 82 local measures carry
only a generic "this is a tax" lean stub. This plan closes that gap.

**Deadline.** Today is 2026-07-17; the primary is 2026-08-04 (~18 days). The
model below is **incremental release**: process one ~50-dossier batch at a time,
re-assemble, and the owner releases whenever "enough" is scored, then keeps
releasing as more batches land. Unscored candidates degrade gracefully today
(they show "not enough evidence to score"), so every batch leaves the site in a
releasable state.

---

## Locked decisions (from the owner)

1. **Rollout: incremental, importance-ordered batches of ~50 dossiers.** Process
   batch by batch; re-assemble after each; the owner may release the site once
   "enough" batches are done and continue releasing as research comes in. (This
   supersedes the earlier all-or-nothing idea.)
2. **Depth: King's deep/light/omit doctrine.** 3+ candidate races get a full
   multi-source dossier; 2-candidate races get a light dossier (pamphlet +
   campaign site, fewer axes); uncontested single-candidate races stay listed
   with a one-line "advances regardless" note and **no** dossier/score. Score
   only axes the evidence supports; **omit** an axis rather than guess.
3. **Measures: score all 82 for real** — `what_it_does`, `cost_line`,
   `pro_summary`, `con_summary`, proper `lean_mappings` like King's 7. Run as a
   parallel side-track (they're low-variance); fold big-county measures in early.
4. **Execution: multi-agent workflow fleet with reliable live web.** Fan out
   research → score → refute agents in parallel, bounded by web rate limits and
   token budget.

These are settled — execute against them.

---

## The batch model (the spine of this plan)

`pipeline/build_dossier_batches.py` is the single source of truth for what to
research next. It emits `data/final/dossier-batches.json`: **590 candidate
dossiers in 12 importance-ordered batches of ~50.** Regenerate it after each
batch lands (finished candidates drop out) or when weights change.

**How the 1,333 naive candidates become 590 dossiers:**
- **Uncontested single-candidate races (189) get no dossier** — everyone
  advances; they're just listed.
- **Congressional + legislative races are deduped across counties.** CD-5 spans
  12 counties, LD-9/Pos.2 spans 7 — each is researched ONCE and its scores fan
  out to every county instance. This collapses 854 federal/state instances to
  276 unique, and those 276 share one Tier-1 source (the SOS state pamphlet).

**Importance ordering** = `reach / candidates × contested-boost`, i.e. how many
voters a race serves per dossier of work, favoring races that are cheap to
finish and widely seen. Result: big-county countywide races and high-reach
deduped congressional races surface first; small-county sub-district races last.
Populations in the script are coarse ordering weights, not published figures —
tune them if the owner wants a different priority (e.g. weight small rural
counties up because they have the least other coverage).

**A "research unit"** = one contest, except congressional/legislative which are
one deduped unit across all their counties. A batch is whole units summing to
~50 dossiers, so a race is never split across batches.

**Batch shape (from the current run — regenerate for exact contents):**

| Batch | Dossiers | Races | Shared fed/state units | Character |
|---|---|---|---|---|
| 1 | 54 | 16 | 4 | Big-county county offices (Pierce/Spokane/Clark) + top congressional |
| 2 | 54 | 18 | 2 | Clark/Thurston/Kitsap/Yakima county offices + CD-1/CD-3 |
| 3 | 50 | 13 | 8 | CD-4/CD-5 + first legislative + Benton/Whatcom/Yakima |
| 4 | 52 | 24 | 24 | Legislative sweep (mostly 2-way, many multi-county) |
| 5 | 53 | 17 | 12 | Legislative (3-way) + Skagit/Cowlitz + first city race |
| 6–8 | ~52 each | ~15 | 6–9 | Remaining legislative + mid-size county offices |
| 9–12 | ~50 each | ~16 | 0 | Small-county offices, PUD/port, fire-district commissioners |

Batch 1 concretely: Pierce council districts 1/5/7 + district court; Spokane
clerk/auditor/prosecutor; Clark assessor/clerk/auditor + council 2/5 + PUD;
Congressional Districts 2, 6, 8, 10. Full per-candidate contents live in
`dossier-batches.json`.

**Measures (82)** ride alongside as a side-track; do a county's measures when
you do that county's local races (their pro/con sources are in the same
pamphlet). Prioritize big-county / countywide measures early.

---

## Reference implementation (copy King exactly)

King is the worked example — read these before writing anything; they are the
authoritative spec and every dossier/score must match them:

- `data/washington-state/counties/king/dossiers/RESEARCH-GUIDE.md` — dossier
  format, source-tier policy, evidence_level rules, same-name traps.
- `data/washington-state/counties/king/scoring/SCORING-GUIDE.md` — scoring JSON
  format, sign convention, omission-over-guessing, applicability, the
  independent refutation pass, and the measure-scoring format.
- `data/final/rubric.json` — the 14 axes, poles, and `applies_to` (which
  categories each axis scores). READ IT FIRST when scoring.
- A King contest as a template, e.g.
  `dossiers/congressional-district-1-united-states-representative/` and its
  `scoring/…json` + `scoring/refutations/…json`.

Doctrine that must not drift (from those guides + ADR 0002):
- **Every factual claim cites a listed source. No source, no claim.**
- **Scoring is dossier-only** — no web, no new facts at the scoring stage.
- **Omit, never guess.** No evidence for an axis → omit it. Never infer from
  party preference.
- **Independent refutation** by a different agent; `merge_scores.py` applies it.
- **Neutral tone.** Describe positions; never grade them.
- **Judicial candidates** score only `judicial`, `safety`, `experience`.
- **Honest `evidence_level`** — when in doubt, downgrade.

---

## Data model & integration point

Ballot structure exists at
`data/washington-state/counties/<county>/interim/app-contests.json` /
`app-measures.json` (built by `build_votewa_lite_data.py` for 32 counties,
`build_<county>_lite_data.py` for the original 6). Candidate objects carry
`scores: {}` today.

Scored artifacts stay **separate** from ballot structure (ADR 0002), mirroring
King:
```
data/washington-state/counties/<county>/
  interim/contests.json, measures.json      # normalized (Phase 0)
  interim/pamphlet-text/…, pamphlet-index.json, research-plan.json
  dossiers/<contest-slug>/_contest.md, <candidate-slug>.md
  scoring/<contest-slug>.json
  scoring/refutations/<contest-slug>.json
  scoring/measures.json + refutations/measures.json
data/washington-state/statewide/
  dossiers/<district-office-slug>/…         # shared federal+state (the 276)
  scoring/<district-office-slug>.json + refutations/…
```

`assemble_app_data.py` already merges King's `data/final/scores.json` onto
contests by slug. After Phase 0 it merges every county's + the statewide shared
scores onto every contest instance, fanning shared federal/state scores onto
each county copy by `(category, district, office, candidate-slug)`. **Do not**
restructure the scope model or create shared contest slugs — keep per-county
contest entries and fan scores on at assembly time.

---

## Phase 0 — Generalize the pipeline (prerequisite, do once, before any batch)

The scoring scripts are hardcoded to King + statewide. This phase is pure
plumbing — no scores produced — and everything downstream depends on it.

- [ ] **Per-county `interim/contests.json` + `measures.json`** in the shape
  `parse_candidates.py` produces for King (research-plan/validate read these).
  Carry `category`, `office`, `district`, `candidate {slug, name,
  party_preference}`. Cover all 38 counties + the deduped statewide set.
- [ ] **`build_research_plan.py`:** parameterize by county; emit
  `statewide/interim/research-plan.json` for the deduped federal/state races;
  keep the depth rule (3+ deep, 2 light, 1 uncontested→no dossier).
- [ ] **`extract_axis_notes.py`, `validate_scoring.py`, `merge_scores.py`:**
  replace the hardcoded `[STATE, KING]` dir lists with iteration over all county
  packages + statewide.
- [ ] **`assemble_app_data.py`:** merge each county's scoring onto its
  candidates by slug; fan statewide shared federal/state scores onto every
  county instance by `(category, district, office, candidate-slug)`. Keep the
  King path byte-identical.
- [ ] **Regression gate:** with no new scores, `assemble` + `validate_scoring` +
  `npm test` still pass and King output is byte-identical.
- [ ] `build_dossier_batches.py` already exists and produces the batch manifest;
  confirm it still runs after the normalization changes.

---

## Per-batch loop (repeat for batch 1 … N)

Each batch is a self-contained, releasable increment. For batch _k_:

1. **Read** the batch's units from `dossier-batches.json`.
2. **Source acquisition** for any race whose pamphlet text isn't cached yet:
   - Federal/state → the **WA SOS state voters' pamphlet** (one statewide PDF;
     store `statewide/raw/…pdf.url` + extracted text via
     `extract_pamphlet_text.py` / `extract_pdf_text.mjs`, indexed by
     `build_pamphlet_index.py`).
   - Local races → that **county's local pamphlet** (URLs in each
     `interim/app-*.json` `derived_from`); fall back to the VoteWA online
     voters' guide or accept campaign-site-only / `pamphlet-only` honest gaps.
   - Keep large PDFs out of git (`.pdf.url` + extracted text only).
3. **Fleet** (see spec below): research → score → refute each unit.
4. **Validate** the touched counties: `validate_scoring.py` must be green;
   `verify_dossiers.py` clean. Fix before moving on.
5. **Assemble:** `merge_scores.py` → `assemble_app_data.py` → `npm test` +
   `npm run build`. Spot-check a couple of the batch's counties with the
   end-to-end lookup harness (shim `/api/geocode` to the real Census geocoder,
   run `lookupBallotContext` + `scopeMatches`) and confirm those candidates now
   carry scores.
6. **Checkpoint:** commit the batch (dossiers + scoring + regenerated app-data).
   The site is now releasable at this new coverage level.
7. **Regenerate** `dossier-batches.json` (finished candidates drop out) and go to
   batch _k+1_.

Measures side-track: when a batch includes a county's local races, also score
that county's measures (Phase-4 format below) in the same pass.

---

## Fleet orchestration spec

Use the `Workflow` tool. Per research unit, a three-stage pipeline; fan units
out in parallel, bounded by the concurrency cap and web rate limits.

```
per unit (deep or light):
  Stage 1  research agent   -> dossiers/<unit>/_contest.md + <cand>.md
                               (live web: pamphlet text, campaign site, PDC,
                               leg.wa.gov / congress.gov, Tier-2 news/endorsements)
  Stage 2  scoring agent    -> scoring/<unit>.json   (DOSSIER-ONLY, no web;
                               reads rubric.json + the dossiers)
  Stage 3  refutation agent -> scoring/refutations/<unit>.json
                               (independent; tries to refute each score)
```

Orchestrator rules:
- **Stage 2 and 3 must not have web access** (or be strictly instructed
  dossier-only). The research↔scoring separation is the transparency guarantee.
- **Stage 3 is a different agent instance than Stage 2** for that unit.
- Pipeline units within a batch so a slow research task doesn't stall scoring of
  others.
- Throttle source hosts (SOS / county GIS / congress.gov / FEC / PDC); browser
  User-Agent; cache fetched pages.
- Agents return a small structured status (unit id, candidates written,
  evidence_levels, axes scored, unresolved identity ambiguity) — not file bodies.
- A red `validate_scoring.py` blocks the batch.

Measure scoring (Phase 4 format): for each measure emit `what_it_does`,
`cost_line`, `pro_summary`, `con_summary` (attributed), and `lean_mappings`
(e.g. `{"taxes": 2, "local-control": 1}` with basis + citations); `{}` if no
confident mapping. Refute measures too. Sources: the resolution / explanatory
statement + pro/con committee statements in the local pamphlet.

---

## Quality gates (a score is not "done" until all pass)

1. `validate_scoring.py` green (integer scores in [-2,2], citations exist in the
   cited dossier frontmatter, axis applicability, evidence_level matches).
2. Every score cites ≥1 source that actually appears in that candidate's dossier
   frontmatter.
3. Every scored candidate-axis pair has a refutation verdict.
4. Neutral tone in summaries/highlights/basis.
5. Same-name identity verified (jurisdiction/office) before attributing web
   facts — a real risk for common names in small counties.
6. `evidence_level` honest; axes omitted where evidence is absent (not guessed).

## Anti-patterns to reject

- Party-preference-inferred scores with a hand-wave citation.
- Fetching new facts during the scoring stage (breaks transparency).
- Uniform `confidence: high` across a thin dossier.
- Fabricated / mismatched citations (S-id not in frontmatter).
- Fanning a shared federal/state score onto a county where the
  `(district, office, candidate)` match doesn't actually hold.
- Silent truncation: if a unit skips candidates (no statement found), `log()` it
  — don't let it read as "covered."

## Risks

- **Deadline:** 590 dossiers + 82 measures in ~18 days. The batch model is the
  mitigation — front-loaded value means an early release already helps most
  voters even if later batches slip. Track batches-done vs. days-left and tell
  the owner where the line lands.
- **Thin-web down-ballot candidates:** many small-district candidates have only
  a pamphlet statement → correct outcome is `pamphlet-only`, few/omitted axes.
- **Source access:** some county sites block bots (Garfield, Skamania, Stevens
  seen in coverage work); SOS state pamphlet + VoteWA online guide are fallbacks.
- **Phase 0 bugs:** it edits shared scripts — the King byte-identical regression
  gate guards existing scores.

## Definition of done (per batch, and overall)

Per batch: its units have dossiers + scores + refutations; touched counties pass
`validate_scoring.py` + `verify_dossiers.py`; `merge_scores.py` +
`assemble_app_data.py` + `npm test` + `npm run build` green; spot-checked
counties show scored candidates; committed and releasable.

Overall: all 12 batches + 82 measures complete; every non-King voter receives
scored alignment on the contested races on their ballot.

---

## Key facts for the handoff agent (verified 2026-07-17)

- Dossier workload: **590** (uncontested excluded, federal/state deduped) in
  **12 batches**, `data/final/dossier-batches.json`. Naive count 1,333.
  Measures: **82**.
- Shared federal/state unique candidates: **276** (854 instances). King reuse is
  negligible (~13 candidates — King's metro districts barely reach other
  counties), so don't rely on it.
- Regenerate ordering: `python3 pipeline/build_dossier_batches.py`. Tune weights
  in that file (`POP`, `FEDERAL_REACH`, `STATE_REACH`, `SUBCOUNTY_DISCOUNT`) to
  change priority.
- Rubric categories in scope: `Federal`, `State` (deduped), `County`, `City`,
  `Judicial`, `PublicUtility`, `Port`. `applies_to` gates axes per category.
- Reference commits: coverage expansion `90978b6`; review fixes `815ed9e`; data
  corrections `c0d795d`.
