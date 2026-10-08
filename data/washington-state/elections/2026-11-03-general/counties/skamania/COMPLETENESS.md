# Skamania County Completeness Note

Election: 2026 Washington general election, November 3, 2026 (VoteWA
election 899, county code 30).

Research package for #32 (county wave 7). Not yet shipped: the director
declares it in `APP_PACKAGES["2026-11-03-general"]["counties"]`.

Contests are built by `pipeline/build_votewa_lite_data.py --county skamania`
from the VoteWA candidate list (`raw/votewa/candidate-list.csv.url`, 29 rows)
and the overrides in that script's
`ELECTION_MEASURES["2026-11-03-general"]["skamania"]`, checked against the
Skamania County Auditor's sample ballot
(`raw/skamania/sample-ballot.pdf.url`, text in
`interim/pdf-text/sample-ballot.txt`), the Local Voters' Pamphlet
(`raw/skamania/local-voters-pamphlet.pdf.url`, text in
`interim/pdf-text/local-voters-pamphlet.txt`) and VoteWA's online voters'
guide for the county (`https://voter.votewa.gov/genericvoterguide.aspx?e=899&c=30`;
records under `raw/votewa/voter-guide/`, text in `interim/voter-guide-text/`).
All three agree contest for contest. The Auditor's Current Election page
(`raw/skamania/current-election.html.url`) links the pamphlet
(`showpublisheddocument/19600`), the sample ballot (`/19606`) and the guide.

skamaniacounty.gov sits behind Akamai: it answers HTTP 403 to a bare
scripted User-Agent (curl `-A 'Mozilla/5.0'`, WebFetch) and 200 to full
browser request headers (Chrome User-Agent, Accept, Accept-Language,
Sec-Fetch-*). The pointer metas record the headers used. The pamphlet still
prints the old `www.skamaniacounty.org/elections` address; the live
elections page is
`https://www.skamaniacounty.gov/departments-offices/auditor/elections/current-election`.

The builder reports `full_county` with no UNRESOLVABLE layer: every scope is
`COUNTY` or a Census layer.

## What is on the ballot

12 contests (7 contested, 5 uncontested) and no local measure. The five
Supreme Court contests and the three statewide initiatives are dropped by
the builder and ship from the statewide package.

| Kind | Contests | Contested | Uncontested | Scope | Researched |
|---|---|---|---|---|---|
| U.S. Representative (CD 3) | 1 | 1 | 0 | `CONGDST` `3` | Clark package |
| LD 17 Rep. Pos. 1, Pos. 2 | 2 | 2 | 0 | `LEGDST` `17` | Clark package |
| Assessor, Clerk | 2 | 2 | 0 | `COUNTY` | here (carried from the primary, re-researched) |
| County Commissioner District No. 3 | 1 | 1 | 0 | `COUNTY` | here (carried from the primary, re-researched) |
| Auditor, Prosecuting Attorney, Sheriff, Treasurer | 4 | 0 | 4 | `COUNTY` | here (info-only) |
| District Court Judge | 1 | 0 | 1 | `COUNTY` | here (info-only) |
| PUD No. 1 Commissioner District No. 3 | 1 | 1 | 0 | `COUNTY` | here (new; no applicable axis) |

All of Skamania County is in CD 3 and LD 17; there is no LD 17 Senate race
in 2026. The research plan lists CD 3, LD 17 Pos. 1 and LD 17 Pos. 2 as
researched in Clark (`candidates_missing` empty for all three); no
legislative or congressional seat lacks an owner. No Court of Appeals seat
is on Skamania's ballot (none in the candidate list, the guide or the sample
ballot), and no port, fire, hospital, school or city race.

No local measures: the sample ballot lists only IP26-645, IL26-001 and
IL26-638; the pamphlet names the participating jurisdictions as "State of
Washington, Skamania County, Skamania County Public Utility District"; the
VoteWA guide's Measures category lists only 7325-7327. The builder's entry is
`"measures": []` with an `extra_notes` line saying so. (The primary's Home
Valley Water District levy was decided on August 4.)

