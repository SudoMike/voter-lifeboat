# Scoring guide

How every file in this directory was produced. Scoring agents follow this
spec exactly. Scoring is a **dossier-only** stage: no web access, no new
facts. If the dossier doesn't support a score, the axis is omitted.

## Inputs

- `data/final/rubric.json` — the 14 axes, pole definitions, and which
  contest categories each axis applies to. READ IT FIRST.
- `data/dossiers/<contest-slug>/*.md` — the only permitted evidence.
- `data/interim/contests.json` — candidate names/party/category per contest.

## Output — `data/scoring/<contest-slug>.json`

```json
{
  "contest_slug": "...",
  "scored_at": "2026-07-16",
  "derived_from": ["data/dossiers/<contest-slug>/"],
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
  Municipal Court): ONLY `judicial`, `safety`, and `experience`, and `safety`
  only from documented bail/diversion/professional-formation evidence.
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

## Refutation pass — `data/scoring/refutations/<contest-slug>.json`

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

## Measures — `data/scoring/measures.json`

For each measure: display content (what it does, cost line, pro/con
one-liners with attribution) plus `lean_mappings`: axis directions a YES
vote aligns with, e.g. `{"taxes": 2, "local-control": 2}` with basis +
citations. Strength 1 or 2 (sign = pole direction). A measure with no
confident mapping gets `"lean_mappings": {}` — the app shows no Lean.
