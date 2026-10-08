import test from 'node:test'
import assert from 'node:assert/strict'
import { activeAppDataPath, loadActiveAppData } from './elections.js'

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
