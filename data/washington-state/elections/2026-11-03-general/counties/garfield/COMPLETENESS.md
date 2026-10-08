# Garfield County Completeness Note

Election: 2026 Washington general election, November 3, 2026 (VoteWA
election 899, county code 12).

Status (#32): research package, not yet shipped. Garfield is not in
`APP_PACKAGES["2026-11-03-general"]["counties"]`; the ship pass declares it.

Contests are built by `pipeline/build_votewa_lite_data.py --county garfield`
from the VoteWA candidate list (`raw/votewa/candidate-list.csv.url`) and
the overrides in that script's `ELECTION_MEASURES["2026-11-03-general"]["garfield"]`.
They were checked against:

- VoteWA's online voters' guide for the county
  (`https://voter.votewa.gov/genericvoterguide.aspx?e=899&c=12`, HTTP 200 on
  2026-10-08). The race index and every county and Court of Appeals race
  record are under `raw/votewa/voter-guide/`, with text in
  `interim/voter-guide-text/`.
- The August 4, 2026 primary results (`raw/garfield/votewa-results-20260804.json.url`)
  and the Secretary of State's precinct exports for 2018, 2020, the 2022 and
  2024 primaries and generals (`raw/garfield/sos-results-*.csv.url`).

**Sample ballot and pamphlet not checked.** `garfieldcountywa.gov` (and
`co.garfield.wa.us`, which redirects to it) answers every scripted request
with a Cloudflare challenge (HTTP 403, `cf-mitigated: challenge`), including
full browser request headers, and WebFetch gets the same 403. The Internet
Archive was offline. So the county's sample ballot, any local pamphlet and
its elections page could not be read or pointed to. The VoteWA guide is the
official listing used here. It shows no local measure, and the East
Washingtonian's filing and primary coverage mentions none. No Garfield
general pamphlet edition is cited, so every record would link the VoteWA
guide (`countyGuides.garfield`, `c=12`).

The builder reports `full_county`, 13 contests, 0 measures, with no
UNRESOLVABLE layer. Every scope is `COUNTY` or a Census layer, so
`COUNTY_LAYERS.garfield` (empty in `geo.js`) needs no entry for the general.

## What is on the ballot

13 contests (6 contested, 7 uncontested) and no local measure. The builder
drops the five Supreme Court contests and the three statewide initiatives;
they ship from the statewide package.

| Kind | Contests | Contested | Scope | Researched |
|---|---|---|---|---|
| U.S. Representative (CD 5) | 1 | yes | `CONGDST` `5` | Spokane package |
| LD 9 Rep. Pos. 2 | 1 | yes | `LEGDST` `9` | Spokane package |
| LD 9 Rep. Pos. 1 (Mary Dye) | 1 | no | `LEGDST` `9` | Spokane package (info-only) |
| County Commissioner District 1 (2-year unexpired term) | 1 | yes | `COUNTY` | here (scored) |
| County Commissioner District 3 | 1 | yes | `COUNTY` | here (scored) |
| Sheriff | 1 | yes | `COUNTY` | here (scored) |
| Treasurer | 1 | yes | `COUNTY` | here (scored) |
| Assessor, Auditor, Clerk, Prosecutor | 4 | no | `COUNTY` | here (info-only) |
| District Court Judge | 1 | no | `COUNTY` | here (info-only) |
| Court of Appeals Div. III, Dist. 2, Pos. 1 | 1 | no | `COUNTY` | here (info-only county copy) |

The research plan names CD 5 and LD 9 Pos. 2 `researched_in` Spokane with no
`candidates_missing`. LD 9 Pos. 1 is uncontested and not in the plan;
Spokane's info-only scoring matches it by `shared_contests.contest_key`, as
for Asotin and Whitman. There is no LD 9 Senate seat in 2026.

The Treasurer race became contested after the primary: Katie Nagle ran as a
write-in (230 write-in votes to Tereasa Summers's 593) and was added to the
general list on 2026-08-19 (the CSV's Filing Date).

## District scoping

- **Commissioner Districts 1 and 3.** VoteWA lists both as `Countywide` /
  `County` / `COUNTY COMMISSIONER 1` and `... 3`. Garfield is a non-charter
  county (1,683 registered voters in the August primary, per the East
  Washingtonian). RCW 36.32.040 has commissioners nominated by
  district. RCW 36.32.050(1) has them "elected by the qualified voters of the
  county"; subsection (2), district-only elections, applies only to
  noncharter counties of 400,000 or more (`raw/garfield/rcw-36.32.0{40,50}.html.url`).
  Results agree:
  - The district-only primaries ran in 4 of 11 precincts: District 3
    (Peola, Scoggin, Ward 1, Ward 4) in August 2022; District 1 (Mayview,
    Ping, Tucannon, Ward 3) and District 2 (Pataha, Pleasant, Ward 2) in
    August 2024; Districts 1 and 3 in 4 of 4 units each in August 2026.
  - The general elections ran on all 11 precincts: Commissioner 3 in 2022,
    Commissioners 1 and 2 in 2024, and Commissioners 1 and 2 on all 12
    precincts in 2020.
  - The East Washingtonian's primary report says the same: "Commissioner
    District voting in the primary is limited to voters in the specific
    district. The November general will include all voters in the county."

  The overrides scope both races `COUNTY` and keep the primary's contest
  names, so the slugs match the primary's
  (`garfield-garfield-county-commissioner-district-{1,3}-county-commissioner-{1,3}`)
  and the primary dossiers carried forward. The generic rule would have
  named them `Garfield County` / `County Commissioner 1`. In the archived
  primary these races are `COUNTY_COUNCIL` and unresolvable
  (`garfield/COUNTY_COUNCIL` in `UNRESOLVABLE_SCOPES`); the general does not
  use that layer.
- **District Court Judge.** One county-wide court (the court directory
  lists one judge, in Pomeroy; Cox's 2018 and 2022 races ran on every
  precinct). The override files VoteWA's `DISTRICT COURT JUDGE` as
  `Garfield County District Court` / `District Court Judge`, category
  `Judicial`.
- **Court of Appeals Division III, District 2.** Covers the whole county
  (2022: on all 11 precincts); shipped as a county-scoped information-only
  copy, as Adams, Asotin, Benton, Grant, Walla Walla and Whitman do.
- **Special districts.** No hospital, port, school, fire, EMS, library,
  park or cemetery measure or race is on the general ballot (VoteWA guide).
  For the record, the DOR 2025 layers were probed anyway (below). FIR2025
  (`1`), HSP2025 (`1`) and PRT2025 (`GARFIELD`) each have exactly one
  Garfield polygon (`where COUNTYNAME = 'GARFIELD'`). SCH2025 has two:
  `110` (Pomeroy) and `27J`, a sliver in the southeast corner (extent
  -117.447 to -117.228, 46.294 to 46.471). The SOS 2019 export also shows
  Clarkston School District 250 directors on 3 Garfield precincts. A future
  school measure must therefore be scoped `SCHDST`, not `COUNTY`.

## Layers each scope needs

None beyond Census. Point checks on 2026-10-08 (Census geocoder,
`Public_AR_Current` benchmark, `Current_Current` vintage; WA DOR
`https://webgis.dor.wa.gov/arcgis/rest/services/Programs/WADOR_PropertyTax/MapServer`,
whose `MapServer?f=json` still lists tax year 2025 as the newest group):

| Point | Census | DOR 2025 (`DISTATTRIB`) |
|---|---|---|
| 789 W Main St, Pomeroy (courthouse; geocodes as 789 Main St) | `Pomeroy city`, CD `5`, LD `9` | FIR `1`, HSP `1`, PRT `GARFIELD`, SCH `110`, TCA `0001`; CEM, EMS, LIB, PKR, PUD, WAT none |
| 120 E Main St, Pomeroy | `Pomeroy city`, CD `5`, LD `9` | same as above |
| (-117.5175, 46.4706), Pataha | no place, CD `5`, LD `9` | FIR `1`, HSP `1`, PRT `GARFIELD`, SCH `110`, TCA `0020` |
| (-117.70, 46.62), near the Snake River | no place, CD `5`, LD `9` | same as Pataha |
| (-117.55, 46.22), Blue Mountains | no place, CD `5`, LD `9` | same as Pataha |
| (-117.85, 46.50), west county | (not geocoded) | same as Pataha |

`1012 S 3rd St, Pomeroy` did not geocode. The county's GIS could not be
searched (site blocked), and no county layer is proposed: none is needed.

Suggested live-check addresses (`node pipeline/live_ballot.mjs ...`):

- `789 W Main St, Pomeroy, WA 99347`: CD 5, LD 9, `CITY` Pomeroy; all 13
  contests, no local measure.
- `120 E Main St, Pomeroy, WA 99347`: the same ballot.
- No rural street address was tried beyond the one that failed; an
  interior point such as (-117.5175, 46.4706) at Pataha, run through
  `lookupBallotContext` with the Census coordinates endpoint, should give
  the same ballot with no `CITY`.

## Sources

The VoteWA guide carries statements for the commissioner, sheriff,
treasurer, auditor and Court of Appeals candidates. Its records for
Assessor Bartels, Clerk Gormsen, Prosecutor Newberg and Judge Cox have no
statement text. Local news is the East Washingtonian (Pomeroy weekly), found
through `sitemap_stories1.xml`. Most of its 2026 stories, including the
July 16 candidate profiles and the hiring-freeze stories, are paywalled:
non-subscribers get the opening paragraph only, and only that was read and
cited. The appointment, resignation, filing, forum, primary-results and
flood-emergency stories were served in full. Pointers are under
`raw/garfield/news/`. The site rate-limits scripted reads (Cloudflare error
1015), so fetches were spaced out. The Lewiston Tribune was not tried after
Asotin's agent found it blocked. Campaign finance is the PDC summary
dataset (data.wa.gov `3h9x-7bvm`): every candidate chose mini reporting
except Dixon (full reporting, $0).

## Research

- **Commissioner District 1** (contested; two-year unexpired term). The
  appointed incumbent Vonda (Vonni) Mulrony (`moderate`) faces Beau Blachly
  (`pamphlet-only`). Commissioner Jim Nelson resigned in December 2025 and
  the board appointed Mulrony on 2026-02-23. Scores: Mulrony `experience` -1
  medium, `spending` -1 medium; Blachly `experience` +1 medium, `spending` 0
  medium. The primary dossier's claims from the county's appointment record
  (`garfieldcountywa.gov/media/11806`: landowner rights in alternative
  energy, FEMA skepticism) are carried and labelled not re-read; no score
  uses them.
- **Commissioner District 3** (contested). Incumbent and 2026 chair Justin
  E. Dixon (`rich`) faces Fire District 1 commissioner Gary W. Bowles
  (`pamphlet-only`). Bowles led the district-only primary 171 to 165.
  Scores: Dixon `experience` -2 high, `spending` -1 medium; Bowles
  `experience` +1 medium.
- **Sheriff** (contested, open seat; Sheriff Drew Hyer is not running).
  Deputy and union president Kristopher Lee Taylor and Undersheriff Calvin
  Dansereau, both `pamphlet-only`. Scores: Taylor `experience` +1 medium;
  Dansereau `experience` -1 high. Neither states an enforcement or
  prevention agenda, so `safety` is not scored.
- **Treasurer** (contested). Incumbent Tereasa Summers (`moderate`) faces
  former chief deputy Katie Nagle (`pamphlet-only`, write-in in the
  primary). Scores: Summers `experience` -2 high; Nagle `experience` +1
  medium.
- **Six uncontested contests ship information-only** (scoring files with
  empty scores; LD 9 Pos. 1 ships from Spokane): Assessor Bartels
  (`pamphlet-only`), Auditor Lueck (`pamphlet-only`), Clerk Gormsen
  (`moderate`), Prosecutor Newberg (`moderate`), District Court Judge Cox
  (`moderate`), Court of Appeals III-2 Pos. 1 Tyson R. Hill (`moderate`).
- Refutations for the four contested races are in `scoring/refutations/`.

## Known gaps

- **County site blocked.** No sample ballot, local pamphlet or county
  elections page was read; the absence of local measures rests on the
  VoteWA guide and local press. The ship pass needs an elections office URL
  for `COUNTY_ELECTIONS_URLS`; `garfieldcountywa.gov` answers 403 to
  scripts, so it must be checked another way or taken from an official
  printed source (as `election.py` allows).
- **Thin candidate evidence.** Six of the eight contested-race candidates
  are `pamphlet-only`. The East Washingtonian's candidate profiles and its
  forum coverage are paywalled, and the forum story did not report the
  answers.
- **Statement discrepancy.** Summers's statement says "elected 2019"; the SOS
  export shows her winning the November 2018 general (she would have taken
  office in January 2019). Dixon's "2015 to Current" has no 2015 or 2016
  general contest for the seat in the SOS exports. He was presumably
  appointed in 2015, but that is not documented here.
