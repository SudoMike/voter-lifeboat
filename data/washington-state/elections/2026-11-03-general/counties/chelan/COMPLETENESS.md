# Chelan County Completeness Note

Election: 2026 Washington general election, November 3, 2026 (VoteWA
election 899, county code 04).

Status (#29): researched, scored and refuted; **not yet declared** in
`APP_PACKAGES["2026-11-03-general"]["counties"]`. The builder
(`pipeline/build_votewa_lite_data.py --county chelan`) writes
`interim/app-contests.json` and `interim/app-measures.json` with
`coverage: "full_county"`. Every contest scope is `CONGDST`, `LEGDST` or
`COUNTY`. One measure scope, `SCHDST` `246`, needs a layer that
`app/src/lib/geo.js` `COUNTY_LAYERS.chelan` does not list yet (see District
scoping); until the director adds it, assembly would mark Chelan
`partial_county` for that measure.

## Sources

- Candidate list: VoteWA GENERAL 2026 export
  (`raw/votewa/candidate-list.csv.{url,meta.json}`, 40 rows).
- Chelan County Elections' general election page
  (`https://www.co.chelan.wa.us/elections/pages/november-3-2026-general-election`):
  - Official Local Voters' Pamphlet (`raw/chelan/local-voters-pamphlet.pdf.url`,
    text in `interim/pdf-text/`). Candidate statements on PDF pages 6-15,
    Wenatchee School District Prop. 1 on pages 16-17, City of Cashmere
    Prop. 1 on page 18. Dossiers cite it as `local-voters-pamphlet page N`,
    so county candidates and both measures ship `pamphlet_pages`. The
    edition id is `local-voters-pamphlet`, as for Skagit and Cowlitz.
  - Sample ballot (`raw/chelan/sample-ballot.pdf.url`), the legal notice of
    election (`raw/chelan/legal-notice.pdf.url`), and the certified August
    primary results (`raw/chelan/primary-official-results.pdf.url`).
- VoteWA online voters' guide for Chelan County
  (`https://voter.votewa.gov/genericvoterguide.aspx?e=899&c=04`): records
  under `raw/votewa/voter-guide/`, text in `interim/voter-guide-text/`.
  The Court of Appeals candidate is not in the local pamphlet; her dossier
  cites the guide (no pages).
- State voters' pamphlet for Chelan: SOS Edition 02 (Chelan, Douglas,
  Grant, Kittitas). Not cited by Chelan's dossiers: every federal and
  legislative race is shipped with another package's research.

## What ships

19 contests (11 contested, 8 uncontested) and 2 local measures. The five
Supreme Court contests are dropped by the builder and ship from the
statewide package.

| Contest | Candidates | Status | Research |
|---|---|---|---|
| U.S. Representative, CD 8 | Schrier, Meline | contested | King's package |
| LD 7 State Senator | Short, McCoy | contested | Spokane's package |
| LD 7 Representative Pos. 1 | Engell | uncontested | Spokane's package (info-only) |
| LD 7 Representative Pos. 2 | Abell | uncontested | Spokane's package (info-only) |
| LD 12 Representative Pos. 1 | Burnett, Willoughby | contested | King's package |
| LD 12 Representative Pos. 2 | Steele, Adams | contested | King's package |
| Assessor | Port, Cornelius | contested | Chelan |
| Auditor (short and full term) | Brett, Cappell | contested | Chelan |
| Clerk | Arechiga, Young | contested | Chelan |
| Commissioner District No. 2 | Smith, Strand | contested | Chelan |
| Coroner (short and full term) | Crowe | uncontested | Chelan, info-only |
| Prosecuting Attorney | Sealby | uncontested | Chelan, info-only |
| Sheriff | Morrison, Langlow | contested | Chelan |
| Treasurer | Viall, Miller | contested | Chelan |
| Court of Appeals Div. 3, Dist. 3, Pos. 1 | Murphy | uncontested | Chelan, info-only (county-scoped copy; Yakima ships its own) |
| District Court Judge Pos. 1 | Volyn | uncontested | Chelan, info-only |
| District Court Judge Pos. 2 | Blackmon | uncontested | Chelan, info-only |
| Chelan PUD Commissioner District 1 | Frei, Young | contested | Chelan (PublicUtility: no rubric axis applies, so no scores) |
| Chelan PUD Commissioner District B (At Large) | Allen | uncontested | Chelan, info-only |

