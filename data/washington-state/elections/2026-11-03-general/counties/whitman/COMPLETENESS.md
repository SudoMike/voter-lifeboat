# Whitman County Completeness Note

Election: 2026 Washington general election, November 3, 2026 (VoteWA
election 899, county code 38).

Research package for #30 (county wave 5), not yet shipped: the county is
not in `APP_PACKAGES["2026-11-03-general"]["counties"]`. Contests and
measures are built by `pipeline/build_votewa_lite_data.py --county whitman`
from the VoteWA candidate list (`raw/votewa/candidate-list.csv.url`) and the
overrides and measures in that script's
`ELECTION_MEASURES["2026-11-03-general"]["whitman"]`, checked against the
Whitman County Auditor's general sample ballot
(`raw/whitman/sample-ballot.pdf.url`, DocumentCenter 12666, text in
`interim/pdf-text/sample-ballot.txt`), the printed Official Local Voters'
Pamphlet (`raw/whitman/local-voters-pamphlet.pdf.url`, DocumentCenter
12618, 32 pages, PDF page = printed page, text in
`interim/pdf-text/local-voters-pamphlet.txt`), both linked from
`https://www.whitmancounty.gov/172/Current-Election`
(`raw/whitman/current-election.html.url`), and VoteWA's online voters'
guide for the county (`https://voter.votewa.gov/genericvoterguide.aspx?e=899&c=38`;
records under `raw/votewa/voter-guide/`, text in `interim/voter-guide-text/`).

The builder reports `full_county` for contests (every contest is
`CONGDST`, `LEGDST` or `COUNTY`). The measures need three DOR layers that
`COUNTY_LAYERS.whitman` does not read yet (below); until they are added the
assembler would mark the county `partial_county`.

## What is on the ballot

13 contests (3 contested, 10 uncontested) and 31 local measures, matching
the sample ballot. The five Supreme Court contests and the three statewide
initiatives are dropped by the builder and ship from the statewide package.

| Kind | Contests | Contested | Uncontested | Scope | Researched |
|---|---|---|---|---|---|
| U.S. Representative (CD 5) | 1 | 1 | 0 | `CONGDST` `5` | Spokane package |
| LD 9 Rep. Pos. 2 | 1 | 1 | 0 | `LEGDST` `9` | Spokane package |
| LD 9 Rep. Pos. 1 (Mary Dye) | 1 | 0 | 1 | `LEGDST` `9` | Spokane package (info-only) |
| Auditor | 1 | 1 | 0 | `COUNTY` | here |
| Assessor, Clerk, Coroner, Prosecuting Attorney, Sheriff, Treasurer | 6 | 0 | 6 | `COUNTY` | here (info-only) |
| County Commissioner District 3 | 1 | 0 | 1 | `COUNTY` | here (info-only) |
| District Court Judge Position No. 1 | 1 | 0 | 1 | `COUNTY` | here (info-only) |
| Court of Appeals Div. III, Dist. 2, Pos. 1 | 1 | 0 | 1 | `COUNTY` | here (info-only county copy) |

No LD 9 Senate seat is on the 2026 ballot. The plan names CD 5 and LD 9
Pos. 2 `researched_in` Spokane with no `candidates_missing`. LD 9 Pos. 1 is
uncontested and not in the plan; Spokane's info-only scoring
(`spokane-legislative-district-9-state-representative-pos-1.json`) matches it
by `shared_contests.contest_key`, so assembly ships it with Spokane's entry
and Whitman keeps no copy.

## District scoping

- Commissioner District 3: VoteWA's general export lists it as
  `Countywide` / `County` / `Commissioner 3`. Whitman is a non-charter county
  of about 48,000; RCW 36.32.040 nominates commissioners by district and RCW
  36.32.050(1) has them "elected by the qualified voters of the county"
  (subsection (2), district-only elections, applies only to noncharter
  counties of 400,000 or more). The 2026 primary counted the race in 28 of 81
  reporting units (`raw/whitman/votewa-results-20260804.json.url`); the SOS
  precinct exports put 'Whitman Commissioner 1' and '2' (2024) and
  'Whitman Commissioner 3' (2022) in all 80 voting precincts, the same set as
  the statewide races (`raw/whitman/sos-results-20241105-whitman-precincts.csv.url`,
  `...-20221108-...`). Scope `COUNTY`. The override keeps the primary's
  contest name, so the slug
  (`whitman-whitman-county-commissioner-district-3-commissioner-3`) matches
  the primary's.
