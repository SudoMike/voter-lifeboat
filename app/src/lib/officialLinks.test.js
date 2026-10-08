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
    // Spokane's, Pierce's, Kitsap's, Whatcom's, Benton's, Grant's, Island's,
    // Lewis's, Grays Harbor's, Stevens's, Douglas's, Okanogan's, Pacific's and Adams's measures cite
    // VoteWA's unpaged online guide (countyGuides), as do Whitman's eight that
    // filed hardship waivers (not in its printed pamphlet). Wahkiakum's two
    // cite its sample ballot (no pamphlet) and link its guide (#32).
    if (['spokane', 'pierce', 'kitsap', 'whatcom', 'benton', 'grant', 'island', 'lewis', 'grays-harbor', 'stevens', 'douglas', 'okanogan',
      'pacific', 'adams', 'wahkiakum'].includes(m.owner)) continue
    if (m.owner === 'whitman' && !m.pamphlet_pages.length) continue
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

test('Clark, Kitsap and Thurston general citations link their PDFs at the cited page, else a county guide', () => {
  const id = general.election.id
  assert.equal(
    pamphletLink([{ edition: 'local-voters-pamphlet', page: 86 }], 'clark', id),
    'https://clark.wa.gov/sites/default/files/media/document/2026-09/2026clarkcountygeneralvp_web.pdf#page=86'
  )
  assert.equal(pamphletLink([], 'clark', id), 'https://voter.votewa.gov/genericvoterguide.aspx?e=899&c=06')
  assert.equal(pamphletLink([], 'kitsap', id), 'https://voter.votewa.gov/genericvoterguide.aspx?e=899&c=18')
  assert.equal(
    pamphletLink([{ edition: 'local-voters-pamphlet', page: 26 }], 'thurston', id),
    'https://www.thurstoncountywa.gov/media/34849#page=26'
  )
  assert.equal(
    pamphletLink([{ edition: 'voters-pamphlet-edition-27-thurston', page: 31 }], 'thurston', id),
    'https://www.sos.wa.gov/sites/default/files/2026-10/Voters%20Pamphlet%202026%20-%20Edition%2027%20-%20Thurston.pdf#page=31'
  )
  // Thurston has no county guide; the primary keeps its own PDFs.
  assert.equal(pamphletLink([], 'thurston', id), null)
  assert.equal(
    pamphletLink([{ edition: 'local-voters-pamphlet', page: 4 }], 'thurston', primary.election.id),
    'https://www.thurstoncountywa.gov/media/33642#page=4'
  )
})

test('shipped Clark, Kitsap and Thurston records link their own PDFs or guide; their offices link directly', () => {
  const id = general.election.id
  const PDF = {
    clark: /2026clarkcountygeneralvp_web\.pdf#page=\d+$/,
    thurston: /(thurstoncountywa\.gov\/media\/34849|Edition%2027%20-%20Thurston\.pdf)#page=\d+$/,
  }
  const paged = { clark: 0, kitsap: 0, thurston: 0 }
  for (const item of [...general.contests, ...general.measures]) {
    if (!(item.owner in paged)) continue
    const pages = item.candidates ? item.candidates.map((c) => c.pamphlet_pages) : [item.pamphlet_pages]
    for (const p of pages) {
      if (!p?.length) continue
      assert.match(pamphletLink(p, item.owner, id), PDF[item.owner], item.slug)
      paged[item.owner]++
    }
  }
  // Kitsap cites VoteWA only; every Clark and Thurston measure has pages.
  assert.equal(paged.kitsap, 0)
  assert.ok(paged.clark >= 40 && paged.thurston >= 30, JSON.stringify(paged))
  for (const [county, name, url] of [
    ['clark', 'Clark County', 'https://clark.wa.gov/elections'],
    ['kitsap', 'Kitsap County', 'https://www.kitsap.gov/auditor/Pages/Elections.aspx'],
    ['thurston', 'Thurston County', 'https://www.thurstoncountywa.gov/departments/auditor/elections'],
  ]) {
    assert.deepEqual(countyElectionsOffice(general, { id: county, name }), { name: `${name} Elections`, url, direct: true })
  }
})

