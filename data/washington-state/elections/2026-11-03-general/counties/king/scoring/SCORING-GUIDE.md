# Scoring guide

How every file in this directory was produced. Scoring agents follow this
spec exactly. Scoring is a **dossier-only** stage: no web access, no new
facts. If the dossier doesn't support a score, the axis is omitted.

This guide covers every package in the November 3, 2026 general election.
Paths below use `E` = `data/washington-state/elections/2026-11-03-general`
and `<package>` = `statewide` or `counties/<county>` (the package that owns
the contest). As in the primary, the statewide package follows this guide
rather than carrying its own copy.

## Inputs

- `data/final/2026-11-03-general/rubric.json` — the 15 axes, pole
  definitions, and which contest categories each axis applies to. READ IT
  FIRST. Its derivation and the intended statewide measure mappings are in
  `data/final/2026-11-03-general/rubric-derivation.md`.
- `E/<package>/dossiers/<contest-slug>/*.md` — the only permitted evidence.
- `E/<package>/interim/contests.json` — candidate names/party/category per
  contest.

## Output — `E/<package>/scoring/<contest-slug>.json`

```json
{
  "contest_slug": "...",
  "scored_at": "2026-07-16",
  "derived_from": ["E/<package>/dossiers/<contest-slug>/"],
  "office_does": "One plain sentence: what this office actually does.",
  "race_blurb": "1-2 neutral sentences on this race's dynamics.",
  "candidates": [
    {
      "slug": "...",
      "summary": "1-2 neutral sentences for the candidate card.",
      "highlights": [
        "3-5 short bullets (2-3 for light contests): positions/record, each ending with its dossier citation tag like [S2]"
      ],
      "evidence_level": "copy from the dossier frontmatter",
      "withdrawn": false,
      "scores": {
        "<axis-id>": {
          "score": -2,
          "confidence": "high | medium | low",
          "citations": ["S1", "S3"],
          "basis": "One line: the evidence that places them here."
        }
      }
    }
  ]
}
```

## Rules

- **Sign convention:** -2 = fully pole_a, +2 = fully pole_b, 0 = genuinely
  mixed (NOT unknown). Integers only.
- **Omission over guessing:** no supporting evidence in the dossier → omit
  the axis for that candidate entirely. An omitted axis is an honest gap the
  app displays; a guessed score is a lie. Never infer from party preference
  alone — that's what the evidence is supposed to show.
- **Applicability:** score only axes whose `applies_to` includes the
  contest's category. Judicial candidates (StateSupremeCourt, DistrictCourt,
  Municipal Court, Court of Appeals): ONLY `judicial`, `safety`, and
  `experience`, and `safety` only from documented
  bail/diversion/professional-formation evidence. Judges are **never**
  scored on `social` or `parental-rights`.
- **`social` vs `parental-rights`** (split for the general; see
  rubric-derivation.md): `social` is gender, LGBTQ+ and reproductive policy
  (trans participation in sports, gender-affirming care, abortion,
  anti-discrimination law). `parental-rights` is parents and public schools
  (notification, record access, opt-outs over what schools teach and
  provide). Score each from evidence about that topic only: a position on
  curricula opt-outs is not evidence on `social`, and a position on abortion
  is not evidence on `parental-rights`. Candidates scored on `social` in the
  primary are re-checked against the narrowed definition during their
  refresh, not copied over.
- **Confidence:** high = record or repeated explicit statements; medium =
  single clear statement or strong endorsement pattern; low = indirect
  inference (use sparingly; the app excludes low from alignment math).
- **Citations** must be source ids that exist in that candidate's dossier
  frontmatter. Every score carries at least one.
- **experience axis:** -2 = maximal proven-record case (long tenure,
  enacted record), +2 = maximal outsider/renewal case. This describes the
  candidate's profile, not its merit.
- **Withdrawn candidates** (e.g., Calkins, Seattle Muni Court): set
  `"withdrawn": true`, keep summary, omit scores.
- Neutral wording everywhere. Summaries/highlights describe; they never
  evaluate.

## Refutation pass — `E/<package>/scoring/refutations/<contest-slug>.json`

A second, independent agent re-reads the dossiers and tries to REFUTE each
score: wrong direction, overstated confidence, citation doesn't support it,
axis inapplicable, missed evidence pointing the other way.

```json
{
  "contest_slug": "...",
  "reviewed_at": "2026-07-16",
  "verdicts": [
    {"candidate": "<slug>", "axis": "<axis-id>",
     "verdict": "upheld | adjust | refuted",
     "adjusted_score": -1, "adjusted_confidence": "medium",
     "note": "why (only for adjust/refuted)"}
  ],
  "missing": [
    {"candidate": "<slug>", "axis": "<axis-id>",
     "proposed_score": 1, "confidence": "medium", "citations": ["S2"],
     "basis": "evidence the scorer missed"}
  ]
}
```

Every scored candidate-axis pair gets a verdict. `pipeline/merge_scores.py`
applies them: refuted scores are dropped, adjustments applied, well-supported
missing scores added.

## Measures — `E/<package>/scoring/measures.json`

For each measure: display content (what it does, cost line, pro/con
one-liners with attribution) plus `lean_mappings`: axis directions a YES
vote aligns with, e.g. `{"taxes": 2, "local-control": 2}` with basis +
citations. Strength 1 or 2 (sign = pole direction). A measure with no
confident mapping gets `"lean_mappings": {}` — the app shows no Lean.
Measure refutations go in `E/<package>/scoring/refutations/measures.json`.

Intended statewide mappings (confirm against the measure dossier): I-645 →
`taxes` and `local-control`; I-1 → `parental-rights`; I-638 → `social`.
School-district and other school-adjacent measures may map to
`parental-rights` when the dossier supports it.

## Addendum (2026-10-08, issue #19): evidence rules

These apply to every package in this election from this date. Existing
scoring files are not rewritten for them; they apply at each contest's next
scoring or refutation pass.

- **Single-vote evidence on `taxes`.** A legislator's floor vote on ESSB 6346
  (chapter 238, Laws of 2026, the 9.9% tax on income over $1M), when it is
  the only `taxes` evidence in the dossier, scores magnitude 1 (+1 for a yes
  vote, -1 for a no vote) at `medium` confidence. Score ±2 or `high` only when
  the dossier has a second independent source on taxes (another recorded
  vote, a sponsored bill, an explicit statement or a platform plank).
- **`parental-rights` scope.** Score it only for State legislative contests
  and measures, as its `applies_to` says. Federal, County and City
  candidates are not scored on it even when the dossier records a position;
  the position stays in the dossier and can inform the race blurb.
- **`local-control` vs `parental-rights`.** Evidence about school
  governance (who decides curricula, notification, record access and
  opt-outs) is `parental-rights` evidence, not `local-control` evidence.
  `local-control` keeps zoning, growth management, state mandates on local
  governments, annexations and regional authorities.