## District scoping

- Skamania is a non-charter county. Commissioner District No. 3 is
  nominated by District 3 in the primary (the 2026 primary race reported 8 of
  23 units) and elected county-wide in the general (RCW 36.32.040,
  36.32.050(1); `raw/statutes/`). The sample ballot prints "Skamania County
  Commissioner District No. 3" under "ONLY REGISTERED VOTERS IN COUNTY ARE
  ELIGIBLE TO VOTE"; the county's Meet Your Commissioners page says "In the
  general election, all county voters are given an opportunity to select
  whom they would like to serve" (`raw/skamania/meet-your-commissioners.html.url`);
  the SOS precinct exports show the 2022 Commissioner #3 race and the 2020
  and 2024 Commissioner #1 and #2 races on all 23 precincts
  (`raw/skamania/sos-results-*.csv.url`). VoteWA's export lists the race as
  `Countywide` / `County` / `Commissioner No. 3`. Scope `COUNTY`; the override
  keeps the primary's names, so the slug
  (`skamania-skamania-county-commissioner-district-3-commissioner-no-3`)
  matches the primary's and its dossiers carried forward.
- District Court: one county-wide judge (2022: on all 23 precincts). The
  override names it `Skamania County District Court`, category `Judicial`.
- Public Utility District No. 1 of Skamania County covers the whole county:
  WA DOR PUD2025 (layer 17) has one Skamania polygon, `DISTATTRIB` `1`, whose
  area (9,058,178,385) equals the sum of Skamania's six SCH2025 polygons
  (`112-6`, `17-405`, `2`, `29`, `303`, `31`), and it answers `1` at every
  probe address below. Its commissioners are nominated by district and
  elected PUD-wide (RCW 54.12.010(3)); the 2020 Commissioner #3, 2022 #2 and
  2024 #1 races are on all 23 precincts. The sample ballot prints the race
  under "ONLY REGISTERED VOTERS IN PUBLIC UTILITY DISTRICT" on its single
  ballot style. Scope `COUNTY`, as Kittitas's and Jefferson's. The
  override names it `Public Utility District No. 1 of Skamania County
  Commissioner District 3`, so no other package's PUD seat matches its
  `NAMED` key (the generic rule would have produced `PUDDST` `3`, an
  unresolvable scope).
- The generic rule had named the commissioner race `Skamania County` /
  `Commissioner No. 3` (a new slug) and the District Court seat category
  `County`; both are overridden.

## Layers

`app/src/lib/geo.js` `COUNTY_LAYERS.skamania` today: `COUNTY_COUNCIL`
(`services3.arcgis.com/uKh72TYBlxpm42Cm/arcgis/rest/services/CommissionerDistrict/FeatureServer/0`,
`CommDist`) and `WATDST` (DOR 22). **No general scope uses either**: every
general contest is `COUNTY`, `CONGDST` or `LEGDST`, and there is no measure.
Both re-probed alive on 2026-10-08 (the archived primary uses them for its
Commissioner District 3 race and the Home Valley Water District levy):

- `CommissionerDistrict/FeatureServer/0?f=json`: name `CommissionerDistrict`,
  fields `OBJECTID`, `CommDist`, `Shape__Area`, `Shape__Length`, last edit
  2025-07-23; `where 1=1` returns three features, `CommDist` 1, 2, 3.
- DOR WAT2025 (layer 22): `DISTATTRIB` `1` (`COUNTYNAME` `SKAMANIA`) at the
  interior point (-121.77392, 45.71730) in Home Valley; no feature at the
  street addresses below.

DOR still lists tax year 2025 as its newest group; layer ids 3, 6, 7, 11, 12,
14, 16, 17, 20, 22 and 23 are unchanged.

### Point queries (2026-10-08, Census geocoder `Public_AR_Current`)

