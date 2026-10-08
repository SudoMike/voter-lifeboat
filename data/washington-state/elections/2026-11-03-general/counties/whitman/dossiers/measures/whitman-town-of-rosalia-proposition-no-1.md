---
slug: whitman-town-of-rosalia-proposition-no-1
jurisdiction: Town of Rosalia
title: "Street Levy"
researched_at: 2026-10-08
evidence_level: moderate
derived_from:
  - data/washington-state/elections/2026-11-03-general/counties/whitman/interim/voter-guide-text/measure-7404.txt
  - data/washington-state/elections/2026-11-03-general/counties/whitman/interim/pdf-text/local-voters-pamphlet.txt
  - data/washington-state/elections/2026-11-03-general/counties/whitman/interim/app-measures.json
  - data/washington-state/elections/2026-11-03-general/counties/whitman/raw/whitman/sos-results-20241105-whitman-precincts.csv.url
  - data/washington-state/elections/2026-11-03-general/counties/whitman/raw/measures/whitman-town-of-rosalia-proposition-no-1/
sources:
  - id: S1
    tier: 1
    type: pamphlet
    ref: VoteWA voters' guide, Whitman County, GENERAL 2026, measure 7404 (ballot title and explanatory statement; no statements for or against, no volunteers came forward)
    url: https://voter.votewa.gov/elections/measure.ashx?m=7404&e=899&la=en&c=38
    pointer: counties/whitman/raw/votewa/voter-guide/measure-7404.json.url
    accessed: 2026-10-08
  - id: S2
    tier: 1
    type: pamphlet
    ref: local-voters-pamphlet page 23
    url: https://www.whitmancounty.gov/DocumentCenter/View/12618
    pointer: counties/whitman/raw/whitman/local-voters-pamphlet.pdf.url
    accessed: 2026-10-08
  - id: S3
    tier: 1
    type: results
    outlet: "WA Secretary of State election results, Whitman County precinct export, November 5, 2024 general"
    url: https://results.vote.wa.gov/results/20241105/export/20241105_whitmanprecincts.csv
    pointer: counties/whitman/raw/whitman/sos-results-20241105-whitman-precincts.csv.url
    accessed: 2026-10-08
  - id: S4
    tier: 2
    type: news
    outlet: "Moscow-Pullman Daily News, \"Numerous Whitman County levies to appear on general election ballot\" (Emily Pearce, 2024-10-18)"
    url: https://www.dnews.com/stories/numerous-whitman-county-levies-to-appear-on-general-election-ballotpage_465
    pointer: counties/whitman/raw/measures/whitman-town-of-rosalia-proposition-no-1/dnews-2024-10-18-numerous-levies.html.url
    accessed: 2026-10-08
  - id: S5
    tier: 1
    type: results
    outlet: "Washington Secretary of State election results, Whitman County precinct export, November 7, 2023 general"
    url: https://results.vote.wa.gov/results/20231107/export/20231107_whitmanprecincts.csv
    pointer: counties/whitman/raw/measures/whitman-town-of-rosalia-proposition-no-1/sos-results-20231107-whitman-precincts.csv.url
    accessed: 2026-10-08
  - id: S6
    tier: 1
    type: results
    outlet: "Washington Secretary of State election results, Whitman County precinct export, November 4, 2025 general"
    url: https://results.vote.wa.gov/results/20251104/export/20251104_whitmanprecincts.csv
    pointer: counties/whitman/raw/measures/whitman-town-of-rosalia-proposition-no-1/sos-results-20251104-whitman-precincts.csv.url
    accessed: 2026-10-08
  - id: S7
    tier: 1
    type: government-website
    ref: Washington Department of Revenue, Local property tax levy detail for all counties, taxes due in 2025
    url: https://dor.wa.gov/sites/default/files/2025-10/All_County_Levy_Detail_2025.xlsx
    pointer: counties/whitman/raw/measures/whitman-town-of-rosalia-proposition-no-1/dor-all-county-levy-detail-2025.xlsx.url
    accessed: 2026-10-08
  - id: S8
    tier: 2
    type: government-website
    ref: Municipal Research and Services Center (MRSC), "Levy Lid Lifts"
    url: https://mrsc.org/explore-topics/finance/property-taxes/levy-lid-lifts
    pointer: counties/whitman/raw/measures/whitman-town-of-rosalia-proposition-no-1/mrsc-levy-lid-lifts.html.url
    accessed: 2026-10-08
  - id: S9
    tier: 1
    type: pdc
    ref: Public Disclosure Commission campaign finance summary (data.wa.gov 3h9x-7bvm), 2026 committees
    url: https://data.wa.gov/resource/3h9x-7bvm.json?$select=filer_name,filer_type,jurisdiction,jurisdiction_county&$where=election_year=2026%20AND%20filer_type=%27CO%27%20AND%20(jurisdiction_county=%27WHITMAN%27%20OR%20upper(filer_name)%20like%20%27%25OAKESDALE%25%27%20OR%20upper(filer_name)%20like%20%27%25PALOUSE%25%27%20OR%20upper(filer_name)%20like%20%27%25ROSALIA%25%27%20OR%20upper(filer_name)%20like%20%27%25ST%20JOHN%25%27%20OR%20upper(filer_name)%20like%20%27%25TEKOA%25%27%20OR%20upper(filer_name)%20like%20%27%25UNIONTOWN%25%27%20OR%20upper(filer_name)%20like%20%27%25LEVY%25%27)&$limit=200
    pointer: counties/whitman/raw/measures/whitman-town-of-rosalia-proposition-no-1/pdc-committees-towns-2026.json.url
    accessed: 2026-10-08
