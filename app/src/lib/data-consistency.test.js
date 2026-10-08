// Static consistency between the shipped app data and the resolver config in
// geo.js: every supported county must be recognizable from a geocode, and
// every DISTRICT scope in the data must be producible by some configured
// layer for its county (or by the census-derived districts).
//
// Every election listed in the index is checked, not only the active one, so
// an archived election's data (still served at /washington-state/<id>) stays
// guarded. An election with no contests yet passes trivially; checks on the
// `coverage` block apply only once it claims statewide_complete.
import test from 'node:test'
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { COUNTY_IDS, COUNTY_LAYERS, KING_LAYERS } from './geo.js'
import { DISTRICT_LABELS, describeDistrict } from './districts.js'
import { ELECTION_INDEX_PATH, activeAppDataPath, appDataPath } from './elections.js'

// Read each election's data the same way the app does: through the election
// index.
const readPublic = (path) =>
  JSON.parse(readFileSync(new URL(`../../public/${path}`, import.meta.url), 'utf8'))
const electionIndex = readPublic(ELECTION_INDEX_PATH)
const elections = electionIndex.elections.map((entry) => ({
  entry,
  data: readPublic(appDataPath(entry)),
  dossierQueue: JSON.parse(
    readFileSync(
      new URL(`../../../data/final/${entry.id}/dossier-batches.json`, import.meta.url),
      'utf8'
    )
  ),
}))

test('the index names a listed active election and every entry has its app id', () => {
  assert.doesNotThrow(() => activeAppDataPath(electionIndex))
  for (const { entry, data } of elections) {
    assert.ok(entry.app_id, `${entry.id}: index entry has no app_id`)
    assert.equal(data.election.id, entry.app_id, `${entry.id}: app-data election.id`)
    assert.equal(data.data_version, entry.data_version, `${entry.id}: data_version`)
    assert.equal(
      entry.status,
      entry.id === electionIndex.active ? 'active' : 'archived',
      `${entry.id}: status`
    )
  }
})

const eachElection = (name, fn) => {
  for (const { entry, data, dossierQueue } of elections)
    test(`${name} [${entry.id}]`, () => fn(data, dossierQueue))
}
const eachCompleteElection = (name, fn) =>
  eachElection(name, (data, queue) => {
    if (data.coverage.statewide_complete) fn(data, queue)
  })

// The rubric and interview are hand-authored per election, so their shape is
// checked per election: the primary keeps its 14 axes, while the general
// split `social` and added `parental-rights` (issue #4).
const EXPECTED_AXES = {
  '2026-08-04-primary': 14,
  '2026-11-03-general': 15,
}

test('each election ships its own rubric size', () => {
  for (const { entry, data } of elections) {
    if (!(entry.id in EXPECTED_AXES)) continue
    assert.equal(data.rubric.axes.length, EXPECTED_AXES[entry.id], `${entry.id}: rubric axis count`)
  }
  const general = elections.find(({ entry }) => entry.id === '2026-11-03-general')?.data
  const primary = elections.find(({ entry }) => entry.id === '2026-08-04-primary')?.data
  if (general) assert.ok(general.rubric.axes.some((a) => a.id === 'parental-rights'))
  if (primary) assert.ok(!primary.rubric.axes.some((a) => a.id === 'parental-rights'))
})

eachElection('rubric axis ids are unique and the interview reaches every axis', (data) => {
  const ids = data.rubric.axes.map((a) => a.id)
  assert.equal(new Set(ids).size, ids.length, 'duplicate rubric axis id')
  const known = new Set(ids)
  const reached = new Set()
  for (const item of data.interview.items) {
    const axes = item.kind === 'statement' ? [item.axis] : item.options.flatMap((o) => Object.keys(o.effects))
    for (const axis of axes) {
      assert.ok(known.has(axis), `${item.id}: unknown axis ${axis}`)
      reached.add(axis)
    }
  }
  for (const id of ids) assert.ok(reached.has(id), `axis ${id}: no interview item asks about it`)
})

