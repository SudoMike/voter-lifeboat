# Asotin County Completeness Note

Election: 2026 Washington general election, November 3, 2026 (VoteWA
election 899, county code 02).

Status (#31): shipped at Full County Coverage in
`APP_PACKAGES["2026-11-03-general"]["counties"]`, with its elections office
(`https://www.asotincountywa.gov/186/Current-Election`), its local pamphlet
(`pamphletPdfs['asotin/local-voters-pamphlet']`, cited by PDF page) and its
VoteWA guide (`countyGuides.asotin`, `c=02`). `COUNTY_LAYERS.asotin` reads
`PUDDST` (DOR PUD2025) and `RURALEMSDST` (the presence layer on DOR TCA2025
proposed below, `value: '2'`) beside `EMSDST`; `districts.js` names
`RURALEMSDST` '2' `Asotin County Rural EMS District No. 2`. CD 5 and LD 9
ship with Spokane's research. Live ballots on 2026-10-08, each
`full_county` with no missing layer: 829 5th St, Clarkston (PUD seat, no
local measure), 121 2nd St, Asotin (neither) and 992 Park Rd, Anatone
(Rural EMS levy, no PUD seat). The paragraphs below describe the package
as researched.

Research package for #31 (county wave 6). Contests and
measures are built by `pipeline/build_votewa_lite_data.py --county asotin`
from the VoteWA candidate list (`raw/votewa/candidate-list.csv.url`) and the
overrides and measures in that script's
`ELECTION_MEASURES["2026-11-03-general"]["asotin"]`. They were checked
against the following sources:

- The Asotin County Auditor's general sample ballot
  (`raw/asotin/sample-ballot.pdf.url`, DocumentCenter 18053). It is two
  scanned pages for precinct 001.02 Anatone with no text layer:
  `interim/pdf-text/sample-ballot.txt` is empty and the content was read
  by OCR in the agent's scratch space.
- The printed Local Voters' Pamphlet (`raw/asotin/local-voters-pamphlet.pdf.url`,
  DocumentCenter 18054, 12 PDF pages, text in
  `interim/pdf-text/local-voters-pamphlet.txt`).
- The Auditor's Current Election page, which links both
  (`https://www.asotincountywa.gov/186/Current-Election`,
  `raw/asotin/current-election.html.url`;
  `https://www.co.asotin.wa.us/` redirects to `asotincountywa.gov`).
- VoteWA's online voters' guide for the county
  (`https://voter.votewa.gov/genericvoterguide.aspx?e=899&c=02`). Records are
  under `raw/votewa/voter-guide/` and text in `interim/voter-guide-text/`.

**Pamphlet pages.** The pamphlet's printed page numbers run 37-48; PDF page
n is printed page n + 36. Dossiers cite PDF pages
(`local-voters-pamphlet page N`), as `pamphlet_refs.py` expects:

| PDF page | Content |
|---|---|
| 3 | Assessor |
| 4 | Auditor |
| 5 | Clerk |
| 6 | Commissioner District 3 |
| 7 | Prosecutor |
| 8 | Sheriff (both candidates) |
| 9 | Treasurer |
| 10 | District Court |
| 11 | PUD (both candidates) |
| 12 | Rural EMS levy |

The Court of Appeals seat is not in the local pamphlet; it cites the VoteWA
guide.

The builder reports `full_county` with no UNRESOLVABLE layer. Two scopes
need layers that `COUNTY_LAYERS.asotin` does not read yet (below). Until
they are added, the assembler would mark the county `partial_county`.

## What is on the ballot

13 contests (4 contested, 9 uncontested) and 1 local measure, matching the
sample ballot and the VoteWA guide. The builder drops the five Supreme
Court contests and the three statewide initiatives; they ship from the
statewide package.

| Kind | Contests | Contested | Scope | Researched |
|---|---|---|---|---|
| U.S. Representative (CD 5) | 1 | yes | `CONGDST` `5` | Spokane package |
| LD 9 Rep. Pos. 2 | 1 | yes | `LEGDST` `9` | Spokane package |
| LD 9 Rep. Pos. 1 (Mary Dye) | 1 | no | `LEGDST` `9` | Spokane package (info-only) |
| Sheriff | 1 | yes | `COUNTY` | here (scored) |
| PUD Commissioner District No. 1 | 1 | yes | `PUDDST` `1` | here (no applicable axis) |
| Assessor, Auditor, Clerk, Prosecutor, Treasurer | 5 | no | `COUNTY` | here (info-only) |
| County Commissioner District 3 | 1 | no | `COUNTY` | here (info-only) |
| District Court Judge | 1 | no | `COUNTY` | here (info-only) |
| Court of Appeals Div. III, Dist. 2, Pos. 1 | 1 | no | `COUNTY` | here (info-only county copy) |
| Rural EMS District No. 2 Prop. 1 | measure | | `RURALEMSDST` `2` | here |

