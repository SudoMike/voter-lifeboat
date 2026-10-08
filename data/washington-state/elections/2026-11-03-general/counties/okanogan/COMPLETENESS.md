# Okanogan County Completeness Note

Election: 2026 Washington general election, November 3, 2026 (VoteWA
election 899, county code 24).

Research package for #30 (county wave 5). Not shipped: the director
declares it. Contests and measures are built by
`pipeline/build_votewa_lite_data.py --county okanogan` from the VoteWA
candidate list (`raw/votewa/candidate-list.csv.url`) and the overrides and
measures in that script's `ELECTION_MEASURES["2026-11-03-general"]["okanogan"]`,
checked against VoteWA's online voters' guide for the county
(`https://voter.votewa.gov/genericvoterguide.aspx?e=899&c=24`; records under
`raw/votewa/voter-guide/`, text in `interim/voter-guide-text/`) and the
Auditor's Elections and District Resolutions pages
(`raw/okanogan/elections-page.html.url`, `raw/okanogan/district-resolutions.html.url`).
Okanogan County prints no local voters' pamphlet, and on 2026-10-08 its
Elections page listed "Sample Ballot (PDF)" with no link, so the sample
ballot could not be checked. Every candidate and local measure in the
guide is in the package, and the guide's local measures match the
Auditor's resolution packets (the county's own levy, Resolution 48-2026,
was on the August primary and is not on this ballot).

The builder reports `partial_county` (`UNRESOLVABLE: PUDDST`): the two PUD
seats have no queryable boundary (below).

## What is on the ballot

18 contests (9 contested, 9 uncontested) and 6 local measures. The five
Supreme Court contests and the three statewide initiatives are dropped by
the builder and ship from the statewide package.

| Kind | Contests | Contested | Uncontested | Scope | Researched |
|---|---|---|---|---|---|
| U.S. Representative (CD 4) | 1 | 1 | 0 | `CONGDST` `4` | Benton package |
| LD 7 Senator | 1 | 1 | 0 | `LEGDST` `7` | Spokane package |
| LD 7 Rep. Pos. 1, Pos. 2 | 2 | 0 | 2 | `LEGDST` `7` | Spokane package (info-only) |
| Commissioner District 3 | 1 | 1 | 0 | `COUNTY` | here |
| Coroner, Sheriff | 2 | 2 | 0 | `COUNTY` | here |
| Assessor, Auditor, Clerk, Prosecuting Attorney, Treasurer | 5 | 0 | 5 | `COUNTY` | here (info-only) |
| District Court Judge Positions No. 1, No. 2 | 2 | 2 | 0 | `COUNTY` | here |
| Superior Court Judge Position 2 (unexpired) | 1 | 0 | 1 | `COUNTY` | here (info-only) |
| Court of Appeals Div. III, Dist. 1, Pos. 2 | 1 | 0 | 1 | `COUNTY` | Spokane package (info-only) |
| Okanogan County PUD Commissioner Dist. 1 | 1 | 1 | 0 | `PUDDST` `1` (unresolvable) | here (no applicable axis) |
| Ferry County PUD No. 1 Commissioner #3 | 1 | 1 | 0 | `PUDDST` `3` (unresolvable) | here (no applicable axis) |

All of Okanogan County is in CD 4 and LD 7 (Census geocoder at Omak,
Oroville, Brewster, Twisp, Winthrop and Mazama addresses: CD 4, LD 7);
no LD 12 or CD 5 race is on the VoteWA list. The uncontested LD 7 House seats and
the Court of Appeals seat have no scoring file here: assembly ships them
with Spokane's information-only scoring (`shared_contests.contest_key`
matches `LEGDST` and the `NAMED` key `court of appeals, division 3, district
1` / `judge position 2`).

Measures (VoteWA guide records 7278-7283):

- Public Hospital District No. 1, Okanogan and Douglas Counties (Three
  Rivers Hospital) Proposition No. 1, $48 million bonds: `HOSPDST` `1J`.
- City of Brewster Proposition No. 1, EMS levy continuation: `CITY` `Brewster`.
- Town of Twisp Proposition No. 1, one-year EMS excess levy: `CITY` `Twisp`.
- Town of Winthrop Proposition No. 1, one-year EMS excess levy: `CITY` `Winthrop`.
- Methow Valley EMS District Proposition No. 1, one-year EMS excess levy:
  `EMSDST` `MV`.
- Okanogan County Fire Protection District No. 1 (Oroville area)
  Proposition No. 1, levy lid lift: `FIRDST` `1`.

## District scoping

