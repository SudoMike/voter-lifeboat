import test from 'node:test'
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import {
  VOTEWA_URL,
  DROP_BOX_URL,
  COUNTY_OFFICES_URL,
  electionGuide,
  pamphletLink,
  countyElectionsOffice,
} from './officialLinks.js'

const load = (id) =>
  JSON.parse(readFileSync(new URL(`../../public/data/${id}/app-data.json`, import.meta.url), 'utf8'))
const general = load('2026-11-03-general')
const primary = load('2026-08-04-primary')

const SOS_EDITION_06 =
  'https://www.sos.wa.gov/sites/default/files/2026-10/Voters%20Pamphlet%202026%20-%20Edition%2006%20-%20King%20-%20South%20and%20Southeast.pdf'

test('official voter URLs are https and on the state election sites', () => {
  assert.equal(VOTEWA_URL, 'https://voter.votewa.gov/')
  assert.match(DROP_BOX_URL, /^https:\/\/www\.sos\.wa\.gov\/elections\/.*drop-box/)
  assert.match(COUNTY_OFFICES_URL, /^https:\/\/www\.sos\.wa\.gov\/elections\/.*county-elections-offices$/)
})

test('the general links the SOS voters guide and has no primary-only copy', () => {
  const g = electionGuide(general.election)
  assert.equal(g.kind, 'general')
  assert.match(g.statePamphlet.url, /^https:\/\/www\.sos\.wa\.gov\/.*2026-general-election-voters-guide$/)
  assert.doesNotMatch(JSON.stringify(g), /primary|top 2|kingcounty/i)
})

test('the archived primary keeps its own King pamphlet link and top-2 note', () => {
  const g = electionGuide(primary.election)
  assert.equal(g.kind, 'primary')
  assert.match(g.statePamphlet.url, /kingcounty\.gov/)
  assert.match(g.resultsNote, /top 2/)
})

test('an unknown election falls back to the SOS pamphlet archive with no kind-specific copy', () => {
  const g = electionGuide({ id: '2027-11-02-general', day: '2027-11-02' })
  assert.match(g.statePamphlet.url, /^https:\/\/www\.sos\.wa\.gov\//)
  assert.equal(g.resultsNote, null)
  assert.equal(electionGuide(undefined).resultsNote, null)
})

test('statewide general pages link the cited SOS edition PDF at that page', () => {
  assert.equal(
    pamphletLink([{ edition: 'edition-06', page: 9 }], 'statewide', general.election.id),
    `${SOS_EDITION_06}#page=9`
  )
})

test('an uncataloged general edition links the SOS pamphlet PDFs page, unpaged', () => {
  const url = pamphletLink([{ edition: 'edition-99', page: 3 }], 'statewide', general.election.id)
  assert.match(url, /^https:\/\/www\.sos\.wa\.gov\/.*2026-voters-pamphlet-pdfs$/)
})

test('no pages, no link', () => {
  assert.equal(pamphletLink([], 'statewide', general.election.id), null)
  assert.equal(pamphletLink(undefined, 'king', primary.election.id), null)
})

test('primary pages keep their county editions (and King for statewide contests)', () => {
  assert.match(
    pamphletLink([{ edition: 'edition-1', page: 4 }], 'statewide', primary.election.id),
    /kingcounty\.gov\/.*2026\/08\/english\/edition-1\.pdf#page=4$/
  )
  assert.match(
    pamphletLink([{ edition: 'local-voters-pamphlet', page: 2 }], 'spokane', primary.election.id),
    /spokanecounty\.gov\/.*#page=2$/
  )
  // A general edition id means nothing in the primary.
  assert.equal(pamphletLink([{ edition: 'edition-06', page: 9 }], 'statewide', primary.election.id), null)
})

test('every statewide contest and measure in the shipped general gets a paged SOS link', () => {
  let n = 0
  for (const c of general.contests)
    for (const cand of c.candidates)
      if (cand.pamphlet_pages?.length) {
        assert.match(pamphletLink(cand.pamphlet_pages, c.owner, general.election.id), /#page=\d+$/, cand.slug)
        n++
      }
  for (const m of general.measures) {
    assert.match(pamphletLink(m.pamphlet_pages, m.owner, general.election.id), /#page=\d+$/, m.slug)
    n++
  }
  assert.ok(n > 3)
})

test('county elections office comes from coverage.supported_counties elections_url', () => {
  const data = {
    coverage: {
      supported_counties: [
        { id: 'king', name: 'King County', elections_url: 'https://kingcounty.gov/en/dept/elections' },
        { id: 'pierce', name: 'Pierce County' },
      ],
    },
  }
  assert.deepEqual(countyElectionsOffice(data, { id: 'king', name: 'King County' }), {
    name: 'King County Elections',
    url: 'https://kingcounty.gov/en/dept/elections',
    direct: true,
  })
})

test('a known county without its own URL gets the SOS county offices directory', () => {
  const data = { coverage: { supported_counties: [{ id: 'pierce', name: 'Pierce County' }] } }
  assert.deepEqual(countyElectionsOffice(data, { id: 'pierce', name: 'Pierce County' }), {
    name: 'Pierce County Elections',
    url: COUNTY_OFFICES_URL,
    direct: false,
  })
  assert.deepEqual(countyElectionsOffice(general, { id: 'spokane', name: 'Spokane County' }), {
    name: 'Spokane County Elections',
    url: COUNTY_OFFICES_URL,
    direct: false,
  })
})

test('no county, no county office', () => {
  assert.equal(countyElectionsOffice(general, null), null)
  assert.equal(countyElectionsOffice(general, {}), null)
})
