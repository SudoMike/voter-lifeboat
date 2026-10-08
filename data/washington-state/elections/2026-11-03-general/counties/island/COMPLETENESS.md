# Island County Completeness Note

Election: 2026 Washington general election, November 3, 2026 (VoteWA
election 899, county code 15).

Researched in #29 (county wave 4) and shipped on 2026-10-08 at Full County
Coverage: declared in `APP_PACKAGES["2026-11-03-general"]["counties"]`, with
the Auditor's Elections & Voter Registration page as its elections office
and VoteWA's guide (`countyGuides.island`) for its records' pamphlet links.
`interim/app-contests.json`
and `interim/app-measures.json` are built by
`pipeline/build_votewa_lite_data.py --county island` from the VoteWA
candidate list (`raw/votewa/candidate-list.csv.url`) and the overrides and
measures in that script's `ELECTION_MEASURES["2026-11-03-general"]["island"]`,
checked against the Island County Auditor's general sample ballot
(`raw/island/sample-ballot.pdf.url`, text in `interim/pdf-text/sample-ballot.txt`).

The builder reports `full_county` (it checks contest layers only), and the
assembler agrees: `app/src/lib/geo.js` `COUNTY_LAYERS.island` reads the
three layers below (`PUDDST`, `PORTDST`, `UNINC`) since #29, next to
`COUNTY_COUNCIL` and `LIBDST` left from the primary (no general record uses
either), and `election.DISTRICT_ADAPTER_LAYERS["island"]` matches.

## What is on the ballot

13 contests (10 contested, 3 uncontested) and 3 local measures, matching the
sample ballot. The five Supreme Court contests and the three statewide
initiatives are dropped by the builder and ship from the statewide package.

| Kind | Contests | Contested | Uncontested | Scope | Researched |
|---|---|---|---|---|---|
| U.S. Representative (CD 2) | 1 | 1 | 0 | `CONGDST` | Snohomish package (shared race) |
| LD 10 State Representative Pos. 1 and 2 | 2 | 2 | 0 | `LEGDST` | Snohomish package (shared races) |
| Assessor, Auditor, Clerk (short and full term), Prosecutor, Sheriff | 5 | 5 | 0 | `COUNTY` | here |
| County Commissioner, District 3 | 1 | 1 | 0 | `COUNTY` | here |
| Coroner, Treasurer | 2 | 0 | 2 | `COUNTY` | here (info-only) |
| District Court Judge (short and full term) | 1 | 0 | 1 | `COUNTY` | here (info-only) |
| Snohomish County PUD No. 1 Commissioner District 1 | 1 | 1 | 0 | `PUDDST` `53029` (Camano Island) | Snohomish package (shared race) |

There is no LD 10 Senate race and no LD 39 race on Island's list (VoteWA
export, 33 rows). No port, hospital, fire or city offices are on the 2026
general ballot in Island County.

Measures (VoteWA online guide records 7304, 7305, 7306; sample ballot pages
1-3):

| Measure | Scope | Layer source |
|---|---|---|
| Unincorporated Island County advisory vote on consumer fireworks (Resolution C-62-25) | `UNINC` `ISLAND` | WA DOR TCA2025 (layer 23) |
| City of Langley Proposition No. 1, Governmental Services and Technology Levy | `CITY` `Langley` | Census place |
| Port District of South Whidbey Island Proposition No. 1, levy lid lift | `PORTDST` `S WHIDBEY` | WA DOR PRT2025 (layer 16) |

## Official sources

Island County posts no printed general pamphlet as of 2026-10-09. The
Auditor's Elections page (`https://www.islandcountywa.gov/423/Elections-Voter-Registration`)
links VoteWA's online voters' guide
(`https://voter.votewa.gov/GenericVoterGuide.aspx?e=899&c=15`) as its online
guide. Its race and measure records are pointed to under
`raw/votewa/voter-guide/`, with text in `interim/voter-guide-text/`. Those
citations carry no page numbers, so, as for Spokane, Benton and Whatcom, the
county's records ship no `pamphlet_pages`; at ship time the app should link
the guide through `officialLinks.js` `countyGuides.island`.
The printed August primary pamphlet (`raw/island/primary-local-voters-pamphlet.pdf.url`)
is cited for carried-forward primary statements and for the commissioner
election rule. Every such citation's `ref` names the primary, so
`pamphlet_refs.py` gives it no pages.

## Scoping decisions

