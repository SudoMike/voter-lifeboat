---
contest: wahkiakum-public-utility-district-no-1-of-wahkiakum-county-commissioner-1
office: Public Utility District No. 1 of Wahkiakum County, Commissioner #1
district: Wahkiakum County
category: PublicUtility
depth: light
researched_at: 2026-10-08
candidates:
  - gene-healy
derived_from:
  - data/washington-state/elections/2026-11-03-general/counties/wahkiakum/interim/contests.json
sources:
  - id: S1
    tier: 1
    type: official-election
    outlet: Wahkiakum County Elections, General Election Sample Ballot, November 3, 2026
    url: https://www.co.wahkiakum.wa.us/DocumentCenter/View/3637
    pointer: counties/wahkiakum/raw/wahkiakum/sample-ballot.pdf.url
    accessed: 2026-10-08
  - id: S2
    tier: 1
    type: official-election-filing
    outlet: VoteWA candidate list, GENERAL 2026, Wahkiakum County
    url: https://voter.votewa.gov/candidatelist.aspx?c=35&e=899
    pointer: counties/wahkiakum/raw/votewa/candidate-list.csv.url
    accessed: 2026-10-08
  - id: S3
    tier: 1
    type: official-election
    outlet: Washington Secretary of State, November 3, 2020 general election results, Wahkiakum County
    url: https://results.vote.wa.gov/results/20201103/wahkiakum/
    pointer: counties/wahkiakum/raw/sos/results-20201103-wahkiakum.html.url
    accessed: 2026-10-08
  - id: S4
    tier: 1
    type: official-election
    outlet: Washington Secretary of State, November 8, 2022 general election precinct results, Wahkiakum County
    url: https://results.vote.wa.gov/results/20221108/export/20221108_wahkiakumprecincts.csv
    pointer: counties/wahkiakum/raw/sos/precincts-20221108-wahkiakum.csv.url
    accessed: 2026-10-08
  - id: S5
    tier: 1
    type: official-election
    outlet: Washington Secretary of State, November 5, 2024 general election precinct results, Wahkiakum County
    url: https://results.vote.wa.gov/results/20241105/export/20241105_wahkiakumprecincts.csv
    pointer: counties/wahkiakum/raw/sos/precincts-20241105-wahkiakum.csv.url
    accessed: 2026-10-08
  - id: S6
    tier: 1
    type: official-record
    outlet: "RCW 54.12.010, PUD commissioners: number, districts, terms"
    url: https://app.leg.wa.gov/RCW/default.aspx?cite=54.12.010
    pointer: counties/wahkiakum/raw/law/rcw-54.12.010.html.url
    accessed: 2026-10-08
  - id: S7
    tier: 1
    type: official-gis
    outlet: WA Department of Revenue, PUD2025 taxing-district layer (WADOR_PropertyTax MapServer layer 17), Wahkiakum features
    url: https://webgis.dor.wa.gov/arcgis/rest/services/Programs/WADOR_PropertyTax/MapServer/17/query?where=COUNTYNAME%3D%27WAHKIAKUM%27&outFields=COUNTYNAME,DISTATTRIB,Shape_Area&returnGeometry=false&f=json
    pointer: counties/wahkiakum/COMPLETENESS.md (District scoping; live query, not cached)
    accessed: 2026-10-08
  - id: S8
    tier: 1
    type: pdc
    outlet: PDC campaign finance summary (data.wa.gov 3h9x-7bvm), 2026 Wahkiakum County candidates
    url: https://data.wa.gov/resource/3h9x-7bvm.json?election_year=2026&jurisdiction_county=WAHKIAKUM&$limit=200
    pointer: counties/wahkiakum/raw/pdc/pdc-candidates-2026.json.url
    accessed: 2026-10-08
---

## What the office does
The PUD's powers are exercised through its three-member commission [S6]. Public Utility District No. 1 of Wahkiakum County covers the whole county: WA DOR's 2025 PUD layer has a single Wahkiakum polygon, district 1 [S7]. Each is nominated by the voters of a commissioner district and elected by all PUD voters [S6]; the 2022 and 2024 PUD commissioner races were on every precinct's general ballot [S4][S5]. Six-year term [S1].

## Race dynamics
Uncontested. Commissioner Gene Healy, elected unopposed in 2020, is the only candidate [S1][S3].

## Differentiating issue axes
None: uncontested, shipped as information only.
