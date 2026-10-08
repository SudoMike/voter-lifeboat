# Pacific County Completeness Note

Election: 2026 Washington general election, November 3, 2026 (VoteWA
election 899, county code 25).

Status (#31): researched, scored and refuted; not yet declared in
`APP_PACKAGES`. The builder reports `full_county`, but the two District
Court seats are scoped `DISTCRT` (`North`, `South`), which no adapter layer
resolves yet (see District scoping). Until a layer is added the assembler
will mark Pacific `partial_county` for `DISTCRT`, or the director adds
`pacific/DISTCRT` to `UNRESOLVABLE_SCOPES`.

## Sources

- Candidate list: VoteWA GENERAL 2026 export
  (`raw/votewa/candidate-list.csv.{url,meta.json}`, 31 rows; the ten
  Supreme Court rows are dropped by the builder).
- Candidate statements and measure records: VoteWA's online voters' guide
  for Pacific County (`https://voter.votewa.gov/genericvoterguide.aspx?e=899&c=25`),
  records under `raw/votewa/voter-guide/` (`voterguide.json`,
  `race-<RaceID>.json`, `measure-<id>.json`), text in
  `interim/voter-guide-text/`. The guide index lists exactly the export's
  races plus four local measures (7284, 7388, 7389, 7391) and the three
  statewide ones. The dossiers cite these unpaged records, so the app should
  link the county's VoteWA guide (`officialLinks.js` `countyGuides.pacific`,
  `c=25`).
- Pacific County's own site did not answer on 2026-10-08:
  `pacificcountywa.gov` has no A record (NXDOMAIN for `www`), and
  `co.pacific.wa.us` (96.66.228.67) refused or timed out on ports 80 and 443
  from here and from WebFetch. The Auditor's local voters' pamphlet is
  mailed in the ballot envelope (Chinook Observer, 2026-09-13) and was not
  found online; no sample ballot was read. The ballot was checked against
  VoteWA's guide index instead. The director should re-try
  `https://co.pacific.wa.us/auditor/elections.htm` before choosing the
  elections office URL.
- SOS election results (`raw/sos/`): 2018, 2020, 2022, 2024 and 2025
  general summary pages, the 2018, 2022 and 2024-primary/2022-primary
  precinct exports, and the VoteWA results API for the 2026 primary.
- Local press: Chinook Observer (WordPress REST search,
  `chinookobserver.com/wp-json/wp/v2/posts?search=`), which also carries
  Willapa Harbor Herald coverage of north county. Pointers under
  `raw/news/`, `raw/candidates/<contest>/`, `raw/measures/<slug>/`.
- PDC: data.wa.gov dataset `3h9x-7bvm` (`raw/pdc/`).

## What ships

13 contests (8 contested, 5 uncontested) and 4 local measures.

| Contest | Candidates | Status | Research |
|---|---|---|---|
| U.S. Representative, CD 3 | Braun, Gluesenkamp Perez | contested | Clark's package |
| LD 19 Representative Pos. 1 | Walsh, Moynihan | contested | Thurston's package |
| LD 19 Representative Pos. 2 | Carlson, McEntire | contested | Thurston's package |
| Commissioner District 3 | Gray, Doyle | contested | Pacific (carried from the primary) |
| Sheriff | Garcia, Byrd | contested | Pacific (carried from the primary) |
| Assessor | Walker, Phelan | contested | Pacific (carried from the primary) |
| Auditor (short and full term) | Graves, Deskins | contested | Pacific (carried from the primary) |
| Prosecuting Attorney (open) | Zorn, Turner | contested | Pacific (carried from the primary) |
| Clerk | Rose | uncontested | Pacific, info-only |
| Treasurer (open) | Didion | uncontested | Pacific, info-only |
| District Court, North District | Harmer | uncontested | Pacific, info-only |
| District Court, South District | McAllister | uncontested | Pacific, info-only |
| PUD No. 2 Commissioner District 1 | Hickey | uncontested | Pacific, info-only |

`build_research_plan.py pacific` shows CD 3 `researched_in` Clark and LD
19 Pos. 1 and 2 `researched_in` Thurston, each with no candidates missing.
No Court of Appeals seat is on Pacific's ballot: Division II District 3
Position 1 was elected in 2024 and Position 2 in 2022 (SOS results), and
neither the export nor the guide lists one. No Superior Court seat (Pacific
and Wahkiakum share one, elected in 2024) and no port, hospital or fire
commissioner race is on the general ballot.

Measures (all researched, scored and refuted):