test('shipped Yakima, Whatcom and Benton records link their VoteWA guide; their offices link directly', () => {
  const id = general.election.id
  const GUIDE = {
    yakima: 'https://voter.votewa.gov/genericvoterguide.aspx?e=899&c=39',
    whatcom: 'https://voter.votewa.gov/genericvoterguide.aspx?e=899&c=37',
    benton: 'https://voter.votewa.gov/genericvoterguide.aspx?e=899&c=03',
  }
  const linked = { yakima: 0, whatcom: 0, benton: 0 }
  for (const item of [...general.contests, ...general.measures]) {
    if (!(item.owner in linked)) continue
    const pages = item.candidates ? item.candidates.map((c) => c.pamphlet_pages) : [item.pamphlet_pages]
    for (const p of pages) {
      assert.deepEqual(p, [], item.slug)
      assert.equal(pamphletLink(p, item.owner, id), GUIDE[item.owner], item.slug)
      linked[item.owner]++
    }
  }
  assert.ok(linked.yakima >= 30 && linked.whatcom >= 25 && linked.benton >= 40, JSON.stringify(linked))
  for (const [county, name, url] of [
    ['yakima', 'Yakima County', 'https://www.yakimacounty.us/170/Elections'],
    ['whatcom', 'Whatcom County', 'https://www.whatcomcounty.us/2794/Elections'],
    ['benton', 'Benton County', 'https://www.bentoncountywa.gov/government/elected_officials/auditor/elections/index.php'],
  ]) {
    assert.deepEqual(countyElectionsOffice(general, { id: county, name }), { name: `${name} Elections`, url, direct: true })
  }
})

test('shipped Skagit and Cowlitz records link their local pamphlet at the cited page, Grant its VoteWA guide', () => {
  const id = general.election.id
  const PDF = {
    skagit: 'https://www.skagitcountywa.gov/media/nopbncyw/2026-11-03-vp-skagit.pdf',
    cowlitz: 'https://www.co.cowlitz.wa.us/DocumentCenter/View/39451/G126-Combined-Voters-Pamplet_SOS',
  }
  const GUIDE = {
    skagit: 'https://voter.votewa.gov/genericvoterguide.aspx?e=899&c=29',
    cowlitz: 'https://voter.votewa.gov/genericvoterguide.aspx?e=899&c=08',
    grant: 'https://voter.votewa.gov/genericvoterguide.aspx?e=899&c=13',
  }
  // Skagit PDF p. 18 is printed p. 56 (Mount Vernon Prop 1); Cowlitz p. 57 is Longview Prop 1.
  assert.equal(pamphletLink([{ edition: 'local-voters-pamphlet', page: 18 }], 'skagit', id), `${PDF.skagit}#page=18`)
  assert.equal(pamphletLink([{ edition: 'local-voters-pamphlet', page: 57 }], 'cowlitz', id), `${PDF.cowlitz}#page=57`)
  const paged = { skagit: 0, cowlitz: 0 }
  const guided = { skagit: 0, cowlitz: 0, grant: 0 }
  for (const item of [...general.contests, ...general.measures]) {
    if (!(item.owner in guided)) continue
    const pages = item.candidates ? item.candidates.map((c) => c.pamphlet_pages) : [item.pamphlet_pages]
    for (const p of pages) {
      if (p?.length) {
        assert.ok(item.owner in PDF, item.slug)
        assert.equal(pamphletLink(p, item.owner, id), `${PDF[item.owner]}#page=${p[0].page}`, item.slug)
        paged[item.owner]++
      } else {
        // Grant's records, and races shipped with another package's research.
        assert.equal(pamphletLink(p, item.owner, id), GUIDE[item.owner], item.slug)
        guided[item.owner]++
      }
    }
  }
  assert.ok(paged.skagit >= 20 && paged.cowlitz >= 10 && guided.grant >= 30, JSON.stringify({ paged, guided }))
  for (const [county, name, url] of [
    ['skagit', 'Skagit County', 'https://www.skagitcountywa.gov/government/auditor-s-office/elections-and-voting/'],
    ['cowlitz', 'Cowlitz County', 'https://www.co.cowlitz.wa.us/2357/Elections'],
    ['grant', 'Grant County', 'https://www.grantcountywa.gov/270/Elections'],
  ]) {
    assert.deepEqual(countyElectionsOffice(general, { id: county, name }), { name: `${name} Elections`, url, direct: true })
  }
})

