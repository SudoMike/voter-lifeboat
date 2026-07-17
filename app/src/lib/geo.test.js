import test from 'node:test'
import assert from 'node:assert/strict'
import { scopeMatches } from './geo.js'

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
