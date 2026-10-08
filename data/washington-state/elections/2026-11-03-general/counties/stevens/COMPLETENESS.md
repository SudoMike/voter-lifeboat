# Stevens County Completeness Note

Election: 2026 Washington general election, November 3, 2026 (VoteWA
election 899, county code 33).

Research package for #30 (county wave 5). Not yet declared in
`APP_PACKAGES["2026-11-03-general"]["counties"]`. Contests and measures are
built by `pipeline/build_votewa_lite_data.py --county stevens` from the
VoteWA candidate list (`raw/votewa/candidate-list.csv.url`) and the
overrides and measures in that script's
`ELECTION_MEASURES["2026-11-03-general"]["stevens"]`. Stevens County's own
site (`stevenscountywa.gov`) answered 403 to every scripted request
(2026-10-08), so no county sample ballot or pamphlet was fetched; the
contests and measures were checked against VoteWA's online voters' guide for
the county (`https://voter.votewa.gov/genericvoterguide.aspx?e=899&c=33`;
records under `raw/votewa/voter-guide/`, text in
`interim/voter-guide-text/`), which lists the same 16 non-Supreme-Court
races as the candidate list and four local measures. Stevens publishes no
printed general pamphlet that could be fetched; its records cite the VoteWA
guide, so the app would link it through `officialLinks.js` `countyGuides`
(as for Spokane, Lewis and Grant).

The builder reports `full_county`.

## What is on the ballot

16 contests (7 contested, 9 uncontested) and 4 local measures. The five
Supreme Court contests and the three statewide initiatives are dropped by
the builder and ship from the statewide package.

| Kind | Contests | Contested | Uncontested | Scope | Researched |
|---|---|---|---|---|---|
| U.S. Representative (CD 5) | 1 | 1 | 0 | `CONGDST` `5` | Spokane package |
| LD 7 State Senator | 1 | 1 | 0 | `LEGDST` `7` | Spokane package |
| LD 7 Representative Pos. 1, Pos. 2 | 2 | 0 | 2 | `LEGDST` `7` | Spokane package (info-only) |
| Auditor, Coroner | 2 | 2 | 0 | `COUNTY` | here |
| Commissioner District 2 (elected county-wide) | 1 | 1 | 0 | `COUNTY` | here |
| District Court Judge | 1 | 1 | 0 | `COUNTY` | here (judicial axes) |
| PUD No. 1 Commissioner District 2 | 1 | 1 | 0 | `COUNTY` | Spokane package (no applicable axis) |
| Assessor, Clerk, Prosecuting Attorney, Sheriff, Treasurer | 5 | 0 | 5 | `COUNTY` | here (info-only) |
| Superior Court (Ferry, Pend Oreille, Stevens) Pos. 2, unexpired | 1 | 0 | 1 | `COUNTY` | here (info-only) |
| Court of Appeals Div. III Dist. 1 Pos. 2 | 1 | 0 | 1 | `COUNTY` | here (info-only county copy) |

The research plan names CD 5, LD 7 Senate and the PUD seat `researched_in`
spokane, with no `candidates_missing`. LD 7 Pos. 1 (Andrew Engell) and Pos. 2
(Hunter Abell) are uncontested, so the plan does not list them; Spokane's
package has information-only scoring files for both, and assembly ships
Stevens's two contests with them (`researched_elsewhere` by
`shared_contests.contest_key`). No Stevens copy was written, so each race is
researched once. The PUD contest is named exactly as Spokane names it
(`Public Utility District No. 1 of Stevens County Commissioner District 2`,
office `PUD Commissioner`) so the shared-race key matches.

Measures (VoteWA guide records 7251, 7323, 7330, 7331):

- Stevens County Rural Library District Proposition No. 2, levy lid lift
  ($0.27 to $0.44 per $1,000 for 2027): `LIBDST` `L`.
- Stevens County Fire Protection District No. 10 Proposition No. 1, levy
  ($0.54 to $0.75 per $1,000 for 2027): `FIRDST` `10`.
- Nine Mile Falls School District No. 325-179 Propositions No. 1
  (replacement EP&O levy, est. $2.10) and No. 2 (capital levy, est. $0.38):
  `SCHDST` `179J`. The district is administered by Spokane County; the
  Spokane package has its own copies of both.

## District scoping

- Commissioner District 2: Stevens is a non-charter county under 400,000,
  so commissioners are nominated by district (RCW 36.32.040) and elected by
  the voters of the whole county (RCW 36.32.050(1);
  `raw/statutes/rcw-36.32.050.html.url`). VoteWA's general export lists the
  race as `Countywide`, and in the SOS 2020-11-03 precinct export the
  Commissioner #1 and #3 races appear on all 58 Stevens precincts
  (`raw/stevens/sos-results-20201103-stevens-precincts.csv.url`). Scope
  `COUNTY`; the override keeps the primary's contest name, so its slug
  (`stevens-stevens-county-commissioner-district-2-commissioner-2`) matches
  the primary.
