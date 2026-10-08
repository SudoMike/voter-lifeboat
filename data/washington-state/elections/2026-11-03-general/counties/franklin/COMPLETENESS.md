# Franklin County Completeness Note

Election: 2026 Washington general election, November 3, 2026 (VoteWA
election 899, county code 11).

Status: shipped (#29) at Full County Coverage in
`APP_PACKAGES["2026-11-03-general"]["counties"]`, with its elections office
(`https://www.franklincountywa.gov/Elections`), its local pamphlet in
`officialLinks.js` `pamphletPdfs['franklin/local-voters-pamphlet']` and its
VoteWA guide (`countyGuides.franklin`, `c=11`). `COUNTY_LAYERS.franklin`
reads `COUNTY_COUNCIL` (portal `Commissioner_Districts/MapServer/0`, since
the 2026-10-09 hotfix), `PORTDST` (`Special_tax_districts/MapServer/7`) and
`FIRDST` (DOR FIR2025), as proposed below. Live ballots on 2026-10-08: 525 N
3rd Ave, Pasco (CD 4, LD 14, COM2, PoP1; no port race, no measure); 5600 N
Rd 68, Pasco (LD 16, COM3, PoP3, FIR '3': the commissioner and port races
and the FPD 3 levy); 104 E Adams St, Connell (CD 5, LD 16, PoP3); 2108 N Rd
84, Pasco (LD 8, COM1, PoP2); 103 Franklin St, Mesa (CD 5, PoP3); each
`full_county` with no missing layer.

Contests and measures are built by
`pipeline/build_votewa_lite_data.py --county franklin` from the VoteWA
candidate list (`raw/votewa/candidate-list.csv.url`) and the Franklin block of
that script's `ELECTION_MEASURES` (overrides and the one local measure). The
ballot was checked against the Franklin County Auditor's general sample ballot
(`raw/franklin/sample-ballot.pdf.url`, text in
`interim/pdf-text/sample-ballot.txt`) and the county's printed Official Local
Voters' Pamphlet (`raw/franklin/local-voters-pamphlet.pdf.url`, 16 PDF pages,
printed pages 43-58, text in `interim/pdf-text/local-voters-pamphlet.txt`).

## What is on the ballot

21 contests (11 contested, 10 uncontested) and 1 measure, matching the sample
ballot. The five Supreme Court contests and the three statewide initiatives
are dropped by the builder and ship from the statewide package.

| Kind | Contests | Contested | Uncontested | Scope | Researched |
|---|---|---|---|---|---|
| U.S. Representative CD 4, CD 5 | 2 | 2 | 0 | `CONGDST` | Benton (CD 4), Spokane (CD 5) |
| LD 8 Senate, Rep. Pos. 1, Pos. 2 | 3 | 1 | 2 | `LEGDST` | Benton (Senate scored; Pos. 1, 2 info-only) |
| LD 14 Rep. Pos. 1, Pos. 2 | 2 | 2 | 0 | `LEGDST` | Yakima |
| LD 16 Rep. Pos. 1, Pos. 2 | 2 | 2 | 0 | `LEGDST` | Benton |
| Assessor, Sheriff | 2 | 2 | 0 | countywide | here |
| Auditor, Clerk, Coroner, Prosecuting Attorney, Treasurer | 5 | 0 | 5 | countywide | here (info-only) |
| County Commissioner District 3 | 1 | 1 | 0 | `COUNTY_COUNCIL` `COM3` | here |
| District Court Judge | 1 | 1 | 0 | countywide | here |
| Court of Appeals, Div. 3, Dist. 2, Judge Pos. 1 | 1 | 0 | 1 | countywide | Benton (info-only) |
| Franklin PUD No. 1 Commissioner District 2 | 1 | 0 | 1 | countywide | here (info-only) |
| Port of Pasco Commissioner District 3 | 1 | 0 | 1 | `PORTDST` `PoP3` | here (info-only) |