test('shipped Island and Lewis records link their VoteWA guide; their offices link directly', () => {
  const id = general.election.id
  const GUIDE = {
    island: 'https://voter.votewa.gov/genericvoterguide.aspx?e=899&c=15',
    lewis: 'https://voter.votewa.gov/genericvoterguide.aspx?e=899&c=21',
  }
  const guided = { island: 0, lewis: 0 }
  for (const item of [...general.contests, ...general.measures]) {
    if (!(item.owner in guided)) continue
    const pages = item.candidates ? item.candidates.map((c) => c.pamphlet_pages) : [item.pamphlet_pages]
    for (const p of pages) {
      // Neither county prints a general pamphlet (#29).
      assert.deepEqual(p, [], item.slug)
      assert.equal(pamphletLink(p, item.owner, id), GUIDE[item.owner], item.slug)
      guided[item.owner]++
    }
  }
  assert.deepEqual(guided, { island: 26, lewis: 29 })
  for (const [county, name, url] of [
    ['island', 'Island County', 'https://www.islandcountywa.gov/423/Elections-Voter-Registration'],
    ['lewis', 'Lewis County', 'https://elections.lewiscountywa.gov/'],
  ]) {
    assert.deepEqual(countyElectionsOffice(general, { id: county, name }), { name: `${name} Elections`, url, direct: true })
  }
})

test('shipped Franklin, Chelan and Clallam records link their local pamphlet at the cited page, Grays Harbor its VoteWA guide', () => {
  const id = general.election.id
  const PDF = {
    franklin: 'https://www.franklincountywa.gov/DocumentCenter/View/4553/2611-Franklin-County-Voters-Pamphlet-',
    chelan: 'https://www.co.chelan.wa.us/files/elections/documents/election/2026%20November%203%20General%20Election%20LVP.pdf',
    clallam: 'https://www.clallamcountywa.gov/DocumentCenter/View/29375/2026-General-Voter-Pamphlet',
  }
  const GUIDE = {
    franklin: 'https://voter.votewa.gov/genericvoterguide.aspx?e=899&c=11',
    chelan: 'https://voter.votewa.gov/genericvoterguide.aspx?e=899&c=04',
    clallam: 'https://voter.votewa.gov/genericvoterguide.aspx?e=899&c=05',
    'grays-harbor': 'https://voter.votewa.gov/genericvoterguide.aspx?e=899&c=14',
  }
  // Franklin FPD 3 is PDF p. 16 (printed p. 58); Clallam District Court 1 p. 55.
  assert.equal(pamphletLink([{ edition: 'local-voters-pamphlet', page: 16 }], 'franklin', id), `${PDF.franklin}#page=16`)
  assert.equal(pamphletLink([{ edition: 'local-voters-pamphlet', page: 55 }], 'clallam', id), `${PDF.clallam}#page=55`)
  const paged = { franklin: 0, chelan: 0, clallam: 0 }
  const guided = { franklin: 0, chelan: 0, clallam: 0, 'grays-harbor': 0 }
  for (const item of [...general.contests, ...general.measures]) {
    if (!(item.owner in guided)) continue
    const pages = item.candidates ? item.candidates.map((c) => c.pamphlet_pages) : [item.pamphlet_pages]
    for (const p of pages) {
      if (p?.length) {
        assert.ok(item.owner in PDF, item.slug)
        assert.equal(pamphletLink(p, item.owner, id), `${PDF[item.owner]}#page=${p[0].page}`, item.slug)
        paged[item.owner]++
      } else {
        // Grays Harbor's records, and races shipped with another package's research.
        assert.equal(pamphletLink(p, item.owner, id), GUIDE[item.owner], item.slug)
        guided[item.owner]++
      }
    }
  }
  assert.ok(paged.franklin >= 15 && paged.chelan >= 20 && paged.clallam >= 25 && guided['grays-harbor'] >= 29,
    JSON.stringify({ paged, guided }))
  for (const [county, name, url] of [
    ['franklin', 'Franklin County', 'https://www.franklincountywa.gov/Elections'],
    ['chelan', 'Chelan County', 'https://www.co.chelan.wa.us/elections'],
    ['clallam', 'Clallam County', 'https://www.clallamcountywa.gov/162/Elections-Voter-Registration'],
    ['grays-harbor', 'Grays Harbor County', 'https://www.graysharbor.us/government/Auditors/elections.php'],
  ]) {
    assert.deepEqual(countyElectionsOffice(general, { id: county, name }), { name: `${name} Elections`, url, direct: true })
  }
})

