# Dossier research guide

How every dossier in this directory was produced. Research agents follow this
spec exactly.

## Source policy (see CONTEXT.md "Source Tier")

- **Tier 1 (always use):** the candidate's official pamphlet statement
  (already archived: `data/interim/pamphlet-text/<edition>/page-NNN.txt`),
  the candidate's own campaign website, PDC campaign-finance filings
  (pdc.wa.gov), official voting/legislative records (leg.wa.gov,
  congress.gov, county/city council records, court opinions for judges).
- **Tier 2 (use and cite):** endorsement lists (newspapers, unions, parties,
  advocacy orgs), news coverage from established outlets (Seattle Times,
  Seattle P-I, Crosscut/Cascade PBS, KUOW, KING5, Publicola, The Stranger,
  Urbanist, local community papers like B-Town Blog / West Seattle Blog).
- **Excluded:** social media posts, opposition sites, personal blogs,
  anonymous sources. Do not let these influence anything, even indirectly.

## File format — `data/dossiers/<contest-slug>/<candidate-slug>.md`

```markdown
---
name: Jane Example
slug: jane-example
contest: state-senator-legislative-district-no-32
depth: deep            # deep | light
evidence_level: rich   # rich | moderate | pamphlet-only
researched_at: 2026-07-16
sources:
  - id: S1
    tier: 1
    type: pamphlet
    ref: edition-1 page 30
  - id: S2
    tier: 1
    type: campaign-website
    url: https://...
    accessed: 2026-07-16
  - id: S3
    tier: 2
    type: news
    outlet: Seattle Times
    url: https://...
    accessed: 2026-07-16
---

## Background
Who they are, current role, relevant history. Every sentence cites [Sn].

## Positions
Grouped by topic (housing, taxes, public safety, transit, climate, courts,
etc. as applicable). Bullet points; each bullet cites [Sn]. Distinguish
"says they will" (campaign promises) from "has done" (record).

## Record
For incumbents/officials: concrete votes, sponsored bills, rulings, actions.
Each item cites [Sn]. Omit section if no record exists.

## Endorsements
Who endorsed them, per [Sn]. Omit if none found.

## Scoring notes
2-5 bullets: what genuinely differentiates this candidate from opponents in
this race. Neutral wording.
```

## Rules

- Every factual claim must cite a listed source. No source, no claim.
- Neutral, descriptive tone. No evaluative language ("impressive",
  "concerning"). Describe positions; never grade them.
- Same-name traps: verify identity (jurisdiction, office, city) before
  attributing anything from the web to the candidate.
- `evidence_level`: `rich` = record + multiple independent sources;
  `moderate` = website/endorsements beyond the pamphlet; `pamphlet-only` =
  nothing found beyond the pamphlet statement. Honesty here is load-bearing:
  when in doubt, downgrade.
- Judges: focus on experience, ratings (bar association evaluations are
  Tier 2), notable rulings; partisan inference is inappropriate.
- Contest overview file `_contest.md` per contest: what the office actually
  does, the dynamics of this particular race, and which issue axes truly
  differentiate these candidates (this feeds rubric derivation).
