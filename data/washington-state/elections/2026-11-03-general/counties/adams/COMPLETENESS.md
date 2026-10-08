# Adams County Completeness Note

Election: 2026 Washington general election, November 3, 2026 (VoteWA
election 899, county code 01).

Research package for #31 (county wave 6). Not yet declared in
`APP_PACKAGES["2026-11-03-general"]["counties"]`; the director ships it.

Contests and measures are built by
`pipeline/build_votewa_lite_data.py --election 2026-11-03-general --county adams`
from the VoteWA candidate list (`raw/votewa/candidate-list.csv.url`, 36 rows)
and the overrides and measures in that script's
`ELECTION_MEASURES["2026-11-03-general"]["adams"]`, checked against the Adams
County Auditor's general sample ballot (`raw/adams/sample-ballot.pdf.url`,
DocumentCenter 2684, text in `interim/pdf-text/sample-ballot.txt`) and
VoteWA's online voters' guide for the county
(`https://voter.votewa.gov/genericvoterguide.aspx?e=899&c=01`; records under
`raw/votewa/voter-guide/`, text in `interim/voter-guide-text/`). Both are
linked from the Auditor's Elections page
(`https://www.co.adams.wa.gov/162/Elections-Elecciones`,
`raw/adams/elections-page.html.url`). Adams County prints no local voters'
pamphlet; every candidate and measure record cites the VoteWA guide, so the
county's records ship no pamphlet pages and should link the guide
(`countyGuides.adams`, `c=01`).

Builder line: `adams contests: 17 measures: 2 full_county`. The builder
scopes are all `CONGDST`, `LEGDST`, `COUNTY`, `FIRDST` or `PARKDST`;
`FIRDST` is not in `COUNTY_LAYERS.adams` yet (below), so until it is added
the assembler would mark the county `partial_county`.

## What is on the ballot

17 contests (9 contested, 8 uncontested) and 2 local measures, matching the
sample ballot and the VoteWA guide. The five Supreme Court contests and the
three statewide initiatives are dropped by the builder and ship from the
statewide package.

| Kind | Contests | Contested | Scope | Researched |
|---|---|---|---|---|
| U.S. Representative CD 4, CD 5 | 2 | 2 | `CONGDST` `4`, `5` | Benton (CD 4), Spokane (CD 5) |
| LD 9 Rep. Pos. 2 | 1 | 1 | `LEGDST` `9` | Spokane |
| LD 9 Rep. Pos. 1 (Mary Dye) | 1 | 0 | `LEGDST` `9` | Spokane (info-only) |
| LD 13 Senator (Alex Ybarra) | 1 | 0 | `LEGDST` `13` | Grant (info-only) |
| LD 13 Rep. Pos. 1 and Pos. 2 | 2 | 2 | `LEGDST` `13` | Grant |
| Assessor, Auditor, Sheriff | 3 | 3 | `COUNTY` | here |
| County Commissioner District 3 | 1 | 1 | `COUNTY` | here |
| Clerk, Prosecutor, Treasurer | 3 | 0 | `COUNTY` | here (info-only) |
| District Court Judge Positions No. 1 and 2 | 2 | 0 | `COUNTY` | here (info-only) |
| Court of Appeals Div. III, Dist. 2, Pos. 1 | 1 | 0 | `COUNTY` | here (info-only county copy) |

The plan (`interim/research-plan.json`) names CD 4 -> Benton, CD 5, LD 9
Pos. 2 -> Spokane, LD 13 Pos. 1 and 2 -> Grant, each with no
`candidates_missing`. The uncontested LD 9 Pos. 1 and LD 13 Senate seats
match Spokane's and Grant's info-only scoring files by
`shared_contests.contest_key`; Adams keeps no copy of any shared race. No LD
9 Senate seat is on the 2026 ballot. Census places Othello (425 E Main St)
in CD 4 and LD 9, and Ritzville, Lind and Washtucna in CD 5 and LD 9; the
LD 13 part of the county is rural.

## District scoping