| Measure | Scope |
|---|---|
| Timberland Regional Library District Prop. 1 (levy lid lift to $0.35) | `COUNTY` |
| North Pacific County EMS District No. 1 Prop. 1 (one-year $0.40 excess levy, max $800,000) | `EMSDST` `1` |
| Pacific County Fire Protection District No. 3 Prop. 1 (lid lift to $0.61) | `FIRDST` `3` |
| Pacific County Fire Protection District No. 6 Prop. 1 ($0.50 with 6% limit factor for five years) | `FIRDST` `6` |

## Builder overrides

The Pacific block in `ELECTION_MEASURES["2026-11-03-general"]` carries an
`overrides` dict, keyed by upper-cased (District, Race):

- `County` / `COUNTY COMMISSIONER #03` (District Type Countywide): kept as
  the primary's contest (`Pacific County Commissioner District 3`, `County
  Commissioner #03`), so the slug matches and the primary dossiers carry
  forward. Scope `COUNTY`: nominated by district, elected county-wide in
  the general (RCW 36.32.040). Evidence: the 2022 District 3 primary ran in
  District 3's precincts only (2022-08-02 precinct export), while every
  precinct voted in the 2018 #03 general (9,231 votes of 11,105 ballots)
  and the 2022 #03 general (10,443 votes of 12,068).
- `Court - North District` / `DISTRICT COURT JUDGE` and `Court - South
  District` / same: category Judicial, `Pacific County District Court North
  District` / `South District`, office `District Court Judge`, scope
  `DISTCRT` `North` / `South`. The generic rule scoped both `COUNTY`, which
  would show both judges to every voter. They are separate electorates: in
  2022 the North judge drew 3,221 votes from 23 precincts and the South
  judge 5,053 from 18 (2022-11-08 precinct export); in 2018, 23 and 16
  precincts.
- `PUD District 2` / `PUBLIC UTILITY COMMISSIONER #01`: `Public Utility
  District No. 2 of Pacific County`, `Commissioner District 1`, scope
  `COUNTY`. The generic rule made it `PUDDST` `2` (unresolvable). DOR
  PUD2025 (layer 17) has one Pacific polygon, `DISTATTRIB` `2`, whose area
  (6,737,423,706) equals the sum of Pacific's TCA2025 polygons
  (6,737,558,937); every precinct voted in the 2018 and 2022 PUD races
  (RCW 54.12.010(3)).

`COUNTY_CONFIG.pacific` (primary geography) is unchanged. Because the
override hook does not report unresolvable layers, the builder prints
`full_county`; the `extra_notes` say the District Court seats need a layer.

## District scoping

`COUNTY_LAYERS.pacific` in `geo.js` lists only `FIRDST` (DOR FIR2025, layer
7, `DISTATTRIB`); it answers live and returns `3` and `6` at the addresses
below. Point queries, 2026-10-08 (Census geocoder, Current vintage; DOR
`WADOR_PropertyTax/MapServer`, tax year 2025, whose layer list is unchanged:
6 EMS2025, 7 FIR2025, 12 LIB2025, 17 PUD2025, 20 SCH2025):

| Address | Place | EMS (6) | FIR (7) | LIB (12) | PUD (17) | SCH (20) | HSP (11) | PRT (16) |
|---|---|---|---|---|---|---|---|---|
| 300 Memorial Dr, South Bend | South Bend city | `1` | none | `L` | `2` | `118` | `2` | `WILL` |
| 230 2nd St, Raymond | Raymond city | `1` | none | `L` | `2` | `116` | `2` | `WILL` |
| 115 Bolstad St, Long Beach | Long Beach city | none | none | `L` | `2` | `101` | `3` | `PEN` |
| 120 1st Ave N, Ilwaco | Ilwaco city | none | none | `L` | `2` | `101` | `3` | `ILW` |
| 1511 Bay Ave, Ocean Park | Ocean Park CDP | `OB` | `1` | `L` | `2` | `101` | `3` | `PEN` |
| 793 State Rte 4, Naselle | Naselle CDP | `1` | `4` | `L` | `2` | `155` | `3` | `ILW` |
| 2964 Kindred Ave, Tokeland | Tokeland CDP | `SBH` | `5 SBRFA` | `L` | `2` | `172` | `2` | `WILL` |
| 810 US Hwy 101, Chinook | Chinook CDP | none | `2` | `L` | `2` | `101` | `3` | `CHIN` |
| 38 2nd St, Bay Center | Bay Center CDP | `1` | `6` | `L` | `2` | `118` | `2` | `WILL` |
| 3 Park St E, Bay Center | Bay Center CDP | `1` | `6` | `L` | `2` | `118` | `2` | `WILL` |
| 1000 State Rte 6, Raymond (Menlo area) | (none) | `1` | `3` | `L` | `2` | `160` | `2` | `WILL` |

