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
