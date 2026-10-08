# Wahkiakum County Completeness Note

Election: 2026 Washington general election, November 3, 2026 (VoteWA
election 899, county code 35).

Status (#32): researched, scored and refuted; not yet shipped (not in
`APP_PACKAGES`). The builder reports `full_county`, but the Fire District 2
measure needs `FIRDST` added to `COUNTY_LAYERS.wahkiakum` (see District
scoping) before the county can ship at full coverage.

## Sources

- Candidate list: VoteWA GENERAL 2026 export
  (`raw/votewa/candidate-list.csv.{url,meta.json}`, 26 rows; the ten
  Supreme Court rows are dropped by the builder).
- Ballot: the Auditor's general sample ballot (`raw/wahkiakum/sample-ballot.pdf.url`,
  `co.wahkiakum.wa.us/DocumentCenter/View/3637`, linked from
  `co.wahkiakum.wa.us/419/Elections`), a two-page "Jurisdiction Wide"
  composite. It lists exactly the export's races plus two local measures.
- Wahkiakum prints no local voters' pamphlet. Its VoteWA online guide
  (`genericvoterguide.aspx?e=899&c=35`; index at `raw/votewa/voter-guide/guide.json.url`)
  carries only the statewide measures, CD 3, LD 19 and the Supreme Court: no
  county race, no candidate statement for a county office, no local measure.
  The county's Elections page still links the primary's guide (`e=898`). The
  county dossiers therefore cite no pamphlet pages; the app should link the
  county's VoteWA guide (`c=35`) for the federal and legislative races and
  otherwise the sample ballot or the elections page.
- Results: SOS summary pages for the 2020, 2022, 2024 and 2025 generals, SOS
  precinct exports for the 2022 primary and general and the 2024 primary and
  general, and the VoteWA results API for the August 2026 primary
  (`raw/sos/`).
- County pages (Assessor, Auditor, Treasurer, Clerk, Sheriff, District
  Court; `raw/wahkiakum/`), the Assessor's 2025 levy-rate sheet (a scan with
  no text layer, read visually), DOR's accredited-appraiser list
  (`raw/dor/`), PDC candidate registrations (`raw/pdc/`), RCW 36.27.020,
  36.32.040, 36.32.050, 54.12.010 and 84.52.069 (`raw/law/`).
- Local press: The Wahkiakum County Eagle (`theeagle.news`, WordPress REST
  search `wp-json/wp/v2/posts?search=`); pointers under `raw/news/`. Many
  Eagle articles are paywalled after the first paragraph; only text visible
  in the cached page is cited. Candidate letters to the editor are recorded
  as `candidate-statement`, tier 1.

## What ships

12 contests (4 contested, 8 uncontested) and 2 local measures.

