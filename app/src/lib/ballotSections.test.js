// Ballot Sections (#40): the Report and the Ballot Brief group a Covered
// Ballot the way a Washington ballot lists it. These run against the shipped
// general and the archived primary so a new pipeline category cannot vanish.
import test from 'node:test'
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { ballotSections, sectionOf, SECTION_ORDER } from './ballotSections.js'
import { scopeMatches } from './geo.js'
import { contestsOnBallot, measuresOnBallot } from './scoring.js'

const load = (id) =>
  JSON.parse(readFileSync(new URL(`../../public/data/${id}/app-data.json`, import.meta.url), 'utf8'))
const general = load('2026-11-03-general')
const primary = load('2026-08-04-primary')

const KING = { id: 'king', fips: '53033', name: 'King County' }
const WHATCOM = { id: 'whatcom', fips: '53073', name: 'Whatcom County' }

// A Seattle voter in CD 7, LD 46 and King County Council district 4, with no
// city, court or school district resolved.
const seattle = { coverageStatus: 'full_county', county: KING, districts: { CONGDST: '7', LEGDST: '46', KCCDST: '4' }, missingLayers: [] }
// A Washington address in no shipped county: the Statewide-Only Guide.
const statewide = { coverageStatus: 'statewide_only', county: { id: 'test-unshipped', fips: '53999', name: 'Test County' }, districts: {}, missingLayers: [] }
// Whatcom's countywide ballot carries port and PUD commissioner seats.
const whatcom = { coverageStatus: 'full_county', county: WHATCOM, districts: {}, missingLayers: [] }

const sectionsFor = (data, context) =>
  ballotSections(contestsOnBallot(data, context, scopeMatches), measuresOnBallot(data, context, scopeMatches))

const counts = (sections) =>
  Object.fromEntries(sections.map((s) => [s.name, s.contests.length + s.measures.length]))

test('sections follow Washington ballot order', () => {
  assert.deepEqual(SECTION_ORDER, ['Measures', 'Federal', 'State', 'Courts', 'County', 'Local'])
})

test('every pipeline category maps to one section; an unknown category lands in Local', () => {
  assert.equal(sectionOf({ category: 'Federal' }), 'Federal')
  assert.equal(sectionOf({ category: 'State' }), 'State')
  for (const category of ['StateSupremeCourt', 'CourtOfAppeals', 'DistrictCourt', 'Judicial'])
    assert.equal(sectionOf({ category }), 'Courts', category)
  assert.equal(sectionOf({ category: 'County' }), 'County')
  for (const category of ['City', 'Port', 'PublicUtility', 'Local'])
    assert.equal(sectionOf({ category }), 'Local', category)
  // A category the pipeline adds later must still show on the Report.
  assert.equal(sectionOf({ category: 'SchoolBoard' }), 'Local')
  assert.equal(sectionOf({}), 'Local')
})

test('the Seattle sample yields Measures 3, Federal 1, State 3, Courts 7, County 4 and no Local card', () => {
  const sections = sectionsFor(general, seattle)
  assert.deepEqual(
    sections.map((s) => s.name),
    ['Measures', 'Federal', 'State', 'Courts', 'County']
  )
  assert.deepEqual(counts(sections), { Measures: 3, Federal: 1, State: 3, Courts: 7, County: 4 })
  const measures = sections[0]
  assert.equal(measures.contests.length, 0)
  assert.equal(measures.measures.length, 3)
  for (const s of sections.slice(1)) assert.equal(s.measures.length, 0, s.name)
})

test('a Statewide-Only Guide has only Measures and Courts in the general', () => {
  assert.deepEqual(counts(sectionsFor(general, statewide)), { Measures: 3, Courts: 5 })
})

test('a county with port or PUD seats gets a Local card', () => {
  const sections = sectionsFor(general, whatcom)
  const local = sections.find((s) => s.name === 'Local')
  assert.ok(local, 'Whatcom has a Local section')
  assert.ok(local.contests.every((c) => ['Port', 'PublicUtility', 'City', 'Local'].includes(c.category)))
  assert.ok(local.contests.some((c) => c.category === 'Port'))
  assert.ok(local.contests.some((c) => c.category === 'PublicUtility'))
})

test('every contest and measure on any ballot lands in exactly one section, in ballot order', () => {
  for (const data of [general, primary]) {
    const sections = ballotSections(data.contests, data.measures)
    const names = sections.map((s) => s.name)
    assert.deepEqual(names, SECTION_ORDER.filter((n) => names.includes(n)))
    const placed = sections.flatMap((s) => [...s.contests, ...s.measures])
    assert.equal(placed.length, data.contests.length + data.measures.length)
    assert.equal(new Set(placed).size, placed.length)
    for (const c of data.contests) assert.ok(SECTION_ORDER.includes(sectionOf(c)), c.slug)
  }
})

test('empty sections are left out and input order is kept within a section', () => {
  const a = { slug: 'a', category: 'State' }
  const b = { slug: 'b', category: 'Federal' }
  const c = { slug: 'c', category: 'State' }
  assert.deepEqual(ballotSections([a, b, c], []), [
    { name: 'Federal', contests: [b], measures: [] },
    { name: 'State', contests: [a, c], measures: [] },
  ])
  assert.deepEqual(ballotSections([], []), [])
})
