// The Ballot Brief: a plain-text packet the voter pastes into their own AI
// chat. Contains their values, their ballot's rankings, candidate summaries
// and sources. See ADR-0001 — this replaces any on-site chat.

import { rankContest, measureLean } from './scoring.js'

const PAMPHLET_URLS = {
  'king/edition-1':
    'https://cdn.kingcounty.gov/-/media/king-county/depts/elections/how-to-vote/voters-pamphlets/2026/08/english/edition-1.pdf',
  'king/edition-2':
    'https://cdn.kingcounty.gov/-/media/king-county/depts/elections/how-to-vote/voters-pamphlets/2026/08/english/edition-2.pdf',
  'clark/local-voters-pamphlet':
    'https://clark.wa.gov/sites/default/files/media/document/2026-06/2026clarkcountyprimaryvp_web.pdf',
  'kitsap/local-voters-pamphlet': 'https://www.kitsap.gov/auditor/Documents/LVP.pdf',
  'pierce/local-voters-pamphlet':
    'https://www.piercecountywa.gov/DocumentCenter/View/158538/Primary-2026-VP-Final',
  'snohomish/local-voters-pamphlet':
    'https://www.snohomishcountywa.gov/DocumentCenter/View/149774',
  'spokane/local-voters-pamphlet':
    'https://www.spokanecounty.gov/DocumentCenter/View/72507/August-4-2026-Primary-Election-Voters-Pamphlet-PDF',
  'thurston/local-voters-pamphlet': 'https://www.thurstoncountywa.gov/media/33642',
}

