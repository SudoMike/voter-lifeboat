import React, { useEffect, useMemo, useRef, useState } from 'react'
import { scopeMatches } from '../lib/geo.js'
import {
  contestsOnBallot,
  measuresOnBallot,
  rankContest,
  measureLean,
  axisMatchVerdict,
  pct,
  LOW_COVERAGE,
} from '../lib/scoring.js'
import { writeHash } from '../lib/codec.js'
import { buildBrief, pamphletLink } from '../lib/brief.js'

const EVIDENCE = {
  rich: { marks: '◆◆◆', cls: 'evidence--rich', label: 'Rich record' },
  moderate: { marks: '◆◆◇', cls: 'evidence--mod', label: 'Moderate record' },
  'pamphlet-only': { marks: '◆◇◇', cls: 'evidence--thin', label: 'Pamphlet only — take with sea salt' },
}

function postFeedback(payload) {
  return fetch('/api/feedback', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
}

// Fire-and-forget: record this report (answers + districts, never an address)
// into the public dataset. See /api/report in server.js and the #data page.
function postReport(dataVersion, districts, answers) {
  const a = {}
  for (const [axis, { v, w }] of Object.entries(answers)) a[axis] = [v, w]
  fetch('/api/report', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ v: dataVersion, districts, answers: a }),
  }).catch(() => {})
}

function ReportButton({ contest, candidate }) {
  const [open, setOpen] = useState(false)
  const [msg, setMsg] = useState('')
  const [state, setState] = useState(null) // 'sent' | 'error'
  if (state === 'sent')
    return <span style={{ fontSize: 11.5, fontWeight: 800, color: 'var(--seafoam-deep)' }}>✓ report sent — thank you</span>
  if (!open)
    return (
      <button className="report" onClick={() => setOpen(true)}>
        ⚑ report an error
      </button>
    )
  return (
    <div className="report-form" style={{ width: '100%' }}>
      <div style={{ fontSize: 12, fontWeight: 800 }}>
        What's wrong{candidate ? ` about ${candidate}` : ''}?
      </div>
      <textarea
        className="field"
        rows={2}
        style={{ marginTop: 6 }}
        value={msg}
        onChange={(e) => setMsg(e.target.value)}
        placeholder="A score, a citation, a fact…"
      />
      {state === 'error' && (
        <div style={{ fontSize: 11.5, fontWeight: 700, color: 'var(--coral-deep)', marginTop: 4 }}>
          Couldn't send — try again in a moment.
        </div>
      )}
      <div style={{ display: 'flex', gap: 8, marginTop: 8 }}>
        <button
          className="btn btn--navy btn--xs"
          onClick={() =>
            postFeedback({ kind: 'error-report', contest, candidate, message: msg })
              .then((r) => setState(r.ok ? 'sent' : 'error'))
              .catch(() => setState('error'))
          }
        >
          Send
        </button>
        <button className="linkish" style={{ fontSize: 12 }} onClick={() => setOpen(false)}>
          cancel
        </button>
      </div>
    </div>
  )
}

function SourceLine({ s }) {
  const label = s.outlet || s.type || 'source'
  const detail = s.ref || s.url || ''
  return (
    <div className="source-line">
      <span className="tier-tag">T{s.tier}</span>
      <strong>{s.id}</strong> · {label}
      {' — '}
      {s.url ? (
        <a href={s.url} target="_blank" rel="noopener noreferrer">
          {s.url.replace(/^https?:\/\/(www\.)?/, '').slice(0, 60)}
        </a>
      ) : (
        detail
      )}
    </div>
  )
}

