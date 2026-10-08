# Columbia County Completeness Note

Election: 2026 Washington general election, November 3, 2026 (VoteWA
election 899, county code 07).

Status (#32): shipped at Full County Coverage in
`APP_PACKAGES["2026-11-03-general"]["counties"]`, with its elections office
(`https://www.columbiaco.com/616/2026-General-Election`), its local pamphlet
(`pamphletPdfs['columbia/local-voters-pamphlet']`, PDF pages) and its VoteWA
guide (`countyGuides.columbia`, `c=07`). `COUNTY_LAYERS.columbia` gained
`PARKDST` (DOR PKR2025, layer 14) as proposed below; `COUNTY_COUNCIL` was
re-probed. CD 5 and LD 9 Pos. 1/2 ship with Spokane's research. The ship
pass rewrote the Prosecutor ref's nested parenthesis, which had added a
wrong PDF p. 5 to Ward's pages. Live ballots on 2026-10-08, each
`full_county` with no missing layer and the 12 contests: 341 E Main St,
Dayton (Pool District levy), 101 Main St, Starbuck (no local measure) and
the Prescott district point (-118.21, 46.40) (Columbia's Prescott levy). The
paragraphs below describe the package as researched.

Research package for #32 (county wave 7). Contests and
measures are built by `pipeline/build_votewa_lite_data.py --county columbia`
from the VoteWA candidate list (`raw/votewa/candidate-list.csv.url`) and the
overrides and measures in that script's
`ELECTION_MEASURES["2026-11-03-general"]["columbia"]`, checked against:

- the Columbia County Auditor's local voters' pamphlet
  (`raw/columbia/local-voters-pamphlet.pdf.url`,
  `https://www.columbiaco.com/DocumentCenter/View/8822`, 12 PDF pages, text
  in `interim/pdf-text/local-voters-pamphlet.txt`). **PDF page = printed
  page + 1** (the cover is unnumbered): Assessor and Auditor PDF p. 5, Clerk
  and Prosecutor p. 6, Commissioner No. 3 p. 7, Sheriff and Treasurer p. 8,
  District Court Judge p. 9, Pool District levy p. 10, Prescott levy p. 11.
  It prints local races and measures only.
- the sample ballot for precinct Brooklyn, published as two JPEG images on
  `https://www.columbiaco.com/624/Sample-Ballot`
  (`raw/columbia/sample-ballot-page-{1,2}.jpg.url`; read visually, no text
  layer).
- VoteWA's online voters' guide for the county
  (`https://voter.votewa.gov/genericvoterguide.aspx?e=899&c=07`; records
  under `raw/votewa/voter-guide/`, text in `interim/voter-guide-text/`).

All three are linked from the Auditor's 2026 General Election page,
`https://www.columbiaco.com/616/2026-General-Election`
(`raw/columbia/elections-page.html.url`; 200 to a browser User-Agent on
2026-10-08). The Auditor's office is at 115 E Main St, Suite 3, Dayton,
509-382-4541 (pamphlet).

The builder reports `full_county` with no unresolvable layer, but its flag
does not check measure scopes: the two measures need `PARKDST`, which
`app/src/lib/geo.js` `COUNTY_LAYERS.columbia` does not read yet (it reads
only `COUNTY_COUNCIL`). See "Layers to add at ship time".

## What is on the ballot

12 contests (3 contested, 9 uncontested) and 2 local measures, matching the
sample ballot and the guide. The five Supreme Court contests and the three
statewide initiatives are dropped by the builder and ship from the
statewide package.

| Kind | Contests | Contested | Uncontested | Scope | Researched |
|---|---|---|---|---|---|
| U.S. Representative (CD 5) | 1 | 1 | 0 | `CONGDST` `5` | Spokane package |
| LD 9 Rep. Pos. 2 | 1 | 1 | 0 | `LEGDST` `9` | Spokane package |
| LD 9 Rep. Pos. 1 (Mary Dye) | 1 | 0 | 1 | `LEGDST` `9` | Spokane package (info-only scoring exists there) |
| County Commissioner No. 3 | 1 | 1 | 0 | `COUNTY` | here |
| Assessor, Auditor, Clerk, Prosecutor (short and full), Sheriff, Treasurer | 6 | 0 | 6 | `COUNTY` | here (info-only) |
| District Court Judge | 1 | 0 | 1 | `COUNTY` | here (info-only) |
| Court of Appeals Div. III, Dist. 2, Pos. 1 | 1 | 0 | 1 | `COUNTY` | here (info-only copy, as the other District 2 counties) |

**Columbia County is in LD 9, not LD 16.** VoteWA's general export, the
sample ballot ("Legislative District 09") and the Census geocoder
(`2026 State Legislative Districts - Lower/Upper` = `9` at every probe
below) agree. No LD 9 Senate seat is on the 2026 ballot. The research plan
names CD 5 and LD 9 Pos. 2 `researched_in` Spokane with no
`candidates_missing`; LD 9 Pos. 1 is uncontested, so it is not in the plan,
and Spokane's package has an info-only scoring file for it
(`spokane-legislative-district-9-state-representative-pos-1.json`). No
legislative or congressional seat on Columbia's ballot lacks an owner.

Carried forward from the primary package (dossiers rewritten from new
sources, scores redone under the general's rubric): Commissioner No. 3, both
finalists (Warren, Miller). The primary's dossiers were filing-level for
Warren and thin for Miller. New since the primary: the District Court and
Court of Appeals seats (not on the primary ballot) and the info-only
entries for the six uncontested county offices.

Measures (VoteWA guide records 7423 and 7379):

- Columbia County Park and Recreation Pool District Proposition No. 1,
  operation excess levy, $200,000 for 2027 (about $0.20 per $1,000):
  `PARKDST` `CPR`. Pamphlet PDF p. 10.
- Prescott Joint Park and Recreation District Proposition No. 1,
  maintenance and operation excess levy, $175,000 for 2027 (about $0.35 per
  $1,000): `PARKDST` `PRES`. Pamphlet PDF p. 11. **The same measure (guide
  record 7379) is in Walla Walla County's shipped package**, scoped
  `PARKDST` `PRES` there too. Each copy carries its own county in its scope
  (`{"county": "walla-walla", ...}` vs `{"county": "columbia", ...}`), so a
  voter sees only their own county's copy, as with McCleary SD 65
  (Grays Harbor/Mason). Walla Walla's copy cannot reach Columbia voters, so
  Columbia carries its own. Both map `taxes` +2. Columbia's dossier adds the
  Columbia County share of the 2025 vote (3 yes, 1 no; SOS export), which
  Walla Walla's dossier lists as not found.

## District scoping

- **Commissioner No. 3: county-wide in the general.** Columbia is a
  non-charter county with three commissioners, nominated by district in the
  primary and elected county-wide in the general (RCW 36.32.040,
  36.32.050(1)). Evidence:
  - VoteWA's general export lists the race as District Type `Countywide`,
    District `County`.
  - The 2026 primary race drew 417 votes (Warren 215, Miller 198, write-in
    4) against about 1,050 in the county-wide races (Assessor 1,049, Auditor
    1,050) (`raw/columbia/votewa-2026-08-04-primary-results.json.url`).
  - SOS precinct exports: the 2022 Commissioner #3 race and the 2024 #1 and
    #2 races are on all 13 voting precincts, the same 13 as Sheriff (2022)
    and Governor (2024) (`raw/columbia/sos-results-20221108-*.url`,
    `raw/columbia/sos-results-20241105-*.url`).
  - The Union-Bulletin (2026-08-04): "Only voters in District 3 of Columbia
    County were able to vote for this race in the primary. However, the
    whole county will be able to vote in the general election in November."

  Scope `COUNTY`. The override keeps the primary's contest name, so the slug
  `columbia-columbia-county-commissioner-district-3-columbia-county-commissioner-no-3`
  and the primary dossiers carry forward. `COUNTY_COUNCIL` is not needed in
  the general (the archived primary uses it).
- **District Court**: one county-wide district court judge (2022 race on all
  13 precincts). VoteWA files it as District Type `Judicial`, District
  `Court District`; the override names it `Columbia County District Court` /
  `District Court Judge`, category `Judicial`.
- **Court of Appeals Div. III, Dist. 2, Pos. 1**: the generic rule scopes it
  `COUNTY` (whole-county electorate; RCW 2.06.020); shipped info-only.
- **No PUD, port, fire, hospital, library, cemetery, EMS or school race or
  measure.** WA DOR PUD2025 (17) has no Columbia polygon; PRT2025 (16) and
  HSP2025 (11) have one county-wide `COLUMBIA` polygon each; LIB2025 (12)
  `RL` covers the county outside the Town of Starbuck; none has a 2026
  contest or measure.

## Layers each scope needs (probed 2026-10-08)

Addresses geocoded with the Census geocoder
(`geocoding.geo.census.gov/geocoder/geographies/onelineaddress`,
`Public_AR_Current`, vintage `Current_Current`) and point-queried with
`?geometry=<x>,<y>&geometryType=esriGeometryPoint&inSR=4326&spatialRel=esriSpatialRelIntersects&outFields=...&returnGeometry=false&f=json`.
`DOR` = `https://webgis.dor.wa.gov/arcgis/rest/services/Programs/WADOR_PropertyTax/MapServer`.
`COMM` = `https://services9.arcgis.com/zq1Ay6bxXC1T1CBk/arcgis/rest/services/CommissionerDistricts/FeatureServer/0`
(`District`), the layer `COUNTY_LAYERS.columbia` reads; re-probed alive
(metadata and every point query answered).

| Point | Census place | CD / LD | DOR PKR2025 (14) | DOR SCH2025 (20) | DOR FIR2025 (7) | DOR LIB2025 (12) | `COMM` `District` |
|---|---|---|---|---|---|---|---|
| 341 E Main St, Dayton 99328 (-117.97830, 46.32082) | Dayton | 5 / 9 | `CPR` | `2` | `3` | `RL` | `2` |
| 650 Wagon Rd, Dayton 99328 (-117.99663, 46.31160) | none | 5 / 9 | `CPR` | `2` | `3` | `RL` | `3` |
| 100 Hogeye Hollow Rd, Dayton 99328 (-117.99145, 46.26394) | none | 5 / 9 | `CPR` | `2` | `3` | `RL` | `3` |
| 101 Main St, Starbuck 99359 (-118.12764, 46.51784) | Starbuck | 5 / 9 | none | `35` | none | none | `3` |
| 401 Main St, Starbuck 99359 (-118.12772, 46.52088) | Starbuck | 5 / 9 | none | `35` | none | none | `3` |
| interior point (-118.21, 46.40), Prescott district | n/a | n/a | `PRES` | `37` | `2` | `RL` | `3` |
| interior point (-118.20, 46.45), rural Starbuck SD | n/a | n/a | `CPR` | `35` | `1` | `RL` | `3` |
| interior point (-117.75, 46.45), Tucannon | n/a | n/a | `CPR` | `2` | `3` | `RL` | `2` |
| interior point (-117.80, 46.10), Blue Mountains | n/a | n/a | `CPR` | `2` | none | `RL` | `2` |

(CD/LD from the geocoder's geographies for the five street addresses;
interior points have no geocoder result.)

- `CONGDST`, `LEGDST`: Census layers; every contest above resolves.
- `COUNTY`: no layer.
- `PARKDST` `CPR` (Pool District) and `PRES` (Prescott, Columbia part): WA
  DOR PKR2025, layer 14, attribute `DISTATTRIB`. Columbia County has exactly
  two polygons (`where COUNTYNAME='COLUMBIA'`): `CPR` and `PRES`; they do not
  overlap (each probe returns one feature). `CPR` matches the district's
  legal description (county minus the Town of Starbuck and the Prescott
  district): no feature in the Town of Starbuck, consistent with the 2024
  pool levy appearing on every precinct but STARBUCK CITY. The `PRES`
  polygon is the county's western strip (bbox -118.242..-118.179,
  46.331..46.500), matching SOS results that put the Prescott levy only on
  the ALTO and STARBUCK COUNTRY precinct parts. `PRES` is also Walla Walla's
  value for the same district; the scope's county keeps the copies apart. No
  Columbia street address inside `PRES` geocoded, so its check is the
  interior point (-118.21, 46.40).

### Layers to add at ship time

```js
columbia: [
  { key: 'COUNTY_COUNCIL', url: 'https://services9.arcgis.com/zq1Ay6bxXC1T1CBk/arcgis/rest/services/CommissionerDistricts/FeatureServer/0/query', attr: 'District' },
  // WA DOR PKR2025: 'CPR' Columbia County Park and Recreation Pool District
  // (341 E Main St, Dayton), 'PRES' Prescott Joint P&R District, Columbia part
  // (interior point -118.21, 46.40); no feature in the Town of Starbuck.
  { key: 'PARKDST', url: `${DOR_TAX_DISTRICTS}/14/query`, attr: 'DISTATTRIB' },
],
```

and `election.DISTRICT_ADAPTER_LAYERS["columbia"]` = `CONGDST`, `LEGDST`,
`CITY`, `COUNTY_COUNCIL`, `PARKDST`. Without `PARKDST` the assembler would
mark the county `partial_county` for both measures. `districts.js` has no
`PARKDST` labels for `CPR` or `PRES` (nor for Walla Walla's `PRES`/`WAIT`);
the ship pass may add `CPR: 'Columbia County Park and Recreation Pool
District'` and `PRES: 'Prescott Joint Park and Recreation District'`.

### Suggested live checks

- 341 E Main St, Dayton, WA 99328: CD 5, LD 9, `COUNTY_COUNCIL` `2`,
  `PARKDST` `CPR`; expect the Pool District levy, not the Prescott levy.
- 101 Main St, Starbuck, WA 99359: Census place Starbuck, no `PARKDST`;
  expect neither measure.
- 650 Wagon Rd, Dayton, WA 99328 (unincorporated): `COUNTY_COUNCIL` `3`,
  `PARKDST` `CPR`; expect the Pool District levy.
- Prescott district: no geocodable address; check `PRES` by a direct point
  query at (-118.21, 46.40) or a coordinates-based `lookupBallotContext`.

Every address should show all 10 county-owned contests (six county offices,
Commissioner No. 3, District Court, Court of Appeals), CD 5 and LD 9 Pos. 2
with Spokane's scoring, and LD 9 Pos. 1 with Spokane's info-only entry.

## Sources

Candidate and measure records can carry `local-voters-pamphlet` PDF pages
(above). The general pamphlet PDF is
`https://www.columbiaco.com/DocumentCenter/View/8822` (redirects to
`.../8822/2026_General_New_Covers_LVP_?bidId=`; 200, application/pdf,
1,149,871 bytes, sha256 3297fad3... on 2026-10-08). The Court of Appeals
entry cites VoteWA's guide (the local pamphlet does not print it). Local
news is the Walla Walla Union-Bulletin, whose site search
(`/search/?q=...&t=article`) and story pages are readable by script. Web
search was unavailable to this research session, so sources were found by
direct fetches (Union-Bulletin search, PDC open data, SOS exports, county
site); the Dayton Chronicle was not searched. wwcc.edu answered 403 to
scripts, so Warren's trusteeship rests on the pamphlet and the
Union-Bulletin.

## Known gaps

- Sheriff Joe Helm submitted no 2026 statement; his entry rests on 2022
  coverage and results.
- Auditor: the 2022 general elected Anne D. Higgins (unopposed); Hutchens
  lists himself as auditor from 2023. How he took office (appointment) was
  not confirmed in a source.
- Jack Miller's mailing address differs between VoteWA (PO Box 95, Dayton)
  and the pamphlet/PDC (632 Lower Hogeye Rd, Waitsburg; the pamphlet prints
  ZIP 99361 on p. 4 and 99328 on p. 7). He lives in unincorporated Columbia
  County (Union-Bulletin).
- The 2016 Ecology water-rights settlement is attributed to the candidate
  by identity match (Bill Warren, operator of Warren Orchards on the Touchet
  River near Dayton; the candidate describes himself as a Columbia County
  orchardist), not by an explicit link in the article.
- The Pool District's argument for spells "lnnovia Foundation" (Innovia).
