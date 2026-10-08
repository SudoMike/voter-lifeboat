# Cowlitz County Completeness Note

Election: 2026 Washington general election, November 3, 2026 (VoteWA
election 899, county code 08).

Shipped (#28): the package is declared in
`APP_PACKAGES["2026-11-03-general"]["counties"]` and ships at Full County
Coverage, with the elections office link
`https://www.co.cowlitz.wa.us/2357/Elections`, the local pamphlet
(`officialLinks.js` `pamphletPdfs['cowlitz/local-voters-pamphlet']`) and the
county's VoteWA guide (`countyGuides.cowlitz`) for any record without a
page. Its builder output is
`coverage: "full_county"`. Every contest and measure scope is one the
Cowlitz District Adapter resolves: Census `CONGDST`/`LEGDST`/`CITY`, or
`COUNTY`. `interim/app-contests.json` and `interim/app-measures.json` are
built by `pipeline/build_votewa_lite_data.py --county cowlitz` from the VoteWA
candidate list (pointer `raw/votewa/candidate-list.csv.url`) and the
`ELECTION_MEASURES["2026-11-03-general"]["cowlitz"]` block, which holds the
contest overrides and the one local measure.

## What ships

18 contests (4 contested and researched here, 5 contested and researched in
another package, 9 uncontested) and 1 local measure. The builder drops the
five Supreme Court contests, which ship once from the statewide package.

| Kind | Contests | Contested | Uncontested (info-only) | Scope | Research |
|---|---|---|---|---|---|
| U.S. Representative (CD 3) | 1 | 1 | 0 | `CONGDST` | Clark (`clark-congressional-district-3-u-s-representative`) |
| State Representative (LD 19 Pos. 1, 2) | 2 | 2 | 0 | `LEGDST` | Thurston (`thurston-legislative-district-19-state-representative-pos-{1,2}`) |
| State Representative (LD 20 Pos. 1, 2) | 2 | 2 | 0 | `LEGDST` | Clark (`clark-legislative-district-20-state-representative-pos-{1,2}`) |
| County Commissioner District 3 | 1 | 1 | 0 | `COUNTY` | here |
| Clerk | 1 | 1 | 0 | `COUNTY` | here |
| Assessor, Auditor, Coroner, Prosecuting Attorney, Sheriff, Treasurer | 6 | 0 | 6 | `COUNTY` | here (info-only) |
| Superior Court Judge Position 4 (2-year unexpired) | 1 | 1 | 0 | `COUNTY` | here |
| District Court Judge Positions 1, 2, 3 | 3 | 1 (Pos. 3) | 2 | `COUNTY` | here |
| PUD No. 1 Commissioner District 1 | 1 | 0 | 1 | `COUNTY` | here (info-only) |

The research plan found no `candidates_missing` in the five shared races.
No legislative seat touching Cowlitz is left unresearched: LD 19 and LD 20
each have only the two House seats on this ballot, and no Senate seat.

Measure: City of Longview Proposition 1, a levy lid lift for fire and EMS
(`CITY` `Longview`). It maps to `taxes` +2 and `spending` +1, and both are
upheld in `scoring/refutations/measures.json`. The general sample ballot and
local pamphlet list no other local measure, and VoteWA's online guide for
county 08 agrees (`raw/votewa/voter-guide/guide.json.url`).

## Overrides and scoping (verified)

The overrides are in the `cowlitz` block of `ELECTION_MEASURES` in
`build_votewa_lite_data.py`:

- **Commissioner District 3** keeps the primary's contest name
  (`cowlitz-cowlitz-county-commissioner-district-3-commissioner-district-3`)
  so the primary dossiers carry forward. It is scoped `COUNTY`. VoteWA's
  general export lists it as District Type `Countywide`. Under RCW 36.32.040
  commissioners are nominated by district and elected county-wide. SOS
  certified results confirm county-wide voting: in the 2024 general,
  Commissioner District 2 drew 56,821 votes of 59,822 ballots
  (`raw/sos/results-20241105-cowlitz.html.url`), and in 2022 District 3 drew
  43,964 of 45,267 (`raw/sos/results-20221108-cowlitz.html.url`).
- **District Court Positions 1 to 3** are renamed from VoteWA's bare
  `District Court` to `Cowlitz County District Court` / `Judge Position No. N`,
  as the pamphlet and other counties name them. Each is scoped `COUNTY`
  because there is a single county-wide district; in 2022 each position drew
  about 30,400 votes.
- **PUD No. 1 Commissioner District 1** is scoped `COUNTY` instead of the
  generic unresolvable `PUDDST`. RCW 54.12.010(3) has the whole PUD elect
  each commissioner in the general. The PUD covers the whole county:
  WA DOR `PUD2025` (layer 17) has a single Cowlitz polygon (`DISTATTRIB`
  `1`, about 1,136 sq mi, which matches the county). Point queries
  returned `COWLITZ`/`1` at Longview, Kelso, Castle Rock and Woodland, and
  the 2022 `PUBLIC UTILITY DISTRICT ALL` District 3 race drew 30,453 votes
  county-wide.
- The override wiring (`cfg["overrides"]` in `config_for`, the `override`
  lambda in `county_docs`) is identical to Whatcom's #28 branch, because it
  was not on main when this work started.

Point checks on 2026-10-09 used the Census geocoder (Current) and the
county's `Political_Administrative_Districts/MapServer/1` layer. 1525
Broadway, Longview gave CD 3, LD 19, place `Longview`, commissioner
district 2. 230 Cowlitz Way, Kelso gave LD 19, `Kelso`, district 1. 141 Front
Ave SW, Castle Rock gave LD 19, district 3. 200 E Scott Ave, Woodland gave
LD 20, `Woodland`, district 1. `pipeline/live_ballot.mjs` was run on a
scratch copy of the general app data with this package appended (not
written to the repo). Longview and Kelso each got `full_county`,
`missing=[]` and 21 contests; Longview got Prop 1 and Kelso did not.
Woodland got LD 20 and no Prop 1. Re-run against the shipped data on
2026-10-08 (#28): Longview and Woodland both `full_county`, `missing=[]`,
21 contests; LD 19 ships with Thurston's scoring, CD 3 and LD 20 with
Clark's.

`COUNTY_LAYERS.cowlitz` in `app/src/lib/geo.js` lists only `COUNTY_COUNCIL`.
No Cowlitz scope uses it in the general, and no new layer is needed.

## Pamphlet links

The dossiers cite the county's printed pamphlet by page
(`raw/cowlitz/local-voters-pamphlet.pdf.url`, edition id
`local-voters-pamphlet`; the combined SOS and local edition, 72 PDF pages).
Superior Court is on p. 37; the county offices are on pp. 45-52; District
Court on pp. 53-55; PUD on p. 56; Longview Prop 1 on pp. 57-58.
`officialLinks.js` `pamphletPdfs['cowlitz/local-voters-pamphlet']` links
https://www.co.cowlitz.wa.us/DocumentCenter/View/39451/G126-Combined-Voters-Pamplet_SOS
(checked 2026-10-08: 200 application/pdf, 72 pages, sha256 as in the
pointer's meta). Longview Prop 1 ships `pamphlet_pages` 57-58, set by
`pages=` in the builder block.
The county elections page https://www.co.cowlitz.wa.us/2357/Elections
answered HTTP 200 to scripted requests on 2026-10-09.

## Evidence and known gaps

- The Daily News (tdn.com) is paywalled, and only its open lead paragraphs
  were used. Local news comes mainly from KLOG.
- Clerk candidates Staci Myklebust and Ashley White are `pamphlet-only`:
  neither has a campaign site, and no independent coverage of either
  platform was found.
- The 2026 judicial evaluation poll used for the Superior and District
  Court races was published on Judge Karmy's campaign site. The PDF does not
  name the polling organization, and every dossier says so. Four-number rows
  (one blank column) were not quoted except where unambiguous.
- PDC lists the SAFE Longview committee (treasurer: Mayor Erik Halvorson,
  who voted against placing Prop 1 on the ballot) as supporting Prop 1. The
  dossier reports the record without interpreting it.
- Uncontested candidates are mostly pamphlet-only. The Sheriff (KLOG) and
  PUD (KLOG) entries are `moderate`.
- Refutation adjustments that `merge_scores.py` applies: Chandler
  `experience` +2 to +1; Lervold `safety` -2 to -1. Every other score is
  upheld.