The legislative and congressional races, LD 8 Pos. 1 and Pos. 2 and the Court
of Appeals seat are the same races other packages list. `shared_contests`
matches them, and assembly ships the owning package's scoring and dossiers.
There are no copies here. The rebuilt plan shows `candidates_missing: []` for
all seven contested shared races. No LD 9 seat is on Franklin's 2026 ballot.

Measure: Franklin County Fire Protection District No. 3 Proposition No. 1
(single-year permanent levy lid lift to $1.24 per $1,000), `FIRDST` `3`.

## District scoping

- **Commissioner District 3: elected by district.** VoteWA's District is
  `COUNTY COMMISSION DISTRICT 3`, not `... ALL COUNTY`. In the 2024 general
  (SOS precinct export, `raw/franklin/sos-results-2024-general-precincts.csv.url`)
  District 1 was on 48 precincts and District 2 on 31, against 123 for
  county-wide races. In 2022 District 3 was still on every precinct
  (`raw/franklin/sos-results-2022-general-precincts.csv.url`). The 2026
  District 3 primary was counted in 44 of 123 reporting units
  (`raw/franklin/votewa-2026-08-04-primary-results.json.url`). RCW
  36.32.040(3) lets a county change its system under the Voting Rights Act.
  The districts are from Resolution 2022-082. Scope `COUNTY_COUNCIL` `COM3`,
  the generic rule (`COUNTY_CONFIG.franklin.commissioner` = `COM{n}`).
- **Franklin PUD No. 1: the whole county, elected PUD-wide.** The county's PUD
  layer (`Special_tax_districts/MapServer/6`: PUD1-PUD3) covers the county. The
  2024 PUD District 3 general was on all 123 precincts, as were 2022 District 1
  and 2020 District 2. DOR PUD2025 (layer 17) has no Franklin polygon. Override
  to `COUNTY` (RCW 54.12.010(3)), as for Clark, Kitsap and Thurston.
- **Port of Pasco: not the whole county, and by district from 2026.** The
  Port of Kahlotus covers the east end (DOR PRT2025 layer 16: one `PASCO` and
  one `KAHLOTUS` polygon; 2025 port races: precinct 097 only in Kahlotus, 095
  and 096 split). The Port of Pasco moved to by-district primaries and
  generals, first used in 2026 (NonStop Local, 2025-10-03,
  `raw/franklin/nonstop-2025-10-03-port-by-district.html.url`). The pamphlet
  and sample ballot say "Port of Pasco, Commissioner District 3". The county
  layer `Special_tax_districts/MapServer/7` has `DISTRICT_CODE` `PoP1`/`PoP2`/
  `PoP3` (Port Resolution 1577) and `PoK1`-`PoK3`. Override to `PORTDST`
  `PoP3`. A port-wide scope would show the race to voters who cannot vote in it.
- **District Court and Court of Appeals:** county-wide. The District Court
  seat is renamed by override to category `Judicial`, district "Franklin County
  District Court", office "Judge" (the slug is unchanged).
- **FPD 3:** WA DOR FIR2025 (layer 7) `DISTATTRIB` `3`.

Point queries 2026-10-08 (Census geocoder, Current vintage):

| Address | Commissioner (`Commissioner_Districts/0`) | Port (`Special_tax_districts/7`) | PUD (`/6`) | DOR FIR2025 | Precinct-split layer |
|---|---|---|---|---|---|
| 1016 N 4th Ave, Pasco (courthouse) | COM2 | PoP1 | PUD3 | none | Precinct 006: COM2, POP1, PUD3, PFD, PASCO |
| 5600 N Rd 68, Pasco (unincorporated) | COM3 | PoP3 | PUD2 | `3` | Precinct 071: COM3, PoP3, PUD2, FPD3 |
| 6600 Burden Blvd, Pasco (HAPO Center) | COM3 | PoP2 | PUD1 | none | Precinct 039: COM3, POP2, PUD3, PFD |
| 103 Franklin St, Mesa | COM2 | PoP3 | PUD2 | none | Precinct 084: COM2, PoP3, PUD2 |
| 104 E Adams St, Connell | COM2 | PoP3 | PUD2 | none | Precinct 092: COM2, PoP3, PUD2, CFD |
| 2108 N Rd 84, Pasco | COM1 | PoP2 | PUD1 | none | Precinct 049: COM1, POP2, PUD3, PFD |

