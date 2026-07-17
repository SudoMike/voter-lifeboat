import React, { useMemo, useRef, useState } from 'react'
import { buildProfile } from '../lib/scoring.js'

const AXIS_LABEL = (data, id) =>
  data.rubric.axes.find((a) => a.id === id)?.title?.toUpperCase() || id.toUpperCase()

// Shared progress bar — the sail slides toward the finish as cards are answered.
// `tone` recolors it to stay legible on the seafoam and navy screens.
function ProgressHeader({ idx, total, tone, style }) {
  const pct = `${Math.round((idx / total) * 100)}%`
  return (
    <header className={`progress${tone ? ` progress--${tone}` : ''}`} style={style}>
      <div className="progress-track">
        <div className="progress-fill" style={{ width: pct }} />
      </div>
      <div className="progress-count">
        {idx + 1} of {total}
      </div>
    </header>
  )
}

export default function Interview({ data, items, onDone }) {
  const [idx, setIdx] = useState(0)
  const [responses, setResponses] = useState([])
  const [weights, setWeights] = useState({})
  const [pulseFor, setPulseFor] = useState(null) // {axis, answered: 'agree'|'disagree'|'chose'}
  const [exiting, setExiting] = useState(null) // 'agree' | 'disagree'
  const touch = useRef(null)

  const total = items.length
  const tradeoffCount = items.filter((i) => i.kind === 'tradeoff').length
  const tradeoffNo = items.slice(0, idx + 1).filter((i) => i.kind === 'tradeoff').length

  const finish = (resps) => onDone(buildProfile(resps, weightsRef()))
  // weights state may lag one tick when finishing from a pulse; read fresh
  const weightsLatest = useRef(weights)
  weightsLatest.current = weights
  const weightsRef = () => weightsLatest.current

  const advance = (resps) => {
    if (idx + 1 >= total) {
      onDone(buildProfile(resps, weightsRef()))
    } else {
      setIdx(idx + 1)
    }
  }

  const answer = (choice) => {
    const item = items[idx]
    const resps = [...responses, { item, choice }]
    setResponses(resps)
    const answered = choice !== null
    if (answered && item.pulse) {
      const axis = item.kind === 'statement' ? item.axis : Object.keys(item.options[choice].effects)[0]
      setPulseFor({ axis, resps, choice })
    } else {
      advance(resps)
    }
  }

  const answerCard = (choice) => {
    if (exiting) return
    if (choice === null) return answer(null)
    setExiting(choice)
    setTimeout(() => {
      setExiting(null)
      answer(choice)
    }, 210)
  }

  const pickWeight = (w) => {
    const { axis, resps } = pulseFor
    const nextWeights = { ...weights, [axis]: w }
    setWeights(nextWeights)
    weightsLatest.current = nextWeights
    setPulseFor(null)
    if (idx + 1 >= total) {
      onDone(buildProfile(resps, nextWeights))
    } else {
      setIdx(idx + 1)
    }
  }

  // --- care pulse screen ---
  if (pulseFor) {
    const verb = pulseFor.choice === 'agree' ? 'You agreed.' : pulseFor.choice === 'disagree' ? 'You disagreed.' : 'Noted.'
    const axisTitle = data.rubric.axes.find((a) => a.id === pulseFor.axis)?.title?.toLowerCase()
    return (
      <main className="screen screen--app screen--navy rise" style={{ padding: '18px 24px 34px', textAlign: 'center' }}>
        <ProgressHeader idx={idx} total={total} tone="navy" style={{ marginBottom: 24, textAlign: 'left' }} />
        <div className="eyebrow" style={{ letterSpacing: 2 }}>QUICK PULSE</div>
        <h1 className="display" style={{ fontSize: 26, lineHeight: 1.25, marginTop: 12 }}>
          {verb} How much do you care about this one?
        </h1>
        <div className="pulse-row" style={{ marginTop: 26 }}>
          {data.interview.care_pulse.options.map((o, i) => (
            <button key={o.label} className="pulse-opt" onClick={() => pickWeight(o.weight)}>
              <span className="dot" style={{ width: 12 + i * 9, height: 12 + i * 9, opacity: 0.5 + i * 0.25 }} />
              {o.label}
            </button>
          ))}
        </div>
        <p className="note" style={{ marginTop: 24, color: 'rgba(251,245,234,.55)' }}>
          This weights {axisTitle} in your results
        </p>
      </main>
    )
  }

  // A ballot whose covered candidates and measures carry no scored axes
  // yields zero interview items; skip straight to results rather than crash.
  if (!total) {
    return (
      <main className="screen screen--app rise" style={{ padding: '60px 24px', textAlign: 'center' }}>
        <h1 className="display display--md">Nothing to ask you yet</h1>
        <p className="copy" style={{ margin: '10px auto 0', maxWidth: 320 }}>
          None of the covered items on this ballot have scored positions, so
          there is no interview to take — you can still browse the ballot.
        </p>
        <button className="btn btn--navy btn--sm" style={{ marginTop: 20 }} onClick={() => onDone({})}>
          Show my ballot
        </button>
      </main>
    )
  }

  const item = items[idx]

  // --- trade-off scenario ---
  if (item.kind === 'tradeoff') {
    return (
      <main className="screen screen--app screen--seafoam rise" style={{ paddingBottom: 30 }} key={item.id}>
        <div style={{ padding: '18px 24px 0' }}>
          <ProgressHeader idx={idx} total={total} tone="seafoam" />
          <div className="eyebrow" style={{ color: 'var(--navy)', letterSpacing: 2, marginTop: 14 }}>
            ⚓ TRADE-OFF · {tradeoffNo} OF {tradeoffCount}
          </div>
        </div>
        <section style={{ padding: '26px 24px 0' }}>
          <h1 className="display" style={{ fontSize: 29, lineHeight: 1.2, color: '#fff', textShadow: '0 2px 0 rgba(27,58,87,.2)', textWrap: 'pretty' }}>
            {item.text}
          </h1>
          <p style={{ fontSize: 14, fontWeight: 700, margin: '8px 0 0', color: '#EAF6F2' }}>
            No splitting it — pick the one that matters more.
          </p>
        </section>
        <section style={{ display: 'flex', flexDirection: 'column', gap: 12, padding: '24px 20px 0' }}>
          {item.options.map((o, i) => (
            <React.Fragment key={o.label}>
              {i > 0 && <div className="vs">— or —</div>}
              <button className="choice" onClick={() => answer(i)}>
                <div className="choice-label">OPTION {i === 0 ? 'A' : 'B'}</div>
                <div className="choice-text">{o.label}</div>
                {o.detail && (
                  <div style={{ fontSize: 12.5, fontWeight: 700, color: 'var(--ink-soft)', marginTop: 3 }}>{o.detail}</div>
                )}
              </button>
            </React.Fragment>
          ))}
        </section>
        <button className="skip" style={{ marginTop: 16 }} onClick={() => answer(null)}>
          skip this one →
        </button>
      </main>
    )
  }

  // --- statement card (tap or swipe) ---
  const onTouchStart = (e) => (touch.current = e.touches[0].clientX)
  const onTouchEnd = (e) => {
    if (touch.current == null) return
    const dx = e.changedTouches[0].clientX - touch.current
    touch.current = null
    if (dx > 60) answerCard('agree')
    else if (dx < -60) answerCard('disagree')
  }

  return (
    <main className="screen screen--app rise" style={{ paddingBottom: 26 }} key={item.id}>
      <ProgressHeader idx={idx} total={total} style={{ padding: '18px 24px 0' }} />
      <section
        className={`statement${exiting ? ` exit-${exiting}` : ''}`}
        style={{ margin: '22px 20px 0', touchAction: 'pan-y' }}
        onTouchStart={onTouchStart}
        onTouchEnd={onTouchEnd}
      >
        <div className="eyebrow">
          {AXIS_LABEL(data, item.axis)} · CARD {idx + 1}
        </div>
        <p className="statement-text">{item.text}</p>
        <div className="swipe-hint">↔ swipe, or tap below</div>
      </section>
      <section className="answer-row" style={{ padding: '18px 20px 0' }}>
        <button className="answer answer--disagree" onClick={() => answerCard('disagree')}>
          Disagree
        </button>
        <button className="answer answer--agree" onClick={() => answerCard('agree')}>
          Agree
        </button>
      </section>
      <button className="skip" style={{ marginTop: 14 }} onClick={() => answerCard(null)}>
        skip this one →
      </button>
    </main>
  )
}
