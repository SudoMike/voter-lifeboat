import test from 'node:test'
import assert from 'node:assert/strict'
import { initials } from './initials.js'

test('Initials Portrait takes the first letter of the first and last tokens, uppercase', () => {
  assert.equal(initials('Colleen Melody'), 'CM')
  assert.equal(initials('mary alice heuschel'), 'MH')
  assert.equal(initials('Sean O’Donnell'), 'SO')
  assert.equal(initials('Mary-Alice Heuschel'), 'MH')
})

test('Initials Portrait ignores nicknames and generational suffixes', () => {
  assert.equal(initials('Sean "Tex" O\'Donnell'), 'SO')
  assert.equal(initials('Robert (Bob) Ferguson'), 'RF')
  assert.equal(initials('Martin Luther King Jr.'), 'MK')
  assert.equal(initials('John Smith III'), 'JS')
})

test('Initials Portrait handles one-word and empty names', () => {
  assert.equal(initials('Cher'), 'C')
  assert.equal(initials(''), '')
  assert.equal(initials(undefined), '')
  assert.equal(initials('  '), '')
})