- District Court Judge Position No. 1: one county-wide court. The override
  renames VoteWA's `District Court Judge Postion 1` to `Whitman County
  District Court` / `Judge Position No. 1`, category `Judicial`.
- Court of Appeals Division III, District 2 (Adams, Asotin, Benton,
  Columbia, Franklin, Garfield, Grant, Walla Walla, Whitman): the whole
  county; county-scoped information-only copy, as Benton ships.

## Layers the measures need

Point-checked 2026-10-08 (Census geocoder, `Public_AR_Current` benchmark,
`Current_Current` vintage; WA DOR
`https://webgis.dor.wa.gov/arcgis/rest/services/Programs/WADOR_PropertyTax/MapServer`,
tax year 2025 layers, attribute `DISTATTRIB`).

`COUNTY_LAYERS.whitman` in `app/src/lib/geo.js` already reads
`COUNTY_COUNCIL` (the county's `Whitman_County_BOCC_Districts___Feb__2026_WFL1/FeatureServer/10`,
`BOCC`: `2` at Pullman, `3` at Colfax; no general contest uses it), `FIRDST`
(DOR 7) and `PARKDST` (DOR 14). The brief said it had no layers; it has
these three. Proposed additions, none of which exists yet:

```js
{ key: 'CEMDST', url: `${DOR_TAX_DISTRICTS}/3/query`, attr: 'DISTATTRIB' },
{ key: 'LIBDST', url: `${DOR_TAX_DISTRICTS}/12/query`, attr: 'DISTATTRIB' },
{ key: 'SCHDST', url: `${DOR_TAX_DISTRICTS}/20/query`, attr: 'DISTATTRIB' },
```

and `CEMDST`, `LIBDST`, `SCHDST` in `election.DISTRICT_ADAPTER_LAYERS["whitman"]`
next to `CONGDST`, `LEGDST`, `CITY`, `COUNTY_COUNCIL`, `FIRDST`, `PARKDST`.

| Scope | Layer | Point | Result |
|---|---|---|---|
| `CITY` `Pullman` (no local measure) | Census Incorporated Places | 325 SE Paradise St, Pullman | `Pullman`; LIB, FIR, PKR, CEM: no feature; SCH `267` |
| `LIBDST` `L` | DOR 12 LIB2025 (one Whitman polygon) | 200 S Mill St, Colfax; 123 Crosby St, Tekoa; 120 E Main St, Palouse; 101 Steptoe Ave, Oakesdale; 101 Front St, St. John; 201 N Main St, Albion; 102 N Main Ave, LaCrosse | `L` |
| `LIBDST` (outside) | DOR 12 | 325 SE Paradise St, Pullman; 105 S Whitman Ave, Rosalia; 405 E California St, Garfield; Endicott interior (-117.6858, 46.9268); 705 Broadway St, Colton; 110 S Montgomery St, Uniontown | no feature |
| `SCHDST` `316` (Cheney SD 360, Whitman portion) | DOR 20 SCH2025 | interior point (-117.70, 47.24), north of St. John | `316`; OSPI's Cheney polygon (county copy, `Whitman_County_Elections_Precinct_Data___Feb__2026_WFL1/FeatureServer/46`, `LEAName` `Cheney School District`) at the same point; the county's copy of SCH2025 (same service, layer 62) labels `316` 'Cheney School Tax District' |
| `CITY` towns | Census places (`BASENAME`) | Albion 201 N Main St; Colton 705 Broadway St; Endicott interior point; Garfield 405 E California St; Oakesdale 101 Steptoe Ave; Palouse 120 E Main St; Rosalia 105 S Whitman Ave; St. John 101 Front St (`St. John`); Tekoa 123 Crosby St; Uniontown 110 S Montgomery St | the town's name |
| `FIRDST` `8` | DOR 7 (already read) | (-117.85, 46.80) and (-117.80, 46.85) near LaCrosse | `8` (the Town of LaCrosse itself: no feature) |
| `FIRDST` `14` | DOR 7 | 110 S Montgomery St, Uniontown; 705 Broadway St, Colton | `14` |
| `PARKDST` `1`, `2`, `3`, `4`, `7` | DOR 14 (already read) | LaCrosse 102 N Main Ave; Garfield; St. John; Oakesdale; Endicott interior point | `1`, `2`, `3`, `4`, `7` |
| `CEMDST` `1`, `2`, `3`, `4` | DOR 3 | Oakesdale; Garfield; St. John; Endicott interior point | `1`, `2`, `3`, `4` |

