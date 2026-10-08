# How the Rubric was derived

Per ADR intent and CONTEXT.md, the Rubric is **derived from this ballot** —
axes were chosen because they demonstrably differentiate the actual choices
on the August 4, 2026 King County primary ballot, not imported from generic
ideology scales.

## Method (traceability chain)

1. Every contest overview (`data/dossiers/*/_contest.md`) and measure file
   was written by a research agent that identified "which issue axes
   genuinely differentiate these candidates," grounded in cited sources.
2. `pipeline/extract_axis_notes.py` mechanically collected all of those
   sections into `data/interim/axis-notes.md` (633 lines).
3. This document + `rubric.json` are a manual synthesis of that file:
   recurring differentiators were clustered, named, and given neutral poles.

## Clustering decisions (and why)

- **taxes** and **spending** kept separate: the notes repeatedly show
  candidates who favor progressive taxation *and* audits/oversight (e.g.,
  Salomon, Scully, Duda's lane vs Mosqueda). One axis would erase the
  within-party signal that dominates this heavily-Democratic ballot.
- **safety** absorbs homelessness/encampment policy AND judicial
  prosecution-vs-defense formation: the dossier evidence treats these as one
  enforcement↔services spectrum (Seattle D5, KCC D8 three-strikes, Muni
  Court bail/diversion). One interview question powers all three.
- **housing** poles are market-supply vs public/tenant-protection, NOT
  pro/anti-housing — every serious candidate claims to want affordability;
  the evidence splits on mechanism.
- **experience** (record vs renewal) is deliberately non-ideological. It is
  the single most recurrent differentiator in the axis notes and the ONLY
  axis available in several same-party races (LD37 P1, LD11 P1).
- **local-control** exists mainly because of the measures (two fire-authority
  annexations, a new park district) and the LD1/LD33 mandate fights.
- **tech** earns a standalone axis this cycle: the notes call AI regulation
  "the race's novel flashpoint" (LD46 P1) and it splits candidates in at
  least five contests in ways uncorrelated with left-right.
- **defense** is federal-only; **judicial** is courts-only. The interview
  only asks about axes present on the voter's ballot, so scoping costs
  nothing.
- Transit was NOT given an axis: it appears (KCC D2 service-vs-electrification,
  RapidRide) but never as a primary divider; it folds into climate/housing.
- Partisan identity was NOT given an axis: party preference is shown as a
  fact on candidate cards; several strong differentiators above already
  encode it where it matters, and county/judicial races are nonpartisan.

## Scoring conventions (for the next pipeline stage)

- Candidates: -2..+2 per applicable axis, with citations to dossier sources
  and a confidence rating. No confident evidence → axis omitted for that
  candidate (never guessed) → shows as Evidence Level gap in the app.
- Judicial candidates are scored ONLY on `judicial`, `safety` (via
  documented bail/diversion/formation evidence), and `experience`;
  partisan-adjacent axes are never inferred for judges (RESEARCH-GUIDE rule).
- Measures: mapped to axes with a direction (a "yes" vote's alignment),
  e.g., Seattle Prop 1 yes = taxes+2/spending+1; annexations = local-control
  −2 direction. Weak mappings omitted (Lean not shown).

## November 3, 2026 general: social split (2026-10-08, issue #4)

Everything above describes the primary rubric, which this file was copied
from. Its paths (`data/dossiers/`, `data/interim/axis-notes.md`) are the
pre-split layout; the same files now live under
`data/washington-state/elections/2026-08-04-primary/`. The primary's rubric,
interview and scores are unchanged.

### Why `social` was split

The general ballot carries two statewide initiatives that both touch the old
`social` axis ("Social issues & schools"):

- **I-1** (IL26-001): parental rights in public schools.
- **I-638** (IL26-638): sex verification for girls' school sports.

On one axis, a voter who supports one and opposes the other averages to
about zero, then gets a confident, wrong lean on both measures. The two
questions are about different things: one is who decides what schools teach
and disclose, the other is gender and sex-based policy. So the axis is split
in two:

- **`social`** is now "Gender, LGBTQ+ and reproductive policy": trans
  participation in sports, gender-affirming care, reproductive rights,
  anti-discrimination law. The curricula and parental-rights language is
  gone from its tension and poles. Pole A (-2) is still the traditional
  pole and pole B (+2) the progressive one.
- **`parental-rights`** is new: "Parents and public schools". Should parents
  have broad notification, record access and opt-out rights over what schools
  teach and provide, or should schools and students have discretion?
  Pole A (-2) "Parental notification and opt-out", pole B (+2) "School and
  student discretion". `applies_to` is `State` and `measures`: state
  legislative contests, school-district and other school-adjacent measures,
  and statewide initiatives. Never judicial contests.

### Why the `social` id was kept

The decision was to keep `social` and add `parental-rights`, not to retire
`social` in favor of two new ids. Reasons:

- Report links and anonymous report records carry axis ids. Old links still
  decode against the rubric, and the archived primary keeps its 14-axis
  rubric with the old `social` meaning.
- Candidates scored on `social` in the primary keep a meaningful sign when
  they are re-scored in their general-election refresh, because the pole
  direction did not flip. There is no bulk rescoring: each candidate's
  `social` score is re-checked against the narrowed definition during that
  refresh, and `parental-rights` is scored then if the dossier supports it.
- The new axis takes the narrower, newly separated concern, so it gets the
  new id.

### Interview changes

- `card-social` was reworded. The old text ("Parents should have more say
  over what public schools teach about gender and race") was a
  parental-rights statement, so it now asks about legal protection for
  transgender people, with school sports as the concrete case. Agree is now
  the progressive pole (`value: 2`).
- `card-parental-rights` was added after it, with agree = parental
  notification and opt-out (`value: -2`) and a care pulse. Agree keeps
  alternating poles across neighbouring statement cards: healthcare -2,
  social +2, parental-rights -2, tech +2, defense -2.
- As with every axis, the card appears only when a contest or measure on the
  voter's ballot is scored on `parental-rights`.

### Intended statewide measure mappings (for research tickets #6, #7)

Measure scoring must still cite the dossier, but research should start from
these mappings:

| Measure | Axes |
|---|---|
| I-645 (IP26-645): repeal the 9.9% tax on household income over $1M and ban state and local income taxes | `taxes`, `local-control` |
| I-1 (IL26-001): parental rights in schools | `parental-rights` |
| I-638 (IL26-638): sex verification for girls' school sports | `social` |

### Judges

Judicial candidates are never scored on `social` or `parental-rights`.
Neither axis lists a judicial category in `applies_to`, and
`pipeline/validate_scoring.py` rejects any judicial axis other than
`judicial`, `safety` and `experience`.
