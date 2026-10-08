---
contest: judge-position-no-1-northeast-electoral-district
office: King County District Court Judge, Northeast Electoral District, Position No. 1
category: DistrictCourt
depth: light
researched_at: 2026-10-08
derived_from:
  - data/washington-state/elections/2026-11-03-general/counties/king/raw/pamphlet/local-edition.pdf.url
  - data/washington-state/elections/2026-11-03-general/counties/king/interim/pdf-text/local-edition.txt
  - data/washington-state/elections/2026-08-04-primary/counties/king/dossiers/judge-position-no-1-northeast-electoral-district/_contest.md
  - data/washington-state/elections/2026-11-03-general/counties/king/raw/candidates/judge-position-no-1-northeast-electoral-district/data-kingcounty-gov-1ddb3073.url
  - data/washington-state/elections/2026-11-03-general/counties/king/raw/candidates/judge-position-no-1-northeast-electoral-district/data-kingcounty-gov-7ace5ca1.url
  - data/washington-state/elections/2026-11-03-general/counties/king/raw/candidates/judge-position-no-1-northeast-electoral-district/kingcounty-gov-4546213c.url
  - data/washington-state/elections/2026-11-03-general/counties/king/raw/candidates/judge-position-no-1-northeast-electoral-district/nwasianweekly-com-63a32577.url
  - data/washington-state/elections/2026-11-03-general/counties/king/raw/candidates/judge-position-no-1-northeast-electoral-district/kcba-org-85c741d1.url
  - data/washington-state/elections/2026-11-03-general/counties/king/raw/candidates/judge-position-no-1-northeast-electoral-district/wwl-org-578d39a2.url
  - data/washington-state/elections/2026-11-03-general/counties/king/raw/candidates/judge-position-no-1-northeast-electoral-district/abaw-org-1ebaece8.url
  - data/washington-state/elections/2026-11-03-general/counties/king/raw/candidates/judge-position-no-1-northeast-electoral-district/abaw-org-22cbc6d7.url
  - data/washington-state/elections/2026-11-03-general/counties/king/raw/candidates/judge-position-no-1-northeast-electoral-district/kcdems-org-5097d7da.url
  - data/washington-state/elections/2026-11-03-general/counties/king/raw/candidates/judge-position-no-1-northeast-electoral-district/data-wa-gov-874079b1.url
  - data/washington-state/elections/2026-11-03-general/counties/king/raw/candidates/judge-position-no-1-northeast-electoral-district/data-wa-gov-06741ba7.url
  - data/washington-state/elections/2026-11-03-general/counties/king/raw/candidates/judge-position-no-1-northeast-electoral-district/trasenforjudge-com-92729392.url
  - data/washington-state/elections/2026-11-03-general/counties/king/raw/candidates/judge-position-no-1-northeast-electoral-district/biancaforjudge-org-1256c2e0.url
  - data/washington-state/elections/2026-11-03-general/counties/king/raw/candidates/judge-position-no-1-northeast-electoral-district/thestranger-com-ec84536c.url
  - data/washington-state/elections/2026-11-03-general/counties/king/raw/candidates/judge-position-no-1-northeast-electoral-district/trasenforjudge-com-735eed83.url
  - data/washington-state/elections/2026-11-03-general/counties/king/raw/candidates/judge-position-no-1-northeast-electoral-district/biancaforjudge-org-1978dd63.url