---
## What it does

A one-year special (excess) property tax levy for the town's City Street Fund, "to help defray the costs of street lights, seal coating, shoulder work, capital improvements, equipment and regular maintenance of city streets," levied on 2026 assessed value for collection in 2027 [S1][S2]. The explanatory statement lists streetlights, shoulder work, maintenance staff wages, equipment and regular street maintenance "including plowing/sanding," and says levy funds may be combined with grants for future street projects [S1][S2].

## Cost

- $50,000, at $1.50 per $1,000 of 2026 assessed value, collected in 2027 [S1][S2]. Unlike most town levies on this ballot, the title states the rate as a set figure rather than an estimate.
- In 2024 the Daily News reported the town's $50,000 street levy at $177 per $100,000 of assessed value ($1.77 per $1,000) [S4].

## Fiscal mechanics / What it replaces

MRSC describes excess levies under RCW 84.52.052 as separate from the regular levy, expiring after one year for all agencies except fire protection districts, and requiring a 60% majority [S8].

- **A recurring street levy.** Rosalia's November 2025 street levy passed with 153 yes, 66 no (69.9%) [S6]. The November 2024 street levy received 186 yes, 129 no (59.0%) [S3], below the 60% MRSC cites [S8], and the Department of Revenue's levy detail for 2025 collection lists Rosalia's regular levy ($58,641 at $1.84 per $1,000) but no Rosalia special levy [S7]. A town Proposition No. 1 also passed in November 2023 (108 yes, 62 no, 63.5%) [S5].

## Arguments for

After repeated recruitment attempts, no volunteers came forward to write a statement for the ballot measure [S1][S2].

## Arguments against

After repeated recruitment attempts, no volunteers came forward to write a statement against the ballot measure [S1][S2].

## Endorsements and campaign

None found. The PDC 2026 committee data lists no committee for or against this levy [S9].

## Lean notes

- `taxes`: a yes vote continues the town's annual one-year $50,000 street levy, which voters approved in 2025 [S6], at $1.50 per $1,000, below the $1.77 reported for the 2024 request [S1][S4]. Direction +1.
- `spending`: street lights, maintenance, plowing, equipment and grant match; upkeep, not expansion [S1]. Not mapped.
- `local-control`, `social`, `parental-rights`: not addressed. Not mapped.
