# Klickitat County Completeness Note

Election: 2026 Washington general election, November 3, 2026 (VoteWA
election 899, county code 20).

Status (#31): shipped at partial coverage in
`APP_PACKAGES["2026-11-03-general"]["counties"]`, with its elections office
(`https://www.klickitatcounty.gov/1136/ElectionsVoter-Registration`), its
voters' pamphlet (`pamphletPdfs['klickitat/local-voters-pamphlet']`, PDF
page = printed page) and its VoteWA guide (`countyGuides.klickitat`,
`c=20`). `COUNTY_LAYERS.klickitat` reads `EMSDST` (DOR EMS2025, layer 6,
proposed below) beside `COUNTY_COUNCIL` and `FIRDST`. The East and West
District Court seats stay `DISTCRT` and hidden: `klickitat/DISTCRT` is in
`UNRESOLVABLE_SCOPES`, and the builder block's `unresolvable_layers`
(added at ship time, since the override hook cannot report a layer) makes
the package itself say `partial_county`. CD 4 ships with Benton's research,
LD 14 with Yakima's, LD 17 with Clark's. Live ballots on 2026-10-08, each
`partial_county` with no missing layer: 205 S Columbus Ave, Goldendale (LD
17, the EMS levy) and 100 E Market St, Bickleton (LD 14, no EMS levy);
neither shows a District Court seat. The paragraphs below describe the
package as researched.

