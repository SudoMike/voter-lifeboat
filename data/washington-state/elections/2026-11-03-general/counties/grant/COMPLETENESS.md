# Grant County Completeness Note

Election: 2026 Washington general election, November 3, 2026 (VoteWA
election 899, county code 13).

Shipped (#28): the package is declared in
`APP_PACKAGES["2026-11-03-general"]["counties"]` and ships at Full County
Coverage, with the elections office link
`https://www.grantcountywa.gov/270/Elections` and the county's VoteWA guide
(`officialLinks.js` `countyGuides.grant`). The builder
(`pipeline/build_votewa_lite_data.py --county grant`) writes
`interim/app-contests.json` and `interim/app-measures.json` with
`coverage: "full_county"`: every contest and measure scope is `CONGDST`,
`LEGDST`, `CITY`, `COUNTY` or a DOR layer in `app/src/lib/geo.js`
`COUNTY_LAYERS.grant` (`FIRDST` and `CEMDST` added at ship time, see District
scoping).

## Sources

- Candidate list: VoteWA GENERAL 2026 export (`raw/votewa/candidate-list.csv.{url,meta.json}`, 41 rows).
- Candidate statements and measure records: VoteWA's online voters' guide
  for Grant County (`https://voter.votewa.gov/genericvoterguide.aspx?e=899&c=13`),
  records under `raw/votewa/voter-guide/` (`race-<RaceID>.json`,
  `measure-<id>.json`, `voterguide.json`), text in
  `interim/voter-guide-text/`. Grant County prints no local voters'
  pamphlet; the dossiers cite these unpaged guide records, so no Grant
  record ships `pamphlet_pages`. The app should link the county's VoteWA
  guide (`officialLinks.js` `countyGuides.grant`) as for Spokane.
- Official sample ballot and filed measure resolutions: Grant County
  Elections' Current Election page (`https://www.grantcountywa.gov/1374/Current-Election`),
  pointers under `raw/grant/`, text in `interim/pdf-text/` (the four
  resolutions are scans with no text layer; the measures researcher OCR'd
  them for reading only).

## What ships

21 contests (10 contested, 11 uncontested) and 5 local measures. The
Supreme Court contests are dropped by the builder and ship from the
statewide package.

| Contest | Candidates | Status | Research |
|---|---|---|---|
| U.S. Representative, CD 4 | McKinney, Duresky | contested | Benton's package (#28) |
| LD 13 State Senator | Ybarra | uncontested | Grant, info-only |
| LD 13 Representative Pos. 1 | Dent, Garcia | contested | Grant |
| LD 13 Representative Pos. 2 | Martinez, Thompson | contested | Grant |
| LD 16 Representative Pos. 1 | Klicker, Palmer | contested | Benton's package (#28) |
| LD 16 Representative Pos. 2 | Rude, Sarley | contested | Benton's package (#28) |
| Assessor | Johnson, Bartrand | contested | Grant |
| Auditor (short and full term) | Falstad, Homesley | contested | Grant |
| Clerk | Allen | uncontested | Grant, info-only |
| Commissioner District 3 | Raap, Durfee | contested | Grant |
| Coroner | Morrison | uncontested | Grant, info-only |
| Prosecutor (short and full term) | Guernsey | uncontested | Grant, info-only |
| Sheriff | Gregg, Kriete | contested | Grant |
| Treasurer (short and full term) | Heston | uncontested | Grant, info-only |
| Court of Appeals Div. 3, Dist. 2, Pos. 1 | Hill | uncontested | Grant, info-only (county-scoped copy; Benton ships its own) |
| Superior Court Pos. 3 (unexpired) | Chadwick, Bevier | contested | Grant |
| District Court Pos. 1, 2, 3 | Middleton, Wallace, Gwinn | uncontested | Grant, info-only |
| Grant PUD Commissioner District 3 | Schaapman | uncontested | Grant, info-only |
| Grant PUD Commissioner District B (At Large) | Cox | uncontested | Grant, info-only |

After the #28 merges `build_research_plan.py grant` shows CD 4 and LD 16
Pos. 1 and 2 `researched_in` Benton with no candidates missing; they ship
with Benton's scoring and dossiers.

Measures (all five researched, scored and refuted):

| Measure | Scope |
|---|---|
| Grant County Advisory Vote Only Prop. 1 (0.1% behavioral health sales tax, RCW 82.14.460) | `COUNTY` |
| Grant County Public Hospital District No. 4 Prop. 1 ($9.94M McKay Healthcare bonds) | `HOSPDST` `4` |
| City of Moses Lake Prop. 1 (0.1% public safety sales tax) | `CITY` `Moses Lake` |
| Grant County Fire Protection District No. 7 Prop. 1 (EMS levy) | `FIRDST` `7` |
| Grant County Cemetery District No. 2 (Wilson Creek) Prop. 1 (M&O levy) | `CEMDST` `2` |

## Builder overrides

The generic VoteWA parser stops on Grant's PUD rows (District `Grant County
PUD All`, which carries no number). The Grant block in `ELECTION_MEASURES`
carries an `overrides` dict, keyed by upper-cased (District, Race):

- `Commissioner District #3` (District Type Countywide): kept as the
  primary's contest (`Grant County Commissioner District 3`), so the slug
  matches and primary dossiers carry forward. Scope `COUNTY`: nominated by
  district in the primary, elected county-wide in the general (RCW
  36.32.040); VoteWA files the general race as Countywide and the sample
  ballot lists it under County Partisan Offices.
- `District Court Judge #1`-`#3` (District Type Countywide): category
  Judicial, `Grant County District Court`, `Judge Position No. N`, scope
  `COUNTY` (one county-wide district court).
- Grant PUD `Commissioner Dist #3` and `Commissioner Dist #B AL`: Public
  Utility District No. 2 of Grant County, scope `COUNTY`. The PUD is
  county-wide (DOR PUD2025 layer 17 has one Grant polygon, `DISTATTRIB`
  `2`, at Moses Lake, Soap Lake, Coulee City, Grand Coulee and Wilson
  Creek) and its whole electorate elects every commissioner in the general
  (RCW 54.12.010(3)).

The override wiring in `config_for` / `county_docs` is the same few lines
Whatcom's branch added (#28), so the two merge trivially.

## District scoping

Point queries, 2026-10-08 (Census geocoder, Current vintage; DOR
`WADOR_PropertyTax/MapServer`, tax year 2025):

| Scope | Layer | Address | Result |
|---|---|---|---|
| `CITY` `Moses Lake` | Census places | 321 S Balsam St, Moses Lake | Moses Lake |
| `HOSPDST` `4` | DOR HSP2025 (11), in `COUNTY_LAYERS.grant` | 127 Main Ave E, Soap Lake | `4` |
| `FIRDST` `7` | DOR FIR2025 (7), **not** in `COUNTY_LAYERS.grant` | 34875 Park Lake Rd NE, Coulee City | `7` |
| `CEMDST` `2` | DOR CEM2025 (3), **not** in `COUNTY_LAYERS.grant` | 103 Railroad St, Wilson Creek | `2` |
| PUD county-wide | DOR PUD2025 (17) | five towns above | `2` everywhere |

At ship time (#28) `FIRDST` (`${DOR_TAX_DISTRICTS}/7`, `DISTATTRIB`) and
`CEMDST` (`${DOR_TAX_DISTRICTS}/3`, `DISTATTRIB`) were added to
`COUNTY_LAYERS.grant` and `election.DISTRICT_ADAPTER_LAYERS["grant"]`, each
re-verified by the same point queries; both layers already serve other
counties (Benton, Adams). `COUNTY_COUNCIL` (the county's commissioner layer)
stays in the adapter but no general scope uses it, since the commissioner
race is county-wide.

Live ballots on 2026-10-08 (`pipeline/live_ballot.mjs`, `full_county`,
`missing=[]`): 321 S Balsam St, Moses Lake (LD 13, advisory vote, Moses
Lake Prop 1); 127 Main Ave E, Soap Lake (Hospital District 4 bonds); 103
Railroad St, Wilson Creek (Hospital District 4, Cemetery District 2); 34875
Park Lake Rd NE, Coulee City (Hospital District 4, FD 7). The Coulee City
point lies inside DOR HSP2025 district 4, so it gets the McKay bonds too.

## Known gaps

- Thin evidence: District Court Pos. 1-3 are `pamphlet-only`; Juan "Jerry"
  Garcia's dossier rests on his statement, one Columbia Basin Herald Q&A and
  PDC; Anson Bartrand (a primary write-in who passed 1%) has no site or
  filings beyond PDC registration.
- Web search quota ran out during research; sources were found through
  outlet site searches, GCJ.news, PDC open data, leg.wa.gov web services
  and VoteWA. iFIBER One is paywalled; Columbia Basin Herald search
  rate-limited some queries.
- City of Moses Lake: the ballot title cites Resolution No. 4042, the
  filed copy is headed 4051. Not resolved.
- Some guide statements are stale (Chadwick's "unseat" the appointee, who
  lost in the primary; Falstad and Heston list pre-interim roles); the
  dossiers say so.