test('shipped Mason records link the local pamphlet at the cited page, else the county\'s VoteWA guide', () => {
  const id = general.election.id
  const PDF = 'https://www.masoncountywa.gov/Documents/Departments/Auditor/Elections/Current%20Election/General_2026_Local_Voters_Pamphlet.pdf'
  const GUIDE = 'https://voter.votewa.gov/genericvoterguide.aspx?e=899&c=23'
  // City of Shelton Prop. 1 is PDF p. 30.
  assert.equal(pamphletLink([{ edition: 'local-voters-pamphlet', page: 30 }], 'mason', id), `${PDF}#page=30`)
  let paged = 0
  let guided = 0
  for (const item of [...general.contests, ...general.measures]) {
    if (item.owner !== 'mason') continue
    const pages = item.candidates ? item.candidates.map((c) => c.pamphlet_pages) : [item.pamphlet_pages]
    for (const p of pages) {
      if (p?.length) {
        assert.equal(pamphletLink(p, 'mason', id), `${PDF}#page=${p[0].page}`, item.slug)
        paged++
      } else {
        // CD 6, LD 35 and the Court of Appeals seat ship with another package's research.
        assert.equal(pamphletLink(p, 'mason', id), GUIDE, item.slug)
        guided++
      }
    }
  }
  assert.ok(paged >= 20 && guided >= 9, JSON.stringify({ paged, guided }))
  assert.deepEqual(countyElectionsOffice(general, { id: 'mason', name: 'Mason County' }), {
    name: 'Mason County Elections',
    url: 'https://www.masoncountywa.gov/departments/auditor/elections/index.php',
    direct: true,
  })
})

test('shipped Walla Walla records link the local pamphlet at the cited page, else the county\'s VoteWA guide', () => {
  const id = general.election.id
  const PDF = 'https://www.wwcowa.gov/November%20General%202026-%20Final.pdf'
  const GUIDE = 'https://voter.votewa.gov/genericvoterguide.aspx?e=899&c=36'
  // Prescott park levy, pamphlet pp. 24-25.
  assert.equal(pamphletLink([{ edition: 'local-voters-pamphlet', page: 24 }], 'walla-walla', id), `${PDF}#page=24`)
  let paged = 0
  let guided = 0
  for (const item of [...general.contests, ...general.measures]) {
    if (item.owner !== 'walla-walla') continue
    const pages = item.candidates ? item.candidates.map((c) => c.pamphlet_pages) : [item.pamphlet_pages]
    for (const p of pages) {
      if (p?.length) {
        assert.equal(pamphletLink(p, 'walla-walla', id), `${PDF}#page=${p[0].page}`, item.slug)
        paged++
      } else {
        // CD 5, LD 16 and the Court of Appeals seat cite VoteWA or another package.
        assert.equal(pamphletLink(p, 'walla-walla', id), GUIDE, item.slug)
        guided++
      }
    }
  }
  assert.ok(paged >= 16 && guided >= 7, JSON.stringify({ paged, guided }))
  assert.deepEqual(countyElectionsOffice(general, { id: 'walla-walla', name: 'Walla Walla County' }), {
    name: 'Walla Walla County Elections',
    url: 'https://www.wwcowa.gov/government/auditor/current_election.php',
    direct: true,
  })
})

test('shipped Stevens records link the county\'s VoteWA guide', () => {
  const id = general.election.id
  const GUIDE = 'https://voter.votewa.gov/genericvoterguide.aspx?e=899&c=33'
  let n = 0
  for (const item of [...general.contests, ...general.measures]) {
    if (item.owner !== 'stevens') continue
    const pages = item.candidates ? item.candidates.map((c) => c.pamphlet_pages) : [item.pamphlet_pages]
    for (const p of pages) {
      assert.equal(pamphletLink(p, 'stevens', id), GUIDE, item.slug)
      n++
    }
  }
  assert.ok(n >= 27, String(n))
  assert.deepEqual(countyElectionsOffice(general, { id: 'stevens', name: 'Stevens County' }), {
    name: 'Stevens County Elections',
    url: 'https://www.stevenscountywa.gov/20911/Elections',
    direct: true,
  })
})

