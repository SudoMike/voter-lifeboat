// The November 3, 2026 general as shipped: King County at Full County
// Coverage (issue #16), Spokane at partial coverage, Pierce at full coverage
// (#21), Snohomish at full coverage (#27), Clark, Kitsap and Thurston at full
// coverage (#22), every other Washington address a Statewide-Only
// Guide (issue #9). These run the app's own ballot, interview, lean and Ballot Brief
// code against public/data/2026-11-03-general.
import test from 'node:test'
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { scopeMatches, coverageAdvice } from './geo.js'
import {
  contestsOnBallot,
  measuresOnBallot,
  axesForBallot,
  interviewItemsForBallot,
  buildProfile,
  measureLean,
  rankContest,
} from './scoring.js'
import { buildBrief } from './brief.js'
import { contestHeading } from './contests.js'

const data = JSON.parse(
  readFileSync(new URL('../../public/data/2026-11-03-general/app-data.json', import.meta.url), 'utf8')
)

const KING = { id: 'king', fips: '53033', name: 'King County' }

// What lookupBallotContext returns for a Washington address in a county the
// general does not ship (geo.test.js covers the lookup itself).
const yakima = {
  coverageStatus: 'statewide_only',
  county: { id: 'yakima', fips: '53077', name: 'Yakima County' },
  districts: {},
  missingLayers: [],
}

// King districts as the live District Adapter resolved them on 2026-10-08
// (Census geocoder + King GIS + the DOR cemetery layer).
const king = (districts) => ({ coverageStatus: 'full_county', county: KING, districts, missingLayers: [] })
const ADDRESSES = {
  // 600 4th Ave, Seattle 98104 (City Hall)
  cityHall: king({ CONGDST: '7', LEGDST: '34', KCCDST: '8', SCCDST: 'SCC7', JUDDST: 'W', SCHDST: '1', CITY: 'Seattle' }),
  // 11700 Pinehurst Way NE, Seattle 98125
  pinehurst: king({ CONGDST: '7', LEGDST: '46', KCCDST: '1', SCCDST: 'SCC5', JUDDST: 'W', SCHDST: '1', CITY: 'Seattle' }),
  // 17500 Midvale Ave N, Shoreline 98133
  shoreline: king({ CONGDST: '7', LEGDST: '32', KCCDST: '1', JUDDST: 'SH', FIRDST: '4', SCHDST: '412', CITY: 'Shoreline' }),
  // 10105 SW Bank Rd, Vashon 98070
  vashon: king({ CONGDST: '7', LEGDST: '34', KCCDST: '8', JUDDST: 'SW', FIRDST: '13', SCHDST: '402', CEMDST: '1' }),
  // 220 4th Ave S, Kent 98032
  kent: king({ CONGDST: '9', LEGDST: '33', KCCDST: '5', JUDDST: 'SE', SCHDST: '415', CITY: 'Kent' }),
  // 25 W Main St, Auburn 98001
  auburn: king({ CONGDST: '9', LEGDST: '47', KCCDST: '7', JUDDST: 'SE', SCHDST: '408', CITY: 'Auburn' }),
}

const ballotFor = (context) => {
  const contests = contestsOnBallot(data, context, scopeMatches)
  const measures = measuresOnBallot(data, context, scopeMatches)
  const axes = axesForBallot(data, contests, measures)
  return { contests, measures, axes, items: interviewItemsForBallot(data, axes) }
}

const SUPREME_COURT = [1, 3, 4, 5, 7].map((n) => `justice-position-no-${n}-supreme-court`)
const STATE_MEASURES = [
  'initiative-measure-no-ip26-645',
  'initiative-measure-no-il26-001',
  'initiative-measure-no-il26-638',
]

