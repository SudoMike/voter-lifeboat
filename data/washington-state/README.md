# Data pipeline — Washington State August 4, 2026 Primary

The Washington dataset is package-based:

```
statewide/       Washington-wide contests and sources
counties/king/   King County local package
../final/        generated app-facing JSON
```

Every file in `data/final/` must be traceable back through package `interim/`
files to verbatim or pointer `raw/` sources. Large source artifacts should be
stored as small `.url` pointer files plus metadata, not committed binaries.

## Packages

### `statewide/`

Owns Statewide Contests: contests whose electorate is all Washington voters for
the active election. For this election that package owns the Supreme Court
primary contests and their scoring/dossiers. Its raw source pointer is the
official VoteWA PRIMARY 2026 Candidate List.

### `counties/king/`

Owns King County local coverage: King County Elections raw pages/CSVs, local
pamphlet text, county/local dossiers, measures, and county-specific scoping.
King County remains the first fully supported county.

## Transformations

| Script | In → Out |
|---|---|
| `pipeline/extract_pamphlet_text.py` | King `.pdf.url` pointers → cached PDFs → `counties/king/interim/pamphlet-text/` |
| `pipeline/parse_candidates.py` | King raw KCE HTML/CSV → `counties/king/interim/{contests,measures}.json` |
| `pipeline/build_pamphlet_index.py` | King contests/measures/page text → `counties/king/interim/pamphlet-index.json` |
| `pipeline/build_research_plan.py` | King contests/measures/index → `counties/king/interim/research-plan.json` |
| `pipeline/verify_dossiers.py` | package dossiers + King plan → `counties/king/interim/dossier-audit.json` |
| `pipeline/extract_axis_notes.py` | package `_contest.md` files + King measures → `counties/king/interim/axis-notes.md` |
| `pipeline/validate_scoring.py` | package scoring + dossiers + rubric → validation report |
| `pipeline/merge_scores.py` | state + King scoring/refutations → `data/final/{scores,measures}.json` |
| `pipeline/assemble_app_data.py` | packages + final scores/rubric/interview → `data/final/app-data.json` and app copy |

## Election Facts

- Active election: August 4, 2026 Primary and Special Election.
- Public route: `/washington-state`.
- Supported counties: King County.
- Coverage statuses emitted by the app: `full_county`, `partial_county`,
  `statewide_only`.
- Statewide scope is explicit (`{"kind":"STATEWIDE"}`); countywide and local
  scopes are not represented by the old overloaded `ALL` value.
