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
| `2026-11-03-general` | November 3, 2026 General Election | active (`ACTIVE`); King, Snohomish, Pierce, Clark, Kitsap, Thurston, Yakima, Whatcom, Benton, Skagit, Cowlitz and Grant Counties at Full County Coverage, Spokane County at partial coverage (Stevens County PUD seat unresolvable), every other county a Statewide-Only Guide (5 Supreme Court contests, 3 initiatives) |

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
`app-*.json`, its original behaviour). The general declares `["king"]` (#16),
so King is its only Supported County and every other Washington address gets
the Statewide-Only Guide.

### `counties/king/`

Owns King County local coverage: King County Elections raw pages/CSVs, local
pamphlet text, county/local dossiers, measures, and county-specific scoping.
King County is fully supported in both elections; the general's package
status is in `elections/2026-11-03-general/counties/king/COMPLETENESS.md`.

From the general on, King's interim files are schema 2 (`parse_candidates.py`;
since #20 `office` is the seat and `district` the jurisdiction, as in every
other package)
and `assemble_app_data.py` reads them by rule rather than by the primary's
hand-written scope tables:

- `owner`: `"statewide"` marks the Supreme Court contests KCE also lists. They
  are not shipped from King; the statewide package's own contest takes their
  place in King's (KCE ballot) order, so each appears once. Assembly stops if
  King lists a statewide-owned contest the statewide package lacks, or with
  different candidate names.
- `scope`: used verbatim. Every DISTRICT layer must be one the King District
  Adapter resolves (`election.DISTRICT_ADAPTER_LAYERS["king"]`, kept equal to
  `KING_LAYERS` in `app/src/lib/geo.js` by `test_general_app_data.py`), or
  King is assembled as `partial_county` and the unresolvable records are
  printed. `CEMDST` (Cemetery District No. 1) is resolved from the WA DOR
  cemetery layer; the measure's `scope_unresolved` note in
  `interim/measures.json` predates that and is not read by assembly.
- `uncontested`: shipped information-only, with no scores: `office_does`,
  `race_blurb` and the candidate's summary and highlights from the
  empty-score `scoring/<slug>.json`. An uncontested contest with no scoring
  file ships as the official ballot entry alone (`evidence_level:
  "official-ballot-only"`); a contested contest with no scoring file stops
  assembly.
- Pamphlet pages: from each dossier's `type: pamphlet` source refs
  (`pipeline/pamphlet_refs.py`), which name the statement page.
  `interim/pamphlet-index.json` is a name search that also hits endorsement
  lists on other candidates' pages, so it is used only for a record with no
  dossier, and for a legislative contest only on pages that carry that
  contest's own statement heading. Edition ids are the King raw pointer names
  (`local-edition`, `voters-pamphlet-edition-0N-king-*`); the app links them
  in `app/src/lib/officialLinks.js`.

### Other County Packages

County packages may exist before the app supports that county. A package marked
`ingested, not app-supported` has official source pointers in place, but still
needs parsed contests/measures, dossiers, scoring files, and district scoping
before it can be added to `coverage.supported_counties`.

In the general, county packages are built from VoteWA election 899's
candidate list (`pipeline/fetch_votewa_candidate_list.py`, then the county's
builder; the export's Election Status column is blank, so
`election.VOTEWA_SOURCES` filters on `""`) and taken through research,
scoring and refutation by `docs/county-wave-playbook.md`. A race another
package already researched (for example a legislative district King shares)
is not researched again: `build_research_plan.py` names the owning package
and `assemble_app_data.py` ships that package's scoring and dossiers.

