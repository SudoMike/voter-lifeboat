# Voter Lifeboat

Voter Lifeboat is an interactive public voter guide. It interviews a voter
about their values, identifies the contests covered for their address, and
shows how candidates and measures align with those values.

## Language

**Election Scope**:
The geographic and legal boundary of a guide's election dataset, such as
Washington State or a supported county within Washington State.
_Avoid_: Site scope, region

**Active Election**:
The election dataset currently served by an Election Scope's stable public
route.
_Avoid_: Current data, selected election

**Archived Election**:
A past election dataset that stays explorable, read-only, at its own route
after a later election became the Active Election. It keeps the Rubric and
data version its reports were made with and records no new Anonymous Report
Records.
_Avoid_: Old election, past data, inactive election

**Election Index**:
The list of every election an Election Scope has a dataset for, naming which
one is the Active Election and which are Archived Elections.
_Avoid_: Election list, manifest

**Supported County**:
A county whose local contests, measures, pamphlet material, district scoping,
and scored dossiers are available in Voter Lifeboat.
_Avoid_: Active county, enabled county

**Unsupported County**:
A Washington county that Voter Lifeboat can recognize from an address, but
whose local ballot contents are not yet covered.
_Avoid_: Missing county, unavailable county

**Coverage Status**:
The guide's level of ballot coverage for a voter after address lookup: full
county coverage, partial county coverage, or statewide-only coverage.
_Avoid_: Availability, support state

**Full County Coverage**:
A Coverage Status where the voter is in a Supported County and Voter Lifeboat
resolved the district data needed to identify the local Covered Ballot.
_Avoid_: Full support

**Partial County Coverage**:
A Coverage Status where the voter is in a Supported County, but one or more
local district lookups failed or are incomplete, so the Covered Ballot may omit
local contests.
_Avoid_: Degraded support, incomplete support

**Statewide-Only Guide**:
A partial guide for a Washington voter in an Unsupported County, limited to
the complete set of statewide Contests for the Active Election.
_Avoid_: Generic guide, fallback ballot

**Statewide Contest**:
A Contest whose electorate is all Washington voters in the Active Election,
regardless of which official publication carries it.
_Avoid_: State guide contest, all-county contest

**Countywide Contest**:
A Contest whose electorate is all voters in one county, but not all Washington
voters.
_Avoid_: All contest, local statewide

**Contest**:
A single item a voter decides: either a candidate race or a Measure.
_Avoid_: Race, item

**Measure**:
A yes/no Contest such as a levy or proposition.
_Avoid_: Ballot measure, proposition

**Candidate**:
A person running in a candidate Contest.
_Avoid_: Office seeker

**District**:
A geographic unit that determines which Contests appear on a voter's Ballot,
such as a congressional, legislative, county council, city, school, or fire
district.
_Avoid_: Region, area

**District Adapter**:
A county-specific resolver that maps a geocoded address to the District values
needed to identify the local Covered Ballot in a Supported County.
_Avoid_: GIS integration, district lookup

**Ballot**:
The voter-specific set of Contests assigned to a residential address. There is
no single Washington Ballot and no single county Ballot.
_Avoid_: Pamphlet, guide

**Pamphlet**:
An official voter information publication for an Election Scope. It may contain
more Contests than any one voter will receive on their Ballot.
_Avoid_: Ballot, booklet

**Dossier**:
The compiled evidence about one Candidate or Measure: pamphlet statement plus
public record such as votes, endorsements, news, or prior statements.
_Avoid_: Research file, candidate profile

**Candidate Photo**:
A verified link to a headshot of a Candidate on a pamphlet, government, or
campaign page, carried in the Dossier. It is an identity aid and never
evidence of qualification.
_Avoid_: Portrait, headshot, thumbnail, image

**Initials Portrait**:
The stand-in shown wherever a Candidate Photo would appear but none exists,
so a Candidate is never represented by a gap.
_Avoid_: Placeholder, fallback avatar

