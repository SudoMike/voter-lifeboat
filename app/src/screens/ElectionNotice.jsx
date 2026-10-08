import React from 'react'
import GitHubLink from './GitHubLink.jsx'
import { archivedElections, electionHref, guideLinkText } from '../lib/elections.js'
import { KeyDates } from './Landing.jsx'

// The active election before any of its contests are researched: say what is
// coming and point at the archived guide. No address form.
export default function ElectionNotice({ data, index, base }) {
  const { name, day } = data.election
  const previous = archivedElections(index)[0]
  return (
    <main className="screen screen--app rise">
      <header
        style={{
          padding: '22px 24px 0',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
        }}
      >
        <div className="brand">
          <div className="buoy" />
          <div className="brand-name">Voter Lifeboat</div>
        </div>
        <GitHubLink />
      </header>
      <section style={{ padding: '34px 24px 8px' }}>
        <h1 className="display display--lg">{name}</h1>
        <KeyDates day={day} />
        <p className="copy" style={{ marginTop: 16 }}>
          This guide is being researched now and will appear here first for
          statewide contests and measures, then county by county.
        </p>
      </section>
      {previous && (
        <section style={{ padding: '18px 24px 0' }}>
          <a className="btn btn--navy" href={electionHref(base, previous)}>
            {guideLinkText(previous)}
          </a>
        </section>
      )}
      <footer style={{ marginTop: 26 }}>
        <div className="note" style={{ textAlign: 'center', padding: '0 24px 18px', fontSize: 12 }}>
          Follow the work on{' '}
          <a href="https://github.com/SudoMike/voter-lifeboat" target="_blank" rel="noopener noreferrer">
            GitHub
          </a>{' '}
          · <a href="#methodology">How this guide is built</a>
        </div>
        <div className="wave-bottom">
          <div className="wave-label">NO ACCOUNTS · NO COOKIES · OPEN DATA</div>
        </div>
      </footer>
    </main>
  )
}
