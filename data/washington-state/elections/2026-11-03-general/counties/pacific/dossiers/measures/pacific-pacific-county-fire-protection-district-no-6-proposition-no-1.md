---
slug: pacific-pacific-county-fire-protection-district-no-6-proposition-no-1
jurisdiction: Pacific County Fire Protection District No. 6
title: "Authorizing Regular Property Tax Levy"
researched_at: 2026-10-08
evidence_level: pamphlet-only
derived_from:
  - data/washington-state/elections/2026-11-03-general/counties/pacific/interim/measures.json
  - data/washington-state/elections/2026-11-03-general/counties/pacific/interim/voter-guide-text/measure-7391.txt
sources:
  - id: S1
    tier: 1
    type: pamphlet
    ref: VoteWA voters' guide, Pacific County, GENERAL 2026, measure 7391 (ballot title and explanatory statement by the district; no statements for or against were filed)
    url: https://voter.votewa.gov/elections/measure.ashx?m=7391&e=899&la=en&c=25
    pointer: counties/pacific/raw/votewa/voter-guide/measure-7391.json.url
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

The Board of Fire Commissioners adopted Resolution No. 2026-7-23-1 to authorize a regular property tax levy of $0.50 per $1,000 of assessed value in 2026 (collected in 2027), and a limit factor of up to 106% (but never above $1.50 per $1,000) for each of the five following years. "The maximum allowable levy in 2031, collected in 2032, shall serve as the base for subsequent levy limitations as provided by Chapter 84.55 RCW" [S1].

- **The district.** Pacific County Fire Protection District No. 6 [S1]. Its WA DOR 2025 fire-district polygon covers the Bay Center area on Willapa Bay (38 2nd St and 3 Park St E, Bay Center, both fall inside it; see `pipeline/build_votewa_lite_data.py`, Pacific block). Its 2025 commissioner race drew 134 votes [S2].
- **Who votes.** Voters inside the district; scoped to DOR's fire-district layer, value `6`.

## Cost

$0.50 per $1,000 of assessed value for 2027 collection, then up to 6% more levy revenue a year for five years (capped at $1.50 per $1,000) [S1]. The explanatory statement says this "restore[s]" the levy to $0.50; it does not give the current rate [S1]. (About $120 a year on a $240,000 property at $0.50, by arithmetic.)

## Fiscal mechanics / What it replaces

Without voter approval, fire districts can raise their levy revenue by only 1% a year; this measure lets the district exceed that limit [S1]. "This levy is the primary source of funding for emergency services provided by the District," and approval "will provide funding for the District to significantly improve and expand current fire and emergency services" [S1].

## Arguments for

No statement for was filed. The district says approval would let it "significantly improve and expand" fire and emergency services [S1].

## Arguments against

No statement against was filed [S1]. No PDC committee for or against was found [S3].

## Lean notes

- `taxes`: a yes vote is a levy lid lift (taxes pole_b) that restores the rate and allows up to 6% yearly growth for five years [S1]. Direction +2.
- `spending`: the district says the money would "significantly improve and expand" services [S1]; not mapped, since a small fire district's service expansion is not the program-expansion debate the axis describes.
