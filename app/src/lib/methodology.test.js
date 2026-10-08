import test from 'node:test'
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { rubricNotes, ELECTION_RULES } from './methodology.js'

const appData = (id) =>
  JSON.parse(readFileSync(new URL(`../../public/data/${id}/app-data.json`, import.meta.url), 'utf8'))

test('the general rubric gets the split, parental-rights scope and overlap notes', () => {
  const data = appData('2026-11-03-general')
  const notes = rubricNotes(data.rubric, data.election.id)
  assert.equal(data.rubric.axes.length, 15)
  assert.equal(notes.split, true)
  assert.deepEqual(notes.parentalRights, {
    scored: 'state legislative contests and ballot measures',
    notScored: 'federal, county and city',
  })
  assert.equal(notes.localControlOverlap, true)
  assert.deepEqual(notes.rules.map((r) => r.id), ['taxes-single-vote'])
})

test('the archived primary keeps its own rubric and shows none of the general notes', () => {
  const data = appData('2026-08-04-primary')
  const notes = rubricNotes(data.rubric, data.election.id)
  assert.equal(notes.split, false)
  assert.equal(notes.parentalRights, null)
  assert.equal(notes.localControlOverlap, false)
  assert.deepEqual(notes.rules, [])
})

test('election rules are keyed by app-data election ids that ship', () => {
  const index = JSON.parse(
    readFileSync(new URL('../../public/data/elections.json', import.meta.url), 'utf8'),
  )
  const appIds = new Set(index.elections.map((e) => e.app_id))
  for (const id of Object.keys(ELECTION_RULES)) assert.ok(appIds.has(id), id)
})

test('a rule is dropped when its axis is not in the rubric', () => {
  const notes = rubricNotes({ axes: [{ id: 'social' }] }, '2026-11-03-general')
  assert.deepEqual(notes.rules, [])
  assert.equal(rubricNotes(null).split, false)
})
