// The Results page's link to the archived election (issue #18), and how the
// archived page reads the payload it receives. Checked against the shipped
// data so the ids, versions and axis titles stay in step with it.
import test from 'node:test'
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import {
  SOURCE_AXIS_TITLES,
  answersInRubric,
  comparisonHref,
  comparisonLinkText,
  comparisonNote,
  comparisonTarget,
  reconcileContext,
} from './compare.js'
import { decodeProfile } from './codec.js'
import { ELECTION_INDEX_PATH, appDataPath, findElection } from './elections.js'
import { shouldRecordReport } from './reports.js'
import { contestsOnBallot, measuresOnBallot } from './scoring.js'
import { scopeMatches } from './geo.js'

const readPublic = (path) =>
  JSON.parse(readFileSync(new URL(`../../public/${path}`, import.meta.url), 'utf8'))
const index = readPublic(ELECTION_INDEX_PATH)
const generalEntry = findElection(index, '2026-11-03-general')
const primaryEntry = findElection(index, '2026-08-04-primary')
const general = readPublic(appDataPath(generalEntry))
const primary = readPublic(appDataPath(primaryEntry))

const BASE = '/washington-state/'
const KING = { id: 'king', fips: '53033', name: 'King County' }

// A statewide-only King context: what lookupBallotContext returned for a King
// address against the general before King shipped in it (#16).
const liveGeneralContext = {
  coverageStatus: 'statewide_only',
  county: KING,
  districts: {},
  missingLayers: [],
  matched: '1301 3RD AVE, SEATTLE, WA, 98101',
}

const allGeneralAnswers = Object.fromEntries(
  general.rubric.axes.map((a, i) => [a.id, { v: (i % 5) - 2, w: 1 }])
)

const fromHash = (href) => decodeProfile(href.split('#p=')[1])

test('the link shows for a live, address-resolved ballot context on the active election', () => {
  const target = comparisonTarget({ index, election: generalEntry, context: liveGeneralContext, restored: null })
  assert.equal(target, primaryEntry)
  for (const coverageStatus of ['full_county', 'partial_county']) {
    const context = { ...liveGeneralContext, coverageStatus, districts: { LEGDST: '43' } }
    assert.equal(comparisonTarget({ index, election: generalEntry, context, restored: null }), primaryEntry)
  }
})

test('the link is hidden for restored links, unresolved contexts and archived pages', () => {
  const show = (over) =>
    comparisonTarget({ index, election: generalEntry, context: liveGeneralContext, restored: null, ...over })
  // A report that arrived by link, tampered or not.
  assert.equal(show({ restored: { context: liveGeneralContext } }), null)
  // A context with no matched address did not come from the address flow
  // (decodeProfile never carries `matched`).
  const { matched, ...noMatch } = liveGeneralContext
  assert.equal(show({ context: noMatch }), null)
  assert.equal(show({ context: { ...liveGeneralContext, county: undefined } }), null)
  assert.equal(show({ context: { ...liveGeneralContext, coverageStatus: 'bogus' } }), null)
  assert.equal(show({ context: null }), null)
  // Already on the archived election.
  assert.equal(show({ election: primaryEntry }), null)
  // No archived election in the index.
  assert.equal(show({ index: { ...index, elections: [generalEntry] } }), null)
})

test('the link text names the archived election by its day and kind', () => {
  assert.equal(
    comparisonLinkText(primaryEntry),
    'See how these values would have applied to the August 4 primary ballot →'
  )
})

