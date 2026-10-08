---
contest: judge-position-no-5-southwest-electoral-district
office: King County District Court, Southwest Electoral District, Judge Position No. 5
category: DistrictCourt
depth: light
researched_at: 2026-10-08
derived_from:
  - data/washington-state/elections/2026-11-03-general/counties/king/raw/pamphlet/local-edition.pdf.url
  - data/washington-state/elections/2026-11-03-general/counties/king/interim/pdf-text/local-edition.txt
  - data/washington-state/elections/2026-11-03-general/counties/king/raw/candidates/judge-position-no-5-southwest-electoral-district/data-kingcounty-gov-fa8c883c.url
  - data/washington-state/elections/2026-11-03-general/counties/king/raw/candidates/judge-position-no-5-southwest-electoral-district/kingcounty-gov-4546213c.url
  - data/washington-state/elections/2026-08-04-primary/counties/king/raw/kce/2026-candidates.csv
  - data/washington-state/elections/2026-11-03-general/counties/king/raw/candidates/judge-position-no-5-southwest-electoral-district/reneewallsforjudge-com-d74c294a.url
  - data/washington-state/elections/2026-11-03-general/counties/king/raw/candidates/judge-position-no-5-southwest-electoral-district/reneewallsforjudge-com-cd91775b.url
  - data/washington-state/elections/2026-11-03-general/counties/king/raw/candidates/judge-position-no-5-southwest-electoral-district/merfeldforjudge-com-fc205129.url
  - data/washington-state/elections/2026-11-03-general/counties/king/raw/candidates/judge-position-no-5-southwest-electoral-district/merfeldforjudge-com-f0e4100c.url
  - data/washington-state/elections/2026-11-03-general/counties/king/raw/candidates/judge-position-no-5-southwest-electoral-district/34dems-org-7e2ca42d.url
  - data/washington-state/elections/2026-11-03-general/counties/king/raw/candidates/judge-position-no-5-southwest-electoral-district/kcdems-org-0cc67429.url
  - data/washington-state/elections/2026-11-03-general/counties/king/raw/candidates/judge-position-no-5-southwest-electoral-district/kcba-org-85c741d1.url
  - data/washington-state/elections/2026-11-03-general/counties/king/raw/candidates/judge-position-no-5-southwest-electoral-district/data-wa-gov-4e274be1.url
  - data/washington-state/elections/2026-11-03-general/counties/king/raw/candidates/judge-position-no-5-southwest-electoral-district/data-wa-gov-aff2c06c.url
sources:
  - id: S1
    tier: 1
    type: pamphlet
    ref: local-edition page 35
  - id: S2
    tier: 1
    type: pamphlet
    ref: local-edition page 14 (duties of offices)
  - id: S3
    tier: 1
    type: election-results
    outlet: King County Elections, November 2022 General Election Final Precinct Results (data.kingcounty.gov dataset u2qf-rdct)
    url: https://data.kingcounty.gov/resource/u2qf-rdct.json?$select=race,countertype,sum(sumofcount)&$where=starts_with(race,'Southwest%20Electoral')&$group=race,countertype&$order=race
    accessed: 2026-10-08
  - id: S4
    tier: 1
    type: official
    outlet: King County District Court judges roster
    url: https://kingcounty.gov/en/court/district-court/courts-jails-legal-system/court-calendars-locations-operations/judges
    accessed: 2026-10-08
  - id: S5
    tier: 1
    type: official
    outlet: King County Elections 2026 candidate filing list (filing week May 2026)
    ref: data/washington-state/elections/2026-08-04-primary/counties/king/raw/kce/2026-candidates.csv
  - id: S6
    tier: 1
    type: campaign-website
    url: https://www.reneewallsforjudge.com/about
    accessed: 2026-10-08
  - id: S7
    tier: 1
    type: campaign-website
    url: https://www.reneewallsforjudge.com/endorsements
    accessed: 2026-10-08
  - id: S8
    tier: 1
    type: campaign-website
    url: https://merfeldforjudge.com/about/
    accessed: 2026-10-08
  - id: S9
    tier: 1
    type: campaign-website
    url: https://merfeldforjudge.com/values/
    accessed: 2026-10-08
  - id: S10
    tier: 2
    type: endorsement
    outlet: 34th District Democrats, 2026 endorsements
    url: https://34dems.org/2026-endorsements/
    accessed: 2026-10-08
  - id: S11
    tier: 2
    type: endorsement
    outlet: King County Democrats, 2026 endorsements
    url: https://www.kcdems.org/2026-endorsements/
    accessed: 2026-10-08
  - id: S12
    tier: 2
    type: bar-rating
    outlet: King County Bar Association
    url: https://www.kcba.org/?pg=Rating-of-Candidates-in-2026-Election
    accessed: 2026-10-08
  - id: S13
    tier: 1
    type: campaign-finance
    outlet: Washington State Public Disclosure Commission, campaign finance summary (data.wa.gov 3h9x-7bvm)
    url: https://data.wa.gov/resource/3h9x-7bvm.json?election_year=2026&$where=upper(filer_name)%20like%20'%25WALLS%25'
    accessed: 2026-10-08
  - id: S14
    tier: 1
    type: campaign-finance
    outlet: Washington State Public Disclosure Commission, campaign finance summary (data.wa.gov 3h9x-7bvm)
    url: https://data.wa.gov/resource/3h9x-7bvm.json?election_year=2026&$where=upper(filer_name)%20like%20'%25MERFELD%25'
    accessed: 2026-10-08
