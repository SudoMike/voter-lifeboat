import React from 'react'

export default function Landing({ data, onStart }) {
  return (
    <main className="screen screen--app rise">
      <header style={{ padding: '22px 24px 0' }}>
        <div className="brand">
          <div className="buoy" />
          <div className="brand-name">Voter Lifeboat</div>
        </div>
      </header>
      <section style={{ padding: '34px 24px 8px' }}>
        <h1 className="display display--xl">
          Your values.
          <br />
          Your ballot.
          <br />
          <span className="accent">Charted.</span>
        </h1>
        <p className="lede" style={{ marginTop: 16 }}>
          Answer a few quick questions. See how everyone on <em>your</em> ballot
          lines up with <em>your</em> values. King County primary · Aug 4, 2026.
        </p>
      </section>
      <section style={{ padding: '20px 24px 0' }}>
        <button className="btn btn--navy btn--lg" onClick={onStart}>
          Hop in — takes 3 minutes
        </button>
      </section>
      <section
        style={{ padding: '26px 24px 0', display: 'flex', flexDirection: 'column', gap: 10 }}
      >
        <div className="panel trust-row">
          <div className="trust-icon" style={{ background: 'var(--seafoam)' }}>
            AI
          </div>
          <div>
            <strong>Built and researched entirely by AI.</strong> We make no
            accuracy claims — every score shows its sources so you can check our
            work.
          </div>
        </div>
        <div className="panel trust-row">
          <div className="trust-icon" style={{ background: 'var(--coral)' }}>
            ⌂
          </div>
          <div>
            <strong>Private by design.</strong> Your address and answers never
            leave your browser, except to look up your voting districts.
          </div>
        </div>
      </section>
      <footer style={{ marginTop: 26 }}>
        <div className="wave-bottom">
          <div className="wave-label">NO ACCOUNTS · NO COOKIES · NO TRACKING</div>
        </div>
      </footer>
    </main>
  )
}