eachElection('judges are never scorable on social or parental-rights', (data) => {
  const JUDICIAL = ['StateSupremeCourt', 'DistrictCourt', 'Judicial']
  for (const axis of data.rubric.axes.filter((a) => ['social', 'parental-rights'].includes(a.id))) {
    for (const category of JUDICIAL) {
      assert.ok(!axis.applies_to.includes(category), `${axis.id} applies to ${category}`)
    }
  }
})

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
  // Spokane voters inside Public Utility District No. 1 of Stevens County
  // vote for its commissioner seat; no electoral boundary layer for the
  // PUD's Spokane territory is published (the county's Water Districts layer
  // maps water-service areas, not electoral boundaries;
  // build_spokane_lite_data.py general_override), so the general's Spokane
  // package is partial_county.
  'spokane/PUDDST',
])

const CENSUS_LAYERS = new Set(['CONGDST', 'LEGDST', 'CITY'])

eachCompleteElection('every supported county has a FIPS mapping in geo.js', (data) => {
  const ids = new Set(Object.values(COUNTY_IDS))
  for (const county of data.coverage.supported_counties) {
    assert.ok(ids.has(county.id), `county ${county.id} missing from COUNTY_IDS`)
    assert.equal(COUNTY_IDS[county.fips], county.id, `FIPS ${county.fips} must map to ${county.id}`)
  }
})

eachElection('every DISTRICT scope layer in the data is resolvable for its county', (data) => {
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

eachCompleteElection('every supported county with local DISTRICT scopes has a District Adapter', (data) => {
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

eachElection('release data has no unfinished contested candidate dossiers', (data, dossierQueue) => {
  assert.equal(dossierQueue.total_units, 0)
  assert.equal(dossierQueue.total_dossiers, 0)
  assert.equal(dossierQueue.total_batches, 0)
  for (const contest of data.contests.filter((item) => item.candidates.length >= 2)) {
    for (const candidate of contest.candidates) {
      assert.notEqual(
        candidate.evidence_level,
        'official-ballot-only',
        `${contest.slug}/${candidate.slug} is still ballot-only`
      )
      assert.ok(candidate.sources.length, `${contest.slug}/${candidate.slug} has no assembled sources`)
      const sourceIds = new Set(candidate.sources.map((source) => source.id))
      for (const [axis, score] of Object.entries(candidate.scores || {})) {
        for (const citation of score.citations || []) {
          assert.ok(sourceIds.has(citation), `${contest.slug}/${candidate.slug}/${axis}: missing ${citation}`)
        }
      }
    }
  }
})

eachElection('researched county measures are present in the shipped app data', (data) => {
  for (const measure of data.measures.filter((item) => item.owner !== 'king')) {
    assert.ok(measure.what_it_does, `${measure.slug}: missing what_it_does`)
    assert.ok(measure.cost_line, `${measure.slug}: missing cost_line`)
    assert.ok(measure.pro_summary, `${measure.slug}: missing pro_summary`)
    assert.ok(measure.con_summary, `${measure.slug}: missing con_summary`)
    assert.equal(typeof measure.lean_mappings, 'object', `${measure.slug}: bad lean_mappings`)
  }
})

// CITY is deliberately absent from DISTRICT_LABELS: describeDistrict renders it
// as 'City of X' rather than a numbered district.
const UNLABELED_BY_DESIGN = new Set(['CITY'])

eachElection('every district layer a voter can be placed in has a voter-facing label', (data) => {
  const configured = new Set([
    ...Object.keys(KING_LAYERS),
    ...Object.values(COUNTY_LAYERS).flatMap((layers) => layers.map((l) => l.key)),
  ])
  for (const item of [...data.contests, ...data.measures]) {
    if (item.scope?.kind === 'DISTRICT') configured.add(item.scope.layer)
  }
  for (const layer of configured) {
    if (UNLABELED_BY_DESIGN.has(layer)) continue
    assert.ok(
      DISTRICT_LABELS[layer],
      `layer ${layer} has no entry in DISTRICT_LABELS, so voters would see the raw key`
    )
  }
})

eachElection('every district value in the shipped data renders as readable text', (data) => {
  for (const item of [...data.contests, ...data.measures]) {
    const scope = item.scope
    if (scope?.kind !== 'DISTRICT') continue
    const text = describeDistrict(scope.layer, scope.value)
    assert.ok(text, `${item.slug}: ${scope.layer}=${scope.value} produced no label`)
    assert.ok(
      !/^[A-Z_]+ /.test(text) || DISTRICT_LABELS[scope.layer],
      `${item.slug}: ${scope.layer} fell through to the raw-key fallback`
    )
  }
})
