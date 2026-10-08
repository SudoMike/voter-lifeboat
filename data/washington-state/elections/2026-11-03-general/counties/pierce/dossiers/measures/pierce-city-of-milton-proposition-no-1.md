---
slug: pierce-city-of-milton-proposition-no-1
jurisdiction: City of Milton
title: Additional Sales and Use Tax for Police and Public Safety
researched_at: 2026-10-08
evidence_level: moderate
derived_from:
  - data/washington-state/elections/2026-11-03-general/counties/pierce/interim/measures.json
  - data/washington-state/elections/2026-11-03-general/counties/pierce/raw/measures/pierce-city-of-milton-proposition-no-1/
  - data/washington-state/elections/2026-11-03-general/counties/king/dossiers/measures/city-of-milton-proposition-no-1.md
sources:
  - id: S1
    tier: 1
    type: votewa
    ref: VoteWA voter-guide measure record 7310 (election 899, county code 27), City of Milton Proposition No. 1 (ballot title, explanatory statement, statement for, committee; no statement against)
    url: https://voter.votewa.gov/elections/measure.ashx?m=7310&e=899&la=en&c=27
    pointer: counties/pierce/raw/measures/pierce-city-of-milton-proposition-no-1/votewa-measure-7310.json.meta.json
    accessed: 2026-10-08
  - id: S2
    tier: 1
    type: government-document
    ref: City of Milton City Council agenda packet, August 3, 2026 (item 7D staff report, July 20, 2026 presentation, draft Resolution No. 26-2005; July 20, 2026 minutes)
    url: https://www.miltonwa.gov/AgendaCenter/ViewFile/Agenda/_08032026-917
    pointer: counties/pierce/raw/measures/pierce-city-of-milton-proposition-no-1/milton-council-agenda-packet-2026-08-03.pdf.url
    accessed: 2026-10-08
  - id: S3
    tier: 1
    type: government-document
    ref: City of Milton City Council agenda packet, August 17, 2026 (minutes of the August 3, 2026 meeting, for approval)
    url: https://www.miltonwa.gov/AgendaCenter/ViewFile/Agenda/_08172026-922
    pointer: counties/pierce/raw/measures/pierce-city-of-milton-proposition-no-1/milton-council-agenda-packet-2026-08-17.pdf.url
    accessed: 2026-10-08
  - id: S4
    tier: 1
    type: government-data
    ref: Washington State Department of Revenue, local sales and use tax rates (quarterly CSV, Quarter 4 2026)
    url: https://dor.wa.gov/taxes-rates/sales-use-tax-rates/lsu-quarterly-tax-rates.csv
    pointer: counties/pierce/raw/measures/pierce-city-of-milton-proposition-no-1/dor-local-sales-use-tax-rates-q4-2026.csv.url
    accessed: 2026-10-08
  - id: S5
    tier: 1
    type: legislative-record
    ref: RCW 82.14.450 (public safety sales and use tax)
    url: https://app.leg.wa.gov/RCW/default.aspx?cite=82.14.450
    pointer: counties/pierce/raw/measures/pierce-city-of-milton-proposition-no-1/rcw-82.14.450.html.url
    accessed: 2026-10-08
  - id: S6
    tier: 1
    type: pdc
    ref: PDC Campaign Finance Summary (data.wa.gov 3h9x-7bvm), 2026 committees query by jurisdiction and name for the Pierce measures
    url: https://data.wa.gov/resource/3h9x-7bvm.json
    pointer: counties/pierce/raw/measures/pierce-city-of-milton-proposition-no-1/pdc-committees-query-2026.json.url
    accessed: 2026-10-08
---

This is the same measure the King package researched as `city-of-milton-proposition-no-1`. This dossier starts from that one, re-fetches its web sources and re-cites them with Pierce raw pointers. The VoteWA record held in the Pierce package is byte-identical to a fresh fetch made on 2026-10-08 [S1].

## What it does

Proposition No. 1 asks City of Milton voters to raise the city's sales and use tax by "one-tenth of one percent (0.001) to provide ongoing funding for public safety purposes permitted under RCW 82.14.450, such as providing adequate law enforcement staffing levels." The increase would take effect in 2027 [S1]. The explanatory statement says the measure "would maintain funding for police services and community safety" and that the city needs "additional funds to supplement existing city general fund revenue which is applied for these purposes" [S1]. Under RCW 82.14.450(7), the city must share 15% of the proceeds with the county [S1].

