# Lincoln County Completeness Note

Election: 2026 Washington general election, November 3, 2026 (VoteWA
election 899, county code 22).

Status (#32): shipped at Full County Coverage in
`APP_PACKAGES["2026-11-03-general"]["counties"]`, with its elections office
(`https://www.lincolncountywa.com/312/Current-Future-Elections`), its
pamphlet (`pamphletPdfs['lincoln/local-voters-pamphlet']`, PDF page =
printed page) and its VoteWA guide (`countyGuides.lincoln`, `c=22`). No
layer was added; `CEMDST` was re-probed. CD 5 and LD 9 ship with Spokane's
research. Live ballots on 2026-10-08, each `full_county` with no missing
layer and the 12 contests and no local measure: 450 Logan St, Davenport and
211 W 2nd St, Sprague. The paragraphs below describe the package as
researched.

Research package for #32 (county wave 7).

Contests are built by `pipeline/build_votewa_lite_data.py --county lincoln`
from the VoteWA candidate list (`raw/votewa/candidate-list.csv.url`, 24
rows) and the overrides in that script's
`ELECTION_MEASURES["2026-11-03-general"]["lincoln"]`. They were checked
against the Lincoln County Auditor's general sample ballot and Local Voters'
Pamphlet (`raw/lincoln/{sample-ballot,local-voters-pamphlet}.pdf.url`,
linked from `https://www.lincolncountywa.com/312/Current-Future-Elections`;
text in `interim/pdf-text/`) and VoteWA's online voters' guide for the
county (`https://voter.votewa.gov/genericvoterguide.aspx?e=899&c=22`; race
index and records under `raw/votewa/voter-guide/`, text in
`interim/voter-guide-text/`). All three list the same 12 non-Supreme-Court
races. The county's web site moved from `co.lincoln.wa.us` (its elections
path now answers 404; the pamphlet still prints
`www.co.lincoln.wa.us/elections`) to `lincolncountywa.com`.

The builder reports `full_county` with no unresolvable layer.

## What is on the ballot

12 contests (2 contested, 10 uncontested) and no local measure. The five
Supreme Court contests and the three statewide initiatives are dropped by
the builder and ship from the statewide package.

| Kind | Contests | Contested | Uncontested | Scope | Researched |
|---|---|---|---|---|---|
| U.S. Representative (CD 5) | 1 | 1 | 0 | `CONGDST` `5` | Spokane package |
| LD 9 Representative Pos. 2 | 1 | 1 | 0 | `LEGDST` `9` | Spokane package |
| LD 9 Representative Pos. 1 (Mary Dye) | 1 | 0 | 1 | `LEGDST` `9` | Spokane package (info-only) |
| Assessor, Auditor, Clerk, Prosecuting Attorney, Sheriff, Treasurer | 6 | 0 | 6 | `COUNTY` | here (info-only) |
| Commissioner District No. 3 (elected county-wide) | 1 | 0 | 1 | `COUNTY` | here (info-only) |
| District Court Judge | 1 | 0 | 1 | `COUNTY` | here (info-only, judicial) |
| Court of Appeals Div. III Dist. 1 Pos. 2 | 1 | 0 | 1 | `COUNTY` | here (info-only county copy) |

All of Lincoln County is in the 9th Legislative District (the Record-Times,
May 14, 2026; every address probed below is LD 9) and the 5th Congressional
District. The research plan names CD 5 and LD 9 Pos. 2 `researched_in`
spokane, with no `candidates_missing`; LD 9 Pos. 1 is uncontested, so the
plan does not list it, and Spokane's package has an information-only scoring
file for it (`spokane-legislative-district-9-state-representative-pos-1`,
candidate `mary-dye`), which assembly ships for Lincoln's contest by
`shared_contests.contest_key`. No Lincoln copy of any legislative or
congressional race was written. The Court of Appeals seat is Lincoln's own
information-only copy, as Stevens, Spokane and Okanogan carry theirs.

Every county office drew a single Republican candidate at filing, and every
contest Lincoln researches is uncontested, so nothing here is scored:
each of the nine contests has a `scoring/<slug>.json` with empty `scores`,
`office_does` and `race_blurb`, and there are no refutation files (no scored
candidate-axis pair exists).

No local measures: the pamphlet's table of contents (p. 2) lists only the
county offices and the District Court; the sample ballot has no "Local
Issues" section; the guide's Measures category holds only the three
statewide initiatives (7325-7327); and no district crossing into Lincoln from
another county appears in the guide. (The primary's composite sample ballot
did print the Sprague-only Cemetery District 7 levy under "Local Issues".)
The builder block says so in `extra_notes`, with `"measures": []`, so the
package cannot read as "not curated". There is no `scoring/measures.json`.

## District scoping

