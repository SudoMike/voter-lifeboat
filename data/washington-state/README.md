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
| `2026-11-03-general` | November 3, 2026 General Election | active (`ACTIVE`); Statewide-Only Guide (5 Supreme Court contests, 3 initiatives), no county packages shipped yet |

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
in `pipeline/election.py`. While an election has no contests and no measures
the app shows a notice page instead of the guide.

Every file in `data/final/` must be traceable back through package `interim/`
files to verbatim or pointer `raw/` sources. Large source artifacts should be
stored as small `.url` pointer files plus metadata, not committed binaries.

## Packages

Paths below are relative to `elections/<id>/`.

### `statewide/`

Owns Statewide Contests and statewide measures: those whose electorate is all
Washington voters (ADR-0003).

- General (`2026-11-03-general`): `interim/contests.json` (five Supreme Court
  contests) and `interim/measures.json` (IP26-645, IL26-001, IL26-638) are
  hand-built from the VoteWA GENERAL 2026 candidate list and the SOS voters'
  pamphlet, with explicit `{"kind":"STATEWIDE"}` scope, and are the ballot
  source `assemble_app_data.py` reads. Dossiers, scoring and refutations for
  all eight live here too. See `statewide/COMPLETENESS.md`.
- Primary (`2026-08-04-primary`): owns the Supreme Court scoring/dossiers, but
  its `interim/contests.json` is the normalizer's research-only list of
  deduplicated congressional/legislative contests; the primary's Supreme Court
  ballot entries come from King's interim files.

#### District contest ownership (decided in issue #9)

From the general onward, congressional and legislative contests are owned by
the county packages, even when a district crosses county lines. The statewide
package holds only Statewide Contests and measures. This is declared per
election in `pipeline/election.py` (`APP_PACKAGES[<id>]["district_contests"]`:
`"statewide"` for the primary, `"county"` for the general), and
`normalize_research_inputs.py` enforces it (see Transformations).

### Which packages ship

`pipeline/election.py` `APP_PACKAGES[<id>]` declares, per election, whether the
statewide package is the ballot source for Statewide Contests
(`statewide_ballot`) and which county packages are complete enough to ship
(`counties`). `merge_scores.py` and `assemble_app_data.py` read only those
packages, so a county package being researched never leaks into the app.
The primary uses `counties: None` (King's interim files plus every county's
`app-*.json`, its original behaviour). The general declares no counties yet,
so `coverage.supported_counties` is empty and every Washington address gets
the Statewide-Only Guide; King joins in #16.

### `counties/king/`

Owns King County local coverage: King County Elections raw pages/CSVs, local
pamphlet text, county/local dossiers, measures, and county-specific scoping.
King County is fully supported in the primary. In the general its package is
being researched and is not shipped.

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
| `pipeline/normalize_research_inputs.py` | county `app-*.json` → county `interim/{contests,measures}.json`; for the primary also `E/statewide/interim/contests.json` (see below) |
| `pipeline/build_research_plan.py` | package contests/measures/index → `interim/research-plan.json` |
| `pipeline/verify_dossiers.py` | package dossiers + plan → `interim/dossier-audit.json` |
| `pipeline/extract_axis_notes.py` | package `_contest.md` files + measures → `E/counties/king/interim/axis-notes.md` |
| `pipeline/validate_scoring.py` | package scoring + dossiers + `F/rubric.json` → validation report |
| `pipeline/merge_scores.py` | shipped packages' scoring/refutations → `F/{scores,measures}.json` |
| `pipeline/assemble_app_data.py` | shipped packages + `F/{scores,measures,rubric,interview}.json` → `F/app-data.json`, `app/public/data/<id>/app-data.json`, `elections.json` |
| `pipeline/build_dossier_batches.py` | `F/app-data.json` → `F/dossier-batches.json` |

`F/rubric.json`, `F/interview.json` and `F/rubric-derivation.md` are
hand-authored per election, not generated.

`normalize_research_inputs.py` never replaces an interim file whose `script`
field names another script (or is `null`, as in hand-built files):

- Where district contests are statewide-owned (the primary), statewide
  `interim/contests.json` is the normalizer's own file and is regenerated in
  full from the deduplicated congressional and legislative contests; a
  hand-built file there stops the run before anything is written.
- Where district contests are county-owned (the general), the statewide
  package is never written: `interim/{contests,measures}.json` stay exactly as
  hand-built, and district contests remain in each county's
  `interim/contests.json`. (Before #9 the normalizer appended district
  contests to a hand-built statewide file; that path is removed.)
- Statewide `interim/measures.json` that is hand-built is left untouched.
- A county `interim/{contests,measures}.json` written by another script stops
  the run before anything is written.

King has no `app-contests.json`, so its contests never feed the normalizer.
The general currently has no other county packages, so running the
normalizer for it changes no file.

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
- Supported counties: the primary ships King County (full) plus the other 38
  counties (partial); the general ships none yet (`statewide_complete: true`,
  `supported_counties: []`), so every Washington address gets the
  Statewide-Only Guide.
- Coverage statuses emitted by the app: `full_county`, `partial_county`,
  `statewide_only`.
- Statewide scope is explicit (`{"kind":"STATEWIDE"}`); countywide and local
  scopes are not represented by the old overloaded `ALL` value.
