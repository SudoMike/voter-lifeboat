// Profile <-> URL hash fragment. The fragment never reaches any server
// (ours included) — that's the whole point. Compact keys keep URLs short.
//
// payload: { v: dataVersion, d: districts, a: {axis: [value, weight]} }

const b64url = (s) => btoa(s).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '')
const unb64url = (s) => atob(s.replace(/-/g, '+').replace(/_/g, '/'))

export function encodeProfile(dataVersion, districts, answers) {
  const a = {}
  for (const [axis, { v, w }] of Object.entries(answers)) a[axis] = [v, w]
  const json = JSON.stringify({ v: dataVersion, d: districts, a })
  return b64url(unescape(encodeURIComponent(json)))
}

export function decodeProfile(fragment) {
  try {
    const json = decodeURIComponent(escape(unb64url(fragment)))
    const p = JSON.parse(json)
    if (!p || typeof p !== 'object' || !p.d || !p.a) return null
    const answers = {}
    for (const [axis, [v, w]] of Object.entries(p.a)) {
      if (typeof v !== 'number' || typeof w !== 'number') return null
      answers[axis] = { v: Math.max(-2, Math.min(2, v)), w }
    }
    return { dataVersion: p.v, districts: p.d, answers }
  } catch {
    return null
  }
}

export function readHash() {
  const m = location.hash.match(/#p=([A-Za-z0-9_-]+)/)
  return m ? decodeProfile(m[1]) : null
}

export function writeHash(dataVersion, districts, answers) {
  const frag = encodeProfile(dataVersion, districts, answers)
  history.replaceState(null, '', `#p=${frag}`)
  return `${location.origin}${location.pathname}#p=${frag}`
}

export function clearHash() {
  history.replaceState(null, '', location.pathname)
}
