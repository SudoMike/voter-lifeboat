# Jefferson County Completeness Note

Election: 2026 Washington general election, November 3, 2026 (VoteWA
election 899, county code 16).

Research package for #31 (county wave 6); not yet declared in
`APP_PACKAGES`. Contests and measures are built by
`pipeline/build_votewa_lite_data.py --county jefferson` from the VoteWA
candidate list (`raw/votewa/candidate-list.csv.url`, 28 rows) and the
overrides and measures in that script's
`ELECTION_MEASURES["2026-11-03-general"]["jefferson"]`, checked against the
Jefferson County Auditor's Local Voters' Pamphlet
(`raw/jefferson/local-voters-pamphlet.pdf.url`, text in
`interim/pdf-text/local-voters-pamphlet.txt`; it "contains all races and
issues in this election"), the sample ballot
(`raw/jefferson/sample-ballot.pdf.url`; page 1 is an image, page 2 has
text) and VoteWA's online voters' guide for the county
(`https://voter.votewa.gov/genericvoterguide.aspx?e=899&c=16`; records under
`raw/votewa/voter-guide/`, text in `interim/voter-guide-text/`). All three
agree contest for contest. The Elections page
(`https://www.co.jefferson.wa.us/1266/Elections`, HTTP 200 on 2026-10-08,
`raw/jefferson/elections.html.url`) links the pamphlet
(`DocumentCenter/View/25551`), the sample ballot (`/25497`) and the two
measure resolutions (`/25266`, `/25264`; scanned images, no text).

The builder reports `full_county`. The assembler will mark the county
`partial_county` until `COUNTY_LAYERS.jefferson` reads `SCHDST` (proposed
below); `COUNTY_COUNCIL` in `geo.js` points at a dead host (below), but no
general contest uses it.

## What is on the ballot

13 contests (5 contested, 8 uncontested) and 2 local measures. The five
Supreme Court contests and the three statewide initiatives are dropped by
the builder and ship from the statewide package.

| Kind | Contests | Contested | Uncontested | Scope | Researched |
|---|---|---|---|---|---|
| U.S. Representative (CD 6) | 1 | 1 | 0 | `CONGDST` `6` | Pierce package |
| LD 24 Rep. Pos. 1, Pos. 2 | 2 | 2 | 0 | `LEGDST` `24` | Clallam package |
| County Commissioner District 3 | 1 | 1 | 0 | `COUNTY` | here (carried from the primary, re-researched) |
| Assessor, Auditor, Clerk, Prosecutor, Sheriff, Treasurer | 6 | 0 | 6 | `COUNTY` | here (info-only) |
| District Court Judge Position No. 1 | 1 | 0 | 1 | `COUNTY` | here (info-only) |
| Court of Appeals Div. II, Dist. 2, Pos. 1 | 1 | 0 | 1 | `COUNTY` | another package's info-only file (Clallam, Grays Harbor, Kitsap and Thurston each have one) |
| PUD No. 1 Commissioner District 2 | 1 | 1 | 0 | `COUNTY` | here (no applicable axis) |

All of Jefferson County is in LD 24 and CD 6. There is no LD 24 Senate race
in 2026. No port, hospital, fire commissioner or Superior Court seat is on
the general ballot. The research plan lists CD 6 as researched in Pierce
(`candidates_missing` empty) and LD 24 Pos. 1 and Pos. 2 as researched in
Clallam (`candidates_missing` empty); no legislative seat lacks an owner.

Measures (VoteWA guide records 7296, 7292; pamphlet pp. 14-15). Both belong
to districts based in Clallam County whose edge reaches Jefferson's West End;
Clallam's package ships its own copies, scoped to Clallam:

- Quillayute Valley School District No. 402 Proposition No. 1, $34 million
  bonds to rebuild Forks Middle School: `SCHDST` `402`.
- Clallam County Fire Protection District No. 1 Proposition No. 1, levy lid
  lift to $1.00 per $1,000 with a nine-year CPI escalator: `FIRDST` `9`.

No Jefferson-based district has a measure on this ballot (the parks levy and
the Quilcene and Brinnon fire and cemetery measures were decided in the
August primary).

## District scoping

- Jefferson County is not a charter county. Commissioner District 3 is
  nominated by district in the primary (13 of 37 precincts voted in it on
  August 4) and elected county-wide in the general (RCW 36.32.040). VoteWA's
  general export lists it as `Countywide` / `County` / `District 3`. In the
  SOS precinct exports the 2022 District 3 race is on all 37 precincts and
  the 2020 and 2024 District 1 and 2 races on all 39 and 37
  (`raw/jefferson/sos-results-*.csv.url`). Scope `COUNTY`; the override keeps
  the primary's names, so the slug
  (`jefferson-jefferson-county-commissioner-district-3-district-3`) matches
  the primary's.
- District Court: one county-wide judge (2022 SOS export: Position No. 1 on
  all 37 precincts). Override names it `Jefferson County District Court`,
  category `Judicial`.
- Public Utility District No. 1 of Jefferson County covers the whole county,
  Port Townsend included: WA DOR PUD2025 (layer 17) has one Jefferson
  polygon, `DISTATTRIB` `1`, whose area (12,473,615,980) equals the sum of
  Jefferson's seven SCH2025 polygons, and it answers `1` at every probe
  address below. Its seats are nominated by district and elected PUD-wide in
  the general (RCW 54.12.010(3); the 2020 District 2, 2022 District 1 and
  2024 District 3 races are on every precinct in the SOS exports; Kisler's
  site: "All of Jefferson County can vote for Keith this November"). Scope
  `COUNTY`, as Clark's, Kitsap's and Thurston's. The override names it
  `Public Utility District No. 1 of Jefferson County`, so no other package's
  PUD seat matches the `NAMED` key.
- Court of Appeals Div. II, Dist. 2, Pos. 1: `COUNTY` (generic rule);
  Jefferson is one of six counties in the district. Its `NAMED` key matches
  Clallam's, Grays Harbor's, Kitsap's and Thurston's info-only files, so assembly ships
  the first owning package's; no Jefferson copy was written.
- Quillayute Valley SD 402: DOR SCH2025 (layer 20) has a Jefferson polygon
  `402` (1,662,018,782 of Jefferson's 12,473,615,980), in the West End
  near Forks. DOR's 2025 levy detail has Jefferson rows `Quillayute
  #402 Bond` and `Enrichment` ($27,344,159 assessed value). The county's
  own FindMyDistricts layer 8 returns `SD402` / "Quillayute Valley School
  District No. 402" at the same points.
- Clallam County FPD 1: DOR's Clallam FIR2025 polygon `1` stops at the
  county line; DOR numbers the Jefferson part `9` in FIR2025 (layer 7,
  Jefferson polygon `9`) and in its levy detail (`160700900 Fire Dist #9`,
  $5,659,457 assessed value, $0.47059 per $1,000, the same rate as Clallam's
  Fire Dist #1). The county's FindMyDistricts layer 10 feature `CCFD1`
  ("Clallam County Fire District No. 1") covers the same area: of 8,621
  grid points inside DOR's Jefferson `9`, 8,613 fall inside `CCFD1`. The
  Jefferson Elections page calls it "Clallam/Jefferson County Fire District
  No. 1". Jefferson's own Fire District 1 (East Jefferson Fire Rescue) is
  `1` in the same layer, so the measure must not be scoped `1`.

## Layers

`app/src/lib/geo.js` `COUNTY_LAYERS.jefferson` today: `COUNTY_COUNCIL`
(`gisweb.jeffcowa.us/server/rest/services/OpenData/OpenData/MapServer/26`,
`DISTID`), `CEMDST` (DOR 3) and `FIRDST` (DOR 7).

The general needs only `FIRDST` (already read) and `SCHDST` (to add):

```js
{ key: 'SCHDST', url: `${DOR_TAX_DISTRICTS}/20/query`, attr: 'DISTATTRIB' },
```

### Commissioner layer: dead host, replacement found

`gisweb.jeffcowa.us` answered HTTP 503 ("Service Unavailable") again on
2026-10-08, both `OpenData/MapServer/26?f=json`, the services root and a
point query; the ArcGIS Online item for "Commissioner Districts"
(`c243816b49e74e12b97847fda1c81dc8`) still points at it. No general
contest needs commissioner districts (District 3 is elected county-wide),
but the archived primary scopes its District 3 race `COUNTY_COUNCIL` `3`.

Replacement: the county's own hosted copy of its district layers,
`FindMyDistrictsInstantApp_WFL1` (ArcGIS Online org `RPU019D0wA2T8GMO`, item
`efd697c7eaaa4852b772601e27502480`, "Voting Precincts and Districts in
Jefferson County, WA", public, modified 2026-06-04;
`raw/jefferson/gis-findmydistricts-*.json.url`). Layer 1 "County
Commissioners" has three features with `DISTID` `1`, `2`, `3`, the same
attribute and values the primary uses:

```js
{ key: 'COUNTY_COUNCIL', url: 'https://services3.arcgis.com/RPU019D0wA2T8GMO/arcgis/rest/services/FindMyDistrictsInstantApp_WFL1/FeatureServer/1/query', attr: 'DISTID' },
```

Its layer 0 (Voting Precincts) carries the commissioner district per
precinct (`DISTRICTID`) and agrees at every probe. (Layer 21, "PUD
Commissioners", is a copy of the county commissioner features, county
commissioners' names included; not used.)

### Point queries (2026-10-08, Census geocoder `Public_AR_Current`)

| Address | Precinct (layer 0) | Comm. (hosted 1) | gisweb 26 | DOR FIR (7) | County fire (10) | DOR CEM (3) | DOR SCH (20) | DOR PUD (17) |
|---|---|---|---|---|---|---|---|---|
| 1820 Jefferson St, Port Townsend | 1111 Port Townsend XI | `1` | 503 | `1` | FD1 | none | `50` | `1` |
| 620 Cedar Ave, Port Hadlock | 2305 Port Hadlock | `2` | 503 | `1` | FD1 | none | `49` | `1` |
| 294715 US Hwy 101, Quilcene | 3701 Quilcene | `3` | 503 | `2` | FD2 | `2` | `48` | `1` |
| 272 Schoolhouse Rd, Brinnon | 3801 Brinnon I | `3` | 503 | `4` | FD4 | `1` | `46` | `1` |
| 9500 Oak Bay Rd, Port Ludlow | 3601 Port Ludlow I | `3` | 503 | `1` | FD1 | none | `49` | `1` |
| 1993 Dowans Creek Rd, Forks | 3901 West End | `3` | 503 | `9` | CCFD1 | none | `402` | `1` |
| 18113 Upper Hoh Rd, Forks | 3901 West End | `3` | 503 | none | none | none | `402` | `1` |

Suggested live checks once `SCHDST` is added: 1820 Jefferson St, Port
Townsend (county races, PUD seat, no local measure); 1993 Dowans Creek Rd,
Forks (both West End measures); 18113 Upper Hoh Rd, Forks (Quillayute bond
only).

## Sources

The county prints a local voters' pamphlet whose PDF pages equal its printed
page numbers; dossiers cite it as `local-voters-pamphlet page N` (Assessor
and Auditor 6, Clerk 7, Commissioner 8, Prosecutor and Sheriff 9, Treasurer
10, District Court 11, PUD 12, measures 14 and 15). Local news is the Port
Townsend Leader (ptleader.com; most stories are paywalled after the lead,
and only readable text was cited) and the Peninsula Daily News; the Forks
Forum covers the West End measures.

## Known gaps

- Michael Brittain's campaign site (mike4pud.com) refuses scripted
  downloads (HTTP 403); it was read through WebFetch, which keeps no
  verbatim copy, so its pointer has no sha256.
- The measure resolutions posted by the county are scanned images; facts
  that depend on them (60% validation) are cited to the state constitution
  instead. Clallam's package read its own copies by OCR.
- The Port Townsend Leader's stories on the September 30 forum and on the
  candidates' filings are paywalled past the lead.
- Uncontested Assessor, Auditor, Clerk, Prosecutor, Treasurer and District
  Court candidates are pamphlet-only. A write-in sheriff candidate (Crystal
  L. Cox) is registered with the PDC.
- The primary's Jefferson dossiers were one-line summaries of the pamphlet;
  nothing from them was carried forward unverified.
