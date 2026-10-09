---
slug: wahkiakum-wahkiakum-county-fire-protection-district-no-2-skamokawa-ballot-measure
jurisdiction: Wahkiakum County Fire Protection District No. 2 (Skamokawa)
title: "Emergency Medical Services Levy - Replacement of Existing Levy"
researched_at: 2026-10-09
evidence_level: pamphlet-only
derived_from:
  - data/washington-state/elections/2026-11-03-general/counties/wahkiakum/interim/measures.json
sources:
  - id: S1
    tier: 1
    type: official-election
    ref: Wahkiakum County Elections, General Election Sample Ballot, November 3, 2026, page 1 (ballot title; Wahkiakum prints no local voters' pamphlet, so no explanatory statement or statements for or against were published)
    url: https://www.co.wahkiakum.wa.us/DocumentCenter/View/3637
    pointer: counties/wahkiakum/raw/wahkiakum/sample-ballot.pdf.url
    accessed: 2026-10-08
  - id: S2
    tier: 1
    type: official-record
    outlet: Wahkiakum County Assessor, 2024 Assessed Values and 2025 Property Tax Levy Rates
    url: https://www.co.wahkiakum.wa.us/DocumentCenter/View/3323/2024-for-2025
    pointer: counties/wahkiakum/raw/wahkiakum/tax-rates-2024-for-2025.pdf.url
    accessed: 2026-10-08
  - id: S3
    tier: 1
    type: official-record
    outlet: RCW 84.52.069, Emergency medical care and service levies (as published on leg.wa.gov 2026-10-09)
    url: https://app.leg.wa.gov/RCW/default.aspx?cite=84.52.069
    pointer: counties/wahkiakum/raw/law/rcw-84.52.069.html.url
    accessed: 2026-10-09
  - id: S4
    tier: 2
    type: legal-notice
    outlet: The Wahkiakum County Eagle, "Notice of Public Hearing on 2026 Budget and Levy of Wahkiakum County Fire Protection District No. 2" (2025-11-13)
    url: https://theeagle.news/2025/11/13/notice-of-public-hearing-on-2026-budget-and-levy-of-wahkiakum-county-fire-protection-district-no-2-3/
    pointer: counties/wahkiakum/raw/news/eagle-2025-11-13-notice-of-public-hearing-on-2026-budget-and-levy-o.html.url
    accessed: 2026-10-08
  - id: S5
    tier: 1
    type: official-election
    outlet: Washington Secretary of State, November 4, 2025 general election results, Wahkiakum County
    url: https://results.vote.wa.gov/results/20251104/wahkiakum/
    pointer: counties/wahkiakum/raw/sos/results-20251104-wahkiakum.html.url
    accessed: 2026-10-08
  - id: S6
    tier: 1
    type: pdc
    outlet: PDC campaign finance summary (data.wa.gov 3h9x-7bvm), 2026 Wahkiakum County candidates and committees
    url: https://data.wa.gov/resource/3h9x-7bvm.json?election_year=2026&jurisdiction_county=WAHKIAKUM&$limit=200
    pointer: counties/wahkiakum/raw/pdc/pdc-candidates-2026.json.url
    accessed: 2026-10-08
---
## What it does

The ballot title describes a replacement of Skamokawa Fire District 2's existing emergency medical services levy with a ten-year property tax under Resolution #2026-01, collected from 2027 for EMS operating and equipment costs. After the first year, growth is limited and tied to the Consumer Price Index [S1]. The ballot cites RCW 84.52.069 [S1], whose text as published on leg.wa.gov limits EMS levies to $0.50 per $1,000 [S3]. The ballot does not explain the proposed $1.00 rate [S1].

"If approved by voters, this proposition would authorize Wahkiakum County Fire Protection District #2 (Skamokawa) to levy a regular property tax at a rate not to exceed one dollar per one thousand dollars of assessed valuation on all taxable property within the district. The levy proceeds would be used to fund operational and equipment costs as more fully described in Fire District #2 Resolution #2026-01 and RCW 84.52.069. The levy would be authorized for a ten-year period, with collection beginning in 2027; and would be subject to RCW chapter 84.55 limitations on levy increases in years two through ten, which are linked to the Consumer Price Index. The final year's levy dollar amount would be used to compute limitations for subsequent levies as provided by RCW Chapter 84.55." Qualifying seniors, veterans and disabled persons would be eligible for exemption under RCW 84.36.381 [S1].

- **The district.** Fire Protection District No. 2 is the Skamokawa district [S1]; its fire station is at 33 East Valley Road, Skamokawa [S4]. Its 2024 assessed value was $71,456,191 [S2]. Its 2025 commissioner race drew 162 votes [S5].
- **Who votes.** Voters inside the district only; scoped to WA DOR's fire-district layer, value `2` (Skamokawa addresses on State Route 4 and Middle Valley Road fall inside it; see `pipeline/build_votewa_lite_data.py`, Wahkiakum block).

## Cost

Up to $1.00 per $1,000 of assessed value a year for ten years, starting with 2027 collection; after the first year, levy growth is limited under chapter 84.55 RCW and tied to the Consumer Price Index [S1]. By arithmetic: up to $300 a year on a $300,000 property, and up to about $71,000 a year on the district's 2024 assessed value [S2].

The ballot title calls this a replacement of an existing levy but does not give the current rate [S1]. The county's 2025 levy-rate sheet shows Fire District 2's regular fire levy at $0.41984 per $1,000 and the county EMS levy at $0.29670 in the district's tax code areas, with no separate Fire District 2 EMS rate; this dossier could not determine what the existing district EMS levy is or whether $1.00 is an increase [S2].

## Fiscal mechanics / What it replaces

EMS levy proceeds may be used only for emergency medical care and services, including personnel, training, equipment, vehicles and structures [S3]. The statute as published on leg.wa.gov (amendment history through 2018) caps an EMS levy at fifty cents per $1,000, limits any other district's EMS levy to the difference up to fifty cents where the county levies one, and bars another district's EMS proposition from the same ballot as a county EMS proposition [S3]. The county's own EMS levy renewal is on this ballot [S1]. Neither the ballot title nor any published statement explains how the $1.00 rate relates to those provisions; Resolution #2026-01 was not found online. Under the published text a renewal of an existing six- or ten-year levy needs a simple majority, a first imposition 60% [S3].

## Arguments for

No statement for was published [S1].

## Arguments against

No statement against was published [S1], and no PDC committee for or against a Wahkiakum measure is registered [S6].

## Lean notes

- `taxes`: a yes vote authorizes a ten-year EMS property tax of up to $1.00 per $1,000 that the ballot title describes as replacing an existing levy [S1]. Whether it raises the district's current EMS rate is not established [S2], so it maps at the renewal tier: direction +1.
- `spending`: not mapped; the levy funds EMS operations and equipment [S1].
