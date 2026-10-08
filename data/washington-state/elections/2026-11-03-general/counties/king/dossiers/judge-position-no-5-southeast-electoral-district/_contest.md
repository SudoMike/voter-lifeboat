---
contest: judge-position-no-5-southeast-electoral-district
office: King County District Court Judge, Southeast Electoral District, Position No. 5
category: DistrictCourt
depth: light
researched_at: 2026-10-08
derived_from:
  - data/washington-state/elections/2026-11-03-general/counties/king/raw/pamphlet/local-edition.pdf.url
  - data/washington-state/elections/2026-11-03-general/counties/king/interim/pdf-text/local-edition.txt
  - data/washington-state/elections/2026-11-03-general/counties/king/interim/contests.json
  - data/washington-state/elections/2026-11-03-general/counties/king/raw/candidates/judge-position-no-5-southeast-electoral-district/data-kingcounty-gov-7ace5ca1.url
  - data/washington-state/elections/2026-11-03-general/counties/king/raw/candidates/judge-position-no-5-southeast-electoral-district/kingcounty-gov-4546213c.url
  - data/washington-state/elections/2026-11-03-general/counties/king/raw/candidates/judge-position-no-5-southeast-electoral-district/kcba-org-85c741d1.url
  - data/washington-state/elections/2026-11-03-general/counties/king/raw/candidates/judge-position-no-5-southeast-electoral-district/wwl-org-578d39a2.url
  - data/washington-state/elections/2026-11-03-general/counties/king/raw/candidates/judge-position-no-5-southeast-electoral-district/abaw-org-1ebaece8.url
  - data/washington-state/elections/2026-11-03-general/counties/king/raw/candidates/judge-position-no-5-southeast-electoral-district/abaw-org-22cbc6d7.url
  - data/washington-state/elections/2026-11-03-general/counties/king/raw/candidates/judge-position-no-5-southeast-electoral-district/kcdems-org-5097d7da.url
  - data/washington-state/elections/2026-11-03-general/counties/king/raw/candidates/judge-position-no-5-southeast-electoral-district/data-wa-gov-9d3a412d.url
  - data/washington-state/elections/2026-11-03-general/counties/king/raw/candidates/judge-position-no-5-southeast-electoral-district/data-wa-gov-28528ae6.url
  - data/washington-state/elections/2026-11-03-general/counties/king/raw/candidates/judge-position-no-5-southeast-electoral-district/heatherbarkerforjudge-com-e09c8b23.url
  - data/washington-state/elections/2026-11-03-general/counties/king/raw/candidates/judge-position-no-5-southeast-electoral-district/josh4kingcounty-com-b94e6549.url
  - data/washington-state/elections/2026-11-03-general/counties/king/raw/candidates/judge-position-no-5-southeast-electoral-district/thestranger-com-ec84536c.url
sources:
  - id: S1
    tier: 1
    type: pamphlet
    ref: local-edition page 30 (District Court duties and salary on page 14)
  - id: S2
    tier: 1
    type: election-results
    ref: King County Elections, November 2022 General Election final precinct results (data.kingcounty.gov dataset u2qf-rdct), summed by race
    url: https://data.kingcounty.gov/resource/u2qf-rdct.json?$select=race,countertype,sum(sumofcount)&$where=upper(race)%20like%20'%25ELECTORAL%20DISTRICT%25'&$group=race,countertype&$limit=500
    accessed: 2026-10-08
  - id: S3
    tier: 1
    type: official-court-page
    outlet: King County District Court, "Judges - District Court"
    url: https://kingcounty.gov/en/court/district-court/courts-jails-legal-system/court-calendars-locations-operations/judges
    accessed: 2026-10-08
  - id: S4
    tier: 2
    type: bar-rating
    outlet: King County Bar Association, "Rating of Candidates in 2026 Election" (last updated August 4, 2026)
    url: https://www.kcba.org/?pg=Rating-of-Candidates-in-2026-Election
    accessed: 2026-10-08
  - id: S5
    tier: 2
    type: bar-rating
    outlet: Washington Women Lawyers, Judicial Ratings
    url: https://www.wwl.org/Judicial-ratings
    accessed: 2026-10-08
  - id: S6
    tier: 2
    type: bar-rating
    outlet: Asian Bar Association of Washington, Joint Asian Judicial Evaluation Committee (JAJEC) ratings page
    url: https://www.abaw.org/page-18213
    accessed: 2026-10-08
  - id: S7
    tier: 2
    type: bar-rating
    outlet: JAJEC 2025 ratings spreadsheet (linked from the ABAW JAJEC page)
    url: https://www.abaw.org/resources/JAJEC%202025.xlsx
    accessed: 2026-10-08
  - id: S8
    tier: 2
    type: endorsement
    outlet: King County Democrats 2026 endorsements
    url: https://www.kcdems.org/our-party/e/2026-endorsements/
    accessed: 2026-10-08
  - id: S9
    tier: 1
    type: campaign-finance
    outlet: Washington PDC campaign finance summary (data.wa.gov dataset 3h9x-7bvm), Heather M. Barker, record updated 2026-09-28
    url: https://data.wa.gov/resource/3h9x-7bvm.json?filer_id=BARKH--482
    accessed: 2026-10-08
  - id: S10
    tier: 1
    type: campaign-finance
    outlet: Washington PDC campaign finance summary (data.wa.gov dataset 3h9x-7bvm), filer HARRJ--638 (2026 and 2022 candidacies), 2026 record updated 2026-09-22
    url: https://data.wa.gov/resource/3h9x-7bvm.json?filer_id=HARRJ--638
    accessed: 2026-10-08
  - id: S11
    tier: 1
    type: campaign-website
    url: https://heatherbarkerforjudge.com/endorsements/
    accessed: 2026-10-08
  - id: S12
    tier: 1
    type: campaign-website
    outlet: Joshua C. Harris campaign site listed in the pamphlet and on the KCE candidate list; returned HTTP 404 (Wix "ConnectYourDomain" error page) at access time
    url: https://josh4kingcounty.com/
    accessed: 2026-10-08
  - id: S13
    tier: 2
    type: endorsement
    outlet: The Stranger, endorsements index (no 2026 general-election endorsements posted at access time)
    url: https://www.thestranger.com/endorsements/
    accessed: 2026-10-08