sources:
  - id: S1
    tier: 1
    type: pamphlet
    ref: local-edition page 23 (District Court duties and salary on page 14)
  - id: S2
    tier: 1
    type: prior-dossier
    ref: data/washington-state/elections/2026-08-04-primary/counties/king/dossiers/judge-position-no-1-northeast-electoral-district/_contest.md
  - id: S3
    tier: 1
    type: election-results
    ref: King County Elections, August 2026 Primary Election final precinct results (data.kingcounty.gov dataset 2ydw-3iau), summed by race
    url: https://data.kingcounty.gov/resource/2ydw-3iau.json?$select=race,countertype,sum(sumofcount)&$where=upper(race)%20like%20'%25NORTHEAST%25'&$group=race,countertype
    accessed: 2026-10-08
  - id: S4
    tier: 1
    type: election-results
    ref: King County Elections, November 2022 General Election final precinct results (data.kingcounty.gov dataset u2qf-rdct), summed by race
    url: https://data.kingcounty.gov/resource/u2qf-rdct.json?$select=race,countertype,sum(sumofcount)&$where=upper(race)%20like%20'%25ELECTORAL%20DISTRICT%25'&$group=race,countertype&$limit=500
    accessed: 2026-10-08
  - id: S5
    tier: 1
    type: official-court-page
    outlet: King County District Court, "Judges - District Court"
    url: https://kingcounty.gov/en/court/district-court/courts-jails-legal-system/court-calendars-locations-operations/judges
    accessed: 2026-10-08
  - id: S6
    tier: 2
    type: news
    outlet: Northwest Asian Weekly, "Tse eyes run for district court judge" (April 2026)
    url: https://nwasianweekly.com/2026/04/tse-eyes-run-for-district-court-judge/
    accessed: 2026-10-08
  - id: S7
    tier: 2
    type: bar-rating
    outlet: King County Bar Association, "Rating of Candidates in 2026 Election" (last updated August 4, 2026)
    url: https://www.kcba.org/?pg=Rating-of-Candidates-in-2026-Election
    accessed: 2026-10-08
  - id: S8
    tier: 2
    type: bar-rating
    outlet: Washington Women Lawyers, Judicial Ratings
    url: https://www.wwl.org/Judicial-ratings
    accessed: 2026-10-08
  - id: S9
    tier: 2
    type: bar-rating
    outlet: Asian Bar Association of Washington, Joint Asian Judicial Evaluation Committee (JAJEC) ratings page
    url: https://www.abaw.org/page-18213
    accessed: 2026-10-08
  - id: S10
    tier: 2
    type: bar-rating
    outlet: JAJEC 2025 ratings spreadsheet (linked from the ABAW JAJEC page)
    url: https://www.abaw.org/resources/JAJEC%202025.xlsx
    accessed: 2026-10-08
  - id: S11
    tier: 2
    type: endorsement
    outlet: King County Democrats 2026 endorsements
    url: https://www.kcdems.org/our-party/e/2026-endorsements/
    accessed: 2026-10-08
  - id: S12
    tier: 1
    type: campaign-finance
    outlet: Washington PDC campaign finance summary (data.wa.gov dataset 3h9x-7bvm), Jan Trasen, record updated 2026-10-05
    url: https://data.wa.gov/resource/3h9x-7bvm.json?filer_id=TRASJ--042
    accessed: 2026-10-08
  - id: S13
    tier: 1
    type: campaign-finance
    outlet: Washington PDC campaign finance summary (data.wa.gov dataset 3h9x-7bvm), Bianca Kwok Tse, record updated 2026-10-05
    url: https://data.wa.gov/resource/3h9x-7bvm.json?filer_id=TSE-B--737
    accessed: 2026-10-08
  - id: S14
    tier: 1
    type: campaign-website
    url: https://trasenforjudge.com/endorsements/
    accessed: 2026-10-08
  - id: S15
    tier: 1
    type: campaign-website
    url: https://biancaforjudge.org/endorsements
    accessed: 2026-10-08
  - id: S16
    tier: 2
    type: endorsement
    outlet: The Stranger, endorsements index (no 2026 general-election endorsements posted at access time)
    url: https://www.thestranger.com/endorsements/
    accessed: 2026-10-08
  - id: S17
    tier: 1
    type: campaign-website
    url: https://trasenforjudge.com/
    accessed: 2026-10-08
  - id: S18
    tier: 1
    type: campaign-website
    url: https://biancaforjudge.org/
    accessed: 2026-10-08
---

## What the office does

