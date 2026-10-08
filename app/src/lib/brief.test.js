import test from 'node:test'
import assert from 'node:assert/strict'
import { buildBrief } from './brief.js'

const data = {
  election: { scope: 'Washington State', name: 'August 4, 2026 Primary and Special Election' },
  rubric: {
    axes: [
      { id: 'judicial', title: 'Judicial restraint', pole_a: { label: 'Restraint' }, pole_b: { label: 'Access' } },
    ],
  },
}

test('Ballot Brief starts in orientation mode and includes coverage warning', () => {
  const text = buildBrief(
    data,
    { coverageStatus: 'statewide_only', county: { name: 'Pierce County' }, districts: {} },
    { judicial: { v: 1, w: 1 } },
    [],
    [],
    'https://example.test/washington-state#p=abc',
    ''
  )
  assert.match(text, /Coverage: STATEWIDE-ONLY GUIDE/)
  assert.match(text, /Do not generate the HTML report immediately/)
  assert.match(text, /Wait for me to ask before producing the HTML report/)
  assert.match(text, /WHEN I ASK FOR THE HTML REPORT/)
})

test('Ballot Brief header and coverage warning name the loaded election and its day', () => {
  const general = {
    ...data,
    election: { id: '2026-11-03-general', scope: 'Washington State', name: 'November 3, 2026 General Election', day: '2026-11-03' },
  }
  const text = buildBrief(
    general,
    { coverageStatus: 'statewide_only', county: { name: 'Pierce County' }, districts: {} },
    { judicial: { v: 1, w: 1 } },
    [],
    [],
    'https://example.test/washington-state#p=abc',
    ''
  )
  assert.match(text, /^# MY BALLOT BRIEF — Washington State, November 3, 2026 General Election$/m)
  assert.match(text, /^Election day: Tuesday, November 3, 2026\.$/m)
  assert.match(text, /only the statewide contests on the November 3, 2026 General Election ballot/)
})

test('Ballot Brief prints a contest term when the data carries one', () => {
  const contest = {
    slug: 'x', office: 'Supreme Court', district: 'Justice Position No. 1', term: '2-year unexpired term',
    scope: { kind: 'STATEWIDE' }, candidates: [],
  }
  const text = buildBrief(
    data,
    { coverageStatus: 'statewide_only', county: { name: 'Pierce County' }, districts: {} },
    { judicial: { v: 1, w: 1 } },
    [contest],
    [],
    'https://example.test/',
    ''
  )
  assert.match(text, /## SUPREME COURT — Justice Position No\. 1\nTerm: 2-year unexpired term/)
})

test('Ballot Brief names unresolved district lookups in words, not layer ids', () => {
  const text = buildBrief(
    data,
    { coverageStatus: 'partial_county', county: { name: 'King County' }, districts: {}, missingLayers: ['KCCDST', 'SCCDST', 'JUDDST'] },
    { judicial: { v: 1, w: 1 } },
    [],
    [],
    'https://example.test/',
    ''
  )
  assert.match(
    text,
    /District lookups that did not resolve: King County Council District, Seattle City Council District, King County District Court Electoral District\./
  )
  assert.doesNotMatch(text, /KCCDST|SCCDST|JUDDST/)
})
