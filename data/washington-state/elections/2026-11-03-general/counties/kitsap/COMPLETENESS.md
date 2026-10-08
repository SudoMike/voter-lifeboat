# Kitsap County Completeness Note

Election: 2026 Washington general election, November 3, 2026 (VoteWA
election 899, county code 18).

Shipped 2026-10-08 (#22) at **Full County Coverage** (`full_county`):
`pipeline/election.py` declares it in
`APP_PACKAGES["2026-11-03-general"]["counties"]` with its elections office
(`https://www.kitsap.gov/auditor/Pages/Elections.aspx`, 200 on 2026-10-08).
Assembly reads `interim/app-contests.json` and `interim/app-measures.json`,
built by `pipeline/build_kitsap_lite_data.py` from the VoteWA candidate
list and Kitsap County's online voters' guide on VoteWA. Every scope
resolves, including `SCHDST` (below). Records carry no pamphlet pages; the
app links Kitsap's VoteWA guide (`officialLinks.js` `countyGuides.kitsap`).
CD 6 and LD 26 (Senator, Pos. 1, Pos. 2) ship with Pierce's scoring and
dossiers.

## What the ballot holds

22 contests (14 contested, 8 uncontested) and 2 measures. The Supreme Court
contests are dropped by the builder and ship once, from the statewide
package.

| Kind | Contests | Contested | Uncontested (info-only) | Scope |
|---|---|---|---|---|
| U.S. Representative (CD 6) | 1 | 1 (researched in Pierce) | 0 | `CONGDST` |
| State Senator / Representative (LD 23, 26, 35) | 8 | 8 (LD 26 Senate, Pos. 1, Pos. 2 researched in Pierce) | 0 | `LEGDST` |
| County Commissioner District 3 | 1 | 1 | 0 | countywide (nominated by district, elected county-wide; VoteWA lists it as Countywide) |
| Assessor, Auditor, Clerk, Prosecuting Attorney, Sheriff, Treasurer | 6 | 4 | 2 (Auditor, Treasurer) | countywide |
| District Court, Departments 1 to 4 | 4 | 0 | 4 | countywide |
| Court of Appeals, Division 2, District 2, Position 1 | 1 | 0 | 1 | countywide |
| Kitsap PUD No. 1 Commissioner District 2 | 1 | 0 | 1 | countywide (whole PUD votes in the general, RCW 54.12.010(3); KPUD is countywide) |

Researched elsewhere (`build_research_plan.py` `researched_in`): CD 6 and
LD 26 Senator, Rep. Pos. 1 and Pos. 2 ship with Pierce's scoring and
dossiers (`counties/pierce/`). No Kitsap copy exists.

Researched here: LD 23 Rep. Pos. 1 and 2; LD 35 Senator, Rep. Pos. 1 and
2 (LD 35 is also listed by Thurston; Kitsap researched it for both);
Commissioner District 3; Assessor; Clerk; Prosecuting Attorney; Sheriff.
Every contested candidate is scored and every contest has a refutation
file. The eight uncontested seats have info-only scoring files (empty
`scores`).

Measures (both researched, refuted):

- South Kitsap School District No. 402 Proposition No. 1, capital levy
  (`SCHDST` `402`): maps to `taxes` +2.
- Kitsap County Public Utility District No. 1 Proposition No. 1, authority
  to construct or acquire electric facilities (countywide): no lean
  mapping (no tax, no spending authorized; public-vs-private ownership
  does not fit the `local-control` poles). The refutation adjusts its
  display text (`_display`).

## Sources and pamphlet links

kitsap.gov serves its HTML pages to scripts but answered HTTP 403 (Azure
WAF) to every PDF on 2026-10-08: the local voters' pamphlet
(`auditor/Documents/LVP.pdf`), the sample ballot (`auditor/Documents/Sample.pdf`)
and the ballot-measure resolutions. The dossiers therefore cite Kitsap
County's VoteWA online voters' guide (`raw/votewa/voter-guide/`, text in
`interim/voter-guide-text/`), as Spokane's do. Those citations carry no page
numbers, so Kitsap records would ship no `pamphlet_pages`; the app should
link the county's VoteWA guide
(`https://voter.votewa.gov/genericvoterguide.aspx?e=899&c=18`) in
`officialLinks.js` `countyGuides`. `officialLinks.js` `pamphletPdfs` still
has `'kitsap/local-voters-pamphlet'` pointing at `LVP.pdf` (the primary's
edition id; the county's elections page now links the same URL for the
general, but its content could not be checked) and no general dossier cites
it.

The measures list was checked against the Auditor's "November 3, 2026
General Election Ballot Resolutions" page (`raw/kitsap/resolutions.html.url`),
which lists exactly the two measures above, and the VoteWA guide index
(`raw/votewa/voter-guide/voterguide.json.url`). The sample ballot could not
be fetched, so the commissioner and PUD electorates were confirmed from
VoteWA (the commissioner race is `Countywide` in the candidate list and
`County` in the guide), RCW 54.12.010(3) and KPUD's own pages, not from the
sample ballot.

## District scoping

- `SCHDST` (South Kitsap SD Prop 1): in `geo.js` `COUNTY_LAYERS.kitsap`
  since #22. Layer: Kitsap County GIS
  `https://services6.arcgis.com/qt3UCV9x5kB4CwRA/arcgis/rest/services/School_District_Outlines/FeatureServer/0`,
  attribute `DISTRICT` (values `100-C`, `303`, `400`, `401`, `402`, `403`;
  `raw/kitsap/school-district-outlines.json.url`). Live 2026-10-08:
  2689 Hoover Ave SE and 1700 SE Mile Hill Dr, Port Orchard `402`;
  345 6th St, Bremerton `100-C`; 19050 Jensen Way NE, Poulsbo `400`;
  280 Madison Ave N, Bainbridge Island `303`; 15376 Seabeck Hwy NW,
  Seabeck `401`. DOR SCH2025 (layer 20) `DISTATTRIB` agreed at each point
  except Bremerton (`100` vs the county's `100-C`). The director re-verified
  Port Orchard, Bremerton and Seabeck on 2026-10-08; the builder's
  `unresolvable_layers` is empty and the package is `full_county`.
- `COUNTY_COUNCIL` and `FIRDST`, also in `COUNTY_LAYERS.kitsap`, are not
  used by any general contest or measure.
- The PUD seat, which #20 left as `PUDDST` (unresolvable), is now scoped
  `COUNTY` (the whole PUD votes in the general and KPUD is countywide), so
  `PUDDST` is no longer needed.

## Known gaps

- Kitsap Sun stories are paywalled (HTTP 402) and were not used. The SOS
  results pages for the August primary returned 404, so some primary
  percentages are missing from dossiers.
- The sample ballot and printed pamphlet could not be fetched (above).
