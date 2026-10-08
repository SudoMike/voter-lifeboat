import React from 'react'
import GitHubLink from './GitHubLink.jsx'
import {
  archivedElections,
  ballotsMailBy,
  electionHref,
  longElectionDay,
  registerOnlineBy,
  shortDay,
} from '../lib/elections.js'
import { VOTEWA_URL } from '../lib/officialLinks.js'

// What a voter needs to know before election day, from the loaded election's
// day: when ballots arrive, the return deadline, and the registration cutoff.
export function KeyDates({ day }) {
  return (
    <p className="copy key-dates" style={{ marginTop: 10, fontSize: 13.5 }}>
      <strong>Election day: {longElectionDay(day)}.</strong> Ballots mail by{' '}
      {ballotsMailBy(day)}; return yours by 8 p.m. {shortDay(day)}. Register or
      update online or by mail by {registerOnlineBy(day)} at{' '}
      <a href={VOTEWA_URL} target="_blank" rel="noopener noreferrer">
        VoteWA.gov
      </a>
      , or in person until 8 p.m. {shortDay(day)}.
    </p>
  )
}

// Archived elections from the index, each at its own route.
function PastElections({ index, election, base }) {
  const past = archivedElections(index)
  if (!past.length) return null
  return (
    <details className="note past-elections" style={{ textAlign: 'center', padding: '0 24px 10px', fontSize: 12 }}>
      <summary>Past elections</summary>
      <ul>
        {past.map((e) => (
          <li key={e.id}>
            {e.id === election?.id ? (
              <>{e.name} (this guide)</>
            ) : (
              <a href={electionHref(base, e)}>{e.name}</a>
            )}
          </li>
        ))}
      </ul>
    </details>
  )
}

export default function Landing({ data, index, election, base, onStart }) {
  const archived = election?.status === 'archived'
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
        <h1 className="display display--xl">
          Nobody finishes the
          <br />
          <span className="accent">voters' pamphlet.</span>
        </h1>
        <p className="lede" style={{ marginTop: 16 }}>
          Get through your whole ballot in three minutes — see how everyone on{' '}
          <em>your</em> covered ballot lines up with <em>your</em> values.
          {data.election.scope} · {data.election.name}.
        </p>
        {!archived && data.election.day && <KeyDates day={data.election.day} />}
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
            accuracy claims — every score shows its sources so you can{' '}
            <a
              href="https://github.com/SudoMike/voter-lifeboat"
              target="_blank"
              rel="noopener noreferrer"
            >
              check our work
            </a>
            . See the <a href="#methodology">methodology</a>.
          </div>
        </div>
        <div className="panel trust-row">
          <div className="trust-icon" style={{ background: 'var(--coral)' }}>
            ⌂
          </div>
          <div>
            <strong>Anonymous &amp; open.</strong> Your address is used once to
            find your ballot context, then discarded — never stored.{' '}
            {archived ? (
              <>
                This election has ended, so answers given here are not
                recorded; earlier answers are in <a href="#data">the open dataset</a>.
              </>
            ) : (
              <>
                Your answers and ballot context are recorded anonymously and
                published as <a href="#data">an open dataset</a>.
              </>
            )}
          </div>
        </div>
      </section>
      <footer style={{ marginTop: 26 }}>
        <div
          className="note"
          style={{ textAlign: 'center', padding: '0 24px 10px', fontSize: 12 }}
        >
          <a href="#methodology">How this guide is built</a> ·{' '}
          <a href="#data">Open dataset</a>
        </div>
        <PastElections index={index} election={election} base={base} />
        <div
          className="note"
          style={{ textAlign: 'center', padding: '0 24px 18px', fontSize: 12 }}
        >
          Interested in the WA state budget?{' '}
          <a
            href="https://washington.openbudgets.app/"
            target="_blank"
            rel="noopener noreferrer"
          >
            Check this out.
          </a>
        </div>
        <div className="wave-bottom">
          <div className="wave-label">NO ACCOUNTS · NO COOKIES · OPEN DATA</div>
        </div>
      </footer>
    </main>
  )
}
