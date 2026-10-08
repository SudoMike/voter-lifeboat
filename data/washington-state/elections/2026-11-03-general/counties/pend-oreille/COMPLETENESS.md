# Pend Oreille County Completeness Note

Election: 2026 Washington general election, November 3, 2026 (VoteWA
election 899, county code 26).

Status (#32): shipped at Full County Coverage in
`APP_PACKAGES["2026-11-03-general"]["counties"]`, with its elections office
(`https://www.pendoreille.gov/auditor/page/elections`), its pamphlet
(`pamphletPdfs['pend-oreille/local-voters-pamphlet']`, PDF page = printed
page - 38) and its VoteWA guide (`countyGuides['pend-oreille']`, `c=26`).
`COUNTY_LAYERS['pend-oreille']` gained `SCHDST` (DOR 20) and `SEWDST` (DOR
21) as proposed below; `COUNTY_COUNCIL` and `HOSPDST` were re-probed. CD 5
and LD 7 ship with Spokane's research, the Superior Court Pos. 2 seat with
Stevens's. Live ballots on 2026-10-08, each `full_county` with no missing
layer: 4571 State Route 211, Newport (hospital bonds and the Sacheen Lake
levy), 1722 Kirkpatrick Rd, Elk (hospital bonds and the Riverside levy) and
201 Main St, Ione (no local measure). The paragraphs below describe the
package as researched.

Contests and measures are built by
`pipeline/build_votewa_lite_data.py --county pend-oreille` from the VoteWA
candidate list (`raw/votewa/candidate-list.csv.url`, 29 rows) and the
overrides and measures in that script's
`ELECTION_MEASURES["2026-11-03-general"]["pend-oreille"]`. They were checked
against three official lists, which agree:

- the Auditor's sample ballot (`raw/pend-oreille/sample-ballot.pdf.url`,
  text in `interim/pdf-text/sample-ballot.txt`);
- the Auditor's local voters' pamphlet
  (`raw/pend-oreille/local-voters-pamphlet.pdf.url`, printed pages 39-57,
  PDF page = printed page - 38; text in
  `interim/pdf-text/local-voters-pamphlet.txt`), both linked from
  `https://www.pendoreille.gov/auditor/page/elections`;
- VoteWA's online voters' guide for the county
  (`https://voter.votewa.gov/genericvoterguide.aspx?e=899&c=26`; records
  under `raw/votewa/voter-guide/`, text in `interim/voter-guide-text/`).

The county's old site (`pendoreilleco.org`) now redirects to
`www.pendoreille.gov`. Records cite the pamphlet by PDF page, so the app can
link `local-voters-pamphlet` pages (`pamphlet_refs` recognizes the edition
id); Staab (Court of Appeals) has no pamphlet entry and cites the VoteWA
guide.

The builder reports `full_county`. That is true only once the director adds
the two DOR layers below to `COUNTY_LAYERS['pend-oreille']`; until then the
assembler will mark the county `partial_county` for `SCHDST` and `SEWDST`.

## What is on the ballot

15 contests (4 contested, 11 uncontested) and 3 local measures. The five
Supreme Court contests and three statewide initiatives ship from the
statewide package.

| Kind | Contests | Contested | Uncontested | Scope | Researched |
|---|---|---|---|---|---|
| U.S. Representative (CD 5) | 1 | 1 | 0 | `CONGDST` `5` | Spokane package |
| LD 7 State Senator | 1 | 1 | 0 | `LEGDST` `7` | Spokane package |
| LD 7 Representative Pos. 1, Pos. 2 | 2 | 0 | 2 | `LEGDST` `7` | Spokane package (info-only) |
| County Commissioner District 2 (elected county-wide) | 1 | 1 | 0 | `COUNTY` | here (scored) |
| PUD No. 1 Commissioner #2 (elected PUD-wide = county) | 1 | 1 | 0 | `COUNTY` | here (no applicable axis) |
| Assessor, Auditor, Clerk, Prosecutor, Sheriff, Treasurer | 6 | 0 | 6 | `COUNTY` | here (info-only) |
| District Court Judge | 1 | 0 | 1 | `COUNTY` | here (info-only) |
| Court of Appeals Div. III Dist. 1 Pos. 2 | 1 | 0 | 1 | `COUNTY` | here (info-only county copy) |
| Superior Court (Ferry, Pend Oreille, Stevens) Pos. 2, unexpired | 1 | 0 | 1 | `COUNTY` | Stevens package (info-only) |

