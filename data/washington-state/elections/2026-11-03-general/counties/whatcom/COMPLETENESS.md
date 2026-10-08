# Whatcom County Completeness Note

Election: 2026 Washington general election, November 3, 2026 (VoteWA
election 899, county code 37).

As of 2026-10-08 (#28) this package is researched, scored and refuted but
not declared: it does not ship until the director adds it to
`APP_PACKAGES["2026-11-03-general"]["counties"]`. `interim/app-contests.json`
and `interim/app-measures.json` are built by
`pipeline/build_votewa_lite_data.py --county whatcom` from the VoteWA
candidate list (`raw/votewa/candidate-list.csv.url`) and the measures and
overrides in that script's `ELECTION_MEASURES["2026-11-03-general"]["whatcom"]`.
The builder reports `full_county`: every contest and measure scope is one the
Whatcom District Adapter (Census `CONGDST`/`LEGDST`/`CITY` plus
`app/src/lib/geo.js` `COUNTY_LAYERS.whatcom`: `PORTDST`, `FIRDST`,
`HOSPDST`) resolves.

## What is on the ballot

12 contests (the five Supreme Court contests are dropped by the builder and
ship from the statewide package) and 5 local measures.

| Kind | Contests | Contested | Uncontested (info-only) | Scope | Research |
|---|---|---|---|---|---|
| U.S. Representative (CD 2) | 1 | 1 | 0 | `CONGDST` | Snohomish package (shared race, not researched here) |
| State Representative (LD 40 Pos. 1 and 2) | 2 | 2 | 0 | `LEGDST` | here (LD 40 also crosses Skagit and San Juan) |
| State Senator, State Representative (LD 42) | 3 | 3 | 0 | `LEGDST` | here (LD 42 is Whatcom-only) |
| Prosecuting Attorney | 1 | 1 | 0 | `COUNTY` | here |
| District Court Judge Positions 1 and 2 | 2 | 0 | 2 | `COUNTY` | here (info-only) |
| Port of Bellingham Commissioner Districts 4 and 5 | 2 | 2 | 0 | `COUNTY` | here |
| PUD No. 1 of Whatcom County Commissioner District 1 | 1 | 1 | 0 | `COUNTY` | here |

No county council, executive or other charter office is on the 2026 general
ballot: the VoteWA list for Whatcom has no Council or Countywide row besides
the Prosecuting Attorney and the two District Court seats.

Measures (all from VoteWA's online voters' guide for Whatcom, records 7295,
7297, 7298, 7299, 7300): City of Bellingham Propositions 2026-06 and 2026-07
(charter amendments) and Initiative 26-01 (`CITY` `Bellingham`); City of
Lynden Proposition 2026-05 (`CITY` `Lynden`); Whatcom County Fire Protection
District No. 1 Proposition 2026-08 (`FIRDST` `1`, DOR FIR2025).

## Scoping decisions

- Port of Bellingham D4 and D5 and PUD No. 1 D1 are scoped `COUNTY`, not to
  their commissioner districts. Both districts are county-wide: the WA DOR
  PRT2025 and PUD2025 layers each hold one Whatcom polygon (identical
  geometry) and point queries at Point Roberts, Glacier, Newhalem,
  Bellingham, Sumas and Acme all fall inside it (`raw/scope/dor-*.url`).
  Only district voters nominate in the primary; voters of the entire port
  or PUD elect in the general (RCW 53.12.010(1), RCW 54.12.010(3);
  `raw/scope/rcw-*.url`). The PUD's own page says its commissioners are
  "elected ... by Whatcom County residents" (`raw/scope/pudwhatcom-the-commission.url`).
  The primary scoped the port seats to `PORTDST` (district-only primary);
  that layer stays in `COUNTY_LAYERS.whatcom` but no general record uses it.
- The port seats keep the primary's contest names (`Port of Bellingham
  Commissioner District 4` / `Commissioner District 4`), so their slugs
  match the primary and its dossiers carried forward.
- VoteWA files the two District Court seats as District Type `Countywide`;
  the override names them `Whatcom County District Court`, `Judge Position
  No. N`, category `Judicial`, as the other county builders do.
- The override mechanism (`overrides` in a county's `ELECTION_MEASURES`
  entry, keyed by upper-cased District and Race) needed two lines of
  wiring in `config_for` and `county_docs`; the primary path does not read
  it (the primary build is byte-identical).

## Official sources

The Whatcom County Auditor's site (whatcomcounty.us) answered HTTP 403
(Cloudflare challenge) to scripted requests on 2026-10-08, so no printed
local pamphlet or Auditor measures list was fetched. Candidate statements and
measure texts come from VoteWA's online voters' guide
(`https://voter.votewa.gov/genericvoterguide.aspx?e=899&c=37`), pointers
under `raw/votewa/voter-guide/`, text in `interim/voter-guide-text/`. Those
citations carry no page numbers, so `pamphlet_refs.py` gives no
`pamphlet_pages`; at ship time the app should link the county's VoteWA guide
(`officialLinks.js` `countyGuides.whatcom`), as for Spokane. The measures
list could not be cross-checked against the Auditor's own list.

## Live checks (2026-10-08)

`pipeline/live_ballot.mjs` against a scratch copy of the shipped app data
with this package's interim files appended (Whatcom declared `full_county`;
nothing in the repo was assembled):

- 1101 Harris Ave, Bellingham (Fairhaven): `CONGDST` 2, `LEGDST` 40, `CITY`
  Bellingham, `PORTDST` 1, `missing=[]`. Ballot: CD 2, LD 40 Pos. 1 and 2,
  Prosecuting Attorney, District Court 1 and 2, Port D4 and D5, PUD D1, and
  the three Bellingham measures.
- 111 W Main St, Everson: `CONGDST` 2, `LEGDST` 42, `CITY` Everson,
  `PORTDST` 4, `FIRDST` 1, `missing=[]`. Ballot: CD 2, LD 42 Senator and
  Pos. 1 and 2, the county-wide races, and Fire District 1 Prop 2026-08.

## Known gaps

- The Auditor's measures list and printed pamphlet could not be fetched
  (403); the measures are VoteWA's guide records.
