// Deterministic client-side alignment math. See ADR-0001: all AI work
// happened offline; this file is transparent arithmetic over static data.

// answers: { axisId: { v: -2..2, w: 0.5|1|2 } }

export function contestsOnBallot(data, districts, matches) {
  return data.contests.filter((c) => matches(c.scope, districts))
}

export function measuresOnBallot(data, districts, matches) {
  return data.measures.filter((m) => matches(m.scope, districts))
}

// Which axes matter for a given ballot (drives the adaptive interview).
export function axesForBallot(data, contests, measures) {
  const wanted = new Set()
  for (const c of contests) {
    for (const cand of c.candidates) {
      for (const axis of Object.keys(cand.scores || {})) wanted.add(axis)
    }
  }
  for (const m of measures) {
    for (const axis of Object.keys(m.lean_mappings || {})) wanted.add(axis)
  }
  return wanted
}

export function interviewItemsForBallot(data, axes) {
  return data.interview.items.filter((item) => {
    if (item.kind === 'statement') return axes.has(item.axis)
    return item.options.some((o) => Object.keys(o.effects).some((a) => axes.has(a)))
  })
}

// Fold raw per-item responses into a Values Profile.
// responses: [{item, choice}] where choice = 'agree'|'disagree'|optionIndex
// weights: {axis: weight} from care pulses
export function buildProfile(responses, weights) {
  const contribs = {}
  for (const { item, choice } of responses) {
    if (choice == null) continue
    if (item.kind === 'statement') {
      const v = choice === 'agree' ? item.value : -item.value
      ;(contribs[item.axis] ||= []).push(v)
    } else {
      const opt = item.options[choice]
      for (const [axis, v] of Object.entries(opt.effects)) {
        ;(contribs[axis] ||= []).push(v)
      }
    }
  }
  const answers = {}
  for (const [axis, vs] of Object.entries(contribs)) {
    const mean = vs.reduce((a, b) => a + b, 0) / vs.length
    answers[axis] = { v: Math.max(-2, Math.min(2, mean)), w: weights[axis] ?? 1 }
  }
  return answers
}

const MIN_SHARED_AXES = 2
export const NOISE_MARGIN = 5 // alignment points

// Shrinkage: a score computed from few shared axes is pulled toward neutral
// (50) as if K unanswered pseudo-axes sat at 0.5 similarity. Without this, a
// candidate scored on 3 axes can hit a perfect 100 and out-rank a candidate
// honestly scored on 10 — false precision from thin evidence.
const SHRINK_K = 4
export const LOW_COVERAGE = 0.5 // < half the voter's answered, applicable axes

export function alignCandidate(candidate, answers, applicableAnswered) {
  if (candidate.withdrawn) return { score: null, shared: [], reason: 'withdrawn' }
  const shared = []
  for (const [axis, s] of Object.entries(candidate.scores || {})) {
    if (s.confidence === 'low') continue
    if (answers[axis] == null) continue
    shared.push(axis)
  }
  if (shared.length < MIN_SHARED_AXES) {
    return { score: null, shared, reason: 'insufficient-data' }
  }
  let num = 0
  let den = 0
  for (const axis of shared) {
    const { v, w } = answers[axis]
    const c = candidate.scores[axis].score
    const sim = 1 - Math.abs(v - c) / 4
    num += w * sim
    den += w
  }
  const score = Math.round(((num + SHRINK_K * 0.5) / (den + SHRINK_K)) * 100)
  const coverage = applicableAnswered ? shared.length / applicableAnswered : 1
  return { score, shared, coverage, reason: null }
}

export function rankContest(contest, answers) {
  // axes any candidate in this contest is scored on, that the voter answered
  const contestAxes = new Set()
  for (const cand of contest.candidates) {
    for (const [axis, s] of Object.entries(cand.scores || {})) {
      if (s.confidence !== 'low' && answers[axis] != null) contestAxes.add(axis)
    }
  }
  const applicableAnswered = contestAxes.size
  const rows = contest.candidates.map((cand) => ({
    cand,
    ...alignCandidate(cand, answers, applicableAnswered),
  }))
  rows.sort((a, b) => {
    if (a.score == null && b.score == null) return 0
    if (a.score == null) return 1
    if (b.score == null) return -1
    return b.score - a.score
  })
  const scored = rows.filter((r) => r.score != null)
  const tooClose =
    scored.length >= 2 && scored[0].score - scored[1].score <= NOISE_MARGIN
  return { rows, tooClose }
}

// Measures: lean of a YES vote given the profile.
export function measureLean(measure, answers) {
  let num = 0
  let den = 0
  const used = []
  for (const [axis, m] of Object.entries(measure.lean_mappings || {})) {
    const a = answers[axis]
    if (!a) continue
    // agreement of voter position with what a YES vote aligns to, in [-1, 1]
    num += a.w * ((a.v * m.direction) / 4)
    den += a.w
    used.push(axis)
  }
  if (!den || !used.length) return { lean: null, used }
  const L = num / den
  if (L >= 0.25) return { lean: 'yes', used }
  if (L <= -0.25) return { lean: 'no', used }
  return { lean: 'split', used }
}

export function axisMatchVerdict(v, c) {
  const d = Math.abs(v - c)
  if (d <= 1) return { label: 'strong match', cls: 'axis-verdict--match', partial: false }
  if (d <= 2) return { label: 'match', cls: 'axis-verdict--match', partial: false }
  if (d <= 3) return { label: 'partial', cls: 'axis-verdict--partial', partial: true }
  return { label: 'differs', cls: 'axis-verdict--partial', partial: true }
}

export const pct = (x) => `${((x + 2) / 4) * 100}%`