The research plan names CD 5 and LD 7 Senate `researched_in` spokane, with
no `candidates_missing`. The uncontested LD 7 House seats and the Superior
Court seat are not in the plan; `shared_contests.contest_key` matches them to
Spokane's and Stevens's information-only scoring files, which assembly uses.
No Pend Oreille copy of any of these was written. The Court of Appeals seat
also matches Stevens's file, but Pend Oreille ships its own county copy (its
own scoring file wins at assembly), as each county in Division III District
1 has done.

Primary carry-forward: the commissioner and PUD contests keep the
primary's contest names (overrides), so their slugs match and the plan
lists `carry_forward: primary` for all four candidates. The primary's
dossiers were thin (filing-level); all four were rebuilt from the general's
sources.

Measures (VoteWA guide records 7307, 7332, 7245; pamphlet PDF pages 14-19):

- Pend Oreille County Public Hospital District No. 1 Proposition No. 1:
  $51 million, 30-year bonds for the Newport Community Hospital expansion,
  est. $1.47 per $1,000; 60% needed. The same bonds failed on August 4,
  1,719 to 2,084 (45.2%). `HOSPDST` `1`.
- Riverside School District No. 416-62 Proposition No. 1: replacement EP&O
  levy, est. $1.58 per $1,000, 2028-2030. `SCHDST` `62` (the district's
  Pend Oreille part; Spokane's package has its own copy scoped to Spokane).
- Sacheen Lake Water and Sewer District Proposition No. 1: one-year excess
  M&O levy, about $0.75 per $1,000 ($113,827) for 2027; 60% needed.
  `SEWDST` `3`.

## District scoping

- Commissioner District 2: non-charter county under 400,000, so
  commissioners are nominated by district (RCW 36.32.040) and elected by the
  whole county (RCW 36.32.050(1); `raw/statutes/`). The August primary for
  District 2 ran in 7 of 27 units; the SOS precinct exports put the 2020
  #1 and #3, 2022 #2 and 2024 #1 and #3 general races on all 27 voting
  precincts (`raw/pend-oreille/sos-results-*.csv.url`). VoteWA lists the
  race as `Countywide`. Scope `COUNTY`.
- PUD No. 1: VoteWA district `Public Utility District (ALL)`. WA DOR
  PUD2025 (layer 17) has one Pend Oreille polygon, `DISTATTRIB` `1`,
  `Shape_Area` 8,410,296,539.69, equal to the sum of the county's six
  SCH2025 polygons (8,410,296,537.7) and of its two HSP2025 polygons; it
  reads `1` at every address probed below. Every PUD voter elects each
  commissioner in the general (RCW 54.12.010(3)); the 2020 #2, 2022 #3 and
  2024 #1 races were on all 27 precincts, while this year's primary ran in
  the 7 District 2 units. Scope `COUNTY`. (The archived primary scoped it
  `COUNTY_COUNCIL` `Commissioner - 02`, the nominating district; the primary
  is frozen.)
- District Court: one county-wide court (2022 race on all 27 precincts);
  filed `Judicial` by override.
- Hospital District No. 1: DOR HSP2025 has two Pend Oreille polygons, `1`
  (south) and `2` (north: Ione, Metaline, Metaline Falls). The August bond
  ran in 22 of 27 units.
- Riverside SD: DOR SCH2025 `62` is a strip along the Spokane County line
  near Elk (DOR's 2025 levy detail: `Riverside #1-62-416 Enrichment`,
  TDCODE 260441610, $113.9 million assessed value). The county's own
  `School_Districts___Open_Data/FeatureServer/1` reads `Riverside Joint
  #416/062` at the same point. `62` is unique in the county.
- Sacheen Lake W/S District: DOR SEW2025 (layer 21) has four Pend Oreille
  polygons (`1`, `2`, `3`, `LID`); `3` is the Sacheen Lake district. The
  county's `Water_Sewer_Districts___Open_Data/FeatureServer/0` reads
  `Sacheen` at all three test addresses; DOR's 2025 levy detail shows one
  sewer levy in the county, `Sewer Excess` (261600170), $0.73487 on $120.3
  million, matching the district's prior one-year levy. The levy appeared
  only in the one `Sacheen` precinct in 2020, 2022 and 2024.

### Layers the District Adapter needs

`app/src/lib/geo.js` `COUNTY_LAYERS['pend-oreille']` reads `COUNTY_COUNCIL`
(county `Commissioner_Districts___Open_Data/FeatureServer/0`, attr
`commission`) and `HOSPDST` (DOR 11). Both re-probed alive on 2026-10-08
(`Commissioner - 02` at Newport, `Commissioner - 03` at Cusick, Ione and
Metaline Falls; HSP2025 values below). No general contest uses
`COUNTY_COUNCIL`. The general needs two more, both DOR:

| Key | URL | Attr | Used by |
|---|---|---|---|
| `HOSPDST` (present) | `${DOR_TAX_DISTRICTS}/11/query` | `DISTATTRIB` | Hospital District No. 1 bonds (`1`) |
| `SCHDST` (add) | `${DOR_TAX_DISTRICTS}/20/query` | `DISTATTRIB` | Riverside SD Prop. 1 (`62`) |
| `SEWDST` (add, new key) | `${DOR_TAX_DISTRICTS}/21/query` | `DISTATTRIB` | Sacheen Lake W/S Prop. 1 (`3`) |

`SEWDST` is a new layer key: no county reads DOR SEW2025 yet, so the
director also needs a label for it in `app/src/lib/districts.js` (as
`WATDST` has 'Water District') and an entry in
`election.DISTRICT_ADAPTER_LAYERS`. Both are outside this package's fence.

Point queries, 2026-10-08 (Census geocoder, Current vintage; DOR
`WADOR_PropertyTax/MapServer` layers 17 PUD / 11 HSP / 20 SCH / 21 SEW;
county layers named):

| Address | Census place | PUD2025 | HSP2025 | SCH2025 | SEW2025 | County layer |
|---|---|---|---|---|---|---|
| 714 W Pine St, Newport | Newport city | `1` | `1` | `56` | none | commission `Commissioner - 02` |
| 111 Calispell Ave, Cusick | Cusick town | `1` | `1` | `59` | none | commission `Commissioner - 03` |
| 201 Main St, Ione | Ione town | `1` | `2` | `70` | none | commission `Commissioner - 03` |
| 305 Park St, Metaline Falls | Metaline Falls town | `1` | `2` | `70` | none | commission `Commissioner - 03` |
| 4571 State Route 211, Newport (Sacheen Lake) | none | `1` | `1` | `56` | `3` | Water_Sewer `Sacheen`; precinct `Sacheen` |
| 62 Schaefers Beach Dr, Newport | none | | `1` | | `3` | Water_Sewer `Sacheen` |
| 636 Mountain View Dr, Newport | none | | | | `3` | Water_Sewer `Sacheen` |
| 1722 Kirkpatrick Rd, Elk | none | `1` | `1` | `62` | none | School_Districts `Riverside Joint #416/062`; precinct `Fertile Valley South` |
| 3441 Allen Rd, Elk | none | | | `62` | | |

A blank cell was not queried. All are LD 7 and CD 5 (Census). Suggested live checks:
4571 State Route 211, Newport (hospital bonds and Sacheen Lake levy);
1722 Kirkpatrick Rd, Elk (hospital bonds and Riverside levy);
201 Main St, Ione (no local measure: Hospital District No. 2).

## Sources

VoteWA guide records and candidate list; the county pamphlet, sample ballot
and district resolutions (scanned, no text) under `raw/pend-oreille/`; SOS
precinct exports (2020, 2022, 2024), the VoteWA results API for August 4,
the PDC summary and DOR's 2025 levy detail under `raw/pend-oreille/`; RCW
pointers under `raw/statutes/`; The Miner (Newport; its site is
`pendoreillerivervalley.com`, since `newportminer.com` no longer resolves)
and Spokesman-Review stories under `raw/news/`, `raw/candidates/` and
`raw/measures/`; campaign sites; PUD board minutes.

## Known gaps

- Brandy Parker Warren's materials state no specific tax, spending or
  land-use positions, and she has not addressed the Usk data center; she is
  scored on `experience` only.
- No rubric axis applies to the PUD race (category `PublicUtility`); it
  ships with descriptions and no scores.
- Robin R. McCroskey (District Court), Tammie Ownbey, Nicole Dice: pamphlet
  statements and results only.
- The Miner rate-limits scripted requests (HTTP 429); article ids 5372-5453
  and 5518-5542 were not indexed, so earlier spring coverage may be missed.
  The Miner had not published commissioner-race candidate profiles as of
  2026-10-08.
- Hospital taxpayer credit: the April Spokesman-Review story says up to
  $500 a year; the Miner (June, July, October) says the cap was raised to
  $750. The records use $750.
