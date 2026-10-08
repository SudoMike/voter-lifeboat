---
slug: pacific-pacific-county-fire-protection-district-no-3-proposition-no-1
jurisdiction: Pacific County Fire Protection District No. 3
title: "Property Tax Levy Lid Lift for Fire Protection, Suppression and Prevention"
researched_at: 2026-10-08
evidence_level: pamphlet-only
derived_from:
  - data/washington-state/elections/2026-11-03-general/counties/pacific/interim/measures.json
  - data/washington-state/elections/2026-11-03-general/counties/pacific/interim/voter-guide-text/measure-7389.txt
sources:
  - id: S1
    tier: 1
    type: pamphlet
    ref: VoteWA voters' guide, Pacific County, GENERAL 2026, measure 7389 (ballot title and explanatory statement by the district's board; no statements for or against were filed)
    url: https://voter.votewa.gov/elections/measure.ashx?m=7389&e=899&la=en&c=25
    pointer: counties/pacific/raw/votewa/voter-guide/measure-7389.json.url
    accessed: 2026-10-08
  - id: S2
    tier: 1
    type: official-election
    outlet: Washington Secretary of State, November 4, 2025 general election results, Pacific County
    url: https://results.vote.wa.gov/results/20251104/pacific/
    pointer: counties/pacific/raw/sos/results-20251104-pacific.html.url
    accessed: 2026-10-08
  - id: S3
    tier: 1
    type: pdc
    ref: PDC campaign finance summary (data.wa.gov 3h9x-7bvm), 2026 committees with a Pacific County jurisdiction
    url: https://data.wa.gov/resource/3h9x-7bvm.json
    pointer: counties/pacific/raw/pdc/pdc-committees-2026.json.url
    accessed: 2026-10-08
---
## What it does

The district's board adopted Resolution No. 26-2503-01 to set its regular property tax for maintenance and operations at up to $0.61 per $1,000 of assessed value, levied in 2026 for collection in 2027. "The maximum allowable levy in 2026 shall serve as the base for computing subsequent levy limitations as provided by chapter 84.55 RCW" [S1].

- **The district.** Pacific County Fire Protection District No. 3 provides fire prevention, protection and suppression to Baleville, Elk Horn Flats, Old Willapa, East Raymond, Menlo, Lebam and Frances [S1]. Its 2025 commissioner race drew 698 votes [S2].
- **Who votes.** Voters inside the district; the package scopes the measure to WA DOR's 2025 fire-district layer, value `3` (point-checked at 1000 State Route 6, near Menlo; see `pipeline/build_votewa_lite_data.py`, Pacific block).
- **Approval threshold.** Simple majority [S1].

## Cost

Up to $0.61 per $1,000 of assessed value for 2027 collection, which the district says is a $0.20 per $1,000 increase [S1]. (About $48 more a year on a $240,000 property, by arithmetic from the stated increase.)

## Fiscal mechanics / What it replaces

A levy lid lift on the district's existing regular levy. The district says its tax revenue has grown about 1.76% a year over the last 14 years, "far under the annual inflation rate," as costs have "recently risen significantly," and that the increase is needed to keep its current service level [S1].

## Arguments for

No statement for was filed. The board's explanatory statement says the levy "will ensure that the District will be able to continue its current service levels for the near future" [S1].

## Arguments against

No statement against was filed [S1]. No PDC committee for or against was found [S3].

## Lean notes

- `taxes`: a yes vote is a levy lid lift (named in the taxes pole_b) that raises the district's rate by about half, from about $0.41 to $0.61 per $1,000 [S1]. Direction +2.
