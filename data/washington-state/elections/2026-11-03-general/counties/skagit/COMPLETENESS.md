# Skagit County Completeness Note

Election: 2026 Washington general election, November 3, 2026 (VoteWA
election 899, county code 29).

Shipped (#28): the package is declared in
`APP_PACKAGES["2026-11-03-general"]["counties"]` and ships at Full County
Coverage, with the elections office link
`https://www.skagitcountywa.gov/government/auditor-s-office/elections-and-voting/`,
the local pamphlet (`officialLinks.js` `pamphletPdfs['skagit/local-voters-pamphlet']`,
PDF pages) and the county's VoteWA guide (`countyGuides.skagit`) for any
record without a page. The builder output is `full_county`: every contest and
measure scope is `COUNTY`, Census `CONGDST`/`LEGDST`/`CITY`, or a layer
already in `app/src/lib/geo.js` `COUNTY_LAYERS.skagit` (`SCHDST`,
`FIRDST`). Assembly reads `interim/app-contests.json` and
`interim/app-measures.json`, built by
`python3 pipeline/build_votewa_lite_data.py --election 2026-11-03-general --county skagit`
from the VoteWA candidate list (`COUNTY_CONFIG["skagit"]`) and the four
measures curated in `ELECTION_MEASURES["2026-11-03-general"]["skagit"]`.

## What ships

19 contests (14 contested, 5 uncontested) and 4 measures. The Supreme
Court contests are dropped by the builder and ship once, from the statewide
package.

| Kind | Contests | Contested | Uncontested (info-only) | Scope | Research |
|---|---|---|---|---|---|
| U.S. Representative (CD 2) | 1 | 1 | 0 | `CONGDST` | Snohomish package |
| State Representative LD 10 and LD 39, Pos. 1 and 2 | 4 | 4 | 0 | `LEGDST` | Snohomish package |
| State Representative LD 40, Pos. 1 and 2 | 2 | 2 | 0 | `LEGDST` | Whatcom package |
| County Commissioner District 3 (short and full term) | 1 | 1 | 0 | `COUNTY` | here |
| Auditor, Clerk, Coroner, Sheriff, Treasurer | 5 | 5 | 0 | `COUNTY` | here |
| Assessor, Prosecuting Attorney | 2 | 0 | 2 | `COUNTY` | here (info-only) |
| District Court Judge Positions 1, 2, 3 | 3 | 0 | 3 | `COUNTY` | here (info-only) |
| Skagit PUD No. 1 Commissioner Position 1 | 1 | 1 | 0 | `COUNTY` | here (no applicable axis; summaries only) |

No State Senate seat in Skagit's districts is on this ballot, and no
Superior Court or Court of Appeals race.

Measures (4): City of Mount Vernon (Mount Vernon Transportation Benefit
District) Prop. 1, 0.2% sales tax renewal (`CITY` `Mount Vernon`); City of
Sedro-Woolley Prop. 1, annexation into the Central Skagit Rural
Partial-County Library District (`CITY` `Sedro-Woolley`); La Conner School
District No. 311 Prop. 1, facility modernization and technology levy
(`SCHDST` `311`); Skagit County Fire Protection District No. 5 Prop. 1,
regular levy restoration (`FIRDST` `5`). The Auditor's Ballot Measures page
(`raw/skagit/ballot-measures.html.url`) lists exactly these four for the
general. Each ships `pamphlet_pages` for the PDF page its dossier cites
(18-21), set by `pages=` in the builder block.

## Sources

- VoteWA candidate list: `raw/votewa/candidate-list.csv.{url,meta.json}`
  (43 rows, pinned by `sha256` and `sha256_case_normalized`).
- Local voters' pamphlet (printed, published by the Skagit County Auditor):
  `raw/skagit/local-voters-pamphlet.pdf.url` (edition id
  `local-voters-pamphlet`, 23 PDF pages). Its printed folios run 39-61, so
  **PDF page = printed page - 38**; dossiers cite PDF pages. Candidate
  statements PDF pages 6-17, measures 18-21. Text in
  `interim/pdf-text/local-voters-pamphlet.txt`.
- Sample ballot: `raw/skagit/sample-ballot.pdf.url` (text in
  `interim/pdf-text/sample-ballot.txt`). Measure resolutions:
  `raw/skagit/<measure>.pdf.url`.
- VoteWA online voters' guide (`genericvoterguide.aspx?e=899&c=29`): race and
  measure records under `raw/votewa/voter-guide/`, text in
  `interim/voter-guide-text/`.
- Statutes: `raw/skagit/rcw-54-12-010.html.url`, `raw/skagit/rcw-36-32-040.html.url`.

## District scoping

- **Commissioner District 3** is elected county-wide in the general: VoteWA
  types the race `Countywide` / `County`, and the sample ballot prints it
  for every precinct under "County Partisan Offices". Skagit is a
  non-charter three-commissioner county; commissioners are nominated by
  district (RCW 36.32.040(1)) and elected county-wide. Nothing found shows
  Skagit adopting district-only elections under RCW 29A.92.040
  (RCW 36.32.040(3)). Scope `COUNTY`; the `COUNTY_COUNCIL` layer in
  `COUNTY_LAYERS.skagit` (the primary's) is not used in the general.
- **Skagit PUD No. 1** is countywide: VoteWA district `SKAGIT PUD DISTRICT
  COUNTYWIDE`, and DOR `WADOR_PropertyTax/MapServer/17` (PUD2025) returns
  `COUNTYNAME SKAGIT, DISTATTRIB 1` at Anacortes (904 6th St), Mount Vernon
  (700 S 2nd St), Sedro-Woolley, La Conner, Bow, Concrete and Marblemount
  (60084 SR 20). The whole PUD votes for each commissioner in the general
  (RCW 54.12.010(3)), so the seat is scoped `COUNTY`
  (`COUNTY_CONFIG["skagit"]` `pud_layer_key: "COUNTY"`). The generic rule
  would have scoped it `PUDDST` (unresolvable).
- **Seat number discrepancy:** the pamphlet (PDF pages 5, 17), VoteWA
  (`Commissioner 1`) and PDC say Commissioner **Position 1**; the sample
  ballot prints "Commissioner Position 3". The package follows VoteWA. The
  Auditor should be asked which is right before shipping.
- **District Court** (Positions 1-3): VoteWA types them `Countywide`; one
  county-wide electorate. The generic rule gives category `County`, office
  `District Court Judge Position N` (no override exists in
  `build_votewa_lite_data.py` for the 32 counties; the app does not read
  `category`, and `validate_scoring.py` treats any `judge` slug as judicial).
- **Point checks (2026-10-08, Census geocoder + DOR tax-district layers):**
  700 S 2nd St, Mount Vernon: place `Mount Vernon city`, CD 2, LD 10,
  `SCHDST` 320, no `FIRDST`, commissioner district 2. 325 Metcalf St,
  Sedro-Woolley: place `Sedro-Woolley city`, LD 39. 305 N 6th St,
  La Conner: `SCHDST` `311`, LD 10. 5800 Main St, Bow (Edison CDP):
  `FIRDST` `5`, LD 40.

## Shared races

`build_research_plan.py` finds CD 2 and LD 10 / LD 39 (both positions)
researched in `snohomish` and LD 40 Pos. 1 and 2 researched in `whatcom`
(rebuilt after the #28 merges; no candidates missing). All seven ship with
the owning package's scoring and dossiers and carry no pamphlet pages.

Live ballots on 2026-10-08 (`pipeline/live_ballot.mjs`, `full_county`,
`missing=[]`): 700 S 2nd St, Mount Vernon (LD 10, Mount Vernon Prop 1);
5800 Main St, Bow (LD 40, FD 5 Prop 1); 305 N 6th St, La Conner (LD 10,
La Conner SD Prop 1).

## Known gaps

- LD 40 (above): no research in this package by design; Whatcom's ships.
- PUD seat number (above): Position 1 per VoteWA and the pamphlet, Position
  3 on the sample ballot; not confirmed with the Auditor before shipping.
- Treasurer: neither candidate has a campaign website or itemized PDC
  reports; evidence is pamphlet, party slates and write-in coverage.
- Some Skagit Valley Herald forum stories (Auditor and PUD forums on
  October 12) postdate this research.
- skagitpud.org answered 403 to scripted requests and WebFetch; no PUD page
  is cited.