A declared non-King county (Snohomish, Spokane and Pierce, from #21; Clark,
Kitsap and Thurston, from #22; Yakima, Whatcom, Benton, Skagit, Cowlitz and
Grant, from #28) ships its
`interim/app-{contests,measures}.json`. Its candidates' `pamphlet_pages` come
from its own dossiers' `type: pamphlet` citations (`pamphlet_refs.py`; edition
ids are the package's `raw/*/<edition>.pdf.url` pointer names, such as
`local-voters-pamphlet`, or Pierce's `voters-pamphlet-edition-09-pierce` and
Thurston's `voters-pamphlet-edition-27-thurston`, the SOS editions); a race
shipped with another package's research
carries none. A county whose dossiers cite VoteWA's unpaged online voters'
guide instead of a printed pamphlet (Spokane, Kitsap, Yakima, Whatcom,
Benton, Grant; Pierce's county offices and local measures) ships no pages for them; the app links
that guide (`officialLinks.js` `countyGuides`). Its coverage is `full_county` only when its package says so and
every DISTRICT scope it ships is in `election.DISTRICT_ADAPTER_LAYERS[<county>]`
(the Census layers plus `geo.js` `COUNTY_LAYERS[<county>]`). See the county's
`COMPLETENESS.md`.

The general's VoteWA pointer metas pin the export by `sha256` and, once
re-written by the fetcher, `sha256_case_normalized` (VoteWA flips the case of
the District Type and District columns between fetches; `pipeline/votewa.py`).

## Transformations

`E` is `data/washington-state/elections/<id>`; `F` is `data/final/<id>`.

| Script | In → Out |
|---|---|
| `pipeline/extract_pamphlet_text.py` | King `.pdf.url` pointers → cached PDFs → `E/counties/king/interim/pamphlet-text/` |
| `pipeline/extract_pdf_text.mjs <county>` | county `.pdf.url` pointers → `E/counties/<county>/interim/pdf-text/` |
| `pipeline/fetch_votewa_candidate_list.py` | VoteWA candidate list (form-post CSV export) → `data/.cache/votewa/` + `E/counties/<county>/raw/votewa/candidate-list.csv.{url,meta.json}` (sha256-pinned pointer; the general onward) |
| `pipeline/build_votewa_lite_data.py` | VoteWA candidate-list CSVs (`pipeline/votewa.py`) → `E/counties/*/interim/app-{contests,measures}.json` (the 32 counties in `COUNTY_CONFIG`; `--county` for one) |
| `pipeline/build_<county>_lite_data.py` | primary: county pdf-text → `E/counties/<county>/interim/app-{contests,measures}.json`; the general onward: the county's VoteWA export (clark, kitsap, pierce, snohomish, spokane, thurston) |
| `pipeline/parse_candidates.py` | King raw KCE HTML/CSV → `E/counties/king/interim/{contests,measures}.json` |
| `pipeline/build_pamphlet_index.py` | King contests/measures/page text → `E/counties/king/interim/pamphlet-index.json` |
| `pipeline/normalize_research_inputs.py` | county `app-*.json` → county `interim/{contests,measures}.json`; for the primary also `E/statewide/interim/contests.json` (see below) |
| `pipeline/build_research_plan.py` | package contests/measures/index → `interim/research-plan.json` (in the general, also which races another package already researched: `pipeline/shared_contests.py`) |
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
In the general it normalizes the VoteWA-built county packages with a
general export: the six of #20 (clark, kitsap, pierce, snohomish, spokane,
thurston), shipped in #21 and #22, and yakima, whatcom, benton, skagit,
cowlitz and grant, shipped in #28.

## Election Facts

### November 3, 2026 General Election (`2026-11-03-general`, active)

- Election day: Tuesday, November 3, 2026. Ballots mailed by October 16
  (18 days before, RCW 29A.40.070). Registration and updates online or by
  mail by October 26 (8 days before, RCW 29A.08.140); in person until 8 p.m.
  on November 3.
- App-data `election.id`: `2026-11-03-general` (same as the package id).
- Statewide Contests: Supreme Court Justice Positions 1, 3, 4, 5 and 7
  (Positions 1 and 5 are 2-year unexpired terms). Statewide measures:
  IP26-645 (I-645, state and local taxes), IL26-001 (I-1, parental rights in
  public school), IL26-638 (I-638, participation in K-12 athletics). Details
  and pamphlet pages in `statewide/COMPLETENESS.md`.
- Official sources: VoteWA election 899 (`statewide/raw/votewa-general-2026-candidate-list.url`);
  SOS voters' pamphlet, every regional edition listed in
  `statewide/interim/pamphlet-editions.json` (Edition 06 is the statewide
  reference); King County Elections eid 55 (`KCE_SOURCES` in
  `pipeline/election.py`); King local pamphlet
  `counties/king/raw/pamphlet/local-edition.pdf.url`.
- Rubric: 15 axes. `F/rubric.json`, `F/interview.json` and
  `F/rubric-derivation.md` started as copies of the primary's and were then
  edited for this ballot (#4): `social` narrowed to gender, LGBTQ+ and
  reproductive policy, and `parental-rights` (parents and public schools)
  added. The rationale is in the dated section of `F/rubric-derivation.md`;
  provenance is in the `.meta.json` siblings and the interview's
  `derived_from`. Intended measure axes: I-645 → `taxes`, `local-control`;
  I-1 → `parental-rights`; I-638 → `social`.
- Coverage today: `coverage.statewide_complete: true` and thirteen Supported
  Counties: King at `full_county` (#16; 92 contests, 41 uncontested and
  information-only, 15 measures), Pierce at `full_county` and Spokane at
  `partial_county` (#21), Snohomish at `full_county` (shipped partial in
  #21, District Court resolved in #27), Clark, Kitsap and Thurston at
  `full_county` (#22), and Yakima, Whatcom, Benton, Skagit, Cowlitz and
  Grant at `full_county` (#28). 397 contests (5 statewide Supreme Court
  contests included) and 105 measures. Every other Washington address gets the
  Statewide-Only Guide. `docs/county-wave-playbook.md` is the procedure for
  taking a county from research to shipped.
- District (congressional and legislative) contests are county-owned
  (`district_contests: "county"`). Uncontested contests ship information-only
  (`scoring/<slug>.json` with empty `scores`).
- Research and scoring rules: `counties/king/dossiers/RESEARCH-GUIDE.md` and
  `counties/king/scoring/SCORING-GUIDE.md` cover every package in this
  election, the statewide package included.

### August 4, 2026 Primary and Special Election (`2026-08-04-primary`, archived)

- App-data `election.id`: `2026-08-04-primary-special`, which its report
  links carry. Both ids resolve to this election.
- Served read-only at `/washington-state/2026-08-04-primary`: a banner, no
  Anonymous Report Records. Its package, `F` files and app data are frozen so
  its `data_version` stays stable.
- Rubric: 14 axes, with the original `social` ("Social issues & schools").
- Supported counties: all 39. 28 ship `full_county` (King among them) and
  11 `partial_county`, where a commissioner or PUD race has no queryable
  official district boundary and is hidden.

### Both elections

- Public routes: `/washington-state` (active election),
  `/washington-state/<id>` (any election in `elections.json`).
- Coverage statuses emitted by the app: `full_county`, `partial_county`,
  `statewide_only`.
- Statewide scope is explicit (`{"kind":"STATEWIDE"}`); countywide and local
  scopes are not represented by the old overloaded `ALL` value.