- Commissioner District 3: nominated by district in the primary (37 of 97
  reporting units in the VoteWA primary results,
  `raw/okanogan/votewa-20260804-primary-results.json.url`), elected
  county-wide in the general (RCW 36.32.040). VoteWA's general export lists
  it as `Countywide` / `County`, and in the SOS precinct exports the 2020
  Districts 1 and 2, 2022 District 3 and 2024 Districts 1 and 2 races are
  on all 248 precincts, like U.S. Senator. Scope `COUNTY`; the override
  keeps the primary's contest name, so its slug
  (`okanogan-okanogan-county-commissioner-district-3-commissioner-district-3`)
  matches the primary's.
- District Court: one county-wide district; both seats were on all 248
  precincts in 2022. Override names it `Okanogan County District Court`,
  `Judge Position No. 1` / `No. 2`, category `Judicial`.
- Superior Court: Okanogan is its own judicial district; Positions 1 and 2
  were on all 248 precincts in 2020. Scope `COUNTY` (generic rule).
- **Okanogan County PUD Commissioner Dist. 1**: nominated by district,
  elected by the whole PUD in the general (RCW 54.12.010(3); the 2022 and
  2024 `OKANOGAN PUD` races were on 247 of 248 precincts). The PUD is not
  the whole county: the Auditor's Votes By District report
  (`raw/okanogan/votes-by-district-pud.pdf.url`, as of 11/20/2025) counts
  26,809 registered voters in `OKANOGAN PUD COUNTY` and 325 in
  `PUD (COUNTYWIDE)`, which is Ferry County PUD No. 1; the commissioner
  districts total 27,134 = 26,809 + 325
  (`raw/okanogan/votes-by-district-commissioners.pdf.url`). Those 325
  voters sit in eight northeastern precincts (2020-2024 names: BODIE,
  CHESAW, SAN POIL, WAUCONDA, TORODA, SOURDOUGH, BUCKHORN MTN, MYERS CREEK),
  which carried Ferry PUD's race in 2020, 2022 and 2024; BODIE carried no
  Okanogan PUD race in 2024. WA DOR PUD2025 (layer 17) has a single
  Okanogan polygon (`DISTATTRIB` `1`) covering the whole county (point
  queries at Wauconda, Chesaw, (-118.88, 48.83) near Bodie, and Omak all
  answer `OKANOGAN` `1`), and its Ferry polygon stops at the county line;
  NoaNet's `PUDOkanogan`/`PUDFerry` service-area layers are county
  outlines too. No Auditor precinct or PUD layer is public (the county's
  ArcGIS org `services3.arcgis.com/p1XMcn4KWrkdZVeA` has fire, EMS,
  hospital, parcels and addressing layers only; WAGeoservices' statewide
  precinct splits are from 2019, before Resolution 99-2025 renumbered
  every Okanogan precinct). So the seat stays `PUDDST` `1`, unresolvable,
  and is hidden (generic builder rule, so the builder flags it). Scoping it
  `COUNTY` would show it to the 325 Ferry PUD voters (1.2% of the
  county); reading DOR PUD2025 for `PUDDST` would do the same. That is the
  director's call; this package does not make it.
- **Ferry County PUD No. 1 Commissioner #3** (Pooler, Aubertin): elected
  PUD-wide ("PUD (COUNTYWIDE)" in VoteWA), on Okanogan's ballot only for the
  ~325 voters above. Scope `PUDDST` `3` (generic rule), unresolvable; no
  layer finds those voters. It would stay hidden even if DOR PUD2025 were
  added (no Okanogan polygon carries `3`). The generic contest name
  (`Public Utility District Commissioner District 3`) does not say Ferry;
  the dossiers do. An override could rename it, but the bulk builder's
  overrides do not mark a layer unresolvable, so the builder would then
  report `full_county`; the generic rule was kept so the package's coverage
  stays honest.
- Hospital bonds: Three Rivers Hospital's district is DOR HSP2025 (layer
  11) `1J` in Okanogan (Brewster, Pateros, the Methow Valley; 8,066
  Okanogan voters per `raw/okanogan/votes-by-district-hospitals.pdf.url`).
  The Douglas County part votes on the Douglas ballot.
- Methow Valley EMS District: DOR EMS2025 (layer 6) `MV`, which leaves
  out the towns of Twisp (`TC`) and Winthrop (`WC`); the towns run their
  own levies for the same provider (Aero Methow Rescue Service).
- Fire District 1: DOR FIR2025 (layer 7) `1`, the rural Oroville area; the
  City of Oroville is outside it.
- Brewster, Twisp, Winthrop: Census places.

