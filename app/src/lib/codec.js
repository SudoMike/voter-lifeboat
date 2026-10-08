// Profile <-> URL hash fragment. The fragment never reaches any server.
//
// payload: {
//   s: schema version,
//   e: election id,
//   v: data version,
//   c: ballot context,
//   a: {axis: [value, weight]},
//   f: (optional) election id the answers were given for, when it differs
//      from `e` — set by the Results page's link to an archived election
// }

const b64url = (s) => btoa(s).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '')
const unb64url = (s) => atob(s.replace(/-/g, '+').replace(/_/g, '/'))

export function encodeProfile(data, context, answers, { from } = {}) {
  const a = {}
  for (const [axis, { v, w }] of Object.entries(answers)) a[axis] = [v, w]
  const safeContext = {
    coverageStatus: context.coverageStatus,
    county: context.county
      ? {
          id: context.county.id,
          fips: context.county.fips,
          name: context.county.name,
        }
      : undefined,
    districts: context.districts || {},
    missingLayers: context.missingLayers || [],
  }
  const json = JSON.stringify({
    s: 2,
    e: data.election?.id,
    v: data.data_version,
    c: safeContext,
    a,
    ...(from && from !== data.election?.id ? { f: from } : {}),
  })
  return b64url(unescape(encodeURIComponent(json)))
}

/**
 * Encode a profile for another election's page, named by its index entry
 * (elections.json). `e` is the entry's `app_id` and `v` its `data_version`,
 * the two values that page compares against its own `data.election.id` and
 * `data.data_version`, so it shows no "data updated" banner. `from` is the
 * app id of the election the answers were given for.
 */
export function encodeProfileForElection(entry, context, answers, from) {
  return encodeProfile(
    { election: { id: entry.app_id }, data_version: entry.data_version },
    context,
    answers,
    { from }
  )
}

export function decodeProfile(fragment) {
  try {
    const json = decodeURIComponent(escape(unb64url(fragment)))
    const p = JSON.parse(json)
    if (!p || typeof p !== 'object' || !p.a) return null
    const context = p.c || (p.d ? { coverageStatus: 'full_county', county: { id: 'king', fips: '53033', name: 'King County' }, districts: p.d } : null)
    if (!context) return null
    // A tampered or corrupted link must not overclaim coverage or distort the
    // scoring weights; unknown statuses degrade to the partial-county banner.
    const statuses = ['full_county', 'partial_county', 'statewide_only']
    if (!statuses.includes(context.coverageStatus)) context.coverageStatus = 'partial_county'
    const answers = {}
    for (const [axis, [v, w]] of Object.entries(p.a)) {
      if (typeof v !== 'number' || typeof w !== 'number') return null
      answers[axis] = { v: Math.max(-2, Math.min(2, v)), w: Math.max(0, Math.min(4, w)) }
    }
    return {
      schema: p.s || 1,
      electionId: p.e,
      dataVersion: p.v,
      fromElectionId: typeof p.f === 'string' ? p.f : undefined,
      context,
      districts: context.districts || {},
      answers,
    }
  } catch {
    return null
  }
}

export function readHash() {
  const m = location.hash.match(/#p=([A-Za-z0-9_-]+)/)
  return m ? decodeProfile(m[1]) : null
}

export function writeHash(data, context, answers, opts) {
  const frag = encodeProfile(data, context, answers, opts)
  history.replaceState(null, '', `${location.pathname}#p=${frag}`)
  return `${location.origin}${location.pathname}#p=${frag}`
}

export function clearHash() {
  history.replaceState(null, '', location.pathname)
}
