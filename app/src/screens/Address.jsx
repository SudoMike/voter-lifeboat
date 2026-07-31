import React, { useEffect, useRef, useState } from 'react'
import { lookupBallotContext, suggestAddresses, hasZip, withZip, GeoError } from '../lib/geo.js'

// 'no-match' means we could not place the line, which is nearly always a
// fixable typo — keep it distinct from the out-of-coverage headline so it does
// not read as "your town is not supported".
const ERROR_HEADLINES = {
  'no-match': "We couldn't find that address",
  'outside-wa': "We're off the map",
  'unsupported-county': "We're off the map",
  'no-districts': 'That one puzzled us',
  network: 'Rough seas',
}

export default function Address({ data, onBack, onFound }) {
  const [addr, setAddr] = useState('')
  const [busy, setBusy] = useState(false)
  const [err, setErr] = useState(null)
  const [suggestions, setSuggestions] = useState([])
  const [open, setOpen] = useState(false)
  const [activeIndex, setActiveIndex] = useState(-1)
  // The exact line we submitted, so a ZIP retry rebuilds from it rather than
  // from whatever the voter has since typed into the retry box.
  const [tried, setTried] = useState('')
  const [zip, setZip] = useState('')
  const blurTimer = useRef(null)

  useEffect(() => {
    const controller = new AbortController()
    const timer = setTimeout(async () => {
      try {
        const results = await suggestAddresses(addr, { signal: controller.signal })
        setSuggestions(results)
        setActiveIndex(-1)
        setOpen(results.length > 0)
      } catch {
        // stale request aborted, or the suggest lookup failed — no dropdown, not fatal
      }
    }, 200)
    return () => {
      clearTimeout(timer)
      controller.abort()
    }
  }, [addr])

  const go = async (e, addressOverride) => {
    e?.preventDefault()
    const address = (addressOverride ?? addr).trim()
    if (!address || busy) return
    setOpen(false)
    setBusy(true)
    setErr(null)
    setTried(address)
    try {
      const context = await lookupBallotContext(data, address)
      onFound(context)
    } catch (ex) {
      setErr(
        ex instanceof GeoError
          ? ex
          : new GeoError('Something went wrong looking that up.', 'network')
      )
      setBusy(false)
    }
  }

  const pick = (suggestion) => {
    setAddr(suggestion.label)
    setSuggestions([])
    setOpen(false)
    go(null, suggestion.label)
  }

  // A no-match on a line with no ZIP is usually a missing city, not a typo, so
  // ask for the one piece that fixes it instead of sending them back to a blank
  // box. If the retry fails too, the standard error screen takes over.
  const askedForZip = err?.kind === 'no-match' && !hasZip(tried)

  const retryWithZip = (e) => {
    e?.preventDefault()
    const z = zip.trim()
    if (!/^\d{5}$/.test(z)) return
    const composed = withZip(tried, z)
    // Keep the visible box in step, so if this retry also fails the voter is
    // editing the line we actually sent.
    setAddr(composed)
    go(null, composed)
  }

  const onKeyDown = (e) => {
    if (!open || suggestions.length === 0) return
    if (e.key === 'ArrowDown') {
      e.preventDefault()
      setActiveIndex((i) => (i + 1) % suggestions.length)
    } else if (e.key === 'ArrowUp') {
      e.preventDefault()
      setActiveIndex((i) => (i <= 0 ? suggestions.length - 1 : i - 1))
    } else if (e.key === 'Enter' && activeIndex >= 0) {
      e.preventDefault()
      pick(suggestions[activeIndex])
    } else if (e.key === 'Escape') {
      setOpen(false)
    }
  }

  if (busy)
    return (
      <main className="screen screen--app rise" style={{ padding: '60px 24px 56px', textAlign: 'center' }}>
        <h1 className="display display--md">Finding your ballot…</h1>
        <p className="copy" style={{ marginTop: 10, fontSize: 14 }}>
          Looking up your county and voting districts.
          <br />
          This is the only thing that leaves your browser.
        </p>
        <div className="bar bar--busy" style={{ margin: '22px auto 0', width: 150 }} role="progressbar" aria-label="Loading">
          <i />
        </div>
      </main>
    )

  if (askedForZip)
    return (
      <main className="screen screen--app rise" style={{ padding: '44px 24px 40px', textAlign: 'center' }}>
        <div
          style={{
            width: 64, height: 64, margin: '0 auto', borderRadius: '50%',
            background: 'var(--seafoam-tint)', display: 'flex', alignItems: 'center',
            justifyContent: 'center', fontSize: 28, color: 'var(--seafoam)', fontWeight: 800,
          }}
        >
          ⌖
        </div>
        <h1 className="display display--md" style={{ marginTop: 14 }}>
          Almost — what's your ZIP?
        </h1>
        <p className="copy" style={{ margin: '10px auto 0', maxWidth: 320 }}>
          A street on its own can sit in a dozen towns, so we couldn't place{' '}
          <strong>{tried}</strong>. Your ZIP code is usually all it needs.
        </p>
        <form onSubmit={retryWithZip}>
          <div className="input" style={{ margin: '20px auto 0', maxWidth: 150, textAlign: 'left' }}>
            <input
              type="text"
              inputMode="numeric"
              maxLength={5}
              placeholder="98059"
              aria-label="ZIP code"
              value={zip}
              onChange={(e) => setZip(e.target.value.replace(/\D/g, ''))}
              autoFocus
            />
          </div>
          <button
            className="btn btn--coral btn--sm"
            style={{ marginTop: 16, opacity: zip.trim().length === 5 ? 1 : 0.5 }}
            type="submit"
            disabled={zip.trim().length !== 5}
          >
            Find my ballot
          </button>
        </form>
        <button
          onClick={() => {
            setErr(null)
            setZip('')
          }}
          style={{
            marginTop: 18, fontFamily: 'var(--font-display)', fontWeight: 700,
            fontSize: 14, color: 'var(--muted)',
          }}
        >
          ← edit the address instead
        </button>
      </main>
    )

  if (err)
    return (
      <main className="screen screen--app rise" style={{ padding: '44px 24px 40px', textAlign: 'center' }}>
        <div
          style={{
            width: 64, height: 64, margin: '0 auto', borderRadius: '50%',
            background: 'var(--coral-tint)', display: 'flex', alignItems: 'center',
            justifyContent: 'center', fontSize: 28, color: 'var(--coral)', fontWeight: 800,
          }}
        >
          ?
        </div>
        <h1 className="display display--md" style={{ marginTop: 14 }}>
          {ERROR_HEADLINES[err.kind] || "We couldn't find that address"}
        </h1>
        <p className="copy" style={{ margin: '10px auto 0', maxWidth: 300 }}>
          {err.kind === 'no-match' &&
            "We couldn't match that address, even with the ZIP. Check the street number and name, or try a neighbor's address — any address on your block finds the same ballot."}
          {err.kind === 'outside-wa' &&
            'That address looks like it is outside Washington State. This guide supports Washington elections only.'}
          {err.kind === 'unsupported-county' &&
            'That Washington county is not covered yet, and the statewide fallback is not available for this election data.'}
          {err.kind === 'no-districts' &&
            'We found the address but could not resolve its voting districts. Double-check the address, or try again in a moment.'}
          {err.kind === 'network' &&
            'A lookup service did not answer. Give it a moment and try again.'}
        </p>
        <form onSubmit={go}>
          <div className="input input--error" style={{ margin: '20px auto 0', maxWidth: 300, textAlign: 'left' }}>
            <input
              type="text"
              value={addr}
              onChange={(e) => setAddr(e.target.value)}
              aria-label="Street address"
              aria-invalid="true"
            />
          </div>
          <button className="btn btn--navy btn--sm" style={{ marginTop: 16 }} type="submit">
            Try again
          </button>
        </form>
        <p style={{ margin: '14px 0 0', fontSize: 13, fontWeight: 700, color: 'var(--seafoam)' }}>
          Voter Lifeboat currently supports Washington State elections.
        </p>
      </main>
    )

  return (
    <main className="screen screen--app rise" style={{ paddingBottom: 28 }}>
      <nav style={{ padding: '20px 24px' }}>
        <button
          onClick={onBack}
          style={{ fontFamily: 'var(--font-display)', fontWeight: 700, fontSize: 15, color: 'var(--muted)' }}
        >
          ← back
        </button>
      </nav>
      <section style={{ padding: '6px 24px 0' }}>
        <h1 className="display display--lg">Where do you call home port?</h1>
        <div className="dashed-note" style={{ marginTop: 12 }}>
          <strong>We do not store your address.</strong> It's only used to
          find your county and districts, then it's forgotten — see{' '}
          <a href="https://github.com/SudoMike/voter-lifeboat" target="_blank" rel="noopener noreferrer">
            the source code
          </a>
          .
        </div>
      </section>
      <form onSubmit={go} autoComplete="off">
        <section style={{ padding: '22px 24px 0' }}>
          <div className="suggest">
            <div className="input">
              <span className="input-icon">⌖</span>
              <input
                type="text"
                placeholder="4218 SW Othello St, Seattle…"
                aria-label="Street address"
                aria-autocomplete="list"
                aria-expanded={open}
                aria-controls="address-suggestions"
                aria-activedescendant={activeIndex >= 0 ? `address-suggestion-${activeIndex}` : undefined}
                role="combobox"
                value={addr}
                onChange={(e) => setAddr(e.target.value)}
                onKeyDown={onKeyDown}
                onFocus={() => suggestions.length > 0 && setOpen(true)}
                onBlur={() => {
                  blurTimer.current = setTimeout(() => setOpen(false), 120)
                }}
                autoComplete="off"
                autoFocus
              />
            </div>
            {open && suggestions.length > 0 && (
              <ul className="suggest-list" id="address-suggestions" role="listbox">
                {suggestions.map((s, i) => (
                  <li key={s.full} role="presentation">
                    <button
                      type="button"
                      id={`address-suggestion-${i}`}
                      role="option"
                      aria-selected={i === activeIndex}
                      className={`suggest-item${i === activeIndex ? ' suggest-item--active' : ''}`}
                      onMouseDown={(e) => e.preventDefault()}
                      onClick={() => pick(s)}
                    >
                      {s.label}
                    </button>
                  </li>
                ))}
              </ul>
            )}
          </div>
          <button className="btn btn--coral btn--md" style={{ marginTop: 16 }} type="submit">
            Find my ballot
          </button>
          <p className="note" style={{ marginTop: 24, color: 'var(--muted)' }}>
            Street address only — no name, no email, no signup. Ever. The address
            goes to the U.S. Census geocoder and official district services to
            find your ballot context, and nowhere else.
          </p>
        </section>
      </form>
    </main>
  )
}
