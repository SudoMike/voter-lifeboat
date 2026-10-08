# Clark County Completeness Note

Election: 2026 Washington general election, November 3, 2026 (VoteWA
election 899, county code 06).

As of 2026-10-08 (#22) this package is researched but **not declared**:
`pipeline/election.py` does not list it in `APP_PACKAGES["2026-11-03-general"]["counties"]`,
so Clark addresses still get the Statewide-Only Guide until the director
ships it. Assembly would read `interim/app-contests.json` and
`interim/app-measures.json`, built by `pipeline/build_clark_lite_data.py`
from the VoteWA candidate list, Clark's sample ballot and local voters'
pamphlet, and Clark's VoteWA online voters' guide. The package is
`partial_county` for one layer, `SCHDST` (below).

## What ships

25 contests (16 contested, 9 uncontested) and 12 measures. The Supreme
Court contests are dropped by the builder and ship once, from the statewide
package.

| Kind | Contests | Contested | Uncontested (info-only) | Scope |
|---|---|---|---|---|
| U.S. Representative (CD 3) | 1 | 1 | 0 | `CONGDST` |
| State Representative (LD 17, 18, 20, 49; Pos. 1 and 2) | 8 | 8 | 0 | `LEGDST` |
| County Council (Districts 1, 2, 5) | 3 | 3 | 0 | `COUNTY_COUNCIL` |
| Assessor, Auditor, Clerk | 3 | 3 | 0 | countywide |
| Prosecuting Attorney, Sheriff, Treasurer | 3 | 0 | 3 | countywide |
| District Court, Departments 1 to 6 | 6 | 0 | 6 | countywide |
| Clark Public Utilities Commissioner District 3 | 1 | 1 | 0 | countywide (see below) |

No State Senate seat in Clark's districts is on this ballot. No race is
researched in another package; CD 3 and LD 20 (Pos. 1 and 2) are also
listed by Thurston's package and were researched here, once, for the whole
district (Clark sorts first among the unresearched listers).

The PUD race is category `Local`, to which no rubric axis applies, so its
two candidates ship summaries without scores.

Measures (12): Proposed Charter Amendments No. 19 to 27 and County
Propositions No. 12 (jail/courts/Sheriff headquarters bonds) and No. 13
(public safety levy lid lift), all countywide; Battle Ground School
District No. 119 Proposition No. 11 (EP&O levy), `SCHDST` `119`.

## Sources

- VoteWA candidate list: `raw/votewa/candidate-list.csv.{url,meta.json}`
  (re-pinned 2026-10-08 with `sha256_case_normalized`; the re-fetch differed
  from the first pin only in the case of District Type/District values, and
  the builder output was unchanged).
- Sample ballot and local voters' pamphlet: `raw/clark/sample-ballot.pdf.url`,
  `raw/clark/local-voters-pamphlet.pdf.url` (edition id
  `local-voters-pamphlet`; the SOS state section and Clark's local section in
  one 112-page PDF). Text in `interim/pdf-text/`.
- The pamphlet's **local section (PDF pages 41-99) has no extractable
  text**: its fonts carry no Unicode map, so pdf.js returns glyph ids. The
  same candidate statements and measure statements were read from Clark's
  VoteWA online voters' guide (`raw/votewa/voter-guide/*.json.url`, text in
  `interim/voter-guide-text/`). Dossiers cite the printed pamphlet page
  (`local-voters-pamphlet page N`) with the VoteWA record as the source of
  the wording; pages were located with a rough glyph decoder and should be
  spot-checked against the PDF. State-section pages (23-34) extract cleanly.

## District scoping

- `COUNTY_COUNCIL`: `ClarkView_Public/BoardofCountyCouncilorsDistrict/MapServer/0`,
  `BOCCDistrict` (already in `geo.js` `COUNTY_LAYERS.clark`). Council members
  are elected by district in the general (2022 District 1 general: 29,167
  votes, results.vote.wa.gov/results/20221108/clark/).
- PUD No. 1 District 3: nominated by district, but RCW 54.12.010(3) has the
  whole PUD elect each district's commissioner in the general, and Clark
  Public Utilities is countywide (its commissioner-district layer has the
  council layer's extent; the 2024 District 1 general drew 222,496 votes).
  The builder therefore scopes the general race `COUNTY`, not `PUDDST`. The
  `PUDDST` layer in `COUNTY_LAYERS.clark` is unused in the general.
- `FIRDST`: in `COUNTY_LAYERS.clark`, unused (East County Fire and Rescue's
  measure was rescinded; no fire measure is on the general ballot).
- `SCHDST` (**not in `COUNTY_LAYERS.clark`**): Battle Ground SD Prop 11 is
  scoped `SCHDST` `119` and listed in the builder's `unresolvable_layers`,
  so the package is `partial_county` and the measure stays hidden until a
  layer is added. Proposed layer:
  `https://gis.clark.wa.gov/arcgisfed/rest/services/ClarkView_Public/SchoolDistrict/MapServer/0/query`,
  attribute `SCHDST` (integer; 37 Vancouver, 93 Mount Pleasant, 98
  Hockinson, 101 La Center, 102 Woodland, 103 Green Mountain, 112 Washougal,
  114 Evergreen, 117 Camas, 119 Battle Ground, 122 Ridgefield). Point query
  2026-10-08 at 109 SW 1st St, Battle Ground (Census -122.53766, 45.78008):
  `SCHDST` 119; DOR SCH2025 (layer 20) gives `DISTATTRIB` '119' at the same
  point. At 1300 Franklin St, Vancouver: `SCHDST` 37. If the director adds
  it, remove `SCHDST` from `unresolvable_layers` and the package is
  `full_county`.

## Research state

All 16 contested contests have dossiers, `_contest.md`, raw pointers for
every web source, a scoring file and (except the unscored PUD race) a
refutation; the 12 measures have dossiers, `scoring/measures.json` and
`scoring/refutations/measures.json`; the 9 uncontested races have light
dossiers and info-only scoring files (empty `scores`). Every candidate
dossier was carried forward from its primary dossier and re-scored on the
general's 15-axis rubric. Refutation verdicts (applied at merge):
adjustments for Gluesenkamp Perez (climate -1, reform +1), McClintock
(spending -2, parental-rights -1, tech low), Letinich (spending +1, safety
low), Ley (reform low), Jones (experience high), Stonier (immigration and
healthcare low), Thompson (taxes low), Van Nortwick (spending low),
Quiring O'Brien (experience -1), McCoy (safety high), Silliman (spending
-1), and Battle Ground Prop 11 (taxes +2); proposed missing scores for
Braun (tech, healthcare, low), Perez (taxes, low) and Abbarno
(immigration -1, medium).

## Known gaps

- The session's web-search budget ran out during research. Sources were
  then reached by direct URL and WebFetch; the uncontested info-only entries
  rely on the pamphlet statement (`pamphlet-only`) and Tyler Thoune
  (Assessor) is `pamphlet-only`.
- The Columbian is paywalled past the first paragraphs; dossiers cite only
  what the cached openings show. A few of Andy Zahn's campaign pages (LD 20)
  answer 429 to scripts and were read via WebFetch only (no cached copy or
  sha256 in their metas).
- The county's measure resolutions (`clark.wa.gov/media/document/...`) are
  scanned PDFs with no text; they are cited only as listed on the county's
  election page, not for their content.
- Battle Ground SD Prop 11: the opposing statement says the levy failed
  three times in two years; this research confirmed two 2025 failures
  (February Prop 8, April Prop 9) and not the third.
