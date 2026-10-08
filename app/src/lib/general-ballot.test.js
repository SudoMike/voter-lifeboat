// The November 3, 2026 general as shipped: King County at Full County
// Coverage (issue #16), Spokane at partial coverage, Pierce at full coverage
// (#21), Snohomish at full coverage (#27), Clark, Kitsap and Thurston at full
// coverage (#22), Yakima, Whatcom, Benton, Skagit, Cowlitz and Grant at full
// coverage (#28), Island, Lewis, Franklin, Chelan, Clallam and Grays Harbor at
// full coverage (#29), Mason, Walla Walla, Stevens, Whitman and Douglas at full coverage and Okanogan at
// partial coverage (#30), Jefferson and Kittitas at full coverage (#31), every other Washington address a Statewide-Only Guide (issue #9). These run the app's own ballot, interview, lean and Ballot Brief
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
// general does not ship (geo.test.js covers the lookup itself). Garfield
// since #30 shipped Walla Walla.
const garfield = {
  coverageStatus: 'statewide_only',
  county: { id: 'garfield', fips: '53023', name: 'Garfield County' },
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

test('the general ships twenty-five counties at full county coverage, Spokane and Okanogan at partial, with their elections offices', () => {
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
      {
        // Full: Commissioner District 1 (elected by district) resolves from
        // the county commissioner layer; no local measures (#28).
        id: 'yakima',
        name: 'Yakima County',
        state: 'WA',
        fips: '53077',
        coverage: 'full_county',
        elections_url: 'https://www.yakimacounty.us/170/Elections',
      },
      {
        // Full: port and PUD seats are countywide; Fire District 1's levy
        // resolves from DOR FIR2025 (#28).
        id: 'whatcom',
        name: 'Whatcom County',
        state: 'WA',
        fips: '53073',
        coverage: 'full_county',
        elections_url: 'https://www.whatcomcounty.us/2794/Elections',
      },
      {
        // Full: the PUD seat (PUDDST) resolves from the Auditor's
        // PrecinctSplits layer, the Ki-Be levy (SCHDST) from DOR SCH2025 (#28).
        id: 'benton',
        name: 'Benton County',
        state: 'WA',
        fips: '53005',
        coverage: 'full_county',
        elections_url: 'https://www.bentoncountywa.gov/government/elected_officials/auditor/elections/index.php',
      },
      {
        // Full: PUD and commissioner seats are countywide; the Fire District 5
        // and La Conner SD levies resolve from DOR FIR2025/SCH2025 (#28).
        id: 'skagit',
        name: 'Skagit County',
        state: 'WA',
        fips: '53057',
        coverage: 'full_county',
        elections_url: 'https://www.skagitcountywa.gov/government/auditor-s-office/elections-and-voting/',
      },
      {
        // Full: every county seat is countywide; one city measure (#28).
        id: 'cowlitz',
        name: 'Cowlitz County',
        state: 'WA',
        fips: '53015',
        coverage: 'full_county',
        elections_url: 'https://www.co.cowlitz.wa.us/2357/Elections',
      },
      {
        // Full: fire, cemetery and hospital district measures resolve from
        // DOR FIR2025, CEM2025 and HSP2025 (#28).
        id: 'grant',
        name: 'Grant County',
        state: 'WA',
        fips: '53025',
        coverage: 'full_county',
        elections_url: 'https://www.grantcountywa.gov/270/Elections',
      },
      {
        // Full: the Camano PUD seat reads the Auditor's precinct layer; the
        // port and unincorporated-county measures read DOR PRT2025 and
        // TCA2025 (#29).
        id: 'island',
        name: 'Island County',
        state: 'WA',
        fips: '53029',
        coverage: 'full_county',
        elections_url: 'https://www.islandcountywa.gov/423/Elections-Voter-Registration',
      },
      {
        // Full: the PUD seat and Timberland levy read DOR PUD2025 and LIB2025 (#29).
        id: 'lewis',
        name: 'Lewis County',
        state: 'WA',
        fips: '53041',
        coverage: 'full_county',
        elections_url: 'https://elections.lewiscountywa.gov/',
      },
      {
        // Full: the Port of Pasco seat reads the county's port layer, the FPD 3
        // levy DOR FIR2025 (#29).
        id: 'franklin',
        name: 'Franklin County',
        state: 'WA',
        fips: '53021',
        coverage: 'full_county',
        elections_url: 'https://www.franklincountywa.gov/Elections',
      },
      {
        // Full: Wenatchee SD 246 reads DOR SCH2025 (#29).
        id: 'chelan',
        name: 'Chelan County',
        state: 'WA',
        fips: '53007',
        coverage: 'full_county',
        elections_url: 'https://www.co.chelan.wa.us/elections',
      },
      {
        // Full: District Court 1 and 2 read the Auditor's District_Court layer,
        // the PUD seat PUDALL (any feature of the PUD's district layer), QVSD
        // DOR SCH2025 (#29).
        id: 'clallam',
        name: 'Clallam County',
        state: 'WA',
        fips: '53009',
        coverage: 'full_county',
        elections_url: 'https://www.clallamcountywa.gov/162/Elections-Voter-Registration',
      },
      {
        // Full: the Timberland levy and McCleary SD 65 read DOR LIB2025 and SCH2025 (#29).
        id: 'grays-harbor',
        name: 'Grays Harbor County',
        state: 'WA',
        fips: '53027',
        coverage: 'full_county',
        elections_url: 'https://www.graysharbor.us/government/Auditors/elections.php',
      },
      {
        // Full: the PUD No. 1 and No. 3 seats read DOR PUD2025, the school
        // measures DOR SCH2025 (#30).
        id: 'mason',
        name: 'Mason County',
        state: 'WA',
        fips: '53045',
        coverage: 'full_county',
        elections_url: 'https://www.masoncountywa.gov/departments/auditor/elections/index.php',
      },
      {
        // Full: the Dixie SD 101 and Prescott park levies read DOR SCH2025
        // and PKR2025 (#30).
        id: 'walla-walla',
        name: 'Walla Walla County',
        state: 'WA',
        fips: '53071',
        coverage: 'full_county',
        elections_url: 'https://www.wwcowa.gov/government/auditor/current_election.php',
      },
      {
        // Full: the library, Fire District 10 and Nine Mile Falls SD measures
        // read DOR LIB2025, FIR2025 and SCH2025 (#30).
        id: 'stevens',
        name: 'Stevens County',
        state: 'WA',
        fips: '53065',
        coverage: 'full_county',
        elections_url: 'https://www.stevenscountywa.gov/20911/Elections',
      },
      {
        // Full: the library, cemetery and Cheney SD measures read DOR LIB2025,
        // CEM2025 and SCH2025 (#30).
        id: 'whitman',
        name: 'Whitman County',
        state: 'WA',
        fips: '53075',
        coverage: 'full_county',
        elections_url: 'https://www.whitmancounty.gov/172/Current-Election',
      },
      {
        // Full: Eastmont SD and Cemetery District 2 read DOR SCH2025 and
        // CEM2025; the proposed Rimrock Meadows fire district the county's
        // own fire layer (PROPFIRDST, #30).
        id: 'douglas',
        name: 'Douglas County',
        state: 'WA',
        fips: '53017',
        coverage: 'full_county',
        elections_url: 'https://www.douglascountywa.gov/206/Current-Election',
      },
      {
        // Partial: the Okanogan County PUD seat (247 of 248 precincts) and
        // Ferry County PUD No. 1's (the other 8) are PUDDST, which no public
        // layer separates (#30).
        id: 'okanogan',
        name: 'Okanogan County',
        state: 'WA',
        fips: '53047',
        coverage: 'partial_county',
        elections_url: 'https://www.okanogancounty.gov/337/Elections',
      },
      {
        // Full: the West End Quillayute Valley SD 402 bonds and Clallam FD 1
        // levy read DOR SCH2025 ('402') and FIR2025 ('9') (#31).
        id: 'jefferson',
        name: 'Jefferson County',
        state: 'WA',
        fips: '53031',
        coverage: 'full_county',
        elections_url: 'https://www.co.jefferson.wa.us/1266/Elections',
      },
      {
        // Full: the Upper and Lower District Court seats read the Auditor's
        // Court_Districts layer (DISTCRT, #31).
        id: 'kittitas',
        name: 'Kittitas County',
        state: 'WA',
        fips: '53037',
        coverage: 'full_county',
        elections_url: 'https://www.co.kittitas.wa.us/auditor/elections/default.aspx',
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

test('a Yakima ballot: Benton\'s research for CD 4, Commissioner District 1 only inside district 1', () => {
  const YAKIMA = { id: 'yakima', fips: '53077', name: 'Yakima County' }
  const yak = (districts) => ({ coverageStatus: 'full_county', county: YAKIMA, districts, missingLayers: [] })
  // Districts as the live District Adapter resolved them on 2026-10-08.
  // 128 N 2nd St, Yakima: commissioner district 2, no commissioner race.
  const yakima = ballotFor(yak({ CONGDST: '4', LEGDST: '14', CITY: 'Yakima', COUNTY_COUNCIL: '2' }))
  const ys = yakima.contests.map((c) => c.slug)
  assert.equal(new Set(ys).size, ys.length)
  for (const slug of SUPREME_COURT) assert.ok(ys.includes(slug), slug)
  assert.deepEqual(yakima.measures.map((m) => m.slug), STATE_MEASURES)
  sameScoring(yakima, 'yakima-congressional-district-4-u-s-representative', 'benton-congressional-district-4-u-s-representative')
  assert.ok(!yakima.contests.some((c) => c.owner === 'benton'))
  assert.ok(ys.includes('yakima-legislative-district-14-state-representative-pos-1'))
  assert.ok(!ys.some((s) => s.includes('commissioner-district-1')), ys.join())
  // 115 W Naches Ave, Selah: LD 15, Commissioner District 1.
  const selah = ballotFor(yak({ CONGDST: '4', LEGDST: '15', CITY: 'Selah', COUNTY_COUNCIL: '1' }))
  const ss = selah.contests.map((c) => c.slug)
  assert.ok(ss.includes('yakima-yakima-county-commissioner-district-1-county-commissioner-district-1'))
  assert.ok(ss.includes('yakima-legislative-district-15-state-representative-pos-2'))
  assert.ok(!ss.some((s) => s.includes('district-14')), ss.join())
  assert.equal(coverageAdvice(yak({})), null)
})

test('a Whatcom ballot: Snohomish\'s research for CD 2, Bellingham and Fire District 1 measures by district', () => {
  const WHATCOM = { id: 'whatcom', fips: '53073', name: 'Whatcom County' }
  const wha = (districts) => ({ coverageStatus: 'full_county', county: WHATCOM, districts, missingLayers: [] })
  // 1101 Harris Ave, Bellingham.
  const bellingham = ballotFor(wha({ CONGDST: '2', LEGDST: '40', CITY: 'Bellingham', PORTDST: '1' }))
  const bs = bellingham.contests.map((c) => c.slug)
  assert.equal(new Set(bs).size, bs.length)
  for (const slug of SUPREME_COURT) assert.ok(bs.includes(slug), slug)
  sameScoring(bellingham, 'whatcom-congressional-district-2-u-s-representative', 'snohomish-congressional-district-2-u-s-representative')
  assert.ok(!bellingham.contests.some((c) => c.owner === 'snohomish'))
  // Port and PUD seats are elected countywide in the general.
  for (const slug of [
    'whatcom-port-of-bellingham-commissioner-district-4-commissioner-district-4',
    'whatcom-port-of-bellingham-commissioner-district-5-commissioner-district-5',
    'whatcom-public-utility-district-no-1-of-whatcom-county-commissioner-district-1',
    'whatcom-legislative-district-40-state-representative-pos-1',
  ]) assert.ok(bs.includes(slug), slug)
  assert.deepEqual(ownLocal(bellingham, 'whatcom'), [
    'whatcom-city-of-bellingham-proposition-2026-06',
    'whatcom-city-of-bellingham-proposition-2026-07',
    'whatcom-city-of-bellingham-initiative-26-01',
  ])
  // 111 W Main St, Everson: LD 42, Fire District 1.
  const everson = ballotFor(wha({ CONGDST: '2', LEGDST: '42', CITY: 'Everson', PORTDST: '4', FIRDST: '1' }))
  assert.ok(everson.contests.some((c) => c.slug === 'whatcom-legislative-district-42-state-senator'))
  assert.deepEqual(ownLocal(everson, 'whatcom'), ['whatcom-whatcom-county-fire-protection-district-no-1-proposition-2026-08'])
  assert.equal(coverageAdvice(wha({})), null)
})

test('a Benton ballot: Yakima\'s research for LD 14/15, the PUD seat only inside the PUD, Ki-Be levy only in SD 52', () => {
  const BENTON = { id: 'benton', fips: '53005', name: 'Benton County' }
  const ben = (districts) => ({ coverageStatus: 'full_county', county: BENTON, districts, missingLayers: [] })
  const PUD = 'benton-public-utility-district-commissioner-district-2-commissioner-pos-2'
  // 210 W 6th Ave, Kennewick: LD 8, Benton PUD, Kennewick SD 17.
  const kennewick = ballotFor(ben({ CONGDST: '4', LEGDST: '8', CITY: 'Kennewick', COUNTY_COUNCIL: '3', PUDDST: 'Benton PUD', SCHDST: '17' }))
  const ks = kennewick.contests.map((c) => c.slug)
  assert.equal(new Set(ks).size, ks.length)
  for (const slug of SUPREME_COURT) assert.ok(ks.includes(slug), slug)
  assert.ok(ks.includes('benton-congressional-district-4-u-s-representative'))
  assert.ok(ks.includes('benton-legislative-district-8-state-senator'))
  assert.ok(ks.includes(PUD))
  assert.ok(!ks.includes('benton-city-of-richland-council-pos-4'))
  assert.deepEqual(ownLocal(kennewick, 'benton'), [])
  // 1009 Dale Ave, Benton City: LD 16, Benton City props, Ki-Be levy, PUD.
  const bc = ballotFor(ben({
    CONGDST: '4', LEGDST: '16', CITY: 'Benton City', COUNTY_COUNCIL: '2', FIRDST: '2', PUDDST: 'Benton PUD', SCHDST: '52',
  }))
  assert.ok(bc.contests.some((c) => c.slug === PUD))
  assert.deepEqual(ownLocal(bc, 'benton'), [
    'benton-city-of-benton-city-proposition-no-1',
    'benton-city-of-benton-city-proposition-no-2',
    'benton-kiona-benton-city-school-district-no-52-proposition-no-1',
  ])
  // 625 Swift Blvd, Richland: no PUD race; Richland Council Pos. 4.
  const richland = ballotFor(ben({ CONGDST: '4', LEGDST: '16', CITY: 'Richland', COUNTY_COUNCIL: '1', SCHDST: '400' }))
  const rs = richland.contests.map((c) => c.slug)
  assert.ok(!rs.includes(PUD))
  assert.ok(rs.includes('benton-city-of-richland-council-pos-4'))
  // An LD 15 address: Yakima's research for the House seats.
  const ld15 = ballotFor(ben({ CONGDST: '4', LEGDST: '15', COUNTY_COUNCIL: '3', PUDDST: 'Benton PUD' }))
  for (const pos of [1, 2])
    sameScoring(ld15, `benton-legislative-district-15-state-representative-pos-${pos}`, `yakima-legislative-district-15-state-representative-pos-${pos}`)
  assert.ok(!ld15.contests.some((c) => c.owner === 'yakima'))
  assert.equal(coverageAdvice(ben({})), null)
})

test('a Skagit ballot: Snohomish\'s research for CD 2 and LD 10, Whatcom\'s for LD 40, levies by district', () => {
  const SKAGIT = { id: 'skagit', fips: '53057', name: 'Skagit County' }
  const ska = (districts) => ({ coverageStatus: 'full_county', county: SKAGIT, districts, missingLayers: [] })
  // Districts as the live District Adapter resolved them on 2026-10-08.
  // 700 S 2nd St, Mount Vernon.
  const mv = ballotFor(ska({ CONGDST: '2', LEGDST: '10', CITY: 'Mount Vernon', COUNTY_COUNCIL: '2', HOSPDST: '1', SCHDST: '320' }))
  const ms = mv.contests.map((c) => c.slug)
  assert.equal(new Set(ms).size, ms.length)
  for (const slug of SUPREME_COURT) assert.ok(ms.includes(slug), slug)
  sameScoring(mv, 'skagit-congressional-district-2-u-s-representative', 'snohomish-congressional-district-2-u-s-representative')
  for (const pos of [1, 2])
    sameScoring(mv, `skagit-legislative-district-10-state-representative-pos-${pos}`, `snohomish-legislative-district-10-state-representative-pos-${pos}`)
  assert.ok(!mv.contests.some((c) => c.owner === 'snohomish'))
  // PUD and commissioner seats are elected countywide in the general.
  for (const slug of ['skagit-public-utility-district-commissioner-district-1-commissioner-1', 'skagit-skagit-county-commissioner-district-3'])
    assert.ok(ms.includes(slug), slug)
  assert.deepEqual(ownLocal(mv, 'skagit'), ['skagit-city-of-mount-vernon-proposition-no-1'])
  // 5800 Main St, Bow: LD 40, Fire District 5.
  const bow = ballotFor(ska({ CONGDST: '2', LEGDST: '40', COUNTY_COUNCIL: '1', FIRDST: '5', HOSPDST: '304', SCHDST: '100' }))
  for (const pos of [1, 2])
    sameScoring(bow, `skagit-legislative-district-40-state-representative-pos-${pos}`, `whatcom-legislative-district-40-state-representative-pos-${pos}`)
  assert.ok(!bow.contests.some((c) => c.owner === 'whatcom'))
  assert.deepEqual(ownLocal(bow, 'skagit'), ['skagit-skagit-county-fire-protection-district-no-5-proposition-no-1'])
  // 305 N 6th St, La Conner: La Conner SD 311.
  const lc = ballotFor(ska({ CONGDST: '2', LEGDST: '10', CITY: 'La Conner', COUNTY_COUNCIL: '1', SCHDST: '311' }))
  assert.deepEqual(ownLocal(lc, 'skagit'), ['skagit-la-conner-school-district-no-311-proposition-no-1'])
  assert.equal(coverageAdvice(ska({})), null)
})

test('a Cowlitz ballot: Thurston\'s research for LD 19, Clark\'s for CD 3 and LD 20, Longview Prop 1 only in Longview', () => {
  const COWLITZ = { id: 'cowlitz', fips: '53015', name: 'Cowlitz County' }
  const cow = (districts) => ({ coverageStatus: 'full_county', county: COWLITZ, districts, missingLayers: [] })
  // 1525 Broadway, Longview.
  const lv = ballotFor(cow({ CONGDST: '3', LEGDST: '19', CITY: 'Longview', COUNTY_COUNCIL: '2' }))
  const ls = lv.contests.map((c) => c.slug)
  assert.equal(new Set(ls).size, ls.length)
  for (const slug of SUPREME_COURT) assert.ok(ls.includes(slug), slug)
  sameScoring(lv, 'cowlitz-congressional-district-3-u-s-representative', 'clark-congressional-district-3-u-s-representative')
  for (const pos of [1, 2])
    sameScoring(lv, `cowlitz-legislative-district-19-state-representative-pos-${pos}`, `thurston-legislative-district-19-state-representative-pos-${pos}`)
  assert.ok(!lv.contests.some((c) => c.owner === 'thurston' || c.owner === 'clark'))
  assert.ok(ls.includes('cowlitz-public-utility-district-no-1-of-cowlitz-county-commissioner-district-1'))
  assert.deepEqual(ownLocal(lv, 'cowlitz'), ['cowlitz-city-of-longview-proposition-1'])
  // 200 E Scott Ave, Woodland: LD 20, no local measure.
  const wd = ballotFor(cow({ CONGDST: '3', LEGDST: '20', CITY: 'Woodland', COUNTY_COUNCIL: '1' }))
  for (const pos of [1, 2])
    sameScoring(wd, `cowlitz-legislative-district-20-state-representative-pos-${pos}`, `clark-legislative-district-20-state-representative-pos-${pos}`)
  assert.ok(!wd.contests.some((c) => c.slug.includes('district-19')))
  assert.deepEqual(ownLocal(wd, 'cowlitz'), [])
  assert.deepEqual(wd.measures.map((m) => m.slug), STATE_MEASURES)
  assert.equal(coverageAdvice(cow({})), null)
})

test('a Grant ballot: Benton\'s research for CD 4, the advisory vote countywide, district measures by district', () => {
  const GRANT = { id: 'grant', fips: '53025', name: 'Grant County' }
  const gra = (districts) => ({ coverageStatus: 'full_county', county: GRANT, districts, missingLayers: [] })
  const ADVISORY = 'grant-grant-county-advisory-vote-only-proposition-no-1'
  const HOSP4 = 'grant-grant-county-public-hospital-district-no-4-mckay-healthcare-rehabilitation-proposition-no-1'
  // 321 S Balsam St, Moses Lake: LD 13, Hospital District 1.
  const ml = ballotFor(gra({ CONGDST: '4', LEGDST: '13', CITY: 'Moses Lake', COUNTY_COUNCIL: '2', HOSPDST: '1' }))
  const ms = ml.contests.map((c) => c.slug)
  assert.equal(new Set(ms).size, ms.length)
  for (const slug of SUPREME_COURT) assert.ok(ms.includes(slug), slug)
  sameScoring(ml, 'grant-congressional-district-4-u-s-representative', 'benton-congressional-district-4-u-s-representative')
  assert.ok(!ml.contests.some((c) => c.owner === 'benton'))
  assert.ok(ms.includes('grant-legislative-district-13-state-representative-pos-1'))
  assert.ok(ms.includes('grant-court-of-appeals-division-3-district-2-judge-position-1'))
  assert.ok(!ms.some((s) => s.includes('district-16')), ms.join())
  assert.deepEqual(ownLocal(ml, 'grant'), [ADVISORY, 'grant-city-of-moses-lake-proposition-no-1'])
  // 127 Main Ave E, Soap Lake: Hospital District 4.
  const sl = ballotFor(gra({ CONGDST: '4', LEGDST: '13', CITY: 'Soap Lake', COUNTY_COUNCIL: '1', HOSPDST: '4' }))
  assert.deepEqual(ownLocal(sl, 'grant'), [ADVISORY, HOSP4])
  // 103 Railroad St, Wilson Creek: Cemetery District 2 too.
  const wc = ballotFor(gra({ CONGDST: '4', LEGDST: '13', CITY: 'Wilson Creek', COUNTY_COUNCIL: '1', HOSPDST: '4', CEMDST: '2' }))
  assert.deepEqual(ownLocal(wc, 'grant'), [ADVISORY, HOSP4, 'grant-grant-county-cemetery-district-no-2-wilson-creek-proposition-no-1'])
  // 34875 Park Lake Rd NE, Coulee City: Fire District 7.
  const cc = ballotFor(gra({ CONGDST: '4', LEGDST: '13', COUNTY_COUNCIL: '1', HOSPDST: '4', FIRDST: '7' }))
  assert.deepEqual(ownLocal(cc, 'grant'), [ADVISORY, HOSP4, 'grant-grant-county-fire-protection-district-no-7-proposition-no-1'])
  // An LD 16 address: Benton's research for the House seats.
  const ld16 = ballotFor(gra({ CONGDST: '4', LEGDST: '16', COUNTY_COUNCIL: '3' }))
  for (const pos of [1, 2])
    sameScoring(ld16, `grant-legislative-district-16-state-representative-pos-${pos}`, `benton-legislative-district-16-state-representative-pos-${pos}`)
  assert.equal(coverageAdvice(gra({})), null)
})

test('an Island ballot: Snohomish\'s research for CD 2, LD 10 and the Camano PUD seat, local measures by district', () => {
  const ISLAND = { id: 'island', fips: '53029', name: 'Island County' }
  const isl = (districts) => ({ coverageStatus: 'full_county', county: ISLAND, districts, missingLayers: [] })
  const PUD = 'island-public-utility-district-no-1-commissioner-district-1'
  const FIREWORKS = 'island-unincorporated-island-county-advisory-vote'
  // Districts as the live District Adapter resolved them on 2026-10-08.
  // 865 SW Barrington Dr, Oak Harbor: no PUD seat, port or advisory vote.
  const oh = ballotFor(isl({ CONGDST: '2', LEGDST: '10', CITY: 'Oak Harbor', COUNTY_COUNCIL: '2', LIBDST: 'L' }))
  const os = oh.contests.map((c) => c.slug)
  assert.equal(new Set(os).size, os.length)
  for (const slug of SUPREME_COURT) assert.ok(os.includes(slug), slug)
  sameScoring(oh, 'island-congressional-district-2-u-s-representative', 'snohomish-congressional-district-2-u-s-representative')
  for (const pos of [1, 2])
    sameScoring(oh, `island-legislative-district-10-state-representative-pos-${pos}`, `snohomish-legislative-district-10-state-representative-pos-${pos}`)
  assert.ok(!oh.contests.some((c) => c.owner === 'snohomish'))
  assert.ok(os.includes('island-island-county-county-commissioner-district-3'))
  assert.ok(!os.includes(PUD))
  assert.deepEqual(ownLocal(oh, 'island'), [])
  // 848 N Sunrise Blvd, Camano Island: the Snohomish PUD seat and the advisory vote.
  const cam = ballotFor(isl({ CONGDST: '2', LEGDST: '10', COUNTY_COUNCIL: '3', LIBDST: 'L', PUDDST: '53029', UNINC: 'ISLAND' }))
  sameScoring(cam, PUD, 'snohomish-public-utility-district-no-1-commissioner-district-1')
  assert.deepEqual(ownLocal(cam, 'island'), [FIREWORKS])
  // 112 2nd St, Langley: Langley Prop 1 and the South Whidbey port levy, no advisory vote.
  const lan = ballotFor(isl({ CONGDST: '2', LEGDST: '10', CITY: 'Langley', COUNTY_COUNCIL: '1', LIBDST: 'L', PORTDST: 'S WHIDBEY' }))
  assert.ok(!lan.contests.some((c) => c.slug === PUD))
  assert.deepEqual(ownLocal(lan, 'island'), [
    'island-city-of-langley-proposition-no-1',
    'island-port-district-of-south-whidbey-island-proposition-no-1',
  ])
  assert.equal(coverageAdvice(isl({})), null)
})

test('a Lewis ballot: Clark\'s research for CD 3 and LD 20, Thurston\'s for LD 19, PUD seat outside Centralia, Timberland levy by district', () => {
  const LEWIS = { id: 'lewis', fips: '53041', name: 'Lewis County' }
  const lew = (districts) => ({ coverageStatus: 'full_county', county: LEWIS, districts, missingLayers: [] })
  const PUD = 'lewis-public-utility-district-commissioner-district-1-commissioner-district-1'
  const TRL = 'lewis-timberland-regional-library-district-proposition-no-1'
  // Districts as the live District Adapter resolved them on 2026-10-08.
  // 351 NW North St, Chehalis: LD 20, the PUD seat, Timberland and the Chehalis TBD.
  const ch = ballotFor(lew({ CONGDST: '3', LEGDST: '20', CITY: 'Chehalis', COUNTY_COUNCIL: '2', PUDDST: '1', LIBDST: 'L' }))
  const cs = ch.contests.map((c) => c.slug)
  assert.equal(new Set(cs).size, cs.length)
  for (const slug of SUPREME_COURT) assert.ok(cs.includes(slug), slug)
  sameScoring(ch, 'lewis-congressional-district-3-u-s-representative', 'clark-congressional-district-3-u-s-representative')
  for (const pos of [1, 2])
    sameScoring(ch, `lewis-legislative-district-20-state-representative-pos-${pos}`, `clark-legislative-district-20-state-representative-pos-${pos}`)
  assert.ok(!ch.contests.some((c) => c.owner === 'clark' || c.owner === 'thurston'))
  assert.ok(cs.includes(PUD))
  assert.ok(cs.includes('lewis-lewis-county-commissioner-district-3-county-commissioner-district-3'))
  assert.deepEqual(ownLocal(ch, 'lewis'), [TRL, 'lewis-transportation-benefit-district-of-chehalis-proposition-no-1'])
  // 118 W Maple St, Centralia: outside the PUD.
  const ce = ballotFor(lew({ CONGDST: '3', LEGDST: '20', CITY: 'Centralia', COUNTY_COUNCIL: '1', FIRDST: 'RFPSA 1', LIBDST: 'L' }))
  assert.ok(!ce.contests.some((c) => c.slug === PUD))
  assert.deepEqual(ownLocal(ce, 'lewis'), [TRL])
  // 2152 Jackson Hwy, Chehalis: Fire District 6.
  const jh = ballotFor(lew({ CONGDST: '3', LEGDST: '20', COUNTY_COUNCIL: '2', FIRDST: '6', PUDDST: '1', LIBDST: 'L' }))
  assert.deepEqual(ownLocal(jh, 'lewis'), [TRL, 'lewis-lewis-county-fire-protection-district-no-6-proposition-no-1'])
  // 200 S Main St, Pe Ell: LD 19, outside Timberland.
  const pe = ballotFor(lew({ CONGDST: '3', LEGDST: '19', CITY: 'Pe Ell', COUNTY_COUNCIL: '2', FIRDST: '11', PUDDST: '1' }))
  for (const pos of [1, 2])
    sameScoring(pe, `lewis-legislative-district-19-state-representative-pos-${pos}`, `thurston-legislative-district-19-state-representative-pos-${pos}`)
  assert.ok(pe.contests.some((c) => c.slug === PUD))
  assert.deepEqual(ownLocal(pe, 'lewis'), [])
  assert.equal(coverageAdvice(lew({})), null)
})

test('a Franklin ballot: Benton\'s, Spokane\'s and Yakima\'s research for the shared seats, port and commissioner seats by district', () => {
  const FRANKLIN = { id: 'franklin', fips: '53021', name: 'Franklin County' }
  const fra = (districts) => ({ coverageStatus: 'full_county', county: FRANKLIN, districts, missingLayers: [] })
  const COM3 = 'franklin-franklin-county-commissioner-district-3-commissioner-district-3'
  const PORT = 'franklin-port-of-pasco-commissioner-district-3'
  const FPD3 = 'franklin-franklin-county-fire-protection-district-no-3-proposition-no-1'
  // Districts as the live District Adapter resolved them on 2026-10-08.
  // 525 N 3rd Ave, Pasco: CD 4, LD 14, COM2, PoP1.
  const pa = ballotFor(fra({ CONGDST: '4', LEGDST: '14', CITY: 'Pasco', COUNTY_COUNCIL: 'COM2', PORTDST: 'PoP1' }))
  const ps = pa.contests.map((c) => c.slug)
  assert.equal(new Set(ps).size, ps.length)
  for (const slug of SUPREME_COURT) assert.ok(ps.includes(slug), slug)
  sameScoring(pa, 'franklin-congressional-district-4-u-s-representative', 'benton-congressional-district-4-u-s-representative')
  for (const pos of [1, 2])
    sameScoring(pa, `franklin-legislative-district-14-state-representative-pos-${pos}`, `yakima-legislative-district-14-state-representative-pos-${pos}`)
  assert.ok(!pa.contests.some((c) => c.owner !== 'franklin' && c.owner !== 'statewide'))
  assert.ok(ps.includes('franklin-public-utility-district-no-1-of-franklin-county-commissioner-district-2'))
  assert.ok(!ps.includes(COM3) && !ps.includes(PORT))
  assert.deepEqual(ownLocal(pa, 'franklin'), [])
  // 5600 N Rd 68, Pasco (unincorporated): COM3, PoP3, Fire District 3.
  const rd68 = ballotFor(fra({ CONGDST: '4', LEGDST: '16', COUNTY_COUNCIL: 'COM3', PORTDST: 'PoP3', FIRDST: '3' }))
  assert.ok(rd68.contests.some((c) => c.slug === COM3))
  assert.ok(rd68.contests.some((c) => c.slug === PORT))
  for (const pos of [1, 2])
    sameScoring(rd68, `franklin-legislative-district-16-state-representative-pos-${pos}`, `benton-legislative-district-16-state-representative-pos-${pos}`)
  assert.deepEqual(ownLocal(rd68, 'franklin'), [FPD3])
  // 104 E Adams St, Connell: CD 5 (Spokane's research), PoP3, no fire district.
  const co = ballotFor(fra({ CONGDST: '5', LEGDST: '16', CITY: 'Connell', COUNTY_COUNCIL: 'COM2', PORTDST: 'PoP3' }))
  sameScoring(co, 'franklin-congressional-district-5-u-s-representative', 'spokane-congressional-district-5-u-s-representative')
  assert.ok(co.contests.some((c) => c.slug === PORT))
  assert.deepEqual(ownLocal(co, 'franklin'), [])
  // 2108 N Rd 84, Pasco: LD 8 (Benton's research), PoP2.
  const r84 = ballotFor(fra({ CONGDST: '4', LEGDST: '8', CITY: 'Pasco', COUNTY_COUNCIL: 'COM1', PORTDST: 'PoP2' }))
  sameScoring(r84, 'franklin-legislative-district-8-state-senator', 'benton-legislative-district-8-state-senator')
  assert.ok(!r84.contests.some((c) => c.slug === PORT))
  assert.equal(coverageAdvice(fra({})), null)
})

test('a Chelan ballot: King\'s research for CD 8 and LD 12, Wenatchee SD 246 and Cashmere Prop 1 by district', () => {
  const CHELAN = { id: 'chelan', fips: '53007', name: 'Chelan County' }
  const che = (districts) => ({ coverageStatus: 'full_county', county: CHELAN, districts, missingLayers: [] })
  const SD246 = 'chelan-wenatchee-school-district-no-246-proposition-no-1'
  // Districts as the live District Adapter resolved them on 2026-10-08.
  // 316 Washington St, Wenatchee: district 1, Wenatchee SD 246.
  const we = ballotFor(che({ CONGDST: '8', LEGDST: '12', CITY: 'Wenatchee', COUNTY_COUNCIL: '1', SCHDST: '246' }))
  const ws = we.contests.map((c) => c.slug)
  assert.equal(new Set(ws).size, ws.length)
  for (const slug of SUPREME_COURT) assert.ok(ws.includes(slug), slug)
  sameScoring(we, 'chelan-congressional-district-8-u-s-representative', 'congressional-district-8-united-states-representative')
  for (const pos of [1, 2])
    sameScoring(we, `chelan-legislative-district-12-state-representative-pos-${pos}`, `state-representative-position-no-${pos}-legislative-district-no-12`)
  assert.ok(!we.contests.some((c) => c.owner === 'king'))
  // The commissioner and PUD seats are elected countywide in the general.
  assert.ok(ws.includes('chelan-chelan-county-commissioner-district-2-commissioner-district-no-2'))
  assert.ok(ws.includes('chelan-public-utility-district-no-1-of-chelan-county-commissioner-district-1'))
  assert.deepEqual(ownLocal(we, 'chelan'), [SD246])
  // 101 Woodring St, Cashmere: Cashmere SD 222, the city's levy.
  const ca = ballotFor(che({ CONGDST: '8', LEGDST: '12', CITY: 'Cashmere', COUNTY_COUNCIL: '2', SCHDST: '222' }))
  assert.deepEqual(ownLocal(ca, 'chelan'), ['chelan-city-of-cashmere-proposition-no-1'])
  // 700 US Hwy 2, Leavenworth: no local measure.
  const le = ballotFor(che({ CONGDST: '8', LEGDST: '12', CITY: 'Leavenworth', COUNTY_COUNCIL: '2', SCHDST: '228' }))
  assert.deepEqual(le.measures.map((m) => m.slug), STATE_MEASURES)
  assert.equal(coverageAdvice(che({})), null)
})

test('a Clallam ballot: District Court by district, the PUD seat outside Port Angeles, school and fire measures by district', () => {
  const CLALLAM = { id: 'clallam', fips: '53009', name: 'Clallam County' }
  const cll = (districts) => ({ coverageStatus: 'full_county', county: CLALLAM, districts, missingLayers: [] })
  const PUD = 'clallam-public-utility-district-no-1-of-clallam-county-commissioner-district-no-2'
  const DC1 = 'clallam-clallam-county-district-court-1-judge'
  const DC2 = 'clallam-clallam-county-district-court-2-judge'
  const CHARTER = [1, 2, 3].map((n) => `clallam-clallam-county-proposed-charter-amendment-no-${n}`)
  // Districts as the live District Adapter resolved them on 2026-10-08.
  // 223 E 4th St, Port Angeles: District Court 1, outside the PUD.
  const pa = ballotFor(cll({ CONGDST: '6', LEGDST: '24', CITY: 'Port Angeles', COUNTY_COUNCIL: '2', DISTCRT: '1', SCHDST: '121' }))
  const ps = pa.contests.map((c) => c.slug)
  assert.equal(new Set(ps).size, ps.length)
  for (const slug of SUPREME_COURT) assert.ok(ps.includes(slug), slug)
  sameScoring(pa, 'clallam-congressional-district-6-u-s-representative', 'pierce-congressional-district-6-u-s-representative')
  assert.ok(ps.includes(DC1) && !ps.includes(DC2) && !ps.includes(PUD))
  assert.ok(ps.includes('clallam-legislative-district-24-state-representative-pos-1'))
  assert.deepEqual(ownLocal(pa, 'clallam'), CHARTER)
  // 500 E Division St, Forks: District Court 2, the PUD seat, QVSD 402, Fire District 1.
  const fo = ballotFor(cll({
    CONGDST: '6', LEGDST: '24', CITY: 'Forks', COUNTY_COUNCIL: '3', PUDDST: '3', FIRDST: '1', DISTCRT: '2', SCHDST: '402', PUDALL: '1',
  }))
  const fs = fo.contests.map((c) => c.slug)
  assert.ok(fs.includes(DC2) && !fs.includes(DC1) && fs.includes(PUD))
  assert.deepEqual(ownLocal(fo, 'clallam'), [
    ...CHARTER,
    'clallam-quillayute-valley-school-district-no-402-proposition-no-1',
    'clallam-clallam-county-fire-protection-district-no-1-proposition-no-1',
  ])
  // 3851 S Mount Angeles Rd, Port Angeles (outside the city): Fire District 2 and the PUD seat.
  const ma = ballotFor(cll({ CONGDST: '6', LEGDST: '24', COUNTY_COUNCIL: '2', PUDDST: '3', FIRDST: '2', DISTCRT: '1', SCHDST: '121', PUDALL: '1' }))
  assert.ok(ma.contests.some((c) => c.slug === PUD))
  assert.deepEqual(ownLocal(ma, 'clallam'), [...CHARTER, 'clallam-clallam-county-fire-protection-district-no-2-proposition-no-1'])
  // 7764 La Push Rd: Fire District 6.
  const lp = ballotFor(cll({ CONGDST: '6', LEGDST: '24', COUNTY_COUNCIL: '3', PUDDST: '3', FIRDST: '6', DISTCRT: '2', SCHDST: '402', PUDALL: '1' }))
  assert.deepEqual(ownLocal(lp, 'clallam'), [
    ...CHARTER,
    'clallam-quillayute-valley-school-district-no-402-proposition-no-1',
    'clallam-clallam-county-fire-protection-district-no-6-proposition-no-1',
  ])
  assert.equal(coverageAdvice(cll({})), null)
})

test('a Grays Harbor ballot: Clallam\'s research for LD 24, Thurston\'s for LD 19, Timberland outside Ocean Shores', () => {
  const GRAYS_HARBOR = { id: 'grays-harbor', fips: '53027', name: 'Grays Harbor County' }
  const gh = (districts) => ({ coverageStatus: 'full_county', county: GRAYS_HARBOR, districts, missingLayers: [] })
  const TRL = 'grays-harbor-timberland-regional-library-district-proposition-no-1'
  // Districts as the live District Adapter resolved them on 2026-10-08.
  // 200 W Market St, Aberdeen: LD 19, Timberland only.
  const ab = ballotFor(gh({ CONGDST: '6', LEGDST: '19', CITY: 'Aberdeen', LIBDST: 'L', SCHDST: '5' }))
  const as = ab.contests.map((c) => c.slug)
  assert.equal(new Set(as).size, as.length)
  for (const slug of SUPREME_COURT) assert.ok(as.includes(slug), slug)
  sameScoring(ab, 'grays-harbor-congressional-district-6-u-s-representative', 'pierce-congressional-district-6-u-s-representative')
  for (const pos of [1, 2])
    sameScoring(ab, `grays-harbor-legislative-district-19-state-representative-pos-${pos}`, `thurston-legislative-district-19-state-representative-pos-${pos}`)
  assert.ok(!ab.contests.some((c) => c.owner !== 'grays-harbor' && c.owner !== 'statewide'))
  assert.deepEqual(ownLocal(ab, 'grays-harbor'), [TRL])
  // 100 S 3rd St, McCleary: McCleary SD 65.
  const mc = ballotFor(gh({ CONGDST: '6', LEGDST: '19', CITY: 'McCleary', LIBDST: 'L', SCHDST: '65' }))
  assert.deepEqual(ownLocal(mc, 'grays-harbor'), [TRL, 'grays-harbor-mccleary-school-district-no-65-proposition-no-1'])
  // 110 Main St, Oakville: Fire District 1.
  const ok = ballotFor(gh({ CONGDST: '6', LEGDST: '19', CITY: 'Oakville', FIRDST: '1', LIBDST: 'L', SCHDST: '400' }))
  assert.deepEqual(ownLocal(ok, 'grays-harbor'), [TRL, 'grays-harbor-grays-harbor-county-fire-protection-district-no-1-proposition-no-1'])
  // 200 N Main St, Montesano: LD 24 (Clallam's research), Montesano Prop 1.
  const mo = ballotFor(gh({ CONGDST: '6', LEGDST: '24', CITY: 'Montesano', LIBDST: 'L', SCHDST: '66' }))
  for (const pos of [1, 2])
    sameScoring(mo, `grays-harbor-legislative-district-24-state-representative-pos-${pos}`, `clallam-legislative-district-24-state-representative-pos-${pos}`)
  assert.deepEqual(ownLocal(mo, 'grays-harbor'), [TRL, 'grays-harbor-city-of-montesano-proposition-no-1'])
  // 585 Point Brown Ave NW, Ocean Shores: outside Timberland.
  const os = ballotFor(gh({ CONGDST: '6', LEGDST: '24', CITY: 'Ocean Shores', SCHDST: '64' }))
  assert.deepEqual(os.measures.map((m) => m.slug), STATE_MEASURES)
  assert.equal(coverageAdvice(gh({})), null)
})

test('a Mason ballot: Pierce\'s research for CD 6, Kitsap\'s for LD 35, PUD No. 1 or No. 3, school measures by district', () => {
  const MASON = { id: 'mason', fips: '53045', name: 'Mason County' }
  const ma = (districts) => ({ coverageStatus: 'full_county', county: MASON, districts, missingLayers: [] })
  const TRL = 'mason-timberland-regional-library-district-proposition-no-1'
  const PUD1 = 'mason-public-utility-district-no-1-of-mason-county-commissioner-district-2'
  const PUD3 = 'mason-public-utility-district-no-3-of-mason-county-commissioner-district-2'
  // Districts as the live District Adapter resolved them on 2026-10-08.
  // 525 W Cota St, Shelton: PUD 3, Shelton SD 309 (no measure), the city's TBD.
  const sh = ballotFor(ma({ CONGDST: '6', LEGDST: '35', CITY: 'Shelton', COUNTY_COUNCIL: '3', PUDDST: '3', SCHDST: '309' }))
  const ss = sh.contests.map((c) => c.slug)
  assert.equal(new Set(ss).size, ss.length)
  for (const slug of SUPREME_COURT) assert.ok(ss.includes(slug), slug)
  sameScoring(sh, 'mason-congressional-district-6-u-s-representative', 'pierce-congressional-district-6-u-s-representative')
  sameScoring(sh, 'mason-legislative-district-35-state-senator', 'kitsap-legislative-district-35-state-senator')
  for (const pos of [1, 2])
    sameScoring(sh, `mason-legislative-district-35-state-representative-pos-${pos}`, `kitsap-legislative-district-35-state-representative-pos-${pos}`)
  assert.ok(!sh.contests.some((c) => c.owner !== 'mason' && c.owner !== 'statewide'))
  assert.ok(ss.includes(PUD3) && !ss.includes(PUD1))
  // The commissioner seat is elected countywide in the general.
  assert.ok(ss.includes('mason-mason-county-commissioner-district-3-county-commissioner-district-no-3'))
  assert.deepEqual(ownLocal(sh, 'mason'), [TRL, 'mason-city-of-shelton-proposition-no-1'])
  // 24151 N US Hwy 101, Hoodsport: PUD 1, Hood Canal SD 404.
  const ho = ballotFor(ma({ CONGDST: '6', LEGDST: '35', COUNTY_COUNCIL: '2', FIRDST: '18', PUDDST: '1', SCHDST: '404' }))
  const hs = ho.contests.map((c) => c.slug)
  assert.ok(hs.includes(PUD1) && !hs.includes(PUD3))
  assert.deepEqual(ownLocal(ho, 'mason'), [TRL])
  // 23850 NE State Route 3, Belfair: PUD 3, North Mason SD 403.
  const be = ballotFor(ma({ CONGDST: '6', LEGDST: '35', COUNTY_COUNCIL: '1', FIRDST: 'NMRFA', PUDDST: '3', SCHDST: '403' }))
  assert.ok(be.contests.some((c) => c.slug === PUD3))
  assert.deepEqual(ownLocal(be, 'mason'), [TRL])
  // 281 W Bonnieview Dr, McCleary (Mason side): McCleary SD 65, Mason's copy only.
  const mc = ballotFor(ma({ CONGDST: '6', LEGDST: '35', COUNTY_COUNCIL: '2', FIRDST: '13', PUDDST: '3', SCHDST: '65' }))
  assert.deepEqual(mc.measures.filter((m) => m.slug.includes('mccleary')).map((m) => m.slug),
    ['mason-mccleary-school-district-no-65-proposition-no-1'])
  assert.deepEqual(ownLocal(mc, 'mason'), [TRL, 'mason-mccleary-school-district-no-65-proposition-no-1'])
  // 112 E Spencer Lake Rd: Pioneer SD 402; 161 SE Collier Rd: Southside SD 42.
  const pi = ballotFor(ma({ CONGDST: '6', LEGDST: '35', COUNTY_COUNCIL: '3', FIRDST: '5', PUDDST: '3', SCHDST: '402' }))
  assert.deepEqual(ownLocal(pi, 'mason'), [TRL, 'mason-pioneer-school-district-no-402-proposition-no-1'])
  const so = ballotFor(ma({ CONGDST: '6', LEGDST: '35', COUNTY_COUNCIL: '3', FIRDST: '4', PUDDST: '3', SCHDST: '42' }))
  assert.deepEqual(ownLocal(so, 'mason'), [TRL, 'mason-southside-school-district-no-42-proposition-no-1'])
  assert.equal(coverageAdvice(ma({})), null)
})

test('a Walla Walla ballot: Spokane\'s research for CD 5, Benton\'s for LD 16, levies by district', () => {
  const WALLA_WALLA = { id: 'walla-walla', fips: '53071', name: 'Walla Walla County' }
  const ww = (districts) => ({ coverageStatus: 'full_county', county: WALLA_WALLA, districts, missingLayers: [] })
  const DIXIE = 'walla-walla-dixie-school-district-no-101-proposition-1'
  const PRESCOTT = 'walla-walla-prescott-joint-park-and-recreation-district-proposition-no-1'
  // Districts as the live District Adapter resolved them on 2026-10-08.
  // 108 S D St, Prescott: Prescott SD 402, park district PRES.
  const pr = ballotFor(ww({ CONGDST: '5', LEGDST: '16', CITY: 'Prescott', COUNTY_COUNCIL: '2', SCHDST: '402', PARKDST: 'PRES' }))
  const ps = pr.contests.map((c) => c.slug)
  assert.equal(new Set(ps).size, ps.length)
  assert.equal(ps.length, 14 + SUPREME_COURT.length)
  for (const slug of SUPREME_COURT) assert.ok(ps.includes(slug), slug)
  sameScoring(pr, 'walla-walla-congressional-district-5-u-s-representative', 'spokane-congressional-district-5-u-s-representative')
  for (const pos of [1, 2])
    sameScoring(pr, `walla-walla-legislative-district-16-state-representative-pos-${pos}`, `benton-legislative-district-16-state-representative-pos-${pos}`)
  assert.ok(!pr.contests.some((c) => c.owner !== 'walla-walla' && c.owner !== 'statewide'))
  // Commissioner District 3 is elected countywide in the general.
  assert.ok(ps.includes('walla-walla-walla-walla-county-commissioner-district-3-county-commissioner-district-3'))
  assert.deepEqual(ownLocal(pr, 'walla-walla'), [PRESCOTT])
  // 315 W Main St, Walla Walla (SD 140) and 106 Preston Ave, Waitsburg (SD
  // 401, park district WAIT): no local measure.
  const wa = ballotFor(ww({ CONGDST: '5', LEGDST: '16', CITY: 'Walla Walla', COUNTY_COUNCIL: '1', SCHDST: '140' }))
  assert.equal(wa.contests.length, 14 + SUPREME_COURT.length)
  assert.deepEqual(ownLocal(wa, 'walla-walla'), [])
  const wb = ballotFor(ww({ CONGDST: '5', LEGDST: '16', CITY: 'Waitsburg', COUNTY_COUNCIL: '2', SCHDST: '401', PARKDST: 'WAIT' }))
  assert.deepEqual(ownLocal(wb, 'walla-walla'), [])
  // Dixie (interior point -118.153, 46.140): SD 101.
  const dx = ballotFor(ww({ CONGDST: '5', LEGDST: '16', COUNTY_COUNCIL: '2', SCHDST: '101' }))
  assert.deepEqual(ownLocal(dx, 'walla-walla'), [DIXIE])
  assert.equal(coverageAdvice(ww({})), null)
})

test('a Stevens ballot: Spokane\'s research for CD 5, LD 7 and the PUD seat, library, fire and school measures by district', () => {
  const STEVENS = { id: 'stevens', fips: '53065', name: 'Stevens County' }
  const st = (districts) => ({ coverageStatus: 'full_county', county: STEVENS, districts, missingLayers: [] })
  const LIBRARY = 'stevens-stevens-county-rural-library-district-proposition-no-2'
  const FD10 = 'stevens-stevens-county-fire-protection-district-no-10-proposition-no-1'
  const NMF = [1, 2].map((n) => `stevens-nine-mile-falls-school-district-no-325-179-proposition-no-${n}`)
  const PUD = 'stevens-public-utility-district-no-1-of-stevens-county-commissioner-district-2-pud-commissioner'
  // Districts as the live District Adapter resolved them on 2026-10-08.
  // 6015 State Route 291, Nine Mile Falls: FD 1, library L, SD 179J.
  const nm = ballotFor(st({ CONGDST: '5', LEGDST: '7', COUNTY_COUNCIL: '1', FIRDST: '1', LIBDST: 'L', SCHDST: '179J' }))
  const ns = nm.contests.map((c) => c.slug)
  assert.equal(new Set(ns).size, ns.length)
  assert.equal(ns.length, 16 + SUPREME_COURT.length)
  for (const slug of SUPREME_COURT) assert.ok(ns.includes(slug), slug)
  sameScoring(nm, 'stevens-congressional-district-5-u-s-representative', 'spokane-congressional-district-5-u-s-representative')
  sameScoring(nm, 'stevens-legislative-district-7-state-senator', 'spokane-legislative-district-7-state-senator')
  for (const pos of [1, 2])
    sameScoring(nm, `stevens-legislative-district-7-state-representative-pos-${pos}`, `spokane-legislative-district-7-state-representative-pos-${pos}`)
  sameScoring(nm, PUD, 'spokane-public-utility-district-no-1-of-stevens-county-commissioner-district-2-pud-commissioner')
  assert.ok(!nm.contests.some((c) => c.owner !== 'stevens' && c.owner !== 'statewide'))
  assert.deepEqual(ownLocal(nm, 'stevens'), [LIBRARY, ...NMF])
  // 2785 Aladdin Rd, Colville: FD 10, library L, SD 211.
  const al = ballotFor(st({ CONGDST: '5', LEGDST: '7', COUNTY_COUNCIL: '3', FIRDST: '10', LIBDST: 'L', SCHDST: '211' }))
  assert.deepEqual(ownLocal(al, 'stevens'), [LIBRARY, FD10])
  // 215 S Oak St, Colville: outside the library district; the PUD seat is
  // still on the ballot (PUD No. 1 covers the whole county).
  const co = ballotFor(st({ CONGDST: '5', LEGDST: '7', CITY: 'Colville', COUNTY_COUNCIL: '3', SCHDST: '115' }))
  assert.deepEqual(ownLocal(co, 'stevens'), [])
  assert.ok(co.contests.some((c) => c.slug === PUD))
  assert.equal(coverageAdvice(st({})), null)
})

test('a Whitman ballot: Spokane\'s research for CD 5 and LD 9, town, library, park, cemetery and fire measures by district', () => {
  const WHITMAN = { id: 'whitman', fips: '53075', name: 'Whitman County' }
  const wh = (districts) => ({ coverageStatus: 'full_county', county: WHITMAN, districts, missingLayers: [] })
  const LIBRARY = 'whitman-whitman-county-rural-library-district-proposition-no-1'
  const CHENEY = [1, 2].map((n) => `whitman-cheney-school-district-no-360-proposition-no-${n}`)
  // Districts as the live District Adapter resolved them on 2026-10-08.
  // 325 SE Paradise St, Pullman: no local measure.
  const pu = ballotFor(wh({ CONGDST: '5', LEGDST: '9', CITY: 'Pullman', COUNTY_COUNCIL: '2', SCHDST: '267' }))
  const ps = pu.contests.map((c) => c.slug)
  assert.equal(new Set(ps).size, ps.length)
  assert.equal(ps.length, 13 + SUPREME_COURT.length)
  for (const slug of SUPREME_COURT) assert.ok(ps.includes(slug), slug)
  sameScoring(pu, 'whitman-congressional-district-5-u-s-representative', 'spokane-congressional-district-5-u-s-representative')
  for (const pos of [1, 2])
    sameScoring(pu, `whitman-legislative-district-9-state-representative-pos-${pos}`, `spokane-legislative-district-9-state-representative-pos-${pos}`)
  assert.ok(!pu.contests.some((c) => c.owner !== 'whitman' && c.owner !== 'statewide'))
  // Commissioner District 3 is elected countywide in the general.
  assert.ok(ps.includes('whitman-whitman-county-commissioner-district-3-commissioner-3'))
  assert.deepEqual(ownLocal(pu, 'whitman'), [])
  // 101 Steptoe Ave, Oakesdale: library L, Park District 4, Cemetery District 1.
  const oa = ballotFor(wh({
    CONGDST: '5', LEGDST: '9', CITY: 'Oakesdale', COUNTY_COUNCIL: '1', PARKDST: '4', CEMDST: '1', LIBDST: 'L', SCHDST: '324',
  }))
  assert.deepEqual(ownLocal(oa, 'whitman'), [
    LIBRARY,
    'whitman-town-of-oakesdale-proposition-no-1',
    'whitman-town-of-oakesdale-proposition-no-2',
    'whitman-oakesdale-park-recreation-district-no-4-proposition-no-1',
    'whitman-oakesdale-cemetery-district-no-1-proposition-no-1',
  ])
  // 110 S Montgomery St, Uniontown: FD 14, no library levy.
  const un = ballotFor(wh({ CONGDST: '5', LEGDST: '9', CITY: 'Uniontown', COUNTY_COUNCIL: '2', FIRDST: '14', SCHDST: '306' }))
  assert.deepEqual(ownLocal(un, 'whitman'), [
    'whitman-town-of-uniontown-proposition-no-1',
    'whitman-whitman-county-fire-protection-district-no-14-proposition-no-1',
  ])
  // 200 S Mill St, Colfax: the library levy only (Cemetery District 6 has none).
  const co = ballotFor(wh({ CONGDST: '5', LEGDST: '9', CITY: 'Colfax', COUNTY_COUNCIL: '3', CEMDST: '6', LIBDST: 'L', SCHDST: '300' }))
  assert.deepEqual(ownLocal(co, 'whitman'), [LIBRARY])
  // Interior point (-117.70, 47.24): Cheney SD's Whitman portion.
  const ch = ballotFor(wh({ CONGDST: '5', LEGDST: '9', COUNTY_COUNCIL: '1', FIRDST: '5', LIBDST: 'L', SCHDST: '316' }))
  assert.deepEqual(ownLocal(ch, 'whitman'), [LIBRARY, ...CHENEY])
  assert.equal(coverageAdvice(wh({})), null)
})

test('a Douglas ballot: Benton\'s, Spokane\'s and Grant\'s research for the shared races, Rimrock only inside the proposed district', () => {
  const DOUGLAS = { id: 'douglas', fips: '53017', name: 'Douglas County' }
  const dg = (districts) => ({ coverageStatus: 'full_county', county: DOUGLAS, districts, missingLayers: [] })
  const RIMROCK = 'douglas-proposed-rimrock-meadows-fire-protection-district-no-9'
  const RIMROCK_SEATS = [1, 2, 3].map((n) => `${RIMROCK}-commissioner-no-${n}`)
  const HOSP2 = 'douglas-douglas-county-public-hospital-district-no-2-proposition-no-1'
  const CEM2 = 'douglas-douglas-county-cemetery-district-no-2-proposition-no-1'
  // Districts as the live District Adapter resolved them on 2026-10-08.
  // 100 Eastmont Ave, East Wenatchee: Eastmont SD 206.
  const ew = ballotFor(dg({ CONGDST: '4', LEGDST: '7', CITY: 'East Wenatchee', FIRDST: '2', SCHDST: '206', PROPFIRDST: '002' }))
  const es = ew.contests.map((c) => c.slug)
  assert.equal(new Set(es).size, es.length)
  assert.equal(es.length, 15 + SUPREME_COURT.length)
  for (const slug of SUPREME_COURT) assert.ok(es.includes(slug), slug)
  sameScoring(ew, 'douglas-congressional-district-4-u-s-representative', 'benton-congressional-district-4-u-s-representative')
  sameScoring(ew, 'douglas-legislative-district-7-state-senator', 'spokane-legislative-district-7-state-senator')
  assert.ok(!ew.contests.some((c) => c.owner !== 'douglas' && c.owner !== 'statewide'))
  assert.ok(!es.some((s) => s.startsWith(RIMROCK)))
  assert.deepEqual(ownLocal(ew, 'douglas'), ['douglas-eastmont-school-district-no-206-proposition-no-1'])
  // 213 S Chelan Ave, Waterville: Hospital District 2, Cemetery District 2.
  const wv = ballotFor(dg({ CONGDST: '4', LEGDST: '7', CITY: 'Waterville', HOSPDST: '2', SCHDST: '209', CEMDST: '2', PROPFIRDST: '000' }))
  assert.deepEqual(ownLocal(wv, 'douglas'), [HOSP2, CEM2])
  // 1206 Columbia Ave, Bridgeport: Three Rivers Hospital (District 1) bonds.
  const bp = ballotFor(dg({ CONGDST: '4', LEGDST: '7', CITY: 'Bridgeport', HOSPDST: '1', SCHDST: '75', PROPFIRDST: 'BPR' }))
  assert.deepEqual(ownLocal(bp, 'douglas'),
    ['douglas-public-hospital-district-no-1-okanogan-and-douglas-counties-three-rivers-hospital-proposition-no-1'])
  // 1005 Ashcroft Dr, Ephrata (Rimrock Meadows): LD 13, formation and three seats.
  const rr = ballotFor(dg({ CONGDST: '4', LEGDST: '13', SCHDST: '209', PROPFIRDST: '009' }))
  const rs = rr.contests.map((c) => c.slug)
  assert.equal(rs.length, 18 + SUPREME_COURT.length)
  for (const slug of RIMROCK_SEATS) assert.ok(rs.includes(slug), slug)
  sameScoring(rr, 'douglas-legislative-district-13-state-senator', 'grant-legislative-district-13-state-senator')
  for (const pos of [1, 2])
    sameScoring(rr, `douglas-legislative-district-13-state-representative-pos-${pos}`, `grant-legislative-district-13-state-representative-pos-${pos}`)
  assert.ok(!rs.some((s) => s.includes('legislative-district-7')))
  assert.deepEqual(ownLocal(rr, 'douglas'), [`${RIMROCK}-proposition-no-1`])
  // 448 Belmont Pl, Ephrata: the county layer's existing district '001', no Rimrock items.
  const bl = ballotFor(dg({ CONGDST: '4', LEGDST: '7', FIRDST: '1', HOSPDST: '2', SCHDST: '209', CEMDST: '2', PROPFIRDST: '001' }))
  assert.ok(!bl.contests.some((c) => c.slug.startsWith(RIMROCK)))
  assert.deepEqual(ownLocal(bl, 'douglas'), [HOSP2, CEM2])
  // CD 8 (King's research) reaches one north East Wenatchee precinct.
  const cd8 = ballotFor(dg({ CONGDST: '8', LEGDST: '7', SCHDST: '206' }))
  const owner = data.contests.find((c) => c.slug === 'congressional-district-8-united-states-representative')
  const shipped = cd8.contests.find((c) => c.slug === 'douglas-congressional-district-8-u-s-representative')
  assert.deepEqual(shipped.candidates.map((c) => [c.slug, c.scores]), owner.candidates.map((c) => [c.slug, c.scores]))
  assert.equal(coverageAdvice(dg({})), null)
})

test('an Okanogan ballot: Benton\'s and Spokane\'s research for the shared races, EMS levies by district or town, no PUD seat', () => {
  const OKANOGAN = { id: 'okanogan', fips: '53047', name: 'Okanogan County' }
  const ok = (districts) => ({ coverageStatus: 'partial_county', county: OKANOGAN, districts, missingLayers: [] })
  const THREE_RIVERS = 'okanogan-public-hospital-district-no-1-okanogan-and-douglas-counties-proposition-no-1'
  // Districts as the live District Adapter resolved them on 2026-10-08.
  // 50 Lost River Rd, Mazama: Methow Valley EMS District, Three Rivers Hospital.
  const mz = ballotFor(ok({ CONGDST: '4', LEGDST: '7', FIRDST: '6', HOSPDST: '1J', EMSDST: 'MV' }))
  const ms = mz.contests.map((c) => c.slug)
  assert.equal(new Set(ms).size, ms.length)
  assert.equal(ms.length, 16 + SUPREME_COURT.length)
  for (const slug of SUPREME_COURT) assert.ok(ms.includes(slug), slug)
  assert.deepEqual(mz.measures.slice(0, 3).map((m) => m.slug), STATE_MEASURES)
  sameScoring(mz, 'okanogan-congressional-district-4-u-s-representative', 'benton-congressional-district-4-u-s-representative')
  sameScoring(mz, 'okanogan-legislative-district-7-state-senator', 'spokane-legislative-district-7-state-senator')
  for (const pos of [1, 2])
    sameScoring(mz, `okanogan-legislative-district-7-state-representative-pos-${pos}`, `spokane-legislative-district-7-state-representative-pos-${pos}`)
  assert.ok(!mz.contests.some((c) => c.owner !== 'okanogan' && c.owner !== 'statewide'))
  // Both PUD seats stay hidden: PUDDST is unresolvable (data-consistency.test.js).
  assert.ok(!ms.some((s) => s.includes('public-utility-district')), ms.join())
  assert.ok(data.contests.some((c) => c.owner === 'okanogan' && c.scope.layer === 'PUDDST'))
  assert.deepEqual(ownLocal(mz, 'okanogan'),
    [THREE_RIVERS, 'okanogan-methow-valley-emergency-medical-services-district-proposition-no-1'])
  // 206 Riverside Ave, Winthrop and 118 S Glover St, Twisp: each town's own EMS levy.
  const wi = ballotFor(ok({ CONGDST: '4', LEGDST: '7', CITY: 'Winthrop', FIRDST: '6', HOSPDST: '1J', EMSDST: 'WC' }))
  assert.deepEqual(ownLocal(wi, 'okanogan'), [THREE_RIVERS, 'okanogan-town-of-winthrop-proposition-no-1'])
  const tw = ballotFor(ok({ CONGDST: '4', LEGDST: '7', CITY: 'Twisp', FIRDST: '6', HOSPDST: '1J', EMSDST: 'TC' }))
  assert.deepEqual(ownLocal(tw, 'okanogan'), [THREE_RIVERS, 'okanogan-town-of-twisp-proposition-no-1'])
  // 415 Hospital Way, Brewster.
  const br = ballotFor(ok({ CONGDST: '4', LEGDST: '7', CITY: 'Brewster', HOSPDST: '1J', EMSDST: 'BC' }))
  assert.deepEqual(ownLocal(br, 'okanogan'), [THREE_RIVERS, 'okanogan-city-of-brewster-proposition-no-1'])
  // 2 S Ash St, Omak: county races only.
  const om = ballotFor(ok({ CONGDST: '4', LEGDST: '7', CITY: 'Omak', HOSPDST: '3' }))
  assert.deepEqual(ownLocal(om, 'okanogan'), [])
  assert.equal(om.contests.length, 16 + SUPREME_COURT.length)
  // 38 Swanson Mill Rd, Oroville: Fire District 1's lid lift.
  const or = ballotFor(ok({ CONGDST: '4', LEGDST: '7', FIRDST: '1', HOSPDST: '4', EMSDST: 'OR' }))
  assert.deepEqual(ownLocal(or, 'okanogan'), ['okanogan-okanogan-county-fire-protection-district-no-1-proposition-no-1'])
  // The partial package tells every Okanogan voter the ballot may be incomplete.
  assert.equal(coverageAdvice(ok({})), 'degraded')
})

test('a Jefferson ballot: Pierce\'s and Clallam\'s research for the shared races, the West End measures only in the West End', () => {
  const JEFFERSON = { id: 'jefferson', fips: '53031', name: 'Jefferson County' }
  const jf = (districts) => ({ coverageStatus: 'full_county', county: JEFFERSON, districts, missingLayers: [] })
  const QVSD = 'jefferson-quillayute-valley-school-district-no-402-proposition-no-1'
  const CCFD1 = 'jefferson-clallam-county-fire-protection-district-no-1-proposition-no-1'
  // Districts as the live District Adapter resolved them on 2026-10-08.
  // 1820 Jefferson St, Port Townsend: county races, no local measure.
  const pt = ballotFor(jf({ CONGDST: '6', LEGDST: '24', CITY: 'Port Townsend', COUNTY_COUNCIL: '1', FIRDST: '1', SCHDST: '50' }))
  const ps = pt.contests.map((c) => c.slug)
  assert.equal(new Set(ps).size, ps.length)
  assert.equal(ps.length, 13 + SUPREME_COURT.length)
  for (const slug of SUPREME_COURT) assert.ok(ps.includes(slug), slug)
  assert.deepEqual(pt.measures.map((m) => m.slug), STATE_MEASURES)
  sameScoring(pt, 'jefferson-congressional-district-6-u-s-representative', 'pierce-congressional-district-6-u-s-representative')
  for (const pos of [1, 2])
    sameScoring(pt, `jefferson-legislative-district-24-state-representative-pos-${pos}`, `clallam-legislative-district-24-state-representative-pos-${pos}`)
  assert.ok(!pt.contests.some((c) => c.owner !== 'jefferson' && c.owner !== 'statewide'))
  // Commissioner District 3 and the PUD seat are elected county-wide.
  assert.ok(ps.includes('jefferson-jefferson-county-commissioner-district-3-district-3'))
  assert.ok(ps.includes('jefferson-public-utility-district-no-1-of-jefferson-county-commissioner-district-2'))
  // 1993 Dowans Creek Rd, Forks (Jefferson side): both West End measures,
  // Jefferson's copies, not Clallam's.
  const dc = ballotFor(jf({ CONGDST: '6', LEGDST: '24', COUNTY_COUNCIL: '3', FIRDST: '9', SCHDST: '402' }))
  assert.deepEqual(ownLocal(dc, 'jefferson'), [QVSD, CCFD1])
  assert.deepEqual(ownLocal(dc, 'clallam'), [])
  // 18113 Upper Hoh Rd, Forks: the bond only.
  const uh = ballotFor(jf({ CONGDST: '6', LEGDST: '24', COUNTY_COUNCIL: '3', SCHDST: '402' }))
  assert.deepEqual(ownLocal(uh, 'jefferson'), [QVSD])
  // 620 Cedar Ave, Port Hadlock: East Jefferson Fire Rescue is FIRDST '1', not Clallam's district.
  const ph = ballotFor(jf({ CONGDST: '6', LEGDST: '24', COUNTY_COUNCIL: '2', FIRDST: '1', SCHDST: '49' }))
  assert.deepEqual(ownLocal(ph, 'jefferson'), [])
  assert.equal(coverageAdvice(jf({})), null)
})

test('a Kittitas ballot: King\'s and Grant\'s research for the shared races, one District Court seat per district', () => {
  const KITTITAS = { id: 'kittitas', fips: '53037', name: 'Kittitas County' }
  const kt = (districts) => ({ coverageStatus: 'full_county', county: KITTITAS, districts, missingLayers: [] })
  const LOWER = 'kittitas-lower-kittitas-county-district-court-district-court-judge'
  const UPPER = 'kittitas-upper-kittitas-county-district-court-district-court-judge'
  // Districts as the live District Adapter resolved them on 2026-10-08.
  // 205 W 5th Ave, Ellensburg: Lower District Court.
  const el = ballotFor(kt({ CONGDST: '8', LEGDST: '13', CITY: 'Ellensburg', COUNTY_COUNCIL: '3', FIRDST: '2', DISTCRT: 'Lower District Court' }))
  const es = el.contests.map((c) => c.slug)
  assert.equal(new Set(es).size, es.length)
  assert.equal(es.length, 15 + SUPREME_COURT.length)
  for (const slug of SUPREME_COURT) assert.ok(es.includes(slug), slug)
  assert.ok(es.includes(LOWER))
  assert.ok(!es.includes(UPPER))
  assert.deepEqual(el.measures.map((m) => m.slug), STATE_MEASURES)
  sameScoring(el, 'kittitas-congressional-district-8-u-s-representative', 'congressional-district-8-united-states-representative')
  sameScoring(el, 'kittitas-legislative-district-13-state-senator', 'grant-legislative-district-13-state-senator')
  for (const pos of [1, 2])
    sameScoring(el, `kittitas-legislative-district-13-state-representative-pos-${pos}`, `grant-legislative-district-13-state-representative-pos-${pos}`)
  assert.ok(!el.contests.some((c) => c.owner !== 'kittitas' && c.owner !== 'statewide'))
  // 719 E 3rd St, Cle Elum: Upper District Court.
  const ce = ballotFor(kt({ CONGDST: '8', LEGDST: '13', CITY: 'Cle Elum', COUNTY_COUNCIL: '2', DISTCRT: 'Upper District Court' }))
  const cs = ce.contests.map((c) => c.slug)
  assert.equal(cs.length, 15 + SUPREME_COURT.length)
  assert.ok(cs.includes(UPPER))
  assert.ok(!cs.includes(LOWER))
  // Commissioner 3 and the PUD seat are elected county-wide.
  for (const slug of ['kittitas-kittitas-county-commissioner-district-3-commissioner-3',
    'kittitas-public-utility-district-no-1-of-kittitas-county-commissioner-district-1-commissioner-1'])
    assert.ok(es.includes(slug) && cs.includes(slug), slug)
  assert.equal(coverageAdvice(kt({})), null)
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
  const { contests, measures } = ballotFor(garfield)
  assert.deepEqual(contests.map((c) => c.slug), SUPREME_COURT)
  assert.deepEqual(measures.map((m) => m.slug), STATE_MEASURES)
  assert.equal(coverageAdvice(garfield), 'statewide-only')
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
  const { axes, items } = ballotFor(garfield)
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
  for (const context of [garfield, ...Object.values(ADDRESSES)]) {
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
  const { contests, measures, text } = briefFor(garfield)
  assert.match(text, /November 3, 2026 General Election/)
  assert.match(text, /Coverage: STATEWIDE-ONLY GUIDE/)
  assert.match(text, /omits county, city, school, fire, judicial district, and other local contests/)
  assert.match(text, /Resolved county: Garfield County/)
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
  const { text } = briefFor(garfield)
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