test('the general ships King, Snohomish, Pierce, Clark, Kitsap and Thurston at full county coverage, Spokane at partial, with their elections offices', () => {
  assert.equal(data.election.id, '2026-11-03-general')
  assert.deepEqual(data.coverage, {
    statewide_complete: true,
    supported_counties: [
      {
        id: 'king',
        name: 'King County',
        state: 'WA',
        fips: '53033',
        coverage: 'full_county',
        elections_url: 'https://kingcounty.gov/en/dept/elections',
      },
      {
        // Full since #27: the District Court seats (DISTCRT) resolve from the
        // Auditor's Court_Districts layer.
        id: 'snohomish',
        name: 'Snohomish County',
        state: 'WA',
        fips: '53061',
        coverage: 'full_county',
        elections_url: 'https://www.snohomishcountywa.gov/224/Elections-Voter-Registration',
      },
      {
        // Partial: the Stevens County PUD seat Spokane voters inside that PUD
        // elect is scoped to PUDDST, which no electoral layer resolves (#21).
        id: 'spokane',
        name: 'Spokane County',
        state: 'WA',
        fips: '53063',
        coverage: 'partial_county',
        elections_url: 'https://www.spokanecounty.gov/elections',
      },
      {
        // Full: every Pierce scope resolves, KCDISTCRT, PTBA and SCHDST from
        // the Election_Precincts layer (#21).
        id: 'pierce',
        name: 'Pierce County',
        state: 'WA',
        fips: '53053',
        coverage: 'full_county',
        elections_url: 'https://www.piercecountywa.gov/elections',
      },
      {
        // Full: Battle Ground SD's levy (SCHDST) resolves from Clark's own
        // school district layer (#22).
        id: 'clark',
        name: 'Clark County',
        state: 'WA',
        fips: '53011',
        coverage: 'full_county',
        elections_url: 'https://clark.wa.gov/elections',
      },
      {
        // Full: South Kitsap SD's levy (SCHDST) resolves from Kitsap's school
        // district outlines; commissioner and PUD seats are countywide (#22).
        id: 'kitsap',
        name: 'Kitsap County',
        state: 'WA',
        fips: '53035',
        coverage: 'full_county',
        elections_url: 'https://www.kitsap.gov/auditor/Pages/Elections.aspx',
      },
      {
        // Full: Yelm's levy (SCHDST) and West Thurston RFA's (RFADST) resolve
        // from Thurston's Jurisdictions and fire layers (#22).
        id: 'thurston',
        name: 'Thurston County',
        state: 'WA',
        fips: '53067',
        coverage: 'full_county',
        elections_url: 'https://www.thurstoncountywa.gov/departments/auditor/elections',
      },
    ],
  })
})

// A race listed by two counties ships once per county, with the researching
// package's scoring (shared_contests): same candidates, same scores.
const sameScoring = (ballot, slug, ownerSlug) => {
  const shipped = ballot.contests.find((c) => c.slug === slug)
  const owner = data.contests.find((c) => c.slug === ownerSlug)
  assert.ok(shipped, slug)
  assert.deepEqual(shipped.candidates.map((c) => [c.slug, c.scores]), owner.candidates.map((c) => [c.slug, c.scores]))
}
const ownLocal = (ballot, owner) => ballot.measures.filter((m) => m.owner === owner).map((m) => m.slug)

test('a Clark ballot: council district, Battle Ground SD levy only inside the district', () => {
  const CLARK = { id: 'clark', fips: '53011', name: 'Clark County' }
  const cla = (districts) => ({ coverageStatus: 'full_county', county: CLARK, districts, missingLayers: [] })
  // Districts as the live District Adapter resolved them on 2026-10-08.
  // 1300 Franklin St, Vancouver.
  const vancouver = ballotFor(cla({
    CONGDST: '3', LEGDST: '49', CITY: 'Vancouver', COUNTY_COUNCIL: '1', PUDDST: '3', FIRDST: '26', SCHDST: '37',
  }))
  const vs = vancouver.contests.map((c) => c.slug)
  assert.equal(new Set(vs).size, vs.length)
  for (const slug of SUPREME_COURT) assert.ok(vs.includes(slug), slug)
  assert.deepEqual(vancouver.measures.slice(0, 3).map((m) => m.slug), STATE_MEASURES)
  assert.ok(vs.includes('clark-clark-county-council-district-1-county-councilor'))
  assert.ok(vs.includes('clark-legislative-district-49-state-representative-pos-1'))
  // The PUD seat is elected countywide in the general.
  assert.ok(vs.includes('clark-public-utility-district-no-1-of-clark-county-district-3-pud-commissioner'))
  assert.ok(!vs.some((s) => s.includes('council-district-5')), vs.join())
  assert.equal(ownLocal(vancouver, 'clark').length, 11)
  assert.ok(!ownLocal(vancouver, 'clark').includes('clark-battle-ground-school-district-no-119-proposition-no-11'))
  // 109 SW 1st St, Battle Ground.
  const bg = ballotFor(cla({
    CONGDST: '3', LEGDST: '18', CITY: 'Battle Ground', COUNTY_COUNCIL: '5', PUDDST: '1', FIRDST: '3', SCHDST: '119',
  }))
  const bs = bg.contests.map((c) => c.slug)
  assert.ok(bs.includes('clark-clark-county-council-district-5-county-councilor'))
  assert.ok(bs.includes('clark-legislative-district-18-state-representative-pos-2'))
  assert.ok(ownLocal(bg, 'clark').includes('clark-battle-ground-school-district-no-119-proposition-no-11'))
  assert.equal(coverageAdvice(cla({})), null)
})