Research status (#31): researched, scored and refuted. The builder
(`pipeline/build_votewa_lite_data.py --county klickitat`) writes
`interim/app-contests.json` and `interim/app-measures.json`. As researched
it printed `full_county`, only because the bulk builder's override hook
could not mark a layer unresolvable: the two District Court seats are
scoped `DISTCRT`, for which no queryable boundary was found (see District
scoping), and the Emergency Medical Services District measure needed
`EMSDST`, which `COUNTY_LAYERS.klickitat` did not yet read.

## Sources

- Candidate list: VoteWA GENERAL 2026 export
  (`raw/votewa/candidate-list.csv.{url,meta.json}`, 34 rows; county 20
  confirmed by the page's County dropdown, `Klickitat`).
- Klickitat County Auditor, Elections/Voter Registration page
  (`https://www.klickitatcounty.gov/1136/ElectionsVoter-Registration`;
  klickitatcounty.org redirects to klickitatcounty.gov):
  - official sample ballot (`raw/klickitat/sample-ballot.pdf.url`,
    DocumentCenter 23909; a composite precinct sample);
  - the 2026 General Election Voters' Pamphlet
    (`raw/klickitat/local-voters-pamphlet.pdf.url`, DocumentCenter 23954):
    the SOS state pamphlet (pp. 1-38, Court of Appeals on p. 37) bound with
    the Klickitat local pamphlet (pp. 39-57; candidates pp. 46-55, the EMS
    measure p. 56). PDF page numbers equal printed page numbers. Dossiers
    cite `local-voters-pamphlet page N`, so records can link the PDF page;
  - EMS District No. 1 Resolution 2026-02
    (`raw/klickitat/resolution-ems-district-1-2026-2.pdf.url`);
  - Votes By District as of 11/25/2025
    (`raw/klickitat/votes-by-district-2025.pdf.url`), registered voters per
    district.
  Text of all four PDFs is in `interim/pdf-text/`
  (`node pipeline/extract_pdf_text.mjs klickitat --election 2026-11-03-general`).
- VoteWA online voters' guide index
  (`raw/votewa/voter-guide/voterguide.json.url`,
  `https://voter.votewa.gov/genericvoterguide.aspx?e=899&c=20`): the same
  races and the one local measure (7277).
- Results: VoteWA results API for the August 4, 2026 primary
  (`raw/klickitat/votewa-results-20260804-ballot-items.url`) and SOS
  Klickitat precinct exports for 2018, 2022, 2024 and 2025
  (`raw/klickitat/sos-results-*-precincts.csv.url`).
- Candidate and measure sources: `raw/candidates/<contest-slug>/`,
  `raw/news/` (Goldendale Sentinel stories used by more than one contest)
  and `raw/measures/<measure-slug>/`: campaign sites, PDC summaries, the
  Goldendale Sentinel (free to read; one story is a Columbia Gorge News
  report it republished), the Yakima Herald-Republic, the county's court
  pages, the Assessor's 2026 levy report and RCW 84.52.069.

## What ships

16 contests (8 contested, 8 uncontested) and 1 local measure. The five
Supreme Court contests are dropped by the builder and ship from the
statewide package.

| Contest | Candidates | Status | Research |
|---|---|---|---|
| U.S. Representative, CD 4 | McKinney, Duresky | contested | Benton's package |
| LD 14 Representative Pos. 1 | Mendoza, Dimas | contested | Yakima's package |
| LD 14 Representative Pos. 2 | Manjarrez, Morfin | contested | Yakima's package |
| LD 17 Representative Pos. 1 | Christly, Waters | contested | Clark's package |
| LD 17 Representative Pos. 2 | Perez, Stuebe | contested | Clark's package |
| County Assessor | Bare | uncontested | Klickitat, info-only |
| County Auditor | Jobe | uncontested | Klickitat, info-only |
| County Clerk | Campbell | uncontested | Klickitat, info-only |
| County Commissioner 2 | Zoller, Kallinen | contested | Klickitat (carried from the primary) |
| Prosecuting Attorney (short and full term) | Cranston | uncontested | Klickitat, info-only |
| Sheriff | Matulovich, Warren | contested | Klickitat (carried from the primary) |
| Treasurer | Gallagher | uncontested | Klickitat, info-only |
| Court of Appeals Div. 3, Dist. 3, Pos. 1 | Murphy | uncontested | Klickitat, info-only (county-scoped copy) |
| East District Court Judge | Hansen | uncontested | Klickitat, info-only; `DISTCRT` `East` (hidden) |
| West District Court Judge | Baker | uncontested | Klickitat, info-only; `DISTCRT` `West` (hidden) |
| PUD No. 1 Commissioner Pos. 3 | Siebert, Gunkel | contested | Klickitat (carried from the primary; PublicUtility: no rubric axis applies, no scores) |

`build_research_plan.py klickitat` shows CD 4 `researched_in` Benton, LD
14 Pos. 1 and 2 Yakima, LD 17 Pos. 1 and 2 Clark, each with no candidates
missing. Klickitat has no Senate race (LD 14 and LD 17 Senate seats are not
up). The Census geocoder puts Goldendale, White Salmon, Bingen, Lyle and
Trout Lake in LD 17, Bickleton and Klickitat in LD 14; the Auditor counts
5,221 LD 14 and 11,200 LD 17 voters.

Measure (researched, scored and refuted):

| Measure | Scope |
|---|---|
| Emergency Medical Services District No. 1 Prop. 1 (permanent EMS levy, up to $0.50 per $1,000) | `EMSDST` `1` |

The EMS measure has a threshold discrepancy recorded in its dossier: RCW
84.52.069(2) requires three-fifths approval (with validation) for a
permanent EMS levy, but Resolution 2026-02 says a simple majority. The
resolution text also does not mention the referendum procedure the statute
requires for permanent levies.

## Builder overrides

The Klickitat block in `ELECTION_MEASURES["2026-11-03-general"]` carries an
`overrides` dict keyed by upper-cased (District, Race). `COUNTY_CONFIG`
was not changed (the primary is frozen).

- `COUNTY` / `COUNTY COMMISSIONER 2` (District Type Countywide): kept as
  the primary's contest (`Klickitat County Commissioner District 2`,
  `County Commissioner 2`) so the slug matches and primary dossiers carry
  forward. Scope `COUNTY`: Klickitat is a non-charter county whose
  commissioners are nominated by district and elected county-wide in the
  general (RCW 36.32.040). The SOS precinct exports show Commissioner 2 on
  all 29 precincts in 2018 and 2022, and Commissioners 1 and 3 on all 33 in
  2024; the 2026 primary ran on 13 district units.
- `PUBLIC UTILITY DISTRICT # 1` / `PUBLIC UTILITY DISTRICT #1 COMMISSIONER POS. 3`:
  the generic rule reads `# 1` as commissioner district 1 (`PUDDST` `1`),
  which is wrong. Kept as the primary's names (`Public Utility District
  Commissioner District 3`) so the slug matches, scope `COUNTY`. PUD No. 1
  covers the whole county (Votes By District 2025: 16,421 voters, equal to
  Congressional District 4 and the Superior Court, i.e. the county; DOR
  PUD2025 has one Klickitat polygon, `1`, at every address below) and the
  whole PUD elects each commissioner in the general (RCW 54.12.010(3); 2018
  Pos. 1, 2020 Pos. 3, 2022 Pos. 2 and 2024 Pos. 1 on every precinct).
- `EAST DISTRICT COURT` / `KLICKITAT COUNTY EAST DISTRICT COURT JUDGE` and
  `WEST DISTRICT COURT` / `KLICKITAT COUNTY WEST DISTRICT COURT JUDGE`:
  category Judicial, `Klickitat County East/West District Court`, `Judge`,
  scope `DISTCRT` `East` / `West`. The two courts are separate electorates
  that partition the county: Votes By District 2025 gives East 7,550 and
  West 8,871 (sum 16,421); the 2018 and 2022 judge races were on 18 (East)
  and 15-16 (West) of 29 precincts, with Appleton, Centerville, Glenwood,
  Mt Brook, River and (2018) Trout Lake on both, i.e. split precincts. The
  generic rule would have scoped them `COUNTY`, which would show each seat
  to the other court's voters.

## District scoping

Point queries, 2026-10-08 (Census geocoder, Current vintage; DOR
`WADOR_PropertyTax/MapServer`, tax year 2025, layer list unchanged:
3 CEM2025, 6 EMS2025, 7 FIR2025, 11 HSP2025, 12 LIB2025, 14 PKR2025,
16 PRT2025, 17 PUD2025, 20 SCH2025). County layers on
`geo.gartrellgroup.com/server/rest/services/Klickitat/Layers/MapServer`.

| Address | Census place, CD, LD | County 21 Commissioner `NO` | County 27 Precinct | County 23 Fire `DISTRICT_N` | DOR EMS (6) | DOR FIR (7) | DOR PUD (17) | DOR HSP (11) | DOR SCH (20) |
|---|---|---|---|---|---|---|---|---|---|
| 205 S Columbus Ave, Goldendale | Goldendale, CD 4, LD 17 | `3` | `0104` | `City of GD` | `1` | none | `1` | `1` | `404` |
| 100 N Main Ave, White Salmon | White Salmon, CD 4, LD 17 | `1` | `0109` | `WKRFA` | `1` | none | `1` | `2` | `405` |
| 208 W Steuben St, Bingen | Bingen, CD 4, LD 17 | `1` | `0101` | `City of Bingen` | `1` | none | `1` | `2` | `405` |
| 5 Lyle Snowden Rd, Lyle | (no place), CD 4, LD 17 | `2` | `0004` | `4` | `1` | `4` | `1` | `2` | `406` |
| 100 E Market St, Bickleton | Bickleton CDP, CD 4, LD 14 | `3` | `0001` | `2` | none | `2` | `1` | none | `203` |
| 2383 State Rte 141, Trout Lake | Trout Lake CDP, CD 4, LD 17 | `1` | `0016` | `1` | `1` | `1` | `1` | `2` | `400` |
| 103 Main St, Klickitat | Klickitat CDP, CD 4, LD 14 | `2` | `0017` | `12` | `1` | `12` | `1` | `1` | `402` |

`where COUNTYNAME = 'KLICKITAT'` returns one EMS2025 feature (`1`) and one
PUD2025 feature (`1`).

Layers each general scope needs:

- `CONGDST` `4`, `LEGDST` `14`/`17`: Census.
- `COUNTY`: every county office, the Commissioner 2 and PUD Pos. 3 seats
  (county-wide in the general) and the Court of Appeals seat.
- `EMSDST` `1` (EMS District No. 1 Prop. 1): **not in
  `COUNTY_LAYERS.klickitat` yet. Proposed:**
  `{ key: 'EMSDST', url: \`${DOR_TAX_DISTRICTS}/6/query\`, attr: 'DISTATTRIB' }`
  (Ferry and Asotin already read EMS2025). Live: Goldendale, White Salmon,
  Bingen, Lyle, Trout Lake and Klickitat return `1`; Bickleton returns no
  feature. The Auditor counts 16,105 EMS District voters of 16,421, so the
  outside area is small. Without this layer the measure is hidden county-wide.
- `DISTCRT` `East`/`West` (both District Court seats, uncontested):
  **unresolvable.** Searched: the county's Gartrell MapServer (layers 0-28:
  commissioner, cemetery, fire, recreation, school, water, voting precincts
  `PRECINCT` only, no court attribute; `Layers1` has two unrelated layers;
  the `imap.klickitatcounty.gov` viewer uses the same services), DOR
  property-tax layers (no court districts), ArcGIS Online search for
  "klickitat" and "klickitat district court" (232 items, none a court or
  election-district layer), the county's elections page (precinct
  descriptions and a commissioner/legislative district map PDF only) and
  both court pages (no boundary). Precincts are split between the courts
  (see Builder overrides), so a precinct-list `where` on layer 27 would
  also be wrong. Proposed: add `'klickitat/DISTCRT'` to
  `UNRESOLVABLE_SCOPES` with the reason "East/West District Court
  electoral districts have no public GIS layer"; the county then ships
  `partial_county`. The Auditor could supply the boundary.