Resolution No. 26-2005 states its purpose as "to secure additional funding for existing police and public safety services" [S2].

Passage requires a simple majority: RCW 82.14.450 lets a city impose the tax "if the proposition is approved by a majority of persons voting" [S5].

**Which county runs the election.** Milton lies in both King and Pierce counties. The VoteWA record sits under county code 27 (Pierce) and lists the counties as "King, Pierce" [S1]. This research could not read Pierce County's own local voters' pamphlet, because piercecountywa.gov refused automated requests (HTTP 403).

## Cost

- The rate is "one-tenth of one percent (0.001)" [S1], or 10 cents on a $100 taxable purchase. The ballot materials give no per-household estimate [S1].
- The statement in favor calls it "just one-tenth of a penny on every dollar" [S1].
- **Pierce County side:** the current combined rate in "Milton in Pierce County" is 10.2%, so the tax would bring it to 10.3%. The King County part of Milton is at 10.3% and would go to 10.4% [S4]. The +0.1 arithmetic was done for this dossier [S4].
- Revenue: "Based on 2026 sales taxes received to date, it is estimated that a Public Safety Sales Tax would generate about $200,000 annually" [S2]. The staff report does not say whether this is before or after the 15% county share [S2].
- State law exempts motor vehicle sales and the first 36 months of vehicle leases from this tax [S5].

## Fiscal mechanics / What it replaces

- This is a new tax, not a renewal. According to the staff report, "Pierce County and King County do not currently have a Public Safety Sales Tax" [S2].
- The ballot title calls the funding "ongoing" and sets no expiration date [S1].
- Use of funds: under RCW 82.14.450(5), one-third of the money "must be used solely for criminal justice purposes, fire protection purposes, or both" [S5].
- City budget context, from the staff report by the Finance Director and Police Chief [S2]:
  - General Fund revenue has run above budget for several years, mainly because of sales tax and permit fees from large development projects that are now finishing, and the city "does not anticipate continued revenues at these levels."
  - The city expects Sound Transit light rail construction to reduce sales tax from businesses along the SR 99 corridor.
  - 2026 General Fund expenditures total $7,808,874. That includes a $4,400,000 transfer to the Criminal Justice Fund for Police Department operations, 56% of budgeted General Fund spending.
  - "At current budgeted levels of revenues and expenditures, fund balance in the General Fund will fall below the targeted amount of at least 8% of budgeted operating expenditures by the end of 2028."

## Arguments for

From the statement in favor, by committee members Dave Strader and Jacki Strader (YESonMiltonProp1@gmail.com) [S1]:

- "Safety is more important now than ever." The tax "will allow the Milton Police Department to maintain its current budget and high-quality services" [S1].
- "Costs for staffing, training, insurance, technology, equipment, investigations, jail services, prosecution, and municipal court operations continue to rise, while demand for public safety has increased dramatically" [S1].
- A yes vote helps "preserve financial stability, ease pressure on the General Fund, and protect funding for streets, parks, and essential infrastructure" [S1].

## Arguments against

VoteWA shows "No statement was submitted against this issue" [S1]. At the August 3, 2026 council meeting, Mayor White said two people wanted to write the "For" statement "but nobody yet for the 'Against' statement" [S3].

## Campaign committees and money (PDC)

A query of 2026 PDC committee registrations by jurisdiction and name found no committee registered for or against this measure [S6].

## Endorsements

No endorsements were found.

## Context / Coverage

- **Council action.** On August 3, 2026 the council adopted Resolution 26-2005 6 to 0. A second 6-0 motion changed the ballot wording to ".001" instead of ".01%" [S3].
- **Coverage.** No news coverage was found. Search engines were unavailable during this research, so the search was limited to the sources above.

## Axis notes

- `taxes`: a yes vote adds a new, open-ended 0.1% sales and use tax that neither county levies now [S1][S2]. The Pierce-side combined rate would go from 10.2% to 10.3% [S4]. The city estimates about $200,000 a year [S2].
- `spending`: the stated purpose is to maintain existing police services, not expand them [S1][S2].
- `local-control`, `social`, `parental-rights`: not addressed by the measure or the statement [S1].