test('shipped Whitman records link the local pamphlet at the cited page, else the county\'s VoteWA guide', () => {
  const id = general.election.id
  const PDF = 'https://www.whitmancounty.gov/DocumentCenter/View/12618'
  const GUIDE = 'https://voter.votewa.gov/genericvoterguide.aspx?e=899&c=38'
  // Sheriff Myers, pamphlet p. 11 (PDF page = printed page).
  assert.equal(pamphletLink([{ edition: 'local-voters-pamphlet', page: 11 }], 'whitman', id), `${PDF}#page=11`)
  let paged = 0
  let guided = 0
  for (const item of [...general.contests, ...general.measures]) {
    if (item.owner !== 'whitman') continue
    const pages = item.candidates ? item.candidates.map((c) => c.pamphlet_pages) : [item.pamphlet_pages]
    for (const p of pages) {
      if (p?.length) {
        assert.equal(pamphletLink(p, 'whitman', id), `${PDF}#page=${p[0].page}`, item.slug)
        paged++
      } else {
        // CD 5, LD 9, the Court of Appeals seat and the eight hardship-waiver
        // measures cite VoteWA or another package.
        assert.equal(pamphletLink(p, 'whitman', id), GUIDE, item.slug)
        guided++
      }
    }
  }
  assert.ok(paged >= 32 && guided >= 14, JSON.stringify({ paged, guided }))
  assert.deepEqual(countyElectionsOffice(general, { id: 'whitman', name: 'Whitman County' }), {
    name: 'Whitman County Elections',
    url: 'https://www.whitmancounty.gov/172/Current-Election',
    direct: true,
  })
})

test('shipped Douglas records link the county\'s VoteWA guide', () => {
  const id = general.election.id
  const GUIDE = 'https://voter.votewa.gov/genericvoterguide.aspx?e=899&c=09'
  let n = 0
  for (const item of [...general.contests, ...general.measures]) {
    if (item.owner !== 'douglas') continue
    const pages = item.candidates ? item.candidates.map((c) => c.pamphlet_pages) : [item.pamphlet_pages]
    for (const p of pages) {
      assert.equal(pamphletLink(p, 'douglas', id), GUIDE, item.slug)
      n++
    }
  }
  assert.ok(n >= 37, String(n))
  assert.deepEqual(countyElectionsOffice(general, { id: 'douglas', name: 'Douglas County' }), {
    name: 'Douglas County Elections',
    url: 'https://www.douglascountywa.gov/206/Current-Election',
    direct: true,
  })
})

test('shipped Okanogan records link the county\'s VoteWA guide', () => {
  const id = general.election.id
  const GUIDE = 'https://voter.votewa.gov/genericvoterguide.aspx?e=899&c=24'
  let n = 0
  for (const item of [...general.contests, ...general.measures]) {
    if (item.owner !== 'okanogan') continue
    const pages = item.candidates ? item.candidates.map((c) => c.pamphlet_pages) : [item.pamphlet_pages]
    for (const p of pages) {
      assert.equal(pamphletLink(p, 'okanogan', id), GUIDE, item.slug)
      n++
    }
  }
  assert.ok(n >= 33, String(n))
  assert.deepEqual(countyElectionsOffice(general, { id: 'okanogan', name: 'Okanogan County' }), {
    name: 'Okanogan County Elections',
    url: 'https://www.okanogancounty.gov/337/Elections',
    direct: true,
  })
})

