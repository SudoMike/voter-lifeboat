# Grays Harbor County Completeness Note

Election: 2026 Washington general election, November 3, 2026 (VoteWA
election 899, county code 14).

Status (#29): researched, scored and refuted; **not yet declared** in
`APP_PACKAGES["2026-11-03-general"]["counties"]` (the director ships). The
builder (`pipeline/build_votewa_lite_data.py --county grays-harbor`) writes
`interim/app-contests.json` and `interim/app-measures.json` with `coverage:
"full_county"`, but two measure scopes use layers that `app/src/lib/geo.js`
`COUNTY_LAYERS['grays-harbor']` does not list yet (`LIBDST`, `SCHDST`; see
District scoping). Until they are added the assembler would ship the county
`partial_county`.

## Sources

- Candidate list: VoteWA GENERAL 2026 export
  (`raw/votewa/candidate-list.csv.{url,meta.json}`, 39 rows; Supreme Court
  rows dropped by the builder).
- Candidate statements and measure records: VoteWA's online voters' guide
  for Grays Harbor County (`https://voter.votewa.gov/genericvoterguide.aspx?e=899&c=14`),
  records under `raw/votewa/voter-guide/` (`voterguide.json`,
  `race-<RaceID>.json`, `measure-<id>.json`), text in
  `interim/voter-guide-text/`. The dossiers cite these unpaged records, so
  the app should link the county's VoteWA guide (`officialLinks.js`
  `countyGuides['grays-harbor']`), as for Grant and Spokane.
- Grays Harbor County Auditor: the Current Election page
  (`raw/grays-harbor/current-election.html`; still showing the primary's
  results link on 2026-10-08) links VoteWA as the voters' pamphlet and a
  **supplemental pamphlet for the District Court judges**
  (`raw/grays-harbor/district-court-judges-pamphlet.pdf.url`, text in
  `interim/pdf-text/`). That PDF is "page 14", which "was inadvertently left
  out of your voter guide", so the county mails a printed local guide, but
  it is not posted online and no sample ballot PDF is posted either. The
  ballot here is checked against VoteWA's guide index, which lists exactly
  the export's races plus five local measures.
- SOS election results used for electorate checks:
  `raw/sos/results-20241105-grays-harbor.html`, `results-20221108-grays-harbor.html`.
- SOS voters' pamphlet Edition 08 (Grays Harbor, Lewis, Pacific,
  Wahkiakum) carries the federal and legislative statements only; it has no
  Grays Harbor local section.

## What ships

17 contests (12 contested, 5 uncontested) and 5 local measures. The
Supreme Court contests are dropped by the builder and ship from the
statewide package.

| Contest | Candidates | Status | Research |
|---|---|---|---|
| U.S. Representative, CD 6 | Randall, Fox | contested | Pierce's package (#21) |
| LD 19 Representative Pos. 1 | Walsh, Moynihan | contested | Thurston's package (#22) |
| LD 19 Representative Pos. 2 | Carlson, McEntire | contested | Thurston's package (#22) |
| LD 24 Representative Pos. 1 | Bernbaum, Pratt | contested | **not here**: assigned to Clallam (in progress, not on main) |
| LD 24 Representative Pos. 2 | Kelbon, Kuehn | contested | **not here**: assigned to Clallam |
| Assessor | Lindgren, Nuxoll | contested | Grays Harbor |
| Auditor (open seat) | Paull, Joyce | contested | Grays Harbor |
| Commissioner District 3 | Sturgeon, Streifel | contested | Grays Harbor |
| Prosecutor | Walker, Crawford | contested | Grays Harbor |
| Sheriff | Wallace, Welter | contested | Grays Harbor |
| Treasurer | Hill, Cormier | contested | Grays Harbor |
| District Court Pos. 2 | Valentine, Mistachkin | contested | Grays Harbor |
| Clerk | Foster | uncontested | Grays Harbor, info-only |
| Coroner | Kelley | uncontested | Grays Harbor, info-only |
| District Court Pos. 1 | Vingo | uncontested | Grays Harbor, info-only |
| Court of Appeals Div. 2, Dist. 2, Pos. 1 | Price | uncontested | Grays Harbor, info-only (county-scoped copy; Thurston and Kitsap ship their own) |
| PUD No. 1 Commissioner District 3 | Martin | uncontested | Grays Harbor, info-only |

No Superior Court, port or hospital-district seat is on Grays Harbor's
general ballot (none is in the export or the guide index). LD 35 does not
appear in Grays Harbor's export.

`build_research_plan.py grays-harbor` shows CD 6 and LD 19 Pos. 1 and 2
`researched_in` Pierce and Thurston with no candidates missing. LD 24 Pos. 1
and 2 show as "to research here" (the Clallam research is not on main yet):
`verify_dossiers.py` reports them as the two `untouched_contests`. Once the
Clallam branch merges, the plan should show them `researched_in` Clallam.

Measures (all five researched, scored and refuted):

| Measure | Scope |
|---|---|
| Timberland Regional Library District Prop. 1 (levy lid lift to $0.35) | `LIBDST` `L` |
| City of Montesano Prop. 1 (levy lid lift to $3.22) | `CITY` `Montesano` |
| McCleary School District No. 65 Prop. 1 ($12.8M bonds) | `SCHDST` `65` |
| Grays Harbor County Fire Protection District No. 1 Prop. 1 (permanent EMS levy) | `FIRDST` `1` |
| Grays Harbor County Fire Protection District No. 2 Prop. 1 (two-year lid lift to $1.50) | `FIRDST` `2` |

