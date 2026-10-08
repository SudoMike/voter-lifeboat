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
  // King's general pamphlet PDFs are kingcounty.gov links, but nothing may
  // point at the primary's pamphlets (voters-pamphlets/2026/08) or copy.
  const { pamphletPdfs, ...copy } = g
  assert.doesNotMatch(JSON.stringify(copy), /primary|top 2|kingcounty/i)
  assert.doesNotMatch(JSON.stringify(pamphletPdfs), /primary|top 2|\/2026\/08\//i)
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
    // Spokane's and Pierce's measures cite VoteWA's unpaged online guide (countyGuides).
    if (m.owner === 'spokane' || m.owner === 'pierce') continue
    assert.match(pamphletLink(m.pamphlet_pages, m.owner, general.election.id), /#page=\d+$/, m.slug)
    n++
  }
  assert.ok(n > 3)
})

test('King general pages link the KCE local pamphlet or the SOS King edition at that page', () => {
  assert.equal(
    pamphletLink([{ edition: 'local-edition', page: 60 }], 'king', general.election.id),
    'https://cdn.kingcounty.gov/-/media/king-county/depts/elections/how-to-vote/voters-pamphlets/2026/11/local-edition.pdf#page=60'
  )
  assert.match(
    pamphletLink([{ edition: 'voters-pamphlet-edition-04-king-seattle', page: 24 }], 'king', general.election.id),
    /^https:\/\/www\.sos\.wa\.gov\/.*Edition%2004%C2%A0-%20King%20-%20Seattle\.pdf#page=24$/
  )
  // Every King candidate and measure with pamphlet pages gets a paged link to
  // one of those four PDFs, never the unpaged SOS index.
  let n = 0
  for (const item of [...general.contests, ...general.measures]) {
    if (item.owner !== 'king') continue
    const pages = item.candidates ? item.candidates.map((c) => c.pamphlet_pages) : [item.pamphlet_pages]
    for (const p of pages.filter((x) => x?.length)) {
      assert.match(
        pamphletLink(p, 'king', general.election.id),
        /^https:\/\/(cdn\.kingcounty\.gov|www\.sos\.wa\.gov\/sites)\/.*\.pdf#page=\d+$/,
        item.slug
      )
      n++
    }
  }
  assert.ok(n > 150, `${n} King pamphlet links`)
})

test('Spokane general records, which cite VoteWA\'s unpaged online guide, link that guide', () => {
  const GUIDE = 'https://voter.votewa.gov/genericvoterguide.aspx?e=899&c=32'
  assert.equal(pamphletLink([], 'spokane', general.election.id), GUIDE)
  assert.equal(pamphletLink(undefined, 'spokane', general.election.id), GUIDE)
  assert.equal(pamphletLink([{ edition: 'unknown', page: 3 }], 'spokane', general.election.id), GUIDE)
  // Snohomish has no county guide; the primary keeps its PDF and no guide.
  assert.equal(pamphletLink([], 'snohomish', general.election.id), null)
  assert.equal(pamphletLink([], 'spokane', primary.election.id), null)
  assert.equal(
    pamphletLink([{ edition: 'local-voters-pamphlet', page: 4 }], 'spokane', primary.election.id),
    'https://www.spokanecounty.gov/DocumentCenter/View/72507/August-4-2026-Primary-Election-Voters-Pamphlet-PDF#page=4'
  )
})

test('Snohomish general pages link the county Local Voters\' Pamphlet at that page', () => {
  assert.equal(
    pamphletLink([{ edition: 'local-voters-pamphlet', page: 92 }], 'snohomish', general.election.id),
    'https://www.snohomishcountywa.gov/DocumentCenter/View/151457#page=92'
  )
  // The primary keeps its own Snohomish pamphlet.
  assert.equal(
    pamphletLink([{ edition: 'local-voters-pamphlet', page: 2 }], 'snohomish', primary.election.id),
    'https://www.snohomishcountywa.gov/DocumentCenter/View/149774#page=2'
  )
  let n = 0
  for (const item of [...general.contests, ...general.measures]) {
    if (item.owner !== 'snohomish') continue
    const pages = item.candidates ? item.candidates.map((c) => c.pamphlet_pages) : [item.pamphlet_pages]
    for (const p of pages.filter((x) => x?.length)) {
      assert.match(
        pamphletLink(p, 'snohomish', general.election.id),
        /^https:\/\/www\.snohomishcountywa\.gov\/DocumentCenter\/View\/151457#page=\d+$/,
        item.slug
      )
      n++
    }
  }
  assert.ok(n > 40, `${n} Snohomish pamphlet links`)
})