All addresses are LD 19 and CD 3 in the Census geocoder.

Scopes and the layers they need:

- `COUNTY` (commissioner, PUD, county offices, TRL levy): no layer.
  Timberland: DOR LIB2025 has one Pacific polygon, `L`, with the county's
  area, so the levy is county-wide (as in Mason, unlike Grays Harbor).
- `FIRDST` `3`, `6`: DOR FIR2025, already in `COUNTY_LAYERS.pacific`.
- `EMSDST` `1`: DOR EMS2025 (layer 6), **not** in `COUNTY_LAYERS.pacific`.
  Proposal: add `{ key: 'EMSDST', url: `${DOR_TAX_DISTRICTS}/6/query`, attr:
  'DISTATTRIB' }` (Ferry and Asotin use the same) to `COUNTY_LAYERS.pacific`
  and `election.DISTRICT_ADAPTER_LAYERS["pacific"]`. DOR EMS2025's Pacific
  polygons are `1` (3,997,285,969 sq ft), `OB`, `SBH` and `15`; `1` matches
  the ballot title's district (Pacific County minus the Ocean Beach, Ocosta
  and North River school districts): South Bend, Raymond, Naselle, Bay
  Center and Menlo return `1`; Ocean Park `OB`; Tokeland `SBH`; Long Beach,
  Ilwaco and Chinook nothing.
- `DISTCRT` `North` / `South`: **no layer found.** Searched: the DOR
  layers (no court districts), ArcGIS Online (`Pacific County precinct`,
  `district court`, `commissioner districts`, `Willapa`: no Pacific County
  org or election layers), the county's own GIS (site unreachable). The
  only precinct geometry found is WAGeoservices' `Statewide_Precincts_2019General_SPS`
  (`services.arcgis.com/jsIt88o09Q0r1j8h/.../FeatureServer/0`, `CountyName
  = 'Pacific'`, 42 precincts with `PrecCode`/`PrecName`), a 2019 snapshot
  that is not the current election geography. Joining it to the 2018
  precinct results shows the court districts follow precinct lines that
  roughly match school districts: North = precincts in Raymond SD 116, South
  Bend SD 118, Willapa Valley SD 160, North River SD 200 and Ocosta SD 172;
  South = Ocean Beach SD 101 and Naselle-Grays River SD 155. Several
  precincts straddle (sample points in Naselle precinct fall in SD 160, in
  Bay Center and South Bend 1R in SD 101), so a school-district proxy would
  misplace some voters. Recommendation: ship `DISTCRT` unresolvable
  (`pacific/DISTCRT` in `UNRESOLVABLE_SCOPES`, both seats uncontested and
  information-only) unless the Pacific County Auditor publishes a precinct
  or court-district layer. Commissioner districts do not match either
  (South Bend and Bay Center are in Commissioner District 1 but vote in the
  North court district; 2024 primary precinct export).

Suggested live checks (each should show TRL; EMS where noted; no `missing`
layer once EMSDST is added): 300 Memorial Dr, South Bend 98586 (EMS 1);
115 Bolstad St, Long Beach 98631 (no EMS, no fire measure); 38 2nd St, Bay
Center 98527 (EMS 1, FD 6); 1000 State Rte 6, Raymond 98577 (EMS 1, FD 3);
2964 Kindred Ave, Tokeland 98590 (no local measure but TRL).

## Known gaps

- No county pamphlet, sample ballot or Auditor page could be read (site
  unreachable); scopes were checked against VoteWA, SOS results and GIS.
- Walker (assessor) and McAllister (South District Court) filed no
  voters' guide statement; Walker's dossier rests on his assessor columns
  and SOS results.
- Turner (prosecutor) has no campaign site and no press Q&A; the Chinook
  Observer ran questionnaires only for the commissioner and sheriff races.
- Fire District 3 and Fire District 6 measures are `pamphlet-only`: no
  statements for or against, no local coverage, no PDC committee. Fire
  District 6's explanatory statement does not give its current levy rate.
- The EMS measure's district is the DOR EMS2025 polygon `1`; the ballot
  title defines it by school-district exclusions. The two agree at every
  address probed, but DOR's tax-year-2025 polygon could lag a boundary
  change.