function CandidateExpanded({ data, contest, row, answers }) {
  const c = row.cand
  const srcById = Object.fromEntries((c.sources || []).map((s) => [s.id, s]))
  const axes = Object.entries(c.scores || {})
    .filter(([axis]) => answers[axis])
    .sort((a, b) => answers[b[0]].w - answers[a[0]].w)
  const pam = pamphletLink(c.pamphlet_pages)
  return (
    <div className="race-expand rise">
      {c.summary && (
        <p className="copy" style={{ fontSize: 13, marginBottom: 12 }}>
          {c.summary}
        </p>
      )}
      {c.evidence_level === 'pamphlet-only' && (
        <div className="pamphlet-warn" style={{ marginBottom: 12 }}>
          All we have is their pamphlet statement — little or no record, no
          coverage. Any score here is a rough read, drawn with a wide brush.{' '}
          {pam && (
            <a className="cite" style={{ color: 'var(--amber-ink)' }} href={pam} target="_blank" rel="noopener noreferrer">
              Read the pamphlet →
            </a>
          )}
        </div>
      )}
      {axes.length > 0 && (
        <div className="stack" style={{ gap: 14 }}>
          {axes.map(([axisId, s]) => {
            const ax = data.rubric.axes.find((a) => a.id === axisId)
            const you = answers[axisId].v
            const verdict = axisMatchVerdict(you, s.score)
            const cites = (s.citations || []).map((id) => srcById[id]).filter(Boolean)
            return (
              <div key={axisId}>
                <div className="axis-head">
                  <span>{ax?.title || axisId}</span>
                  <span className={verdict.cls}>
                    {verdict.label}
                    {s.confidence === 'medium' ? ' · med. confidence' : ''}
                  </span>
                </div>
                <div className="axis-track">
                  <div className={`axis-dot${verdict.partial ? ' axis-dot--partial' : ''}`} style={{ left: pct(s.score) }} />
                  <div className="axis-you" style={{ left: pct(you) }} />
                </div>
                <div className="axis-scale">
                  <span>{ax?.pole_a.label.toLowerCase()}</span>
                  <span className="you">◆ you</span>
                  <span>{ax?.pole_b.label.toLowerCase()}</span>
                </div>
                <div className="axis-note">
                  {s.basis}{' '}
                  {cites.map((src) =>
                    src.url ? (
                      <a key={src.id} className="cite" href={src.url} target="_blank" rel="noopener noreferrer">
                        {src.outlet || src.type || src.id}
                      </a>
                    ) : (
                      <span key={src.id} className="cite" title={src.ref || src.type}>
                        {src.id === 'S1' || src.type === 'pamphlet' ? 'pamphlet' : src.id}
                      </span>
                    )
                  ).reduce((acc, el, i) => (i ? [...acc, ' · ', el] : [el]), [])}
                </div>
              </div>
            )
          })}
        </div>
      )}
      {(c.highlights || []).length > 0 && (
        <div style={{ marginTop: 14 }}>
          <div className="eyebrow eyebrow--sm eyebrow--muted">FROM THE RESEARCH</div>
          <ul style={{ margin: '6px 0 0', paddingLeft: 18 }}>
            {c.highlights.map((h, i) => (
              <li key={i} className="copy" style={{ fontSize: 12.5, marginBottom: 4 }}>
                {h}
              </li>
            ))}
          </ul>
        </div>
      )}
      <div
        style={{
          marginTop: 16, paddingTop: 12, borderTop: '2px dashed var(--sand)',
          display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: 10, flexWrap: 'wrap',
        }}
      >
        <details className="sources-list" style={{ flex: 1, minWidth: 200 }}>
          <summary>All {(c.sources || []).length} sources →</summary>
          <div style={{ marginTop: 8, display: 'flex', flexDirection: 'column', gap: 4 }}>
            {(c.sources || []).map((s) => (
              <SourceLine key={s.id} s={s} />
            ))}
            {pam && (
              <div className="source-line">
                <span className="tier-tag">T1</span>
                <strong>pamphlet</strong> ·{' '}
                <a href={pam} target="_blank" rel="noopener noreferrer">
                  official statement (PDF)
                </a>
              </div>
            )}
          </div>
        </details>
        <ReportButton contest={contest.slug} candidate={c.name} />
      </div>
    </div>
  )
}

