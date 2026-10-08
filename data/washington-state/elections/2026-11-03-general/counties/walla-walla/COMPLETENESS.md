# Walla Walla County Completeness Note

Election: 2026 Washington general election, November 3, 2026 (VoteWA
election 899, county code 36).

Research package for #30 (county wave 5), not yet shipped. Contests and
measures are built by `pipeline/build_votewa_lite_data.py --county
walla-walla` from the VoteWA candidate list (`raw/votewa/candidate-list.csv.url`)
and the overrides and measures in that script's
`ELECTION_MEASURES["2026-11-03-general"]["walla-walla"]`, checked against the
Walla Walla County Auditor's general sample ballot
(`raw/walla-walla/sample-ballot.pdf.url`, text in
`interim/pdf-text/sample-ballot.txt`), its local voters' pamphlet
(`raw/walla-walla/local-voters-pamphlet.pdf.url`, 28 pages, text in
`interim/pdf-text/local-voters-pamphlet.txt`; PDF page numbers equal the
printed page numbers) and VoteWA's online voters' guide for the county
(`https://voter.votewa.gov/genericvoterguide.aspx?e=899&c=36`; records under
`raw/votewa/voter-guide/`, text in `interim/voter-guide-text/`). The pamphlet
and sample ballot are linked from the Auditor's Current Election page,
`https://www.wwcowa.gov/government/auditor/current_election.php` (the page's
`<base href>` is `https://www.wwcowa.gov/`, so its relative links resolve at
the site root). The older `co.walla-walla.wa.us` domain still serves the home
page; the elections office's own address is `elections@wwcowa.gov`.

The builder reports `full_county` with no unresolvable layer, but its flag
does not check measure scopes: the two measures need `SCHDST` and `PARKDST`,
which `app/src/lib/geo.js` `COUNTY_LAYERS['walla-walla']` does not read yet
(it reads only `COUNTY_COUNCIL`). See "Layers to add at ship time".

## What is on the ballot

14 contests (7 contested, 7 uncontested) and 2 local measures, matching the
sample ballot. The five Supreme Court contests and the three statewide
initiatives are dropped by the builder and ship from the statewide package.

| Kind | Contests | Contested | Uncontested | Scope | Researched |
|---|---|---|---|---|---|
| U.S. Representative (CD 5) | 1 | 1 | 0 | `CONGDST` `5` | Spokane package |
| LD 16 Rep. Pos. 1, Pos. 2 | 2 | 2 | 0 | `LEGDST` `16` | Benton package |
| Auditor (short and full term), Sheriff | 2 | 2 | 0 | `COUNTY` | here |
| County Commissioner District 3 | 1 | 1 | 0 | `COUNTY` | here |
| District Court Judge, Part Time | 1 | 1 | 0 | `COUNTY` | here |
| Assessor, Clerk, Coroner, Prosecuting Attorney, Treasurer | 5 | 0 | 5 | `COUNTY` | here (info-only) |
| District Court Judge, Full Time | 1 | 0 | 1 | `COUNTY` | here (info-only) |
| Court of Appeals Div. III, Dist. 2, Pos. 1 | 1 | 0 | 1 | `COUNTY` | here (info-only copy, as Benton and Grant) |

Walla Walla County is wholly in CD 5 and LD 16 (Census geocoder, Current
vintage, at all five probe addresses below). No LD 16 Senate seat is on the
2026 ballot. The plan names all three shared races `researched_in` (Spokane:
CD 5; Benton: LD 16 Pos. 1 and Pos. 2) with no `candidates_missing`. None of
the 11 county-owned contests is shared with another package.

