# Douglas County Completeness Note

Election: 2026 Washington general election, November 3, 2026 (VoteWA
election 899, county code 09).

Status (#30): shipped at Full County Coverage in
`APP_PACKAGES["2026-11-03-general"]["counties"]`, with its elections office
(`https://www.douglascountywa.gov/206/Current-Election`) and its VoteWA
guide (`countyGuides.douglas`, `c=09`). `COUNTY_LAYERS.douglas` reads
`SCHDST` (DOR SCH2025), `CEMDST` (DOR CEM2025) and `PROPFIRDST` (the
county's `All_Districts_Temporary/MapServer/4` `FireNumber`) beside
`FIRDST` and `HOSPDST`, as proposed below; `districts.js` names only
`PROPFIRDST` `009`. CD 4 ships with Benton's research, CD 8 with King's, LD
7 with Spokane's, LD 13 with Grant's. Live ballots on 2026-10-08, each
`full_county` with no missing layer: 100 Eastmont Ave, East Wenatchee
(Eastmont bonds); 213 S Chelan Ave, Waterville (Hospital District 2 and
Cemetery District 2 levies); 1206 Columbia Ave, Bridgeport (Three Rivers
bonds); 1005 Ashcroft Dr, Ephrata (LD 13; Rimrock formation and its three
commissioner seats); 448 Belmont Pl, Ephrata (LD 7; no Rimrock items;
Hospital District 2 and Cemetery District 2 levies). The paragraphs below
describe the package as researched.

Research status (#30): researched, scored and refuted. The builder
(`pipeline/build_votewa_lite_data.py --county douglas`) writes
`interim/app-contests.json` and `interim/app-measures.json` with
`coverage: "full_county"`, but three scope layers are not yet in
`app/src/lib/geo.js` `COUNTY_LAYERS.douglas` (see District scoping): until
they are added the assembler will mark the county `partial_county`.

## Sources

- Candidate list: VoteWA GENERAL 2026 export
  (`raw/votewa/candidate-list.csv.{url,meta.json}`, 42 rows).
- Douglas County Auditor's Current Election page
  (`https://www.douglascountywa.gov/206/Current-Election`):
  - official sample ballot (`raw/douglas/sample-ballot.pdf.url`, DocumentCenter 13224);
  - the five measure resolutions (`raw/douglas/resolution-*.pdf.url`). They are
    scans; the Rimrock Meadows resolutions (CE 26-19B, CE 26-25) and the
    Hospital District 2 and Cemetery District 2 resolutions were OCR'd for
    reading only.
- VoteWA online voters' guide for Douglas County
  (`https://voter.votewa.gov/genericvoterguide.aspx?e=899&c=09`): records
  under `raw/votewa/voter-guide/` (`race-<RaceID>.json`, `measure-<id>.json`,
  `voterguide.json`), text in `interim/voter-guide-text/`. Douglas prints no
  local voters' pamphlet; dossiers cite these unpaged guide records, so no
  Douglas record ships `pamphlet_pages`. The app should link the county's
  VoteWA guide (`officialLinks.js` `countyGuides.douglas`, `c=09`).
- Results: VoteWA results API for the August 4, 2026 primary
  (`raw/douglas/votewa-results-20260804-ballot-items.url`) and SOS Douglas
  results for 2020, 2022, 2024 and 2025 (`raw/douglas/sos-results-*.url`,
  with the 2022 and 2024 precinct exports).
- Candidate and measure sources: `raw/candidates/<contest-slug>/` and
  `raw/measures/<measure-slug>/` (campaign sites, PDC, KPQ, NCWLIFE,
  Wenatchee World (metered: opening paragraphs only), district pages, RCW).

## What ships

22 contests (10 contested, 12 uncontested) and 5 local measures. The five
Supreme Court contests are dropped by the builder and ship from the
statewide package.

| Contest | Candidates | Status | Research |
|---|---|---|---|
| U.S. Representative, CD 4 | McKinney, Duresky | contested | Benton's package |
| U.S. Representative, CD 8 | Schrier, Meline | contested | King's package (one Douglas precinct, 107, north East Wenatchee) |
| LD 7 State Senator | Short, McCoy | contested | Spokane's package |
| LD 7 Representative Pos. 1 | Engell | uncontested | Spokane's package (info-only) |
| LD 7 Representative Pos. 2 | Abell | uncontested | Spokane's package (info-only) |
| LD 13 State Senator | Ybarra | uncontested | Grant's package (info-only) |
| LD 13 Representative Pos. 1 | Dent, Garcia | contested | Grant's package |
| LD 13 Representative Pos. 2 | Martinez, Thompson | contested | Grant's package |
| Assessor | Ruud | uncontested | Douglas, info-only |
| Auditor | Duvall | uncontested | Douglas, info-only |
| Clerk of Superior Court | Biggar, Jester | contested | Douglas (carried from the primary) |
| Commissioner District No. 3 | Straub, Lesky | contested | Douglas (carried from the primary) |
| Coroner | Bateman | uncontested | Douglas, info-only |
| Prosecuting Attorney (short and full term) | Lewis | uncontested | Douglas, info-only (Lewis resigned effective 2026-09-30; his name stays on the ballot) |
| Sheriff (short and full term) | Caille, Musgrove | contested | Douglas (carried from the primary) |
| Treasurer | Rosales | uncontested | Douglas, info-only |
| Douglas PUD Commissioner District 2 | Simpson, Warner | contested | Douglas (new; PublicUtility: no rubric axis applies, no scores) |
| Court of Appeals Div. 3, Dist. 3, Pos. 1 | Murphy | uncontested | Douglas, info-only (county-scoped copy; Chelan and Yakima ship their own) |
| District Court Judge | E. Biggar | uncontested | Douglas, info-only |
| Proposed Rimrock Meadows FPD 9 Commissioner No. 1 | Cabral, Mayer | contested | Douglas (new; category Local: no rubric axis applies, no scores) |
| Proposed Rimrock Meadows FPD 9 Commissioner No. 2 | Blanchard | uncontested | Douglas, info-only |
| Proposed Rimrock Meadows FPD 9 Commissioner No. 3 | Walker | uncontested | Douglas, info-only |

`build_research_plan.py douglas` shows CD 4 `researched_in` Benton, CD 8
King, LD 7 Senator Spokane, LD 13 Pos. 1 and 2 Grant, each with no
candidates missing. Douglas has no LD 12 race (the Census geocoder puts
East Wenatchee, Waterville, Bridgeport and Mansfield in LD 7, Rock Island
and Rimrock Meadows in LD 13). The uncontested LD 7 House seats and LD 13
Senate seat have info-only scoring files in Spokane's and Grant's packages.

Measures (all five researched, scored and refuted):

| Measure | Scope |
|---|---|
| Public Hospital District No. 1, Okanogan and Douglas Counties (Three Rivers Hospital) Prop. 1 ($48M bonds) | `HOSPDST` `1` |
| Douglas County Public Hospital District No. 2 Prop. 1 (one-year $80,000 levy) | `HOSPDST` `2` |
| Eastmont School District No. 206 Prop. 1 ($125M bonds) | `SCHDST` `206` |
| Proposed Rimrock Meadows Fire Protection District No. 9 Prop. 1 (formation) | `PROPFIRDST` `009` |
| Douglas County Cemetery District No. 2 Prop. 1 (one-year $50,000 levy) | `CEMDST` `2` |

## Builder overrides

The generic VoteWA parser stops on Douglas's fire-district rows (District
Type `Fire`). The Douglas block in `ELECTION_MEASURES` carries an
`overrides` dict, keyed by upper-cased (District, Race):

- `COMMISSIONER DISTRICT NO. 3` (District Type Countywide): kept as the
  primary's contest (`Douglas County Commissioner District 3`) so the slug
  matches and primary dossiers carry forward. Scope `COUNTY`: Douglas is a
  non-charter county with three commissioners, nominated by district in the
  primary and elected county-wide in the general (RCW 36.32.040). The SOS
  precinct exports show the 2022 Commissioner 3 race and the 2024
  Commissioner 1 and 2 races on all 49 Douglas precincts; the 2026 primary
  ran on 19 units.
- `DISTRICT COURT JUDGE` (District Type Countywide): category Judicial,
  `Douglas County District Court`, `Judge`, scope `COUNTY` (one county-wide
  seat; 2022 race on all 49 precincts).
- `DOUGLAS COUNTY PUBLIC UTILITY DISTRICT` / `COMMISSIONER NO. 2`: Public
  Utility District No. 1 of Douglas County, `Commissioner District 2`, scope
  `COUNTY`. DOR PUD2025 (layer 17) has a single Douglas polygon,
  `DISTATTRIB` `1`, at every point queried below; the county's precinct-part
  layer gives every Douglas precinct part a PUD commissioner district; the
  whole PUD elects each commissioner in the general (RCW 54.12.010(3)): the
  2024 Commissioner No. 1 and 2022 Commissioner No. 3 races were on all 49
  precincts, and SOS labelled the 2020 race "Public Utility District
  Countywide".
- `RIMROCK MEADOWS FIRE PROTECTION DISTRICT NO. 9` / `COMMISSIONER NO. 1`,
  `2`, `3`: category Local, `Proposed Rimrock Meadows Fire Protection District
  No. 9`, scope `PROPFIRDST` `009`. The formation vote and the election of
  the initial commissioners are one election among the electors inside the
  proposed boundary (RCW 52.02.080; Resolution CE 26-19B, Section 2). The
  district forms only on three-fifths yes (RCW 52.02.110); the guide's
  explanatory statement says "majority".

## District scoping

Point queries, 2026-10-08 (Census geocoder, Current vintage; DOR
`WADOR_PropertyTax/MapServer`, tax year 2025, re-listed: layer ids
unchanged):

| Address | Census | DOR HSP2025 (11) | DOR CEM2025 (3) | DOR SCH2025 (20) | DOR PUD2025 (17) | DOR FIR2025 (7) | County fire layer `FireNumber` |
|---|---|---|---|---|---|---|---|
| 100 Eastmont Ave, East Wenatchee | East Wenatchee, CD 4, LD 7 | none | none | `206` | `1` | `2` | `002` |
| 205 34th St NW, East Wenatchee (unincorporated) | CD 8, LD 7 | none | none | `206` | `1` | | |
| 213 S Chelan Ave, Waterville | Waterville, CD 4, LD 7 | `2` | `2` | `209` | `1` | none | `000` |
| 1206 Columbia Ave, Bridgeport | Bridgeport, CD 4, LD 7 | `1` | none | `75` | `1` | none | |
| 50 Main St, Mansfield | Mansfield, CD 4, LD 7 | `1` | none | `207` | `1` | `5` | |
| 1 Rock Island Dr, Rock Island | Rock Island, CD 4, LD 13 | none | none | `206` | `1` | `2` | |
| 236 Brays Landing Rd, Orondo | | none | `1` | `13` | `1` | `4` | |
| 1005 Ashcroft Dr, Ephrata (Rimrock Meadows) | CD 4, LD 13 | | | | | | `009` |
| 431 Murcur Pl and 9005 W Coyote Trl, Ephrata | | | | | | | `009` |
| 448 Belmont Pl, Ephrata | | | | | | | `001` |

`COUNTY_LAYERS.douglas` today reads `FIRDST` (DOR FIR2025, layer 7) and
`HOSPDST` (DOR HSP2025, layer 11), both re-probed live above (Douglas
FIR2025 holds `1`-`5`, `8`, `J15`; HSP2025 `1`, `2`, `3`, `6`). The
archived primary uses them (FD 15 `J15`, Hospital District 1). No general
scope uses `FIRDST`; `HOSPDST` serves both hospital measures.

**Proposed for the director** (add to `COUNTY_LAYERS.douglas` and
`election.DISTRICT_ADAPTER_LAYERS["douglas"]`):

1. `{ key: 'SCHDST', url: \`${DOR_TAX_DISTRICTS}/20/query\`, attr: 'DISTATTRIB' }`
   (Eastmont SD 206; Benton and Chelan already read it).
2. `{ key: 'CEMDST', url: \`${DOR_TAX_DISTRICTS}/3/query\`, attr: 'DISTATTRIB' }`
   (Cemetery District 2; Grant already reads it).
3. `{ key: 'PROPFIRDST', url: 'https://gis.douglascountywa.gov/server/rest/services/All_Districts_Temporary/MapServer/4/query', attr: 'FireNumber' }`
   for the proposed Rimrock Meadows district (formation measure and its three
   commissioner races). Feature `FireNumber` `009`, `FireName` `Proposed
   Rimrock Fire`, `FireLabel` `Proposed Rimrock Meadows Fire District #9`,
   18,621 acres, `DateUpdated` 2026-08-19 (the day after Resolution CE 26-25).
   Other features read `001`-`008`, `015`, `BPR` and `000` (no fire district),
   so no `where` is needed (a `where FireNumber = '009'` returns the same at
   the three Rimrock points and nothing elsewhere). DOR FIR2025 has no
   Rimrock polygon (the district does not exist yet), so `FIRDST` cannot be
   used, and repointing `FIRDST` to this layer would break the archived
   primary's `J15` scope. Caveats: the service is named "Temporary"; and the
   county's precinct-part layer (`All_Districts_Temporary/MapServer/16`,
   `FireDistNumber` `RMR`) tags a different, older area (parts 209.04 and
   209.14, 65 square miles, edited 2026-08-04) while parts 211.08 and 211.09,
   inside the layer-4 polygon, read `000`. The address layer
   (`Addresses_view/FeatureServer/2` `DCFireDistrict`) reads `000` at the
   Rimrock addresses. Layer 4 was edited after the Boundary Review Board and
   the renaming resolution, so it is taken as the proposed boundary; the
   Auditor could confirm. If the director prefers not to rely on it, keep
   the four Rimrock records as an unresolvable `douglas/PROPFIRDST` scope
   (`partial_county`); they must not be scoped `COUNTY`.

Suggested live checks: 100 Eastmont Ave, East Wenatchee (Eastmont bonds);
213 S Chelan Ave, Waterville (Hospital District 2, Cemetery District 2);
1206 Columbia Ave, Bridgeport (Three Rivers bonds); 1005 Ashcroft Dr,
Ephrata (Rimrock formation and commissioners, LD 13); 205 34th St NW, East
Wenatchee (CD 8). The commissioner district layer
(`services2.arcgis.com/fjst9C4kBtvXuiLQ/.../Commissioner_Districts_view/FeatureServer/0`)
is public but no general scope needs it.

## Known gaps

- WebSearch quota was exhausted; sources came from direct fetches of
  outlet search pages, county and district sites, PDC open data and SOS
  results. Wenatchee World is metered (opening paragraphs only).
  eastmont206.org and marcstraub.com fail TLS verification here and were
  fetched with `curl -k` (noted in their metas); Molly Simpson's campaign
  site returns a Cloudflare 403 to curl and was read through WebFetch (its
  meta has no sha256).
- Thin evidence: Michael S. Lesky (Commissioner D3) submitted no statement
  and has no site (pamphlet-only, no scores); the Rimrock candidates
  (Cabral, Mayer, Blanchard, Walker) are statement-only. Walker's Skagit
  Fire District 5 and United General Hospital District 304 service is his
  own claim, not verified. The Rimrock candidates filed on 2026-08-31 per
  VoteWA, after the August 24-26 special filing period KPQ reported.
- Adam Musgrove's Navy service: 25 years and retired senior chief in his
  statement, "a ten-year stint" per KPQ; not reconciled.
- Prosecuting Attorney: the only candidate, appointed prosecutor Sean P.
  Lewis, resigned effective September 30, 2026 (KPQ); former prosecutor
  Gordon Edgar is interim and the commissioners plan another interim
  appointment in early 2027.
- The Hospital District 1 (Resolution 2026-10) and Eastmont (Resolution
  2026-02) resolutions are scans that were not read; measure texts come
  from the sample ballot and VoteWA records.