test('a Kitsap ballot: Pierce\'s research for LD 26 and CD 6, its own for LD 35, South Kitsap levy by district', () => {
  const KITSAP = { id: 'kitsap', fips: '53035', name: 'Kitsap County' }
  const kit = (districts) => ({ coverageStatus: 'full_county', county: KITSAP, districts, missingLayers: [] })
  // 345 6th St, Bremerton.
  const bremerton = ballotFor(kit({ CONGDST: '6', LEGDST: '26', CITY: 'Bremerton', COUNTY_COUNCIL: '2', SCHDST: '100-C' }))
  const bs = bremerton.contests.map((c) => c.slug)
  assert.equal(new Set(bs).size, bs.length)
  for (const slug of SUPREME_COURT) assert.ok(bs.includes(slug), slug)
  sameScoring(bremerton, 'kitsap-congressional-district-6-u-s-representative', 'pierce-congressional-district-6-u-s-representative')
  sameScoring(bremerton, 'kitsap-legislative-district-26-state-senator', 'pierce-legislative-district-26-state-senator')
  assert.ok(!bremerton.contests.some((c) => c.owner === 'pierce'))
  assert.deepEqual(ownLocal(bremerton, 'kitsap'), ['kitsap-kitsap-county-public-utility-district-no-1-proposition-no-1'])
  // 1700 SE Mile Hill Dr, Port Orchard: South Kitsap SD 402.
  const po = ballotFor(kit({ CONGDST: '6', LEGDST: '26', CITY: 'Port Orchard', COUNTY_COUNCIL: '2', FIRDST: '7', SCHDST: '402' }))
  assert.deepEqual(ownLocal(po, 'kitsap'), [
    'kitsap-south-kitsap-school-district-no-402-proposition-no-1',
    'kitsap-kitsap-county-public-utility-district-no-1-proposition-no-1',
  ])
  // 15376 Seabeck Hwy NW, Seabeck: LD 35, researched by Kitsap.
  const seabeck = ballotFor(kit({ CONGDST: '6', LEGDST: '35', COUNTY_COUNCIL: '3', FIRDST: '1', SCHDST: '401' }))
  const ss = seabeck.contests.map((c) => c.slug)
  assert.ok(ss.includes('kitsap-legislative-district-35-state-senator'))
  assert.ok(!ss.some((s) => s.includes('district-26')), ss.join())
  assert.equal(coverageAdvice(kit({})), null)
})

test('a Thurston ballot: Pierce, Clark and Kitsap research for shared seats, WTRFA and Yelm levies by district', () => {
  const THURSTON = { id: 'thurston', fips: '53067', name: 'Thurston County' }
  const thu = (districts) => ({ coverageStatus: 'full_county', county: THURSTON, districts, missingLayers: [] })
  // 601 4th Ave E, Olympia: CD 10 with Pierce's scoring, LD 22 Thurston's own.
  const olympia = ballotFor(thu({
    CONGDST: '10', LEGDST: '22', CITY: 'Olympia', COUNTY_COUNCIL: '1', PUDDST: '1', FIRDST: 'OFD', FIRE_AUTH: 'Olympia',
    SCHDST: 'OLYMPIA',
  }))
  const os = olympia.contests.map((c) => c.slug)
  assert.equal(new Set(os).size, os.length)
  for (const slug of SUPREME_COURT) assert.ok(os.includes(slug), slug)
  sameScoring(olympia, 'thurston-congressional-district-10-u-s-representative', 'pierce-congressional-district-10-u-s-representative')
  assert.ok(os.includes('thurston-legislative-district-22-state-representative-pos-2'))
  assert.deepEqual(ownLocal(olympia, 'thurston'), ['thurston-timberland-regional-library-district-proposition-no-1'])
  // 18346 Albany St SW, Rochester: CD 3 (Clark's), LD 35 (Kitsap's), WTRFA.
  const rochester = ballotFor(thu({
    CONGDST: '3', LEGDST: '35', COUNTY_COUNCIL: '4', PUDDST: '3', FIRDST: 'FD01', FIRE_AUTH: 'WTRFA - South Btn',
    RFADST: 'FD01', SCHDST: 'ROCHESTER',
  }))
  sameScoring(rochester, 'thurston-congressional-district-3-u-s-representative', 'clark-congressional-district-3-u-s-representative')
  sameScoring(rochester, 'thurston-legislative-district-35-state-senator', 'kitsap-legislative-district-35-state-senator')
  sameScoring(rochester, 'thurston-legislative-district-35-state-representative-pos-1', 'kitsap-legislative-district-35-state-representative-pos-1')
  assert.ok(!rochester.contests.some((c) => c.owner !== 'thurston' && c.owner !== 'statewide'))
  assert.deepEqual(ownLocal(rochester, 'thurston'), [
    'thurston-timberland-regional-library-district-proposition-no-1',
    'thurston-west-thurston-regional-fire-authority-rochester-littlerock-proposition-no-1',
  ])
  // 105 W Yelm Ave, Yelm: LD 2 (Pierce's), Yelm Community Schools.
  const yelm = ballotFor(thu({
    CONGDST: '10', LEGDST: '2', CITY: 'Yelm', COUNTY_COUNCIL: '2', PUDDST: '2', FIRDST: 'FD02',
    FIRE_AUTH: 'S.E. Thurston Fire Authority', SCHDST: 'YELM',
  }))
  sameScoring(yelm, 'thurston-legislative-district-2-state-representative-pos-1', 'pierce-legislative-district-2-state-representative-pos-1')
  assert.deepEqual(ownLocal(yelm, 'thurston'), [
    'thurston-timberland-regional-library-district-proposition-no-1',
    'thurston-yelm-community-schools-proposition-no-1',
  ])
  // Pierce's own Yelm Community Schools copy is scoped to Pierce.
  assert.ok(!yelm.measures.some((m) => m.owner === 'pierce'))
  // 420 College St SE, Lacey: Lacey Fire District 3's bonds.
  const lacey = ballotFor(thu({ CONGDST: '10', LEGDST: '22', CITY: 'Lacey', FIRDST: 'FD03', FIRE_AUTH: 'Lacey', SCHDST: 'NORTH THURSTON' }))
  assert.ok(ownLocal(lacey, 'thurston').includes('thurston-thurston-county-fire-protection-district-no-3-lacey-fire-district-3-proposition-no-1'))
  assert.equal(coverageAdvice(thu({})), null)
})

