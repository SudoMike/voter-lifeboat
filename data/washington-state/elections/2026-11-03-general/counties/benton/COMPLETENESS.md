# Benton County Completeness Note

Election: 2026 Washington general election, November 3, 2026 (VoteWA
election 899, county code 03).

Shipped (#28): the package is declared in
`APP_PACKAGES["2026-11-03-general"]["counties"]` and ships at Full County
Coverage, with the elections office link
`https://www.bentoncountywa.gov/government/elected_officials/auditor/elections/index.php`
and the county's VoteWA guide (`officialLinks.js` `countyGuides.benton`).
Contests and measures are built by
`pipeline/build_votewa_lite_data.py --county benton` from the VoteWA
candidate list (`raw/votewa/candidate-list.csv.url`) and the measures curated
in that script's `ELECTION_MEASURES` block, checked against the Benton County
Auditor's general sample ballot (`raw/benton/sample-ballot.pdf.url`, text in
`interim/pdf-text/sample-ballot.txt`).

## What is on the ballot

27 contests (13 contested, 14 uncontested) and 3 measures, matching the
sample ballot. The five Supreme Court contests and the three statewide
initiatives are dropped by the builder and ship from the statewide package.

| Kind | Contests | Contested | Uncontested | Scope | Researched |
|---|---|---|---|---|---|
| U.S. Representative (CD 4) | 1 | 1 | 0 | `CONGDST` | here |
| LD 8 Senate, Rep. Pos. 1, Pos. 2 | 3 | 1 | 2 | `LEGDST` | here (Pos. 1, 2 info-only) |
| LD 16 Rep. Pos. 1, Pos. 2 | 2 | 2 | 0 | `LEGDST` | here |
| LD 14 Rep. Pos. 1, Pos. 2; LD 15 Senate, Rep. Pos. 1, Pos. 2 | 5 | 4 | 1 | `LEGDST` | Yakima package; the four House seats ship with Yakima's scoring and dossiers |
| Assessor, Auditor, Clerk, Coroner, Prosecuting Attorney, Sheriff, Treasurer | 7 | 2 | 5 | countywide | here |
| County Commissioner District #2 | 1 | 0 | 1 | countywide | here (info-only) |
| District Court Judge 1 to 5 | 5 | 1 | 4 | countywide | here |
| Court of Appeals, Div. 3, Dist. 2, Judge Pos. 1 | 1 | 0 | 1 | countywide | here (info-only) |
| Benton County PUD Commissioner Pos. 2 | 1 | 1 | 0 | `PUDDST` `Benton PUD` | here (no applicable axis) |
| City of Richland Council Pos. 4 | 1 | 1 | 0 | `CITY` `Richland` | here |

Measures: City of Benton City Propositions 1 (council-manager form of
government) and 2 (community safety levy lid lift), `CITY` `Benton City`;
Kiona-Benton City School District No. 52 Proposition 1 (EP&O replacement
levy), `SCHDST` `52`.

## Sources

Benton County publishes its general voters' pamphlet only as VoteWA's online
guide (`https://voter.votewa.gov/genericvoterguide.aspx?e=899&c=03`, linked
from the Auditor's Current Election page). Its race and measure records are
pointed to under `raw/votewa/voter-guide/` and their text is in
`interim/voter-guide-text/`. Those citations carry no page numbers, so, as
for Spokane, the county's records would ship no `pamphlet_pages`; the app
would link the guide through `officialLinks.js` `countyGuides`.

## District scoping

- Commissioner District #2: nominated by district in the primary (VoteWA
  primary District Type `Commissioner`), elected county-wide in the general
  (RCW 36.32.040; VoteWA's general export lists it as `Countywide`). Scope
  `COUNTY`.
- District Court and Court of Appeals Div. 3 Dist. 2: county-wide.
- Benton County PUD: nominated by commissioner district, elected by the
  whole PUD (RCW 54.12.010(3)). The PUD is not the whole county: Richland
  and most of West Richland are in none of its districts. The DOR PUD2025
  layer (17) has one county-wide Benton polygon and is not an electoral
  boundary. The Benton County Auditor's precinct layer
  `https://services7.arcgis.com/NURlY7V8UHl6XumF/arcgis/rest/services/PrecinctSplits/FeatureServer/6`
  carries `PUD_District` = `Benton PUD` on exactly the precincts that voted
  in the 2024 Benton PUD race (SOS 20241105 Benton precinct export), except
  precinct 4017 (West Richland), coded `Yes` with no 2024 PUD vote
  (`raw/benton/gis-precinct-splits-pud.json.url`). Point queries
  2026-10-08: 210 W 6th Ave, Kennewick and 1009 Dale Ave, Benton City
  `Benton PUD`; 625 Swift Blvd, Richland and 3801 W Van Giesen St, West
  Richland null. The race is scoped `PUDDST` `Benton PUD`.
- Ki-Be SD 52: WA DOR SCH2025 (layer 20) `DISTATTRIB` `52` at 1009 Dale
  Ave, Benton City; the PrecinctSplits layer agrees there (`SchoolDistrict`
  `Kiona-Benton City School District 52`).
- Benton City: Census incorporated place `Benton City` at 1009 Dale Ave.

`app/src/lib/geo.js` `COUNTY_LAYERS.benton` reads both (#28): `PUDDST`
from PrecinctSplits layer 6, `PUD_District`, with `where PUD_District =
'Benton PUD'`, and `SCHDST` from DOR SCH2025 (layer 20) `DISTATTRIB`. Live
2026-10-08: Kennewick and Benton City `Benton PUD`, Richland and West
Richland no feature; Benton City `52`, Kennewick `17`, Richland `400`.

Known layer issue: precinct 4017 (West Richland, `PrecinctName` WR17) is
coded `PUD_District` `Yes`, not `Benton PUD`, and cast no 2024 PUD vote.
The `where` filter makes it read as no PUD district, so its voters do not
see the PUD race; if 4017 is in fact inside the PUD, that is a missing
race there, not a wrong one. Richland precinct 6322.1 reads the string
`<Null>`, which the filter also drops.

`Benton City` is the Census place `BASENAME`. Until #28 `geo.js` stripped a
trailing "City" from it (CITY `Benton`), which hid both Benton City
propositions; it now strips the suffix from `NAME` only.

## Known gaps

- District Court categories: the generic VoteWA rules give the District
  Court contests category `County` (District Type `Countywide`). The
  scoring follows the judicial rules (only `judicial`, `safety`,
  `experience`), and `validate_scoring.py` treats them as judicial by slug.
  The category is display-only and ships as is; Whatcom's merge added an
  `overrides` hook to `ELECTION_MEASURES` that could rename them later.
- The Tri-City Herald blocked scripted and WebFetch access; its coverage
  appears only through reprints or not at all. The research session's web
  search quota ran out, so sources were found by direct fetches.
- LD 14 and LD 15 House seats are researched by Yakima's package; the
  rebuilt plan names them `researched_in` yakima with no
  `candidates_missing`. Yakima's CD 4 ships with this package's scoring.
