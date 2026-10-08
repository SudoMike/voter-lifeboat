# Lewis County Completeness Note

Election: 2026 Washington general election, November 3, 2026 (VoteWA
election 899, county code 21).

Not shipped: research package for #29 (county wave 4). Contests and measures
are built by `pipeline/build_votewa_lite_data.py --county lewis` from the
VoteWA candidate list (`raw/votewa/candidate-list.csv.url`) and the overrides
and measures in that script's `ELECTION_MEASURES["2026-11-03-general"]["lewis"]`,
checked against the Lewis County Auditor's general sample ballot
(`raw/lewis/sample-ballot.pdf.url`, text in `interim/pdf-text/sample-ballot.txt`)
and VoteWA's online voters' guide for the county
(`https://voter.votewa.gov/genericvoterguide.aspx?e=899&c=21`, linked from
`https://elections.lewiscountywa.gov/current-election/`; records under
`raw/votewa/voter-guide/`, text in `interim/voter-guide-text/`).

The builder reports `partial_county` (`UNRESOLVABLE: PUDDST`), and one
measure is scoped to `LIBDST`, which `COUNTY_LAYERS.lewis` does not read
either. Both layers exist (see District scoping); with them added the
package would be `full_county`.

## What is on the ballot

16 contests (10 contested, 6 uncontested) and 3 local measures, matching the
sample ballot. The five Supreme Court contests and the three statewide
initiatives are dropped by the builder and ship from the statewide package.

| Kind | Contests | Contested | Uncontested | Scope | Researched |
|---|---|---|---|---|---|
| U.S. Representative (CD 3) | 1 | 1 | 0 | `CONGDST` | Clark package |
| LD 19 Rep. Pos. 1, Pos. 2 | 2 | 2 | 0 | `LEGDST` | Thurston package |
| LD 20 Rep. Pos. 1, Pos. 2 | 2 | 2 | 0 | `LEGDST` | Clark package |
| Auditor, Coroner, Sheriff | 3 | 3 | 0 | `COUNTY` | here |
| Assessor, Clerk, Prosecuting Attorney, Treasurer | 4 | 0 | 4 | `COUNTY` | here (info-only) |
| County Commissioner District 3 | 1 | 1 | 0 | `COUNTY` | here |
| District Court Judge, Dept 1 and Dept 2 | 2 | 0 | 2 | `COUNTY` | here (info-only) |
| PUD No. 1 Commissioner District 1 (at large) | 1 | 1 | 0 | `PUDDST` `1` | here (no applicable axis) |

No LD 19 or LD 20 Senate seat is on the 2026 ballot. The plan names all five
shared races `researched_in` (Clark: CD 3, LD 20 Pos. 1 and 2; Thurston: LD
19 Pos. 1 and 2) with no `candidates_missing`.

Measures (VoteWA guide records 7284, 7365, 7366):

- Timberland Regional Library District Proposition No. 1, levy lid lift
  ($0.22 to $0.35 per $1,000 for 2027 and 2028): `LIBDST` `L`.
- Transportation Benefit District of Chehalis Proposition No. 1, renewal of
  the 0.2% sales and use tax for 2027-2037: `CITY` `Chehalis`.
- Lewis County Fire Protection District No. 6 Proposition No. 1, levy lid
  lift to $1.15 per $1,000: `FIRDST` `6`.

## District scoping

- Commissioner District 3: nominated by district in the primary, elected
  county-wide in the general (RCW 36.32.040). VoteWA's general export lists
  it as `Countywide` / `County`; in the SOS 2020-11-03 Lewis precinct export
  the District 1 and 2 races are on all 96 precincts
  (`raw/lewis/sos-results-20201103-lewis-precincts.csv.url`). Scope `COUNTY`;
  the override keeps the primary's contest name, so its slug
  (`lewis-lewis-county-commissioner-district-3-county-commissioner-district-3`)
  and primary dossiers carry forward.
- District Court Dept 1 and Dept 2: one county-wide district. Override names
  them `Lewis County District Court`, category `Judicial`.
