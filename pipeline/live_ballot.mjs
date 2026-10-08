// Live lookupBallotContext: geocode real addresses with the US Census
// geocoder, query the county District Adapter's live GIS layers exactly as
// the app does (app/src/lib/geo.js), and list the Covered Ballot an
// app-data file gives each address (app/src/lib/scoring.js).
//
// Usage (from the repo root; needs network, no npm install):
//   node pipeline/live_ballot.mjs <app-data.json> "<address>" ["<address>" ...]
//   node pipeline/live_ballot.mjs data/final/2026-11-03-general/app-data.json "930 Tacoma Ave S, Tacoma, WA 98402"
//
// Prints, per address: coverage status, county, resolved districts, layers
// that failed or are missing, the contest and measure counts, and every slug.
// Exit code 1 if any address errors.
import { readFileSync } from 'node:fs'
import { dirname, join, resolve } from 'node:path'
import { fileURLToPath, pathToFileURL } from 'node:url'

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..')
const LIB = join(ROOT, 'app/src/lib')
const [dataPath, ...addresses] = process.argv.slice(2)
if (!dataPath || !addresses.length) {
  console.error('usage: node pipeline/live_ballot.mjs <app-data.json> "<address>" ["<address>" ...]')
  process.exit(2)
}
const { lookupBallotContext, scopeMatches } = await import(pathToFileURL(join(LIB, 'geo.js')).href)
const { contestsOnBallot, measuresOnBallot, axesForBallot } = await import(pathToFileURL(join(LIB, 'scoring.js')).href)
const data = JSON.parse(readFileSync(dataPath, 'utf8'))

// The app proxies the Census geocoder through /api/geocode (server.js);
// here the same query goes straight to the Census API.
const CENSUS = 'https://geocoding.geo.census.gov/geocoder/geographies/onelineaddress'
const realFetch = globalThis.fetch
globalThis.fetch = async (url, opts = {}) => {
  const s = String(url)
  if (s.startsWith('/api/geocode')) {
    const { searchParams } = new URL(s, 'http://internal')
    const a = searchParams.get('address') || ''
    return realFetch(
      `${CENSUS}?address=${encodeURIComponent(a)}&benchmark=Public_AR_Current&vintage=Current_Current&format=json`,
      { signal: AbortSignal.timeout(20000) }
    )
  }
  return realFetch(s, { ...opts, headers: { ...(opts.headers || {}), 'User-Agent': 'Mozilla/5.0 voter-lifeboat-live-ballot' } })
}

let failed = 0
for (const address of addresses) {
  try {
    const ctx = await lookupBallotContext(data, address)
    const contests = contestsOnBallot(data, ctx, scopeMatches)
    const measures = measuresOnBallot(data, ctx, scopeMatches)
    const axes = [...axesForBallot(data, contests, measures)].sort()
    console.log(`ADDRESS ${address}`)
    console.log(`  matched=${ctx.matched} coverage=${ctx.coverageStatus} county=${ctx.county?.id}`)
    console.log(`  districts=${JSON.stringify(ctx.districts)} missing=${JSON.stringify(ctx.missingLayers)}`)
    console.log(`  contests=${contests.length} measures=${measures.length} axes=${axes.join(',')}`)
    for (const c of contests) console.log(`    C ${c.slug} [${c.owner || ''}]${c.uncontested ? ' (info-only)' : ''}`)
    for (const m of measures) console.log(`    M ${m.slug} [${m.owner || ''}]`)
  } catch (e) {
    failed++
    console.log(`ADDRESS ${address}\n  ERROR kind=${e.kind} ${e.message}`)
  }
}
process.exit(failed ? 1 : 0)
