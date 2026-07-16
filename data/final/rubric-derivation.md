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
