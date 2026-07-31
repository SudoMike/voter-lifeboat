// The stop between address lookup and the interview. It exists so a voter can
// catch a wrong match before it silently shapes every answer downstream: the
// Census geocoder matches fuzzily and will happily return a confident hit on a
// different address. It is also the honest place to admit degraded coverage,
// since county GIS layers flake and the same address can resolve fully one
// minute and partially the next.

import React from 'react'
import { describeDistricts } from '../lib/districts.js'

function CoverageNote({ context }) {
  const { coverageStatus, missingLayers, county } = context
  if (coverageStatus === 'statewide_only')
    return (
      <div className="dashed-note" style={{ marginTop: 16, textAlign: 'left' }}>
        <strong>{county.name} isn't covered yet.</strong> You'll get every
        statewide contest, but not local races or levies.
      </div>
    )
  if (coverageStatus === 'partial_county' || missingLayers?.length)
    return (
      <div className="dashed-note" style={{ marginTop: 16, textAlign: 'left' }}>
        <strong>Some local districts didn't answer.</strong> Your ballot may be
        missing a contest or two. Going back and trying again often clears it.
      </div>
    )
  return null
}

export default function Confirm({ data, context, ballot, onProceed, onRetry }) {
  const districts = describeDistricts(context.districts, {
    contests: data.contests,
    county: context.county.id,
  })
  const races = ballot.contests.length
  const measures = ballot.measures.length

  return (
    <main className="screen screen--app rise" style={{ padding: '40px 24px 40px', textAlign: 'center' }}>
      <div
        style={{
          width: 64, height: 64, margin: '0 auto', borderRadius: '50%',
          background: 'var(--seafoam-tint)', display: 'flex', alignItems: 'center',
          justifyContent: 'center', fontSize: 30, color: 'var(--seafoam)', fontWeight: 800,
        }}
      >
        ✓
      </div>
      <h1 className="display display--md" style={{ marginTop: 14 }}>
        Found your ballot
      </h1>
      <p className="note" style={{ margin: '8px auto 0', maxWidth: 320 }}>
        {context.matched}
      </p>

      <div className="panel panel--sand" style={{ margin: '18px auto 0', maxWidth: 340, textAlign: 'left' }}>
        <p className="eyebrow" style={{ margin: 0 }}>
          {context.county.name}
        </p>
        <ul style={{ margin: '9px 0 0', padding: 0, listStyle: 'none' }}>
          {districts.map((d) => (
            <li
              key={d.key}
              className="copy"
              style={{ display: 'flex', gap: 9, alignItems: 'baseline', marginTop: 5 }}
            >
              <span style={{ color: 'var(--seafoam)', fontWeight: 800, flex: 'none' }}>·</span>
              <span>{d.text}</span>
            </li>
          ))}
        </ul>
        {districts.length === 0 && (
          <p className="copy" style={{ marginTop: 6 }}>
            Statewide contests only.
          </p>
        )}
      </div>

      <p className="copy" style={{ margin: '16px auto 0', maxWidth: 320 }}>
        <strong>
          {races} {races === 1 ? 'contest' : 'contests'}
        </strong>{' '}
        on your ballot
        {measures > 0 ? (
          <>
            , plus{' '}
            <strong>
              {measures} local {measures === 1 ? 'measure' : 'measures'}
            </strong>
            .
          </>
        ) : (
          <>. No local measures in your area this election.</>
        )}
      </p>

      <CoverageNote context={context} />

      <button className="btn btn--coral btn--md" style={{ marginTop: 22 }} onClick={onProceed}>
        Start the questions
      </button>

      <div style={{ marginTop: 16 }}>
        <button
          onClick={onRetry}
          style={{
            fontFamily: 'var(--font-display)', fontWeight: 700, fontSize: 14,
            color: 'var(--muted)',
          }}
        >
          Not your address? Try another →
        </button>
      </div>

      <div className="dashed-note" style={{ margin: '22px auto 0', maxWidth: 340, textAlign: 'left' }}>
        <strong>This list is all we keep.</strong> Your address was used to find
        these districts and then dropped — it is never stored and never travels
        with your results.
      </div>
    </main>
  )
}
