import test from 'node:test'
import assert from 'node:assert/strict'
import {
  activeAppDataPath,
  loadActiveAppData,
  electionIdFromPath,
  loadElection,
  ElectionNotFound,
  formatElectionDay,
  ballotsMailBy,
  archivedElections,
  electionHref,
  guideLinkText,
} from './elections.js'

const index = {
  active: '2026-08-04-primary',
  elections: [{ id: '2026-08-04-primary', status: 'active' }],
}

test('active app data lives under the active election id', () => {
  assert.equal(activeAppDataPath(index), 'data/2026-08-04-primary/app-data.json')
})

test('an active id missing from the elections list is rejected', () => {
  assert.throws(() => activeAppDataPath({ active: 'nope', elections: index.elections }))
  assert.throws(() => activeAppDataPath({ elections: index.elections }))
})

test('loads the index first, then the active election file', async () => {
  const requested = []
  const fakeFetch = async (url) => {
    requested.push(url)
    const body = url.endsWith('elections.json') ? index : { election: { id: 'x' } }
    return { ok: true, json: async () => body }
  }
  const data = await loadActiveAppData('/washington-state/', fakeFetch)
  assert.deepEqual(requested, [
    '/washington-state/data/elections.json',
    '/washington-state/data/2026-08-04-primary/app-data.json',
  ])
  assert.deepEqual(data, { election: { id: 'x' } })
})

test('a failed fetch surfaces the HTTP status', async () => {
  const fakeFetch = async () => ({ ok: false, status: 404 })
  await assert.rejects(loadActiveAppData('/', fakeFetch), /data 404/)
})

const BASE = '/washington-state/'

test('the bare scope route names no election (the active one is served)', () => {
  assert.equal(electionIdFromPath('/washington-state', BASE), null)
  assert.equal(electionIdFromPath('/washington-state/', BASE), null)
})

test('a sub-route names the election to serve', () => {
  assert.equal(electionIdFromPath('/washington-state/2026-08-04-primary', BASE), '2026-08-04-primary')
  assert.equal(electionIdFromPath('/washington-state/2026-08-04-primary/', BASE), '2026-08-04-primary')
})

test('paths outside the scope name no election', () => {
  assert.equal(electionIdFromPath('/', BASE), null)
  assert.equal(electionIdFromPath('/elsewhere/x', BASE), null)
})

// Two elections, the way the index looks after the general goes active. The
// primary's app id differs from its package id; report links carry the app id.
const twoElections = {
  active: '2026-11-03-general',
  elections: [
    { id: '2026-08-04-primary', app_id: '2026-08-04-primary-special', status: 'archived' },
    { id: '2026-11-03-general', app_id: '2026-11-03-general', status: 'active' },
  ],
}

function fakeSite(files) {
  const requested = []
  const fetchImpl = async (url) => {
    requested.push(url)
    const path = url.slice(BASE.length)
    if (path === 'data/elections.json') return { ok: true, status: 200, json: async () => twoElections }
    if (!(path in files)) return { ok: false, status: 404 }
    return { ok: true, status: 200, json: async () => files[path] }
  }
  return { fetchImpl, requested }
}

const primaryData = { election: { id: '2026-08-04-primary-special' } }
const generalData = { election: { id: '2026-11-03-general' } }
const siteFiles = {
  'data/2026-08-04-primary/app-data.json': primaryData,
  'data/2026-11-03-general/app-data.json': generalData,
}

test('with no route and no report link, the active election loads', async () => {
  const { fetchImpl } = fakeSite(siteFiles)
  const got = await loadElection(BASE, {}, fetchImpl)
  assert.equal(got.election.id, '2026-11-03-general')
  assert.deepEqual(got.data, generalData)
  assert.equal(got.index, twoElections)
})

test('a route id loads that election, archived or not', async () => {
  const { fetchImpl } = fakeSite(siteFiles)
  const got = await loadElection(BASE, { routeId: '2026-08-04-primary' }, fetchImpl)
  assert.equal(got.election.status, 'archived')
  assert.deepEqual(got.data, primaryData)
})

test('an unknown route id is a clear "no such election", fetched no data file', async () => {
  const { fetchImpl, requested } = fakeSite(siteFiles)
  await assert.rejects(
    loadElection(BASE, { routeId: 'nope' }, fetchImpl),
    (e) => e instanceof ElectionNotFound && e.electionId === 'nope'
  )
  assert.deepEqual(requested, ['/washington-state/data/elections.json'])
})

test("an old report link's app id selects its election, not the active one", async () => {
  const { fetchImpl } = fakeSite(siteFiles)
  const got = await loadElection(BASE, { linkElectionId: '2026-08-04-primary-special' }, fetchImpl)
  assert.equal(got.election.id, '2026-08-04-primary')
  assert.deepEqual(got.data, primaryData)
})

test('a report link may also name an election by package id', async () => {
  const { fetchImpl } = fakeSite(siteFiles)
  const got = await loadElection(BASE, { linkElectionId: '2026-08-04-primary' }, fetchImpl)
  assert.equal(got.election.id, '2026-08-04-primary')
})

test('a report link naming an unlisted election falls back to the active one', async () => {
  const { fetchImpl } = fakeSite(siteFiles)
  const got = await loadElection(BASE, { linkElectionId: '2024-11-05-general' }, fetchImpl)
  assert.equal(got.election.id, '2026-11-03-general')
})

test('a listed election whose file is missing is "no such election", not a parse error', async () => {
  const { fetchImpl } = fakeSite({ 'data/2026-11-03-general/app-data.json': generalData })
  await assert.rejects(
    loadElection(BASE, { routeId: '2026-08-04-primary' }, fetchImpl),
    (e) => e instanceof ElectionNotFound && e.electionId === '2026-08-04-primary'
  )
})

test('election days read as long dates', () => {
  assert.equal(formatElectionDay('2026-08-04'), 'August 4, 2026')
  assert.equal(formatElectionDay('2026-11-03'), 'November 3, 2026')
})

test('ballots mail 18 days before election day (RCW 29A.40.070)', () => {
  assert.equal(ballotsMailBy('2026-11-03'), 'Oct 16')
  assert.equal(ballotsMailBy('2026-08-04'), 'Jul 17')
})

test('archived elections are listed newest first, linking to their own route', () => {
  const index = {
    active: 'c',
    elections: [
      { id: '2025-08-05-primary', day: '2025-08-05', status: 'archived' },
      { id: '2026-08-04-primary', day: '2026-08-04', status: 'archived' },
      { id: '2026-11-03-general', day: '2026-11-03', status: 'active' },
    ],
  }
  assert.deepEqual(archivedElections(index).map((e) => e.id), ['2026-08-04-primary', '2025-08-05-primary'])
  assert.equal(electionHref(BASE, index.elections[1]), '/washington-state/2026-08-04-primary')
  assert.equal(guideLinkText(index.elections[1]), 'Explore the August primary guide')
})

test('an HTML fallback page served for a data file is "no such election"', async () => {
  const fetchImpl = async (url) =>
    url.endsWith('elections.json')
      ? { ok: true, status: 200, json: async () => twoElections }
      : { ok: true, status: 200, json: async () => JSON.parse('<!doctype html>') }
  await assert.rejects(
    loadElection(BASE, { routeId: '2026-08-04-primary' }, fetchImpl),
    (e) => e instanceof ElectionNotFound
  )
})