**Issue Axis**:
One dimension of the scoring rubric, such as housing density or taxation.
Candidates are scored on axes; voters are interviewed on axes.
_Avoid_: Topic, value

**Rubric**:
The fixed set of Issue Axes used to score Candidates and Measures and to
interpret a voter's answers.
_Avoid_: Scoring system, questionnaire model

**Package-Aware Rubric**:
A Rubric assembled from the Issue Axes required by the state package and the
Supported County packages relevant to a Covered Ballot.
_Avoid_: Global rubric, county rubric

**Values Profile**:
A voter's positions and priority weights across the Rubric, produced by the
Interview.
_Avoid_: User profile, preferences

**Interview**:
The questionnaire a voter completes to produce their Values Profile.
_Avoid_: Survey, quiz

**Covered Ballot**:
The subset of a voter's Ballot that Voter Lifeboat can currently explain and
score. In a Statewide-Only Guide, the Covered Ballot excludes local contests.
_Avoid_: Displayed ballot, supported ballot

**Alignment Score**:
The computed similarity between a Values Profile and a Candidate's or Measure's
Rubric scores.
_Avoid_: Recommendation, ranking

**Evidence Level**:
How much sourcing backs a Candidate's or Measure's scores.
_Avoid_: Confidence, certainty

**Ballot Brief**:
The copy-to-clipboard packet containing the voter's Values Profile, covered
Ballot Contests, alignment results, and dossier summaries for use in the
voter's own AI chat.
_Avoid_: Chat export, AI prompt

**Orientation Mode**:
The Ballot Brief's initial chatbot behavior: welcome the voter, summarize the
available data and coverage limits, and offer to generate a report without
generating it until the voter asks.
_Avoid_: Intro mode, pre-report mode

**Research Lens**:
One of the named angles the Ballot Brief asks the voter's chatbot to offer in
Orientation Mode before building the AI Report: no extremists, follow the
money, real track record, who can win.
_Avoid_: Concern chip, suggestion, filter

**Statement Card**:
The Interview's core unit: a short, neutrally worded position statement the
voter agrees with, disagrees with, or skips.
_Avoid_: Question card, prompt

**Trade-off Scenario**:
An Interview question posing a concrete forced choice between two public goods.
_Avoid_: Scenario, dilemma

**Lean**:
The alignment read for a Measure: leans yes, leans no, or genuinely split.
_Avoid_: Endorsement, recommendation

**Source Tier**:
The trust class of a dossier source. Tier 1 includes pamphlet statements,
candidate-owned sources, filings, and voting records; Tier 2 includes
endorsements and established news.
_Avoid_: Source quality, citation class

**Report**:
The page showing one voter's Covered Ballot ranked against their Values
Profile, headlined "Your ballot, charted". It is what a Report Link opens and
what an Anonymous Report Record records.
_Avoid_: Results page, results screen, final report

**Ballot Section**:
One of the groups a Report divides a Covered Ballot into, in the order a
Washington ballot lists them: Measures, Federal, State, Courts, County, Local.
Each Contest belongs to exactly one, derived from its pipeline category.
_Avoid_: Card group, bucket, level

**Pick Row**:
One line on a Ballot Section card, one per contested Contest: the Contest
heading, the Candidate Photo, the best-match name and the score dial, or the
Lean for a Measure. Tapping it opens the Contest's full card in place. A
section's uncontested Contests share one muted row at the foot of the card.
_Avoid_: Summary row, collapsed card, list item

**AI Report**:
The HTML page a voter's own chatbot builds from the Ballot Brief, outside
Voter Lifeboat.
_Avoid_: HTML report, chatbot report, final report

**Report Link**:
The URL of a finished report, containing the voter's Values Profile and
districts but not their address.
_Avoid_: Share link, saved report

**Anonymous Report Record**:
An address-free record of a completed report used for aggregate analysis. It
may include election, Coverage Status, county, Districts, and Values Profile.
_Avoid_: Submission, response