export function pamphletLink(pages, owner) {
  for (const p of pages || []) {
    const url = PAMPHLET_URLS[`${owner}/${p.edition}`] || PAMPHLET_URLS[`king/${p.edition}`]
    if (url) return `${url}#page=${p.page}`
  }
  return null
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

function coverageText(context) {
  if (context.coverageStatus === 'statewide_only') {
    return [
      'Coverage: STATEWIDE-ONLY GUIDE.',
      'This packet includes only Washington-wide contests currently covered by Voter Lifeboat. It omits county, city, school, fire, judicial district, and other local contests.',
    ]
  }
  if (context.coverageStatus === 'partial_county') {
    const lines = [
      'Coverage: PARTIAL COUNTY GUIDE.',
      'This packet includes statewide contests, countywide contests, and local contests whose district scope was resolved exactly. Some local contests may be missing because one or more district lookups failed or are not covered yet.',
    ]
    if (context.missingLayers?.length) {
      lines.push(
        `District lookups that did not resolve: ${context.missingLayers.join(', ')}. Races scoped to these districts are the ones to double-check against my official ballot.`
      )
    }
    return lines
  }
  return [
    'Coverage: FULL COUNTY GUIDE.',
    'This packet includes the contests Voter Lifeboat matched to the resolved ballot context for this supported county.',
  ]
}

export function buildBrief(data, context, answers, contests, measures, shareUrl, concerns) {
  const L = []
  L.push(`# MY BALLOT BRIEF — ${data.election?.scope || 'Washington State'}, ${data.election?.name || ''}`)
  L.push('')
  L.push(
    'I used Voter Lifeboat (an AI-built, citation-first voter guide; it makes no accuracy claims and tells users to verify via sources). Below are MY values from its interview, and how the covered candidates and measures scored against them.'
  )
  for (const line of coverageText(context)) L.push(line)
  if (context.county?.name) L.push(`Resolved county: ${context.county.name}`)
  L.push('')
  L.push('## MY VALUES (from the interview)')
  for (const [axis, { v, w }] of Object.entries(answers)) {
    const care = w >= 2 ? ' — I care A LOT about this' : w <= 0.5 ? ' — low priority for me' : ''
    L.push(`- ${axisName(data, axis)}: ${axisPoleLabel(data, axis, v)}${care}`)
  }
  L.push('')

  for (const contest of contests) {
    const { rows, tooClose } = rankContest(contest, answers)
    L.push(
      `## ${contest.office.toUpperCase()} — ${contest.district || (contest.scope?.kind === 'STATEWIDE' ? 'Statewide' : 'Countywide')}`
    )
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
      const pam = pamphletLink(c.pamphlet_pages, contest.owner)
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
      const pam = pamphletLink(m.pamphlet_pages, m.owner)
      if (pam) L.push(`Official pamphlet entry: ${pam}`)
    }
    L.push('')
  }

  L.push('---')
  L.push(`Regenerate this report anytime: ${shareUrl}`)
  L.push(
    'Method: candidates with completed dossiers were scored -2..+2 per issue axis by an AI pipeline reading official pamphlet statements, candidate websites, public records, endorsements and established news. Every score carries citations, an adversarial AI pass tried to refute each one, and low-confidence scores are excluded from matching. Some county candidates may be official-ballot-only entries with no computed score yet.'
  )
  L.push('')
  L.push('---')
  L.push('')
  L.push('## FIRST RESPONSE INSTRUCTIONS')
  L.push(
    'Do not generate the HTML report immediately. First, briefly welcome me, summarize what election data and coverage limits you have, and tell me you can generate the HTML report now if I want. Also tell me I can ask questions, add personal context, or refine my priorities before you generate the report. Wait for me to ask before producing the HTML report.'
  )
  L.push('')
  if (concerns?.trim()) {
    L.push('## MY QUESTIONS AND CONCERNS')
    L.push(concerns.trim())
    L.push('Address these directly and prominently in your report.')
    L.push('')
  }
  L.push(`## WHEN I ASK FOR THE HTML REPORT
Use these instructions only after I ask you to generate the report.

## YOUR RESEARCH
Search the web for every serious contender above: news coverage, endorsements, donor records, public statements, voting history where applicable. If you do NOT have web access, say so in a prominent banner at the top of the report and confine yourself to analyzing this brief's own contents — do not invent outside facts and do not fabricate links. Candidates marked "not enough evidence to score" are in scope: you may find evidence the pipeline didn't, and one of them may be the best pick. Also draw on whatever you already know about me from our past conversations — my circumstances, priorities, and how I think — to sharpen your verdicts.

## COVERAGE RULES
- Cover EVERY contested race on my ballot, each in its own section, with exactly ONE explicit pick per race. Skip uncontested races.
- The brief's rankings are one input, not the answer. Form your own recommendation from my values, your research, and what you know about me. Where your pick differs from the brief's top match, note the difference and why in a sentence or two — don't make the disagreement the story.
- Cover every ballot measure the same way: an explicit YES or NO recommendation. Where no lean was computed above, reason directly from my values.

## REPORT STRUCTURE — one self-contained HTML file
Match the REFERENCE DESIGN at the bottom of these instructions: a warm editorial layout — cream page, deep-navy masthead with decorative ballot-bubble circles, big tightly-tracked headlines, rounded card sections, and a candidate portrait beside every race. Reuse the reference stylesheet as your <style> and keep its class names; fill it with my actual races.
"Self-contained" means no external stylesheets, scripts, or web fonts (use the system font stack in the reference). Images ARE wanted, but every image MUST be embedded as a base64 data: URI — never hotlink a remote URL — so the single file works offline.
1. Masthead: title, election and date, my districts.
2. The no-web-access banner, if that applies.
3. "Verdicts at a glance", subtitled "What I recommend for each contested race": one small chip per race and measure — race, your pick, verdict color — each anchor-linked to its section below. Directly above the chips, a one-line legend spelling out what the two colors mean.
4. One section per race, in the same order as this brief, then the measures.
5. Closing: patterns you noticed across races (e.g. one of my values doing hidden work in the rankings) and questions back to me — only real ones; if none, say so in one line.
6. Footer: sources consulted, a reminder that I should verify against the linked sources before voting — the vote is mine, not yours or a tool's — and the regenerate link from the top of this brief.

## CANDIDATE PHOTOS — include a portrait for EVERY race
- Lay each race out as two columns: text on the left, a portrait of MY recommended candidate on the right (it stacks above the text on narrow screens). This is the feature I care most about — do not skip it.
- Find a real photo of that candidate from an official, campaign, party, or government page; fetch it and embed it as a base64 data: URI so the file stays self-contained. Add a small caption crediting the source page. A photo is an identity aid, never evidence of qualification — say so once in the glance subtitle and once in the footer.
- If you cannot find or reliably embed a real photo, DO NOT leave a gap: render the fallback "initials portrait" from the reference skeleton — an inline SVG in the same frame, navy background with the candidate's initials. For a ballot measure, use a simple inline-SVG illustration (see the reference measure example) instead of a portrait.
- The frame gets rounded corners and an offset shadow tinted to the race's verdict color; the reference CSS handles this via .candidate-photo — just add the clear/nuanced class to the race card.

## EACH RACE SECTION MUST CONTAIN
- Header: an eyebrow with the body/level, the office title, and one line on what the office does.
- A candidate portrait beside the text (see CANDIDATE PHOTOS), plus a few value-tag pills naming the values driving the pick.
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
- Be direct — I'd rather hear a hard truth now than regret a vote later.

## REFERENCE DESIGN — reproduce this look
Base your <style> on this stylesheet (use it as-is; adapt only where a race truly needs it) and follow the HTML skeleton's structure and class names. The skeleton is a TEMPLATE — replace every [bracketed placeholder] with my real races and drop the example rows; do not copy the sample content. Give each race card the class "clear" (seafoam) or "nuanced" (amber) to drive its accent, badge, and photo-shadow color.

----- REFERENCE STYLESHEET (put between <style> and </style>) -----
:root{
  --cream:#FBF5EA;
  --navy:#1B3A57;
  --seafoam:#5FB39F;
  --amber:#C69A3A;
  --paper:#fffaf2;
  --ink-soft:rgba(27,58,87,.72);
  --line:rgba(27,58,87,.14);
  --shadow:0 24px 70px rgba(27,58,87,.12);
  --radius-xl:34px;
  --radius-lg:24px;
  --radius-md:16px;
}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{
  margin:0;
  color:var(--navy);
  background:
    radial-gradient(circle at 12% 8%, rgba(95,179,159,.10), transparent 24rem),
    radial-gradient(circle at 88% 18%, rgba(198,154,58,.10), transparent 26rem),
    var(--cream);
  font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Inter,Roboto,Helvetica,Arial,sans-serif;
  font-size:17px;
  line-height:1.62;
  -webkit-font-smoothing:antialiased;
}
a{color:inherit;text-underline-offset:.2em;text-decoration-thickness:1px}
a:hover{text-decoration-thickness:2px}
.skip-link{position:absolute;left:-9999px;top:0}
.skip-link:focus{left:18px;top:18px;background:var(--cream);padding:10px 14px;border-radius:10px;z-index:100}
.wrap{width:min(1180px,calc(100% - 34px));margin:0 auto}
.masthead{
  position:relative;
  overflow:hidden;
  margin:24px auto 28px;
  min-height:590px;
  color:var(--cream);
  background:var(--navy);
  border-radius:42px;
  box-shadow:var(--shadow);
}
.masthead:before,.masthead:after{
  content:"";
  position:absolute;
  border-radius:999px;
  border:42px solid rgba(95,179,159,.28);
}
.masthead:before{width:430px;height:430px;right:-145px;top:-135px}
.masthead:after{width:245px;height:245px;right:165px;bottom:-155px;border-color:rgba(198,154,58,.38)}
.ballot-dots{
  position:absolute;inset:auto 52px 44px auto;
  display:grid;grid-template-columns:repeat(4,18px);gap:16px;
  opacity:.72
}
.ballot-dots i{width:18px;height:18px;border:3px solid var(--cream);border-radius:50%;display:block}
.ballot-dots i:nth-child(3n){background:var(--seafoam);border-color:var(--seafoam)}
.masthead-inner{position:relative;z-index:1;padding:72px 76px 66px;max-width:920px}
.kicker{font-size:.78rem;font-weight:800;letter-spacing:.16em;text-transform:uppercase;opacity:.76}
h1{font-size:clamp(3.15rem,7vw,6.9rem);line-height:.91;letter-spacing:-.055em;margin:.22em 0 .25em;max-width:850px}
.deck{max-width:720px;font-size:1.18rem;line-height:1.55;color:rgba(251,245,234,.82);margin:0 0 26px}
.districts{display:flex;flex-wrap:wrap;gap:10px}
.districts span{
  padding:8px 12px;border:1px solid rgba(251,245,234,.3);border-radius:999px;
  font-size:.78rem;font-weight:750;letter-spacing:.02em;background:rgba(251,245,234,.06)
}
.meta-line{margin-top:26px;font-size:.78rem;color:rgba(251,245,234,.6)}
.coverage{
  display:grid;grid-template-columns:1.1fr .9fr;gap:18px;margin:0 auto 28px
}
.note-card{
  background:rgba(255,250,242,.78);border:1px solid var(--line);border-radius:var(--radius-lg);
  padding:24px 26px;box-shadow:0 10px 35px rgba(27,58,87,.06);backdrop-filter:blur(8px)
}
.note-card strong{display:block;font-size:.78rem;text-transform:uppercase;letter-spacing:.12em;margin-bottom:5px}
.note-card p{margin:0;color:var(--ink-soft)}
.glance{
  scroll-margin-top:20px;
  background:var(--paper);border:1px solid var(--line);border-radius:var(--radius-xl);
  padding:38px;box-shadow:var(--shadow);margin-bottom:34px
}
.section-kicker{font-size:.75rem;font-weight:850;letter-spacing:.15em;text-transform:uppercase;color:var(--ink-soft)}
.glance h2{font-size:clamp(2rem,4vw,3.3rem);letter-spacing:-.045em;line-height:1.05;margin:.15em 0 .15em}
.subtitle{margin:0 0 20px;color:var(--ink-soft)}
.legend{display:flex;flex-wrap:wrap;gap:16px 26px;margin:20px 0 24px;padding:15px 18px;border:1px solid var(--line);border-radius:16px;background:var(--cream)}
.legend span{display:flex;align-items:center;gap:9px;font-size:.88rem}
.swatch{width:17px;height:17px;border-radius:5px;display:inline-block}
.swatch.clear{background:var(--seafoam)}
.swatch.nuanced{background:var(--amber)}
.chips{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px}
.verdict-chip{
  position:relative;display:flex;flex-direction:column;justify-content:space-between;min-height:116px;
  padding:17px 18px 15px;border-radius:18px;text-decoration:none;color:var(--navy);
  border:1px solid var(--line);background:var(--cream);overflow:hidden;transition:.18s ease
}
.verdict-chip:before{content:"";position:absolute;left:0;top:0;bottom:0;width:8px}
.verdict-chip.clear:before{background:var(--seafoam)}
.verdict-chip.nuanced:before{background:var(--amber)}
.verdict-chip:hover{transform:translateY(-2px);box-shadow:0 12px 28px rgba(27,58,87,.1)}
.chip-office{font-size:.73rem;line-height:1.35;text-transform:uppercase;letter-spacing:.06em;color:var(--ink-soft)}
.verdict-chip strong{font-size:1.05rem;line-height:1.15;padding-top:12px}
.race-card{
  position:relative;scroll-margin-top:18px;background:var(--paper);border:1px solid var(--line);
  border-radius:var(--radius-xl);padding:44px 44px 24px;margin:0 0 28px;box-shadow:0 15px 50px rgba(27,58,87,.075);
  overflow:hidden
}
.race-card:before{content:"";position:absolute;left:0;right:0;top:0;height:9px}
.race-card.clear:before{background:var(--seafoam)}
.race-card.nuanced:before{background:var(--amber)}
.race-number{
  position:absolute;right:30px;top:15px;font-size:4rem;font-weight:900;line-height:1;
  letter-spacing:-.08em;color:rgba(27,58,87,.055);user-select:none
}
.race-grid{display:grid;grid-template-columns:minmax(0,1fr) 250px;gap:42px;align-items:start}
.eyebrow{font-size:.74rem;font-weight:850;letter-spacing:.14em;text-transform:uppercase;color:var(--ink-soft);margin-bottom:8px}
.race-card h2{font-size:clamp(2rem,4.4vw,3.35rem);letter-spacing:-.045em;line-height:1.03;margin:0 0 12px;max-width:850px}
.role{font-size:.95rem;color:var(--ink-soft);max-width:820px;margin:0 0 22px}
.verdict-row{display:flex;align-items:center;flex-wrap:wrap;gap:10px;margin:18px 0 13px}
.verdict-badge{
  display:inline-flex;align-items:center;min-height:42px;border-radius:999px;padding:9px 15px;
  font-weight:900;font-size:.9rem;letter-spacing:.02em
}
.clear .verdict-badge{background:var(--seafoam)}
.nuanced .verdict-badge{background:var(--amber)}
.score{font-size:.78rem;font-weight:750;border:1px solid var(--line);padding:8px 11px;border-radius:999px;background:var(--cream)}
.value-tags{display:flex;flex-wrap:wrap;gap:7px;margin:0 0 18px}
.value-tag{font-size:.72rem;font-weight:800;letter-spacing:.035em;text-transform:uppercase;padding:5px 9px;border-radius:999px;border:1px solid var(--line);background:rgba(251,245,234,.72)}
.rationale{font-size:1.08rem;line-height:1.68;margin:0;max-width:830px}
.attention,.difference{
  margin-top:18px;padding:15px 17px;border-radius:15px;border:1px solid var(--line);
  background:var(--cream);font-size:.92rem;line-height:1.55
}
.attention{border-left:7px solid var(--amber)}
.difference{border-left:7px solid var(--navy)}
.candidate-photo,.measure-art{margin:0;position:relative}
.candidate-photo img{
  width:250px;height:282px;display:block;object-fit:cover;border-radius:26px;
  border:1px solid var(--line);box-shadow:0 16px 35px rgba(27,58,87,.14);background:var(--navy)
}
.candidate-photo:after{
  content:"";position:absolute;inset:12px -10px -10px 12px;border-radius:26px;z-index:-1;
}
.clear .candidate-photo:after{background:rgba(95,179,159,.32)}
.nuanced .candidate-photo:after{background:rgba(198,154,58,.30)}
figcaption{font-size:.68rem;line-height:1.35;color:var(--ink-soft);margin-top:12px}
.measure-art{color:var(--amber);padding:12px}
.measure-art svg{width:100%;height:auto;display:block}
details{margin-top:32px;border-top:1px solid var(--line);padding-top:4px}
summary{
  cursor:pointer;list-style:none;display:flex;align-items:center;justify-content:space-between;gap:16px;
  padding:18px 2px 12px;font-weight:850
}
summary::-webkit-details-marker{display:none}
summary:before{content:"+";display:inline-grid;place-items:center;width:28px;height:28px;border:1px solid var(--line);border-radius:50%;margin-right:10px;flex:none}
details[open] summary:before{content:"-"}
summary span:first-of-type{margin-right:auto}
.summary-hint{font-weight:600;color:var(--ink-soft);font-size:.78rem}
.evidence-grid{display:grid;grid-template-columns:1.18fr .82fr;gap:32px;padding:10px 0 8px}
.evidence-grid h3{font-size:.86rem;letter-spacing:.1em;text-transform:uppercase;margin:13px 0 13px}
.contender-list{display:grid;gap:10px}
.contender{padding:14px 15px;border:1px solid var(--line);border-radius:14px;background:var(--cream)}
.contender-name{font-weight:850;font-size:.9rem;margin-bottom:3px}
.contender p{font-size:.83rem;line-height:1.5;color:var(--ink-soft);margin:0}
.missed{padding-left:1.4em;margin:0}
.missed li{padding-left:.3em;margin-bottom:10px;font-size:.88rem}
.dig-title{margin-top:24px!important}
.source-links{list-style:none;padding:0;margin:0;display:grid;gap:7px}
.source-links a{display:flex;justify-content:space-between;gap:12px;padding:10px 12px;border:1px solid var(--line);border-radius:12px;text-decoration:none;font-size:.82rem;background:var(--cream)}
.source-links a:hover{border-color:var(--navy)}
.back-top{display:inline-block;margin-top:14px;font-size:.72rem;font-weight:800;text-decoration:none;color:var(--ink-soft)}
.closing{
  display:grid;grid-template-columns:1.25fr .75fr;gap:22px;margin:42px auto 28px
}
.closing-card{background:var(--navy);color:var(--cream);border-radius:var(--radius-xl);padding:38px;box-shadow:var(--shadow)}
.closing-card h2{font-size:2.5rem;letter-spacing:-.04em;line-height:1.04;margin:0 0 16px}
.closing-card p{color:rgba(251,245,234,.78)}
.patterns{display:grid;gap:13px;margin-top:22px}
.pattern{border-top:1px solid rgba(251,245,234,.2);padding-top:13px}
.pattern strong{display:block;margin-bottom:3px}
.question-card{background:var(--seafoam);border-radius:var(--radius-xl);padding:34px;color:var(--navy);box-shadow:var(--shadow)}
.question-card h3{font-size:1.4rem;line-height:1.15;margin:0 0 12px}
.question-card p{margin:0}
footer{
  background:var(--paper);border:1px solid var(--line);border-radius:var(--radius-xl) var(--radius-xl) 0 0;
  padding:34px 38px 44px;margin-top:28px
}
footer h2{font-size:1.05rem;margin:0 0 10px}
.footer-grid{display:grid;grid-template-columns:1fr 1fr;gap:32px}
footer p,footer li{font-size:.8rem;line-height:1.55;color:var(--ink-soft)}
footer ul{margin:0;padding-left:1.2em}
.disclaimer{margin-top:24px;padding-top:20px;border-top:1px solid var(--line);font-weight:750;color:var(--navy)}
.regenerate{word-break:break-all}
@media(max-width:900px){
  .masthead-inner{padding:54px 38px}
  .coverage,.closing,.footer-grid{grid-template-columns:1fr}
  .chips{grid-template-columns:repeat(2,minmax(0,1fr))}
  .race-grid{grid-template-columns:1fr}
  .candidate-photo img{width:100%;height:min(70vw,390px)}
  .candidate-photo{order:-1;max-width:520px}
  .evidence-grid{grid-template-columns:1fr}
}
@media(max-width:620px){
  body{font-size:16px}
  .wrap{width:min(100% - 20px,1180px)}
  .masthead{margin-top:10px;border-radius:28px;min-height:540px}
  .masthead-inner{padding:44px 24px 40px}
  h1{font-size:3.45rem}
  .glance,.race-card,.closing-card,.question-card,footer{border-radius:24px;padding:26px 21px}
  .chips{grid-template-columns:1fr}
  .race-number{font-size:3rem}
  .summary-hint{display:none}
}
@media print{
  body{background:white;font-size:10.5pt}
  .wrap{width:100%;max-width:none}
  .masthead{min-height:auto;border-radius:0;margin:0;box-shadow:none}
  .masthead-inner{padding:36px}
  .coverage,.glance,.race-card,.closing-card,.question-card,footer{box-shadow:none;break-inside:avoid}
  .verdict-chip:hover{transform:none}
  details{display:block}
  details:not([open]) > *:not(summary){display:block}
  summary{display:none}
  .back-top{display:none}
  a{color:inherit;text-decoration:none}
}

----- REFERENCE HTML SKELETON (fill placeholders with my races) -----
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="light">
<title>My [County] Ballot Brief — [election date]</title>
<style>/* the REFERENCE STYLESHEET above goes here */</style>
</head>
<body>
<a class="skip-link" href="#glance">Skip to verdicts</a>

<header class="masthead wrap">
  <div class="masthead-inner">
    <div class="kicker">Independent recommendation · researched [date]</div>
    <h1>My [County]<br>Ballot Brief</h1>
    <p class="deck">[Election name] · [date]. [one-line description of the guide].</p>
    <div class="districts" aria-label="Resolved districts"><span>[District]</span><span>[District]</span></div>
    <div class="meta-line">[levels covered: statewide · countywide · legislative · local]</div>
  </div>
  <div class="ballot-dots" aria-hidden="true"><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i></div>
</header>

<div class="wrap">
  <section class="coverage" aria-label="Coverage and method">
    <div class="note-card"><strong>Coverage</strong><p>[what this guide does and does not cover].</p></div>
    <div class="note-card"><strong>Decision rule</strong><p>Match scores are inputs, not verdicts. Office competence, philosophical fit, evidence quality, and role-specific red flags can override a higher score.</p></div>
  </section>

  <section id="glance" class="glance">
    <div class="section-kicker">Verdicts at a glance</div>
    <h2>What I recommend for each contested race</h2>
    <p class="subtitle">Candidate photos are identity aids, not evidence. Open any race for the full red-flag check and sources.</p>
    <div class="legend" aria-label="Verdict color legend">
      <span><i class="swatch clear"></i><strong>Seafoam:</strong> clear winner - fill the bubble and move on.</span>
      <span><i class="swatch nuanced"></i><strong>Amber:</strong> nuance, thin evidence, or a caveat - read before deciding.</span>
    </div>
    <nav class="chips" aria-label="Recommendations">
      <a class="verdict-chip clear" href="#race-1"><span class="chip-office">[Office]</span><strong>[My pick]</strong></a>
      <a class="verdict-chip nuanced" href="#race-2"><span class="chip-office">[Office]</span><strong>[My pick]</strong></a>
    </nav>
  </section>

  <main>
    <article id="race-1" class="race-card clear" aria-labelledby="race-1-title">
      <div class="race-number">01</div>
      <div class="race-grid">
        <div class="race-main">
          <div class="eyebrow">[Body / level]</div>
          <h2 id="race-1-title">[Office title]</h2>
          <p class="role">[what this office does].</p>
          <div class="verdict-row"><span class="verdict-badge">MY PICK: [name]</span><span class="score">Brief match: [n]/100</span></div>
          <div class="value-tags"><span class="value-tag">[value]</span><span class="value-tag">[value]</span></div>
          <p class="rationale">[2-3 sentences tied to my values].</p>
          <!-- amber races only: <div class="attention"><strong>Why this is amber:</strong> [what to read for].</div> -->
          <!-- if your pick differs from the brief: <div class="difference"><strong>Where I differ from the brief:</strong> [why].</div> -->
        </div>
        <figure class="candidate-photo">
          <img src="data:image/jpeg;base64,[EMBED REAL PHOTO HERE]" alt="[name]" width="250" height="282">
          <figcaption>Photo: <a href="[source page]" target="_blank" rel="noopener noreferrer">[source name]</a></figcaption>
        </figure>
        <!-- NO reliable photo? Replace the <img> above with this initials-portrait fallback:
        <svg viewBox="0 0 800 800" width="250" height="282" role="img" aria-label="[name]" style="display:block;border-radius:26px">
          <rect width="800" height="800" rx="96" fill="#1B3A57"/>
          <circle cx="400" cy="340" r="190" fill="#FBF5EA" opacity=".11"/>
          <path d="M160 750c28-164 112-246 240-246s212 82 240 246" fill="#FBF5EA" opacity=".11"/>
          <text x="400" y="455" text-anchor="middle" font-family="Arial, sans-serif" font-size="210" font-weight="800" fill="#FBF5EA">[INITIALS]</text>
        </svg>
        ...and change the figcaption to note it is an initials portrait. -->
      </div>
      <details>
        <summary><span>Show the evidence</span><span class="summary-hint">contenders · caveats · sources</span></summary>
        <div class="evidence-grid">
          <section>
            <h3>Red-flag check</h3>
            <div class="contender-list">
              <div class="contender"><div class="contender-name">[contender]</div><p>[red-flag note - explicit even when clean].</p></div>
            </div>
          </section>
          <section>
            <h3>What the brief may have missed</h3>
            <ol class="missed"><li>[point].</li></ol>
            <h3 class="dig-title">Dig deeper</h3>
            <ul class="source-links"><li><a href="[verified url]" target="_blank" rel="noopener noreferrer"><span>[label]</span><span>&#8599;</span></a></li></ul>
          </section>
        </div>
      </details>
      <a class="back-top" href="#glance">Back to verdicts &#8593;</a>
    </article>

    <!-- Ballot measure: same card, but swap the photo figure for a measure illustration -->
    <article id="measure-1" class="race-card nuanced" aria-labelledby="measure-1-title">
      <div class="race-number">02</div>
      <div class="race-grid">
        <div class="race-main">
          <div class="eyebrow">[Jurisdiction]</div>
          <h2 id="measure-1-title">[Measure title]</h2>
          <p class="role">[what it does].</p>
          <div class="verdict-row"><span class="verdict-badge">MY PICK: YES</span><span class="score">Brief: leans YES</span></div>
          <p class="rationale">[reasoning from my values].</p>
        </div>
        <figure class="measure-art" aria-label="Stylized illustration">
          <svg viewBox="0 0 420 320" role="img" aria-hidden="true"><!-- a simple relevant line-art illustration in currentColor --></svg>
          <figcaption>Measure illustration</figcaption>
        </figure>
      </div>
      <details>
        <summary><span>Show the evidence</span><span class="summary-hint">yes case · no case · sources</span></summary>
        <div class="evidence-grid">
          <section><h3>The case</h3><div class="contender-list"><div class="contender"><div class="contender-name">YES case</div><p>[...].</p></div><div class="contender"><div class="contender-name">NO case</div><p>[...].</p></div></div></section>
          <section><h3>What the brief may have missed</h3><ol class="missed"><li>[point].</li></ol><h3 class="dig-title">Dig deeper</h3><ul class="source-links"><li><a href="[verified url]" target="_blank" rel="noopener noreferrer"><span>[label]</span><span>&#8599;</span></a></li></ul></section>
        </div>
      </details>
      <a class="back-top" href="#glance">Back to verdicts &#8593;</a>
    </article>
  </main>

  <section class="closing">
    <div class="closing-card">
      <div class="section-kicker" style="color:rgba(251,245,234,.65)">Patterns across the ballot</div>
      <h2>[one-line headline of the strongest pattern].</h2>
      <p>[short paragraph].</p>
      <div class="patterns"><div class="pattern"><strong>[pattern].</strong> [detail].</div></div>
    </div>
    <aside class="question-card">
      <h3>One real calibration question</h3>
      <p>[a genuine question back to me - or say plainly there is not one].</p>
    </aside>
  </section>

  <footer>
    <div class="footer-grid">
      <section><h2>Sources consulted</h2><ul><li>[sources].</li></ul></section>
      <section><h2>Use this correctly</h2><p>Verify the linked sources before voting. This report is an argument, not an authority: the vote is mine, not a tool's.</p><p>Photos were embedded from official, campaign, party, or government pages where a clear source was available. No photo was used as evidence of qualification.</p></section>
    </div>
    <p class="disclaimer">Regenerate the underlying Voter Lifeboat brief: <a class="regenerate" href="[regenerate link from the top of this brief]">[link]</a></p>
  </footer>
</div>
</body>
</html>`)
  return L.join('\n')
}