`COUNTY_LAYERS.klickitat` today reads `COUNTY_COUNCIL` (Gartrell layer 21,
`NO`) and `FIRDST` (DOR FIR2025). Both re-probed live above (layer 21:
`1`-`3`; FIR2025: `4` at Lyle, the archived primary's FD 4 levy scope). No
general scope uses either.

Suggested live checks: 205 S Columbus Ave, Goldendale (EMS measure, LD 17,
county races); 100 E Market St, Bickleton (LD 14; no EMS measure); 103 Main
St, Klickitat (LD 14 with the EMS measure); 100 N Main Ave, White Salmon
(LD 17, EMS measure). Each should list both District Court seats as
missing/hidden until a court layer exists.

## Known gaps

- WebSearch was unavailable (session quota exhausted); sources came from
  direct fetches of the Goldendale Sentinel's search pages, county pages,
  PDC open data, SOS results and VoteWA. Columbia Gorge News
  (gorgenews.com) did not answer.
- Dwayne Matulovich's campaign site is a Canva export whose text is
  rendered client-side; nothing could be read, so his dossier rests on the
  pamphlet and Sentinel coverage.
- PUD candidates file PDC mini reports (no finance data). Gunkel says he
  takes no contributions.
- The Sentinel's July 29 Siebert story calls the seat "Position 1"; the
  ballot says Pos. 3. Its October 7 Zoller story names the prosecutor
  "Rebecca Henke"; the county's appointed prosecutor and the only candidate
  is Rebecca Cranston (Sentinel, January 7 and September 16, 2026).
- Uncontested office-holders were checked against the pamphlet and
  results only; no further research.
- The 2026 EMS measure has no arguments for or against and no news
  coverage was found.
