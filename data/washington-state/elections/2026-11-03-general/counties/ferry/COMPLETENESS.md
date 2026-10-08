# Ferry County Completeness Note

Election: 2026 Washington general election, November 3, 2026 (VoteWA
election 899, county code 10).

Status (#32): shipped at Full County Coverage in
`APP_PACKAGES["2026-11-03-general"]["counties"]`, with its elections office
(`https://www.ferry-county.com/departments/auditor/index.php`) and its
VoteWA guide (`countyGuides.ferry`, `c=10`); no pamphlet. No layer was
added; `COUNTY_COUNCIL` and `EMSDST` were re-probed. CD 5 and LD 7 ship with
Spokane's research and the PUD No. 1 #3 seat with Okanogan's; the ship pass
corrected two display lines of Okanogan's scoring for that seat (see Known
gaps). Live ballots on 2026-10-08, each `full_county` with no missing layer
and the 15 contests (the PUD seat included) and no local measure: 350 E
Delaware Ave, Republic and 39 Shortcut Rd, Inchelium. The paragraphs below
describe the package as researched.

Research package for #32 (county wave 7). Contests are built by
`pipeline/build_votewa_lite_data.py --county ferry` from the VoteWA
candidate list (`raw/votewa/candidate-list.csv.url`, 31 rows) and the
overrides in that script's `ELECTION_MEASURES["2026-11-03-general"]["ferry"]`,
checked against:

- the Ferry County Auditor's general sample ballot
  (`raw/ferry/sample-ballot.pdf.url`, `https://www.ferry-county.com/SampleBallot.pdf`,
  linked as "2026 General" under Sample Ballots on the Auditor's public
  records page, `raw/ferry/auditor-public-records.html.url`; text in
  `interim/pdf-text/sample-ballot.txt`). It is a single card style (CS 17)
  carrying every race below;
- VoteWA's online voters' guide for the county
  (`https://voter.votewa.gov/genericvoterguide.aspx?e=899&c=10`; race index
  `raw/votewa/voter-guide/guide.json.url`, race records
  `race-<id>.json.url`, text in `interim/voter-guide-text/`).

Both list exactly the export's races and the three statewide measures, and
**no local measure**. Ferry printed a local pamphlet for the August primary
(`raw/ferry/primary-local-voters-pamphlet.pdf.url`, cited only for
candidates' primary statements, which match their general statements) but
none for the general; the Auditor's page still showed "Next Election: August
Primary 2026" on 2026-10-08. The primary's two EMS levies (EMS District 1
and City of Republic, Resolutions 2025-03 and 2025-04) were decided in
August and are not on this ballot.

The builder reports `full_county` with no unresolvable layer.

## What is on the ballot

15 contests (6 contested, 9 uncontested) and 0 local measures. The five
Supreme Court contests and the three statewide initiatives are dropped by
the builder and ship from the statewide package.

| Kind | Contests | Contested | Uncontested | Scope | Researched |
|---|---|---|---|---|---|
| U.S. Representative (CD 5) | 1 | 1 | 0 | `CONGDST` `5` | Spokane package |
| LD 7 Senator | 1 | 1 | 0 | `LEGDST` `7` | Spokane package |
| LD 7 Rep. Pos. 1, Pos. 2 | 2 | 0 | 2 | `LEGDST` `7` | Spokane package (info-only) |
| County Commissioner #2 | 1 | 1 | 0 | `COUNTY` | here |
| Clerk, Sheriff | 2 | 2 | 0 | `COUNTY` | here |
| Assessor, Auditor, Prosecuting Attorney, Treasurer | 4 | 0 | 4 | `COUNTY` | here (info-only) |
| District Court Judge | 1 | 0 | 1 | `COUNTY` | here (info-only) |
| Ferry/Pend Oreille/Stevens Superior Court Pos. 2 (unexpired) | 1 | 0 | 1 | `COUNTY` | here (info-only) |
| Court of Appeals Div. III, Dist. 1, Pos. 2 | 1 | 0 | 1 | `COUNTY` | here (info-only) |
| Ferry County PUD No. 1 Commissioner #3 | 1 | 1 | 0 | `COUNTY` | Okanogan package |

Every Ferry address geocoded below is in CD 5 and LD 7.

## District scoping

