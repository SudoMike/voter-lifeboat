# Mason County Completeness Note

Election: 2026 Washington general election, November 3, 2026 (VoteWA
election 899, county code 23).

Research package for #30 (county wave 5), not yet shipped. Contests and
measures are built by `pipeline/build_votewa_lite_data.py --county mason`
from the VoteWA candidate list (`raw/votewa/candidate-list.csv.url`) and the
overrides and measures in that script's
`ELECTION_MEASURES["2026-11-03-general"]["mason"]`, checked against the
Mason County Auditor's Local Voters' Pamphlet
(`raw/mason/local-voters-pamphlet.pdf.url`, text in
`interim/pdf-text/local-voters-pamphlet.txt`; the pamphlet "contains all
races and measures throughout Mason County") and VoteWA's online voters'
guide for the county (`https://voter.votewa.gov/genericvoterguide.aspx?e=899&c=23`,
linked as "Mason County Voter Guide Portal" from
`https://www.masoncountywa.gov/departments/auditor/elections/current_election.php`;
records under `raw/votewa/voter-guide/`, text in `interim/voter-guide-text/`).
The sample ballot (`raw/mason/sample-ballot.pdf.url`) is vector artwork with
no extractable text and could not be rasterized here (no poppler or
Ghostscript), so it was not machine-checked; the pamphlet and the guide
agree contest for contest.

The builder reports `full_county`. The assembler will mark the county
`partial_county` until `COUNTY_LAYERS.mason` reads the two layers proposed
below (`PUDDST`, `SCHDST`).

## What is on the ballot

16 contests (9 contested, 7 uncontested) and 5 local measures. The five
Supreme Court contests and the three statewide initiatives are dropped by
the builder and ship from the statewide package.

| Kind | Contests | Contested | Uncontested | Scope | Researched |
|---|---|---|---|---|---|
| U.S. Representative (CD 6) | 1 | 1 | 0 | `CONGDST` | Pierce package |
| LD 35 Senator, Rep. Pos. 1, Pos. 2 | 3 | 3 | 0 | `LEGDST` | Kitsap package |
| Auditor, Clerk, Treasurer | 3 | 3 | 0 | `COUNTY` | here |
| County Commissioner District 3 | 1 | 1 | 0 | `COUNTY` | here |
| Assessor, Coroner, Prosecutor, Sheriff | 4 | 0 | 4 | `COUNTY` | here (info-only) |
| District Court Judge | 1 | 0 | 1 | `COUNTY` | here (info-only) |
| Court of Appeals Div. II, Dist. 2, Pos. 1 | 1 | 0 | 1 | `COUNTY` | Kitsap package (info-only) |
| PUD No. 1 Commissioner District 2 | 1 | 0 | 1 | `PUDDST` `1` | here (info-only) |
| PUD No. 3 Commissioner District 2 | 1 | 1 | 0 | `PUDDST` `3` | here (no applicable axis) |

All of Mason County is in LD 35 and CD 6; no LD 24 race is on the Mason
list. No Superior Court, port or hospital district seat is on the 2026
general ballot.

Measures (VoteWA guide records 7284, 7383, 7385, 7382, 7384; pamphlet pp.
24-30):

- Timberland Regional Library District Proposition No. 1, levy lid lift
  ($0.22 to $0.35 per $1,000 for 2027 and 2028): `COUNTY`.
- Southside School District No. 42 Proposition No. 1, replacement EP&O
  levy (2027-2030): `SCHDST` `42`.
- McCleary School District No. 65 Proposition No. 1, $12.8 million bonds:
  `SCHDST` `65` (the district is mostly in Grays Harbor County).
- Pioneer School District No. 402 Proposition No. 1, replacement EP&O levy
  (2028-2031): `SCHDST` `402`.
- City of Shelton Proposition No. 1, Transportation Benefit District sales
  tax from 0.2% to 0.3% for ten years: `CITY` `Shelton`.

## District scoping

- Commissioner District 3: nominated by district in the primary, elected
  county-wide in the general (RCW 36.32.040). VoteWA's general export lists
  it as `Countywide` / `County`. In the SOS precinct exports the 2020 and
  2024 District 1 and 2 races and the 2022 District 3 race are on every
  precinct the statewide races are on (`raw/mason/sos-results-*.csv.url`),
  and the Shelton-Mason County Journal's primary story says "voters
  countywide will vote for county commissioner in November". Scope `COUNTY`;
  the override keeps the primary's contest name, so its slug
  (`mason-mason-county-commissioner-district-3-county-commissioner-district-no-3`)
  and primary dossiers carry forward. The Mason commissioner layer in
  `COUNTY_LAYERS.mason` is not used by any general contest.
- District Court: one county-wide judge (2022 SOS export: every precinct).
  Override names it `Mason County District Court`, category `Judicial`.
- PUD No. 1 (Hood Canal / Hoodsport, 42.2 sq mi in DOR PUD2025) and PUD
  No. 3 (the rest of the county, 1,002.7 sq mi) split the county; their
  areas sum to the county's 1,044.9 sq mi (the sum of Mason's SCH2025
  polygons). Each PUD's commissioners are elected PUD-wide in the general
  (RCW 54.12.010(3)); in the SOS exports PUD 1's races are on 6-7 precincts
  and PUD 3's on 42-55. Scopes `PUDDST` `1` and `PUDDST` `3` through builder
  overrides (names `Public Utility District No. 1 of Mason County` /
  `No. 3`, so no other package's PUD seat matches the `NAMED` key).
  Proposed layer, point-queried 2026-10-09: WA DOR PUD2025, layer 17,
  `DISTATTRIB`: 24151 N US Hwy 101, Hoodsport -> `1`; 525 W Cota St,
  Shelton -> `3`; 23850 NE State Route 3, Belfair -> `3`.
  `{ key: 'PUDDST', url: `${DOR_TAX_DISTRICTS}/17/query`, attr: 'DISTATTRIB' }`
- School measures: WA DOR SCH2025, layer 20, `DISTATTRIB`: 161 SE Collier
  Rd, Shelton -> `42`; 112 E Spencer Lake Rd, Shelton -> `402`; interior
  point (-123.2614, 47.0894) -> `65` (Census: McCleary School District,
  Mason County). Proposed:
  `{ key: 'SCHDST', url: `${DOR_TAX_DISTRICTS}/20/query`, attr: 'DISTATTRIB' }`
- Timberland Regional Library: DOR LIB2025 (layer 12) has one Mason polygon
  (`L`), 1,044.9 sq mi, the whole county; the whole five-county district
  votes. Scope `COUNTY` (as Thurston's copy).
- City of Shelton: the TBD's tax applies to sales within the city (its
  board is the City Council). Census place `Shelton` at 525 W Cota St.

`app/src/lib/geo.js` `COUNTY_LAYERS.mason`: `COUNTY_COUNCIL`
(`gis.masoncountywa.gov/arcgis/rest/services/MasonCoSite/Districts/MapServer/1`,
`DIST_ID`; answered 2026-10-09: Shelton `3`, Belfair `1`, Hoodsport `2`)
and `FIRDST` (DOR layer 7; answered: Belfair `NMRFA`, Hoodsport `18`, no
feature at 525 W Cota St, Shelton). Neither is used by a general contest
or measure. The general needs `PUDDST` and `SCHDST` added.

## Point checks (2026-10-09; not a live app ballot)

Assembly was not run (wave agents may not), so these are the expected
ballots from the layers above, not `live_ballot.mjs` output:

- 525 W Cota St, Shelton: CD 6, LD 35, City Shelton, `PUDDST` `3`, SCH
  `309` (Shelton SD, no measure): county races, PUD 3 seat, Timberland,
  Shelton TBD.
- 24151 N US Hwy 101, Hoodsport: `PUDDST` `1`, SCH `404` (Hood Canal SD, no
  measure): county races, PUD 1 seat, Timberland.
- 23850 NE State Route 3, Belfair: `PUDDST` `3`, SCH `403` (North Mason, no
  measure): county races, PUD 3 seat, Timberland.

## Sources

The county prints a local voters' pamphlet with page numbers; dossiers cite
it as `local-voters-pamphlet page N`, and the builder gives each measure its
pamphlet pages. Two-candidate pages print the second-named candidate's
statement first; every attribution was checked against the VoteWA guide
records. Local news is the Shelton-Mason County Journal (masoncounty.com):
its story sitemap lists every story; many stories are paywalled after the
lead, and only readable text was cited.

## Known gaps

- Commissioner District 3 is vacant since Sharon Trask's resignation
  (September 15, 2026); the appointment to year end was pending when
  researched. Write-in candidate Jackie Jewett is also campaigning.
- Randy Lewis (Treasurer), Mick Sprouffske (PUD 3) and Ronald S. Gold
  (PUD 1, no pamphlet statement) are pamphlet-only.
- Pioneer School District's site is script-rendered; its measure rests on
  the ballot title and explanatory statement. Shelton Resolution 1450-0726
  was not found online.
- The primary's Mason dossiers were thin; nothing from them was carried
  forward unverified.
