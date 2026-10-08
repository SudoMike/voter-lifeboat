# Kittitas County Completeness Note

Election: 2026 Washington general election, November 3, 2026 (VoteWA
election 899, county code 19).

Research package for #31 (county wave 6). Not yet shipped: the county is
not in `APP_PACKAGES["2026-11-03-general"]["counties"]`. Contests are built
by `pipeline/build_votewa_lite_data.py --county kittitas` from the VoteWA
candidate list (`raw/votewa/candidate-list.csv.url`) and the overrides in
that script's `ELECTION_MEASURES["2026-11-03-general"]["kittitas"]`. Every
row was checked against the Kittitas County Auditor's sample ballot
(`raw/kittitas/sample-ballot.pdf.url`) and local voters' pamphlet
(`raw/kittitas/local-voters-pamphlet.pdf.url`, 12 pages; text in
`interim/pdf-text/`), and against VoteWA's online voters' guide for the
county (`https://voter.votewa.gov/genericvoterguide.aspx?e=899&c=19`;
records under `raw/votewa/voter-guide/`, text in
`interim/voter-guide-text/`). All four list the same 16 non-Supreme-Court
races.

The builder reports `full_county` with no unresolvable layer. It cannot see
`geo.js`: the two District Court seats need one new layer (`DISTCRT`,
below) before the county can ship at full coverage.

## What is on the ballot

16 contests (5 contested, 11 uncontested) and no local measures. The five
Supreme Court contests and the three statewide initiatives ship from the
statewide package.

| Kind | Contests | Contested | Uncontested | Scope | Researched |
|---|---|---|---|---|---|
| U.S. Representative (CD 8) | 1 | 1 | 0 | `CONGDST` `8` | King package |
| LD 13 State Senator | 1 | 0 | 1 | `LEGDST` `13` | Grant package (info-only) |
| LD 13 Representative Pos. 1, Pos. 2 | 2 | 2 | 0 | `LEGDST` `13` | Grant package |
| Coroner (short and full term), Prosecuting Attorney, Sheriff | 3 | 3 | 0 | `COUNTY` | here |
| Assessor, Auditor, Clerk, Treasurer | 4 | 0 | 4 | `COUNTY` | here (info-only) |
| Commissioner District 3 (elected county-wide) | 1 | 0 | 1 | `COUNTY` | here (info-only) |
| Court of Appeals Div. III Dist. 3 Pos. 1 | 1 | 0 | 1 | `COUNTY` | here (info-only county copy) |
| District Court Judge, Lower and Upper County | 2 | 0 | 2 | `DISTCRT` | here (info-only) |
| PUD No. 1 Commissioner District 1 | 1 | 0 | 1 | `COUNTY` | here (info-only) |

The research plan names CD 8 `researched_in` king and LD 13 Pos. 1 and Pos.
2 `researched_in` grant, each with no `candidates_missing`. LD 13 Senator
(Alex Ybarra) is uncontested and not in the plan; Grant's package has an
information-only scoring file for it. No Kittitas copy of any of those four
races was written.

Split of the 16: 4 researched elsewhere (CD 8, LD 13 Senate, Pos. 1, Pos. 2);
3 contested county races carried from the primary (Coroner, Prosecuting
Attorney, Sheriff: the primary dossiers were thin and every claim was
re-sourced); 9 new to the general, all uncontested and information-only
(Assessor, Auditor, Clerk, Commissioner District 3 and Treasurer were
unopposed in the primary and have no primary dossiers; the Court of Appeals,
both District Court seats and the PUD seat were not on the primary ballot).

No local measures: the sample ballot and pamphlet list only the statewide
measures, the pamphlet's contents list (p. 2) names candidates only, the
Auditor's Ballot Measures & Resolutions table
(`https://www.co.kittitas.wa.us/auditor/elections/current/default.aspx`)
lists no resolution for the general, and the VoteWA guide's measures
category holds only IP26-645, IL26-001 and IL26-638. The builder entry is
`"measures": []` with an `extra_notes` line saying so.

## District scoping

- Commissioner District 3: Kittitas is a non-charter county, so
  commissioners are nominated by district (RCW 36.32.040) and elected by the
  voters of the whole county (RCW 36.32.050(1);
  `raw/statutes/rcw-36.32.050.html.url`). VoteWA's general export lists the
  race as `Countywide`. The SOS precinct exports show the 2022 Commissioner 3
  race on all 48 precincts and the 2020 Commissioner 1 and 2 races on all 62
  (`raw/kittitas/sos-results-*.csv.url`), while the 2026 primary's District 3
  race reported 15 of 54 units (`raw/kittitas/votewa-2026-08-04-primary-results.json.url`).
  Scope `COUNTY`; the override keeps the primary's contest name, so the slug
  `kittitas-kittitas-county-commissioner-district-3-commissioner-3` matches
  the primary's.
- District Court: two electoral districts with one judge each (Kittitas
  County Code 2.08.010-.020, Ord. 2011-014; `raw/statutes/kcc-title-02.html.url`).
  Upper: Hyak, Easton, Mountain, Ronald, Roslyn, Cle Elum, Kachess, South Cle
  Elum, Peoh Point, Swauk, Teanaway, Westside. Lower: the rest (Ellensburg,
  Kittitas, Thorp, Vantage, ...). In the 2022 general each race was on its
  own precincts only (Lower 35 reporting units, Upper 15). The generic rule
  would have scoped both seats `COUNTY`, which would show each judge to the
  other district's voters; the overrides scope them `DISTCRT`
  `Lower District Court` / `Upper District Court`.
