import React from 'react'

export default function Snapshot({ data, answers, onShow }) {
  const axes = data.rubric.axes.filter((a) => answers[a.id])
  const rows = axes
    .map((a) => {
      const { v, w } = answers[a.id]
      return { axis: a, v, w, strength: Math.abs(v) }
    })
    .sort((x, y) => y.w - x.w || y.strength - x.strength)
  const maxW = rows.length ? Math.max(...rows.map((r) => r.w)) : 0

  const tag = (r) => {
    if (r.w === maxW && r.w >= 2) return { text: 'cared most ★', cls: 'tag tag--star' }
    if (r.strength < 0.75) return { text: 'mixed', cls: 'tag' }
    const pole = r.v < 0 ? r.axis.pole_a.label : r.axis.pole_b.label
    return { text: pole.toLowerCase(), cls: 'tag' }
  }

  return (
    <main className="screen screen--app rise" style={{ paddingBottom: 30 }}>
      <header
        className="screen--navy"
        style={{ padding: '30px 24px 26px', textAlign: 'center', borderRadius: '0 0 32px 32px' }}
      >
        <div className="eyebrow" style={{ letterSpacing: 2 }}>
          ALL {rows.length} CHARTED 🎉
        </div>
        <h1 className="display" style={{ fontSize: 28, color: 'var(--cream)', marginTop: 8 }}>
          Your values snapshot
        </h1>
      </header>
      <section className="stack" style={{ padding: '22px 24px 0' }}>
        {rows.map((r) => {
          const t = tag(r)
          const width = `${Math.round(((r.v + 2) / 4) * 100)}%`
          const cls = r.w >= 2 ? 'is-coral' : r.strength < 0.75 ? 'is-light' : ''
          return (
            <div key={r.axis.id}>
              <div className="value-row">
                <span>{r.axis.title}</span>
                <span className={t.cls}>{t.text}</span>
              </div>
              <div className="bar" title={`${r.axis.pole_a.label} ← → ${r.axis.pole_b.label}`}>
                <i className={cls} style={{ width }} />
              </div>
              <div className="axis-scale">
                <span>{r.axis.pole_a.label.toLowerCase()}</span>
                <span>{r.axis.pole_b.label.toLowerCase()}</span>
              </div>
            </div>
          )
        })}
      </section>
      <section style={{ margin: '24px 24px 0', textAlign: 'center' }}>
        <button className="btn btn--coral btn--lg" style={{ fontSize: 18 }} onClick={onShow}>
          Show me my ballot →
        </button>
      </section>
    </main>
  )
}