The county's PUD commissioner polygons and the precinct layer's `PUD` attribute
disagree at three addresses. That does not matter here because the PUD seat is
scoped `COUNTY`.

## District Adapter (action for the director)

`app/src/lib/geo.js` `COUNTY_LAYERS.franklin` has one entry, `COUNTY_COUNCIL`
from
`https://services3.arcgis.com/S61OMZovc3AIomN2/arcgis/rest/services/Districts/FeatureServer/8`
(`DISTRICT_CODE`). On 2026-10-08 that service answered `{"error":{"code":400,
"message":"Invalid URL"}}`. The org's only remaining service is
`FCID_boundary`. So today every Franklin address would get `missingLayers:
['COUNTY_COUNCIL']`, and the archived primary's Franklin commissioner contest
is affected too. Proposed `COUNTY_LAYERS.franklin`, all live on 2026-10-08
with CORS (`Access-Control-Allow-Origin` echoed):

```js
franklin: [
  { key: 'COUNTY_COUNCIL', url: 'https://gisportal.franklin.co.franklin.wa.us/arcgis2/rest/services/districts/Commissioner_Districts/MapServer/0/query', attr: 'DISTRICT_CODE' },
  { key: 'PORTDST', url: 'https://gisportal.franklin.co.franklin.wa.us/arcgis2/rest/services/districts/Special_tax_districts/MapServer/7/query', attr: 'DISTRICT_CODE' },
  { key: 'FIRDST', url: `${DOR_TAX_DISTRICTS}/7/query`, attr: 'DISTATTRIB' },
],
```

The same keys go into `election.DISTRICT_ADAPTER_LAYERS["franklin"]` (with
`CONGDST`, `LEGDST`, `CITY`). The Auditor's precinct-split layer
(`Voting_Precinct_Group/FeatureServer/12`, attributes `COMMISS`, `PORT`, `PUD`,
`FIRE`, `CITY`, `STATE_LEG`, `STATE_CONG`) is an alternative. Its `PORT` values
mix case (`POP1`, `PoP3`) and some read `split`, so the polygon layers are
proposed instead. Until the adapter changes, `PORTDST` and `FIRDST` are scopes
the adapter cannot resolve, and assembly would mark Franklin `partial_county`
and print both.

## Sources

The county publishes a printed local pamphlet. Dossiers cite it as
`local-voters-pamphlet page N` (PDF page; printed page in the note), so
`pamphlet_pages` resolve, and `officialLinks.js` `pamphletPdfs` can link
`'franklin/local-voters-pamphlet'` to
`https://www.franklincountywa.gov/DocumentCenter/View/4553/2611-Franklin-County-Voters-Pamphlet-`.
Other sources: PDC data on data.wa.gov, the county's primary results on
results.votewa.gov, NonStop Local (nbcrightnow.com), and campaign sites. The
Hollingsworth, Huber and Orosco sites answer 403 to curl through Cloudflare
and were read with WebFetch. Their pointers carry no hash.

## Known gaps

- The Tri-City Herald blocked automated access, and the Wayback Machine
  rate-limited, so the herald's 2026 coverage is not used. The session's web
  search budget was exhausted, so sources were found through the county site,
  data.wa.gov, and NonStop Local's own site search.
- Michael Nguyen (District Court) is `pamphlet-only`: his campaign site has
  expired and no coverage was found.
- Rosenau's and Nguyen's PDC filings show no money raised. Rosenau's and Lee's
  campaign sites carry little content.
- The Port of Pasco's resolution adopting by-district elections (1577 on the
  county layer) was not retrieved: portofpasco.org answers 403.
- FPD 3's Resolution No. 491 and the district's own website were not
  retrieved; the current $0.86 rate is the district's figure as reported by
  NonStop Local.