A King County District Court judge "hears and decides misdemeanor criminal cases, small claims, traffic cases, and protection orders"; the 2026 salary is $226,096, and the judge is elected by voters in the electoral district to a four-year term [S1]. Position 1 is one of the Northeast Electoral District seats; the court's East Division judges sit in Bellevue, Redmond, and Issaquah [S5].

## Race dynamics

This is an open seat. Judge Marcus Naylor won Position 1 in 2022 with no named opponent [S4], and the court's judges page still lists him, assigned to Issaquah [S5]. Northwest Asian Weekly reported in April 2026 that he is retiring at the end of the year; that article spells his name "Nailor," as did the primary dossier, while the county's results and the court's own page use "Naylor" [S2][S4][S5][S6]. No source other than that article was found for the retirement itself.

Three candidates ran in the August 4 primary. Jan Trasen received 59,661 votes (47.5% of votes cast for candidates and write-ins), Bianca Tse 35,074 (27.9%), and Josh Schaer 29,752 (23.7%), with 1,015 write-ins; Schaer was eliminated [S3]. Both finalists sit as judges pro tem in King County District Court [S1].

Trasen spent 26 years as a public defender and appellate attorney and is now a full-time administrative law judge [S1]. Tse spent 16 years as a King County deputy prosecutor and then ran a private civil practice [S2][S6]. The two general-election statements now address each other indirectly. Trasen calls herself "the only candidate with full-time judicial experience" and "the only candidate" with "Exceptionally Well Qualified" ratings from six local bar associations. Tse writes that the position "requires different skills than being an administrative law judge," that "judges should be non-partisan," and that she is "endorsed by people who know me by my good work, not by party affiliation" [S1].

Bar ratings that could be checked independently:

| Rater | Trasen | Tse |
|---|---|---|
| KCBA | Exceptionally Well Qualified (June 11, 2025) | Qualified (April 1, 2025) |
| Washington Women Lawyers | Exceptionally Well Qualified (2025) | Qualified (2026) |
| JAJEC | EWQ (2025) | EWQ (2025) |

Sources: KCBA [S7], WWL [S8], JAJEC [S9][S10].

Each campaign also lists ratings that were not confirmed on a rater's page. Trasen lists QLaw, Latina/o Bar, and Cardozo Society ratings of EWQ and a Loren Miller Bar Association rating of "Well Qualified." Tse lists Latino Bar and Loren Miller ratings of EWQ [S14][S15].

King County Democrats endorsed Trasen [S11]. The National Women's Political Caucus and Sen. Manka Dhingra appear in both candidates' endorsement lists [S1]. Tse has raised more money: about $60,400 to Trasen's $39,000, according to PDC summaries updated October 5, 2026 [S12][S13]. The Stranger had not posted 2026 general-election endorsements at access time, and its primary endorsements did not cover this race [S16].

## What genuinely differentiates the candidates

- **Professional formation.** Trasen's career is in public defense and criminal and dependency appeals. Tse's is in prosecution, followed by private civil practice [S1][S2][S6]. This is the main substantive contrast for a misdemeanor court.
- **Type of judicial experience.** Trasen judges full time as an administrative law judge, plus pro tem work. Tse's judging is pro tem service in this court and several Eastside municipal courts since 2021, which she presents as more relevant to a high-volume trial docket [S1][S2][S18].
- **Stated approach to treatment and recidivism.** Trasen's campaign names mental-health and substance-use treatment options to reduce recidivism [S17]. Tse's campaign lists "Safety" (community accountability, "holistic approaches") among her values without naming specific programs [S18]. Neither has a documented bail or therapeutic-court record.
- **Independent bar ratings.** KCBA and WWL rate Trasen one or two levels higher than Tse; JAJEC rates both EWQ [S7][S8][S10].

## Not differentiating

Both candidates promise fairness and respect for everyone in the courtroom, and both claim readiness from current pro tem service in this court [S1]. Party endorsements (King County and LD Democrats for Trasen) are organizational support in a nonpartisan race, not evidence of judicial philosophy [S1][S11]. Neither candidate has published rulings that can be compared.
