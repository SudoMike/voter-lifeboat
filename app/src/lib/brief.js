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
    'Now that you have my Ballot Brief above, act as my personal election advisor and write me a supplementary report before I vote.'
  )
  L.push('')
  if (concerns?.trim()) {
    L.push('## MY QUESTIONS AND CONCERNS')
    L.push(concerns.trim())
    L.push('Address these directly and prominently in your report.')
    L.push('')
  }
  L.push(`## YOUR RESEARCH
Search the web for every serious contender above: news coverage, endorsements, donor records, public statements, voting history where applicable. If you do NOT have web access, say so in a prominent banner at the top of the report and confine yourself to analyzing this brief's own contents — do not invent outside facts and do not fabricate links. Candidates marked "not enough evidence to score" are in scope: you may find evidence the pipeline didn't, and one of them may be the best pick. Also draw on whatever you already know about me from our past conversations — my circumstances, priorities, and how I think — to sharpen your verdicts.

## COVERAGE RULES
- Cover EVERY contested race on my ballot, each in its own section, with exactly ONE explicit pick per race. Skip uncontested races.
- The brief's rankings are one input, not the answer. Form your own recommendation from my values, your research, and what you know about me. Where your pick differs from the brief's top match, note the difference and why in a sentence or two — don't make the disagreement the story.
- Cover every ballot measure the same way: an explicit YES or NO recommendation. Where no lean was computed above, reason directly from my values.

## REPORT STRUCTURE — one self-contained HTML file (no external fonts, scripts, images, or stylesheets)
1. Masthead: title, election and date, my districts.
2. The no-web-access banner, if that applies.
3. "Verdicts at a glance", subtitled "What I recommend for each contested race": one small chip per race and measure — race, your pick, verdict color — each anchor-linked to its section below. Directly above the chips, a one-line legend spelling out what the two colors mean.
4. One section per race, in the same order as this brief, then the measures.
5. Closing: patterns you noticed across races (e.g. one of my values doing hidden work in the rankings) and questions back to me — only real ones; if none, say so in one line.
6. Footer: sources consulted, a reminder that I should verify against the linked sources before voting — the vote is mine, not yours or a tool's — and the regenerate link from the top of this brief.

## EACH RACE SECTION MUST CONTAIN
- Header: the office and what it does.
- A colored verdict badge: "MY PICK: [name]", with the brief's match score beside it.
- A 2–3 sentence rationale tied to MY values.
- A red-flag check covering all serious contenders, not just your pick — explicit even when clean ("nothing concerning surfaced").
- If your pick differs from the brief's top match: a brief note saying so and why.
- 1–3 things the brief's summaries may have missed or understated.
- 2–4 links to dig deeper on the candidates discussed — only links you verified exist.

## PRESENTATION
- Exactly TWO verdict colors, signaling how much of my attention a race needs — nothing else (not party, not agreement with the brief). Seafoam green #5FB39F = clear winner: confident pick — fill in the bubble and move on. Amber #C69A3A = some nuance I might want to look at: a close call, thin evidence, a caveat, or a red flag on a contender — read before deciding. Use these on badges, chips, and section accents, and never leave their meaning implicit — the legend in the glance section is the decoder. Cream #FBF5EA page background, navy #1B3A57 text, matching the Voter Lifeboat site. Friendly rounded sans-serif, system font stack.
- Do NOT overwhelm me — no walls of text. Default view per race = badge, pick, and gist; put the evidence bullets, full red-flag detail, and "what the brief missed" inside native <details>/<summary> toggles ("show the evidence").
- Depth proportional to the verdict: a green race should take ~30 seconds to read; spend your words where my decision could actually change. An amber race with a serious red flag may show more detail by default.
- Link liberally: chips to sections, cross-references between related races, external sources inline.
- Be direct — I'd rather hear a hard truth now than regret a vote later.`)
  return L.join('\n')
}