- Lewis County PUD No. 1: commissioners are nominated by district and
  elected by the whole PUD (the ballot heading reads "Public Utility District
  1 At-Large"; RCW 54.12.010(3)). The PUD is not the whole county: the City
  of Centralia (Centralia City Light) is outside it. The PUD races of 2020,
  2022 and 2024 appear on every Lewis precinct except CENTRALIA #1-#13
  (`raw/lewis/sos-results-2020*`, `2022*`, `2024*`). Scope `PUDDST` `1`.
  Layers that resolve it, point-queried 2026-10-09:
  - WA DOR PUD2025, layer 17
    (`https://webgis.dor.wa.gov/arcgis/rest/services/Programs/WADOR_PropertyTax/MapServer/17`),
    `DISTATTRIB`: one Lewis polygon (`COUNTYNAME` `LEWIS`, `DISTATTRIB`
    `1`). 118 W Maple St, Centralia: no feature. 351 NW North St, Chehalis;
    13068 US Highway 12, Packwood; 200 S Main St, Pe Ell; Morton, Toledo,
    Winlock, Mossyrock, Napavine, Vader: `1`.
  - Lewis County `VotingTaxingDistricts/MapServer/8` ("PUD Commissioner
    Districts", `PUD_COMM` 1-3,
    `https://arcgis.lewiscountywa.gov/arcgispublic/rest/services/VotingTaxingDistricts/MapServer/8`):
    no feature at Centralia, `2` at Chehalis and Pe Ell. It agrees with DOR
    on the Centralia exclusion but carries commissioner districts, not a
    PUD-wide value.
  Proposal: `{ key: 'PUDDST', url: `${DOR_TAX_DISTRICTS}/17/query`, attr: 'DISTATTRIB' }`
  in `COUNTY_LAYERS.lewis`.
- Timberland Regional Library District: DOR LIB2025 (layer 12) `DISTATTRIB`
  `L` at Centralia, Chehalis, Morton, Toledo, Winlock and 2152 Jackson Hwy
  (unincorporated); no feature at Pe Ell (200 S Main St), Mossyrock (243 E
  State St), Napavine (105 2nd Ave NW) and Vader (509 A St). The district is
  not county-wide, so the measure is scoped `LIBDST` `L`. Proposal: `{ key:
  'LIBDST', url: `${DOR_TAX_DISTRICTS}/12/query`, attr: 'DISTATTRIB' }` (as
  Island County reads it). No Lewis County layer carries library districts.
  Until then the builder's coverage flag does not see it (measure scopes are
  not checked there), so the note in `app-measures.json` says so.
- Chehalis TBD: the City Council is its governing board (ballot title), so
  the electorate is the city: Census place `Chehalis` at 351 NW North St.
- Fire District 6: DOR FIR2025 (layer 7) `DISTATTRIB` `6` at 2152 Jackson
  Hwy, Chehalis; the county's Precinct Splits layer (12) reads `Lewis County
  FD #6` there. `COUNTY_LAYERS.lewis` already reads FIR2025.

`app/src/lib/geo.js` `COUNTY_LAYERS.lewis` today: `COUNTY_COUNCIL`
(VotingTaxingDistricts layer 0, `COMMISSION`) and `FIRDST` (DOR layer 7).
This package uses `FIRDST`; no general contest uses `COUNTY_COUNCIL`.

## Sources

Lewis County publishes its general voters' pamphlet only as VoteWA's online
guide. Its citations carry no page numbers, so the county's records would
ship no `pamphlet_pages`; the app would link the guide through
`officialLinks.js` `countyGuides` (as for Benton and Whatcom). Local news is
The Chronicle (chronline.com): its `/search/` page answers 403, but
`browse.html?search_filter=` works and story pages are readable; a few
stories are paywalled and were not cited.

## Known gaps

- The two District Court judges and Prosecuting Attorney Meyer submitted no
  guide statements; their info-only entries are pamphlet-only.
- Michael Hadaller's campaign site did not respond; his platform comes from
  The Chronicle's profile and forum coverage.
- Fire District 6: the explanatory statement puts the current rate at about
  $0.79 and the district's flyer at about $0.73; the ballot title cites
  Resolution No. 2026-2 and the Prosecuting Attorney's memo 2026-03.
- The primary's Lewis dossiers cited Facebook and hometowndebate.com or
  listed no sources; nothing from them was carried forward unverified.