---

## What the office does

A King County District Court judge hears misdemeanor criminal cases, small claims, traffic cases and protection orders. The 2026 salary is $226,096, and judges are elected by the voters of their electoral district to four-year terms [S2].

## Race dynamics

- **Open seat.** Elizabeth D. Stephenson was elected to Southwest Position 5 unopposed in November 2022 [S3]. The District Court's judges page now lists "Judge Elizabeth D. Stephenson (retired)" and does not include her on the South Division roster [S4]. Neither 2026 candidate is a sitting judge [S1]. No source reviewed says when she retired or whether an interim appointee holds the seat.
- **No primary.** Only two candidates filed [S5], so the race appears for the first time on the general ballot.
- **The candidates.** Renee Walls is a municipal prosecutor of 26 years (for Algona, Burien, Federal Way and Tukwila, per her site) and a judge pro tem of 17 years [S1][S6]. Noel Merfeld is a child dependency attorney who was previously a prosecutor in Okanogan County and a public defender in Okanogan and Snohomish counties [S1][S8].
- **Endorsements.** Walls lists most of the King County District Court bench, including the Chief Presiding Judge, plus three Supreme Court justices and four state senators [S7]. The 34th District Democrats endorsed Walls [S10]. The King County Democrats made no endorsement in this race [S11]. Both candidates claim the 33rd LD Democrats, and both list SeaTac Mayor Mohamed Egal [S1][S7].
- **Money.** Fundraising is about even and mostly self-funded. The PDC summaries show $30,838 raised for Walls and $30,274 for Merfeld [S13][S14].
- **Bar ratings.** No King County Bar Association rating exists for this general-only race [S12].

## What genuinely differentiates the candidates

- **Experience (`experience`).** Walls has substantially longer practice and 17 years as a pro tem judicial officer (self-reported) [S1][S6]. Merfeld describes no judicial or pro tem service [S1][S8].
- **Professional formation (`safety`).** Walls's formation is municipal prosecution [S6]. Merfeld's spans prosecution, public defense and dependency [S8]. He explicitly backs expanding therapeutic courts while saying he will impose jail when needed to protect the public [S9]. Walls has not published bail, diversion or sentencing positions beyond a youth-diversion community board role [S6].
- **Judicial approach (`judicial`).** Merfeld publishes a detailed community-engagement and access-to-justice platform, including court facilitators for self-represented litigants [S9]. Walls's materials stress experience, temperament and integrity rather than specific approaches [S1][S6].

## Not differentiating

- Neither candidate has a bar rating on the pages checked [S12].
- Both rely mainly on their own money [S13][S14].
