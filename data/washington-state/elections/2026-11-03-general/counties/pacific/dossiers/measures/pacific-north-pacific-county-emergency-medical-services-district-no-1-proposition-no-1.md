---
slug: pacific-north-pacific-county-emergency-medical-services-district-no-1-proposition-no-1
jurisdiction: North Pacific County Emergency Medical Services District No. 1
title: "Ambulance and Emergency Medical Services Funding"
researched_at: 2026-10-08
evidence_level: moderate
derived_from:
  - data/washington-state/elections/2026-11-03-general/counties/pacific/interim/measures.json
  - data/washington-state/elections/2026-11-03-general/counties/pacific/interim/voter-guide-text/measure-7388.txt
  - data/washington-state/elections/2026-11-03-general/counties/pacific/raw/sos/
sources:
  - id: S1
    tier: 1
    type: pamphlet
    ref: VoteWA voters' guide, Pacific County, GENERAL 2026, measure 7388 (ballot title, explanatory statement; no statements for or against were filed)
    url: https://voter.votewa.gov/elections/measure.ashx?m=7388&e=899&la=en&c=25
    pointer: counties/pacific/raw/votewa/voter-guide/measure-7388.json.url
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
    type: official-election
    outlet: Washington Secretary of State, November 5, 2024 general election results, Pacific County
    url: https://results.vote.wa.gov/results/20241105/pacific/
    pointer: counties/pacific/raw/sos/results-20241105-pacific.html.url
    accessed: 2026-10-08
  - id: S4
    tier: 1
    type: official-election
    outlet: Washington Secretary of State, November 3, 2020 general election results, Pacific County
    url: https://results.vote.wa.gov/results/20201103/pacific/
    pointer: counties/pacific/raw/sos/results-20201103-pacific.html.url
    accessed: 2026-10-08
  - id: S5
    tier: 1
    type: pdc
    ref: PDC campaign finance summary (data.wa.gov 3h9x-7bvm), 2026 committees with a Pacific County jurisdiction
    url: https://data.wa.gov/resource/3h9x-7bvm.json
    pointer: counties/pacific/raw/pdc/pdc-committees-2026.json.url
    accessed: 2026-10-08
---
## What it does

The North Pacific County Emergency Medical Services District No. 1 adopted Resolution 2026-721 to ask voters for "an excess levy of forty cents per thousand dollars of assessed value ($.40/1000av), replacing the expired 2026 levy," to be collected in 2027 "to subsidize Ambulance and emergency medical services" in its service area [S1].

- **The district.** It provides ambulance and medical response for "the greater Naselle, Nemah, Bay Center, South Bend, Raymond and Willapa Valley areas," supplying vehicles and equipment, with staffing through contracts with the City of Raymond and Pacific County Fire Protection District No. 4 [S1].
- **Who votes.** The levy applies to "all property in Pacific County, except for that property which is within the boundaries of the Ocean Beach, Ocosta, or North River School Districts" [S1]: the Long Beach peninsula, Ilwaco and Chinook (Ocean Beach SD), Tokeland and North Cove (Ocosta SD) and the North River area are outside. The package scopes it to WA DOR's 2025 EMS-district layer, value `1` (point-checked in South Bend, Raymond, Naselle and Bay Center; see `pipeline/build_votewa_lite_data.py`, Pacific block).
- **Approval threshold.** An excess levy that "must be renewed annually" and needs 60% approval [S1].

## Cost

$0.40 per $1,000 of assessed value, capped at $800,000 in total, for collection in 2027 only [S1]. (About $96 on a $240,000 property, by arithmetic from the stated rate.)

## Fiscal mechanics / What it replaces

A one-year excess levy that replaces the expiring 2026 levy so the district can "continue its' current service levels through 2027" [S1]. Voters have renewed it every recent year it appeared on the ballot: 73.62% yes in November 2025 (2,763 votes) [S2], 68.49% in 2024 (5,230 votes) [S3] and 74.27% in 2020 (5,317 votes) [S4].

## Arguments for

No statement for was filed [S1]. The district's explanatory statement says the levy keeps current ambulance service levels through 2027 [S1].

## Arguments against

No statement against was filed [S1]. No PDC committee for or against was found [S5].

## Lean notes

- `taxes`: a yes vote approves an excess property tax levy [S1]. It renews an expiring annual levy rather than raising a rate, so +1 rather than +2.
- `spending`: continues existing service levels; not mapped.