- **County Commissioner District 3.** VoteWA's general export lists it as
  `Countywide` / `County` / `County Commissioner District 3`. Adams is a
  non-charter county of about 20,700; RCW 36.32.040 nominates
  commissioners by district and RCW 36.32.050(1) has them "elected by the
  qualified voters of the county" (subsection (2), district-only elections,
  applies only to noncharter counties of 400,000 or more)
  (`raw/adams/rcw-36.32.040.html.url`, `rcw-36.32.050.html.url`). The 2026
  primary counted the race in 5 of 30 reporting units
  (`raw/adams/votewa-results-20260804.json.url`); the SOS general precinct
  exports put 'Adams County Commissioner District 3' (2022) in all 28
  precincts and Districts 1 and 2 (2024) in all 29, the same sets as the
  county-wide offices (`raw/adams/sos-results-20221108-adams-precincts.csv.url`,
  `...-20241105-...`). Scope `COUNTY`. The override keeps the primary's
  contest name, so the slug
  (`adams-adams-county-commissioner-district-3-county-commissioner-district-3`)
  matches the primary's and its dossiers carried forward. The archived
  primary scoped this race `COUNTY_COUNCIL` `3`, unresolvable (no
  commissioner-district layer); that does not matter in the general.
- **District Court Judge Positions No. 1 and 2.** One county-wide court
  (2022: both on all 28 precincts). The overrides rename VoteWA's `District
  Court Judge Position 1/2` to `Adams County District Court` / `Judge
  Position No. 1/2`, category `Judicial`.
- **Court of Appeals Division III, District 2** (Adams, Asotin, Benton,
  Columbia, Franklin, Garfield, Grant, Walla Walla, Whitman): the whole
  county; county-scoped information-only copy, as Benton, Grant and Whitman
  ship.
- **No PUD or port race.** DOR PUD2025 (layer 17) has no Adams polygon.

## Layers the scopes need

Point-checked 2026-10-08 (Census geocoder, `Public_AR_Current` benchmark,
`Current_Current` vintage; WA DOR
`https://webgis.dor.wa.gov/arcgis/rest/services/Programs/WADOR_PropertyTax/MapServer`,
tax year 2025, attribute `DISTATTRIB`; `MapServer?f=json` still lists 2025
as the newest group with the same layer ids).

`COUNTY_LAYERS.adams` in `app/src/lib/geo.js` reads `CEMDST` (DOR 3) and
`PARKDST` (DOR 14). Both re-probed alive (table). No general scope uses
`CEMDST`. One addition is needed, for the Fire District 4 levy:

```js
{ key: 'FIRDST', url: `${DOR_TAX_DISTRICTS}/7/query`, attr: 'DISTATTRIB' },
```

and `FIRDST` in `election.DISTRICT_ADAPTER_LAYERS["adams"]` next to
`CONGDST`, `LEGDST`, `CITY`, `CEMDST`, `PARKDST`. DOR FIR2025 has seven
Adams polygons, `DISTATTRIB` `1`-`7`; DOR's levy detail names No. 4 "Fire
Dist #4 Harder-McCall".

| Scope | Layer | Point | Result |
|---|---|---|---|
| `PARKDST` `2` (Washtucna Pool levy) | DOR 14 PKR2025 (already read) | 155 W Main St, Washtucna (geocodes as 155 N Main St) | `2` |
| `PARKDST` (other districts) | DOR 14 | 210 W Broadway Ave, Ritzville; 107 E 2nd St, Lind; 425 E Main St, Othello | `4`; `3`; `1` |
| `FIRDST` `4` (FD 4 levy) | DOR 7 FIR2025 (proposed) | interior points (-118.02, 47.15) and (-118.05, 47.10), east of Ritzville | `4` |
| `FIRDST` (outside FD 4) | DOR 7 | 1780 E Templin Rd, Ritzville | `1` |
| `FIRDST` (cities and towns) | DOR 7 | Ritzville, Lind, Washtucna and Othello addresses above | no feature |
| `CEMDST` (re-probe; unused) | DOR 3 CEM2025 (already read) | Washtucna; Lind; Othello | `1`; `3`; `2` (Ritzville: no feature) |
| `PUDDST` (none) | DOR 17 PUD2025 | whole county (`COUNTYNAME='ADAMS'` query) | no features |