| Contest | Candidates | Status | Research |
|---|---|---|---|
| U.S. Representative, CD 3 | Braun, Gluesenkamp Perez | contested | Clark's package |
| LD 19 Representative Pos. 1 | Walsh, Moynihan | contested | Thurston's package |
| LD 19 Representative Pos. 2 | Carlson, McEntire | contested | Thurston's package |
| Assessor | Jenkins, Moriarty | contested | Wahkiakum (carried from the primary, refreshed) |
| Auditor | Bergseng | uncontested | Wahkiakum, info-only |
| Clerk | Reddon | uncontested | Wahkiakum, info-only |
| Sheriff | Mason | uncontested | Wahkiakum, info-only |
| Treasurer (open) | Longtain | uncontested | Wahkiakum, info-only |
| Prosecuting Attorney | Bigelow | uncontested | Wahkiakum, info-only |
| Commissioner District 3 (#3, short and full term) | Letham | uncontested | Wahkiakum, info-only |
| District Court Judge | Heywood | uncontested | Wahkiakum, info-only |
| PUD No. 1 Commissioner #1 | Healy | uncontested | Wahkiakum, info-only |

`build_research_plan.py wahkiakum` shows CD 3 `researched_in` Clark and LD
19 Pos. 1 and 2 `researched_in` Thurston, each with `candidates_missing: []`.
No LD 19 Senate seat is on the ballot. No Court of Appeals seat: Division
II District 3 Position 2 was elected in 2022 and Position 1 in 2024 (SOS
precinct exports), and neither the export nor the sample ballot lists one.
No Superior Court seat (the Pacific/Wahkiakum court's Position 1 was
elected in 2024), and no port, fire, cemetery or school race is on the
general ballot.

Measures (researched, scored and refuted):

| Measure | Scope |
|---|---|
| Wahkiakum County: Countywide Emergency Medical Services Levy, replacement of existing levy (up to $0.40 for six years, Resolution No. 87-26) | `COUNTY` |
| Fire Protection District No. 2 (Skamokawa): Emergency Medical Services Levy, replacement of existing levy (up to $1.00 for ten years, Resolution #2026-01) | `FIRDST` `2` |

Neither measure has a proposition number on the sample ballot, so both
slugs end in `ballot-measure` (`m(..., None, ...)`).

## Builder overrides

The Wahkiakum block in `ELECTION_MEASURES["2026-11-03-general"]` carries an
`overrides` dict, keyed by upper-cased (District, Race):

- `County` / `COMMISSIONER #3` (District Type Countywide): kept as the
  primary's contest (`Wahkiakum County Commissioner District 3`,
  `Commissioner #3`), so the slug matches. Scope `COUNTY`: nominated by
  district (RCW 36.32.040), elected by the county (RCW 36.32.050(1)). The
  2022 District 3 primary ran in 4 of 11 precincts (Deep River, Grays
  River, Rosburg/Altoona, Skamokawa) and the 2022 general on all 11; the
  2024 District 1 and 2 primaries ran in 3 and 4 precincts and their
  generals on all 11; the 2026 District 3 primary reported 4 of 4 units.
  Without the override the generic rule names it `Wahkiakum County` /
  `Commissioner #3` (a different slug) with the same `COUNTY` scope.
- `PUBLIC UTILITY DISTRICT COUNTYWIDE` / `COMMISSIONER #1`: `Public Utility
  District No. 1 of Wahkiakum County`, `Commissioner #1`, scope `COUNTY`.
  The generic rule made it `PUDDST` `1` (unresolvable, `partial_county`).
  DOR PUD2025 (layer 17) has one Wahkiakum polygon, `DISTATTRIB` `1`, with
  `Shape_Area` 1,552,022,023, equal to the county's single EMS2025 polygon
  and to the sum of its two SCH2025 polygons (392,447,980 + 1,159,574,043);
  the 2022 #3 and 2024 #2 PUD races were on all 11 precincts (RCW
  54.12.010(3)). The name includes "of Wahkiakum County", so its shared-race
  key cannot match Island's `("public utility district 1", "commissioner
  district 1")`.
- `County` / `DISTRICT COURT JUDGE`: category Judicial, `Wahkiakum County
  District Court`, `District Court Judge`, scope `COUNTY` (one county-wide
  court; 2022 general on all 11 precincts).

`COUNTY_CONFIG.wahkiakum` (primary geography) is unchanged. The builder
prints `wahkiakum contests: 12 measures: 2 full_county`.

## District scoping

Point queries, 2026-10-08 (Census geocoder `Public_AR_Current` /
`Current_Current`; DOR `WADOR_PropertyTax/MapServer`, tax year 2025, layer
list unchanged: 3 CEM2025, 6 EMS2025, 7 FIR2025, 12 LIB2025, 16 PRT2025, 17
PUD2025, 20 SCH2025, 22 WAT2025; county commissioner layer
`services5.arcgis.com/SQaKrZ90pTH1GKNW/arcgis/rest/services/Commissioner_Districts1/FeatureServer/1`,
`District_Number`):

| Address | Census place | Comm. | FIR (7) | EMS (6) | PUD (17) | CEM (3) | PRT (16) | SCH (20) | LIB (12) |
|---|---|---|---|---|---|---|---|---|---|
| 64 Main St, Cathlamet | Cathlamet town | `2` | none | `1` | `1` | `1` | `1` | `200` | none |
| 6 Linquist Ln, Cathlamet | East Cathlamet CDP | `2` | `4` | `1` | `1` | `1` | `1` | `200` | none |
| 341 Risk Rd, Cathlamet | (none) | `2` | `4` | `1` | `1` | `1` | `1` | `200` | none |
| 25 Elochoman Valley Rd, Cathlamet | (none) | `2` | `4` | `1` | `1` | `1` | `1` | `200` | none |
| 222 E Sunny Sands Rd, Cathlamet (Puget Island) | Puget Island CDP | `1` | `1` | `1` | `1` | `1` | `2` | `200` | none |
| 79 W Birnie Slough Rd, Cathlamet (Puget Island) | Puget Island CDP | `1` | `1` | `1` | `1` | `1` | `2` | `200` | none |
| 1391 State Rte 4, Skamokawa | Skamokawa Valley CDP | `3` | `2` | `1` | `1` | `2` | `2` | `200` | none |
| 391 Middle Valley Rd, Skamokawa | Skamokawa Valley CDP | `3` | `2` | `1` | `1` | `2` | `2` | `200` | none |
| 4 Covered Bridge Rd, Grays River | Grays River CDP | `3` | `3` | `1` | `1` | none | `2` | `155` | none |
| 50 Rosburg School Rd, Rosburg | Rosburg CDP | `3` | `3` | `1` | `1` | none | `2` | `155` | none |
| 100 Altoona Pillar Rock Rd, Rosburg | Rosburg CDP | `3` | `3` | `1` | `1` | none | `2` | `155` | none |

