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