test('a Spokane ballot: its own districts, school and fire measures by name, no PUD seat', () => {
  const SPOKANE = { id: 'spokane', fips: '53063', name: 'Spokane County' }
  const spo = (districts) => ({ coverageStatus: 'partial_county', county: SPOKANE, districts, missingLayers: [] })
  // 808 W Spokane Falls Blvd, Spokane (live 2026-10-08, see geo.js).
  const downtown = ballotFor(spo({
    CONGDST: '5', LEGDST: '3', CITY: 'Spokane', COUNTY_COUNCIL: '1', SCHDST: 'Spokane #81', FIRDST: 'City of Spokane',
  }))
  const slugs = downtown.contests.map((c) => c.slug)
  assert.equal(new Set(slugs).size, slugs.length)
  for (const slug of SUPREME_COURT) assert.ok(slugs.includes(slug), slug)
  assert.ok(slugs.includes('spokane-congressional-district-5-u-s-representative'))
  assert.ok(slugs.includes('spokane-legislative-district-3-state-representative-pos-1'))
  assert.ok(slugs.includes('spokane-spokane-county-sheriff'))
  assert.ok(!slugs.some((s) => s.includes('public-utility-district')), slugs.join())
  const dm = downtown.measures.map((m) => m.slug)
  assert.ok(dm.includes('spokane-spokane-school-district-no-81-proposition-no-1'))
  assert.ok(!dm.some((s) => s.includes('fire-protection-district')), dm.join())
  // 3801 E Farwell Rd, Mead: Fire District 9's two propositions.
  const mead = ballotFor(spo({ CONGDST: '5', LEGDST: '4', COUNTY_COUNCIL: '3', SCHDST: 'Mead #354', FIRDST: 'Fire District 9' }))
  const mm = mead.measures.map((m) => m.slug)
  assert.ok(mm.includes('spokane-spokane-county-fire-protection-district-no-9-proposition-no-1'))
  assert.ok(mm.includes('spokane-spokane-county-fire-protection-district-no-9-proposition-no-2'))
  assert.ok(!mm.some((s) => s.includes('school-district')), mm.join())
  assert.equal(coverageAdvice(spo({})), 'degraded')
})

