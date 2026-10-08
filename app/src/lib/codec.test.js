import test from 'node:test'
import assert from 'node:assert/strict'
import { decodeProfile, encodeProfile } from './codec.js'
import { loadElection } from './elections.js'

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

const b64url = (s) => btoa(s).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '')

test('crafted links cannot inject out-of-range weights or values', () => {
  const payload = {
    s: 2,
    c: { coverageStatus: 'full_county', county: { id: 'king' }, districts: {} },
    a: { housing: [40, -9], taxes: [-1, 999] },
  }
  const decoded = decodeProfile(b64url(JSON.stringify(payload)))
  assert.deepEqual(decoded.answers.housing, { v: 2, w: 0 })
  assert.deepEqual(decoded.answers.taxes, { v: -1, w: 4 })
})

test('unknown coverage status degrades to partial_county instead of overclaiming', () => {
  const payload = {
    s: 2,
    c: { coverageStatus: 'totally_bogus', county: { id: 'king' }, districts: {} },
    a: { housing: [1, 1] },
  }
  const decoded = decodeProfile(b64url(JSON.stringify(payload)))
  assert.equal(decoded.context.coverageStatus, 'partial_county')
})

test('legacy p.d links still decode as full-county King reports', () => {
  const payload = { s: 1, a: { housing: [1, 1] }, d: { LEGDST: '43' } }
  const decoded = decodeProfile(b64url(JSON.stringify(payload)))
  assert.equal(decoded.context.county.id, 'king')
  assert.deepEqual(decoded.districts, { LEGDST: '43' })
})

test('a primary report link renders against the primary after the general goes active', async () => {
  const primary = { data_version: '5204e0a', election: { id: '2026-08-04-primary-special' } }
  const general = { data_version: 'later', election: { id: '2026-11-03-general' } }
  const index = {
    active: '2026-11-03-general',
    elections: [
      { id: '2026-08-04-primary', app_id: '2026-08-04-primary-special', status: 'archived' },
      { id: '2026-11-03-general', app_id: '2026-11-03-general', status: 'active' },
    ],
  }
  const files = {
    '/washington-state/data/elections.json': index,
    '/washington-state/data/2026-08-04-primary/app-data.json': primary,
    '/washington-state/data/2026-11-03-general/app-data.json': general,
  }
  const fetchImpl = async (url) => ({
    ok: url in files,
    status: url in files ? 200 : 404,
    json: async () => files[url],
  })

  const link = encodeProfile(primary, { coverageStatus: 'statewide_only', districts: {} }, { taxes: { v: 1, w: 2 } })
  const decoded = decodeProfile(link)
  const got = await loadElection('/washington-state/', { linkElectionId: decoded.electionId }, fetchImpl)

  assert.equal(got.election.id, '2026-08-04-primary')
  assert.equal(got.election.status, 'archived')
  assert.equal(got.data, primary)
  // Same election and data version as the link: no data-changed banner.
  assert.equal(decoded.electionId, got.data.election.id)
  assert.equal(decoded.dataVersion, got.data.data_version)
})