- PUD No. 1 of Kittitas County covers the whole county: WA DOR PUD2025
  (layer 17) has one Kittitas polygon, `DISTATTRIB` `1`, whose
  `Shape_Area` (13,045,746,521.3) equals the sum of Kittitas's SCH2025 and
  TCA2025 polygons; `1` at every address probed, Ellensburg included. The
  whole PUD elects each commissioner in the general (RCW 54.12.010(3)), and
  the 2020 Commissioner 1 race was on all 62 precincts, the 2022 Commissioner
  3 and 2024 Commissioner 2 races on all 48. Scope `COUNTY`. The Auditor's
  `PUD_Commissioner_Districts/FeatureServer/0` (`pud_comm_district_name`
  `District 1`-`3`) covers the county too; it is the nomination geography and
  is not needed.
- Court of Appeals Div. III Dist. 3 (Chelan, Douglas, Kittitas, Klickitat,
  Yakima; RCW 2.06.020): the whole county votes; scoped `COUNTY` as this
  package's own information-only copy (Yakima and Chelan have theirs).

### Layers the District Adapter needs

`app/src/lib/geo.js` `COUNTY_LAYERS.kittitas` reads `COUNTY_COUNCIL`
(Auditor `Commissioner_Districts/FeatureServer/7`,
`commissioner_district_nbr`) and `FIRDST` (DOR FIR2025). Both re-probed
alive on 2026-10-08; no general scope uses either. The general needs one
more:

| Key | URL | Attr | Used by |
|---|---|---|---|
| `DISTCRT` (add) | `https://services.arcgis.com/eSnyVpqwqWBADfzp/arcgis/rest/services/Court_Districts/FeatureServer/0/query` | `court_district_name` | Lower (`Lower District Court`) and Upper (`Upper District Court`) District Court seats |

The layer is the Auditor's "Court Districts" item (ArcGIS item
`ebc627b198074ad082c07be0f59b1405`, snippet "Upper - Lower court districts
designated"), whose description is the text of KCC 2.08.010: a
precinct-built district layer, like Snohomish's `Court_Districts`. It has
two features, `Upper District Court` (OBJECTID 1) and `Lower District Court`
(OBJECTID 3), whose areas sum to the county commissioner districts' total
(13.047e9 in the service's units). Without it the two seats are hidden and
the county would ship `partial_county` with `kittitas/DISTCRT` in
`UNRESOLVABLE_SCOPES`.

Point queries, 2026-10-08 (Census geocoder, Current vintage; Auditor layers
and DOR `WADOR_PropertyTax/MapServer` layers 7 / 17 / 20):

| Address | Census place | Court_Districts | Commissioner | FIR2025 | PUD2025 | SCH2025 |
|---|---|---|---|---|---|---|
| 205 W 5th Ave, Ellensburg | Ellensburg city | `Lower District Court` | `3` | `2` | `1` | `401` |
| 207 Main St, Kittitas (entered as 207 N Main St) | Kittitas city | `Lower District Court` | `1` | none | `1` | `403` |
| 10700 Thorp Hwy N, Thorp | Thorp CDP | `Lower District Court` | `2` | `1` | `1` | `400` |
| 719 E 3rd St, Cle Elum | Cle Elum city | `Upper District Court` | `2` | none | `1` | `404` |
| 201 S 1st St, Roslyn | Roslyn city | `Upper District Court` | `2` | none | `1` | `404` |
| 523 Lincoln Ave, South Cle Elum | South Cle Elum town | `Upper District Court` | `2` | none | `1` | `404` |
| 1893 Railroad St, Easton | Easton CDP | `Upper District Court` | `2` | `3` | `1` | `28` |

All seven are CD 8 and LD 13 (Census). Suggested live checks: 205 W 5th
Ave, Ellensburg (Lower District Court seat, no Upper) and 719 E 3rd St, Cle
Elum (Upper District Court seat, no Lower). Both should show CD 8, LD 13
(Senate, Pos. 1, Pos. 2), the eight county offices, the Court of Appeals
seat and the PUD seat, and no local measure.

## Sources

Sample ballot, local pamphlet and VoteWA guide records; SOS precinct
exports (2020, 2022, 2024) and VoteWA results API (August 4, 2026) under
`raw/kittitas/`; PDC summary (`raw/kittitas/pdc-kittitas-2026.json.url`);
Daily Record (Ellensburg) stories under `raw/news/` (found through the
site's own search, which answered scripted requests); campaign sites under
`raw/candidates/`; the Yakima Herald-Republic's 2025 appointment story for
Judge Murphy; RCW and Kittitas County Code pointers under `raw/statutes/`.
The Northern Kittitas County Tribune publishes only weekly headline lists
online (its July 2, 2026 list names a candidacy statement by Darryl Chepoda
Jr., its March 5 one by Ben Kokjer); the stories themselves are print-only
and were not used.

## Known gaps

- Darryl Chepoda Jr. (Sheriff) has no website, gave no contact details in
  the pamphlet and reports no PDC totals; his dossier rests on his pamphlet
  statement (`pamphlet-only`).
- Charlie Divine's dossier has his statement, website and PDC data but no
  news coverage of his positions.
- The League of Women Voters general-election forums (October 13 and 14,
  2026) had not happened when this package was researched.
- Assessor, District Court and PUD candidates are `pamphlet-only`.