test('a Pierce ballot: its own districts, King\'s research for shared races, transit and school measures by flag and name', () => {
  const PIERCE = { id: 'pierce', fips: '53053', name: 'Pierce County' }
  const pie = (districts) => ({ coverageStatus: 'full_county', county: PIERCE, districts, missingLayers: [] })
  const local = (ballot) => ballot.measures.filter((m) => m.owner === 'pierce' && !m.slug.includes('charter')).map((m) => m.slug)
  // Districts as the live District Adapter resolved them on 2026-10-08.
  // 930 Tacoma Ave S, Tacoma.
  const tacoma = ballotFor(pie({
    CONGDST: '6', LEGDST: '27', CITY: 'Tacoma', COUNTY_COUNCIL: '4', FIRDST: 'TACOMA', DISTCRT: 'YES',
    KCDISTCRT: 'NO', PTBA: 'YES', SCHDST: 'TACOMA SCHOOL DISTRICT NO. 10',
  }))
  const ts = tacoma.contests.map((c) => c.slug)
  assert.equal(new Set(ts).size, ts.length)
  for (const slug of SUPREME_COURT) assert.ok(ts.includes(slug), slug)
  assert.deepEqual(tacoma.measures.slice(0, 3).map((m) => m.slug), STATE_MEASURES)
  assert.ok(ts.includes('pierce-congressional-district-6-u-s-representative'))
  assert.ok(ts.includes('pierce-pierce-county-district-court-no-7-judge-position-no-7'))
  assert.equal(ts.filter((s) => s.startsWith('pierce-city-of-tacoma-tacoma-municipal-court-')).length, 3)
  // No council seat is up in District 4; no King District Court seat.
  assert.ok(!ts.some((s) => s.includes('county-council') || s.includes('king-county-district-court')), ts.join())
  assert.deepEqual(local(tacoma), ['pierce-pierce-transit-proposition-no-1', 'pierce-city-of-tacoma-initiative-no-1'])
  assert.equal(tacoma.measures.filter((m) => m.slug.includes('charter-amendment')).length, 7)
  // 1402 Lake Tapps Pkwy SE, Auburn: CD 10 (Census and the precinct layer
  // agree), LD 31 and King County District Court's Southeast seats, with
  // King's research; Auburn SD 408's Pierce copy, never King's.
  const auburn = ballotFor(pie({
    CONGDST: '10', LEGDST: '31', CITY: 'Auburn', COUNTY_COUNCIL: '1', FIRDST: 'VALLEY REGIONAL FIRE AUTHORITY',
    DISTCRT: 'NO', KCDISTCRT: 'YES', PTBA: 'YES', SCHDST: 'AUBURN SCHOOL DISTRICT NO. 408',
  }))
  const as = auburn.contests.map((c) => c.slug)
  assert.equal(as.filter((s) => s.startsWith('pierce-king-county-district-court-southeast-')).length, 6)
  assert.ok(!as.some((s) => s.startsWith('pierce-pierce-county-district-court-')), as.join())
  assert.ok(as.includes('pierce-pierce-county-council-district-1-county-councilmember'))
  assert.ok(!auburn.contests.some((c) => c.owner === 'king'))
  const sec5 = auburn.contests.find((c) => c.slug === 'pierce-king-county-district-court-southeast-electoral-district-judge-position-no-5')
  const king5 = data.contests.find((c) => c.slug === 'judge-position-no-5-southeast-electoral-district')
  assert.deepEqual(sec5.candidates.map((c) => c.scores), king5.candidates.map((c) => c.scores))
  assert.deepEqual(local(auburn), ['pierce-pierce-transit-proposition-no-1', 'pierce-auburn-school-district-no-408-proposition-no-1'])
  assert.ok(!auburn.measures.some((m) => m.owner === 'king'))
  // 811 Main St, Buckley: CD 8 with King's scoring; outside Pierce Transit.
  const buckley = ballotFor(pie({
    CONGDST: '8', LEGDST: '31', CITY: 'Buckley', COUNTY_COUNCIL: '1', FIRDST: 'BUCKLEY', DISTCRT: 'YES',
    KCDISTCRT: 'NO', PTBA: 'NO', SCHDST: 'WHITE RIVER SCHOOL DISTRICT NO. 416',
  }))
  const cd8 = buckley.contests.find((c) => c.slug === 'pierce-congressional-district-8-u-s-representative')
  const kingCd8 = data.contests.find((c) => c.slug === 'congressional-district-8-united-states-representative')
  assert.deepEqual(cd8.candidates.map((c) => c.scores), kingCd8.candidates.map((c) => c.scores))
  assert.deepEqual(local(buckley), [])
  // 3510 Grandview St, Gig Harbor: Council District 7.
  const gigHarbor = ballotFor(pie({
    CONGDST: '6', LEGDST: '26', CITY: 'Gig Harbor', COUNTY_COUNCIL: '7', FIRDST: 'FPD #005 GIG HARBOR', DISTCRT: 'YES',
    KCDISTCRT: 'NO', PTBA: 'YES', SCHDST: 'PENINSULA SCHOOL DISTRICT NO. 401',
  }))
  assert.ok(gigHarbor.contests.some((c) => c.slug === 'pierce-pierce-county-council-district-7-county-councilmember'))
  assert.equal(coverageAdvice(pie({})), null)
})

