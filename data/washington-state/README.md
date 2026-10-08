# Data pipeline — Washington State

The Washington dataset is split by election, and each election is
package-based:

```
elections/ACTIVE                       one line: the Active Election's id
elections/<id>/statewide/              Washington-wide contests and sources
elections/<id>/counties/king/          King County local package
elections/<id>/counties/*/             other county packages
../final/<id>/                         generated app-facing JSON for <id>
../final/elections.json                index of elections with app data
```

Elections:

| id | Election | Status |
|---|---|---|
| `2026-08-04-primary` | August 4, 2026 Primary and Special Election | archived, served at `/washington-state/2026-08-04-primary` |
| `2026-11-03-general` | November 3, 2026 General Election | active (`ACTIVE`); stub app data, no contests yet |

Every pipeline script takes `--election <id>`; without it the script uses the
id in `elections/ACTIVE`. Outputs land in `data/final/<id>/` and the app copy
in `app/public/data/<id>/app-data.json`. `assemble_app_data.py` also writes
`elections.json` (to `data/final/` and `app/public/data/`), which lists every
election whose `app-data.json` exists and names the active one. Each entry
carries `id` (package id), `app_id` (the `election.id` inside its app data,
which report links carry) and `status` (`active` or `archived`). The app loads
that index first, then the file for the route's election (`/washington-state`
is the active one, `/washington-state/<id>` any listed one).

An election package may be empty: `merge_scores.py` then writes empty
`scores.json`/`measures.json`, and `assemble_app_data.py` writes app data with
no contests, no supported counties and the `statewide_complete` value declared
in `pipeline/election.py`. While the active election has no contests the app
shows a notice page instead of the guide.

Every file in `data/final/` must be traceable back through package `interim/`
files to verbatim or pointer `raw/` sources. Large source artifacts should be
stored as small `.url` pointer files plus metadata, not committed binaries.

## Packages

Paths below are relative to `elections/<id>/`.

### `statewide/`

Owns Statewide Contests: contests whose electorate is all Washington voters for
the active election. For this election that package owns the Supreme Court
primary contests and their scoring/dossiers. Its raw source pointer is the
official VoteWA PRIMARY 2026 Candidate List.

### `counties/king/`

Owns King County local coverage: King County Elections raw pages/CSVs, local
pamphlet text, county/local dossiers, measures, and county-specific scoping.
King County remains the first fully supported county.

### Other County Packages

County packages may exist before the app supports that county. A package marked
`ingested, not app-supported` has official source pointers in place, but still
needs parsed contests/measures, dossiers, scoring files, and district scoping
before it can be added to `coverage.supported_counties`.

## Transformations

`E` is `data/washington-state/elections/<id>`; `F` is `data/final/<id>`.

| Script | In → Out |
|---|---|
| `pipeline/extract_pamphlet_text.py` | King `.pdf.url` pointers → cached PDFs → `E/counties/king/interim/pamphlet-text/` |
| `pipeline/extract_pdf_text.mjs <county>` | county `.pdf.url` pointers → `E/counties/<county>/interim/pdf-text/` |
| `pipeline/build_votewa_lite_data.py` | VoteWA candidate-list CSVs → `E/counties/*/interim/app-{contests,measures}.json` |
| `pipeline/build_<county>_lite_data.py` | county pdf-text → `E/counties/<county>/interim/app-{contests,measures}.json` (clark, kitsap, pierce, snohomish, spokane, thurston) |
| `pipeline/parse_candidates.py` | King raw KCE HTML/CSV → `E/counties/king/interim/{contests,measures}.json` |
| `pipeline/build_pamphlet_index.py` | King contests/measures/page text → `E/counties/king/interim/pamphlet-index.json` |
| `pipeline/normalize_research_inputs.py` | county `app-*.json` → county `interim/{contests,measures}.json` + `E/statewide/interim/contests.json` |
| `pipeline/build_research_plan.py` | package contests/measures/index → `interim/research-plan.json` |
| `pipeline/verify_dossiers.py` | package dossiers + plan → `interim/dossier-audit.json` |
| `pipeline/extract_axis_notes.py` | package `_contest.md` files + measures → `E/counties/king/interim/axis-notes.md` |
| `pipeline/validate_scoring.py` | package scoring + dossiers + `F/rubric.json` → validation report |
| `pipeline/merge_scores.py` | package scoring/refutations → `F/{scores,measures}.json` |
| `pipeline/assemble_app_data.py` | packages + `F/{scores,measures,rubric,interview}.json` → `F/app-data.json`, `app/public/data/<id>/app-data.json`, `elections.json` |
| `pipeline/build_dossier_batches.py` | `F/app-data.json` → `F/dossier-batches.json` |

`F/rubric.json`, `F/interview.json` and `F/rubric-derivation.md` are
hand-authored per election, not generated.

## Election Facts

- Active election: November 3, 2026 General Election (`2026-11-03-general`).
  Its `F/rubric.json`, `F/interview.json` and `F/rubric-derivation.md` are
  verbatim copies of the primary's (see the `.meta.json` siblings and the
  interview's `derived_from`).
- Archived: August 4, 2026 Primary and Special Election
  (`2026-08-04-primary`; its app-data `election.id` is
  `2026-08-04-primary-special`, which report links carry).
- Public routes: `/washington-state` (active election),
  `/washington-state/<id>` (any election in `elections.json`).
- Supported counties: King County.
- Coverage statuses emitted by the app: `full_county`, `partial_county`,
  `statewide_only`.
- Statewide scope is explicit (`{"kind":"STATEWIDE"}`); countywide and local
  scopes are not represented by the old overloaded `ALL` value.