### Layers each scope needs

| Scope | Layer | URL | Attribute | In `COUNTY_LAYERS.okanogan` today |
|---|---|---|---|---|
| `CONGDST`, `LEGDST`, `CITY` | Census geocoder | built in | | yes |
| `FIRDST` `1` | DOR FIR2025 | `https://webgis.dor.wa.gov/arcgis/rest/services/Programs/WADOR_PropertyTax/MapServer/7` | `DISTATTRIB` | yes |
| `HOSPDST` `1J` | DOR HSP2025 | `.../MapServer/11` | `DISTATTRIB` | yes |
| `EMSDST` `MV` | DOR EMS2025 | `.../MapServer/6` | `DISTATTRIB` | **no: proposed** |
| `PUDDST` | none found | | | no (unresolvable) |

Proposed addition:
`{ key: 'EMSDST', url: `${DOR_TAX_DISTRICTS}/6/query`, attr: 'DISTATTRIB' }`

Point queries, 2026-10-08 (Census geocoder `Public_AR_Current` /
`Current_Current`, then the DOR layer with the returned x/y):

| Address | Census place | FIR2025 (7) | HSP2025 (11) | EMS2025 (6) |
|---|---|---|---|---|
| 415 Hospital Way, Brewster | Brewster city | none | `1J` | `BC` |
| 118 S Glover St, Twisp | Twisp town | `6` | `1J` | `TC` |
| 206 Riverside Ave, Winthrop | Winthrop town | `6` | `1J` | `WC` |
| 50 Lost River Rd, Mazama | none | `6` | `1J` | `MV` |
| 2 S Ash St, Omak | Omak city | none | `3` | none |
| 1308 Ironwood St, Oroville | Oroville city | none | `4` | `OC` |
| 26 Eastside Oroville Rd, Oroville | none | `1` | | |
| 38 Swanson Mill Rd, Oroville | none | `1` | | |

`COUNTY_LAYERS.okanogan` (`FIRDST`, `HOSPDST`, both DOR) answered every
query above; no commissioner layer is needed (the general's commissioner
race is county-wide).

Suggested live-check addresses: 50 Lost River Rd, Mazama (hospital bonds,
Methow Valley EMS); 206 Riverside Ave, Winthrop (hospital bonds, Winthrop
EMS); 118 S Glover St, Twisp (hospital bonds, Twisp EMS); 415 Hospital Way,
Brewster (hospital bonds, Brewster EMS); 38 Swanson Mill Rd, Oroville (Fire
District 1); 2 S Ash St, Omak (county races only). Every address should
list the county contests; none can list the PUD seats while `PUDDST` is
unresolvable.

## Sources

Okanogan prints no local pamphlet. Candidate and measure dossiers cite
VoteWA's online voters' guide (`candidate.ashx`/`measure.ashx`, no pages),
so the county's records ship no pamphlet pages; the director would link
the guide (`countyGuides.okanogan`, `c=24`). Local news is the Methow
Valley News and Methow Valley Examiner (WordPress REST API, full text) and
the Omak-Okanogan County Chronicle (often paywalled; only readable text is
cited).

## Research (#30)

Dossiers, scoring and an independent refutation pass for the seven
contested races researched here and the six measures; information-only
scoring files (empty `scores`) for the five uncontested county offices and
Superior Court Position 2. The primary's Okanogan dossiers (commissioner,
coroner, sheriff) were thin and were re-researched, not carried.

Refutation results (`scoring/refutations/`, applied by `merge_scores.py`):
Gonzalez `safety` -2 adjusted to -1; Jensen `experience` +2 adjusted to +1;
Gonzalez and Stucker `reform` refuted (trust and transparency talk is not
money-in-politics reform); every other score upheld. The measure display
corrections (Twisp and Methow Valley EMS pro summaries) were applied by hand
to `scoring/measures.json`.

## Known gaps

- No bar ratings were found for any judicial candidate, and the Commission
  on Judicial Conduct's records were not machine-readable.
- Robert Grim's statement lists District Court service 2015-2022; the
  Methow Valley News says he left that court in 2021 for private practice.
  Both are recorded in his dossier.
- Doug Aubertin's statement says both "Ferry County Commissioner in
  District #3 for the past 18 years" and "your PUD Commissioner"; the
  dossier quotes it as written. Ferry County PUD's website did not answer.
- Steven Gadd (PUD) and Andrew Pooler (Ferry PUD) are pamphlet-only; Fire
  District 1's levy had no press coverage.
- The resolution packets are scans; OCR was not possible here, so the
  measures rest on the VoteWA guide records.
