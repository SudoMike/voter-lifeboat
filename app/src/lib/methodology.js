// Rubric-specific notes for the Methodology page. The page renders whichever
// election is being served, and an archived election keeps its own rubric
// (ADR-0004), so every note here is derived from that election's rubric or
// keyed by its app-data `election.id` rather than written for one election.

// Readable names for rubric `applies_to` categories, as contests...
const CATEGORY_NAMES = {
  Federal: 'federal contests',
  State: 'state legislative contests',
  County: 'county contests',
  City: 'city contests',
  measures: 'ballot measures',
}

// ...and as the candidates in them. Only categories that can hold a
// partisan-adjacent axis are listed; judges are never on one.
const CANDIDATE_NAMES = {
  Federal: 'federal',
  State: 'state legislative',
  County: 'county',
  City: 'city',
}

// Scoring rules adopted for one election's research, keyed by app-data
// `election.id`. Each is recorded as a dated addendum in that election's
// counties/king/scoring/SCORING-GUIDE.md.
export const ELECTION_RULES = {
  '2026-11-03-general': [
    {
      id: 'taxes-single-vote',
      axis: 'taxes',
      title: 'One vote is not a record',
      text:
        "A legislator's single floor vote on the 2026 tax on income over " +
        '$1 million (ESSB 6346), with no second independent source in the ' +
        'dossier, places them one step from the middle on the taxes axis at ' +
        'medium confidence, never at the pole.',
    },
  ],
}

const joinWords = (words) =>
  words.length <= 1
    ? words.join('')
    : `${words.slice(0, -1).join(', ')} and ${words[words.length - 1]}`

/**
 * Notes for one election's rubric:
 * - `split`: the rubric has both `social` and `parental-rights`;
 * - `parentalRights`: { scored, notScored } readable category lists, or null;
 * - `localControlOverlap`: `local-control` and `parental-rights` both exist,
 *   so school-governance evidence needs a stated home;
 * - `rules`: election-specific evidence rules whose axis is in the rubric.
 */
export function rubricNotes(rubric, electionId) {
  const axes = rubric?.axes || []
  const byId = Object.fromEntries(axes.map((a) => [a.id, a]))
  const pr = byId['parental-rights']
  const applies = pr?.applies_to || []
  return {
    split: Boolean(byId.social && pr),
    parentalRights: pr
      ? {
          scored: joinWords(applies.map((c) => CATEGORY_NAMES[c] || c)),
          notScored: joinWords(
            Object.keys(CANDIDATE_NAMES)
              .filter((c) => !applies.includes(c))
              .map((c) => CANDIDATE_NAMES[c]),
          ),
        }
      : null,
    localControlOverlap: Boolean(pr && byId['local-control']),
    rules: (ELECTION_RULES[electionId] || []).filter((r) => byId[r.axis]),
  }
}