- **Commissioner #2**: Ferry is a non-charter county under 400,000, so
  commissioners are nominated by district and elected by the voters of the
  whole county (RCW 36.32.040, RCW 36.32.050(1); `raw/ferry/rcw-36.32.*.html.url`).
  The SOS precinct exports put Commissioner #1 and #3 (2020), #2 (2022) and
  #1 and #3 (2024) on all 19 precincts, while the 2026 primary's #2 race
  reported 7 of 19 units (`raw/ferry/votewa-results-20260804.json.url`).
  VoteWA lists the race as `Countywide`. Scope `COUNTY`; the override keeps
  the primary's contest name, so the slug
  (`ferry-ferry-county-commissioner-district-2-county-commissioner-2`) and
  primary dossiers carry forward.
- **District Court**: one county-wide court with one judge (2022 and 2024
  races on all 19 precincts). Override names it `Ferry County District Court`
  with category `Judicial`.
- **Superior Court Pos. 2** and **Court of Appeals III-1 Pos. 2**: generic
  rule, `COUNTY` (Ferry's part of each electorate). Each is its own
  information-only copy here (Stevens and Spokane hold their own copies).
- **Ferry County PUD No. 1 Commissioner #3** (Andrew Pooler, Doug Aubertin):
  VoteWA district `PUD (COUNTYWIDE)`. The PUD covers all of Ferry County:
  WA DOR PUD2025 (layer 17 of
  `https://webgis.dor.wa.gov/arcgis/rest/services/Programs/WADOR_PropertyTax/MapServer`)
  has one Ferry polygon, `DISTATTRIB` `1`, whose `Shape_Area`
  (12,939,379,609) equals the sum of Ferry's SCH2025 polygons and of its
  TCA2025 (layer 23) polygons other than `8888`. That `8888` code (no taxing
  district) also covers part of Inchelium: 39 Shortcut Rd, Inchelium answers
  TCA `8888` and **no PUD2025 feature**, so DOR's layer cannot be used to
  scope the seat. The election results settle it: the whole PUD elects each
  commissioner (RCW 54.12.010(3), `raw/ferry/rcw-54.12.010.html.url`), and
  the 2020 (#3), 2022 (#1) and 2024 (#2) PUD races were on all 19
  precincts, Inchelium included, with per-precinct totals close to the
  county-wide races' (Inchelium 138 vs 140, 42 vs 44, 73 vs 81). Scope
  `COUNTY`. The PUD also reaches eight northeastern Okanogan precincts
  (about 325 voters), where Okanogan's copy of the seat stays `PUDDST` and
  hidden.

  The Ferry contest keeps the generic names (district `Public Utility
  District Commissioner District 3`, office `Public Utility Commissioner
  #3`), which are exactly Okanogan's, so `shared_contests.contest_key` gives
  both `("NAMED", "public utility district commissioner district 3",
  "public utility commissioner 3")` and the research plan reports it
  researched in `okanogan/okanogan-public-utility-district-commissioner-district-3-public-utility-commissioner-3`
  (`candidates_missing: []`). It is not re-researched here. The plan lists
  no other package with that key. The names do not say "Ferry"; renaming
  would break the match.

### Layers each scope needs

No general scope needs a county layer: every Ferry contest is `COUNTY`,
`CONGDST` or `LEGDST`, and there are no local measures.

| Scope | Layer | In `COUNTY_LAYERS.ferry` | Needed by a general scope |
|---|---|---|---|
| `CONGDST`, `LEGDST`, `CITY` | Census geocoder | built in | CD 5, LD 7 |
| `COUNTY_COUNCIL` | `https://services8.arcgis.com/BBejpmYP0j5q6NLc/arcgis/rest/services/Political_Boundaries/FeatureServer/0` (`CommisionersDistricts`), attr `DISTRICT` (values 1, 2, 3) | yes | no (commissioner elected county-wide) |
| `EMSDST` | DOR EMS2025, layer 6, `DISTATTRIB` (Ferry values `1`, `3`, `REP`) | yes | no (no EMS measure in the general; the archived primary uses it) |

Both existing layers re-probed alive on 2026-10-08. Point queries (Census
geocoder `Public_AR_Current` / `Current_Current`, then each layer with the
returned x/y):

| Address | Census place | CD/LD | `COUNTY_COUNCIL` | EMS2025 (6) | FIR2025 (7) | HSP2025 (11) | LIB2025 (12) | PUD2025 (17) | SCH2025 (20) | TCA2025 (23) |
|---|---|---|---|---|---|---|---|---|---|---|
| 290 E Tessie Ave, Republic | Republic city | 5 / 7 | 2 | `REP` | none | `FERRY CO HEALTH` | `L` | `1` | `309` | |
| 350 E Delaware Ave, Republic | Republic city | 5 / 7 | 2 | `REP` | none | `FERRY CO HEALTH` | `L` | `1` | `309` | |
| 39 Shortcut Rd, Inchelium | none | 5 / 7 | 3 | none | none | none | none | **none** | none | `8888` |
| 10 Customs Rd, Curlew | none | 5 / 7 | 1 | none | `2` | `FERRY CO HEALTH` | `L` | `1` | `50` | `0006` |
| 11665 State Rte 21, Keller | none | 5 / 7 | 3 | none | none | `FERRY CO HEALTH` | `L` | `1` | `3` | |
| 151 Main St, Orient | none | 5 / 7 | 1 | `3` | `3` | none | `L` | `1` | `65` | |
| 19097 State Rte 21, Danville | none | 5 / 7 | 1 | none | `2` | `FERRY CO HEALTH` | `L` | `1` | `50` | |

(30 Customs Rd, Curlew did not geocode; 10 Customs Rd did.) The Census
coordinates endpoint puts the Inchelium point in Ferry County.

Suggested live-check addresses: 350 E Delaware Ave, Republic (commissioner
district 2, the main city) and 11665 State Rte 21, Keller or 39 Shortcut
Rd, Inchelium (district 3, the reservation side). Each should show the same
15 county, judicial, PUD, CD 5 and LD 7 contests and no local measure, with
`missing=[]` and `full_county`.

## Sources

Dossiers cite VoteWA's online voters' guide (`candidate.ashx`, no pages),
so the county's records ship no pamphlet pages; the director would link
the guide (`countyGuides.ferry`, `c=10`). The primary pamphlet is cited as
`official-voter-guide`, not `pamphlet`, so it yields no page links. Other
sources: VoteWA primary results, SOS precinct exports (2020, 2022, 2024),
the PDC campaign-finance summary (`raw/ferry/pdc-ferry-2026-candidates.json.url`,
every Ferry candidate on mini reporting), the Washington Supreme Court's
May 2026 ruling in the sheriffs' SSSB 5974 suit, the state court
directory, Ferry County EMS District No. 1 minutes, the WDFW Wolf Advisory
Group roster, the Statesman-Examiner (Webster) and the Spokesman-Review
(Staab, 2020). Local press is thin: the Ferry County View publishes its
stories only in a paywalled e-edition (its WordPress API has no news
posts), and the Spokesman-Review's search did not answer scripts.

## Research (#32)

Plan (`interim/research-plan.json`): 6 contested races.

- Researched elsewhere (3): CD 5 and LD 7 Senate (Spokane), PUD #3
  (Okanogan). The uncontested LD 7 House seats ship with Spokane's
  information-only scoring by the same key.
- Researched here (3), all carried from the primary and refreshed: Sheriff
  (Olson, Maycumber), Clerk (Breezee, Mott), Commissioner #2 (Berry, Dean).
  The primary's Jeremiah (Aymish) Adams did not advance.
- Information-only here (7): Assessor, Auditor, Prosecuting Attorney,
  Treasurer, District Court Judge, Superior Court Pos. 2, Court of Appeals
  III-1 Pos. 2 (`scoring/<slug>.json` with empty `scores`).

Refutation (`scoring/refutations/`, applied by `merge_scores.py`): 9
scores, 7 upheld, 2 adjusted (Olson `safety` -2 to -1; Breezee
`experience` -2 to -1), none refuted, no missing scores.

## Known gaps

- Olson, Berry and the uncontested county officers are pamphlet-only.
- Michael Golden says he has been Prosecuting Attorney since November 2024,
  but the November 2024 general elected Jesse D. Lamp unopposed; how Golden
  came to the office is not in the sources found. The dossier records both.
- The Okanogan package's scoring for the PUD seat, which ships here, says
  in `office_does` that the race "appears only for about 325 northeastern
  voters" on Okanogan's ballot, and describes Andrew Pooler as "running for
  his first elected office"; Pooler ran for Ferry County Commissioner #3 in
  2024 (lost 1,129 to 2,439, `raw/ferry/sos-results-20241105-ferry-precincts.csv.url`).
  Not edited here (outside this package). Fixed in the ship pass: the
  `office_does` clause is gone and Pooler's summary records the 2024 race,
  in Okanogan's scoring file, so both copies carry it.