## Builder overrides

The Grays Harbor block in `ELECTION_MEASURES` carries an `overrides` dict,
keyed by upper-cased (District, Race):

- `County` / `Commissioner #3` (District Type Countywide): kept as the
  primary's contest (`Grays Harbor County Commissioner District 3`,
  `Commissioner #3`), so the slug matches and primary dossiers carry
  forward. Scope `COUNTY`: nominated by district, elected county-wide in the
  general (RCW 36.32.040; the 2024 Commissioner #1 race drew 36,166 votes of
  38,102 ballots).
- `County` / `District Court #1`, `#2`: category Judicial, `Grays Harbor
  County District Court`, `Judge Position No. N`, scope `COUNTY` (one
  county-wide court; 2022 District Court #1 drew 24,257 votes of 29,916
  ballots).
- `PUD District` / `PUD Comm (3)`: `Public Utility District No. 1 of Grays
  Harbor County`, `Commissioner District 3`, scope `COUNTY`. The generic
  rule made it `PUDDST` `3` (unresolvable). The PUD covers the county (DOR
  PUD2025 layer 17 has one Grays Harbor polygon, `DISTATTRIB` `1`, at
  Aberdeen, Hoquiam, Montesano, McCleary, Ocean Shores and Westport) and the
  whole PUD elects each commissioner (RCW 54.12.010(3)); the 2022
  uncontested PUD Comm (2) drew 18,505 votes, as many as the county-wide
  uncontested District Court #2 (18,521).

`COUNTY_CONFIG['grays-harbor']` (primary geography) is unchanged.

## District scoping

`COUNTY_LAYERS['grays-harbor']` in `geo.js` lists only `FIRDST` (DOR
FIR2025, layer 7, `DISTATTRIB`); it answers live. Point queries, 2026-10-08
(Census geocoder, Current vintage; DOR `WADOR_PropertyTax/MapServer`, tax
year 2025):

| Scope | Layer | Address | Result |
|---|---|---|---|
| `CITY` `Montesano` | Census places | 112 N Main St, Montesano | `Montesano city` |
| `FIRDST` `1` | DOR FIR2025 (7), in `COUNTY_LAYERS` | 110 Main St, Oakville | `1` |
| `FIRDST` `2` | DOR FIR2025 (7), in `COUNTY_LAYERS` | 500 Wynoochee Valley Rd, Montesano | `2` |
| `SCHDST` `65` | DOR SCH2025 (20), **not** in `COUNTY_LAYERS` | 100 S 3rd St, McCleary | `65` |
| `LIBDST` `L` | DOR LIB2025 (12), **not** in `COUNTY_LAYERS` | 200 W Market St, Aberdeen; 609 8th St, Hoquiam; 112 N Main St, Montesano; 100 S 3rd St, McCleary; 506 S Montesano St, Westport | `L` |
| (outside TRL) | DOR LIB2025 (12) | 585 Point Brown Ave NW, Ocean Shores | no feature |
| PUD county-wide | DOR PUD2025 (17) | the six addresses above | `1` everywhere |
| Port (none on ballot) | DOR PRT2025 (16) | same | `GRAYS HARBOR` everywhere (one port district) |

Proposal for the director: add to `COUNTY_LAYERS['grays-harbor']` (and
`election.DISTRICT_ADAPTER_LAYERS["grays-harbor"]`)
`{ key: 'LIBDST', url: `${DOR_TAX_DISTRICTS}/12/query`, attr: 'DISTATTRIB' }`
(Island uses the same) and
`{ key: 'SCHDST', url: `${DOR_TAX_DISTRICTS}/20/query`, attr: 'DISTATTRIB' }`
(Benton uses the same). The TRL levy cannot be scoped `COUNTY`: Ocean
Shores runs its own library and is outside the district (the library's
Grays Harbor assessed value equals the county's minus Ocean Shores; see the
measure dossier). DOR HSP2025 has two Grays Harbor hospital districts (`1`,
`2`) but no hospital measure or seat is on this ballot. No `COUNTY_COUNCIL`
layer is needed: the commissioner race is county-wide.

## Known gaps

- The Daily World ran written Q&As (Oct. 7) for the sheriff, auditor,
  treasurer, District Court #2 and LD 24 races, but none for the assessor,
  prosecutor or commissioner races as of 2026-10-08.
- Price (Court of Appeals) is `pamphlet-only`.
- Nuxoll (assessor) has no endorsements and minimal PDC activity; Streifel
  (commissioner) has a short record as the appointee since May 16, 2026.
- The county's printed local voters' guide and sample ballot are not posted
  online; scopes were checked against VoteWA and GIS instead.
- Measures: the assessor's 2026 levy book was read by OCR (rates for
  cities, schools and fire districts checked against page images; the
  library's Grays Harbor rate line was not). Montesano's adopted Ordinance
  No. 1679 is not posted; Fire District 1's Resolution 2026-005/006 is not
  posted; no Grays Harbor-registered PDC committee for any measure.