`build_research_plan.py chelan` shows CD 8 and LD 12 Pos. 1 and 2
`researched_in` King and LD 7 Senator `researched_in` Spokane, with no
candidates missing. LD 12 was assigned to Chelan in #29, but King's
package (shipped in #16) already scores both LD 12 seats, so Chelan did
not research them again.

Measures (both researched, scored and refuted):

| Measure | Scope |
|---|---|
| Wenatchee School District No. 246 Prop. 1 ($275M bonds: new Wenatchee High School, HVAC at seven schools) | `SCHDST` `246` |
| City of Cashmere Prop. 1 (public safety and government services levy lid lift) | `CITY` `Cashmere` |

## Builder overrides

The generic VoteWA parser stops on Chelan's PUD rows (District `PUD ALL`,
which carries no number). The Chelan block in `ELECTION_MEASURES` carries
an `overrides` dict, keyed by upper-cased (District, Race):

- `COMMISSIONER DISTRICT NO. 2` (District Type Countywide): kept as the
  primary's contest (`Chelan County Commissioner District 2`), so the slug
  matches and primary dossiers carry forward. Scope `COUNTY`: nominated by
  district in the primary, elected county-wide in the general (RCW
  36.32.040). In the 2022 general this race drew 33,392 votes of 34,530
  Chelan ballots (SOS results).
- `DISTRICT COURT JUDGE POSITION 1` and `2` (District Type County):
  category Judicial, `Chelan County District Court`, `Judge Position No.
  N`, scope `COUNTY`. There is one county-wide district court (2022 Judge
  #1: 29,039 votes).
- PUD `COMMISSIONER DIST 1` and `COMMISSIONER DIST B`: Public Utility
  District No. 1 of Chelan County, scope `COUNTY`. The PUD is county-wide:
  DOR PUD2025 (layer 17) returns `DISTATTRIB` `1` at Wenatchee, Cashmere,
  Leavenworth, Chelan and a Stehekin-area point. The whole PUD elects each
  commissioner in the general (RCW 54.12.010(3); 2022 District 3 drew
  28,626 votes).

## District scoping

Point queries, 2026-10-08 (Census geocoder, Current vintage; DOR
`WADOR_PropertyTax/MapServer`, tax year 2025):

| Scope | Layer | Address | Result |
|---|---|---|---|
| `CITY` `Cashmere` | Census places | 101 Woodring St, Cashmere | Cashmere |
| `SCHDST` `246` | DOR SCH2025 (20), **not** in `COUNTY_LAYERS.chelan` | 350 Orondo Ave, Wenatchee | `246` |
| (not in 246) | DOR SCH2025 (20) | 101 Woodring St, Cashmere | `222` |
| PUD county-wide | DOR PUD2025 (17) | five points above | `1` everywhere |
| Port county-wide (no race) | DOR PRT2025 (16) | same points | `CHELAN` everywhere |

`COUNTY_LAYERS.chelan` today lists only `COUNTY_COUNCIL` (the county's
`PW/Commissioner_Districts/MapServer/0`, `DIST_NO`; live: Wenatchee `1`,
Cashmere and Leavenworth `2`, Chelan `3`). No general scope uses it,
because the commissioner race is county-wide. **Proposed for the
director:** add `{ key: 'SCHDST', url: \`${DOR_TAX_DISTRICTS}/20/query\`,
attr: 'DISTATTRIB' }` to `COUNTY_LAYERS.chelan` and `SCHDST` to
`election.DISTRICT_ADAPTER_LAYERS["chelan"]`. Benton already reads this
layer.

Hospital districts (HSP2025) return `1` at Leavenworth and `2` at Chelan,
but no hospital measure is on this ballot. The Census geocoder puts
Wenatchee, Cashmere, Leavenworth, Chelan and Manson in LD 12 and CD 8.
LD 7 reaches only a sparsely populated part of the county; its races ship
with Spokane's research.

## Known gaps

- WebSearch quota ran out during research. Sources were found through
  outlet site searches (NCWLIFE, Wenatchee World, iFIBER One/Source ONE),
  PDC open data, SOS results and campaign sites. Wenatchee World and
  iFIBER One are metered: only readable opening paragraphs are cited, and
  each pointer's `notes` says so. chelanpud.org, cityofcashmere.org,
  Leavenworth Echo, Cashmere Valley Record and Lake Chelan Mirror blocked
  scripted access; the PUD commissioner pages are cited from Internet
  Archive copies.
- No candidate forums or debates were found for any county race.
- Thin evidence: Doug Miller (Treasurer) and Brian Brett (Auditor) have no
  campaign site. Clint Strand's council votes were not found individually.
  The PUD District 1 identification of Aaron Young with "former Chelan
  County Republican chairman Aaron Young" (NCWLIFE) rests on the matching
  party role, as his dossier says.
- City of Cashmere: no explanatory statement or committees in the
  pamphlet. Ordinance 1345 is a scan; the measure researcher OCR'd it for
  reading only. No council minutes or revenue estimate were found.
- Assessor race: Cornelius's campaign disputes the date of Port's
  appraiser accreditation. The dispute is recorded as his campaign's claim
  only.
