import test from 'node:test'
import assert from 'node:assert/strict'
import { buildBrief, researchLenses } from './brief.js'

const data = {
  election: { scope: 'Washington State', name: 'August 4, 2026 Primary and Special Election' },
  rubric: {
    axes: [
      { id: 'judicial', title: 'Judicial restraint', pole_a: { label: 'Restraint' }, pole_b: { label: 'Access' } },
    ],
  },
}

const primary = {
  ...data,
  election: { id: '2026-08-04-primary-special', scope: 'Washington State', name: 'August 4, 2026 Primary and Special Election', day: '2026-08-04' },
}
const general = {
  ...data,
  election: { id: '2026-11-03-general', scope: 'Washington State', name: 'November 3, 2026 General Election', day: '2026-11-03' },
}

const statewideOnly = { coverageStatus: 'statewide_only', county: { name: 'Pierce County' }, districts: {} }
const answers = { judicial: { v: 1, w: 1 } }

test('Ballot Brief starts in orientation mode and includes coverage warning', () => {
  const text = buildBrief(data, statewideOnly, answers, [], [], 'https://example.test/washington-state#p=abc')
  assert.match(text, /Coverage: STATEWIDE-ONLY GUIDE/)
  assert.match(text, /Do not generate the HTML report immediately/)
  assert.match(text, /Wait for my answer before producing the HTML report/)
  assert.match(text, /WHEN I ASK FOR THE HTML REPORT/)
})

