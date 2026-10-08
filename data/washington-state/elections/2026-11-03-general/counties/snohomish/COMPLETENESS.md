# Snohomish County Completeness Note

Election: 2026 Washington general election, November 3, 2026 (VoteWA
election 899, county code 34).

As of 2026-10-08 (#21) this package ships in the general at
`coverage: "partial_county"`: `pipeline/election.py` declares it in
`APP_PACKAGES["2026-11-03-general"]["counties"]` with a
`DISTRICT_ADAPTER_LAYERS["snohomish"]` entry, and every contest and measure
scope except the District Court seats' `DISTCRT` is one the Snohomish
District Adapter (Census `CONGDST`/`LEGDST`/`CITY` plus `app/src/lib/geo.js`
`COUNTY_LAYERS.snohomish`) resolves from an address. Assembly reads
`interim/app-contests.json` and `interim/app-measures.json`, built by
`pipeline/build_snohomish_lite_data.py` from the VoteWA candidate list and
the county's sample ballot and Local Voters' Pamphlet.

## What ships

35 contests (23 contested, 12 uncontested) and 17 measures. The Supreme
Court contests are dropped by the builder and ship once, from the statewide
package.

| Kind | Contests | Contested | Uncontested (info-only) | Scope |
|---|---|---|---|---|
| U.S. Representative (CD 1, 2, 8) | 3 | 3 | 0 | `CONGDST` |
| State Senator / Representative (LD 1, 10, 12, 21, 32, 38, 39, 44) | 20 | 19 | 1 (LD 38 Rep. Pos. 2) | `LEGDST` |
| Prosecuting Attorney | 1 | 0 | 1 | countywide |
| Court of Appeals, Division 1, District 2, Position 2 | 1 | 0 | 1 | countywide |
| District Court (Cascade, Everett, Evergreen, South) | 9 | 0 | 9 | `DISTCRT` (unresolvable) |
| PUD No. 1 Commissioner District 1 | 1 | 1 | 0 | countywide (whole PUD votes in the general, RCW 54.12.010(3)) |

Nine races were researched in King and ship with King's scoring and
dossiers (`shared_contests.contest_key`): CD 1, CD 8, LD 1 Rep. Pos. 1 and 2,
LD 12 Rep. Pos. 1 and 2, LD 32 Senate and Rep. Pos. 1 and 2. They carry no
`pamphlet_pages` (King's pages are in King's editions). The other 14
contested races and the uncontested seats were researched here; their
candidates' pamphlet pages come from their dossiers' citations of
`local-voters-pamphlet` (40 of 58 candidates).

The PUD race has no scorable rubric axis; both candidates ship summaries
and sources without scores.

Measures: five Snohomish County charter propositions (countywide), Bothell
Prop 1 and Everett Props 261 to 265 (`CITY`), Monroe 103, Mukilteo 6 and
Sultan 311 (`SCHDST`), Fire District 10 (`FIRDST`), South Snohomish County
Fire & Rescue RFA Prop 1 (`RFADST` `SCRFA`) and Public Hospital District 1
(`HOSPDST`). All 17 are researched; seven (County Props 3 and 4, Everett
261 to 265) map to no rubric axis, so they ship with empty
`lean_mappings`.

## District scoping

- `RFADST`: the county's fire layer (`FIRDST`, `Fire_Districts_and_RFAs…
  /FeatureServer/1`) has no RFA polygons. `geo.js` reads WA DOR FIR2025
  (`WADOR_PropertyTax/MapServer/7`) `DISTATTRIB` with
  `where DISTATTRIB = 'SCRFA'`; that layer also carries fire-district
  numbers and other RFAs (`SRF`, `NCRFA`, `MARFA`). Live 2026-10-08,
  unfiltered: 19100 44th Ave W, Lynnwood `SCRFA`; 806 W Main St, Monroe
  `SRF`; 2930 Wetmore Ave, Everett no feature. Filtered: Lynnwood `SCRFA`,
  Monroe none.
- `DISTCRT`: Snohomish County District Court elects judges by electoral
  district. No county or DOR GIS layer publishes those boundaries, so the
  nine seats are hidden and voters see the partial-coverage notice.
  `snohomish/DISTCRT` is in `UNRESOLVABLE_SCOPES`
  (`app/src/lib/data-consistency.test.js`).

## Known gaps

- District Court seats (above) never appear on a Snohomish ballot.
- The VoteWA pointer meta (`raw/votewa/candidate-list.csv.meta.json`)
  predates `sha256_case_normalized`, so a fresh export (whose District
  columns differ in case) fails the builder's check until the meta is
  re-written with `fetch_votewa_candidate_list.py --write-pointer
  snohomish` from a cache that matches its `sha256` (the case-normalized
  digest of that export is
  `7580eaf60d6e46174d60fe45f851022e36c8616d601f14b7880a650ccdce993b`).
- PUD No. 1 also serves Camano Island (Island County); this package scopes
  the race to Snohomish County only.
