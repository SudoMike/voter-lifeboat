# Clallam County Completeness Note

Election: 2026 Washington general election, November 3, 2026 (VoteWA
election 899, county code 05).

Status (#29): researched, scored and refuted; not yet declared in
`APP_PACKAGES["2026-11-03-general"]["counties"]`. The builder
(`pipeline/build_votewa_lite_data.py --county clallam`) writes
`interim/app-contests.json` and `interim/app-measures.json` with
`coverage: "full_county"`, but two scopes use layers that
`app/src/lib/geo.js` `COUNTY_LAYERS.clallam` does not list yet (`DISTCRT`,
`SCHDST`, both with a working layer proposed below) and one uses a layer
no adapter can read yet (`PUDALL`, the PUD seat). Until the director adds
or resolves them, the assembler will mark Clallam `partial_county` and print
those scopes.

## Sources

- Candidate list: VoteWA GENERAL 2026 export (`raw/votewa/candidate-list.csv.{url,meta.json}`, 32 rows).
- Clallam County Auditor, 2026 November General Election page
  (`https://www.clallamcountywa.gov/2002/2026-November-General-Election`):
  official sample ballot and the printed combined state and local voters'
  pamphlet (`raw/clallam/{sample-ballot,local-voters-pamphlet}.pdf.url`,
  text in `interim/pdf-text/`), and the seven measure resolution packets
  (`raw/clallam/resolution-*.pdf.url`; the fire and school packets are
  scans with almost no text layer).
- VoteWA's online voters' guide for Clallam
  (`https://voter.votewa.gov/genericvoterguide.aspx?e=899&c=05`): records
  under `raw/votewa/voter-guide/`, text in `interim/voter-guide-text/`.
- Home Rule Charter (`raw/clallam/home-rule-charter.pdf.url`), the
  commissioners' July 14, 2026 Charter Review Commission press release, the
  SOS 2022 general results for Clallam and the Auditor's District Court and
  PUD commissioner district GIS layer metadata (`raw/clallam/`).

The dossiers cite the printed pamphlet's PDF pages (`local-voters-pamphlet
page NN`), so candidate and measure records carry pamphlet pages:
LD 24 Pos. 1 p27, Pos. 2 p28, Court of Appeals p35, Assessor p48, Auditor
p49, Commissioner D3 p50, DCD Director p51, Prosecuting Attorney p52,
Sheriff p53, Treasurer p54, District Court 1 p55, District Court 2 p56, PUD
p57; charter amendments pp42-47, QVSD p58, FD1 p59, FD2 pp60-61, FD6
pp62-63.

## What ships

14 contests (8 contested, 6 uncontested) and 7 local measures. The five
Supreme Court contests are dropped by the builder and ship from the
statewide package.

| Contest | Candidates | Status | Scope | Research |
|---|---|---|---|---|
| U.S. Representative, CD 6 | Randall, Fox | contested | `CONGDST` `6` | Pierce's package |
| LD 24 Representative Pos. 1 | Bernbaum, Pratt | contested | `LEGDST` `24` | Clallam (for all of LD 24) |
| LD 24 Representative Pos. 2 | Kelbon, Kuehn | contested | `LEGDST` `24` | Clallam (for all of LD 24) |
| Commissioner District 3 | Seegers, French | contested | `COUNTY` | Clallam (carried forward) |
| Assessor | Hancock, Price | contested | `COUNTY` | Clallam |
| Auditor | Shogren, Riggs | contested | `COUNTY` | Clallam |
| Director of Community Development | Emery | uncontested | `COUNTY` | Clallam, info-only |
| Prosecuting Attorney | Nichols | uncontested | `COUNTY` | Clallam, info-only |
| Sheriff | King | uncontested | `COUNTY` | Clallam, info-only |
| Treasurer | White | uncontested | `COUNTY` | Clallam, info-only |
| Court of Appeals Div. II, Dist. 2, Pos. 1 | Price | uncontested | `COUNTY` | Clallam, info-only (county-scoped copy; Kitsap and Thurston ship their own) |
| District Court 1 Judge | Schodowski, Murphy | contested | `DISTCRT` `1` | Clallam |
| District Court 2 Judge | Hanify | uncontested | `DISTCRT` `2` | Clallam, info-only |
| PUD No. 1 Commissioner District No. 2 | Paschall, Brackett | contested | `PUDALL` `1` | Clallam (carried forward; no rubric axis applies to PUD seats) |

LD 24 has only the two House seats on this ballot. CD 6 ships with Pierce's
scoring (`build_research_plan.py` shows no candidates missing).

| Measure | Scope |
|---|---|
| Clallam County Proposed Charter Amendment No. 1 (commissioner district town halls) | `COUNTY` |
| Clallam County Proposed Charter Amendment No. 2 (ethics review board) | `COUNTY` |
| Clallam County Proposed Charter Amendment No. 3 (full text of amendments in the local pamphlet) | `COUNTY` |
| Quillayute Valley School District No. 402 Prop. 1 ($34M Forks Middle School bonds) | `SCHDST` `402` |
| Fire Protection District No. 1 Prop. 1 (levy lid lift) | `FIRDST` `1` |
| Fire Protection District No. 2 Prop. 1 (EMS levy) | `FIRDST` `2` |
| Fire Protection District No. 6 Prop. 1 (levy lid lift) | `FIRDST` `6` |

The three charter amendments come from the 15-member Charter Review
Commission elected in November 2024. Its coroner amendment was on the
November 2025 ballot. Its other recommendations went to the board as
non-charter recommendations.

## Builder overrides

The `clallam` block of `ELECTION_MEASURES` carries an `overrides` dict:

- **County Commissioner Dist. No. 3**: kept as the primary's contest
  (`Clallam County Commissioner District 3`) so primary dossiers carry
  forward. Scope `COUNTY`: Home Rule Charter Section 2.20 (amended 2015 and
  2020) has commissioners "nominated by the voters from each of the three
  districts and elected by the voters countywide" (charter PDF page 8). The
  2022 general backs this up: the D3 race drew 39,943 votes and the
  county-wide DCD Director race 37,120.
- **District Court 1 and 2**: separate electoral districts, not county-wide.
  In the 2022 general District Court 1 drew 23,704 votes and District Court
  2 drew 1,940. They are named `Clallam County District Court 1` /
  `Clallam County District Court 2`, office `Judge`, scoped `DISTCRT` `1` and
  `2`.
- **PUD No. 1 Commissioner District No. 2**: renamed from the generic
  parse (`Public Utility District Commissioner District 1`, `PUDDST` `1`,
  which mistook the PUD's number for the district) to `Public Utility
  District No. 1 of Clallam County`. The whole PUD elects each commissioner
  in the general (RCW 54.12.010(3)). The PUD electorate is not the county,
  though: the City of Port Angeles precincts (Port Angeles 101-113) are in
  none of the PUD's commissioner districts (the Auditor's layer
  description lists every precinct in each district; the layer returns no
  feature at 223 E 4th St, Port Angeles). The 2022 District 1 PUD race drew
  28,129 votes against 39,943 county-wide. `COUNTY` would show the race to
  Port Angeles voters. The `PUDDST` key in `COUNTY_LAYERS.clallam` reads the
  commissioner district number (`Comm_Dist` 1-3), not PUD membership, so
  scoping to it would hide the race from two-thirds of the PUD. The seat is
  scoped to the honest layer `PUDALL` `1`. The renamed slug means the
  research plan does not detect the carry-forward; the dossiers carry the
  primary's forward by hand (`carried_forward_from`).
- The builder cannot mark `PUDALL` unresolvable from an override, so its
  line reads `full_county`. An `extra_notes` line says so.

## District scoping and proposed layers

`COUNTY_LAYERS.clallam` today: `COUNTY_COUNCIL` (county
`Commissioner_Districts`, `COM_DIST`), `PUDDST`
(`PUD_Commissioner_District_dissolve`, `Comm_Dist`), `FIRDST` (DOR FIR2025,
`DISTATTRIB`). The general uses only `FIRDST` from it. No general scope uses
`COUNTY_COUNCIL` (the commissioner race is county-wide) or `PUDDST` (see
above). DOR PUD2025 (layer 17) has a single Clallam polygon (`1`) that also
covers Port Angeles, so it is a tax layer, not the electorate. There are no
port or hospital district races or measures on this ballot (DOR PRT2025
returns `PORT ANGELES` county-wide; HSP2025 returns `1` at Forks and `2` at
Port Angeles and Sequim; neither is needed).

Point queries, 2026-10-09 (Census geocoder, Current vintage; DOR
`WADOR_PropertyTax/MapServer`, tax year 2025; Clallam GIS
`services8.arcgis.com/noCZ2SM2C0rVag8y`):

| Address | FIR2025 | SCH2025 | District_Court `DISTRICT` | PUD `Comm_Dist` | `COM_DIST` |
|---|---|---|---|---|---|
| 223 E 4th St, Port Angeles | none (city) | `121` | `1` | no feature | `2` |
| 152 W Cedar St, Sequim | `3` | `323` | `1` | `1` | `1` |
| 500 E Division St, Forks | `1` | `402` | `2` | `3` | `3` |
| 3851 S Mount Angeles Rd, Port Angeles | `2` | `121` | `1` | `3` | `2` |
| 7764 La Push Rd, Forks | `6` | `402` | `2` | `3` | `3` |

The county's `Precinct_Splits` layer agrees on fire (`Fire`), school
(`School`) and court (`Judicial`) at every address.

Proposed for `COUNTY_LAYERS.clallam` and
`election.DISTRICT_ADAPTER_LAYERS["clallam"]`:

1. `DISTCRT`: `https://services8.arcgis.com/noCZ2SM2C0rVag8y/arcgis/rest/services/District_Court/FeatureServer/0/query`,
   attr `DISTRICT` (`'1'`, `'2'`). The layer's description: "Clallam County
   Judicial Districts - i.e. District Courts 1 and 2."
2. `SCHDST`: DOR SCH2025 (`${DOR_TAX_DISTRICTS}/20/query`, `DISTATTRIB`),
   `402` at Forks, as Benton and Skagit use it.
3. `PUDALL` (PUD membership): no layer returns one value for the whole PUD.
   Options: (a) a `geo.js` presence read of
   `PUD_Commissioner_District_dissolve` (any feature means `'1'`); (b) read
   that layer's `created_user` (`cepperson_cc` on all three polygons), which
   works today but rests on edit metadata; (c) ship `partial_county` with
   `'clallam/PUDALL'` in `UNRESOLVABLE_SCOPES` and the seat hidden. Not
   `COUNTY`.

Suggested live checks: 223 E 4th St, Port Angeles (LD 24, county races,
District Court 1, charter amendments; no PUD race, no fire or school
measure) and 500 E Division St, Forks (District Court 2, PUD seat, QVSD
bonds, FD 1 levy). Add 3851 S Mount Angeles Rd, Port Angeles for FD 2 and
7764 La Push Rd, Forks for FD 6.

## Primary-package issue (not edited)

The archived primary scoped the same PUD race `PUDDST` `1` (the generic
parse). It was the District 2 primary, voted only in PUD Commissioner
District 2. With the adapter reading `Comm_Dist`, the primary showed it to
District 1 (Sequim) voters instead. The primary is frozen, so this is reported, not fixed.

## Known gaps

- Thin evidence: Assessor candidates Hancock and Price, Treasurer White and
  Court of Appeals Judge Price are `pamphlet-only`. The Assessor race is
  treated as open because incumbent Pam Rushton is not on the ballot; no
  retirement announcement was found.
- No candidate in any Clallam race has named a position on I-645, I-1 or
  I-638.
- No bar-association rating was found for the District Court 1 race.
- QVSD's own rate estimate ($1.94 per $1,000) is higher than the expiring
  high school bond ($1.34 in 2025), although the board chair said in March
  that the bond "will not increase the tax level". No source explains the
  gap.
- Primary results come from the VoteWA results API
  (`results.votewa.gov/.../clallam-county-wa/20260804`), because the SOS
  results URL returned 404. LD 24 percentages come from The Daily World.
- Web search quota ran out. Research used direct fetches of the Peninsula
  Daily News, Sequim Gazette, Forks Forum, PDC open data, leg.wa.gov web
  services and campaign sites.