test('a Snohomish ballot: statewide races once, its districts and District Court seats, South County Fire only inside the RFA', () => {
  const SNOHOMISH = { id: 'snohomish', fips: '53061', name: 'Snohomish County' }
  const sno = (districts) => ({ coverageStatus: 'full_county', county: SNOHOMISH, districts, missingLayers: [] })
  // 19100 44th Ave W, Lynnwood (live 2026-10-08, see geo.js RFADST, DISTCRT).
  const lynnwood = ballotFor(sno({
    CONGDST: '2', LEGDST: '32', CITY: 'Lynnwood', RFADST: 'SCRFA', DISTCRT: 'South District Court',
  }))
  const slugs = lynnwood.contests.map((c) => c.slug)
  assert.equal(new Set(slugs).size, slugs.length)
  for (const slug of SUPREME_COURT) assert.ok(slugs.includes(slug), slug)
  assert.ok(slugs.includes('snohomish-legislative-district-32-state-senator'))
  // Only the South District Court's three seats, not the other districts'.
  const courts = slugs.filter((s) => s.includes('district-court'))
  assert.deepEqual(courts.sort(), [1, 2, 3].map((n) => `snohomish-snohomish-county-district-court-south-district-judge-position-no-${n}`))
  assert.ok(lynnwood.measures.some((m) => m.slug.includes('south-snohomish-county-fire-rescue')))
  const monroe = ballotFor(sno({
    CONGDST: '1', LEGDST: '12', CITY: 'Monroe', HOSPDST: 'Hospital District 1', DISTCRT: 'Evergreen District Court',
  }))
  assert.ok(!monroe.measures.some((m) => m.slug.includes('south-snohomish-county-fire-rescue')))
  assert.ok(monroe.measures.some((m) => m.slug === 'snohomish-public-hospital-district-no-1-proposition-no-1'))
  assert.deepEqual(monroe.contests.map((c) => c.slug).filter((s) => s.includes('district-court')).sort(),
    [1, 2].map((n) => `snohomish-snohomish-county-district-court-evergreen-district-judge-position-no-${n}`))
  assert.equal(coverageAdvice(sno({})), null)
})

test('each Supreme Court contest ships once, owned by the statewide package', () => {
  for (const slug of SUPREME_COURT) {
    const found = data.contests.filter((c) => c.slug === slug)
    assert.equal(found.length, 1, slug)
    assert.equal(found[0].owner, 'statewide')
    assert.deepEqual(found[0].scope, { kind: 'STATEWIDE' })
  }
  const slugs = data.contests.map((c) => c.slug)
  assert.equal(new Set(slugs).size, slugs.length)
})

test('outside the shipped counties, an address gets all five court races and all three initiatives only', () => {
  const { contests, measures } = ballotFor(yakima)
  assert.deepEqual(contests.map((c) => c.slug), SUPREME_COURT)
  assert.deepEqual(measures.map((m) => m.slug), STATE_MEASURES)
  assert.equal(coverageAdvice(yakima), 'statewide-only')
})

test('every King ballot carries the statewide races once, the countywide races and its district races', () => {
  const COUNTYWIDE = [
    'prosecuting-attorney',
    'assessor',
    'director-of-elections',
    'court-of-appeals-division-1-district-1-judge-position-no-5',
    'court-of-appeals-division-1-district-1-judge-position-no-6',
  ]
  for (const [name, context] of Object.entries(ADDRESSES)) {
    const { contests, measures } = ballotFor(context)
    const slugs = contests.map((c) => c.slug)
    assert.equal(new Set(slugs).size, slugs.length, name)
    for (const slug of [...SUPREME_COURT, ...COUNTYWIDE]) assert.ok(slugs.includes(slug), `${name}: ${slug}`)
    assert.deepEqual(measures.slice(0, 3).map((m) => m.slug), STATE_MEASURES, name)
    assert.ok(slugs.includes(`congressional-district-${context.districts.CONGDST}-united-states-representative`), name)
    assert.ok(slugs.some((s) => s.endsWith(`legislative-district-no-${context.districts.LEGDST}`)), name)
    // The district court contests are exactly the voter's electoral district's.
    const court = { NE: 'northeast', SE: 'southeast', SW: 'southwest', W: 'west', SH: 'shoreline' }[context.districts.JUDDST]
    const courts = slugs.filter((s) => /^judge-position-no-\d+-.+-electoral-district$/.test(s))
    assert.ok(courts.length >= 2, name)
    for (const s of courts) assert.ok(s.endsWith(`-${court}-electoral-district`), `${name}: ${s}`)
    assert.equal(coverageAdvice(context), null)
  }
})

