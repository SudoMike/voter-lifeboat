import test from 'node:test'
import assert from 'node:assert/strict'
import { decodeProfile, encodeProfile } from './codec.js'

test('profile payload round-trips derived location state without street address', () => {
  const data = {
    data_version: 'abc123',
    election: { id: '2026-08-04-primary-special' },
  }
  const context = {
    coverageStatus: 'full_county',
    county: { id: 'king', fips: '53033', name: 'King County' },
    districts: { LEGDST: '43' },
    matched: '4218 SW Othello St, Seattle, WA',
  }
  const encoded = encodeProfile(data, context, { housing: { v: 1, w: 2 } })
  const decoded = decodeProfile(encoded)
  assert.equal(decoded.dataVersion, 'abc123')
  assert.equal(decoded.electionId, '2026-08-04-primary-special')
  assert.deepEqual(decoded.context.districts, { LEGDST: '43' })
  assert.equal(decoded.context.matched, undefined)
  assert.equal(JSON.stringify(decoded).includes('Othello'), false)
})
