# Pierce County Completeness Note

Election: 2026 Washington general election, November 3, 2026 (VoteWA
election 899, county code 27).

As of 2026-10-08 (#21) this package ships in the general at
`coverage: "full_county"`: `pipeline/election.py` declares it in
`APP_PACKAGES["2026-11-03-general"]["counties"]` with a
`DISTRICT_ADAPTER_LAYERS["pierce"]` entry, and every contest and measure
scope is one the Pierce District Adapter (Census `CONGDST`/`LEGDST`/`CITY`
plus `app/src/lib/geo.js` `COUNTY_LAYERS.pierce`) resolves from an
address. Assembly reads `interim/app-contests.json` and
`interim/app-measures.json`, built by `pipeline/build_pierce_lite_data.py`
from the VoteWA candidate list and Pierce County's online voters' guide on
VoteWA.

## What ships

43 contests (27 contested, 16 uncontested) and 14 measures. The Supreme
Court contests are dropped by the builder and ship once, from the statewide
package.

| Kind | Contests | Contested | Uncontested | Scope |
|---|---|---|---|---|
| U.S. Representative (CD 6, 8, 10) | 3 | 3 | 0 | `CONGDST` |
| State Senator / Representative (LD 2, 25, 26, 27, 28, 29, 31) | 17 | 16 | 1 (LD 27 Pos. 2) | `LEGDST` |
| Auditor, Prosecuting Attorney | 2 | 2 | 0 | countywide |
| County Council (Districts 1, 5, 7) | 3 | 3 | 0 | `COUNTY_COUNCIL` |
| Court of Appeals, Division 2, District 1, Position 2 | 1 | 0 | 1 | countywide |
| Pierce County District Court, Positions 1 to 8 | 8 | 2 (Pos. 7, 8) | 6 | `DISTCRT` `YES` |
| King County District Court, Southeast Electoral District, Positions 1 to 6 | 6 | 1 (Pos. 5) | 5 | `KCDISTCRT` `YES` |
| Tacoma Municipal Court, Positions 1 to 3 | 3 | 0 | 3 | `CITY` `Tacoma` |

All 54 contested candidates are scored.

Shared with King (`pipeline/shared_contests.py`), shipped with King's
scoring and dossiers and no pamphlet pages of their own: CD 8, LD 31
Senator, Pos. 1 and Pos. 2, and King County District Court Southeast
Positions 1 to 6. The five uncontested Southeast seats carry King's
information-only entries; the other 11 uncontested seats ship
official-ballot-only (no scoring file).

Measures: Pierce County Charter Amendments 52 to 58 (countywide); Milton
Prop 1, South Prairie Prop 1, Tacoma Initiative 1 (`CITY`); Pierce Transit
Prop 1 (`PTBA` `YES`); Fire Protection District 14 Prop 1 (`FIRDST`
`FPD #014 RIVERSIDE`); Auburn SD 408 Prop 1 and Yelm Community Schools
Prop 1 (`SCHDST`). Charter Amendments 52 to 55 and 58 have no rubric axis.
Milton Prop 1 and Auburn SD 408 Prop 1 are also in King's package; each
copy is scoped to its own county (`pierce-` slugs here), so a voter sees
one.

## Pamphlet links

Federal and legislative candidates Pierce researched cite SOS Edition 09
(`raw/sos/voters-pamphlet-edition-09-pierce.pdf.url`, 64 pages, PDF pages
equal printed pages); their `pamphlet_pages` link that PDF
(`officialLinks.js` `pamphletPdfs`). County offices, District Court and
local measures cite VoteWA's online guide (piercecountywa.gov answered 403
to scripted requests, so the printed local pamphlet was not fetched); they
ship no pages and the app links `countyGuides.pierce`
(`https://voter.votewa.gov/genericvoterguide.aspx?e=899&c=27`).

## District scoping

All from Pierce County's ArcGIS Online services
(`services2.arcgis.com/1UvBaQ5y1ubjUPmd`):

- `COUNTY_COUNCIL`: `Pierce_County_Council_Districts`, `District_Number`.
- `FIRDST`: `Fire_Districts`, `FIRE_DIS` (`FPD #014 RIVERSIDE`).
- `DISTCRT`, `KCDISTCRT`, `PTBA`, `SCHDST`: `Election_Precincts`,
  attributes `PC_DISTRICT`, `KING_DISTRICT`, `PIERCE_TRANSIT` (each
  `YES`/`NO`) and `SCHOOL` (full name, `AUBURN SCHOOL DISTRICT NO. 408`).
  Live 2026-10-08: 1402 Lake Tapps Pkwy SE, Auburn -> `PC_DISTRICT` `NO`,
  `KING_DISTRICT` `YES`, `PIERCE_TRANSIT` `YES`, `SCHOOL` Auburn 408;
  930 Tacoma Ave S -> `YES`, `NO`, `YES`, Tacoma 10; 121 Washington St,
  South Prairie -> `PIERCE_TRANSIT` `NO`; (-122.55764, 46.93652) ->
  `YELM COMMUNITY SCHOOLS`.

The adapter queries the precinct layer once per key (four requests per
address).

## Known gaps

- 1402 Lake Tapps Pkwy SE (Pierce-side Auburn) is in CD 10, not CD 8:
  the Census geocoder and the precinct layer's `CONGRESSIONAL` field agree.
  811 Main St, Buckley is a Pierce CD 8 address.
- The VoteWA pointer meta (`raw/votewa/candidate-list.csv.meta.json`)
  carries `sha256_case_normalized` since #27 (6730ab2, a re-export with the
  same byte count); the builder rebuilds both elections byte-identical.
- `interim/dossier-audit.json` is the pre-research audit; a fresh
  `verify_dossiers.py pierce --election 2026-11-03-general` reports 0
  errors (rich 18, moderate 23, pamphlet-only 3; 5 researched elsewhere)
  but the regenerated file is not committed with the ship.
- The county elections office URL (`https://www.piercecountywa.gov/elections`)
  answers 403 to scripted requests, so it was not checked for HTTP 200.