function ContestCard({ data, contest, answers }) {
  const [openSlug, setOpenSlug] = useState(null)
  const { rows, tooClose } = rankContest(contest, answers)

  if (contest.uncontested) {
    const c = contest.candidates[0]
    return (
      <section className="panel panel--sand" style={{ margin: '12px 20px 0' }}>
        <div className="eyebrow eyebrow--sm eyebrow--muted">
          {contest.office.toUpperCase()} · {(contest.district || 'COUNTYWIDE').toUpperCase()}
        </div>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: 2 }}>
          <div style={{ fontWeight: 800, fontSize: 15 }}>{c.name}</div>
          <div style={{ fontSize: 12, fontWeight: 800, color: 'var(--muted)' }}>uncontested · info only</div>
        </div>
        {c.summary && (
          <p className="copy" style={{ fontSize: 12.5, marginTop: 6 }}>
            {c.summary}
          </p>
        )}
      </section>
    )
  }

  return (
    <section className="card" style={{ margin: '16px 20px 0', overflow: 'hidden' }}>
      <div style={{ padding: '14px 18px 10px', borderBottom: '2px dashed var(--sand)' }}>
        <div className="eyebrow eyebrow--sm">
          {contest.office.toUpperCase()} · {(contest.district || 'COUNTYWIDE').toUpperCase()}
        </div>
        {contest.office_does && (
          <div className="note" style={{ marginTop: 3, fontSize: 11.5 }}>
            {contest.office_does}
          </div>
        )}
      </div>
      {tooClose && (
        <div className="banner-tcc" style={{ margin: '12px 14px 0' }}>
          ⚖ Too close to call — your top two are within our margin of noise. Honestly, it's a coin flip.
        </div>
      )}
      {rows.map((r, i) => {
        const c = r.cand
        const ev = EVIDENCE[c.evidence_level] || EVIDENCE.moderate
        const open = openSlug === c.slug
        const last = i === rows.length - 1
        return (
          <React.Fragment key={c.slug}>
            <button
              className={`cand${c.withdrawn ? ' cand--withdrawn' : ''}`}
              style={{ padding: `${i === 0 ? 13 : 9}px 18px ${last && !open ? 16 : 6}px` }}
              onClick={() => setOpenSlug(open ? null : c.slug)}
            >
              {c.withdrawn ? (
                <div className="gauge--dashed">—</div>
              ) : r.score == null ? (
                <div className="gauge--dashed">?</div>
              ) : c.evidence_level === 'pamphlet-only' || r.coverage < LOW_COVERAGE ? (
                <div className="gauge--dashed">{r.score}</div>
              ) : (
                <div className={`gauge${r.score < 60 ? ' gauge--low' : ''}`} style={{ '--pct': `${r.score}%` }}>
                  <b>{r.score}</b>
                </div>
              )}
              <div style={{ flex: 1 }}>
                <div className={`cand-name${r.score != null && r.score < 60 ? ' cand-name--dim' : ''}`}>
                  {c.name}{' '}
                  {c.withdrawn && <span className="withdrawn-tag">withdrew</span>}
                </div>
                <div className={`evidence ${ev.cls}`}>
                  {ev.marks} {ev.label}
                  {c.sources?.length ? ` · ${c.sources.length} sources` : ''}
                  {c.party ? ` · ${c.party.replace('Prefers ', '').replace(' Party', '')}` : ''}
                </div>
                {c.withdrawn && (
                  <div className="note" style={{ fontSize: 11 }}>
                    Withdrew after the pamphlet was printed; may still appear on your ballot.
                  </div>
                )}
                {r.score == null && !c.withdrawn && (
                  <div className="note" style={{ fontSize: 11 }}>
                    Not enough confident evidence to score against your values.
                  </div>
                )}
                {r.score != null && r.coverage < LOW_COVERAGE && (
                  <div className="note" style={{ fontSize: 11 }}>
                    Rough read — matched on only {r.shared.length} of your values
                    scoreable in this race.
                  </div>
                )}
              </div>
              <div className="chev">{open ? '▴' : '▾'}</div>
            </button>
            {open && <CandidateExpanded data={data} contest={contest} row={r} answers={answers} />}
          </React.Fragment>
        )
      })}
      <div className="note" style={{ padding: '4px 18px 12px', fontSize: 11 }}>
        {contest.race_blurb}
      </div>
    </section>
  )
}