There is no LD 9 Senate seat and no coroner race in 2026. The plan names CD 5
and LD 9 Pos. 2 `researched_in` Spokane with no `candidates_missing`. LD 9
Pos. 1 is uncontested and not in the plan. Spokane's info-only scoring
(`spokane-legislative-district-9-state-representative-pos-1.json`) matches it
by `shared_contests.contest_key`, as for Whitman. No City of Clarkston
measure is on the general ballot: the Clarkston EMS levy passed in August.

## District scoping

- **Commissioner District 3.** VoteWA lists it as `Countywide` / `County` /
  `COUNTY COMMISSIONER 3`. Asotin is a non-charter county of about 22,000.
  RCW 36.32.040 nominates commissioners by district. RCW 36.32.050(1) has
  them "elected by the qualified voters of the county"; subsection (2),
  district-only elections, applies only to noncharter counties of 400,000
  or more (`raw/asotin/rcw-36.32.0{40,50}.html.url`). The SOS precinct
  exports put Commissioner 1, 2 and 3 (2020), Commissioner 3 (2022) and
  Commissioner 1 and 2 (2024) on all 26 precincts
  (`raw/asotin/sos-results-*.csv.url`). The August 2026 primary's District
  No. 3 race reported 7 of 7 units (`raw/asotin/votewa-results-20260804.json.url`).
  Scope `COUNTY`. The override keeps the primary's contest name, so the
  slug matches the primary's
  (`asotin-asotin-county-commissioner-district-3-county-commissioner-3`).
- **District Court Judge.** One county-wide court. The override files
  VoteWA's `DISTRICT COURT JUDGE` as `Asotin County District Court` /
  `District Court Judge`, category `Judicial`.
- **Court of Appeals Division III, District 2.** Covers the whole county;
  shipped as a county-scoped information-only copy, as Benton, Grant,
  Whitman and Walla Walla do.
- **Asotin County PUD No. 1 (water and sewer).** The PUD is not the whole
  county. RCW 54.12.010(3): voters of the entire PUD elect each
  commissioner at the general election. The SOS exports report PUD
  Commissioner 1 (2020), 3 (2022) and 2 (2024) in the same 22 of 26
  precincts; ANATONE, ASOTIN #1, ASOTIN #2 and RURAL ASOTIN are outside.
  WA DOR PUD2025 (layer 17) has one Asotin polygon, `DISTATTRIB` `1`,
  extent -117.123 to -117.035, 46.338 to 46.430. Its tax code areas are
  0021 (Clarkston), 0023P and 0027P; 0027 and 0024 without the `P` are
  outside. The override scopes the seat `PUDDST` `1` and names it
  `Asotin County Public Utility District` / `Commissioner District No. 1`
  (the sample ballot's wording). The generic name would have been
  `Public Utility District Commissioner District 1`, which does not name a
  jurisdiction and could collide with Lewis's key. The precinct-part
  check (below) agrees with the 22 precincts: parts of W ASOTIN (004.03,
  004.06) and CLARKSTON HTS #5 (305.09, 305.12) are in, other parts of
  those precincts are out.
- **Rural EMS District No. 2.** This is not DOR EMS2025's Asotin `1`
  polygon:
  - The EMS2025 `1` polygon has the same area as Fire District 1 (FIR2025
    `1`). It reads `1` at 1406 16th Ave and 2075 Appleside Ct in Clarkston
    Heights and nothing at Anatone. DOR's 2025 levy detail
    (`raw/asotin/dor-all-county-levy-detail-2025.xlsx.url`) shows why. Its
    "EMS Dist #1" row, with assessed value $1,671,578,767, is exactly Fire
    District #1's assessed value. Its "EMS Dist #1 Special" row (AV
    $164,884,935, $0.12084 per $1,000) is the rural district.
  - The county's 2025 Tax Rates by tax code area (`raw/asotin/tax-rates-2025.docx.url`)
    put that $0.12084 in TCAs 25, 30 and 30F. Their regular rate is 5.0540
    against 6.0915 in TCAs 23/24/27, and 6.0915 - 5.0540 = 1.0375 = Fire
    District #1 0.79088 + EMS District #1 0.36745 - 0.12084. TCA 30F adds
    Blue Mountain Fire District (0.64675).
  - Those TCAs are the precinct parts that voted on the levy. In 2020:
    ANATONE, RURAL ASOTIN and CLARKSTON HTS #5 with 0 votes, whose part
    305.10 is TCA 0025 with no voters. In August 2026: 2 of 2 units.
  - KOZE describes the district as the county outside Clarkston and Fire
    District 1, from the south end of the fire district to Oregon
    (`raw/measures/.../koze-2026-08-27-ems-district-2-map.html.url`).

  The measure is scoped `RURALEMSDST` `2`.