test('Seattle gets Seattle Prop 1 and Municipal Court; Council D5 only inside D5', () => {
  for (const name of ['cityHall', 'pinehurst']) {
    const { contests, measures } = ballotFor(ADDRESSES[name])
    const slugs = contests.map((c) => c.slug)
    assert.ok(measures.some((m) => m.slug === 'city-of-seattle-proposition-no-1'), name)
    assert.equal(slugs.filter((s) => s.startsWith('municipal-court-judge-position-no-')).length, 7, name)
    assert.equal(slugs.includes('council-district-no-5-city-of-seattle'), name === 'pinehurst', name)
  }
})

test('local measures reach exactly their own district', () => {
  const local = (name) => ballotFor(ADDRESSES[name]).measures.filter((m) => m.owner === 'king').map((m) => m.slug)
  assert.deepEqual(local('cityHall'), ['city-of-seattle-proposition-no-1'])
  assert.deepEqual(local('shoreline'), ['city-of-shoreline-proposition-no-1'])
  assert.deepEqual(local('vashon'), ['king-county-cemetery-district-no-1-proposition-no-1'])
  assert.deepEqual(local('kent'), ['kent-school-district-no-415-proposition-no-1'])
  assert.deepEqual(local('auburn'), ['auburn-school-district-no-408-proposition-no-1'])
})

test('uncontested King contests ship information-only, with no scores', () => {
  const uncontested = data.contests.filter((c) => c.owner === 'king' && c.uncontested)
  assert.ok(uncontested.length >= 30)
  for (const c of uncontested) {
    assert.equal(c.candidates.length, 1, c.slug)
    assert.deepEqual(c.candidates[0].scores, {}, c.slug)
  }
  // Most carry a researched summary; the rest are the official ballot entry.
  const levels = new Set(uncontested.map((c) => c.candidates[0].evidence_level))
  for (const level of levels) assert.ok(['rich', 'moderate', 'pamphlet-only', 'official-ballot-only'].includes(level), level)
  assert.ok(uncontested.filter((c) => c.candidates[0].summary).length >= 30)
})

// The interview is ballot-driven: a King ballot reaches all fifteen axes,
// parental-rights included; the statewide-only ballot reaches eight.
const STATEWIDE_AXES = ['experience', 'judicial', 'local-control', 'parental-rights', 'safety', 'social', 'spending', 'taxes']

test('the statewide-only interview asks only about axes on the statewide ballot', () => {
  const { axes, items } = ballotFor(yakima)
  assert.deepEqual([...axes].sort(), STATEWIDE_AXES)
  assert.deepEqual(items.map((i) => i.id), [
    'card-taxes',
    'card-spending',
    'scenario-safety',
    'card-experience',
    'card-local',
    'scenario-budget',
    'card-social',
    'card-parental-rights',
    'card-judicial',
  ])
})

test('every King interview asks the parental-rights card and covers the whole rubric', () => {
  for (const [name, context] of Object.entries(ADDRESSES)) {
    const { axes, items } = ballotFor(context)
    assert.equal(axes.size, data.rubric.axes.length, name)
    assert.ok(items.some((i) => i.id === 'card-parental-rights'), name)
  }
})

const agreeWithEverything = (items) =>
  buildProfile(
    items.map((item) => ({ item, choice: item.kind === 'statement' ? 'agree' : 0 })),
    {}
  )

test('a voter who answers the interview gets a lean on every measure on the ballot', () => {
  for (const context of [yakima, ...Object.values(ADDRESSES)]) {
    const { measures, items } = ballotFor(context)
    const answers = agreeWithEverything(items)
    for (const m of measures) {
      const { lean } = measureLean(m, answers)
      assert.ok(['yes', 'no', 'split'].includes(lean), `${m.slug}: lean ${lean}`)
    }
  }
})

test('every contested race ranks all its candidates', () => {
  const { items } = ballotFor(ADDRESSES.cityHall)
  const answers = agreeWithEverything(items)
  for (const c of data.contests.filter((x) => !x.uncontested)) {
    const { rows } = rankContest(c, answers)
    assert.equal(rows.length, c.candidates.length, c.slug)
    assert.ok(c.candidates.length >= 2, c.slug)
  }
})

const briefFor = (context) => {
  const { contests, measures, items } = ballotFor(context)
  return {
    contests,
    measures,
    text: buildBrief(data, context, agreeWithEverything(items), contests, measures, 'https://example.test/washington-state#p=abc', ''),
  }
}