test('Ballot Brief header and coverage warning name the loaded election and its day', () => {
  const text = buildBrief(general, statewideOnly, answers, [], [], 'https://example.test/washington-state#p=abc')
  assert.match(text, /^# MY BALLOT BRIEF — Washington State, November 3, 2026 General Election$/m)
  assert.match(text, /^Election day: Tuesday, November 3, 2026\.$/m)
  assert.match(text, /only the statewide contests on the November 3, 2026 General Election ballot/)
})

test('Ballot Brief prints a contest term when the data carries one', () => {
  const contest = {
    slug: 'x', office: 'Supreme Court', district: 'Justice Position No. 1', term: '2-year unexpired term',
    category: 'StateSupremeCourt', scope: { kind: 'STATEWIDE' }, candidates: [],
  }
  const text = buildBrief(data, statewideOnly, answers, [contest], [], 'https://example.test/')
  assert.match(text, /^### SUPREME COURT — Justice Position No\. 1\nTerm: 2-year unexpired term/m)
})

test('Ballot Brief names unresolved district lookups in words, not layer ids', () => {
  const text = buildBrief(
    data,
    { coverageStatus: 'partial_county', county: { name: 'King County' }, districts: {}, missingLayers: ['KCCDST', 'SCCDST', 'JUDDST'] },
    answers,
    [],
    [],
    'https://example.test/'
  )
  assert.match(
    text,
    /District lookups that did not resolve: King County Council District, Seattle City Council District, King County District Court Electoral District\./
  )
  assert.doesNotMatch(text, /KCCDST|SCCDST|JUDDST/)
})

const photoContest = {
  slug: 'justice-position-no-1-supreme-court', owner: 'statewide', category: 'StateSupremeCourt', office: 'Supreme Court',
  district: 'Justice Position No. 1', scope: { kind: 'STATEWIDE' }, uncontested: false,
  candidates: [
    {
      slug: 'with-photo', name: 'With Photo', evidence_level: 'rich', summary: 'Has a photo.', highlights: [],
      scores: { judicial: { score: 1, confidence: 'high' } }, sources: [], pamphlet_pages: [],
      photo: { url: 'https://www.courts.wa.gov/images/JusticeMelody2025.png', page: 'https://www.courts.wa.gov/appellate_trial_courts/SupremeCourt/?fa=supremecourt.justices', kind: 'government' },
    },
    {
      slug: 'without-photo', name: 'Without Photo', evidence_level: 'moderate', summary: 'No photo.', highlights: [],
      scores: { judicial: { score: -1, confidence: 'high' } }, sources: [], pamphlet_pages: [],
    },
  ],
}

test('Ballot Brief prints a Photo line only for a candidate with a Candidate Photo', () => {
  const text = buildBrief(data, statewideOnly, answers, [photoContest], [], 'https://example.test/')
  assert.match(
    text,
    /^Photo: https:\/\/www\.courts\.wa\.gov\/images\/JusticeMelody2025\.png \(from https:\/\/www\.courts\.wa\.gov\/appellate_trial_courts\/SupremeCourt\/\?fa=supremecourt\.justices\)$/m
  )
  const without = text.slice(text.indexOf('#### Without Photo'), text.indexOf('\n---'))
  assert.doesNotMatch(without, /^Photo:/m)
  assert.equal(text.match(/^Photo: /gm).length, 1)
})

test('Ballot Brief tells the chatbot to hotlink the verified Photo URLs instead of embedding base64', () => {
  const text = buildBrief(data, statewideOnly, answers, [photoContest], [], 'https://example.test/')
  const photoRules = text.slice(text.indexOf('## CANDIDATE PHOTOS'), text.indexOf('## EACH RACE SECTION'))
  assert.doesNotMatch(photoRules, /base64/)
  assert.match(photoRules, /use that URL as the img src/)
  assert.match(photoRules, /Do not search for a different photo when one is given/)
  assert.match(photoRules, /identity aid, never evidence of qualification/)
  assert.match(text, /hotlink them from the "Photo:" URLs given in this brief/)
  assert.doesNotMatch(text, /never hotlink a remote URL/)
  assert.doesNotMatch(text, /EMBED REAL PHOTO HERE/)
  assert.match(text, /<img src="\[Photo URL from the brief\]"/)
  assert.match(text, /Photos are linked from the official, campaign, party, or government pages listed in the brief/)
})

// #40: the concerns textarea is gone; the chatbot asks instead.
test('Ballot Brief has no questions-and-concerns section and takes no concerns argument', () => {
  const text = buildBrief(data, statewideOnly, answers, [], [], 'https://example.test/', 'push back on my lean')
  assert.doesNotMatch(text, /MY QUESTIONS AND CONCERNS/)
  assert.doesNotMatch(text, /push back on my lean/)
})

test('the first response offers all four Research Lenses, asks for anything else, and waits', () => {
  const text = buildBrief(general, statewideOnly, answers, [], [], 'https://example.test/')
  const first = text.slice(text.indexOf('## FIRST RESPONSE INSTRUCTIONS'), text.indexOf('## WHEN I ASK FOR THE HTML REPORT'))
  for (const lens of researchLenses('general')) {
    assert.match(first, new RegExp(`^- ${lens.name}: ${lens.text.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}$`, 'm'))
  }
  assert.deepEqual(
    researchLenses('general').map((l) => l.name),
    ['No extremists', 'Follow the money', 'Real track record', 'Who can win']
  )
  assert.match(first, /offer me these four research lenses and ask me which to apply/)
  assert.match(first, /anything else I want you to know or check/)
  assert.match(first, /Wait for my answer before producing the HTML report/)
})

test('the who-can-win lens follows the election kind', () => {
  const inPrimary = buildBrief(primary, statewideOnly, answers, [], [], 'https://example.test/')
  assert.match(inPrimary, /^- Who can win: .*advancing past the primary\.$/m)
  assert.doesNotMatch(inPrimary, /shot of winning\./)
  const inGeneral = buildBrief(general, statewideOnly, answers, [], [], 'https://example.test/')
  assert.match(inGeneral, /^- Who can win: .*shot of winning\.$/m)
  assert.doesNotMatch(inGeneral, /past the primary/)
  // An election the guide does not know reads as a general.
  assert.match(buildBrief(data, statewideOnly, answers, [], [], 'https://example.test/'), /shot of winning\./)
})

const contestOf = (slug, category, office, district) => ({
  slug, owner: 'king', category, office, district, scope: { kind: 'DISTRICT' }, uncontested: false, candidates: [],
})

test('Ballot Brief groups contests under the Ballot Sections in ballot order, measures first', () => {
  const contests = [
    contestOf('pud', 'PublicUtility', 'Commissioner', 'PUD No. 1'),
    contestOf('assessor', 'County', 'Assessor', ''),
    contestOf('rep', 'Federal', 'United States Representative', 'Congressional District 7'),
    contestOf('senator', 'State', 'State Senator', 'Legislative District 46'),
    contestOf('justice', 'StateSupremeCourt', 'Supreme Court', 'Justice Position No. 1'),
    contestOf('judge', 'DistrictCourt', 'Judge Position No. 1', 'West Electoral District'),
  ]
  const measure = {
    slug: 'i-645', owner: 'statewide', jurisdiction: 'State of Washington', proposition: 'Initiative Measure No. IP26-645',
    title: 'Concerns state and local taxes.', scope: { kind: 'STATEWIDE' }, lean_mappings: {}, pamphlet_pages: [],
  }
  const text = buildBrief(general, statewideOnly, answers, contests, [measure], 'https://example.test/')
  const headings = text
    .slice(text.indexOf('## MEASURES'), text.indexOf('\n---'))
    .split('\n')
    .filter((l) => /^###? /.test(l))
  assert.deepEqual(headings, [
    '## MEASURES',
    '### State of Washington Initiative Measure No. IP26-645: Concerns state and local taxes. — no lean computed (my interview did not map cleanly onto it)',
    '## FEDERAL',
    '### UNITED STATES REPRESENTATIVE — Congressional District 7',
    '## STATE',
    '### STATE SENATOR — Legislative District 46',
    '## COURTS',
    '### SUPREME COURT — Justice Position No. 1',
    '### JUDGE POSITION NO. 1 — West Electoral District',
    '## COUNTY',
    '### ASSESSOR — Countywide',
    '## LOCAL',
    '### COMMISSIONER — PUD No. 1',
  ])
  assert.doesNotMatch(text, /## BALLOT MEASURES/)
  assert.match(text, /in the same order as this brief/)
})

test('a Ballot Brief with no measures has no Measures section', () => {
  const text = buildBrief(general, statewideOnly, answers, [photoContest], [], 'https://example.test/')
  assert.doesNotMatch(text, /^## MEASURES$/m)
  assert.match(text, /^## COURTS$/m)
})

test('Ballot Brief distinguishes experience-only evidence from missing evidence', () => {
  const contest = {
    slug: 'x', office: 'Supreme Court', district: 'Justice Position No. 5',
    category: 'StateSupremeCourt', scope: { kind: 'STATEWIDE' },
    candidates: [
      { name: 'Experience candidate', scores: { experience: { score: -1, confidence: 'high' } } },
      { name: 'No evidence candidate', scores: {} },
      { name: 'Skipped issue candidate', scores: { experience: { score: -1, confidence: 'high' }, judicial: { score: 1, confidence: 'high' } } },
    ],
  }
  for (const profile of [{}, { experience: { v: -1, w: 1 } }]) {
    const text = buildBrief(data, statewideOnly, profile, [contest], [], 'https://example.test/')
    assert.match(text, /#### Experience candidate — scored on record vs\. renewal only; no Alignment Score/)
    assert.match(text, /#### No evidence candidate — not enough evidence to score/)
    assert.match(text, /#### Skipped issue candidate — not enough evidence to score/)
  }
})
