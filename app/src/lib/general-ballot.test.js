// The November 3, 2026 general as shipped: King County at Full County
// Coverage (issue #16), every other Washington address a Statewide-Only Guide
// (issue #9). These run the app's own ballot, interview, lean and Ballot Brief
// code against public/data/2026-11-03-general.
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
import { contestHeading } from './contests.js'

const data = JSON.parse(
  readFileSync(new URL('../../public/data/2026-11-03-general/app-data.json', import.meta.url), 'utf8')
)

const KING = { id: 'king', fips: '53033', name: 'King County' }

// What lookupBallotContext returns for a Washington address outside King
// County (geo.test.js covers the lookup itself).
const spokane = {
  coverageStatus: 'statewide_only',
  county: { id: 'spokane', fips: '53063', name: 'Spokane County' },
  districts: {},
  missingLayers: [],
}

// King districts as the live District Adapter resolved them on 2026-10-08
// (Census geocoder + King GIS + the DOR cemetery layer).
const king = (districts) => ({ coverageStatus: 'full_county', county: KING, districts, missingLayers: [] })
const ADDRESSES = {
  // 600 4th Ave, Seattle 98104 (City Hall)
  cityHall: king({ CONGDST: '7', LEGDST: '34', KCCDST: '8', SCCDST: 'SCC7', JUDDST: 'W', SCHDST: '1', CITY: 'Seattle' }),
  // 11700 Pinehurst Way NE, Seattle 98125
  pinehurst: king({ CONGDST: '7', LEGDST: '46', KCCDST: '1', SCCDST: 'SCC5', JUDDST: 'W', SCHDST: '1', CITY: 'Seattle' }),
  // 17500 Midvale Ave N, Shoreline 98133
  shoreline: king({ CONGDST: '7', LEGDST: '32', KCCDST: '1', JUDDST: 'SH', FIRDST: '4', SCHDST: '412', CITY: 'Shoreline' }),
  // 10105 SW Bank Rd, Vashon 98070
  vashon: king({ CONGDST: '7', LEGDST: '34', KCCDST: '8', JUDDST: 'SW', FIRDST: '13', SCHDST: '402', CEMDST: '1' }),
  // 220 4th Ave S, Kent 98032
  kent: king({ CONGDST: '9', LEGDST: '33', KCCDST: '5', JUDDST: 'SE', SCHDST: '415', CITY: 'Kent' }),
  // 25 W Main St, Auburn 98001
  auburn: king({ CONGDST: '9', LEGDST: '47', KCCDST: '7', JUDDST: 'SE', SCHDST: '408', CITY: 'Auburn' }),
}

const ballotFor = (context) => {
  const contests = contestsOnBallot(data, context, scopeMatches)
  const measures = measuresOnBallot(data, context, scopeMatches)
  const axes = axesForBallot(data, contests, measures)
  return { contests, measures, axes, items: interviewItemsForBallot(data, axes) }
}

const SUPREME_COURT = [1, 3, 4, 5, 7].map((n) => `justice-position-no-${n}-supreme-court`)
const STATE_MEASURES = [
  'initiative-measure-no-ip26-645',
  'initiative-measure-no-il26-001',
  'initiative-measure-no-il26-638',
]

test('the general ships King at full county coverage and Snohomish at partial, with their elections offices', () => {
  assert.equal(data.election.id, '2026-11-03-general')
  assert.deepEqual(data.coverage, {
    statewide_complete: true,
    supported_counties: [
      {
        id: 'king',
        name: 'King County',
        state: 'WA',
        fips: '53033',
        coverage: 'full_county',
        elections_url: 'https://kingcounty.gov/en/dept/elections',
      },
      {
        // Partial: Snohomish District Court seats are scoped to electoral
        // districts (DISTCRT) no GIS layer resolves (#21).
        id: 'snohomish',
        name: 'Snohomish County',
        state: 'WA',
        fips: '53061',
        coverage: 'partial_county',
        elections_url: 'https://www.snohomishcountywa.gov/224/Elections-Voter-Registration',
      },
    ],
  })
})

test('a Snohomish ballot: statewide races once, its districts, South County Fire only inside the RFA', () => {
  const SNOHOMISH = { id: 'snohomish', fips: '53061', name: 'Snohomish County' }
  const sno = (districts) => ({ coverageStatus: 'partial_county', county: SNOHOMISH, districts, missingLayers: [] })
  // 19100 44th Ave W, Lynnwood (live 2026-10-08, see geo.js RFADST).
  const lynnwood = ballotFor(sno({ CONGDST: '2', LEGDST: '32', CITY: 'Lynnwood', RFADST: 'SCRFA' }))
  const slugs = lynnwood.contests.map((c) => c.slug)
  assert.equal(new Set(slugs).size, slugs.length)
  for (const slug of SUPREME_COURT) assert.ok(slugs.includes(slug), slug)
  assert.ok(slugs.includes('snohomish-legislative-district-32-state-senator'))
  // No District Court seat: DISTCRT never resolves, so they stay hidden.
  assert.ok(!slugs.some((s) => s.includes('district-court')), slugs.join())
  assert.ok(lynnwood.measures.some((m) => m.slug.includes('south-snohomish-county-fire-rescue')))
  const monroe = ballotFor(sno({ CONGDST: '1', LEGDST: '12', CITY: 'Monroe', HOSPDST: 'Hospital District 1' }))
  assert.ok(!monroe.measures.some((m) => m.slug.includes('south-snohomish-county-fire-rescue')))
  assert.ok(monroe.measures.some((m) => m.slug === 'snohomish-public-hospital-district-no-1-proposition-no-1'))
  assert.equal(coverageAdvice(sno({})), 'degraded')
})