test('shipped Jefferson and Kittitas records link their local pamphlet at the cited page, else the county\'s VoteWA guide', () => {
  const id = general.election.id
  for (const [county, name, pdf, guide, office, counts] of [
    ['jefferson', 'Jefferson County', 'https://www.co.jefferson.wa.us/DocumentCenter/View/25551',
      'https://voter.votewa.gov/genericvoterguide.aspx?e=899&c=16', 'https://www.co.jefferson.wa.us/1266/Elections', [13, 7]],
    ['kittitas', 'Kittitas County',
      'https://www.co.kittitas.wa.us/uploads/auditor/elections/voters-pamphlet//General%20Pamphlet.pdf',
      'https://voter.votewa.gov/genericvoterguide.aspx?e=899&c=19',
      'https://www.co.kittitas.wa.us/auditor/elections/default.aspx', [14, 8]],
  ]) {
    let paged = 0
    let guided = 0
    for (const item of [...general.contests, ...general.measures]) {
      if (item.owner !== county) continue
      const pages = item.candidates ? item.candidates.map((c) => c.pamphlet_pages) : [item.pamphlet_pages]
      for (const p of pages) {
        if (p?.length) {
          // PDF page = printed page in both pamphlets.
          assert.equal(pamphletLink(p, county, id), `${pdf}#page=${p[0].page}`, item.slug)
          paged++
        } else {
          // CD, LD and Court of Appeals seats: another package's research or VoteWA.
          assert.equal(pamphletLink(p, county, id), guide, item.slug)
          guided++
        }
      }
    }
    assert.deepEqual([paged, guided], counts, county)
    assert.deepEqual(countyElectionsOffice(general, { id: county, name }), {
      name: `${name} Elections`,
      url: office,
      direct: true,
    })
  }
  // Jefferson's Quillayute Valley SD 402 bonds, pamphlet p. 14; Kittitas's
  // District Court judges, p. 10.
  assert.equal(pamphletLink([{ edition: 'local-voters-pamphlet', page: 14 }], 'jefferson', id),
    'https://www.co.jefferson.wa.us/DocumentCenter/View/25551#page=14')
  assert.equal(pamphletLink([{ edition: 'local-voters-pamphlet', page: 10 }], 'kittitas', id),
    'https://www.co.kittitas.wa.us/uploads/auditor/elections/voters-pamphlet//General%20Pamphlet.pdf#page=10')
})

test('shipped Klickitat and Asotin records link their pamphlet at the cited PDF page, else the county\'s VoteWA guide', () => {
  const id = general.election.id
  for (const [county, name, pdf, guide, office, counts] of [
    ['klickitat', 'Klickitat County', 'https://www.klickitatcounty.gov/DocumentCenter/View/23954',
      'https://voter.votewa.gov/genericvoterguide.aspx?e=899&c=20',
      'https://www.klickitatcounty.gov/1136/ElectionsVoter-Registration', [15, 10]],
    ['asotin', 'Asotin County',
      'https://www.asotincountywa.gov/DocumentCenter/View/18054/2026GeneralElectionLocalVotersPamphlet-_Asotin-82726',
      'https://voter.votewa.gov/genericvoterguide.aspx?e=899&c=02',
      'https://www.asotincountywa.gov/186/Current-Election', [12, 6]],
  ]) {
    let paged = 0
    let guided = 0
    for (const item of [...general.contests, ...general.measures]) {
      if (item.owner !== county) continue
      const pages = item.candidates ? item.candidates.map((c) => c.pamphlet_pages) : [item.pamphlet_pages]
      for (const p of pages) {
        if (p?.length) {
          // Citations are PDF pages (Klickitat's equal the printed ones;
          // Asotin's run 36 behind).
          assert.equal(pamphletLink(p, county, id), `${pdf}#page=${p[0].page}`, item.slug)
          paged++
        } else {
          // CD and LD seats ship another package's research; Asotin's Court
          // of Appeals seat cites VoteWA.
          assert.equal(pamphletLink(p, county, id), guide, item.slug)
          guided++
        }
      }
    }
    assert.deepEqual([paged, guided], counts, county)
    assert.deepEqual(countyElectionsOffice(general, { id: county, name }), {
      name: `${name} Elections`,
      url: office,
      direct: true,
    })
  }
  // Klickitat's EMS levy, p. 56; Asotin's Rural EMS levy, PDF p. 12 (printed p. 48).
  assert.equal(pamphletLink([{ edition: 'local-voters-pamphlet', page: 56 }], 'klickitat', id),
    'https://www.klickitatcounty.gov/DocumentCenter/View/23954#page=56')
  assert.equal(pamphletLink([{ edition: 'local-voters-pamphlet', page: 12 }], 'asotin', id),
    'https://www.asotincountywa.gov/DocumentCenter/View/18054/2026GeneralElectionLocalVotersPamphlet-_Asotin-82726#page=12')
})

