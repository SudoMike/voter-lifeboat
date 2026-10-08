---
slug: pacific-timberland-regional-library-district-proposition-no-1
jurisdiction: Timberland Regional Library District
title: "Regular Property Tax Levy Lid Lift for Library Services, Operations and Maintenance"
researched_at: 2026-10-08
evidence_level: rich
derived_from:
  - data/washington-state/elections/2026-11-03-general/counties/pacific/interim/measures.json
  - data/washington-state/elections/2026-11-03-general/counties/pacific/interim/voter-guide-text/measure-7284.txt
  - data/washington-state/elections/2026-11-03-general/counties/pacific/raw/measures/pacific-timberland-regional-library-district-proposition-no-1/
sources:
  - id: S1
    tier: 1
    type: pamphlet
    ref: VoteWA voters' guide, Pacific County, GENERAL 2026, measure 7284 (ballot title, explanatory statement, statements for and against, rebuttals)
    url: https://voter.votewa.gov/elections/measure.ashx?m=7284&e=899&la=en&c=25
    pointer: counties/pacific/raw/votewa/voter-guide/measure-7284.json.url
    accessed: 2026-10-08
  - id: S2
    tier: 1
    type: government-website
    outlet: Timberland Regional Library, "Levy" page
    url: https://trl.org/levy/
    pointer: counties/pacific/raw/measures/pacific-timberland-regional-library-district-proposition-no-1/trl-levy.html.url
    accessed: 2026-10-08
  - id: S3
    tier: 2
    type: news
    outlet: Chinook Observer (Thurston Chronicle), "Library system OKs tax plan for November ballot" (2026-07-26)
    url: https://chinookobserver.com/2026/07/26/library-system-oks-tax-plan-for-november-ballot/
    pointer: counties/pacific/raw/measures/pacific-timberland-regional-library-district-proposition-no-1/co-2026-07-26-library-tax-plan.html.url
    accessed: 2026-10-08
  - id: S4
    tier: 1
    type: pdc
    ref: PDC campaign finance summary (data.wa.gov 3h9x-7bvm), 2026 committees with a Pacific County jurisdiction or named for libraries/Timberland
    url: https://data.wa.gov/resource/3h9x-7bvm.json
    pointer: counties/pacific/raw/pdc/pdc-committees-2026.json.url
    accessed: 2026-10-08
---
## What it does

Proposition No. 1 would "restore the District's regular property tax levy rate for library services, operations and maintenance from $0.22 to $0.35 per $1,000 of assessed valuation for both 2027 and 2028, subject to applicable limitations." The 2028 levy amount becomes the base for later limits under chapter 84.55 RCW. The Board of Trustees adopted Resolution No. 26-002 [S1].

- **The district.** Timberland Regional Library (TRL) has 29 branches in Grays Harbor, Lewis, Mason, Pacific and Thurston counties, and voters in all five counties decide the measure [S1].
- **Who votes in Pacific County.** All of Pacific County is in TRL: WA DOR's 2025 library-district layer has a single Pacific polygon whose area equals the county's, and addresses in South Bend, Raymond, Long Beach, Ilwaco, Ocean Park, Naselle, Tokeland and Chinook all fall inside it (see `pipeline/build_votewa_lite_data.py`, Pacific block). The measure is scoped county-wide.
- **What the money pays for.** The explanatory statement says approval "would provide funding necessary to maintain Library services, staffing, collections, and open hours" [S1]. The board president said voters can either approve an increase or TRL must make "pretty substantial cuts to live within our revenue" [S3].
- **If it fails.** "Further reductions in staffing, books and materials, hours, online services, bookmobile services and programming will begin in 2027," and facility maintenance could be delayed [S1]. The rate would stay at about $0.22 [S2].

## Cost

- Rate: from $0.228924 to $0.35 per $1,000 of assessed value in 2027 and 2028 [S1]. State law allows up to $0.50 [S1][S3].
- Explanatory statement: about $40.44 a year ($3.37 a month) on a $334,000 home [S1].
- TRL's Pacific County estimate: $2.58 a month or $31 a year on the 2025 median home value of $239,100 (revised Aug. 20, 2026, from DOR data). Libraries make up 2.63% of Pacific County property taxes [S2].

## Fiscal mechanics / What it replaces

A levy lid lift on TRL's existing regular levy [S1]. About 96% of TRL's revenue comes from its property tax levy [S1][S2]; budget documents put it at 93.7% for 2026 [S3]. The levy rate has fallen under the 1% annual growth limit to about $0.22; TRL last sought an increase in 2009, which was narrowly defeated [S1][S3]. The lift is TRL's answer to a $3.8 million budget shortfall that led to layoffs and the resignation of its executive director; trustees chose $0.35 over $0.30 and $0.40 options because it rebuilds reserves to the required threshold within a year [S3].

## Arguments for

Statement for and rebuttal [S1]:
- TRL's levy "hasn't increased in 25 years"; the measure is "a long overdue cost-of-living raise."
- Restores hours and staffing and expands collections and community programs.

## Arguments against

Statement against and rebuttal [S1]:
- A no vote "is a vote for fiscal responsibility, taxpayer accountability, and careful budgeting" while households face rising costs and many levies.
- The library should first reduce costs, improve efficiency, seek grants and partnerships; "Voting 'No' is not a vote against libraries or literacy."
- Rebuttal: "Libraries matter, but raising property taxes without accountability is wrong."

## Endorsements and campaign

PDC lists a "Yes For Libraries" committee with a Thurston County jurisdiction ($46,855.18 raised); no committee with a Pacific County jurisdiction for or against was found [S4].

## Lean notes

- `taxes`: a yes vote is a levy lid lift, named in the taxes pole_b, raising TRL's regular rate from $0.228924 to $0.35 per $1,000 [S1][S2]. Direction +2.
- `spending`: restores services cut in 2026 rather than expanding programs; not mapped (consistent with the Grays Harbor, Lewis and Mason packages' treatment of the same measure).
- `social` / `parental-rights`: the measure does not change collections or access policy [S1]. Not mapped.