test('each Supreme Court contest ships once, owned by the statewide package', () => {
  for (const slug of SUPREME_COURT) {
    const found = data.contests.filter((c) => c.slug === slug)
    assert.equal(found.length, 1, slug)
    assert.equal(found[0].owner, 'statewide')
    assert.deepEqual(found[0].scope, { kind: 'STATEWIDE' })
  }
  const slugs = data.contests.map((c) => c.slug)
  assert.equal(new Set(slugs).size, slugs.length)
})

test('outside King, an address gets all five court races and all three initiatives only', () => {
  const { contests, measures } = ballotFor(spokane)
  assert.deepEqual(contests.map((c) => c.slug), SUPREME_COURT)
  assert.deepEqual(measures.map((m) => m.slug), STATE_MEASURES)
  assert.equal(coverageAdvice(spokane), 'statewide-only')
})

test('every King ballot carries the statewide races once, the countywide races and its district races', () => {
  const COUNTYWIDE = [
    'prosecuting-attorney',
    'assessor',
    'director-of-elections',
    'court-of-appeals-division-1-district-1-judge-position-no-5',
    'court-of-appeals-division-1-district-1-judge-position-no-6',
  ]
  for (const [name, context] of Object.entries(ADDRESSES)) {
    const { contests, measures } = ballotFor(context)
    const slugs = contests.map((c) => c.slug)
    assert.equal(new Set(slugs).size, slugs.length, name)
    for (const slug of [...SUPREME_COURT, ...COUNTYWIDE]) assert.ok(slugs.includes(slug), `${name}: ${slug}`)
    assert.deepEqual(measures.slice(0, 3).map((m) => m.slug), STATE_MEASURES, name)
    assert.ok(slugs.includes(`congressional-district-${context.districts.CONGDST}-united-states-representative`), name)
    assert.ok(slugs.some((s) => s.endsWith(`legislative-district-no-${context.districts.LEGDST}`)), name)
    // The district court contests are exactly the voter's electoral district's.
    const court = { NE: 'northeast', SE: 'southeast', SW: 'southwest', W: 'west', SH: 'shoreline' }[context.districts.JUDDST]
    const courts = slugs.filter((s) => /^judge-position-no-\d+-.+-electoral-district$/.test(s))
    assert.ok(courts.length >= 2, name)
    for (const s of courts) assert.ok(s.endsWith(`-${court}-electoral-district`), `${name}: ${s}`)
    assert.equal(coverageAdvice(context), null)
  }
})

test('Seattle gets Seattle Prop 1 and Municipal Court; Council D5 only inside D5', () => {
  for (const name of ['cityHall', 'pinehurst']) {
    const { contests, measures } = ballotFor(ADDRESSES[name])
    const slugs = contests.map((c) => c.slug)
    assert.ok(measures.some((m) => m.slug === 'city-of-seattle-proposition-no-1'), name)
    assert.equal(slugs.filter((s) => s.startsWith('municipal-court-judge-position-no-')).length, 7, name)
    assert.equal(slugs.includes('council-district-no-5-city-of-seattle'), name === 'pinehurst', name)
  }
})

test('local measures reach exactly their own district', () => {
  const local = (name) => ballotFor(ADDRESSES[name]).measures.filter((m) => m.owner === 'king').map((m) => m.slug)
  assert.deepEqual(local('cityHall'), ['city-of-seattle-proposition-no-1'])
  assert.deepEqual(local('shoreline'), ['city-of-shoreline-proposition-no-1'])
  assert.deepEqual(local('vashon'), ['king-county-cemetery-district-no-1-proposition-no-1'])
  assert.deepEqual(local('kent'), ['kent-school-district-no-415-proposition-no-1'])
  assert.deepEqual(local('auburn'), ['auburn-school-district-no-408-proposition-no-1'])
})

test('uncontested King contests ship information-only, with no scores', () => {
  const uncontested = data.contests.filter((c) => c.owner === 'king' && c.uncontested)
  assert.ok(uncontested.length >= 30)
  for (const c of uncontested) {
    assert.equal(c.candidates.length, 1, c.slug)
    assert.deepEqual(c.candidates[0].scores, {}, c.slug)
  }
  // Most carry a researched summary; the rest are the official ballot entry.
  const levels = new Set(uncontested.map((c) => c.candidates[0].evidence_level))
  for (const level of levels) assert.ok(['rich', 'moderate', 'pamphlet-only', 'official-ballot-only'].includes(level), level)
  assert.ok(uncontested.filter((c) => c.candidates[0].summary).length >= 30)
})