---

## What the office does

A King County District Court judge "hears and decides misdemeanor criminal cases, small claims, traffic cases, and protection orders"; the 2026 salary is $226,096, and the judge is elected by voters in the electoral district to a four-year term [S1]. Both candidates describe Southeast King County as home: Barker was raised in Kent and lives in Renton, and Harris lives in Kent [S1]. The court's South Division judges sit at the Maleng Regional Justice Center, in Burien, and in Auburn [S3].

## Race dynamics

No incumbent is on the ballot. Judge Virginia M. Amato won Position 5 in November 2022 with no named opponent [S2]. The court's judges page still lists her, assigned to the Maleng Regional Justice Center [S3]. She is not a 2026 candidate for the seat [S1]. No source found during research explained why she is not running (retirement or otherwise). Only two candidates filed, so the race skipped the August primary [S1][S10].

The two candidates have different paths to the bench:

- **Heather M. Barker** has been a judge pro tem in King County District Court since 2022, including on Mental Health and Veterans Court calendars. She has owned a civil-litigation firm for over a decade [S1].
  - Endorsements: King County Democrats (independently confirmed) [S8]; the King County Police Officers Guild, IAM 751, ATU 587, seven LD Democratic organizations, and "35+ local judges," per her statement [S1].
  - She has raised about $14,400 [S9].
- **Joshua C. Harris** is an attorney, Army National Guard veteran, and founder of a security company. His practice covers employment, business, tax, and administrative law. He says he has completed pro tem judicial training but does not say he has served as a judge pro tem [S1].
  - His pamphlet statement lists no endorsements and no bar ratings [S1].
  - He registered with the PDC under mini reporting, with no reports filed [S10].
  - His campaign website did not load at access time [S12].
  - PDC records show the same filer ID ran for Pierce County Council in 2022 with a Republican party preference [S10]. This is recorded as a fact about a prior candidacy, not as evidence of judicial philosophy.

Bar ratings: KCBA's 2026 ratings page lists only contested primary races and does not include this contest. Barker's claimed KCBA "Exceptionally Well Qualified" rating therefore could not be confirmed there [S4]. The only rating confirmed for either candidate is JAJEC's "Q" (Qualified) for Barker on its 2025 list [S6][S7]. Washington Women Lawyers lists neither candidate [S5]. The Stranger had not posted 2026 general-election endorsements at access time [S13]. No local news coverage of this race was found.

## What genuinely differentiates the candidates

- **Judicial experience.** Barker reports about four years of pro tem service in this court, including Mental Health and Veterans Court. Harris reports pro tem training but no bench service [S1].
- **Professional formation.** Neither candidate reports a career as a prosecutor or public defender. Barker's practice is civil litigation and property law. Harris's is employment, business, tax, and administrative law, plus representation of indigent clients through a "Federal Low Income Tax Clinic", and military service [S1].
- **Stated approach to safety.** Barker says she balances "accountability with rehabilitation" and presides over therapeutic calendars [S1]. Harris emphasizes listening, dignity, and a courtroom "defined by respect—not intimidation" [S1]. Neither has a documented bail record.
- **Evidence depth.** Barker has a campaign site, a confirmed party endorsement, and one confirmed bar rating. Harris has only his pamphlet statement and PDC registration records [S1][S7][S8][S10][S11][S12].

## Not differentiating

Both candidates promise fair, respectful treatment of everyone in court [S1]. Barker's Democratic endorsements and Harris's 2022 Republican-preference candidacy are recorded as facts only. Neither indicates how either would rule in a nonpartisan misdemeanor court [S1][S8][S10].