- District Court: one county-wide court; override names it `Stevens County
  District Court`, category `Judicial`.
- PUD No. 1 of Stevens County: WA DOR PUD2025 (layer 17) has one Stevens
  polygon, `DISTATTRIB` `1`, whose area equals the sum of the county's
  SCH2025 polygons (14,831.2 in the service's units), i.e. the whole county;
  `1` at Colville, Chewelah, Kettle Falls, Northport, Springdale, Suncrest
  and Loon Lake. The whole PUD elects each commissioner in the general (RCW
  54.12.010(3)), and the 2020 PUD Commissioner #2 race was on all 58
  precincts. Scope `COUNTY` (it also has a small Spokane County territory,
  which Spokane's package scopes `PUDDST`, unresolvable).
- Library district: not county-wide. DOR LIB2025 (layer 12) `DISTATTRIB`
  `L` covers the county except the Cities of Colville and Kettle Falls
  (no feature at 215 S Oak St, Colville and 605 Meyers St, Kettle Falls),
  and the district's 2014 levy was on every precinct except COLVILLE 1-7
  and KETTLE FALLS 1-2 (`raw/stevens/sos-results-20141104-stevens-precincts.csv.url`).
  A city annexation after DOR's 2025 tax year would be missed.
- Fire District 10: the Aladdin Road/Spirit area northeast of Colville.
- Nine Mile Falls SD: DOR SCH2025 `179J` is the Stevens side (the county's
  School Districts layer reads `Nine Mile Falls SD 179` at the same point).

### Layers the District Adapter needs

`app/src/lib/geo.js` `COUNTY_LAYERS.stevens` currently reads
`COUNTY_COUNCIL` (county `AdministrativeBoundaries/MapServer/5`,
`districtid`; no general contest uses it) and `FIRDST` (DOR 7). The general
needs two more, both DOR (as Lewis and Island read LIB2025, Benton and
Skagit SCH2025):

| Key | URL | Attr | Used by |
|---|---|---|---|
| `FIRDST` (present) | `${DOR_TAX_DISTRICTS}/7/query` | `DISTATTRIB` | FD 10 Prop. 1 (`10`) |
| `LIBDST` (add) | `${DOR_TAX_DISTRICTS}/12/query` | `DISTATTRIB` | Library Prop. 2 (`L`) |
| `SCHDST` (add) | `${DOR_TAX_DISTRICTS}/20/query` | `DISTATTRIB` | Nine Mile Falls Props. 1 and 2 (`179J`) |

Point queries, 2026-10-08 (Census geocoder, Current vintage; DOR
`WADOR_PropertyTax/MapServer`, layers 7 / 12 / 20 / 17):

| Address | Census place | FIR2025 | LIB2025 | SCH2025 | PUD2025 |
|---|---|---|---|---|---|
| 215 S Oak St, Colville | Colville city | none | none | `115` | `1` |
| 301 E Clay Ave, Chewelah | Chewelah city | none | `L` | `36` | `1` |
| 605 Meyers St, Kettle Falls | Kettle Falls city | none | none | `212` | `1` |
| 3998 State Hwy 292, Loon Lake | Loon Lake CDP | `1` | `L` | `183J` | `1` |
| 6015 State Route 291, Nine Mile Falls | Suncrest CDP | `1` | `L` | `179J` | `1` |
| 2785 Aladdin Rd, Colville | none | `10` | `L` | `211` | `1` |

All six are LD 7 (Census). Suggested live checks: 6015 State Route 291,
Nine Mile Falls (library and both Nine Mile Falls measures), 2785 Aladdin
Rd, Colville (library and FD 10), 215 S Oak St, Colville (no local measure).

## Sources

VoteWA guide records; SOS results exports (2010, 2014, 2018, 2020, 2022) and
VoteWA results API (April 28 and August 4, 2026) under `raw/stevens/`; PDC
summary (`raw/stevens/pdc-stevens-2026.json.url`); Statesman-Examiner
(Colville) stories under `raw/news/` (its Wix search is client-side, so
stories were found through its article sitemap); Spokesman-Review stories
(found through its monthly story sitemaps); campaign sites; RCW pointers
under `raw/statutes/`. The Chewelah Independent was not reached.

## Known gaps

- No county sample ballot or local pamphlet could be fetched (403).
- C. Olivia Irwin (District Court) submitted no guide statement; her
  dossier rests on one forum report. Jack Griffin Jr. and Rick Johnson have
  little beyond the guide; Burrows's listed campaign domain is parked.
- FD 10 Prop. 1 has only the voters' guide record (no news coverage found).
- The Statesman-Examiner pages show no publication date for most stories;
  dates are given from their content (e.g. the July 7 ruling).
- The primary's Stevens dossiers had thin or mismatched citations (Simpson's
  cited Larsen's site); nothing was carried forward unverified.