| Address | Comm. `CommDist` | DOR PUD (17) | DOR FIR (7) | DOR SCH (20) | DOR WAT (22) |
|---|---|---|---|---|---|
| 240 NW Vancouver Ave, Stevenson (courthouse) | `2` | `1` | none | `303` | none |
| 100 Cascade Dr, North Bonneville | `2` | `1` | none | `303` | none |
| 1101 Wind River Rd, Carson | `2` | `1` | `1` | `303` | none |
| 582 Cannavina Rd, Carson | `3` | `1` | `1` | `303` | none |
| 291 Shipherd Falls Rd, Carson | `3` | `1` | `1` | `303` | none |
| 71 Cooper Ave, Underwood | `3` | `1` | `3` | `17-405` | none |
| interior point (-121.77392, 45.71730), Home Valley | `3` | `1` | not queried | not queried | `1` |

At the Stevenson courthouse DOR also returns CEM2025 `1`, EMS2025 `1`,
HSP2025 `SKAMANIA`, LIB2025 `L` and PRT2025 `SKAM`; none is needed. The
Census geocoder matches no address on CBD Mall Dr, North Bonneville (City
Hall is 214), nor 1381 Willard Rd, Cook.

Suggested live checks: 240 NW Vancouver Ave, Stevenson, WA 98648 (all 12
contests, commissioner district 2) and 71 Cooper Ave, Underwood, WA 98651
(commissioner district 3; the same 12 contests). Expect `full_county` and
`missing=[]`; `COUNTY_COUNCIL` and `WATDST` resolve but no general record
uses them.

## Research

- Contested and researched here (4): Assessor (Moser, Spencer), Clerk (Cross,
  Munsch), Commissioner District 3 (Leckie, Mosbrucker), PUD Commissioner 3
  (Green, Dillon). The first three carried from the primary's one-line
  dossiers, which were re-researched; nothing was copied unverified.
- Researched elsewhere (3): CD 3, LD 17 Pos. 1 and Pos. 2 (Clark).
- Uncontested, information-only (5): Auditor (Waymire), Prosecuting Attorney
  (Kick), Sheriff (Scheyer), Treasurer (Sabo, interim since May 2026), District
  Court Judge (Lanz; open seat, Judge Ron Reynier is not on the ballot).
- The PUD race has no rubric axis (no axis lists PublicUtility) and ships
  with empty scores, as every other county's PUD race.

## Sources

The pamphlet's PDF pages are printed pages 35-44 (PDF page = printed page -
34); dossiers cite PDF pages as `local-voters-pamphlet page N (printed page
N+34)`: Assessor and Auditor 6, Clerk 7, Commissioner 8, Prosecuting
Attorney, Treasurer and Sheriff 9, District Court and PUD 10. Local news is
Columbia Gorge News (columbiagorgenews.com; much of its Skamania government
coverage comes from its Uplift Local / Gorge Documenters partnership). The
Skamania County Pioneer's old domains do not resolve or show a parking page. The Skamania County Chamber of Commerce's June 18 candidate
Q&A covers every contested local race except Mosbrucker, who did not answer.
PDC data come from data.wa.gov (`raw/pdc/`).

## Known gaps

- Paul H. Mosbrucker has no campaign website and gave no Chamber answer; his
  positions come from the pamphlet alone (`pamphlet-only`). His school board
  service is documented by a 2009 White Salmon Enterprise report.
- Cora Moser's central charge, that the incumbent assessor proposed selling
  the county fair parking lot to an industrial investor, appears only on her
  campaign site, which posts a CERB grant application and slides as scanned
  images (no text layer; not read). No independent account and no response
  from Spencer were found, so the dossiers attribute it to her.
- No record of the commissioners' votes on the annual 1% levy increase was
  retrieved (the county's resolutions list is loaded by script); Leckie's
  claim that he never voted for it is his own statement.
- Christopher Robert Lanz: pamphlet only; no rulings or bar ratings found.
