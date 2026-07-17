// Static consistency between the shipped app data and the resolver config in
// geo.js: every supported county must be recognizable from a geocode, and
// every DISTRICT scope in the data must be producible by some configured
// layer for its county (or by the census-derived districts).
import test from 'node:test'
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { COUNTY_IDS, COUNTY_LAYERS, KING_LAYERS } from './geo.js'

const data = JSON.parse(
  readFileSync(new URL('../../public/data/app-data.json', import.meta.url), 'utf8')
)

// Scopes that are knowingly unresolvable, with the reason documented at the
// definition site. Keep this list short and deliberate.
const UNRESOLVABLE_SCOPES = new Set([
  'spokane/AQUIFER', // no official West Plains APA boundary exists (build_spokane_lite_data.py)
  // Counties whose commissioner districts have no queryable official boundary
  // (see build_votewa_lite_data.py); their packages claim partial_county.
  'adams/COUNTY_COUNCIL',
  'asotin/COUNTY_COUNCIL',
  'douglas/COUNTY_COUNCIL',
  'garfield/COUNTY_COUNCIL',
  'grays-harbor/COUNTY_COUNCIL',
  'lincoln/COUNTY_COUNCIL',
  'okanogan/COUNTY_COUNCIL',
  'pacific/COUNTY_COUNCIL',
  // PUD commissioner districts with no queryable boundary (island's PUD race
  // is Snohomish PUD No. 1 District 1 on Camano; klickitat's PUD publishes
  // PDF maps only).
  'island/PUDDST',
  'klickitat/PUDDST',
])

const CENSUS_LAYERS = new Set(['CONGDST', 'LEGDST', 'CITY'])

test('every supported county has a FIPS mapping in geo.js', () => {
  const ids = new Set(Object.values(COUNTY_IDS))
  for (const county of data.coverage.supported_counties) {
    assert.ok(ids.has(county.id), `county ${county.id} missing from COUNTY_IDS`)
    assert.equal(COUNTY_IDS[county.fips], county.id, `FIPS ${county.fips} must map to ${county.id}`)
  }
})

test('every DISTRICT scope layer in the data is resolvable for its county', () => {
  const supported = new Set(data.coverage.supported_counties.map((c) => c.id))
  const layersFor = (county) =>
    county === 'king'
      ? new Set(Object.keys(KING_LAYERS))
      : new Set((COUNTY_LAYERS[county] || []).map((l) => l.key))
  for (const item of [...data.contests, ...data.measures]) {
    const scope = item.scope
    if (!scope || scope.kind !== 'DISTRICT') continue
    assert.ok(supported.has(scope.county), `${item.slug}: county ${scope.county} not supported`)
    if (CENSUS_LAYERS.has(scope.layer)) continue
    if (UNRESOLVABLE_SCOPES.has(`${scope.county}/${scope.layer}`)) continue
    assert.ok(
      layersFor(scope.county).has(scope.layer),
      `${item.slug}: layer ${scope.layer} not configured for ${scope.county}`
    )
  }
})

test('every supported county with local DISTRICT scopes has a District Adapter', () => {
  for (const county of data.coverage.supported_counties) {
    if (county.id === 'king') continue
    const needsLocal = [...data.contests, ...data.measures].some(
      (i) =>
        i.scope?.kind === 'DISTRICT' &&
        i.scope.county === county.id &&
        !CENSUS_LAYERS.has(i.scope.layer) &&
        !UNRESOLVABLE_SCOPES.has(`${county.id}/${i.scope.layer}`)
    )
    if (needsLocal) {
      assert.ok(
        (COUNTY_LAYERS[county.id] || []).length,
        `county ${county.id} has local scopes but no configured layers`
      )
    }
  }
})