// The interview is ballot-driven: a King ballot reaches all fifteen axes,
// parental-rights included; the statewide-only ballot reaches eight.
const STATEWIDE_AXES = ['experience', 'judicial', 'local-control', 'parental-rights', 'safety', 'social', 'spending', 'taxes']

test('the statewide-only interview asks only about axes on the statewide ballot', () => {
  const { axes, items } = ballotFor(spokane)
  assert.deepEqual([...axes].sort(), STATEWIDE_AXES)
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

test('every King interview asks the parental-rights card and covers the whole rubric', () => {
  for (const [name, context] of Object.entries(ADDRESSES)) {
    const { axes, items } = ballotFor(context)
    assert.equal(axes.size, data.rubric.axes.length, name)
    assert.ok(items.some((i) => i.id === 'card-parental-rights'), name)
  }
})

const agreeWithEverything = (items) =>
  buildProfile(
    items.map((item) => ({ item, choice: item.kind === 'statement' ? 'agree' : 0 })),
    {}
  )

test('a voter who answers the interview gets a lean on every measure on the ballot', () => {
  for (const context of [spokane, ...Object.values(ADDRESSES)]) {
    const { measures, items } = ballotFor(context)
    const answers = agreeWithEverything(items)
    for (const m of measures) {
      const { lean } = measureLean(m, answers)
      assert.ok(['yes', 'no', 'split'].includes(lean), `${m.slug}: lean ${lean}`)
    }
  }
})

test('every contested race ranks all its candidates', () => {
  const { items } = ballotFor(ADDRESSES.cityHall)
  const answers = agreeWithEverything(items)
  for (const c of data.contests.filter((x) => !x.uncontested)) {
    const { rows } = rankContest(c, answers)
    assert.equal(rows.length, c.candidates.length, c.slug)
    assert.ok(c.candidates.length >= 2, c.slug)
  }
})

const briefFor = (context) => {
  const { contests, measures, items } = ballotFor(context)
  return {
    contests,
    measures,
    text: buildBrief(data, context, agreeWithEverything(items), contests, measures, 'https://example.test/washington-state#p=abc', ''),
  }
}

test('the statewide-only Ballot Brief carries the warning and every contest and measure', () => {
  const { contests, measures, text } = briefFor(spokane)
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

test('a King Ballot Brief is a full county guide naming every contest once and every measure', () => {
  const { contests, measures, text } = briefFor(ADDRESSES.pinehurst)
  assert.match(text, /^Coverage: FULL COUNTY GUIDE\.$/m)
  assert.match(text, /contests on the November 3, 2026 General Election ballot that Voter Lifeboat matched/)
  assert.match(text, /Resolved county: King County/)
  assert.doesNotMatch(text, /STATEWIDE-ONLY|PARTIAL COUNTY/)
  for (const c of contests) {
    const { office, place } = contestHeading(c)
    const heading = `## ${office.toUpperCase()} — ${place}`
    assert.equal(text.split('\n').filter((l) => l === heading).length, 1, heading)
  }
  assert.equal(text.split('\n').filter((l) => l.startsWith('## SUPREME COURT')).length, 5)
  for (const m of measures)
    assert.ok(text.split('\n').some((l) => l.startsWith(`### ${m.jurisdiction} ${m.proposition}:`)), m.slug)
  assert.match(text, /Official pamphlet statement: https:\/\/cdn\.kingcounty\.gov\/.*local-edition\.pdf#page=\d+/)
  assert.match(text, /Official pamphlet statement: https:\/\/www\.sos\.wa\.gov\/.*Edition%2004.*#page=\d+/)
})

test('the general Ballot Brief names election day, terms and SOS pamphlet pages, never the primary', () => {
  const { text } = briefFor(spokane)
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
  const kingText = briefFor(ADDRESSES.kent).text
  assert.doesNotMatch(kingText, /past the primary|top 2|voters-pamphlets\/2026\/08/i)
})

test('the general ships contest terms from the statewide package', () => {
  const terms = Object.fromEntries(data.contests.map((c) => [c.slug, c.term]))
  assert.equal(terms['justice-position-no-1-supreme-court'], '2-year unexpired term')
  assert.equal(terms['justice-position-no-5-supreme-court'], '2-year unexpired term')
  assert.equal(terms['justice-position-no-3-supreme-court'], '6-year term')
})

test('the King Ballot Brief heads each contest office first, then where (issue #25)', () => {
  const { text } = briefFor(ADDRESSES.pinehurst)
  assert.match(text, /^## STATE SENATOR — Legislative District 46$/m)
  assert.match(text, /^## STATE REPRESENTATIVE POSITION NO\. 1 — Legislative District 46$/m)
  assert.match(text, /^## JUDGE POSITION NO\. 1 — King County District Court, West Electoral District$/m)
  assert.match(text, /^## COUNCIL DISTRICT NO\. 5 — City of Seattle$/m)
  assert.match(text, /^## PROSECUTING ATTORNEY — Countywide$/m)
  assert.doesNotMatch(text, /^## (LEGISLATIVE DISTRICT|CITY OF|\w+ ELECTORAL DISTRICT)/m)
})
