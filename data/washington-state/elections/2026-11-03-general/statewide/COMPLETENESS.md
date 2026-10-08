# Statewide Completeness Note

Election: 2026 Washington general election, November 3, 2026.

The statewide package is complete for the general election when it holds every
contest and measure whose electorate is all Washington voters (ADR-0003). As of
2026-10-08 that is five Supreme Court contests and three statewide measures:

| Contest | Candidates (ballot order) | Pamphlet (Edition 06) |
|---|---|---|
| Justice Position No. 1, Supreme Court (2-year unexpired term) | Colleen Melody; Scott Edwards | p. 53 |
| Justice Position No. 3, Supreme Court (6-year term) | David Stevens; Jaime Michelle Hawk | p. 54 |
| Justice Position No. 4, Supreme Court (6-year term) | Ian Birk; Sean O'Donnell | p. 55 |
| Justice Position No. 5, Supreme Court (2-year unexpired term) | Theo Angelis; Dave Larson | p. 56 |
| Justice Position No. 7, Supreme Court (6-year term) | Debra L. Stephens; Todd A. Bloom | p. 57 |

| Measure | Type | Pamphlet (Edition 06) |
|---|---|---|
| Initiative Measure No. IP26-645 (state and local taxes) | Initiative to the People | pp. 9-14; complete text pp. 64-65 |
| Initiative Measure No. IL26-001 (parental rights in public school) | Initiative to the Legislature | pp. 15-19; complete text pp. 65-68 |
| Initiative Measure No. IL26-638 (participation in K-12 athletics) | Initiative to the Legislature | pp. 20-22; complete text pp. 68-70 |

Position No. 4 is new for the general. It was not in the August primary package
because VoteWA listed it as `Advanced to General`, not `In Primary`.

The pamphlet's table of contents lists only these three measures, and the SOS
Proposed Ballot Measure Information page lists the same three initiatives.
There are no advisory votes or legislative referrals this election.

## What this package does not own

The state voters' pamphlet also prints U.S. Representative (p. 23 onward) and
State Legislative (p. 30 onward) contests, and the VoteWA "State" candidate list
includes them, along with Court of Appeals and multi-county Superior Court
races. None of these is a Statewide Contest: each is district-scoped and is
owned by the county packages. A congressional or legislative district that
crosses county lines is still county-owned in this architecture. The August
primary's statewide package held deduplicated congressional and legislative
contests produced by `pipeline/normalize_research_inputs.py`; the general
package does not. Issue #9 recorded this as the ownership rule from the general
onward: `pipeline/election.py` declares `district_contests: "county"` for this
election, and `pipeline/normalize_research_inputs.py` never writes this
package's `interim/` files, so county district contests cannot be merged in.

## Sources

- VoteWA GENERAL 2026 candidate list, county "State" (election 899, county 99):
  `raw/votewa-general-2026-candidate-list.url` (+ `.meta.json` with export steps,
  sha256 and the ballot-order source)
- SOS 2026 General Election Voters' Pamphlet, Edition 06 (King - South and
  Southeast): `raw/sos/voters-pamphlet-edition-06-king-south-southeast.pdf.url`,
  text in `interim/pdf-text/`
- SOS Proposed Ballot Measure Information page and its per-measure PDFs:
  `raw/sos/proposed-ballot-measure-information.html.url`, `raw/sos/measures/`
- SOS 2026 Voters' Pamphlet PDFs page (all editions):
  `raw/sos/2026-voters-pamphlet-pdfs.html.url`, transcribed to
  `interim/pamphlet-editions.json`

Dossiers (`dossiers/`), scoring (`scoring/`) and refutations
(`scoring/refutations/`) exist for all ten justice candidates (#8) and all
three measures (#6, #7). Since #9 this package is the general's whole shipped
ballot: `data/final/2026-11-03-general/app-data.json` has
`coverage.statewide_complete: true` and no supported counties.