function MeasureCard({ measure, answers }) {
  const [open, setOpen] = useState(false)
  const { lean } = measureLean(measure, answers)
  const pill =
    lean === 'yes' ? { text: 'leans YES', bg: 'var(--seafoam)' }
    : lean === 'no' ? { text: 'leans NO', bg: 'var(--coral)' }
    : lean === 'split' ? { text: 'genuinely split', bg: 'var(--muted-deep)' }
    : null
  const pam = pamphletLink(measure.pamphlet_pages)
  return (
    <section className="card" style={{ margin: '12px 20px 0', overflow: 'hidden' }}>
      <button className="cand" style={{ padding: '14px 18px' }} onClick={() => setOpen(!open)}>
        <div style={{ flex: 1 }}>
          <div className="eyebrow eyebrow--sm">
            {measure.jurisdiction.toUpperCase()} · {measure.proposition.toUpperCase()}
          </div>
          <div style={{ fontWeight: 800, fontSize: 15, marginTop: 2 }}>{measure.title}</div>
        </div>
        {pill ? (
          <span className="pill-lean" style={{ background: pill.bg }}>
            {pill.text}
          </span>
        ) : (
          <span className="note" style={{ fontSize: 11 }}>no lean</span>
        )}
        <div className="chev">{open ? '▴' : '▾'}</div>
      </button>
      {open && (
        <div className="race-expand rise" style={{ marginTop: 0 }}>
          <div style={{ background: 'var(--seafoam-tint)', borderRadius: 14, padding: '13px 15px' }}>
            <div className="eyebrow" style={{ letterSpacing: 1 }}>WHAT IT ACTUALLY DOES</div>
            <p className="copy" style={{ fontSize: 13.5, marginTop: 5, color: 'var(--navy)' }}>
              {measure.what_it_does} {measure.cost_line && <em>({measure.cost_line})</em>}
            </p>
          </div>
          {pill ? (
            <div style={{ marginTop: 12, display: 'flex', alignItems: 'center', gap: 12 }}>
              <span className="pill-lean" style={{ background: pill.bg, fontSize: 15, padding: '8px 16px' }}>
                {pill.text}
              </span>
              <div style={{ fontSize: 12, lineHeight: 1.4, fontWeight: 700, color: 'var(--ink-soft)' }}>
                for you — based on your {Object.keys(measure.lean_mappings).join(' & ')} answers
              </div>
            </div>
          ) : (
            <div className="dashed-note" style={{ marginTop: 12 }}>
              <strong>No lean shown</strong> — your interview didn't map cleanly onto this one, and we won't fake it.
            </div>
          )}
          <div style={{ display: 'flex', gap: 10, marginTop: 14 }}>
            <div style={{ flex: 1, background: 'var(--seafoam-tint)', borderRadius: 14, padding: '12px 13px' }}>
              <div className="eyebrow" style={{ letterSpacing: 1, color: 'var(--seafoam-deep)' }}>✓ PRO</div>
              <p style={{ fontSize: 12, lineHeight: 1.55, fontWeight: 600, margin: '5px 0 0' }}>{measure.pro_summary}</p>
            </div>
            <div style={{ flex: 1, background: 'var(--coral-tint)', borderRadius: 14, padding: '12px 13px' }}>
              <div className="eyebrow" style={{ letterSpacing: 1, color: '#C05A3E' }}>✕ CON</div>
              <p style={{ fontSize: 12, lineHeight: 1.55, fontWeight: 600, margin: '5px 0 0' }}>{measure.con_summary}</p>
            </div>
          </div>
          <p className="note" style={{ margin: '12px 0 0', textAlign: 'center', fontSize: 11.5 }}>
            Summaries of official pamphlet statements —{' '}
            {pam ? (
              <a className="cite" href={pam} target="_blank" rel="noopener noreferrer">
                read them unedited
              </a>
            ) : (
              'see the county pamphlet'
            )}
            .
          </p>
        </div>
      )}
    </section>
  )
}

const CONCERN_CHIPS = [
  {
    label: '🚩 No extremists',
    text: "I don't want to support extremists in any direction, even if they match my values on paper. Check each candidate's record, endorsements, and donors for red flags.",
  },
  {
    label: '💰 Follow the money',
    text: 'Look closely at who funds each candidate — individual donors, PACs, party money — and flag anything that could pull them away from my interests.',
  },
  {
    label: '🔨 Real track record',
    text: 'I care more about what candidates have actually done than what they say. Which of these have a real record of delivering?',
  },
  {
    label: '🗳️ Who can win',
    text: 'For close matches, factor in who realistically has a shot of advancing past the primary.',
  },
]