- **County Commissioner, District 3: `COUNTY`.** Nominated by District 3
  voters in the primary, elected by all county voters in the general. The
  primary pamphlet says so (PDF page 19: "All voters in the County are able
  to vote in the general election...", RCW 36.32.040, 36.32.050), and VoteWA's
  general export lists the race as `Countywide`.
- **District Court Judge: `COUNTY`, category `Judicial`.** Island County
  District Court is a single county-wide district. The override names it
  `Island County District Court` / `Judge`, as the Whatcom block names its
  seats; VoteWA files it as District Type `Countywide`.
- **Snohomish County PUD No. 1, Commissioner District 1: `PUDDST` `53029`.**
  The PUD serves Snohomish County and Camano Island. Under RCW 54.12.010(3)
  the whole PUD elects the District 1 seat in the general, so on the Island
  side the electorate is Camano Island, not the whole county (Whidbey Island
  is outside the PUD). The override keeps the Snohomish package's contest
  names (`Public Utility District No. 1` / `Commissioner District 1`), so
  `shared_contests` matches it to `snohomish-public-utility-district-no-1-commissioner-district-1`
  and it ships with Snohomish's research. WA DOR PUD2025 (layer 17) has no
  Island polygon. The Auditor's precinct layer does: Camano Island is
  precincts Camano 01-21 (`raw/island/gis-elections-precinct-splits.json.url`).
  Commissioner District 3 includes North Whidbey precincts, so the
  commissioner layer cannot stand in.
- **Fireworks advisory vote: `UNINC` `ISLAND`.** Only unincorporated voters
  vote on it (ballot title; VoteWA jurisdiction `UNINCORPORATED COUNTY`). The
  incorporated areas are WA DOR tax code areas 0100 (Oak Harbor), 0300
  (Coupeville) and 0700 (Langley). They are the only Island TCAs that overlap
  the Census incorporated places beyond edge contact with their surrounding
  unincorporated TCAs (0110, 0160, 0310, 0710). The county's Tax Codes layer
  gives TCA 100 the fire district `City of Oak Harbor`
  (`raw/island/dor-tca2025-island.json.url`, `raw/island/gis-tax-codes.json.url`).
- **Port of South Whidbey levy: `PORTDST` `S WHIDBEY`** from DOR PRT2025
  (`raw/island/dor-prt2025-island.json.url`).
- **Langley levy: `CITY` `Langley`** (Census place `Langley city`).

## Layers in `COUNTY_LAYERS.island`

Proposed by the research and added at ship time (#29) exactly as below.
Each config was point-queried live on 2026-10-09 by the research and again
on 2026-10-08 by the director (Census geocoder, Current vintage), with the
same results:

```js
{ key: 'PUDDST', url: 'https://maps.islandcountywa.gov/arcgis/rest/services/Geocortex/Elections/MapServer/2/query',
  attr: 'County', where: "PrecinctNa LIKE 'Camano%'" },
{ key: 'PORTDST', url: `${DOR_TAX_DISTRICTS}/16/query`, attr: 'DISTATTRIB' },
{ key: 'UNINC', url: `${DOR_TAX_DISTRICTS}/23/query`, attr: 'COUNTYNAME',
  where: "COUNTYNAME = 'ISLAND' AND DISTATTRIB NOT IN ('0100','0300','0700')" },
```

| Address | PUDDST | PORTDST | UNINC | CITY |
|---|---|---|---|---|
| 865 SW Barrington Dr, Oak Harbor | none | none | none (TCA 0100) | Oak Harbor |
| 2795 Heller Rd, Oak Harbor (unincorporated) | none | none | `ISLAND` (TCA 0110) | none |
| 1 7th St NE, Coupeville | none | `COUPE` (no 2026 measure) | none (TCA 0300) | Coupeville |
| 112 2nd St, Langley | none | `S WHIDBEY` | none (TCA 0700) | Langley |
| 5476 Harbor Rd, Freeland | none | `S WHIDBEY` | `ISLAND` (TCA 0760) | none (Freeland CDP) |
| 848 N Sunrise Blvd, Camano Island | `53029` (precinct Camano 01) | none | `ISLAND` (TCA 0590) | none (Camano CDP) |

The `PUDDST` value is the precinct layer's constant `County` attribute
(`53029`). The `where` clause makes it non-null only on Camano precincts; the
layer has no attribute that names the PUD. `UNINC` relies on DOR's 2025 tax
code areas: a city annexation they do not yet carry would show the advisory
vote to a few incorporated voters. `election.DISTRICT_ADAPTER_LAYERS["island"]`
reads `CONGDST`, `LEGDST`, `CITY`, `COUNTY_COUNCIL`, `LIBDST`, `PUDDST`,
`PORTDST`, `UNINC`.

## Live ballots (2026-10-08)

`node pipeline/live_ballot.mjs data/final/2026-11-03-general/app-data.json`,
each `coverage=full_county`, `missing=[]`, 5 Supreme Court contests and the 3
initiatives:

- 865 SW Barrington Dr, Oak Harbor: CD 2, LD 10 (Snohomish's scoring), City
  Oak Harbor, Commissioner District 2; the 9 county contests; no PUD seat, no
  local measure.
- 848 N Sunrise Blvd, Camano Island: `PUDDST` `53029`, `UNINC` `ISLAND`; the
  Snohomish PUD No. 1 District 1 seat and the fireworks advisory vote.
- 112 2nd St, Langley: City Langley, `PORTDST` `S WHIDBEY`; Langley Prop 1 and
  the Port of South Whidbey levy, no advisory vote, no PUD seat.

## Known gaps

- WebSearch was unavailable to the research session (budget exhausted).
  Sources were found by direct fetches: candidate sites, the Whidbey
  News-Times and South Whidbey Record site searches and RSS feeds, PDC open
  data and the VoteWA results API. The Stanwood Camano News search returned
  404 or a captcha, so Camano-side coverage is thin.
- The October candidate forums (Clinton, Stanwood, League of Women Voters)
  had not been covered yet.
- Rick Felici, Sheilah Crider and Barbara Fuller have no campaign websites.
  retainrick.com belongs to a different candidate.
- Langley Resolution 877 (ecode360 returned 403) and the signed Port
  Resolution 2026-06 were not retrieved. Three committees named in the voters'
  guide have no PDC registration.
- The shared-race key `("NAMED", "public utility district 1", "commissioner
  district 1")` is generic: any other county that lists a bare "Public
  Utility District No. 1 / Commissioner District 1" would also match
  Snohomish's research.