test('the statewide-only Ballot Brief carries the warning and every contest and measure', () => {
  const { contests, measures, text } = briefFor(yakima)
  assert.match(text, /November 3, 2026 General Election/)
  assert.match(text, /Coverage: STATEWIDE-ONLY GUIDE/)
  assert.match(text, /omits county, city, school, fire, judicial district, and other local contests/)
  assert.match(text, /Resolved county: Yakima County/)
  for (const c of contests) assert.ok(text.includes(`## SUPREME COURT — ${c.district}`), c.slug)
  assert.match(text, /## BALLOT MEASURES/)
  for (const m of measures) {
    const line = text.split('\n').find((l) => l.startsWith(`### ${m.jurisdiction} ${m.proposition}:`))
    assert.ok(line, `${m.slug} missing from brief`)
    assert.match(line, /leans (YES|NO) for me|genuinely split for me/, line)
  }
})

test('a King Ballot Brief is a full county guide naming every contest once and every measure', () => {
  const { contests, measures, text } = briefFor(ADDRESSES.pinehurst)
  assert.match(text, /^Coverage: FULL COUNTY GUIDE\.$/m)
  assert.match(text, /contests on the November 3, 2026 General Election ballot that Voter Lifeboat matched/)
  assert.match(text, /Resolved county: King County/)
  assert.doesNotMatch(text, /STATEWIDE-ONLY|PARTIAL COUNTY/)
  for (const c of contests) {
    const { office, place } = contestHeading(c)
    const heading = `## ${office.toUpperCase()} — ${place}`
    assert.equal(text.split('\n').filter((l) => l === heading).length, 1, heading)
  }
  assert.equal(text.split('\n').filter((l) => l.startsWith('## SUPREME COURT')).length, 5)
  for (const m of measures)
    assert.ok(text.split('\n').some((l) => l.startsWith(`### ${m.jurisdiction} ${m.proposition}:`)), m.slug)
  assert.match(text, /Official pamphlet statement: https:\/\/cdn\.kingcounty\.gov\/.*local-edition\.pdf#page=\d+/)
  assert.match(text, /Official pamphlet statement: https:\/\/www\.sos\.wa\.gov\/.*Edition%2004.*#page=\d+/)
})

test('the general Ballot Brief names election day, terms and SOS pamphlet pages, never the primary', () => {
  const { text } = briefFor(yakima)
  assert.match(text, /^# MY BALLOT BRIEF — Washington State, November 3, 2026 General Election$/m)
  assert.match(text, /^Election day: Tuesday, November 3, 2026\.$/m)
  assert.match(text, /statewide contests on the November 3, 2026 General Election ballot/)
  assert.match(text, /^Term: 2-year unexpired term$/m)
  assert.match(text, /Official pamphlet (statement|entry): https:\/\/www\.sos\.wa\.gov\/.*#page=\d+/)
  // Candidate summaries and sources may mention August or King County; the
  // brief's own copy and pamphlet links must not.
  assert.doesNotMatch(text, /past the primary|top 2/i)
  for (const line of text.split('\n').filter((l) => l.startsWith('Official pamphlet')))
    assert.match(line, /: https:\/\/www\.sos\.wa\.gov\//, line)
  const kingText = briefFor(ADDRESSES.kent).text
  assert.doesNotMatch(kingText, /past the primary|top 2|voters-pamphlets\/2026\/08/i)
})

test('the general ships contest terms from the statewide package', () => {
  const terms = Object.fromEntries(data.contests.map((c) => [c.slug, c.term]))
  assert.equal(terms['justice-position-no-1-supreme-court'], '2-year unexpired term')
  assert.equal(terms['justice-position-no-5-supreme-court'], '2-year unexpired term')
  assert.equal(terms['justice-position-no-3-supreme-court'], '6-year term')
})

test('the King Ballot Brief heads each contest office first, then where (issue #25)', () => {
  const { text } = briefFor(ADDRESSES.pinehurst)
  assert.match(text, /^## STATE SENATOR — Legislative District 46$/m)
  assert.match(text, /^## STATE REPRESENTATIVE POSITION NO\. 1 — Legislative District 46$/m)
  assert.match(text, /^## JUDGE POSITION NO\. 1 — King County District Court, West Electoral District$/m)
  assert.match(text, /^## COUNCIL DISTRICT NO\. 5 — City of Seattle$/m)
  assert.match(text, /^## PROSECUTING ATTORNEY — Countywide$/m)
  assert.doesNotMatch(text, /^## (LEGISLATIVE DISTRICT|CITY OF|\w+ ELECTORAL DISTRICT)/m)
})
