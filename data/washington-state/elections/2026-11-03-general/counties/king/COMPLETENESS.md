# King County Completeness Note

Election: 2026 Washington general election, November 3, 2026 (KCE eid 55).

As of 2026-10-08 (#16) this package ships in the general at
`coverage: "full_county"`: `pipeline/election.py` declares it in
`APP_PACKAGES["2026-11-03-general"]["counties"]`, and every King contest and
measure scope is one the King District Adapter (`app/src/lib/geo.js`
`KING_LAYERS`) resolves from an address. How assembly reads this package is
described under `counties/king/` in `data/washington-state/README.md`.

## What ships

`interim/contests.json` lists 97 contests. Five are the Supreme Court
contests (`owner: "statewide"`); they ship once, from the statewide package.
The other 92 are King's:

| Kind | Contests | Contested | Uncontested (info-only) | Scope |
|---|---|---|---|---|
| U.S. Representative | 4 | 4 | 0 | `CONGDST` |
| State Senator / Representative | 46 | 37 | 9 | `LEGDST` |
| Prosecuting Attorney, Assessor, Director of Elections | 3 | 1 | 2 | countywide |
| Metropolitan King County Council | 4 | 2 | 2 | `KCCDST` |
| Court of Appeals, Division 1, District 1 | 2 | 0 | 2 | countywide (the district is King County) |
| District Court (NE, SE, SW, W, Shoreline) | 25 | 5 | 20 | `JUDDST` (`NE`, `SE`, `SW`, `W`, `SH`) |
| Seattle City Council District 5 | 1 | 1 | 0 | `SCCDST` `SCC5` |
| Seattle Municipal Court | 7 | 1 | 6 | `CITY` `Seattle` |

`interim/measures.json` lists 15 local measures, scoped `CITY` (Bothell,
Clyde Hill, Issaquah, Kenmore, Lake Forest Park, Milton, SeaTac, Seattle,
Shoreline), `SCHDST` (Auburn 408, Highline 401 x2, Kent 415), `FIRDST` (20)
and `CEMDST` (Cemetery District No. 1). All 15 are researched and scored
(`scoring/measures.json`, refutations applied by `merge_scores.py`).

Uncontested contests carry no scores. 32 of the 41 ship the office and
candidate summary from their empty-score scoring file. The other nine, all
uncontested legislative seats (LD11 Rep. Pos. 2; LD33, LD34, LD45 and LD48
Senate; LD34 Rep. Pos. 1; LD36 Rep. Pos. 1 and 2; LD43 Rep. Pos. 2), have no
scoring file or dossier in this package and ship as the official ballot
entry alone (`evidence_level: "official-ballot-only"`, with the candidate's
SOS pamphlet statement page).

## District scoping

The layers' values were checked against saved distinct-value queries in
`raw/gis/` (`JUDDST` `NE`/`SE`/`SH`/`SW`/`W`, `FIRDST` `20`, `SCHDST`
`401`/`408`/`415`, `SCCDST` `SCC5`, the `CITY` names). Cemetery District
No. 1 has no King GIS layer. `KING_LAYERS.CEMDST` reads WA DOR tax-district
layer 3 (`CEM2025`, the newest tax year when re-listed live on 2026-10-08),
whose only King feature is `DISTATTRIB` `1` (`raw/gis/dor-cemdst-king.json`).
A live point query at 10105 SW Bank Rd, Vashon returned `1`; downtown
Seattle returned nothing. DOR renumbers its layers when it publishes a new
tax year, so re-check the id before the next election.

## Known gaps

- No `term` is recorded for King contests in `interim/contests.json`, so
  none ships (the statewide package carries terms for its contests).
- The nine uncontested legislative seats above have no researched summary.
- `interim/measures.json` still carries the cemetery measure's
  `scope_unresolved` note, written by `parse_candidates.py` before King's
  adapter had a `CEMDST` layer. Assembly does not read it.
- Measure fields that are not shipped to the app have parse nits: Milton
  (from VoteWA JSON) has no `passage_requirement` or `contact`, and its
  statement-for text has the committee line spliced into the first
  paragraph; Clyde Hill's opposition committee withdrew and no committee name
  is recorded.