## Layers each scope needs

Point-checked 2026-10-08 (Census geocoder, `Public_AR_Current` benchmark,
`Current_Current` vintage; WA DOR
`https://webgis.dor.wa.gov/arcgis/rest/services/Programs/WADOR_PropertyTax/MapServer`,
tax year 2025, `MapServer?f=json` still lists 2025 as the newest group).

`COUNTY_LAYERS.asotin` in `app/src/lib/geo.js` reads only `EMSDST` (DOR 6).
It re-probed alive: `CLAR` at 829 5th St and 1225 Highland Ave, Clarkston;
`ASOT` at 121 2nd St and 215 Filmore St, Asotin; `1` at 1406 16th Ave and
2075 Appleside Ct, Clarkston Heights. No general scope uses it; the
archived primary does (see Known gaps). Proposed additions:

```js
// Asotin County PUD No. 1, elected PUD-wide (RCW 54.12.010(3)): DOR PUD2025.
{ key: 'PUDDST', url: `${DOR_TAX_DISTRICTS}/17/query`, attr: 'DISTATTRIB' },
{
  // Asotin County Rural EMS District No. 2 (#31): DOR TCA2025 tax code areas
  // 0025, 0030 and 0030F, which carry the 'EMS Dist #1 Special' levy (DOR
  // levy detail 2025; county 2025 tax rates). Presence-only: any feature
  // means the district.
  key: 'RURALEMSDST',
  url: `${DOR_TAX_DISTRICTS}/23/query`,
  attr: 'DISTATTRIB',
  where: "COUNTYNAME = 'ASOTIN' AND DISTATTRIB IN ('0025','0030','0030F')",
  value: '2',
},
```

and `PUDDST` and `RURALEMSDST` in `election.DISTRICT_ADAPTER_LAYERS["asotin"]`
next to `CONGDST`, `LEGDST`, `CITY` and `EMSDST`.

| Scope | Layer | Point | Result |
|---|---|---|---|
| `CONGDST` `5`, `LEGDST` `9` | Census | every address below | CD `5`, LD `9` |
| `PUDDST` `1` | DOR 17 PUD2025 `DISTATTRIB` | 829 5th St, Clarkston (`Clarkston city`); 1225 Highland Ave, Clarkston; 1406 16th Ave, Clarkston (Heights, no place); 2075 Appleside Ct, Clarkston | `1` |
| `PUDDST` (outside) | DOR 17 | 121 2nd St and 215 Filmore St, Asotin (`Asotin city`); 992 Park Rd, Anatone; interior (-117.1335, 46.1347) Anatone | no feature |
| `RURALEMSDST` `2` | DOR 23 TCA2025 with the `where` above | 992 Park Rd, Anatone (Fields Spring State Park, TCA `0030`); interior points (-117.1335, 46.1347) `0030F`, (-117.24238, 46.10020) `0030`, (-117.34192, 46.16774) `0030` | a feature |
| `RURALEMSDST` (outside) | DOR 23 with the `where` | 829 5th St, Clarkston (TCA `0021`); 1406 16th Ave (`0023P`); 121 2nd St, Asotin (`0026`); (-117.02696, 46.30732) (`0027`, Fire District 1 part of the Anatone precinct) | no feature |

Precinct-part check: the SOS precinct parts for Asotin, from an ArcGIS
Online copy by Lewis-Clark State College GIS
(`https://services1.arcgis.com/1Wj8xAact2ptcedL/arcgis/rest/services/Asotin_Voters_V2_WFL1/FeatureServer/4`,
`PPartName`). This is not an official county layer and is not proposed;
the other layers in that service hold voter-level points and were not
used. One interior point per part was queried against DOR 17 and 23:

- PUD `1`: every Clarkston (201-208), Clarkston Heights (301-307 except
  305.10 and 305.11), South and West Clarkston (401-503) and Swallows Nest
  (005) part, and W Asotin parts 004.02, 004.03 and 004.06.
