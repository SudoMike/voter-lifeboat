import test from 'node:test'
import assert from 'node:assert/strict'
import { lookupBallotContext, scopeMatches } from './geo.js'

const kingContext = {
  coverageStatus: 'full_county',
  county: { id: 'king', fips: '53033', name: 'King County' },
  districts: { LEGDST: '43', CONGDST: '7' },
}

test('STATEWIDE scopes match any Washington ballot context', () => {
  assert.equal(scopeMatches({ kind: 'STATEWIDE' }, { county: { id: null }, districts: {} }), true)
})

test('COUNTY scopes require matching county id', () => {
  assert.equal(scopeMatches({ kind: 'COUNTY', county: 'king' }, kingContext), true)
  assert.equal(scopeMatches({ kind: 'COUNTY', county: 'pierce' }, kingContext), false)
})

test('DISTRICT scopes require county, layer, and value match', () => {
  assert.equal(scopeMatches({ kind: 'DISTRICT', county: 'king', layer: 'LEGDST', value: '43' }, kingContext), true)
  assert.equal(scopeMatches({ kind: 'DISTRICT', county: 'king', layer: 'LEGDST', value: '37' }, kingContext), false)
  assert.equal(scopeMatches({ kind: 'DISTRICT', county: 'pierce', layer: 'LEGDST', value: '43' }, kingContext), false)
})

function mockGeocode(match) {
  global.fetch = async () => ({
    ok: true,
    async json() {
      return { result: { addressMatches: [match] } }
    },
  })
}

test('unsupported Washington counties receive statewide-only fallback when statewide data is complete', async () => {
  mockGeocode({
    matchedAddress: '3000 PACIFIC AVE SE, OLYMPIA, WA, 98501',
    coordinates: { x: -122.83, y: 47.03 },
    geographies: {
      Counties: [{ STATE: '53', COUNTY: '067', NAME: 'Thurston County' }],
    },
  })
  const context = await lookupBallotContext(
    { coverage: { statewide_complete: true, supported_counties: [{ id: 'king' }] } },
    '3000 Pacific Ave SE Olympia WA 98501'
  )
  assert.equal(context.coverageStatus, 'statewide_only')
  assert.equal(context.county.id, 'thurston')
})

test('supported non-King counties use Census federal/state districts as partial coverage', async () => {
  mockGeocode({
    matchedAddress: '3000 ROCKEFELLER AVE, EVERETT, WA, 98201',
    coordinates: { x: -122.2, y: 48 },
    geographies: {
      Counties: [{ STATE: '53', COUNTY: '061', NAME: 'Snohomish County' }],
      '119th Congressional Districts': [{ BASENAME: '2' }],
      '2024 State Legislative Districts - Lower': [{ BASENAME: '38' }],
      '2024 State Legislative Districts - Upper': [{ BASENAME: '38' }],
    },
  })
  const context = await lookupBallotContext(
    { coverage: { statewide_complete: true, supported_counties: [{ id: 'king' }, { id: 'snohomish' }] } },
    '3000 Rockefeller Ave Everett WA 98201'
  )
  assert.equal(context.coverageStatus, 'partial_county')
  assert.deepEqual(context.districts, { CONGDST: '2', LEGDST: '38' })
  assert.deepEqual(context.missingLayers, ['county-local'])
})
