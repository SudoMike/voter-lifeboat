---
slug: mason-mccleary-school-district-no-65-proposition-no-1
jurisdiction: McCleary School District No. 65
title: "Bonds to Improve Safety, Security and School Facilities"
researched_at: 2026-10-09
evidence_level: moderate
derived_from:
  - data/washington-state/elections/2026-11-03-general/counties/mason/interim/measures.json
  - data/washington-state/elections/2026-11-03-general/counties/mason/interim/voter-guide-text/measure-7385.txt
  - data/washington-state/elections/2026-11-03-general/counties/mason/interim/pdf-text/local-voters-pamphlet.txt
  - data/washington-state/elections/2026-11-03-general/counties/mason/raw/measures/mason-mccleary-school-district-no-65-proposition-no-1/
sources:
  - id: S1
    tier: 1
    type: pamphlet
    ref: local-voters-pamphlet page 28 (Mason County Official Local Voters' Pamphlet, November 3, 2026 General Election, McCleary School District No. 65 bonds: ballot title, explanatory statement)
    url: https://www.masoncountywa.gov/Documents/Departments/Auditor/Elections/Current%20Election/General_2026_Local_Voters_Pamphlet.pdf
    pointer: counties/mason/raw/mason/local-voters-pamphlet.pdf.url
    accessed: 2026-10-09
  - id: S2
    tier: 1
    type: pamphlet
    ref: VoteWA voters' guide, Mason County, GENERAL 2026, measure 7385 (ballot title, explanatory statement)
    url: https://voter.votewa.gov/elections/measure.ashx?m=7385&e=899&la=en&c=23
    pointer: counties/mason/raw/votewa/voter-guide/measure-7385.json.url
    accessed: 2026-10-09
  - id: S3
    tier: 1
    type: government-website
    outlet: McCleary School District, "Levy and Bond" page
    url: https://mccleary.wednet.edu/our-district/levy-bond/
    pointer: counties/mason/raw/measures/mason-mccleary-school-district-no-65-proposition-no-1/mccleary-levy-bond-page.html.url
    accessed: 2026-10-09
  - id: S4
    tier: 1
    type: government-website
    outlet: McCleary School District, "Want to Learn More About the Bond Measure?"
    url: https://mccleary.wednet.edu/want-to-learn-more-about-the-bond-measure/
    pointer: counties/mason/raw/measures/mason-mccleary-school-district-no-65-proposition-no-1/mccleary-bond-info-sessions.html.url
    accessed: 2026-10-09
  - id: S5
    tier: 1
    type: pdc
    ref: PDC campaign finance summary (data.wa.gov 3h9x-7bvm), 2026 committees named for libraries, Timber/TRL, Shelton, Pioneer, Southside or McCleary
    url: https://data.wa.gov/resource/3h9x-7bvm.json
    pointer: counties/mason/raw/measures/mason-timberland-regional-library-district-proposition-no-1/pdc-committees-query-2026.json.url
    accessed: 2026-10-09
---
## What it does

The McCleary School District No. 65 board (Resolution No. 2026-08) asks voters to approve $12,800,000 of general obligation bonds, maturing within 21 years, repaid by annual excess property taxes, for capital work at the McCleary School [S1][S2]:

- Safety and security upgrades: a single-point entry security vestibule, door locks, keycard access, fire alarm [S1][S2].
- Facility improvements: building exteriors, HVAC, drainage, parking areas, access routes [S1][S2].
- Modernized playgrounds for safety and accessibility [S1][S2].

The district spans Grays Harbor and Mason counties: the explanatory statement refers property owners to both counties' assessors for exemptions [S1][S2]. Only Mason voters living inside the district vote on it here (scope: `SCHDST` `65`, see `pipeline/build_votewa_lite_data.py`, Mason block).

## Cost

- The district estimates the bond rate at $1.42 per $1,000 of assessed value: about $426 a year on a $300,000 home, $639 on a $450,000 home and $852 on a $600,000 home [S3].
- Total $12.8 million raised over 21 years [S1][S3].

## Fiscal mechanics / What it replaces

A new bond, not a replacement. On February 10, 2026, district voters approved a replacement two-year EP&O levy (Proposition 1) but rejected Proposition 2, a bond that would have paid for drainage, roofing and outdoor-access repairs, an auxiliary gym and security improvements including a front vestibule [S3]. The district says its community identified bond priorities in summer 2025 and gave more feedback in summer 2026, and that it has applied for a state Small Schools Modernization Grant, which does not cover all repair and building costs [S3]. It held community information sessions on the November measure [S4].

## Arguments for

No statement for was submitted [S1]. The district says the bond would fund "safety and security improvements, key facility repairs, student technology tools, and new playground equipment" [S3].

## Arguments against

No statement against was submitted [S1]. No committee for or against was found in PDC records [S5].

## Lean notes

- `taxes`: a yes vote authorizes new bonds repaid by a new excess property tax, estimated at $1.42 per $1,000 for up to 21 years [S1][S3]. Direction +2.
- `parental-rights`: capital facilities only; nothing on notification, records or opt-outs [S1][S2]. Not mapped.
- `spending`: a capital investment, but the dossier records no for/against argument about spending discipline. Not mapped.
