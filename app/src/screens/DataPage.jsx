// The open dataset, visualized. Every completed report records interview
// answers + ballot context (never an address) — this page aggregates the
// whole file live on each visit. Raw records: GET /api/reports.

import React, { useEffect, useMemo, useState } from 'react'

const HOT_WEIGHT = 2 // weight at which the interview labels an axis "care a lot"

const DISTRICT_GROUPS = [
  ['CITY', 'By city'],
  ['LEGDST', 'By legislative district'],
  ['KCCDST', 'By county council district'],
]

function useReports() {
  const [state, setState] = useState({ status: 'loading', reports: [] })
  useEffect(() => {
    fetch('/api/reports')
      .then((r) => {
        if (!r.ok) throw new Error(`reports ${r.status}`)
        return r.json()
      })
      .then((d) => setState({ status: 'ready', reports: d.reports || [] }))
      .catch(() => setState({ status: 'error', reports: [] }))
  }, [])
  return state
}

// answers arrive as {axis: [value, weight]}; bucket values to -2..2 integers
function axisStats(reports) {
  const stats = {}
  for (const r of reports) {
    for (const [axis, pair] of Object.entries(r.answers || {})) {
      if (!Array.isArray(pair)) continue
      const [v, w] = pair
      const s = (stats[axis] ||= { buckets: [0, 0, 0, 0, 0], n: 0, hot: 0 })
      s.buckets[Math.round(Math.max(-2, Math.min(2, v))) + 2]++
      s.n++
      if (w >= HOT_WEIGHT) s.hot++
    }
  }
  return stats
}

function districtCounts(reports, key) {
  const counts = new Map()
  for (const r of reports) {
    const val = r.districts?.[key]
    if (val != null) counts.set(val, (counts.get(val) || 0) + 1)
  }
  return [...counts.entries()].sort((a, b) => b[1] - a[1])
}

function fieldCounts(reports, read) {
  const counts = new Map()
  for (const r of reports) {
    const val = read(r)
    if (val != null) counts.set(val, (counts.get(val) || 0) + 1)
  }
  return [...counts.entries()].sort((a, b) => b[1] - a[1])
}

function dayCounts(reports, numDays = 28) {
  const byDay = new Map()
  for (const r of reports) {
    const day = (r.at || '').slice(0, 10)
    if (day) byDay.set(day, (byDay.get(day) || 0) + 1)
  }
  const days = []
  const now = new Date()
  for (let i = numDays - 1; i >= 0; i--) {
    const d = new Date(now)
    d.setDate(d.getDate() - i)
    const key = d.toISOString().slice(0, 10)
    days.push({ key, label: `${d.getMonth() + 1}/${d.getDate()}`, n: byDay.get(key) || 0 })
  }
  return days
}

function AxisChart({ axis, stats }) {
  const max = Math.max(...stats.buckets, 1)
  const hotPct = stats.n ? Math.round((stats.hot / stats.n) * 100) : 0
  return (
    <div className="panel" style={{ padding: '14px 16px 12px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', gap: 8 }}>
        <div style={{ fontWeight: 800, fontSize: 14 }}>{axis.title}</div>
        <div style={{ fontSize: 11, fontWeight: 700, color: 'var(--coral-deep)', whiteSpace: 'nowrap' }}>
          🔥 {hotPct}% care a lot
        </div>
      </div>
      <div style={{ display: 'flex', alignItems: 'flex-end', gap: 5, height: 54, marginTop: 10 }}>
        {stats.buckets.map((n, i) => (
          <div
            key={i}
            title={`${n} answer${n === 1 ? '' : 's'}`}
            style={{
              flex: 1,
              borderRadius: '6px 6px 0 0',
              height: `${(n / max) * 100}%`,
              minHeight: n ? 4 : 1,
              background:
                i < 2 ? 'var(--coral)' : i === 2 ? 'var(--sand-deep)' : 'var(--seafoam)',
            }}
          />
        ))}
      </div>
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          gap: 10,
          fontSize: 10.5,
          fontWeight: 700,
          color: 'var(--muted-deep)',
          marginTop: 6,
        }}
      >
        <span>← {axis.pole_a.label}</span>
        <span style={{ textAlign: 'right' }}>{axis.pole_b.label} →</span>
      </div>
    </div>
  )
}

function DistrictBars({ title, entries, total }) {
  if (!entries.length) return null
  const shown = entries.slice(0, 10)
  return (
    <div className="panel" style={{ padding: '14px 16px' }}>
      <div style={{ fontWeight: 800, fontSize: 14 }}>{title}</div>
      <div style={{ marginTop: 10, display: 'flex', flexDirection: 'column', gap: 8 }}>
        {shown.map(([name, n]) => (
          <div key={name}>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 12, fontWeight: 700 }}>
              <span>{name}</span>
              <span style={{ color: 'var(--muted-deep)' }}>{n}</span>
            </div>
            <div className="bar bar--sm">
              <i style={{ width: `${(n / total) * 100}%` }} />
            </div>
          </div>
        ))}
        {entries.length > shown.length && (
          <div className="hint" style={{ fontSize: 11 }}>
            + {entries.length - shown.length} more in the raw data
          </div>
        )}
      </div>
    </div>
  )
}