test('shipped Skamania and San Juan records link their pamphlet at the cited PDF page, else the county\'s VoteWA guide', () => {
  const id = general.election.id
  for (const [county, name, pdf, guide, office, counts] of [
    ['skamania', 'Skamania County',
      'https://www.skamaniacounty.gov/home/showpublisheddocument/19600/639253463106470000',
      'https://voter.votewa.gov/genericvoterguide.aspx?e=899&c=30',
      'https://www.skamaniacounty.gov/departments-offices/auditor/elections/current-election', [13, 6]],
    ['san-juan', 'San Juan County', 'https://www.sanjuancountywa.gov/DocumentCenter/View/36027',
      'https://voter.votewa.gov/genericvoterguide.aspx?e=899&c=28',
      'https://www.sanjuancountywa.gov/1292/Current-Election', [14, 6]],
  ]) {
    let paged = 0
    let guided = 0
    for (const item of [...general.contests, ...general.measures]) {
      if (item.owner !== county) continue
      const pages = item.candidates ? item.candidates.map((c) => c.pamphlet_pages) : [item.pamphlet_pages]
      for (const p of pages) {
        if (p?.length) {
          // Citations are PDF pages (Skamania's run 34 behind the printed
          // ones; San Juan's equal them).
          assert.equal(pamphletLink(p, county, id), `${pdf}#page=${p[0].page}`, item.slug)
          paged++
        } else {
          // CD and LD seats ship another package's research.
          assert.equal(pamphletLink(p, county, id), guide, item.slug)
          guided++
        }
      }
    }
    assert.deepEqual([paged, guided], counts, county)
    assert.deepEqual(countyElectionsOffice(general, { id: county, name }), {
      name: `${name} Elections`,
      url: office,
      direct: true,
    })
  }
  // Skamania's Assessor, PDF p. 6 (printed p. 40); San Juan's Lopez Solid
  // Waste levy, p. 56.
  assert.equal(pamphletLink([{ edition: 'local-voters-pamphlet', page: 6 }], 'skamania', id),
    'https://www.skamaniacounty.gov/home/showpublisheddocument/19600/639253463106470000#page=6')
  assert.equal(pamphletLink([{ edition: 'local-voters-pamphlet', page: 56 }], 'san-juan', id),
    'https://www.sanjuancountywa.gov/DocumentCenter/View/36027#page=56')
})

test('shipped Lincoln and Pend Oreille records link their pamphlet at the cited PDF page, else the county\'s VoteWA guide', () => {
  const id = general.election.id
  for (const [county, name, pdf, guide, office, counts] of [
    ['lincoln', 'Lincoln County', 'https://www.lincolncountywa.com/DocumentCenter/View/2055',
      'https://voter.votewa.gov/genericvoterguide.aspx?e=899&c=22',
      'https://www.lincolncountywa.com/312/Current-Future-Elections', [8, 6]],
    ['pend-oreille', 'Pend Oreille County',
      'https://www.pendoreille.gov/sites/g/files/vyhlif14901/files/media/auditor/file/34071/final_vp_general_2026_pend_oreille.pdf',
      'https://voter.votewa.gov/genericvoterguide.aspx?e=899&c=26',
      'https://www.pendoreille.gov/auditor/page/elections', [14, 8]],
  ]) {
    let paged = 0
    let guided = 0
    for (const item of [...general.contests, ...general.measures]) {
      if (item.owner !== county) continue
      const pages = item.candidates ? item.candidates.map((c) => c.pamphlet_pages) : [item.pamphlet_pages]
      for (const p of pages) {
        if (p?.length) {
          // Citations are PDF pages (Lincoln's equal the printed ones; Pend
          // Oreille's run 38 behind).
          assert.equal(pamphletLink(p, county, id), `${pdf}#page=${p[0].page}`, item.slug)
          paged++
        } else {
          // CD, LD, Court of Appeals and Superior Court seats.
          assert.equal(pamphletLink(p, county, id), guide, item.slug)
          guided++
        }
      }
    }
    assert.deepEqual([paged, guided], counts, county)
    assert.deepEqual(countyElectionsOffice(general, { id: county, name }), {
      name: `${name} Elections`,
      url: office,
      direct: true,
    })
  }
  // Lincoln's Assessor, p. 4; Pend Oreille's Sacheen Lake levy, PDF p. 18
  // (printed p. 56).
  assert.equal(pamphletLink([{ edition: 'local-voters-pamphlet', page: 4 }], 'lincoln', id),
    'https://www.lincolncountywa.com/DocumentCenter/View/2055#page=4')
  assert.equal(pamphletLink([{ edition: 'local-voters-pamphlet', page: 18 }], 'pend-oreille', id),
    'https://www.pendoreille.gov/sites/g/files/vyhlif14901/files/media/auditor/file/34071/final_vp_general_2026_pend_oreille.pdf#page=18')
})