test('the shipped general links Spokane County Elections directly', () => {
  assert.deepEqual(countyElectionsOffice(general, { id: 'spokane', name: 'Spokane County' }), {
    name: 'Spokane County Elections',
    url: 'https://www.spokanecounty.gov/elections',
    direct: true,
  })
  // Every shipped Spokane record links the county's VoteWA guide.
  for (const item of [...general.contests, ...general.measures]) {
    if (item.owner !== 'spokane') continue
    const pages = item.candidates ? item.candidates.map((c) => c.pamphlet_pages) : [item.pamphlet_pages]
    for (const p of pages) {
      assert.equal(pamphletLink(p, 'spokane', general.election.id), 'https://voter.votewa.gov/genericvoterguide.aspx?e=899&c=32', item.slug)
    }
  }
})

test('Pierce general records link SOS Edition 09 at the cited page, else the Pierce VoteWA guide', () => {
  const GUIDE = 'https://voter.votewa.gov/genericvoterguide.aspx?e=899&c=27'
  const ED09 = 'https://www.sos.wa.gov/sites/default/files/2026-10/Voters%20Pamphlet%202026%20-%20Edition%2009%20-%20Pierce.pdf'
  assert.equal(pamphletLink([{ edition: 'voters-pamphlet-edition-09-pierce', page: 24 }], 'pierce', general.election.id), `${ED09}#page=24`)
  assert.equal(pamphletLink([], 'pierce', general.election.id), GUIDE)
  assert.deepEqual(countyElectionsOffice(general, { id: 'pierce', name: 'Pierce County' }), {
    name: 'Pierce County Elections',
    url: 'https://www.piercecountywa.gov/elections',
    direct: true,
  })
  let paged = 0
  for (const item of [...general.contests, ...general.measures]) {
    if (item.owner !== 'pierce') continue
    const pages = item.candidates ? item.candidates.map((c) => c.pamphlet_pages) : [item.pamphlet_pages]
    for (const p of pages) {
      const link = pamphletLink(p, 'pierce', general.election.id)
      if (p?.length) {
        assert.match(link, /Edition%2009%20-%20Pierce\.pdf#page=\d+$/, item.slug)
        paged++
      } else {
        assert.equal(link, GUIDE, item.slug)
      }
    }
  }
  // CD 6 and 10 and the legislative seats Pierce researched itself.
  assert.ok(paged >= 30, `${paged} Pierce paged links`)
})

test('the shipped general links Snohomish County Elections directly', () => {
  assert.deepEqual(countyElectionsOffice(general, { id: 'snohomish', name: 'Snohomish County' }), {
    name: 'Snohomish County Elections',
    url: 'https://www.snohomishcountywa.gov/224/Elections-Voter-Registration',
    direct: true,
  })
})

test('the shipped general links King County Elections directly', () => {
  assert.deepEqual(countyElectionsOffice(general, { id: 'king', name: 'King County' }), {
    name: 'King County Elections',
    url: 'https://kingcounty.gov/en/dept/elections',
    direct: true,
  })
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
  assert.deepEqual(countyElectionsOffice(general, { id: 'yakima', name: 'Yakima County' }), {
    name: 'Yakima County Elections',
    url: COUNTY_OFFICES_URL,
    direct: false,
  })
})

test('no county, no county office', () => {
  assert.equal(countyElectionsOffice(general, null), null)
  assert.equal(countyElectionsOffice(general, {}), null)
})