function BriefSection({ data, answers, contests, measures, shareUrl }) {
  const [copied, setCopied] = useState(false)
  const [concerns, setConcerns] = useState('')
  const addChip = (t) =>
    setConcerns((prev) => (prev.includes(t) ? prev : prev ? `${prev.trimEnd()}\n${t}` : t))
  const text = useMemo(
    () => buildBrief(data, answers, contests, measures, shareUrl, concerns),
    [data, answers, contests, measures, shareUrl, concerns]
  )
  const words = text.split(/\s+/).length
  const copy = () => {
    navigator.clipboard.writeText(text).then(() => {
      setCopied(true)
      setTimeout(() => setCopied(false), 4000)
    })
  }
  return (
    <section className="screen--navy" style={{ margin: '24px 0 0', padding: '30px 24px' }}>
      <div className="eyebrow" style={{ letterSpacing: 2 }}>⚓ THE BALLOT BRIEF</div>
      <h1 className="display" style={{ fontSize: 26, lineHeight: 1.2, marginTop: 8, color: 'var(--cream)' }}>
        Take your ballot to your own AI
      </h1>
      <p className="copy" style={{ fontSize: 14, marginTop: 10, color: '#C7D4DF' }}>
        One tap copies your values, results, and candidate summaries — plus a ready-made
        prompt asking the AI to dig deeper and flag any extremism concerns. Paste and go.
      </p>
      <div className="packet" style={{ marginTop: 18 }}>
        {text.split('\n').slice(4, 5)[0]?.slice(0, 60)}…<br />
        {data.rubric.axes
          .filter((a) => answers[a.id])
          .slice(0, 2)
          .map((a) => `${a.title} · `)}
        …<br />
        <span className="hint">+ summaries &amp; sources for all {contests.length + measures.length} contests</span>
      </div>
      <div style={{ marginTop: 18 }}>
        <label
          className="copy"
          htmlFor="brief-concerns"
          style={{ display: 'block', fontSize: 13, fontWeight: 700, color: '#C7D4DF' }}
        >
          Anything you want the AI to know or check? <span style={{ fontWeight: 400 }}>(optional)</span>
        </label>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8, margin: '10px 0' }}>
          {CONCERN_CHIPS.map((chip) => (
            <button
              key={chip.label}
              type="button"
              onClick={() => addChip(chip.text)}
              disabled={concerns.includes(chip.text)}
              style={{
                font: 'inherit',
                fontSize: 12,
                fontWeight: 700,
                color: concerns.includes(chip.text) ? '#7E93A6' : 'var(--cream)',
                background: 'transparent',
                border: '1.5px solid currentColor',
                borderRadius: 999,
                padding: '5px 12px',
                cursor: concerns.includes(chip.text) ? 'default' : 'pointer',
              }}
            >
              {concerns.includes(chip.text) ? '✓ ' : '+ '}
              {chip.label}
            </button>
          ))}
        </div>
        <textarea
          id="brief-concerns"
          className="field"
          rows={3}
          value={concerns}
          onChange={(e) => setConcerns(e.target.value)}
          placeholder={'Tap a suggestion above or write your own — e.g. "I\'m torn on the transit measure, push back on my lean."'}
          style={{ resize: 'vertical' }}
        />
      </div>
      <div style={{ marginTop: 18, textAlign: 'center' }}>
        <button className="btn btn--coral btn--lg" style={{ fontSize: 18, padding: '15px 32px' }} onClick={copy}>
          Copy my Ballot Brief
        </button>
      </div>
      {copied && <div className="copied" style={{ marginTop: 16 }}>✓ Copied! Paste it into Claude, ChatGPT, or any AI — the prompt is included.</div>}
      <p className="note" style={{ margin: '8px 0 0', textAlign: 'center', fontSize: 11.5 }}>
        ~{Math.round(words / 100) * 100} words · plain text · yours to keep
      </p>
    </section>
  )
}

function Footer() {
  const [msg, setMsg] = useState('')
  const [state, setState] = useState(null)
  const send = () => {
    postFeedback({ kind: 'comment', message: msg })
      .then((r) => setState(r.ok ? 'sent' : 'error'))
      .catch(() => setState('error'))
  }
  return (
    <footer style={{ marginTop: 24 }}>
      <div className="wave-cap" />
      <div style={{ padding: '20px 24px 26px' }}>
        <div className="brand" style={{ gap: 8 }}>
          <div className="buoy buoy--plain" />
          <div className="brand-name brand-name--sm">Voter Lifeboat</div>
        </div>
        <p style={{ margin: '12px 0 0', fontSize: 12.5, lineHeight: 1.65, fontWeight: 600, color: 'var(--ink-soft)' }}>
          Built and researched by AI — <strong style={{ color: 'var(--navy)' }}>we make no accuracy claims.</strong>{' '}
          Check every citation yourself. Not affiliated with King County
          Elections or any campaign. English-only for now — we know, and we're
          sorry. The county's official pamphlet is available in seven languages
          at{' '}
          <a href="https://kingcounty.gov/en/dept/elections/how-to-vote/voters-pamphlet" target="_blank" rel="noopener noreferrer">
            kingcounty.gov
          </a>
          .
        </p>
        <div className="panel" style={{ marginTop: 16 }}>
          {state === 'sent' ? (
            <div style={{ fontWeight: 800, fontSize: 14, color: 'var(--seafoam-deep)' }}>
              ✓ Sent — thank you for helping improve this.
            </div>
          ) : (
            <>
              <div style={{ fontWeight: 800, fontSize: 14 }}>Spot something wrong? Tell us.</div>
              <textarea
                className="field"
                style={{ marginTop: 8 }}
                rows={2}
                placeholder="Your comment…"
                value={msg}
                onChange={(e) => setMsg(e.target.value)}
              />
              {state === 'error' && (
                <div style={{ fontSize: 11.5, fontWeight: 700, color: 'var(--coral-deep)', marginTop: 6 }}>
                  Couldn't send — try again in a moment.
                </div>
              )}
              <button className="btn btn--navy btn--xs" style={{ marginTop: 10 }} onClick={send} disabled={!msg.trim()}>
                Send
              </button>
            </>
          )}
        </div>
        <p style={{ margin: '14px 0 0', fontSize: 11.5, fontWeight: 600, color: 'var(--muted-deep)' }}>
          Your interview answers and voting districts (never your address) are
          recorded anonymously and published as an open dataset —{' '}
          <a href="#data">see what King County values so far</a>.
        </p>
        <p style={{ margin: '10px 0 0', fontSize: 11, fontWeight: 700, color: 'var(--muted)' }}>
          No accounts · no cookies · open methodology · open data
        </p>
      </div>
    </footer>
  )
}