All addresses are CD 3 and LD 19 in the Census geocoder. No Naselle-side
(Deep River) street address geocoded (`10 Deep River Rd, Naselle`, `200
Deep River Rd, Rosburg`: no match); Rosburg and Altoona are the westernmost
addresses checked, in the Naselle-Grays River Valley SD 155 part of the
county. DOR FIR2025's Wahkiakum features are `1`, `2`, `3`, `4` and a tiny
`/4B` polygon (737,951 sq ft); LIB2025 has no Wahkiakum polygon (Timberland
does not cover the county).

Scopes and the layers they need:

- `COUNTY` (every county office, Commissioner District 3, PUD No. 1,
  District Court, the county EMS levy): no layer.
- `CONGDST` `3`, `LEGDST` `19`: Census.
- `FIRDST` `2` (Fire District 2 EMS levy): DOR FIR2025 (layer 7),
  `DISTATTRIB`, **not** in `COUNTY_LAYERS.wahkiakum`. Proposal: add
  `{ key: 'FIRDST', url: `${DOR_TAX_DISTRICTS}/7/query`, attr: 'DISTATTRIB' }`
  to `COUNTY_LAYERS.wahkiakum` and `election.DISTRICT_ADAPTER_LAYERS["wahkiakum"]`
  (Pacific, Adams and Skagit read the same layer). Live: `2` at 1391 State
  Rte 4 and 391 Middle Valley Rd, Skamokawa; `3` at Grays River and
  Rosburg; `1` on Puget Island; `4` around Cathlamet; no feature in the
  Town of Cathlamet. Without it the measure is hidden and the county ships
  `partial_county` (`data-consistency.test.js` would need
  `wahkiakum/FIRDST` in `UNRESOLVABLE_SCOPES`).
- `COUNTY_COUNCIL`: the existing `COUNTY_LAYERS.wahkiakum` entry
  (`Commissioner_Districts1/FeatureServer/1`, `District_Number`) re-probed
  alive: `2` at Cathlamet, `1` on Puget Island, `3` at Skamokawa, Grays
  River and Rosburg. No general scope uses it (Commissioner District 3 is
  elected county-wide); only the archived primary's District 3 race does.

Suggested live checks: 64 Main St, Cathlamet, WA 98612 (county EMS levy
only, no fire measure); 1391 State Rte 4, Skamokawa, WA 98647 (county EMS
levy and Fire District 2 levy); 222 E Sunny Sands Rd, Cathlamet, WA 98612
(Puget Island: county levy only); 4 Covered Bridge Rd, Grays River, WA
98621 (county levy only). Each should show all twelve contests.

## Known gaps

- No local pamphlet, no candidate statements and no explanatory statements
  for or against either measure; no Eagle questionnaire for 2026 races as of
  2026-10-08. The Assessor dossiers rest on the candidates' own Eagle
  letters (2025 for Moriarty, May 2026 for Jenkins), DOR accreditation and
  election results. Moriarty's 2025 campaign site (`votemoriarty.com`) now
  serves unrelated content and is not cited.
- Fire District 2's measure is `pamphlet-only`. The ballot title calls it a
  replacement of an existing levy but gives no current rate; the 2025
  levy-rate sheet shows no separate Fire District 2 EMS rate. Its $1.00 cap
  and its sharing a ballot with the county EMS levy do not match RCW
  84.52.069 as published on leg.wa.gov (history through 2018: 50-cent cap,
  district levies limited where the county levies, no district EMS
  proposition on the same ballot as a county one). Resolution #2026-01 and
  Resolution No. 87-26 were not found online. The dossier records the
  discrepancy without resolving it; the director may want to ask the
  Auditor's office (360-795-3219).
- The District Court and PUD info-only dossiers are `pamphlet-only`: no
  statement, rating or coverage beyond results and the county page.
- Same-name check: a Mark Letham was elected Fire District 3 commissioner
  in 2025 (SOS); the dossier does not attribute it to the county
  commissioner, since no source ties the two.