test('shipped Ferry and Wahkiakum records link the county\'s VoteWA guide; their offices are the Auditors\' pages', () => {
  const id = general.election.id
  // Neither county prints a general pamphlet (#32): every record, its own and
  // those shipped with Spokane's, Okanogan's, Clark's and Thurston's research,
  // is unpaged. Wahkiakum's guide carries no county race; its sample ballot
  // is the official listing.
  for (const [county, name, guide, office, count] of [
    ['ferry', 'Ferry County', 'https://voter.votewa.gov/genericvoterguide.aspx?e=899&c=10',
      'https://www.ferry-county.com/departments/auditor/index.php', 21],
    ['wahkiakum', 'Wahkiakum County', 'https://voter.votewa.gov/genericvoterguide.aspx?e=899&c=35',
      'https://www.co.wahkiakum.wa.us/419/Elections', 18],
  ]) {
    let n = 0
    for (const item of [...general.contests, ...general.measures]) {
      if (item.owner !== county) continue
      const pages = item.candidates ? item.candidates.map((c) => c.pamphlet_pages) : [item.pamphlet_pages]
      for (const p of pages) {
        assert.equal(pamphletLink(p, county, id), guide, item.slug)
        n++
      }
    }
    assert.equal(n, count, county)
    assert.deepEqual(countyElectionsOffice(general, { id: county, name }), {
      name: `${name} Elections`,
      url: office,
      direct: true,
    })
  }
})

test('shipped Pacific records link the county\'s VoteWA guide; its office falls back to the statewide list', () => {
  const id = general.election.id
  const GUIDE = 'https://voter.votewa.gov/genericvoterguide.aspx?e=899&c=25'
  let n = 0
  for (const item of [...general.contests, ...general.measures]) {
    if (item.owner !== 'pacific') continue
    const pages = item.candidates ? item.candidates.map((c) => c.pamphlet_pages) : [item.pamphlet_pages]
    for (const p of pages) {
      assert.equal(pamphletLink(p, 'pacific', id), GUIDE, item.slug)
      n++
    }
  }
  assert.equal(n, 25)
  // co.pacific.wa.us did not answer on 2026-10-08 (#31), so the shipped
  // coverage carries no elections_url for Pacific.
  assert.deepEqual(countyElectionsOffice(general, { id: 'pacific', name: 'Pacific County' }), {
    name: 'Pacific County Elections',
    url: COUNTY_OFFICES_URL,
    direct: false,
  })
})

test('shipped Adams records link the county\'s VoteWA guide; its office is the Auditor\'s Elections page', () => {
  const id = general.election.id
  const GUIDE = 'https://voter.votewa.gov/genericvoterguide.aspx?e=899&c=01'
  // Adams prints no local pamphlet (#31): every record, its own and the CD, LD
  // seats shipped with Benton's, Spokane's and Grant's research, is unpaged.
  let n = 0
  for (const item of [...general.contests, ...general.measures]) {
    if (item.owner !== 'adams') continue
    const pages = item.candidates ? item.candidates.map((c) => c.pamphlet_pages) : [item.pamphlet_pages]
    for (const p of pages) {
      assert.equal(pamphletLink(p, 'adams', id), GUIDE, item.slug)
      n++
    }
  }
  assert.equal(n, 28)
  assert.deepEqual(countyElectionsOffice(general, { id: 'adams', name: 'Adams County' }), {
    name: 'Adams County Elections',
    url: 'https://www.co.adams.wa.gov/162/Elections-Elecciones',
    direct: true,
  })
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
  // Garfield does not ship in the general (Walla Walla does since #30).
  assert.deepEqual(countyElectionsOffice(general, { id: 'garfield', name: 'Garfield County' }), {
    name: 'Garfield County Elections',
    url: COUNTY_OFFICES_URL,
    direct: false,
  })
})

test('no county, no county office', () => {
  assert.equal(countyElectionsOffice(general, null), null)
  assert.equal(countyElectionsOffice(general, {}), null)
})