export default function Results({ data, districts, answers, restored, onStartOver }) {
  const contests = useMemo(
    () => contestsOnBallot(data, districts, scopeMatches),
    [data, districts]
  )
  const measures = useMemo(
    () => measuresOnBallot(data, districts, scopeMatches),
    [data, districts]
  )
  const [shareUrl, setShareUrl] = useState('')
  const [linkCopied, setLinkCopied] = useState(false)

  // Auto-update the address bar so the report is bookmarkable/sharable.
  useEffect(() => {
    setShareUrl(writeHash(data.data_version, districts, answers))
  }, [data, districts, answers])

  // Record fresh completions in the public dataset — once, and never for
  // reports someone else shared (that would double-count the original voter).
  const recorded = useRef(false)
  useEffect(() => {
    if (restored || recorded.current) return
    recorded.current = true
    postReport(data.data_version, districts, answers)
  }, [restored, data, districts, answers])

  const copyLink = () => {
    navigator.clipboard.writeText(shareUrl).then(() => {
      setLinkCopied(true)
      setTimeout(() => setLinkCopied(false), 3500)
    })
  }

  const dataChanged = restored && restored.dataVersion && restored.dataVersion !== data.data_version

  return (
    <main className="screen screen--app screen--wide rise" style={{ paddingBottom: 0 }}>
      <header style={{ padding: '20px 24px 0' }}>
        <h1 className="display" style={{ fontSize: 25 }}>Your ballot, charted</h1>
        <p style={{ fontSize: 13, fontWeight: 700, color: 'var(--ink-soft)', margin: '4px 0 0' }}>
          {contests.length} contests
          {measures.length ? ` · ${measures.length} measure${measures.length > 1 ? 's' : ''}` : ''}{' '}
          · matched to your values · <span className="accent">every score cites sources</span>
        </p>
        <div className="share-row" style={{ marginTop: 10 }}>
          <button className="btn btn--navy btn--xs" onClick={copyLink}>
            {linkCopied ? '✓ link copied' : '🔗 Copy link to my report'}
          </button>
          <button className="linkish" style={{ fontSize: 12 }} onClick={onStartOver}>
            start over
          </button>
        </div>
        <p className="note" style={{ margin: '8px 0 0', fontSize: 11 }}>
          This page's link holds your answers (never your address) — bookmark it
          to come back, share it only with people you'd show your values to.
        </p>
        {dataChanged && (
          <div className="banner-tcc" style={{ marginTop: 10 }}>
            ☔ Our data has been updated since this link was made — scores may
            have shifted slightly.
          </div>
        )}
      </header>

      {contests.map((c) => (
        <ContestCard key={c.slug} data={data} contest={c} answers={answers} />
      ))}

      {measures.length > 0 && (
        <>
          <h2 className="display" style={{ fontSize: 19, margin: '22px 24px 0' }}>Measures</h2>
          {measures.map((m) => (
            <MeasureCard key={m.slug} measure={m} answers={answers} />
          ))}
        </>
      )}

      <p className="note" style={{ margin: '16px 24px 0', textAlign: 'center', color: 'var(--muted)' }}>
        WA primaries send the top 2 to November, regardless of party.
      </p>

      <BriefSection data={data} answers={answers} contests={contests} measures={measures} shareUrl={shareUrl} />
      <Footer />
    </main>
  )
}
