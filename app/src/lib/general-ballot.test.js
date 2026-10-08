// The November 3, 2026 general as shipped (issue #9): a Statewide-Only Guide
// for every Washington address. These run the app's own ballot, interview,
// lean and Ballot Brief code against public/data/2026-11-03-general.
import test from 'node:test'
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { scopeMatches, coverageAdvice } from './geo.js'
import {
  contestsOnBallot,
  measuresOnBallot,
  axesForBallot,
  interviewItemsForBallot,
  buildProfile,
  measureLean,
  rankContest,
} from './scoring.js'
import { buildBrief } from './brief.js'

const data = JSON.parse(
  readFileSync(new URL('../../public/data/2026-11-03-general/app-data.json', import.meta.url), 'utf8')
)

// What lookupBallotContext returns for any Washington address while no county
// ships (geo.test.js covers the lookup itself).
const spokane = {
  coverageStatus: 'statewide_only',
  county: { id: 'spokane', fips: '53063', name: 'Spokane County' },
  districts: {},
  missingLayers: [],
}
const king = { ...spokane, county: { id: 'king', fips: '53033', name: 'King County' } }

const ballotFor = (context) => {
  const contests = contestsOnBallot(data, context, scopeMatches)
  const measures = measuresOnBallot(data, context, scopeMatches)
  const axes = axesForBallot(data, contests, measures)
  return { contests, measures, axes, items: interviewItemsForBallot(data, axes) }
}

test('the general ships real statewide data, so the notice page is not shown', () => {
  assert.equal(data.election.id, '2026-11-03-general')
  assert.deepEqual(data.coverage, { statewide_complete: true, supported_counties: [] })
  // App.jsx shows ElectionNotice only when both lists are empty.
  assert.ok(data.contests.length && data.measures.length)
})

test('every Washington address gets all five court races and all three initiatives', () => {
  for (const context of [spokane, king]) {
    const { contests, measures } = ballotFor(context)
    assert.deepEqual(
      contests.map((c) => c.slug),
      [1, 3, 4, 5, 7].map((n) => `justice-position-no-${n}-supreme-court`)
    )
    assert.deepEqual(measures.map((m) => m.slug), [
      'initiative-measure-no-ip26-645',
      'initiative-measure-no-il26-001',
      'initiative-measure-no-il26-638',
    ])
    assert.equal(coverageAdvice(context), 'statewide-only')
  }
})

// The interview is ballot-driven. Justices are scored on judicial, experience
// and safety; the initiatives map onto parental-rights, social, taxes,
// local-control and (IP26-645, upheld by its refutation) spending.
const GENERAL_AXES = [
  'experience',
  'judicial',
  'local-control',
  'parental-rights',
  'safety',
  'social',
  'spending',
  'taxes',
]

test('the interview asks only about axes on the statewide ballot', () => {
  const { axes, items } = ballotFor(spokane)
  assert.deepEqual([...axes].sort(), GENERAL_AXES)
  const asked = new Set(
    items.flatMap((item) =>
      item.kind === 'statement' ? [item.axis] : item.options.flatMap((o) => Object.keys(o.effects))
    )
  )
  assert.deepEqual([...asked].sort(), GENERAL_AXES)
  assert.deepEqual(items.map((i) => i.id), [
    'card-taxes',
    'card-spending',
    'scenario-safety',
    'card-experience',
    'card-local',
    'scenario-budget',
    'card-social',
    'card-parental-rights',
    'card-judicial',
  ])
})

const agreeWithEverything = (items) =>
  buildProfile(
    items.map((item) => ({ item, choice: item.kind === 'statement' ? 'agree' : 0 })),
    {}
  )

test('a voter who answers the interview gets a lean on all three initiatives', () => {
  const { measures, items } = ballotFor(spokane)
  const answers = agreeWithEverything(items)
  for (const m of measures) {
    const { lean } = measureLean(m, answers)
    assert.ok(['yes', 'no', 'split'].includes(lean), `${m.slug}: lean ${lean}`)
  }
})

test('every court race ranks its candidates', () => {
  const { contests, items } = ballotFor(spokane)
  const answers = agreeWithEverything(items)
  for (const c of contests) {
    const { rows } = rankContest(c, answers)
    assert.equal(rows.length, 2, c.slug)
  }
})

test('the Ballot Brief carries the statewide-only warning and every contest and measure', () => {
  const { contests, measures, items } = ballotFor(spokane)
  const text = buildBrief(
    data,
    spokane,
    agreeWithEverything(items),
    contests,
    measures,
    'https://example.test/washington-state#p=abc',
    ''
  )
  assert.match(text, /November 3, 2026 General Election/)
  assert.match(text, /Coverage: STATEWIDE-ONLY GUIDE/)
  assert.match(text, /omits county, city, school, fire, judicial district, and other local contests/)
  assert.match(text, /Resolved county: Spokane County/)
  for (const c of contests) assert.ok(text.includes(`## SUPREME COURT — ${c.district}`), c.slug)
  assert.match(text, /## BALLOT MEASURES/)
  for (const m of measures) {
    const line = text.split('\n').find((l) => l.startsWith(`### ${m.jurisdiction} ${m.proposition}:`))
    assert.ok(line, `${m.slug} missing from brief`)
    assert.match(line, /leans (YES|NO) for me|genuinely split for me/, line)
  }
})

test('the general Ballot Brief names election day, terms and SOS pamphlet pages, never the primary', () => {
  const { contests, measures, items } = ballotFor(spokane)
  const text = buildBrief(
    data,
    spokane,
    agreeWithEverything(items),
    contests,
    measures,
    'https://example.test/washington-state#p=abc',
    ''
  )
  assert.match(text, /^# MY BALLOT BRIEF — Washington State, November 3, 2026 General Election$/m)
  assert.match(text, /^Election day: Tuesday, November 3, 2026\.$/m)
  assert.match(text, /statewide contests on the November 3, 2026 General Election ballot/)
  assert.match(text, /^Term: 2-year unexpired term$/m)
  assert.match(text, /Official pamphlet (statement|entry): https:\/\/www\.sos\.wa\.gov\/.*#page=\d+/)
  // Candidate summaries and sources may mention August or King County; the
  // brief's own copy and pamphlet links must not.
  assert.doesNotMatch(text, /past the primary|top 2/i)
  for (const line of text.split('\n').filter((l) => l.startsWith('Official pamphlet')))
    assert.match(line, /: https:\/\/www\.sos\.wa\.gov\//, line)
})

test('the general ships contest terms from the statewide package', () => {
  const terms = Object.fromEntries(data.contests.map((c) => [c.slug, c.term]))
  assert.equal(terms['justice-position-no-1-supreme-court'], '2-year unexpired term')
  assert.equal(terms['justice-position-no-5-supreme-court'], '2-year unexpired term')
  assert.equal(terms['justice-position-no-3-supreme-court'], '6-year term')
})
