# Dossier research guide

How every dossier in this directory was produced. Research agents follow this
spec exactly.

This guide covers every package in the November 3, 2026 general election.
Paths below use `E` = `data/washington-state/elections/2026-11-03-general`
and `<package>` = `statewide` or `counties/<county>` (the package that owns
the contest). As in the primary, the statewide package follows this guide
rather than carrying its own copy. The issue axes are in
`data/final/2026-11-03-general/rubric.json` (15 axes).

## Source policy (see CONTEXT.md "Source Tier")

- **Tier 1 (always use):** the candidate's official pamphlet statement
  (archived under the owning package, e.g.
  `E/counties/king/interim/pamphlet-text/<edition>/page-NNN.txt`),
  the candidate's own campaign website, PDC campaign-finance filings
  (pdc.wa.gov), official voting/legislative records (leg.wa.gov,
  congress.gov, county/city council records, court opinions for judges).
- **Tier 2 (use and cite):** endorsement lists (newspapers, unions, parties,
  advocacy orgs), news coverage from established outlets (Seattle Times,
  Seattle P-I, Crosscut/Cascade PBS, KUOW, KING5, Publicola, The Stranger,
  Urbanist, local community papers like B-Town Blog / West Seattle Blog).
- **Excluded:** social media posts, opposition sites, personal blogs,
  anonymous sources. Do not let these influence anything, even indirectly.

## File format — `E/<package>/dossiers/<contest-slug>/<candidate-slug>.md`

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
gender and reproductive policy, parents and schools, etc. as applicable). Bullet points; each bullet cites [Sn]. Distinguish
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

### Photo (the Candidate Photo)

A candidate dossier may carry one optional top-level `photo` block (after
`sources:` or anywhere in the frontmatter):

```yaml
photo:
  url: https://www.courts.wa.gov/images/JusticeMelody2025.png            # direct https image URL
  page: https://www.courts.wa.gov/appellate_trial_courts/SupremeCourt/?fa=supremecourt.justices   # the page a human sees it on
  kind: government                                                        # pamphlet | government | campaign-website | other
```

- `url` is a direct `https://` image URL (served with an `image/*` content
  type), never an HTML page and never a PDF. Pamphlet PDFs cannot be linked
  as a photo; `kind: pamphlet` is for a county or SOS web page that serves
  the pamphlet headshot as an image file.
- `page` is the `https://` page where a human can see the photo (the credit
  caption). It may equal `url` when the image is served standalone.
- When several exist, prefer `pamphlet` > `government` (an official bio page:
  legislature, courts, city or county site) > `campaign-website` > `other`.
  `other` means a party page or similar. Never a news photo (licensing),
  and never a logo, group shot, or ballot-measure graphic: a single-person
  headshot of the right candidate only.
- The photo is an identity aid, never evidence of qualification; it is not
  a source and gets no `[Sn]`.
- Measure dossiers (`dossiers/measures/*.md`) and `_contest.md` never carry
  `photo`.
- `pipeline/propose_candidate_photos.py` proposes photos from campaign
  sites into `interim/photo-proposals.json` for a human or agent to accept;
  `pipeline/verify_dossiers.py` checks the block (`--check-photos` fetches
  each URL).

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
  Tier 2), notable rulings; partisan inference is inappropriate. Judges are
  never scored on `social` or `parental-rights`, so do not research or
  record positions on those topics for judicial candidates.
- `social` and `parental-rights` are separate axes in the general. Keep the
  evidence apart in Positions: gender, LGBTQ+, sports eligibility and
  reproductive policy under one heading; parental notification, record
  access, curricula opt-outs and school-provided services under another. A
  source about one is not evidence about the other.
- Statewide measure dossiers (I-645, I-1, I-638) should note evidence for
  the intended axes recorded in
  `data/final/2026-11-03-general/rubric-derivation.md`: I-645 →
  `taxes` and `local-control`, I-1 → `parental-rights`, I-638 → `social`.
- Contest overview file `_contest.md` per contest: what the office actually
  does, the dynamics of this particular race, and which issue axes truly
  differentiate these candidates (this feeds rubric derivation, via
  `pipeline/extract_axis_notes.py` into `E/counties/king/interim/axis-notes.md`).

## Addendum (2026-10-08, issue #19): recording positions

Matches the 2026-10-08 addendum in `counties/king/scoring/SCORING-GUIDE.md`.

- **Taxes.** For a legislator whose only tax evidence would be the ESSB 6346
  floor vote, look for a second independent source (another recorded vote, a
  sponsored bill, an explicit statement, a platform plank). Without one the
  score is capped at magnitude 1, medium confidence.
- **Parents and schools.** Record positions on parental notification, record
  access and curricula opt-outs for any non-judicial candidate who has them.
  Only State legislative contests and measures are scored on
  `parental-rights`; for Federal, County and City candidates the position is
  recorded in the dossier but not scored.
- **School governance** belongs under the parents-and-schools heading, not
  under local control.
