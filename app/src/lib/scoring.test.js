import test from 'node:test'
import assert from 'node:assert/strict'
import {
  alignCandidate,
  rankContest,
  measureLean,
  buildProfile,
  axesForBallot,
  NOISE_MARGIN,
} from './scoring.js'

const cand = (scores, extra = {}) => ({
  scores: Object.fromEntries(
    Object.entries(scores).map(([axis, score]) => [axis, { score, confidence: 'high' }])
  ),
  ...extra,
})

test('a perfect two-axis match still shrinks toward neutral', () => {
  const answers = { a: { v: 2, w: 1 }, b: { v: -2, w: 1 } }
  const { score } = alignCandidate(cand({ a: 2, b: -2 }), answers, 2)
  // (2*1 + 4*0.5) / (2 + 4) = 0.666… → 67, not 100: thin evidence can't max out.
  assert.equal(score, 67)
  assert.ok(score < 100)
})

test('withdrawn candidates and thin evidence never get scores', () => {
  const answers = { a: { v: 1, w: 1 }, b: { v: 1, w: 1 } }
  assert.equal(alignCandidate(cand({ a: 1, b: 1 }, { withdrawn: true }), answers, 2).score, null)
  assert.equal(alignCandidate(cand({ a: 1 }), answers, 2).reason, 'insufficient-data')
})

test('low-confidence scores are excluded from alignment', () => {
  const answers = { a: { v: 2, w: 1 }, b: { v: 2, w: 1 } }
  const c = {
    scores: {
      a: { score: 2, confidence: 'high' },
      b: { score: -2, confidence: 'low' },
    },
  }
  assert.equal(alignCandidate(c, answers, 1).reason, 'insufficient-data')
})

test('rankContest orders scored candidates first and flags too-close calls', () => {
  const answers = { a: { v: 2, w: 1 }, b: { v: 2, w: 1 } }
  const contest = {
    candidates: [
      cand({ a: -2, b: -2 }, { name: 'far' }),
      { name: 'unscored', scores: {} },
      cand({ a: 2, b: 2 }, { name: 'near' }),
    ],
  }
  const { rows, tooClose } = rankContest(contest, answers)
  assert.equal(rows[0].cand.name, 'near')
  assert.equal(rows[2].cand.name, 'unscored')
  assert.equal(tooClose, false)
  const close = {
    candidates: [cand({ a: 2, b: 2 }), cand({ a: 2, b: 1.5 })],
  }
  const r2 = rankContest(close, answers)
  assert.ok(r2.rows[0].score - r2.rows[1].score <= NOISE_MARGIN)
  assert.equal(r2.tooClose, true)
})

test('measureLean maps weighted agreement to yes/no/split', () => {
  const measure = { lean_mappings: { taxes: { direction: 2 } } }
  assert.equal(measureLean(measure, { taxes: { v: 2, w: 1 } }).lean, 'yes')
  assert.equal(measureLean(measure, { taxes: { v: -2, w: 1 } }).lean, 'no')
  assert.equal(measureLean(measure, { taxes: { v: 0.2, w: 1 } }).lean, 'split')
  assert.equal(measureLean(measure, { housing: { v: 2, w: 1 } }).lean, null)
})

test('buildProfile averages statement and trade-off contributions per axis', () => {
  const statement = { kind: 'statement', axis: 'a', value: 2 }
  const tradeoff = { kind: 'tradeoff', options: [{ effects: { a: -2, b: 1 } }] }
  const answers = buildProfile(
    [
      { item: statement, choice: 'agree' },
      { item: tradeoff, choice: 0 },
      { item: statement, choice: null }, // skipped: no contribution
    ],
    { a: 2 }
  )
  assert.deepEqual(answers.a, { v: 0, w: 2 })
  assert.deepEqual(answers.b, { v: 1, w: 1 })
})

test('axesForBallot unions candidate score axes and measure lean axes', () => {
  const contests = [{ candidates: [cand({ a: 1 })] }]
  const measures = [{ lean_mappings: { b: { direction: 2 } } }]
  assert.deepEqual([...axesForBallot({}, contests, measures)].sort(), ['a', 'b'])
})