- Commissioner District No. 3: Lincoln is a non-charter county under
  400,000, so commissioners are nominated by district (RCW 36.32.040) and
  elected by the voters of the whole county (RCW 36.32.050(1);
  `raw/statutes/`). The county's Commissioners page says the same ("All the
  voters in the county are given the opportunity in the general election to
  select the commissioner"). VoteWA's general export lists the race as
  `Countywide`; in the SOS precinct exports the 2022 District No. 3 general
  race and the 2020 and 2024 District No. 1 and No. 2 races are on all 46
  precincts, while the 2026 primary's District No. 3 race reported 16 of 46
  units (`raw/lincoln/`). Scope `COUNTY`. The override keeps the primary's
  contest name (`Lincoln County Commissioner District 3` / `County
  Commissioner District No. 3`), so the slug
  `lincoln-lincoln-county-commissioner-district-3-county-commissioner-district-no-3`
  matches the primary's. The primary scoped that race `COUNTY_COUNCIL` `3`
  (unresolvable; `lincoln/COUNTY_COUNCIL` is in `UNRESOLVABLE_SCOPES` for
  the primary); the general needs no commissioner layer.
- District Court: one county-wide court with one judge (2022 SOS export:
  all 46 precincts). The override names it `Lincoln County District Court`,
  category `Judicial`.
- Court of Appeals Division III District 1: Ferry, Lincoln, Okanogan, Pend
  Oreille, Spokane and Stevens counties (RCW 2.06.020); scoped `COUNTY` for
  Lincoln's copy.

### Layers the District Adapter needs

None beyond the Census layers. Every general scope is `COUNTY`, `CONGDST`
`5` or `LEGDST` `9`. `app/src/lib/geo.js` `COUNTY_LAYERS.lincoln` reads only
`CEMDST` (DOR CEM2025, layer 3, `DISTATTRIB`), which no general scope uses
(the archived primary's Cemetery District 7 levy does). Re-probed live on
2026-10-08: it answers, `7` at Sprague and `1` at Reardan.

Point queries, 2026-10-08 (Census geocoder `Public_AR_Current` /
`Current_Current`; DOR `WADOR_PropertyTax/MapServer`, layers 3 CEM2025, 6
EMS2025, 7 FIR2025, 11 HSP2025, 14 PKR2025, 17 PUD2025, 20 SCH2025; layer
12 LIB2025 has no Lincoln feature):

| Address (as matched) | Census place | CD | LD | CEM | EMS | FIR | HSP | PKR | PUD | SCH |
|---|---|---|---|---|---|---|---|---|---|---|
| 450 Logan St, Davenport | Davenport city | 5 | 9 | none | none | none | `3` | `3` | `1` | `207` |
| 101 E 1st Ave, Odessa | Odessa town | 5 | 9 | none | none | none | `1` | none | `1` | `105` |
| 14 NW Division St, Wilbur | Wilbur town | 5 | 9 | none | none | none | `3` | none | `1` | `200` |
| 11 S 3rd St, Harrington (matched as 11 N 3rd St) | Harrington city | 5 | 9 | none | none | `6` | `3` | none | `1` | `204` |
| 211 W 2nd St, Sprague | Sprague city | 5 | 9 | `7` | `SPRAGUE` | none | none | none | `1` | `8` |
| 302 S Lake St, Reardan | Reardan town | 5 | 9 | `1` | none | none | `3` | none | `1` | `9` |

(112 W 2nd St, Sprague; 125 E Spokane St and 110 W Broadway Ave, Reardan
did not geocode.)

Suggested live checks: 450 Logan St, Davenport, WA 99122 and 211 W 2nd St,
Sprague, WA 99032 (expect `full_county`, `missing=[]`, CD 5, LD 9, the 12
contests, no local measure).

## Sources

Lincoln County Auditor sample ballot, Local Voters' Pamphlet and elections
page; VoteWA guide records; SOS precinct results exports (2020, 2022, 2024)
and the VoteWA results API for the August 4, 2026 primary under
`raw/lincoln/`; PDC registrations (`raw/lincoln/pdc-lincoln-2026.json.url`);
the county's Commissioners and Prosecutors pages and the commissioners'
April 6, 2026 minutes; Lincoln County Record-Times (Davenport Times and
Odessa Record combined; hosted at odessarecord.com, found through its
`sitemap_stories1.xml`; most stories show only a public preview, which is
all that is cited) and Spokesman-Review stories (found through its monthly
story sitemaps) under `raw/news/`; RCW pointers under `raw/statutes/`. Search
engines were not usable from this session (web-search budget exhausted;
DuckDuckGo returned a bot challenge), so sources were found by direct
fetches and sitemaps only. The Davenport Times and Wilbur Register have no
separate live sites (`davenporttimes.net` does not resolve); their stories
appear on odessarecord.com.

## Known gaps

- Most county candidates submitted no pamphlet statement (Liebing,
  Coffman, Albertson, Lybbert-Hansen) and none has a campaign website; their
  dossiers rest on the pamphlet, results, and news previews.
- Ty Albertson's background beyond his December 2024 appointment story and
  one set of commission minutes was not found.
- Tracy Staab submitted no statement to the 2026 guide; her dossier relies
  on 2020 Spokesman-Review coverage.
- All eight county candidates report to the PDC under the mini-reporting
  option, so no contribution data exists.
