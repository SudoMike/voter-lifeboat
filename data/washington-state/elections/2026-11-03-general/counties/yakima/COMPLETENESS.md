# Yakima County Completeness Note

Election: 2026 Washington general election, November 3, 2026 (VoteWA
election 899, county code 39).

Shipped (#28): the package is declared in
`APP_PACKAGES["2026-11-03-general"]["counties"]` and ships at Full County
Coverage, with the elections office link
`https://www.yakimacounty.us/170/Elections` and the county's VoteWA guide
(`officialLinks.js` `countyGuides.yakima`) for its unpaged citations. Its
contests come from `pipeline/build_votewa_lite_data.py --county yakima`
(VoteWA candidate list, pointer `raw/votewa/candidate-list.csv.url`, pinned
by `sha256` and `sha256_case_normalized`), and the builder reports
`full_county`: every scope is Census `CONGDST`/`LEGDST` or the county
commissioner layer already in `app/src/lib/geo.js` `COUNTY_LAYERS.yakima`.

## What is on the ballot

19 contests (11 contested, 8 uncontested) and no local measures. The
Supreme Court contests are dropped by the builder and ship from the
statewide package.

| Kind | Contests | Contested | Uncontested (info-only) | Scope | Research |
|---|---|---|---|---|---|
| U.S. Representative (CD 4) | 1 | 1 | 0 | `CONGDST` 4 | Benton package; ships with Benton's scoring and dossiers |
| State Representative (LD 14 Pos. 1, 2; LD 15 Pos. 1, 2) | 4 | 4 | 0 | `LEGDST` | this package |
| State Senator (LD 15) | 1 | 0 | 1 | `LEGDST` 15 | this package |
| Assessor, Auditor, Prosecuting Attorney, Sheriff, Treasurer | 5 | 5 | 0 | countywide | this package |
| Clerk, Coroner | 2 | 0 | 2 | countywide | this package |
| County Commissioner District 1 | 1 | 1 | 0 | `COUNTY_COUNCIL` 1 | this package |
| District Court Judge, Positions 1-4 | 4 | 0 | 4 | countywide | this package |
| Court of Appeals, Division III, District 3, Position 1 | 1 | 0 | 1 | countywide | this package |

LD 13 is not on any Yakima ballot: the VoteWA export, the VoteWA online
guide and the Auditor's "Election at a glance" list only LD 14 and 15.

Contested races carry dossiers, scores and a refutation pass; uncontested
races carry dossiers and empty-score scoring files (`office_does`,
`race_blurb`, summary, highlights).

## Measures

None. The Auditor's "Election at a glance"
(`raw/yakima/election-at-a-glance-2026-general.pdf.url`), the sample ballot
(`raw/yakima/sample-ballot-2026-general.pdf.url`) and VoteWA's online guide
for county 39 (`raw/votewa/voter-guide/guide.json.url`) list only the
statewide measures IP26-645, IL26-001 and IL26-638. The builder's
`ELECTION_MEASURES["2026-11-03-general"]["yakima"]` is an explicit empty
list with a note naming those sources.

## District scoping

- `COUNTY_COUNCIL`: Commissioner District 1 is elected by district in the
  general as well as the primary. The Auditor's 2026 Candidate & Election
  Guidebook (`raw/yakima/candidate-election-guidebook-2026.pdf.url`, p. 19):
  "The names of candidates for County Commissioner appear only on the
  ballots within their commissioner district. Aguilar et al. v Yakima County
  et al. Final Order October 2021 RCW 36.32.040(3)". The race is scoped
  `COUNTY_COUNCIL` `1`, resolved by the county layer
  `Commissioner_District_Election_2022/FeatureServer/0`, attribute `ID`.
  Live point queries on 2026-10-09 (Census-geocoded):
  - 115 W Naches Ave, Selah: `ID` 1 (LD 15, CD 4)
  - 128 N 2nd St, Yakima: `ID` 2 (LD 14, CD 4)
  - 818 E Edison Ave, Sunnyside: `ID` 3 (LD 14, CD 4)
- District Court and Court of Appeals seats are whole-county electorates
  (`COUNTY`).
- No PUD, port, fire or school scope is on this ballot, so no DOR layer is
  used. (`COUNTY_LAYERS.yakima` also carries DOR FIR2025 for the primary's
  Fire District 6 measure.)

## Sources

Dossiers cite VoteWA's online voters' guide (`candidate.ashx` race records,
pointers under `raw/votewa/voter-guide/`, text in
`interim/voter-guide-text/`); those citations carry no page numbers, so the
app should link the county's guide
(`https://voter.votewa.gov/genericvoterguide.aspx?e=899&c=39`) as it does
for Spokane. Other web sources have pointers under `raw/candidates/<contest>/`.

## Known gaps

- The generic VoteWA rules map the District Court rows (District Type
  `Countywide`, Race `Yakima County District Court Judge, Position N`) to
  category `County` with the office text repeated in the slug
  (`yakima-yakima-county-yakima-county-district-court-judge-position-1`).
  A county override would make them `Judicial` / `Yakima County District
  Court` / `Judge Position N`, but `build_votewa_lite_data.py` does not pass
  an override to `votewa.parse_contests`, and adding that plumbing was
  outside this package's write fence. All four seats are uncontested and
  carry no scores, so the effect is the display category only.
- CD 4 is researched by the Benton package; the rebuilt plan names it
  `researched_in` benton with no `candidates_missing`. Benton's LD 14 and LD
  15 House seats ship with this package's scoring.
- District Court categories: the seats keep the bulk builder's category
  `County` (display only). Whatcom's merge added an `overrides` hook to
  `ELECTION_MEASURES`, which could rename them `Judicial` / `Yakima County
  District Court` in a later change; the slugs would change with it.
- The Court of Appeals Division III District 3 seat also appears on other
  counties' ballots (Chelan, Douglas, Kittitas, Klickitat); this package
  wrote its info-only entry because it is uncontested and not in the plan.