- Rural EMS TCAs: parts 001.02, 001.03, 001.05 and 001.06 (Anatone, 424
  voters), 003.01 and 003.02 (Rural Asotin) and 305.10 (no voters).
- Anatone parts 001.04 and 001.07 are TCA 0027 (Fire District 1) and do
  not get the levy, which matches the sample ballot for part 001.02
  carrying it.

Suggested live-check addresses (`node pipeline/live_ballot.mjs ...`):

- `829 5th St, Clarkston, WA 99403`: CD 5, LD 9, `CITY` Clarkston, PUD
  District 1 seat; no local measure.
- `1406 16th Ave, Clarkston, WA 99403`: Clarkston Heights, PUD seat; no
  local measure.
- `121 2nd St, Asotin, WA 99402`: City of Asotin; no PUD seat, no measure.
- `992 Park Rd, Anatone, WA 99401`: Rural EMS levy; no PUD seat. No
  street address in the Anatone townsite geocoded; the interior point
  (-117.1335, 46.1347) also returns the levy.

## Sources

The printed pamphlet carries statements for every county candidate and the
measure's ballot title, resolution and explanatory statement (no
arguments for or against). VoteWA's guide repeats them; it has no
statement text for the measure. Local news is KOZE (koze.com, found through
its `post-sitemap*.xml`). The Lewiston Tribune's articles answered 403 to
scripts and to WebFetch, so none are cited. Its sitemap shows headlines
on the sheriff race (including "Asotin County sheriff candidate files
lawsuit challenging new Washington law") and on the rural EMS levy.
Campaign finance is the PDC summary dataset (data.wa.gov `3h9x-7bvm`).

## Research

- **Sheriff** (contested, open seat; Sheriff John Hilderbrand is not
  running). Blake Richards and Monte Renzelman, both `rich`, carried from
  the primary dossiers and refreshed. Scores: Richards `safety` -2 high,
  `experience` 0 medium; Renzelman `experience` -1 high, `safety` -1 high.
  The refutation upheld all four scores. It flagged that Renzelman's
  experience basis quoted his campaign slogan, which the dossier did not
  carry; the slogan is now in the dossier with its source.
- **PUD Commissioner District No. 1** (contested, open seat; board
  president Judy Ridge, who won it in 2020, is not running). Joe Louis and
  Darcy Nelly, both `pamphlet-only`. No rubric axis applies to a
  `PublicUtility` contest, so the scoring file has empty scores, as for
  Lewis's PUD seat.
- **Nine uncontested contests ship information-only** (scoring files with
  empty scores; LD 9 Pos. 1 ships from Spokane):
  - Assessor, Auditor, Clerk, Prosecutor, Treasurer, Commissioner District
    3 and District Court Judge: `pamphlet-only`.
  - Court of Appeals III-2 Pos. 1 (Tyson R. Hill): `moderate`.
- **Rural EMS District No. 2 Prop. 1:** `rich`. Mapped `taxes` +2: the
  ceiling rises from $0.15 to $0.28 per $1,000 and the 2025 rate was
  $0.12. The same proposition failed in the August primary, 118 to 146.
  The measure refutation upheld the mapping and adjusted one phrase of
  `pro_summary` ("only dedicated funding"), fixed in `scoring/measures.json`.

## Known gaps

- **Archived primary misscoped.** The archived primary scoped the same
  Rural EMS District No. 2 proposition `EMSDST` `1` (the `COUNTY_CONFIG`
  comment says "DOR EMS polygon for the rural district carries DISTATTRIB
  '1'"). That polygon is EMS District #1 / Fire District 1, so the
  primary app showed the levy to Clarkston Heights voters and hid it from
  Anatone and Rural Asotin. The primary is frozen and outside this
  package's fence; reported, not changed.
- **Sample ballot.** It is image-only. Only precinct 001.02's style was
  checked by OCR; the other styles were checked through the VoteWA guide's
  race list.
- **Lewiston Tribune.** Its coverage is unreachable. The sheriff
  candidates' SB 5974 positions come from KOZE and the pamphlet; the
  lawsuit Richards refers to ("challenging Olympia") is not documented
  beyond the Tribune's headline.
- **PUD candidates.** No campaign websites or news coverage were found
  for Louis or Nelly. The 2020 Joe Louis is identified as the same person
  by the PDC filer name (Joseph Lee Louis) in 2020 and 2026.
- **Tax code areas.** Rural EMS membership is read from DOR's 2025 tax code
  areas. A boundary change after 2025 would not be reflected. TCAs 28 and
  29 appear in the county's rate table but have no DOR polygon; their rates
  equal TCA 27's (Fire District 1), so they are not in the district.
