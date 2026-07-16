# Context: King County Voter Guide

Interactive public voter guide for the King County August 4, 2026 primary and
special election. Interviews a voter about their values, then shows how every
candidate and measure on *their* ballot aligns with those values.

## Glossary

- **Contest** — a single item a voter decides: either a race (people) or a
  measure (yes/no). The pamphlet is a set of contests.
- **Measure** — a yes/no contest (levy, proposition).
- **Candidate** — a person running in a race.
- **District** — a geographic unit (congressional, legislative, county council,
  city, school, fire, water…) that determines which contests appear on a
  voter's ballot.
- **Ballot** — the voter-specific set of contests, derived from the districts
  containing the voter's address. There is no single "King County ballot."
- **Dossier** — the full compiled evidence about one candidate or measure:
  pamphlet statement plus whatever public record we source (votes, endorsements,
  news, prior statements).
- **Issue Axis** — one dimension of the scoring rubric (e.g., housing density,
  taxation). Candidates are scored on axes; voters are interviewed on axes.
- **Rubric** — the fixed set of issue axes. Frozen before launch.
- **Values Profile** — a voter's positions and priority weights across the
  rubric, produced by the Interview.
- **Interview** — the questionnaire a voter completes to produce their Values
  Profile. Must feel engaging, not arduous.
- **Alignment Score** — the computed similarity between a Values Profile and a
  candidate's rubric scores. Deterministic, client-side math.
- **Evidence Level** — how much sourcing backs a candidate's rubric scores.
  Shown honestly to the voter; hyperlocal candidates may be
  pamphlet-statement-only.
- **Ballot Brief** *(provisional name)* — the copy-to-clipboard packet: the
  voter's Values Profile, their ballot's contests, alignment results, and
  dossier summaries — formatted so the voter can paste it into their own AI
  chat to discuss further.
- **Statement Card** — the interview's core unit: a short, neutrally-worded
  position statement the voter agrees with, disagrees with, or skips;
  strong reactions trigger a "how much do you care?" weight.
- **Trade-off Scenario** — an interview question posing a concrete forced
  choice between two goods (e.g., where a budget surplus goes). Highest
  signal, used sparingly.
- **Lean** — the alignment read for a Measure: leans yes, leans no, or
  genuinely split, derived from the Values Profile via the measure's mapped
  axes. Never shown when the axis mapping is weak.
- **Source Tier** — the trust class of a dossier source. Tier 1: pamphlet
  statement, candidate's own site/filings, official voting records. Tier 2:
  endorsements, established-outlet news. Excluded: social media, opposition
  sites, blogs.
- **Report Link** — the URL of a finished report: the voter's Values Profile
  and districts encoded in the hash fragment, so the identical report can be
  reopened or shared. Contains no address; readable by anyone holding it;
  never transmitted to any server.