Carried forward from the primary package (dossiers refreshed, scores redone
under the general's rubric): Auditor, Commissioner District 3 and Sheriff,
both finalists each. New since the primary: District Court Part Time (two
candidates, no primary held) and the seven uncontested entries.

Measures (VoteWA guide records 7378, 7379; pamphlet pages 22-25):

- Dixie School District No. 101 Proposition 1, replacement capital levy,
  $75,000 a year for 2027-2032 (about $0.50 per $1,000): `SCHDST` `101`.
- Prescott Joint Park and Recreation District Proposition No. 1, one-year
  maintenance and operation excess levy, $175,000 for 2027 (about $0.35 per
  $1,000): `PARKDST` `PRES`. The district is joint with Columbia County, whose
  voters also decide it; Columbia County is not a Supported County.

## District scoping

- **Commissioner District 3: countywide in the general.** Walla Walla County
  is a non-charter county with three commissioners; they are nominated by
  district in the primary and elected countywide in the general (RCW
  36.32.040). Evidence:
  - VoteWA's general export lists the race as District Type `Countywide`,
    District `County`.
  - The 2026 primary's District 3 race reported 18 of 62 units in the VoteWA
    results API; every countywide primary race reported 62 of 62
    (`raw/candidates/walla-walla-walla-walla-county-commissioner-district-3-county-commissioner-district-3/votewa-2026-08-04-primary-results.json.url`).
  - SOS precinct exports: the 2022 District 3 general race and the 2024
    District 1 and District 2 general races appear on all 62 precincts that
    report any race, the same 62 as the statewide offices
    (`raw/walla-walla/sos-results-20221108-walla-walla-precincts.csv.url`,
    `raw/walla-walla/sos-results-20241105-walla-walla-precincts.csv.url`).
  - The Union-Bulletin's Q&As say: "In the November general election, the
    race will be countywide."

  Scope `COUNTY`. The override keeps the primary's contest name, so the slug
  `walla-walla-walla-walla-county-commissioner-district-3-county-commissioner-district-3`
  and primary dossiers carry forward. `COUNTY_COUNCIL` is not needed in the
  general.
- **District Court**: one countywide district with a full-time and a
  part-time judge (Union-Bulletin, 2022 and 2026). VoteWA files both seats as
  District Type `Countywide`; the overrides name them `Walla Walla County
  District Court` / `District Court Judge - Full Time` and `- Part Time`,
  category `Judicial`.
- **Court of Appeals Div. III, Dist. 2, Pos. 1**: the generic rule scopes it
  `COUNTY` (whole-county electorate); shipped info-only.
- **No PUD or port race.** WA DOR PUD2025 (layer 17) returns no feature at
  any Walla Walla probe address; PRT2025 (layer 16) returns one countywide
  `WALLA WALLA` polygon at all five.

## Layers each scope needs (probed 2026-10-08)

Addresses were geocoded with the Census geocoder
(`geocoding.geo.census.gov/geocoder/locations/onelineaddress`,
`Public_AR_Current`) and point-queried with
`?geometry=<x>,<y>&geometryType=esriGeometryPoint&inSR=4326&spatialRel=esriSpatialRelIntersects&outFields=...&returnGeometry=false&f=json`.
`DOR` = `https://webgis.dor.wa.gov/arcgis/rest/services/Programs/WADOR_PropertyTax/MapServer`.

| Address | Census place | CD / LD | DOR SCH2025 (20) `DISTATTRIB` | DOR PKR2025 (14) `DISTATTRIB` | DOR FIR2025 (7) | County `commis_dis` |
|---|---|---|---|---|---|---|
| 315 W Main St, Walla Walla 99362 | Walla Walla city | 5 / 16 | `140` | none | none | 1 |
| 625 S College Ave, College Place 99324 | College Place city | 5 / 16 | `250` | none | none | 3 |
| 940 SE Harvest Dr, College Place 99324 | College Place city | 5 / 16 | `250` | none | none | 3 |
| 106 Preston Ave, Waitsburg 99361 | Waitsburg city | 5 / 16 | `401` | `WAIT` | `2` | 2 |
| 108 S D St, Prescott 99348 | Prescott city | 5 / 16 | `402` | `PRES` | none | 2 |
| 785 Tumbleweed Ln, Burbank 99323 | none (unincorporated) | 5 / 16 | `400` | none | `5` | 3 |
| interior point (-118.153, 46.140), Dixie CDP | none | 5 / 16 | `101` | none | `8` | 2 |

(`commis_dis` is
`https://services8.arcgis.com/COL6rRPkF9w28VGX/arcgis/rest/services/Voting_Districts1/FeatureServer/52/query`,
the layer `COUNTY_LAYERS['walla-walla']` already reads; the general does not
use it.)

- `CONGDST`, `LEGDST`: Census layers; every contest above resolves.
- `COUNTY`: no layer.
- `SCHDST` `101` (Dixie): WA DOR SCH2025, layer 20, attribute `DISTATTRIB`.
  Walla Walla County's values are 101, 140, 250, 300, 400, 401 and 402
  (`where COUNTYNAME='WALLA WALLA'`). `101` also names districts in Clark,
  Pacific, Skagit and Whatcom; a point query inside Walla Walla County never
  reaches them, and only Walla Walla's package lists a `101` measure. The
  Census geocoder matched no street address in Dixie (Dixie School's 10520 E
  Highway 12, and Main St, Biscuit Ridge Rd and Dry Creek Rd variants), so
  the probe used an interior point of the Dixie CDP. The county also has a
  `School_Districts/FeatureServer/0` layer (`district` attribute, not
  probed); DOR is proposed to match the other counties.
- `PARKDST` `PRES` (Prescott): WA DOR PKR2025, layer 14, attribute
  `DISTATTRIB`. Walla Walla County has two park districts in it, `PRES` and
  `WAIT` (Waitsburg); DOR has a `PRES` polygon in Columbia County too.
  Whitman's `COUNTY_LAYERS` already reads this layer the same way.

### Layers to add at ship time

```js
'walla-walla': [
  { key: 'COUNTY_COUNCIL', url: 'https://services8.arcgis.com/COL6rRPkF9w28VGX/arcgis/rest/services/Voting_Districts1/FeatureServer/52/query', attr: 'commis_dis' },
  { key: 'SCHDST', url: `${DOR_TAX_DISTRICTS}/20/query`, attr: 'DISTATTRIB' },
  { key: 'PARKDST', url: `${DOR_TAX_DISTRICTS}/14/query`, attr: 'DISTATTRIB' },
],
```

and `election.DISTRICT_ADAPTER_LAYERS["walla-walla"]` = `CONGDST`, `LEGDST`,
`CITY`, `COUNTY_COUNCIL`, `SCHDST`, `PARKDST`. Without them the assembler
would mark the county `partial_county` for both measures.

### Suggested live checks

- 108 S D St, Prescott, WA 99348: CD 5, LD 16, `SCHDST` `402`, `PARKDST`
  `PRES`; expect the Prescott park levy, no Dixie levy.
- 315 W Main St, Walla Walla, WA 99362: `SCHDST` `140`, no `PARKDST`; expect
  no local measure.
- 106 Preston Ave, Waitsburg, WA 99361: `PARKDST` `WAIT`; expect no local
  measure (Waitsburg's park district has none this year).
- Dixie: no Census-geocodable address was found. `live_ballot.mjs` takes
  addresses, so the Dixie levy can only be checked by a direct point query at
  (-118.153, 46.140) unless the director finds a geocodable address there.

Every address should show all 11 county-owned contests (county offices,
Commissioner District 3, both District Court seats, the Court of Appeals
seat), CD 5 with Spokane's scoring and LD 16 with Benton's.

## Sources

The county prints a local voters' pamphlet (28 pages), so candidate and
measure records can carry `local-voters-pamphlet` pages: Assessor 11, Auditor
12, Clerk 13, Commissioner District 3 14, Coroner 15, Prosecuting Attorney 16,
Sheriff 17, Treasurer 18, District Court Full Time 19, Part Time 20, Dixie
22-23, Prescott 24-25. Its general pamphlet PDF is
`https://www.wwcowa.gov/November%20General%202026-%20Final.pdf` (200,
application/pdf, 6,914,462 bytes on 2026-10-08). The Court of Appeals entry
cites VoteWA's guide (the local pamphlet does not print it). Local news is
the Walla Walla Union-Bulletin (union-bulletin.com), whose site search
(`/search/?q=...`) and story pages are readable by script.

## Known gaps

- Pamphlet page 20 prints Nicholas Holce's statement under Janelle
  Carman-Wagner's contact block; VoteWA guide race 186919 shows the statement
  is Holce's and that Carman-Wagner submitted none. The dossiers cite it that
  way.
- Coroner Greenwood, Prosecuting Attorney Acosta, Treasurer Heimbigner and
  Judge Hawkins submitted no statements; their info-only entries rest on
  incumbency reporting and primary results.
- The Union-Bulletin gave Troy Woody's age as 51 (July) and 61 (October).
- The Dixie levy's expiring-levy rate and the Columbia County share of the
  2025 Prescott vote were not found.
- VoteWA's Dixie record names Peter Berg as the committee against; the
  printed pamphlet says no information was submitted.
- LD 16 Pos. 2 incumbent Skyler Rude resigned from the Legislature effective
  October 31 but stays on the ballot; Benton's package already says so.
