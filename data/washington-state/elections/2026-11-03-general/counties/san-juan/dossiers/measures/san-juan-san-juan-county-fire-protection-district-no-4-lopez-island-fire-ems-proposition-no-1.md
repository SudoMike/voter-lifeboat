---
slug: san-juan-san-juan-county-fire-protection-district-no-4-lopez-island-fire-ems-proposition-no-1
jurisdiction: San Juan County Fire Protection District No. 4 (Lopez Island Fire & EMS)
title: "Property Tax Levy for Fire Protection and Emergency Medical"
researched_at: 2026-10-08
evidence_level: moderate
derived_from:
  - data/washington-state/elections/2026-11-03-general/counties/san-juan/interim/app-measures.json
  - data/washington-state/elections/2026-11-03-general/counties/san-juan/interim/pdf-text/local-voters-pamphlet.txt
  - data/washington-state/elections/2026-11-03-general/counties/san-juan/interim/voter-guide-text/measure-7286.txt
  - data/washington-state/elections/2026-11-03-general/counties/san-juan/raw/san-juan/resolution-fire-district-4-levy.pdf.url
  - data/washington-state/elections/2026-11-03-general/counties/san-juan/raw/san-juan/dor-all-county-levy-detail-2025.xlsx.url
sources:
  - id: S1
    tier: 1
    type: pamphlet
    ref: local-voters-pamphlet pages 50-51 (San Juan County November 3, 2026 General Election Voters' Pamphlet, San Juan County Fire Protection District No. 4 Proposition No. 1; explanatory statement by Brian K. Snure, attorney for the district; argument for by Jim Ghiglione)
    url: https://www.sanjuancountywa.gov/DocumentCenter/View/36027/2026-General-VP-San-Juan-County---Final-State-and-County?bidId=
    pointer: counties/san-juan/raw/san-juan/local-voters-pamphlet.pdf.url
    accessed: 2026-10-08
  - id: S2
    tier: 1
    type: pamphlet
    ref: VoteWA voters' guide, San Juan County, GENERAL 2026, measure 7286 (ballot title, explanatory statement, argument for)
    url: https://voter.votewa.gov/elections/measure.ashx?m=7286&e=899&la=en&c=28
    pointer: counties/san-juan/raw/votewa/voter-guide/measure-7286.json.url
    accessed: 2026-10-08
  - id: S3
    tier: 1
    type: official-page
    ref: San Juan County Elections, Current Election page ("San Juan County Fire District No. 4 (Lopez) Resolution No. 2026-02 ... Property Tax Levy For Fire Protection and Emergency Medical"; the linked resolution is a scanned image with no text layer)
    url: https://www.sanjuancountywa.gov/1292/Current-Election
    pointer: counties/san-juan/raw/san-juan/current-election.html.url
    accessed: 2026-10-08
  - id: S4
    tier: 1
    type: government-data
    ref: Washington State Department of Revenue, Local Property Tax Levy Detail for All Counties, taxes due in 2025 (San Juan row 280700400 'Fire Dist #4 Lopez')
    url: https://dor.wa.gov/sites/default/files/2025-10/All_County_Levy_Detail_2025.xlsx
    pointer: counties/san-juan/raw/san-juan/dor-all-county-levy-detail-2025.xlsx.url
    accessed: 2026-10-08
  - id: S5
    tier: 1
    type: official-record
    ref: RCW 84.55.050 (levy lid lift by majority vote; multi-year limit factors up to 10 consecutive years)
    url: https://app.leg.wa.gov/RCW/default.aspx?cite=84.55.050
    accessed: 2026-10-08
  - id: S6
    tier: 1
    type: gis
    ref: WA DOR FIR2025 (WADOR_PropertyTax MapServer layer 7) DISTATTRIB '4' at 2225 Fisherman Bay Rd, 86 School Rd and 4102 Mud Bay Rd, Lopez Island; none on Decatur Island; county Junior Tax District Boundaries 'San Juan County Fire Protection District #4' (same polygon as the Port of Lopez)
    url: https://webgis.dor.wa.gov/arcgis/rest/services/Programs/WADOR_PropertyTax/MapServer/7
    pointer: counties/san-juan/raw/san-juan/gis-junior-tax-districts.json.url
    accessed: 2026-10-08
---

## What it does

Proposition No. 1 is a multi-year levy lid lift for Lopez Island Fire & EMS (San Juan County Fire Protection District No. 4) under Resolution No. 2026-02 [S1][S2][S3]. It would restore the district's regular property tax levy to $0.74 per $1,000 of assessed value, assessed in 2026 for collection in 2027, and for 2027 through 2035 let the levy grow by a 103% limit factor (up to 3% a year) instead of the statutory 101%; the maximum allowable 2035 levy becomes the base for later limits [S1][S2].

- Fire districts may levy up to $1.50 per $1,000 [S1].
- After the ten-year period, absent another vote, the levy returns to the 1% growth limit [S1].
- A levy lid lift passes with a majority of those voting on it; state law allows limit factors for up to 10 consecutive years [S5].
- Exemptions for qualifying seniors, veterans and others under chapter 84.36 RCW apply [S1].
- The district is Lopez Island and nearby small islands (not Decatur) [S6].

## Cost

- **History:** voters approved $0.83 per $1,000 in 2013 (the argument for says 2014); the 1% limit has since eroded the rate to $0.47 [S1].
- **Current rate:** for taxes due in 2025 the district levied $0.47611 per $1,000 on $2,232,340,908 of assessed value, $1,062,838 [S4].
- **Proposed rate:** $0.74 per $1,000 for 2027 collection, an increase of $0.27 [S1].
- **Computed for this dossier from [S1] and [S4]:** on a $500,000 property the district tax would go from about $238 a year to $370 in 2027. At 2025 assessed values the levy would be about $1.65 million instead of $1.06 million. The 103% factor then lets the levy grow up to 3% a year through 2035.

## Background

- The commissioners say the levy is needed "to maintain the current level of fire protection, fire suppression and emergency medical services while providing for the safety of our firefighters" [S1].
- The argument for says the district has stretched resources by extending loans, refurbishing and buying used vehicles and equipment, seeking grants, billing insurers for EMS, and cooperative purchasing, and that it is continuing a strategic plan begun in 2005 and updated in 2021 [S1].

## Arguments for

- Jim Ghiglione: EMTs, paramedics and firefighters serve 24 hours a day; 12 years have passed since the last levy; the money maintains current emergency services; the 3% factor helps "combat inflation, instead of the standard 1% limit" [S1][S2].

## Arguments against

- None filed. The pamphlet says that "after repeated recruitment attempts, no volunteers came forward to write a statement against the ballot measure" [S1].

## Lean notes

- `taxes`: a yes vote raises the district's regular levy rate by more than half, from about $0.47 to $0.74 per $1,000, and replaces the 1% growth limit with up to 3% for nine years [S1][S4]. It stays within the $1.50 cap and below the 2013 voter-approved $0.83, the case for +1; the size of the increase and the escalator support +2.
- `spending`: the district frames the money as maintaining current service levels; no clear mapping.