export default function DataPage({ data, onBack }) {
  const { status, reports } = useReports()
  const stats = useMemo(() => axisStats(reports), [reports])
  const days = useMemo(() => dayCounts(reports), [reports])
  const maxDay = Math.max(...days.map((d) => d.n), 1)
  const axes = data.rubric.axes.filter((a) => stats[a.id])

  return (
    <main className="screen screen--app screen--wide rise" style={{ paddingBottom: 0 }}>
      <header style={{ padding: '22px 24px 0' }}>
        <div className="brand">
          <div className="buoy" />
          <div className="brand-name">Voter Lifeboat</div>
        </div>
        <div className="eyebrow" style={{ marginTop: 22 }}>The open dataset</div>
        <h1 className="display display--lg" style={{ marginTop: 6 }}>
          What Washington voters value
        </h1>
        <p className="copy" style={{ fontSize: 14, marginTop: 8 }}>
          Every completed report adds one anonymous record — interview answers
          and ballot context, never an address — to a public dataset. This
          page recounts the whole thing on every visit.
        </p>
        <button className="linkish" style={{ fontSize: 12, marginTop: 8 }} onClick={onBack}>
          ← back to the guide
        </button>
      </header>

      <section style={{ padding: '18px 24px 26px', display: 'flex', flexDirection: 'column', gap: 12 }}>
        {status === 'loading' && (
          <div className="bar bar--busy" style={{ width: 150, margin: '30px auto' }}>
            <i />
          </div>
        )}
        {status === 'error' && (
          <div className="panel" style={{ textAlign: 'center', fontWeight: 700 }}>
            Couldn't load the dataset — try again in a moment.
          </div>
        )}
        {status === 'ready' && reports.length === 0 && (
          <div className="panel" style={{ textAlign: 'center', fontWeight: 700 }}>
            No reports yet — yours could be the first on this chart.
          </div>
        )}
        {status === 'ready' && reports.length > 0 && (
          <>
            <div className="panel panel--sand" style={{ textAlign: 'center' }}>
              <div className="display" style={{ fontSize: 34 }}>{reports.length.toLocaleString()}</div>
              <div style={{ fontSize: 12, fontWeight: 800, color: 'var(--muted-deep)', letterSpacing: 0.5 }}>
                BALLOTS CHARTED SO FAR
              </div>
            </div>

            <div className="panel" style={{ padding: '14px 16px 10px' }}>
              <div style={{ fontWeight: 800, fontSize: 14 }}>Reports per day — last 4 weeks</div>
              <div style={{ display: 'flex', alignItems: 'flex-end', gap: 2, height: 60, marginTop: 10 }}>
                {days.map((d) => (
                  <div
                    key={d.key}
                    title={`${d.label}: ${d.n}`}
                    style={{
                      flex: 1,
                      borderRadius: '3px 3px 0 0',
                      height: `${(d.n / maxDay) * 100}%`,
                      minHeight: d.n ? 3 : 1,
                      background: d.n ? 'var(--seafoam)' : 'var(--sand)',
                    }}
                  />
                ))}
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 10.5, fontWeight: 700, color: 'var(--muted)', marginTop: 4 }}>
                <span>{days[0].label}</span>
                <span>today</span>
              </div>
            </div>

            <div className="eyebrow" style={{ marginTop: 10 }}>Where people land, per value</div>
            {axes.map((a) => (
              <AxisChart key={a.id} axis={a} stats={stats[a.id]} />
            ))}

            <div className="eyebrow" style={{ marginTop: 10 }}>Where reports come from</div>
            <DistrictBars
              title="By coverage status"
              entries={fieldCounts(reports, (r) => r.coverageStatus || 'legacy')}
              total={reports.length}
            />
            <DistrictBars
              title="By county"
              entries={fieldCounts(reports, (r) => r.county?.name || r.county?.id)}
              total={reports.length}
            />
            {DISTRICT_GROUPS.map(([key, title]) => (
              <DistrictBars
                key={key}
                title={title}
                entries={districtCounts(reports, key)}
                total={reports.length}
              />
            ))}

            <p className="note" style={{ fontSize: 11.5, marginTop: 6 }}>
              This is the entire dataset — no sampling, no hidden fields. Raw
              records: <a href="/api/reports">/api/reports</a> (JSON). Answers
              are self-reported by whoever completes the interview; nothing here
              is a poll or a prediction.
            </p>
          </>
        )}
      </section>
      <footer>
        <div
          className="note"
          style={{ textAlign: 'center', padding: '4px 24px 18px', fontSize: 12 }}
        >
          How were these scores built? See the{' '}
          <a href="#methodology">methodology</a>.
        </div>
        <div className="wave-bottom">
          <div className="wave-label">NO ACCOUNTS · NO COOKIES · OPEN DATA</div>
        </div>
      </footer>
    </main>
  )
}