The Cheney School District reaches only a thin strip of northern Whitman
(precinct parts 5200.x Lamont Rural and 5400.x St. John Rural in the county's
precinct-splits layer 25 intersect OSPI's Cheney polygon); no addressable
point there geocoded, so the check is an interior point.

Suggested live-check addresses (`node pipeline/live_ballot.mjs ...`):

- `325 SE Paradise St, Pullman, WA 99163`: CD 5, LD 9, `CITY` Pullman; no
  local measure.
- `101 Steptoe Ave, Oakesdale, WA 99158`: Oakesdale Props 1-2, the library
  levy, Oakesdale Park District 4, Oakesdale Cemetery District 1.
- `110 S Montgomery St, Uniontown, WA 99179`: Uniontown Prop 1 and Fire
  District 14; no library levy.
- `101 Front St, Saint John, WA 99171`: St. John Props 1-2, library, St.
  John Park District 3, St. John Cemetery District 3.

Geocoder caveat: the Census geocoder places `304 N Main St, Colfax, WA
99111` (the elections office) and `400 N Main St, Colfax` in the Town of
Albion (-117.2475, 46.7916), not Colfax, so the app would show those
addresses Albion's two levies. `200 S Mill St, Colfax` geocodes correctly.
This is a geocoder range error the package cannot fix.

## Sources

Whitman County prints a local voters' pamphlet; its candidate statements
(pp. 5-11) and 23 of the 31 measures (pp. 12-31) are cited by page as edition
`local-voters-pamphlet`. Eight measures filed hardship waivers and appear
only on the ballot and in VoteWA's guide (Oakesdale Props 1-2, Fire District
14, Park Districts 2, 3, 4 and 7, Oakesdale Cemetery District 1). VoteWA's
online guide carries no statement text for the county candidates except
Flodin, Whelchel, Myers and Nelson. Local news: Whitman County Gazette
(wcgazette.com; its site search answers 403, so stories were found through
its `sitemap_stories1.xml`), Moscow-Pullman Daily News and Lewiston Tribune
(found through their sitemaps).

## Research

- Auditor (contested, open seat; Auditor Sandy Jamison retires): Crystn
  Guenthner and Kenneth Millar, both `moderate`, each scored on
  `experience` only (-2 high, +1 medium); the refutation upheld both. Both
  file under the PDC mini option; no campaign websites were found.
- Nine uncontested contests ship information-only (`scoring/<slug>.json`
  with empty scores): Assessor, Clerk, Commissioner District 3, Coroner,
  Prosecuting Attorney, Sheriff, Treasurer, District Court Judge Position
  No. 1 and Court of Appeals III-2 Pos. 1. All `moderate`.
- 31 measures: the library levy `rich`, the rest `moderate`. Every measure
  maps `taxes` only: +2 for the library lid lift, Fire District 14's lid lift
  ($0.633 to $1.08), and levies that do not continue one collected in 2026
  (Albion 1-2, Oakesdale 1-2, Tekoa, Uniontown, Garfield Park District 2,
  St. John Cemetery District 3); +1 for replacements and yearly
  continuations. The measure refutation upheld all 31 mappings and adjusted
  three display texts (Endicott Prop 2, Palouse Prop 3, Tekoa), fixed in
  `scoring/measures.json`.

## Known gaps

- Sheriff Brett J. Myers: the printed pamphlet (p. 11) says "States No Party
  Preference"; VoteWA, the sample ballot and the candidate list say "Prefers
  Republican Party". The package keeps VoteWA's value; the dossier records
  both.
- Myers, Treasurer Nelson and Judge Hart submitted no pamphlet statements;
  Millar's printed entry has only a statement.
- Prior-year levy history comes from SOS November precinct exports
  (2022-2025) and DOR levy detail; February and April 2026 special-election
  exports answered 404, so a district that levied through a spring 2026
  election may be read as having no 2026 levy (Oakesdale, Garfield Park 2,
  Endicott Park 7, St. John Cemetery 3).
- Tekoa's 2025 street levy (58.2% yes) and Rosalia's 2024 levy (59.0%) are
  read as failed from the 60% excess-levy requirement; no certification
  notice was found.
- St. John Cemetery District 3's estimated $0.16 rate implies about $125
  million of assessed value where DOR shows about $213 million; reported as
  given.
- Garfield Cemetery District 2's proposition is numbered 2026-1 on the ballot
  and pamphlet, 1 in VoteWA and 2027-1 in its explanatory statement.
- Cheney School District No. 360 Prop 2 is mapped +1 to match Spokane's
  score for the same levy, although the levy's dollars nearly double; if
  Spokane's mapping changes, Whitman's should follow.