FD 4's polygon spans roughly -118.09 to -117.96 W, 47.05 to 47.26 N; its
levies have been voted in the single precinct Ritzville Rural SE (SOS
exports 2022-2025), shown on the sample ballot as style "RITZVILLE RURAL
SE-1". No street address inside it geocoded with the Census geocoder in
the attempts made, so the check is an interior point.

Suggested live-check addresses (`node pipeline/live_ballot.mjs ...`):

- `425 E Main St, Othello, WA 99344`: CD 4, LD 9, `CITY` Othello; no local
  measure.
- `155 W Main St, Washtucna, WA 99371`: CD 5, LD 9, Park District 2 (pool
  levy).
- `210 W Broadway Ave, Ritzville, WA 99169`: CD 5, LD 9, `CITY` Ritzville;
  no local measure.
- interior point (-118.02, 47.15): Fire District 4 levy (after `FIRDST` is
  added).

An address in the LD 13 part of the county was not identified; the LD 13
races ship with Grant's research either way.

## Sources

Every county candidate has a VoteWA guide statement. Local news: The
Ritzville Adams County Journal (ritzvillejournal.com; stories found through
its `sitemap_stories1.xml`; most are paywalled, so only the visible lead is
cited, and the site rate-limits scripted fetches) and the Columbia Basin
Herald (columbiabasinherald.com, site search). The Othello Outlook's domain
(othellooutlook.com) no longer hosts the newspaper. PDC candidate records
come from data.wa.gov dataset 3h9x-7bvm (`raw/adams/pdc-adams-2026-candidates.json.url`).
Levy history comes from SOS precinct exports (November 2022-2025, August
2024 and 2025) and the VoteWA 2026 primary results; levy amounts from DOR's
levy detail for taxes due in 2024 and 2025 (`raw/measures/`).

## Research

- Sheriff (Wagner vs Carlson, a 2022 rematch), Assessor (incumbent
  Rodriguez vs Templin), Auditor (open seat; Laird vs Fannin) and
  Commissioner District 3 (Garza vs Brodahl): all eight candidates
  `moderate`. Primary dossiers carried forward and rewritten from the
  general's sources. Scores: experience for all eight; safety for Wagner;
  spending for Fannin, Garza and Brodahl; taxes for Brodahl. No `reform`
  score: nothing in the dossiers is about money or power in politics.
- Six uncontested contests ship information-only (`scoring/<slug>.json`
  with empty scores): Clerk, Prosecutor, Treasurer, District Court Positions
  1 and 2 (all `pamphlet-only`: the statement plus official results and
  PDC records), and Court of Appeals III-2 Pos. 1 (`moderate`).
- Two measures, both `moderate`, both mapped `taxes` +1 (yearly one-year
  special levies): Fire District 4's $11,000 pumper-equipment levy (approved
  every year 2022-2025 in a single precinct) and Park District 2's $85,000
  Washtucna Pool levy (57.4% yes in August 2026, short of 60%; a second
  try).

## Known gaps

- The Journal's 2022 profile says Wagner was "elected sheriff in 2016"; his
  2026 announcement and Q&A say sheriff since 2015. The dossier keeps both.
- The Journal's August 5 primary-night story calls Templin the incumbent
  Assessor; VoteWA statements, the Journal's own October Q&As and the 2022
  results show Rodriguez is. The dossier follows the official record.
- Templin's statement does not name the county or counties where he was
  deputy assessor.
- Whether the August 2025 Washtucna pool levy (73-34) produced a 2026 levy is
  not confirmed: DOR's levy detail for taxes due in 2026 is not yet out.
  DOR shows a $50,000 levy for 2024 and none for 2025.
- Most Journal stories are paywalled; claims rest on the visible lead and
  on the VoteWA statements.
- The 2022 SOS results list the Clerk as "Katie Sloan"; the 2026 ballot
  name is Catherine R. Sloan, who says she was elected in 2022.
