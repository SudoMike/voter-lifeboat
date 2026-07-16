// The Ballot Brief: a plain-text packet the voter pastes into their own AI
// chat. Contains their values, their ballot's rankings, candidate summaries
// and sources. See ADR-0001 — this replaces any on-site chat.

import { rankContest, measureLean } from './scoring.js'

const PAMPHLET_URLS = {
  'edition-1':
    'https://cdn.kingcounty.gov/-/media/king-county/depts/elections/how-to-vote/voters-pamphlets/2026/08/english/edition-1.pdf',
  'edition-2':
    'https://cdn.kingcounty.gov/-/media/king-county/depts/elections/how-to-vote/voters-pamphlets/2026/08/english/edition-2.pdf',
}

export function pamphletLink(pages) {
  if (!pages?.length) return null
  const p = pages[0]
  return `${PAMPHLET_URLS[p.edition]}#page=${p.page}`
}

function axisName(data, id) {
  return data.rubric.axes.find((a) => a.id === id)?.title || id
}

function axisPoleLabel(data, id, v) {
  const ax = data.rubric.axes.find((a) => a.id === id)
  if (!ax) return ''
  if (Math.abs(v) < 0.75) return 'mixed / in between'
  const pole = v < 0 ? ax.pole_a : ax.pole_b
  return `${v <= -1.5 || v >= 1.5 ? 'strongly ' : 'leans '}"${pole.label}"`
}

export function buildBrief(data, answers, contests, measures, shareUrl, concerns) {
  const L = []
  L.push('# MY BALLOT BRIEF — King County Primary, August 4, 2026')
  L.push('')
  L.push(
    'I used Voter Lifeboat (an AI-built, citation-first voter guide; it makes no accuracy claims and tells users to verify via sources). Below are MY values from its interview, and how the candidates and measures on MY ballot scored against them. Please act as my thinking partner: challenge my matches, point out what the summaries might miss, and help me decide. Ask me questions where my values seem ambiguous.'
  )
  L.push('')
  L.push('## MY VALUES (from the interview)')
  for (const [axis, { v, w }] of Object.entries(answers)) {
    const care = w >= 2 ? ' — I care A LOT about this' : w <= 0.5 ? ' — low priority for me' : ''
    L.push(`- ${axisName(data, axis)}: ${axisPoleLabel(data, axis, v)}${care}`)
  }
  L.push('')

  for (const contest of contests) {
    const { rows, tooClose } = rankContest(contest, answers)
    L.push(`## ${contest.office.toUpperCase()} — ${contest.district || 'Countywide'}`)
    if (contest.office_does) L.push(`(${contest.office_does})`)
    if (contest.uncontested) L.push('Uncontested — shown for information only.')
    if (tooClose)
      L.push(
        'NOTE: my top two scores here are within the noise margin — genuinely too close to call.'
      )
    for (const r of rows) {
      const c = r.cand
      const head =
        r.score != null
          ? `${r.score}/100 match`
          : c.withdrawn
            ? 'WITHDRAWN after pamphlet printing'
            : 'not enough evidence to score'
      L.push(`### ${c.name}${c.party ? ` (${c.party})` : ''} — ${head} [evidence: ${c.evidence_level}]`)
      if (c.summary) L.push(c.summary)
      for (const h of c.highlights || []) L.push(`- ${h}`)
      const urls = (c.sources || [])
        .map((s) => s.url)
        .filter(Boolean)
        .slice(0, 5)
      if (urls.length) L.push(`Sources: ${urls.join(' · ')}`)
      const pam = pamphletLink(c.pamphlet_pages)
      if (pam) L.push(`Official pamphlet statement: ${pam}`)
    }
    L.push('')
  }

  if (measures.length) {
    L.push('## BALLOT MEASURES')
    for (const m of measures) {
      const { lean } = measureLean(m, answers)
      const leanTxt =
        lean === 'yes'
          ? 'leans YES for me'
          : lean === 'no'
            ? 'leans NO for me'
            : lean === 'split'
              ? 'genuinely split for me'
              : 'no lean computed (my interview did not map cleanly onto it)'
      L.push(`### ${m.jurisdiction} ${m.proposition}: ${m.title} — ${leanTxt}`)
      if (m.what_it_does) L.push(m.what_it_does)
      if (m.cost_line) L.push(`Cost: ${m.cost_line}`)
      if (m.pro_summary) L.push(`Pro: ${m.pro_summary}`)
      if (m.con_summary) L.push(`Con: ${m.con_summary}`)
    }
    L.push('')
  }

  L.push('---')
  L.push(`Regenerate this report anytime: ${shareUrl}`)
  L.push(
    'Method: candidates were scored -2..+2 per issue axis by an AI pipeline reading official pamphlet statements, candidate websites, public records, endorsements and established news — every score carries citations, an adversarial AI pass tried to refute each one, and low-confidence scores are excluded from matching.'
  )
  L.push('')
  L.push('---')
  L.push('')
  L.push(
    'Now that you have my Ballot Brief above, act as my personal election advisor and go deeper on the candidates recommended for me, before I vote.'
  )
  L.push('')
  if (concerns?.trim()) {
    L.push('## MY QUESTIONS AND CONCERNS')
    L.push(concerns.trim())
    L.push('Address these directly and prominently in your report.')
    L.push('')
  }
  L.push(
    'Using my values above and whatever you can find on these specific candidates (news coverage, endorsements, donor records, public statements, voting history where applicable), write me a supplementary report. For each recommended candidate:'
  )
  L.push('- A quick verdict: how well do they actually fit my values?')
  L.push(
    '- A red-flag check: anything extremist (in any direction), scandal-adjacent, or sharply at odds with their campaign rhetoric?'
  )
  L.push('- 2–3 things the summaries above may have missed or understated')
  L.push('- Your honest bottom line — would you recommend I vote for them?')
  L.push('')
  L.push(
    "Output a nicely-formatted HTML report. Use color panels, verdict badges, and highlights so it's easy to scan. Be direct — I'd rather hear a hard truth now than regret a vote later."
  )
  return L.join('\n')
}
