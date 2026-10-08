---
slug: whitman-town-of-oakesdale-proposition-no-2
jurisdiction: Town of Oakesdale
title: "Street Maintenance Levy"
researched_at: 2026-10-08
evidence_level: moderate
derived_from:
  - data/washington-state/elections/2026-11-03-general/counties/whitman/interim/voter-guide-text/measure-7400.txt
  - data/washington-state/elections/2026-11-03-general/counties/whitman/interim/app-measures.json
  - data/washington-state/elections/2026-11-03-general/counties/whitman/raw/whitman/sos-results-20241105-whitman-precincts.csv.url
  - data/washington-state/elections/2026-11-03-general/counties/whitman/raw/measures/whitman-town-of-oakesdale-proposition-no-2/
sources:
  - id: S1
    tier: 1
    type: pamphlet
    ref: VoteWA voters' guide, Whitman County, GENERAL 2026, measure 7400 (ballot title only; explanatory statement and statements for and against not submitted, hardship waiver on file with the county)
    url: https://voter.votewa.gov/elections/measure.ashx?m=7400&e=899&la=en&c=38
    pointer: counties/whitman/raw/votewa/voter-guide/measure-7400.json.url
    accessed: 2026-10-08
  - id: S2
    tier: 1
    type: results
    outlet: "WA Secretary of State election results, Whitman County precinct export, November 5, 2024 general"
    url: https://results.vote.wa.gov/results/20241105/export/20241105_whitmanprecincts.csv
    pointer: counties/whitman/raw/whitman/sos-results-20241105-whitman-precincts.csv.url
    accessed: 2026-10-08
  - id: S3
    tier: 1
    type: results
    outlet: "Washington Secretary of State election results, Whitman County precinct export, November 7, 2023 general"
    url: https://results.vote.wa.gov/results/20231107/export/20231107_whitmanprecincts.csv
    pointer: counties/whitman/raw/measures/whitman-town-of-oakesdale-proposition-no-2/sos-results-20231107-whitman-precincts.csv.url
    accessed: 2026-10-08
  - id: S4
    tier: 1
    type: results
    outlet: "Washington Secretary of State election results, Whitman County precinct export, November 4, 2025 general"
    url: https://results.vote.wa.gov/results/20251104/export/20251104_whitmanprecincts.csv
    pointer: counties/whitman/raw/measures/whitman-town-of-oakesdale-proposition-no-2/sos-results-20251104-whitman-precincts.csv.url
    accessed: 2026-10-08
  - id: S5
    tier: 1
    type: government-website
    ref: Washington Department of Revenue, Local property tax levy detail for all counties, taxes due in 2025
    url: https://dor.wa.gov/sites/default/files/2025-10/All_County_Levy_Detail_2025.xlsx
    pointer: counties/whitman/raw/measures/whitman-town-of-oakesdale-proposition-no-2/dor-all-county-levy-detail-2025.xlsx.url
    accessed: 2026-10-08
  - id: S6
    tier: 2
    type: government-website
    ref: Municipal Research and Services Center (MRSC), "Levy Lid Lifts"
    url: https://mrsc.org/explore-topics/finance/property-taxes/levy-lid-lifts
    pointer: counties/whitman/raw/measures/whitman-town-of-oakesdale-proposition-no-2/mrsc-levy-lid-lifts.html.url
    accessed: 2026-10-08
  - id: S7
    tier: 1
    type: pdc
    ref: Public Disclosure Commission campaign finance summary (data.wa.gov 3h9x-7bvm), 2026 committees
    url: https://data.wa.gov/resource/3h9x-7bvm.json?$select=filer_name,filer_type,jurisdiction,jurisdiction_county&$where=election_year=2026%20AND%20filer_type=%27CO%27%20AND%20(jurisdiction_county=%27WHITMAN%27%20OR%20upper(filer_name)%20like%20%27%25OAKESDALE%25%27%20OR%20upper(filer_name)%20like%20%27%25PALOUSE%25%27%20OR%20upper(filer_name)%20like%20%27%25ROSALIA%25%27%20OR%20upper(filer_name)%20like%20%27%25ST%20JOHN%25%27%20OR%20upper(filer_name)%20like%20%27%25TEKOA%25%27%20OR%20upper(filer_name)%20like%20%27%25UNIONTOWN%25%27%20OR%20upper(filer_name)%20like%20%27%25LEVY%25%27)&$limit=200
    pointer: counties/whitman/raw/measures/whitman-town-of-oakesdale-proposition-no-2/pdc-committees-towns-2026.json.url
    accessed: 2026-10-08
---
## What it does

A one-year special property tax levy of $60,000 "for street work, street lights, street expenses and maintenance for the Town of Oakesdale," levied on 2026 assessed value for collection in 2027 [S1]. The measure does not appear in the printed local voters' pamphlet; the VoteWA record says no explanatory statement or statements for or against were submitted and that a hardship waiver is on file with the county [S1].

## Cost

- $60,000, an estimated $1.93 per $1,000 of 2026 assessed value, collected in 2027 [S1].
- Oakesdale's Proposition No. 1 on the same ballot asks for a separate $14,000 fire and EMS levy at an estimated $0.46 per $1,000 [S1]; together the two would be about $2.39 per $1,000.

## Fiscal mechanics / What it replaces

MRSC describes excess levies under RCW 84.52.052 as separate from the regular levy, expiring after one year for all agencies except fire protection districts, and requiring a 60% majority [S6].

- **Prior Oakesdale levies.** In November 2024 Oakesdale voters approved a "Street Maintenance Levy" (164 yes, 89 no, 64.8%) and a "Street Work Levy" (167 yes, 85 no, 66.3%) [S2], and in November 2023 approved town Propositions No. 1 and No. 2 (89.1% and 78.8% yes) [S3]. The November 2025 general ballot carried no Oakesdale town levy [S4].
- For 2025 collection the Department of Revenue lists an Oakesdale "Special" levy of $124,000 at $4.19 per $1,000, in addition to the town's regular levy of $56,925 at $1.85 per $1,000 [S5].
- The sources found do not give the amounts of the 2024 street levies separately.

## Arguments for

No statement for was submitted; a hardship waiver is on file with the county [S1].

## Arguments against

No statement against was submitted [S1].

## Endorsements and campaign

None found. The PDC 2026 committee data lists no committee for or against this levy [S7].

## Lean notes

- `taxes`: a yes vote approves a one-year special property tax of $60,000 (about $1.93 per $1,000) for 2027 [S1]. Oakesdale street levies passed in 2024, but no Oakesdale town levy was on the November 2025 ballot [S2][S4], so the sources do not show it continuing a levy collected in 2026. Direction +2.
- `spending`: street work, lights and maintenance; upkeep, not expansion [S1]. Not mapped.
- `local-control`, `social`, `parental-rights`: not addressed. Not mapped.