test('the link goes to the archived route with the archived app id, data version and the same context', () => {
  const href = comparisonHref(BASE, primaryEntry, general.election.id, liveGeneralContext, allGeneralAnswers)
  assert.match(href, /^\/washington-state\/2026-08-04-primary#p=[A-Za-z0-9_-]+$/)
  const p = fromHash(href)
  assert.equal(p.electionId, '2026-08-04-primary-special')
  assert.equal(p.electionId, primary.election.id)
  // Matches the archived data, so its page shows no "data updated" banner.
  assert.equal(p.dataVersion, primary.data_version)
  assert.equal(p.fromElectionId, '2026-11-03-general')
  assert.deepEqual(p.context, {
    coverageStatus: 'statewide_only',
    county: KING,
    districts: {},
    missingLayers: [],
  })
  assert.deepEqual(p.answers, allGeneralAnswers)
  assert.equal(href.includes('SEATTLE'), false)
})

test('the archived page never records a report for the comparison', () => {
  const p = fromHash(comparisonHref(BASE, primaryEntry, general.election.id, liveGeneralContext, allGeneralAnswers))
  assert.equal(shouldRecordReport({ election: primaryEntry, restored: p }), false)
  // Archived alone is enough, even if the payload were not marked restored.
  assert.equal(shouldRecordReport({ election: primaryEntry, restored: null }), false)
})

test('a county with no districts becomes a partial guide on an archived election that covers the county', () => {
  const p = fromHash(comparisonHref(BASE, primaryEntry, general.election.id, liveGeneralContext, allGeneralAnswers))
  const ctx = reconcileContext(p.context, primary)
  assert.equal(ctx.coverageStatus, 'partial_county')
  assert.deepEqual(ctx.districts, {})
  assert.deepEqual(ctx.missingLayers, ['CITY', 'CONGDST', 'LEGDST', 'KCCDST', 'SCCDST', 'JUDDST', 'FIRDST', 'SCHDST'])
  assert.equal(ctx.districtsNotLookedUp, true)
  // Idempotent: the page rewrites its hash with this context and may reload.
  assert.deepEqual(reconcileContext(ctx, primary), ctx)

  // What the archived page then shows: statewide plus King countywide
  // contests, never a district-scoped one.
  const contests = contestsOnBallot(primary, ctx, scopeMatches)
  const measures = measuresOnBallot(primary, ctx, scopeMatches)
  assert.ok(contests.length > 0)
  for (const c of [...contests, ...measures]) assert.ok(['STATEWIDE', 'COUNTY'].includes(c.scope.kind))
  assert.ok(contests.some((c) => c.scope.kind === 'COUNTY'))
})

test('a payload carrying King districts keeps its full-county guide on the archived election', () => {
  const context = {
    coverageStatus: 'full_county',
    county: KING,
    districts: { CONGDST: '9', LEGDST: '37', KCCDST: '2', CITY: 'Seattle', SCCDST: 'SCC2', JUDDST: 'SE', SCHDST: 'Seattle', FIRDST: 'Seattle' },
    missingLayers: [],
    matched: 'x',
  }
  const p = fromHash(comparisonHref(BASE, primaryEntry, general.election.id, context, allGeneralAnswers))
  const ctx = reconcileContext(p.context, primary)
  assert.deepEqual(ctx, p.context)
  const contests = contestsOnBallot(primary, ctx, scopeMatches)
  assert.ok(contests.some((c) => c.scope.kind === 'DISTRICT' && c.scope.layer === 'LEGDST'))
})

test('a live King context from the general opens the primary as a full county guide', () => {
  // 11700 Pinehurst Way NE, Seattle, as the general's District Adapter
  // resolved it live on 2026-10-08.
  const context = {
    coverageStatus: 'full_county',
    county: KING,
    districts: { CONGDST: '7', LEGDST: '46', KCCDST: '1', SCCDST: 'SCC5', JUDDST: 'W', SCHDST: '1', CITY: 'Seattle' },
    missingLayers: [],
    matched: '11700 PINEHURST WAY NE, SEATTLE, WA, 98125',
  }
  assert.equal(comparisonTarget({ index, election: generalEntry, context, restored: null }), primaryEntry)
  const p = fromHash(comparisonHref(BASE, primaryEntry, general.election.id, context, allGeneralAnswers))
  const ctx = reconcileContext(p.context, primary)
  assert.equal(ctx.coverageStatus, 'full_county')
  assert.deepEqual(ctx.missingLayers, [])
  assert.equal(ctx.districtsNotLookedUp, undefined)
  const contests = contestsOnBallot(primary, ctx, scopeMatches)
  const district = contests.filter((c) => c.scope.kind === 'DISTRICT').map((c) => `${c.scope.layer}=${c.scope.value}`)
  for (const want of ['CONGDST=7', 'LEGDST=46']) assert.ok(district.includes(want), want)
  assert.ok(contests.some((c) => c.scope.kind === 'COUNTY'))
  assert.ok(measuresOnBallot(primary, ctx, scopeMatches).some((m) => m.scope.value === 'Seattle'))
})

test('reconcileContext leaves same-election contexts alone and never overclaims', () => {
  // A statewide-only link on the general, for a county the general does not
  // cover: unchanged.
  const yakima = { ...liveGeneralContext, county: { id: 'yakima', fips: '53077', name: 'Yakima County' } }
  assert.deepEqual(reconcileContext(yakima, general), yakima)
  // A King link made before King shipped in the general (#16) carries no
  // districts: it now reads as a partial King guide, never as full coverage.
  const old = reconcileContext(liveGeneralContext, general)
  assert.equal(old.coverageStatus, 'partial_county')
  assert.equal(old.districtsNotLookedUp, true)
  assert.ok(old.missingLayers.includes('CEMDST'))
  // A live King context on the general passes through unchanged.
  const live = {
    coverageStatus: 'full_county',
    county: KING,
    districts: { CONGDST: '7', LEGDST: '46', KCCDST: '1', SCCDST: 'SCC5', JUDDST: 'W', SCHDST: '1', CITY: 'Seattle' },
    missingLayers: [],
  }
  assert.deepEqual(reconcileContext(live, general), live)
  // A partial King link with a failed layer: unchanged.
  const partial = { coverageStatus: 'partial_county', county: KING, districts: { LEGDST: '43' }, missingLayers: ['CITY'] }
  assert.deepEqual(reconcileContext(partial, primary), partial)
  // A county-level claim against data that does not cover the county
  // degrades to statewide-only.
  const claimed = { coverageStatus: 'full_county', county: yakima.county, districts: { LEGDST: '15' }, missingLayers: [] }
  assert.equal(reconcileContext(claimed, general).coverageStatus, 'statewide_only')
})

test('comparison note for a voter who answered every general axis', () => {
  assert.equal(
    comparisonNote(primary, allGeneralAnswers, general.election.id),
    'Compared on 14 of 15 values you answered; the primary guide did not ask about ' +
      'Parents and public schools. Your “Gender, LGBTQ+ and reproductive policy” answer ' +
      'is used as-is for this guide’s “Social issues & schools” value.'
  )
})

test('comparison note: no note without a source election or when nothing differs', () => {
  // A plain primary link (no source election) never gets the note.
  assert.equal(comparisonNote(primary, allGeneralAnswers, undefined), null)
  assert.equal(comparisonNote(primary, allGeneralAnswers, primary.election.id), null)
  // N == M and no retitled axis answered.
  assert.equal(comparisonNote(primary, { taxes: { v: 1, w: 1 }, housing: { v: 1, w: 1 } }, general.election.id), null)
  // N == M but social answered: only the as-is sentence.
  assert.equal(
    comparisonNote(primary, { taxes: { v: 1, w: 1 }, social: { v: 1, w: 1 } }, general.election.id),
    'Your “Gender, LGBTQ+ and reproductive policy” answer is used as-is for this guide’s “Social issues & schools” value.'
  )
  // N < M without social.
  assert.equal(
    comparisonNote(primary, { taxes: { v: 1, w: 1 }, 'parental-rights': { v: 1, w: 1 } }, general.election.id),
    'Compared on 1 of 2 values you answered; the primary guide did not ask about Parents and public schools.'
  )
})

test('answersInRubric keeps only axes the served rubric defines', () => {
  const kept = answersInRubric(allGeneralAnswers, primary)
  assert.equal(Object.keys(kept).length, 14)
  assert.equal(kept['parental-rights'], undefined)
  assert.deepEqual(kept.social, allGeneralAnswers.social)
})

test('SOURCE_AXIS_TITLES covers every active axis an archived rubric lacks or titles differently', () => {
  const active = findElection(index, index.active)
  const activeData = readPublic(appDataPath(active))
  const titles = SOURCE_AXIS_TITLES[activeData.election.id] || {}
  const expected = {}
  for (const entry of index.elections.filter((e) => e.status === 'archived')) {
    const archived = readPublic(appDataPath(entry))
    for (const axis of activeData.rubric.axes) {
      const there = archived.rubric.axes.find((a) => a.id === axis.id)
      if (!there || there.title !== axis.title) expected[axis.id] = axis.title
    }
  }
  assert.deepEqual(titles, expected)
})
