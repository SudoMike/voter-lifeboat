import test from 'node:test'
import assert from 'node:assert/strict'
import { shouldRecordReport } from './reports.js'

const active = { id: '2026-11-03-general', status: 'active' }
const archived = { id: '2026-08-04-primary', status: 'archived' }

test('a fresh report on the active election is recorded', () => {
  assert.equal(shouldRecordReport({ election: active, restored: null }), true)
})

test('a report someone shared is never recorded again', () => {
  assert.equal(shouldRecordReport({ election: active, restored: { answers: {} } }), false)
})

test('a fresh report on an archived election is not recorded', () => {
  assert.equal(shouldRecordReport({ election: archived, restored: null }), false)
})
