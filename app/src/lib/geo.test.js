import test from 'node:test'
import assert from 'node:assert/strict'
import {
  lookupBallotContext,
  scopeMatches,
  hasZip,
  withZip,
  shouldAskForZip,
  coverageAdvice,
  suggestAddresses,
} from './geo.js'

const kingContext = {
  coverageStatus: 'full_county',
  county: { id: 'king', fips: '53033', name: 'King County' },
  districts: { LEGDST: '43', CONGDST: '7' },
}

test('STATEWIDE scopes match any Washington ballot context', () => {
  assert.equal(scopeMatches({ kind: 'STATEWIDE' }, { county: { id: null }, districts: {} }), true)
})

test('COUNTY scopes require matching county id', () => {
  assert.equal(scopeMatches({ kind: 'COUNTY', county: 'king' }, kingContext), true)
  assert.equal(scopeMatches({ kind: 'COUNTY', county: 'pierce' }, kingContext), false)
})

test('DISTRICT scopes require county, layer, and value match', () => {
  assert.equal(scopeMatches({ kind: 'DISTRICT', county: 'king', layer: 'LEGDST', value: '43' }, kingContext), true)
  assert.equal(scopeMatches({ kind: 'DISTRICT', county: 'king', layer: 'LEGDST', value: '37' }, kingContext), false)
  assert.equal(scopeMatches({ kind: 'DISTRICT', county: 'pierce', layer: 'LEGDST', value: '43' }, kingContext), false)
})

function mockGeocode(match) {
  global.fetch = async () => ({
    ok: true,
    async json() {
      return { result: { addressMatches: [match] } }
    },
  })
}

test('unsupported Washington counties receive statewide-only fallback when statewide data is complete', async () => {
  mockGeocode({
    matchedAddress: '3000 PACIFIC AVE SE, OLYMPIA, WA, 98501',
    coordinates: { x: -122.83, y: 47.03 },
    geographies: {
      Counties: [{ STATE: '53', COUNTY: '067', NAME: 'Thurston County' }],
    },
  })
  const context = await lookupBallotContext(
    { coverage: { statewide_complete: true, supported_counties: [{ id: 'king' }] } },
    '3000 Pacific Ave SE Olympia WA 98501'
  )
  assert.equal(context.coverageStatus, 'statewide_only')
  assert.equal(context.county.id, 'thurston')
})

// The general's coverage before any county ships (issue #9): every Washington
// address, King included, gets the Statewide-Only Guide without a district
// lookup; anything outside Washington still stops at the geocode.
const statewideOnlyData = { coverage: { statewide_complete: true, supported_counties: [] } }

test('with no supported counties, every Washington county is statewide-only', async () => {
  for (const [fips, name, id] of [
    ['033', 'King County', 'king'],
    ['063', 'Spokane County', 'spokane'],
  ]) {
    const calls = []
    global.fetch = async (url) => {
      calls.push(String(url))
      return {
        ok: true,
        async json() {
          return {
            result: {
              addressMatches: [
                {
                  matchedAddress: `1 MAIN ST, ${name.toUpperCase()}, WA`,
                  coordinates: { x: -120, y: 47 },
                  geographies: { Counties: [{ STATE: '53', COUNTY: fips, NAME: name }] },
                },
              ],
            },
          }
        },
      }
    }
    const context = await lookupBallotContext(statewideOnlyData, '1 Main St WA')
    assert.equal(context.coverageStatus, 'statewide_only', name)
    assert.equal(context.county.id, id)
    assert.deepEqual(context.districts, {})
    assert.deepEqual(context.missingLayers, [])
    assert.equal(calls.length, 1, `${name}: only the geocoder is called`)
    assert.equal(coverageAdvice(context), 'statewide-only')
  }
})

test('with no supported counties, an out-of-state address still hard-stops', async () => {
  mockGeocode({
    matchedAddress: '1600 PENNSYLVANIA AVE NW, WASHINGTON, DC, 20500',
    coordinates: { x: -77.03, y: 38.89 },
    geographies: { Counties: [{ STATE: '11', COUNTY: '001', NAME: 'District of Columbia' }] },
  })
  await assert.rejects(
    lookupBallotContext(statewideOnlyData, '1600 Pennsylvania Ave NW Washington DC 20500'),
    (err) => err.kind === 'outside-wa'
  )
})

test('without statewide data, an unsupported county is not covered yet', async () => {
  mockGeocode({
    matchedAddress: '808 W SPOKANE FALLS BLVD, SPOKANE, WA, 99201',
    coordinates: { x: -117.42, y: 47.66 },
    geographies: { Counties: [{ STATE: '53', COUNTY: '063', NAME: 'Spokane County' }] },
  })
  await assert.rejects(
    lookupBallotContext({ coverage: { statewide_complete: false, supported_counties: [] } }, 'x'),
    (err) => err.kind === 'unsupported-county'
  )
})

test('Census district layers are found whatever vintage names them', async () => {
  mockGeocode({
    matchedAddress: '789 W MAIN ST, POMEROY, WA, 99347',
    coordinates: { x: -117.6, y: 46.47 },
    geographies: {
      // Garfield's District Adapter has no county layers, so only Census answers.
      Counties: [{ STATE: '53', COUNTY: '023', NAME: 'Garfield County' }],
      '120th Congressional Districts': [{ BASENAME: '5' }],
      '2026 State Legislative Districts - Lower': [{ BASENAME: '9' }],
      '2026 State Legislative Districts - Upper': [{ BASENAME: '9' }],
      'Incorporated Places': [{ BASENAME: 'Pomeroy' }],
    },
  })
  const context = await lookupBallotContext(
    { coverage: { statewide_complete: true, supported_counties: [{ id: 'garfield', coverage: 'full_county' }] } },
    '789 W Main St, Pomeroy, WA 99347'
  )
  assert.deepEqual(context.districts, { CONGDST: '5', LEGDST: '9', CITY: 'Pomeroy' })
  assert.deepEqual(context.missingLayers, [])
  assert.equal(context.coverageStatus, 'full_county')
})

test('a congressional layer without BASENAME falls back to its CD<session> or GEOID number', async () => {
  for (const congressional of [{ CD120: '05', GEOID: '5305' }, { GEOID: '5305' }]) {
    mockGeocode({
      matchedAddress: '789 W MAIN ST, POMEROY, WA, 99347',
      coordinates: { x: -117.6, y: 46.47 },
      geographies: {
        Counties: [{ STATE: '53', COUNTY: '023', NAME: 'Garfield County' }],
        '120th Congressional Districts': [congressional],
        '2026 State Legislative Districts - Lower': [{ SLDL: '009' }],
        '2026 State Legislative Districts - Upper': [{ SLDU: '009' }],
      },
    })
    const context = await lookupBallotContext(
      { coverage: { statewide_complete: true, supported_counties: [{ id: 'garfield', coverage: 'full_county' }] } },
      '789 W Main St, Pomeroy, WA 99347'
    )
    assert.equal(context.districts.CONGDST, '5', JSON.stringify(congressional))
    assert.equal(context.districts.LEGDST, '9')
    assert.deepEqual(context.missingLayers, [])
  }
})

test('supported non-King counties use Census federal/state districts as partial coverage', async () => {
  mockGeocode({
    matchedAddress: '3000 ROCKEFELLER AVE, EVERETT, WA, 98201',
    coordinates: { x: -122.2, y: 48 },
    geographies: {
      Counties: [{ STATE: '53', COUNTY: '061', NAME: 'Snohomish County' }],
      '119th Congressional Districts': [{ BASENAME: '2' }],
      '2024 State Legislative Districts - Lower': [{ BASENAME: '38' }],
      '2024 State Legislative Districts - Upper': [{ BASENAME: '38' }],
      'Incorporated Places': [{ BASENAME: 'Everett' }],
    },
  })
  const context = await lookupBallotContext(
    { coverage: { statewide_complete: true, supported_counties: [{ id: 'king' }, { id: 'snohomish' }] } },
    '3000 Rockefeller Ave Everett WA 98201'
  )
  assert.equal(context.coverageStatus, 'partial_county')
  assert.deepEqual(context.districts, { CONGDST: '2', LEGDST: '38', CITY: 'Everett' })
  assert.deepEqual(context.missingLayers, [])
})

test('configured non-King county layers produce full county coverage', async () => {
  global.fetch = async (url) => {
    if (String(url).startsWith('/api/geocode')) {
      return {
        ok: true,
        async json() {
          return {
            result: {
              addressMatches: [{
                matchedAddress: '1408 FRANKLIN ST, VANCOUVER, WA, 98660',
                coordinates: { x: -122.67, y: 45.63 },
                geographies: {
                  Counties: [{ STATE: '53', COUNTY: '011', NAME: 'Clark County' }],
                  '119th Congressional Districts': [{ BASENAME: '3' }],
                  '2024 State Legislative Districts - Lower': [{ BASENAME: '49' }],
                  'Incorporated Places': [{ BASENAME: 'Vancouver' }],
                },
              }],
            },
          }
        },
      }
    }
    const attr = String(url).includes('BoardofCountyCouncilorsDistrict')
      ? { BOCCDistrict: 1 }
      : String(url).includes('CPUCommissionerDistrict')
        ? { DISTRICT: 3 }
        : String(url).includes('SchoolDistrict')
          ? { SCHDST: 37 }
          : { FIREDST: 10 }
    return {
      ok: true,
      async json() {
        return { features: [{ attributes: attr }] }
      },
    }
  }
  const context = await lookupBallotContext(
    { coverage: { statewide_complete: true, supported_counties: [{ id: 'king' }, { id: 'clark', coverage: 'full_county' }] } },
    '1408 Franklin St Vancouver WA 98660'
  )
  assert.equal(context.coverageStatus, 'full_county')
  assert.deepEqual(context.districts, {
    CONGDST: '3',
    LEGDST: '49',
    CITY: 'Vancouver',
    COUNTY_COUNCIL: '1',
    PUDDST: '3',
    FIRDST: '10',
    SCHDST: '37',
  })
  assert.deepEqual(context.missingLayers, [])
})

test('configured non-King layers stay partial until the county data package is full', async () => {
  global.fetch = async (url) => {
    if (String(url).startsWith('/api/geocode')) {
      return {
        ok: true,
        async json() {
          return {
            result: {
              addressMatches: [{
                matchedAddress: '1116 W BROADWAY AVE, SPOKANE, WA, 99260',
                coordinates: { x: -117.43, y: 47.66 },
                geographies: {
                  Counties: [{ STATE: '53', COUNTY: '063', NAME: 'Spokane County' }],
                  '119th Congressional Districts': [{ BASENAME: '5' }],
                  '2024 State Legislative Districts - Lower': [{ BASENAME: '3' }],
                },
              }],
            },
          }
        },
      }
    }
    const attr = String(url).includes('Boundary/MapServer/8')
      ? { DISTNUM: 2 }
      : String(url).includes('WADOR_PropertyTax')
        ? { DISTATTRIB: 'ROSA' }
        : { NAME: 'Spokane County Library District', PTBA: 'Y' }
    return {
      ok: true,
      async json() {
        return { features: [{ attributes: attr }] }
      },
    }
  }
  const context = await lookupBallotContext(
    { coverage: { statewide_complete: true, supported_counties: [{ id: 'spokane', coverage: 'partial_county' }] } },
    '1116 W Broadway Ave Spokane WA 99260'
  )
  assert.equal(context.coverageStatus, 'partial_county')
  assert.deepEqual(context.missingLayers, [])
})

test('missing census congressional/legislative districts degrade coverage to partial', async () => {
  global.fetch = async (url) => {
    if (String(url).startsWith('/api/geocode')) {
      return {
        ok: true,
        async json() {
          return {
            result: {
              addressMatches: [{
                matchedAddress: '1408 FRANKLIN ST, VANCOUVER, WA, 98660',
                coordinates: { x: -122.67, y: 45.63 },
                geographies: {
                  Counties: [{ STATE: '53', COUNTY: '011', NAME: 'Clark County' }],
                  // No congressional/legislative geographies: the census
                  // vintage rotated or the response degraded.
                },
              }],
            },
          }
        },
      }
    }
    return {
      ok: true,
      async json() {
        return { features: [{ attributes: { BOCCDistrict: 1, District: 3, FIREDST: 10 } }] }
      },
    }
  }
  const context = await lookupBallotContext(
    { coverage: { statewide_complete: true, supported_counties: [{ id: 'clark', coverage: 'full_county' }] } },
    '1408 Franklin St Vancouver WA 98660'
  )
  assert.equal(context.coverageStatus, 'partial_county')
  assert.ok(context.missingLayers.includes('CONGDST'))
  assert.ok(context.missingLayers.includes('LEGDST'))
})

test('King County honors a partial data package even when every GIS layer resolves', async () => {
  global.fetch = async (url) => {
    if (String(url).startsWith('/api/geocode')) {
      return {
        ok: true,
        async json() {
          return {
            result: {
              addressMatches: [{
                matchedAddress: '400 BROAD ST, SEATTLE, WA, 98109',
                coordinates: { x: -122.35, y: 47.62 },
                geographies: { Counties: [{ STATE: '53', COUNTY: '033', NAME: 'King County' }] },
              }],
            },
          }
        },
      }
    }
    return {
      ok: true,
      async json() {
        return { features: [{ attributes: { CONGDST: '7', LEGDST: '36', KCCDST: '4', SCCDST: 'SCC7', juddst: 'W', FIRDST: null, SCHDST: '1', NAME: 'Seattle' } }] }
      },
    }
  }
  const context = await lookupBallotContext(
    { coverage: { statewide_complete: true, supported_counties: [{ id: 'king', coverage: 'partial_county' }] } },
    '400 Broad St Seattle WA 98109'
  )
  assert.equal(context.coverageStatus, 'partial_county')
})

// King County Cemetery District No. 1 (Vashon-Maury Island) has no King GIS
// layer; King's adapter reads the WA DOR cemetery layer the other counties use.
function mockKing(matchedAddress, attrsFor) {
  const calls = []
  global.fetch = async (url) => {
    calls.push(String(url))
    if (String(url).startsWith('/api/geocode')) {
      return {
        ok: true,
        async json() {
          return {
            result: {
              addressMatches: [{
                matchedAddress,
                coordinates: { x: -122.46, y: 47.45 },
                geographies: { Counties: [{ STATE: '53', COUNTY: '033', NAME: 'King County' }] },
              }],
            },
          }
        },
      }
    }
    const attrs = attrsFor(String(url))
    return { ok: true, async json() { return { features: attrs ? [{ attributes: attrs }] : [] } } }
  }
  return calls
}

const kingFull = { coverage: { statewide_complete: true, supported_counties: [{ id: 'king', coverage: 'full_county' }] } }

test('King resolves the cemetery district from the DOR cemetery layer', async () => {
  const calls = mockKing('10105 SW BANK RD, VASHON, WA, 98070', (url) =>
    url.includes('WADOR_PropertyTax/MapServer/3/query')
      ? { DISTATTRIB: '1' }
      : { CONGDST: '7', LEGDST: '34', KCCDST: '8', SCCDST: null, juddst: 'W', FIRDST: '13', SCHDST: '402', NAME: 'King County' }
  )
  const context = await lookupBallotContext(kingFull, '10105 SW Bank Rd Vashon WA 98070')
  assert.equal(context.coverageStatus, 'full_county')
  assert.equal(context.districts.CEMDST, '1')
  assert.equal(context.districts.CITY, undefined)
  assert.deepEqual(context.missingLayers, [])
  const dor = calls.find((u) => u.includes('WADOR_PropertyTax'))
  assert.ok(dor.startsWith('https://webgis.dor.wa.gov/arcgis/rest/services/Programs/WADOR_PropertyTax/MapServer/3/query?'), dor)
  assert.equal(new URL(dor).searchParams.get('outFields'), 'DISTATTRIB')
  assert.ok(scopeMatches({ kind: 'DISTRICT', county: 'king', layer: 'CEMDST', value: '1' }, context))
})

test('a King address outside the cemetery district has no CEMDST and stays full', async () => {
  mockKing('600 4TH AVE, SEATTLE, WA, 98104', (url) =>
    url.includes('WADOR_PropertyTax')
      ? null
      : { CONGDST: '7', LEGDST: '36', KCCDST: '4', SCCDST: 'SCC7', juddst: 'W', FIRDST: null, SCHDST: '1', NAME: 'Seattle' }
  )
  const context = await lookupBallotContext(kingFull, '600 4th Ave Seattle WA 98104')
  assert.equal(context.coverageStatus, 'full_county')
  assert.equal('CEMDST' in context.districts, false)
  assert.ok(!scopeMatches({ kind: 'DISTRICT', county: 'king', layer: 'CEMDST', value: '1' }, context))
})

test('a failed DOR cemetery lookup degrades a King ballot to partial', async () => {
  mockKing('10105 SW BANK RD, VASHON, WA, 98070', (url) =>
    url.includes('WADOR_PropertyTax') ? undefined : { CONGDST: '7', LEGDST: '34', NAME: 'King County' }
  )
  const realFetch = global.fetch
  global.fetch = async (url) =>
    String(url).includes('WADOR_PropertyTax') ? { ok: false, async json() { return {} } } : realFetch(url)
  const context = await lookupBallotContext(kingFull, '10105 SW Bank Rd Vashon WA 98070')
  assert.equal(context.coverageStatus, 'partial_county')
  assert.deepEqual(context.missingLayers, ['CEMDST'])
})

test('hasZip ignores a five-digit house number and only trusts a trailing ZIP', () => {
  assert.equal(hasZip('19019 SE 128th St'), false)
  assert.equal(hasZip('19019 SE 128th Street'), false)
  assert.equal(hasZip('19019 SE 128th St, Renton, WA 98059'), true)
  assert.equal(hasZip('19019 SE 128th St, Renton, WA 98059-1234'), true)
  assert.equal(hasZip('  4218 SW Othello St, Seattle  '), false)
  assert.equal(hasZip(''), false)
  assert.equal(hasZip(undefined), false)
})

test('withZip appends a state and ZIP the Census geocoder can use', () => {
  assert.equal(withZip('19019 SE 128th Street', '98059'), '19019 SE 128th Street, WA 98059')
  assert.equal(withZip('19019 SE 128th Street,', '98059'), '19019 SE 128th Street, WA 98059')
  assert.equal(withZip('  19019 SE 128th Street  ', ' 98059 '), '19019 SE 128th Street, WA 98059')
})

test('a line rebuilt by withZip reads as having a ZIP, so the prompt is not repeated', () => {
  const once = withZip('19019 SE 128th Street', '98059')
  assert.equal(hasZip(once), true)
})

// --- suggest dropdown -------------------------------------------------------
// suggestAddresses hand-builds a SQL where clause against the King County
// address layer, so these lock down the clause itself as much as the output.

function mockArcgis(features) {
  const calls = []
  global.fetch = async (url) => {
    calls.push(String(url))
    return { ok: true, async json() { return { features } } }
  }
  return calls
}

const whereOf = (url) => new URL(url).searchParams.get('where')

test('suggestAddresses asks for a left-anchored prefix match on ADDR_FULL', async () => {
  const calls = mockArcgis([])
  await suggestAddresses('19019 SE 128th')
  assert.equal(whereOf(calls[0]), "ADDR_FULL LIKE '19019 SE 128th%'")
})

test('the typed text reaches the query verbatim, abbreviations and all', async () => {
  // The layer stores 'ST', never 'STREET', so a spelled-out street type matches
  // nothing. Nothing normalizes it — the ZIP recovery prompt is what rescues
  // this case. If that ever changes, this expectation should change with it.
  const calls = mockArcgis([])
  await suggestAddresses('19019 SE 128th Street')
  assert.equal(whereOf(calls[0]), "ADDR_FULL LIKE '19019 SE 128th Street%'")
})

test('apostrophes are escaped so real street names cannot break the clause', async () => {
  // King County really has addresses like 140 LEO'S PL.
  const calls = mockArcgis([])
  await suggestAddresses("140 LEO'S PL")
  assert.equal(whereOf(calls[0]), "ADDR_FULL LIKE '140 LEO''S PL%'")
})

test('a suggestion with no city is labeled unincorporated, keeping its ZIP', async () => {
  mockArcgis([{ attributes: { ADDR_FULL: '19019 SE 128TH ST', CTYNAME: null, ZIP5: '98059' } }])
  const [s] = await suggestAddresses('19019 SE 128th St')
  assert.equal(s.full, '19019 SE 128TH ST')
  assert.equal(s.label, '19019 SE 128TH ST, Unincorporated King County, WA 98059')
})

test('a suggestion inside a city is labeled with that city', async () => {
  mockArcgis([{ attributes: { ADDR_FULL: '1900 5TH AVE', CTYNAME: 'Seattle', ZIP5: '98101' } }])
  const [s] = await suggestAddresses('1900 5th Ave')
  assert.equal(s.label, '1900 5TH AVE, Seattle, WA 98101')
})

test('queries too short to be useful never reach the network', async () => {
  let called = false
  global.fetch = async () => {
    called = true
    return { ok: true, async json() { return { features: [] } } }
  }
  assert.deepEqual(await suggestAddresses('1900'), [])
  assert.deepEqual(await suggestAddresses('   '), [])
  assert.equal(called, false, 'short queries must not hit the address layer')
})

test('a failed or malformed suggest response yields no dropdown, not an error', async () => {
  global.fetch = async () => ({ ok: false, async json() { return {} } })
  assert.deepEqual(await suggestAddresses('19019 SE 128th'), [])
  global.fetch = async () => ({ ok: true, async json() { return { error: { code: 400 } } } })
  assert.deepEqual(await suggestAddresses('19019 SE 128th'), [])
  global.fetch = async () => ({ ok: true, async json() { return {} } })
  assert.deepEqual(await suggestAddresses('19019 SE 128th'), [])
})

// --- screen decisions -------------------------------------------------------

test('shouldAskForZip fires only for an unplaceable line carrying no ZIP', () => {
  assert.equal(shouldAskForZip({ kind: 'no-match' }, '19019 SE 128th Street'), true)
  // Already has one and still failed: a second prompt would just loop.
  assert.equal(shouldAskForZip({ kind: 'no-match' }, '19019 SE 128th Street, WA 98059'), false)
  // A ZIP cannot fix these.
  assert.equal(shouldAskForZip({ kind: 'outside-wa' }, '1600 Pennsylvania Ave'), false)
  assert.equal(shouldAskForZip({ kind: 'network' }, '19019 SE 128th Street'), false)
  assert.equal(shouldAskForZip({ kind: 'no-districts' }, '19019 SE 128th Street'), false)
  assert.equal(shouldAskForZip(null, '19019 SE 128th Street'), false)
})

test('coverageAdvice reports degraded coverage from either cause', () => {
  assert.equal(coverageAdvice({ coverageStatus: 'full_county', missingLayers: [] }), null)
  assert.equal(coverageAdvice({ coverageStatus: 'partial_county', missingLayers: [] }), 'degraded')
  // A full package whose live layer lookup failed reads the same to a voter.
  assert.equal(coverageAdvice({ coverageStatus: 'full_county', missingLayers: ['DISTCRT'] }), 'degraded')
  assert.equal(coverageAdvice({ coverageStatus: 'statewide_only', missingLayers: [] }), 'statewide-only')
  assert.equal(coverageAdvice(null), null)
})

// South County Fire's RFA has no polygon in Snohomish's own fire layer; the
// adapter reads it from the DOR FIR2025 layer filtered to 'SCRFA' (live
// 2026-10-08, unfiltered: 19100 44th Ave W, Lynnwood -> 'SCRFA'; 806 W Main
// St, Monroe -> 'SRF'). The mock answers like the server: the feature at the
// point, dropped when the request's `where` excludes it.
function mockSnohomish(matchedAddress, dorValue, court = null) {
  const calls = []
  global.fetch = async (url) => {
    calls.push(String(url))
    if (String(url).startsWith('/api/geocode')) {
      return {
        ok: true,
        async json() {
          return {
            result: {
              addressMatches: [{
                matchedAddress,
                coordinates: { x: -122.29, y: 47.83 },
                geographies: {
                  Counties: [{ STATE: '53', COUNTY: '061', NAME: 'Snohomish County' }],
                  '120th Congressional Districts': [{ BASENAME: '2' }],
                  '2026 State Legislative Districts - Lower': [{ BASENAME: '32' }],
                },
              }],
            },
          }
        },
      }
    }
    const where = new URL(String(url)).searchParams.get('where')
    const kept = dorValue && (!where || where === `DISTATTRIB = '${dorValue}'`)
    const attrs = String(url).includes('WADOR_PropertyTax/MapServer/7/query') && kept
      ? { DISTATTRIB: dorValue }
      : String(url).includes('Court_Districts/FeatureServer/0/query') && court
        ? { District: court }
        : null
    return { ok: true, async json() { return { features: attrs ? [{ attributes: attrs }] : [] } } }
  }
  return calls
}

const snohomishRfa = { kind: 'DISTRICT', county: 'snohomish', layer: 'RFADST', value: 'SCRFA' }
const snohomishData = {
  coverage: { statewide_complete: true, supported_counties: [{ id: 'snohomish', coverage: 'partial_county' }] },
}

test('Snohomish resolves South County Fire RFA from the DOR fire layer', async () => {
  const calls = mockSnohomish('19100 44TH AVE W, LYNNWOOD, WA, 98036', 'SCRFA')
  const context = await lookupBallotContext(snohomishData, '19100 44th Ave W Lynnwood WA 98036')
  assert.equal(context.districts.RFADST, 'SCRFA')
  assert.deepEqual(context.missingLayers, [])
  assert.ok(scopeMatches(snohomishRfa, context))
  const dor = calls.filter((u) => u.includes('WADOR_PropertyTax'))
  assert.equal(dor.length, 1)
  assert.ok(dor[0].startsWith('https://webgis.dor.wa.gov/arcgis/rest/services/Programs/WADOR_PropertyTax/MapServer/7/query?'), dor[0])
  assert.equal(new URL(dor[0]).searchParams.get('outFields'), 'DISTATTRIB')
  assert.equal(new URL(dor[0]).searchParams.get('where'), "DISTATTRIB = 'SCRFA'")
})

test('another RFA or no fire feature leaves RFADST unset', async () => {
  // Monroe is in Snohomish Regional Fire & Rescue ('SRF'): filtered out, so
  // the voter is not told they live in a regional fire authority 'SRF'.
  mockSnohomish('806 W MAIN ST, MONROE, WA, 98272', 'SRF')
  let context = await lookupBallotContext(snohomishData, '806 W Main St Monroe WA 98272')
  assert.equal('RFADST' in context.districts, false)
  assert.deepEqual(context.missingLayers, [])
  assert.ok(!scopeMatches(snohomishRfa, context))
  mockSnohomish('2930 WETMORE AVE, EVERETT, WA, 98201', null)
  context = await lookupBallotContext(snohomishData, '2930 Wetmore Ave Everett WA 98201')
  assert.equal('RFADST' in context.districts, false)
  assert.ok(!scopeMatches(snohomishRfa, context))
})

// Snohomish District Court electoral districts come from the Auditor's
// Court_Districts layer, District attribute (live 2026-10-08, #27: 2930
// Wetmore Ave, Everett -> 'Everett District Court'; 806 W Main St, Monroe ->
// 'Evergreen District Court'). The seats are scoped to that exact string.
const snohomishCourt = (name) => ({ kind: 'DISTRICT', county: 'snohomish', layer: 'DISTCRT', value: `${name} District Court` })

test('Snohomish resolves its District Court electoral district from Court_Districts', async () => {
  const calls = mockSnohomish('2930 WETMORE AVE, EVERETT, WA, 98201', null, 'Everett District Court')
  const context = await lookupBallotContext(snohomishData, '2930 Wetmore Ave Everett WA 98201')
  assert.equal(context.districts.DISTCRT, 'Everett District Court')
  assert.deepEqual(context.missingLayers, [])
  assert.ok(scopeMatches(snohomishCourt('Everett'), context))
  for (const other of ['Cascade', 'Evergreen', 'South']) assert.ok(!scopeMatches(snohomishCourt(other), context))
  const court = calls.filter((u) => u.includes('Court_Districts'))
  assert.equal(court.length, 1)
  assert.ok(court[0].startsWith('https://services6.arcgis.com/z6WYi9VRHfgwgtyW/arcgis/rest/services/Court_Districts/FeatureServer/0/query?'), court[0])
  assert.equal(new URL(court[0]).searchParams.get('outFields'), 'District')
})

test('a Snohomish point in another court district does not see Everett seats', async () => {
  mockSnohomish('806 W MAIN ST, MONROE, WA, 98272', 'SRF', 'Evergreen District Court')
  const context = await lookupBallotContext(snohomishData, '806 W Main St Monroe WA 98272')
  assert.equal(context.districts.DISTCRT, 'Evergreen District Court')
  assert.ok(scopeMatches(snohomishCourt('Evergreen'), context))
  assert.ok(!scopeMatches(snohomishCourt('Everett'), context))
})

// Spokane school and fire districts come from the county's OpenData/Boundary
// service: layer 6 DISTRCTNAME and layer 1 NAME (live 2026-10-08, #21:
// 808 W Spokane Falls Blvd -> 'Spokane #81', 'City of Spokane'; 3801 E
// Farwell Rd, Mead -> 'Mead #354', 'Fire District 9').
function mockSpokane(matchedAddress, school, fire) {
  const calls = []
  global.fetch = async (url) => {
    calls.push(String(url))
    if (String(url).startsWith('/api/geocode')) {
      return {
        ok: true,
        async json() {
          return {
            result: {
              addressMatches: [{
                matchedAddress,
                coordinates: { x: -117.36, y: 47.77 },
                geographies: {
                  Counties: [{ STATE: '53', COUNTY: '063', NAME: 'Spokane County' }],
                  '120th Congressional Districts': [{ BASENAME: '5' }],
                  '2026 State Legislative Districts - Lower': [{ BASENAME: '7' }],
                },
              }],
            },
          }
        },
      }
    }
    const u = String(url)
    const attrs = u.includes('Boundary/MapServer/6/query')
      ? { DISTRCTNAME: school }
      : u.includes('Boundary/MapServer/1/query')
        ? { NAME: fire }
        : null
    return { ok: true, async json() { return { features: attrs ? [{ attributes: attrs }] : [] } } }
  }
  return calls
}

const spokaneData = {
  coverage: { statewide_complete: true, supported_counties: [{ id: 'spokane', coverage: 'partial_county' }] },
}

test('Spokane resolves school and fire districts by name from the county layers', async () => {
  const calls = mockSpokane('3801 E FARWELL RD, MEAD, WA, 99021', 'Mead #354', 'Fire District 9')
  const context = await lookupBallotContext(spokaneData, '3801 E Farwell Rd Mead WA 99021')
  assert.equal(context.districts.SCHDST, 'Mead #354')
  assert.equal(context.districts.FIRDST, 'Fire District 9')
  assert.deepEqual(context.missingLayers, [])
  assert.ok(scopeMatches({ kind: 'DISTRICT', county: 'spokane', layer: 'FIRDST', value: 'Fire District 9' }, context))
  assert.ok(!scopeMatches({ kind: 'DISTRICT', county: 'spokane', layer: 'SCHDST', value: 'Spokane #81' }, context))
  const fire = calls.find((u) => u.includes('Boundary/MapServer/1/query'))
  // NAME, not CODE: contract towns carry the serving district's CODE.
  assert.equal(new URL(fire).searchParams.get('outFields'), 'NAME')
  const school = calls.find((u) => u.includes('Boundary/MapServer/6/query'))
  assert.equal(new URL(school).searchParams.get('outFields'), 'DISTRCTNAME')
})

test('a Spokane city with its own fire department matches no fire district measure', async () => {
  mockSpokane('808 W SPOKANE FALLS BLVD, SPOKANE, WA, 99201', 'Spokane #81', 'City of Spokane')
  const context = await lookupBallotContext(spokaneData, '808 W Spokane Falls Blvd Spokane WA 99201')
  assert.equal(context.districts.FIRDST, 'City of Spokane')
  assert.ok(scopeMatches({ kind: 'DISTRICT', county: 'spokane', layer: 'SCHDST', value: 'Spokane #81' }, context))
  for (const n of [2, 3, 9, 11, 12]) {
    assert.ok(!scopeMatches({ kind: 'DISTRICT', county: 'spokane', layer: 'FIRDST', value: `Fire District ${n}` }, context))
  }
})

// Pierce's King County District Court (Southeast), Pierce Transit benefit
// area and school district are attributes of the Election_Precincts layer
// that DISTCRT already reads: KING_DISTRICT, PIERCE_TRANSIT, SCHOOL (live
// 2026-10-08, #21: 1402 Lake Tapps Pkwy SE, Auburn -> KING_DISTRICT 'YES',
// PC_DISTRICT 'NO', PIERCE_TRANSIT 'YES', SCHOOL 'AUBURN SCHOOL DISTRICT NO.
// 408'; 121 Washington St, South Prairie -> PIERCE_TRANSIT 'NO').
function mockPierce(matchedAddress, precinct) {
  const calls = []
  global.fetch = async (url) => {
    calls.push(String(url))
    if (String(url).startsWith('/api/geocode')) {
      return {
        ok: true,
        async json() {
          return {
            result: {
              addressMatches: [{
                matchedAddress,
                coordinates: { x: -122.2, y: 47.25 },
                geographies: {
                  Counties: [{ STATE: '53', COUNTY: '053', NAME: 'Pierce County' }],
                  '120th Congressional Districts': [{ BASENAME: '8' }],
                  '2026 State Legislative Districts - Lower': [{ BASENAME: '31' }],
                },
              }],
            },
          }
        },
      }
    }
    const u = new URL(String(url))
    const field = u.searchParams.get('outFields')
    const attrs = u.pathname.includes('Election_Precincts') && field in precinct
      ? { [field]: precinct[field] }
      : null
    return { ok: true, async json() { return { features: attrs ? [{ attributes: attrs }] : [] } } }
  }
  return calls
}

const pierceData = {
  coverage: { statewide_complete: true, supported_counties: [{ id: 'pierce', coverage: 'full_county' }] },
}

test('Pierce resolves King District Court, Pierce Transit and school district from Election_Precincts', async () => {
  const calls = mockPierce('1402 LAKE-TAPPS PKWY SE, AUBURN, WA, 98092', {
    PC_DISTRICT: 'NO', KING_DISTRICT: 'YES', PIERCE_TRANSIT: 'YES', SCHOOL: 'AUBURN SCHOOL DISTRICT NO. 408',
  })
  const context = await lookupBallotContext(pierceData, '1402 Lake Tapps Pkwy SE Auburn WA 98092')
  assert.equal(context.coverageStatus, 'full_county')
  assert.equal(context.districts.KCDISTCRT, 'YES')
  assert.equal(context.districts.PTBA, 'YES')
  assert.equal(context.districts.SCHDST, 'AUBURN SCHOOL DISTRICT NO. 408')
  assert.equal(context.districts.DISTCRT, 'NO')
  assert.deepEqual(context.missingLayers, [])
  assert.ok(scopeMatches({ kind: 'DISTRICT', county: 'pierce', layer: 'KCDISTCRT', value: 'YES' }, context))
  assert.ok(scopeMatches({ kind: 'DISTRICT', county: 'pierce', layer: 'PTBA', value: 'YES' }, context))
  assert.ok(scopeMatches({ kind: 'DISTRICT', county: 'pierce', layer: 'SCHDST', value: 'AUBURN SCHOOL DISTRICT NO. 408' }, context))
  assert.ok(!scopeMatches({ kind: 'DISTRICT', county: 'pierce', layer: 'DISTCRT', value: 'YES' }, context))
  // King's copy of the same races is scoped to King's county, not Pierce.
  assert.ok(!scopeMatches({ kind: 'DISTRICT', county: 'king', layer: 'JUDDST', value: 'SE' }, context))
  // Each key is its own query of the shared layer, one field each.
  const fields = calls
    .filter((u) => u.includes('Election_Precincts'))
    .map((u) => new URL(u).searchParams.get('outFields'))
    .sort()
  assert.deepEqual(fields, ['KING_DISTRICT', 'PC_DISTRICT', 'PIERCE_TRANSIT', 'SCHOOL'])
})

test('a Pierce point outside Pierce Transit and King District Court matches neither', async () => {
  mockPierce('121 WASHINGTON ST, SOUTH PRAIRIE, WA, 98385', {
    PC_DISTRICT: 'YES', KING_DISTRICT: 'NO', PIERCE_TRANSIT: 'NO', SCHOOL: 'WHITE RIVER SCHOOL DISTRICT NO. 416',
  })
  const context = await lookupBallotContext(pierceData, '121 Washington St South Prairie WA 98385')
  assert.ok(!scopeMatches({ kind: 'DISTRICT', county: 'pierce', layer: 'PTBA', value: 'YES' }, context))
  assert.ok(!scopeMatches({ kind: 'DISTRICT', county: 'pierce', layer: 'KCDISTCRT', value: 'YES' }, context))
  assert.ok(!scopeMatches({ kind: 'DISTRICT', county: 'pierce', layer: 'SCHDST', value: 'AUBURN SCHOOL DISTRICT NO. 408' }, context))
  assert.ok(scopeMatches({ kind: 'DISTRICT', county: 'pierce', layer: 'DISTCRT', value: 'YES' }, context))
})

// Clark, Kitsap and Thurston school districts and Thurston's West Thurston
// RFA (#22). Live point queries 2026-10-08 at the Census-geocoded points of
// the addresses below; the mock answers like the server, dropping a feature
// a request's `where` excludes (the Thurston fire layer's polygons carry
// CONSOL_DIS 'WTRFA - South Btn'/'WTRFA - North Btn' only inside the RFA).
function mockWave2(matchedAddress, countyFips, countyName, features) {
  const calls = []
  global.fetch = async (url) => {
    calls.push(String(url))
    if (String(url).startsWith('/api/geocode')) {
      return {
        ok: true,
        async json() {
          return {
            result: {
              addressMatches: [{
                matchedAddress,
                coordinates: { x: -122.9, y: 46.9 },
                geographies: {
                  Counties: [{ STATE: '53', COUNTY: countyFips, NAME: countyName }],
                  '120th Congressional Districts': [{ BASENAME: '10' }],
                  '2026 State Legislative Districts - Lower': [{ BASENAME: '2' }],
                },
              }],
            },
          }
        },
      }
    }
    const u = new URL(String(url))
    const field = u.searchParams.get('outFields')
    const where = u.searchParams.get('where')
    const hit = features.find((f) => u.pathname.includes(f.path))
    let attrs = hit && field in hit.attributes ? { [field]: hit.attributes[field] } : null
    if (attrs && where === "CONSOL_DIS LIKE 'WTRFA%'" && !String(hit.attributes.CONSOL_DIS).startsWith('WTRFA')) attrs = null
    // An equality filter (Benton PUDDST: PUD_District = 'Benton PUD').
    const eq = where?.match(/^(\w+) = '(.*)'$/)
    if (attrs && eq && hit.attributes[eq[1]] !== eq[2]) attrs = null
    return { ok: true, async json() { return { features: attrs ? [{ attributes: attrs }] : [] } } }
  }
  return calls
}

const wave2Data = (id) => ({
  coverage: { statewide_complete: true, supported_counties: [{ id, coverage: 'full_county' }] },
})

test('Clark resolves its school district from the county SchoolDistrict layer', async () => {
  // 109 SW 1st St, Battle Ground: SCHDST is an integer field (119).
  mockWave2('109 SW 1ST ST, BATTLE GROUND, WA, 98604', '011', 'Clark County', [
    { path: 'BoardofCountyCouncilorsDistrict', attributes: { BOCCDistrict: 5 } },
    { path: 'CPUCommissionerDistrict', attributes: { District: 1 } },
    { path: 'FireDistrictBoundary', attributes: { FIREDST: 3 } },
    { path: 'ClarkView_Public/SchoolDistrict/MapServer/0', attributes: { SCHDST: 119 } },
  ])
  const context = await lookupBallotContext(wave2Data('clark'), '109 SW 1st St Battle Ground WA 98604')
  assert.equal(context.coverageStatus, 'full_county')
  assert.equal(context.districts.SCHDST, '119')
  assert.deepEqual(context.missingLayers, [])
  assert.ok(scopeMatches({ kind: 'DISTRICT', county: 'clark', layer: 'SCHDST', value: '119' }, context))
  assert.ok(!scopeMatches({ kind: 'DISTRICT', county: 'kitsap', layer: 'SCHDST', value: '119' }, context))
})

test('Kitsap resolves its school district from School_District_Outlines', async () => {
  // 1700 SE Mile Hill Dr, Port Orchard -> '402'; Bremerton reads '100-C'.
  mockWave2('1700 SE MILE HILL DR, PORT ORCHARD, WA, 98366', '035', 'Kitsap County', [
    { path: 'County_Commissioner_District_Outlines', attributes: { DISTRICT: '2' } },
    { path: 'Fire_District_Outlines', attributes: { DISTRICT: '7' } },
    { path: 'School_District_Outlines', attributes: { DISTRICT: '402' } },
  ])
  let context = await lookupBallotContext(wave2Data('kitsap'), '1700 SE Mile Hill Dr Port Orchard WA 98366')
  assert.equal(context.districts.SCHDST, '402')
  assert.deepEqual(context.missingLayers, [])
  assert.ok(scopeMatches({ kind: 'DISTRICT', county: 'kitsap', layer: 'SCHDST', value: '402' }, context))
  mockWave2('345 6TH ST, BREMERTON, WA, 98337', '035', 'Kitsap County', [
    { path: 'School_District_Outlines', attributes: { DISTRICT: '100-C' } },
  ])
  context = await lookupBallotContext(wave2Data('kitsap'), '345 6th St Bremerton WA 98337')
  assert.ok(!scopeMatches({ kind: 'DISTRICT', county: 'kitsap', layer: 'SCHDST', value: '402' }, context))
})

const thurstonFire = (attrs) => ({ path: 'Thurston_FireDistricts_TCOMM/FeatureServer/0', attributes: attrs })

test('Thurston resolves WTRFA and its school district; fire district and RFA share one layer', async () => {
  // 18346 Albany St SW, Rochester.
  const calls = mockWave2('18346 ALBANY ST SW, ROCHESTER, WA, 98579', '067', 'Thurston County', [
    { path: 'Thurston_CommissionerDistricts', attributes: { CommissionerDistrictNumber: 2 } },
    { path: 'Jurisdictions/FeatureServer/15', attributes: { CommissionerDistrictNumber: 1 } },
    thurstonFire({ DISPATCH_G: 'FD01', CONSOL_DIS: 'WTRFA - South Btn', CONSOL_NUM: 'FD01' }),
    { path: 'Jurisdictions/FeatureServer/10', attributes: { SchoolDistrictName: 'ROCHESTER' } },
  ])
  const context = await lookupBallotContext(wave2Data('thurston'), '18346 Albany St SW Rochester WA 98579')
  assert.equal(context.coverageStatus, 'full_county')
  assert.equal(context.districts.RFADST, 'FD01')
  assert.equal(context.districts.FIRDST, 'FD01')
  assert.equal(context.districts.FIRE_AUTH, 'WTRFA - South Btn')
  assert.equal(context.districts.SCHDST, 'ROCHESTER')
  assert.deepEqual(context.missingLayers, [])
  assert.ok(scopeMatches({ kind: 'DISTRICT', county: 'thurston', layer: 'RFADST', value: 'FD01' }, context))
  assert.ok(!scopeMatches({ kind: 'DISTRICT', county: 'thurston', layer: 'SCHDST', value: 'YELM' }, context))
  // Three queries of the fire layer (FIRDST, FIRE_AUTH, RFADST); only RFADST filters.
  const fire = calls.filter((u) => u.includes('Thurston_FireDistricts_TCOMM')).map((u) => new URL(u).searchParams)
  assert.deepEqual(fire.map((p) => p.get('outFields')).sort(), ['CONSOL_DIS', 'CONSOL_NUM', 'DISPATCH_G'])
  assert.deepEqual(fire.map((p) => p.get('where')).filter(Boolean), ["CONSOL_DIS LIKE 'WTRFA%'"])
})

test('a Thurston point outside WTRFA keeps its fire district and gets no RFA', async () => {
  // 420 College St SE, Lacey: Lacey Fire District 3, North Thurston.
  mockWave2('420 COLLEGE ST SE, LACEY, WA, 98503', '067', 'Thurston County', [
    thurstonFire({ DISPATCH_G: 'FD03', CONSOL_DIS: 'Lacey', CONSOL_NUM: 'FD03' }),
    { path: 'Jurisdictions/FeatureServer/10', attributes: { SchoolDistrictName: 'NORTH THURSTON' } },
  ])
  let context = await lookupBallotContext(wave2Data('thurston'), '420 College St SE Lacey WA 98503')
  assert.equal(context.districts.FIRDST, 'FD03')
  assert.equal('RFADST' in context.districts, false)
  assert.ok(scopeMatches({ kind: 'DISTRICT', county: 'thurston', layer: 'FIRDST', value: 'FD03' }, context))
  assert.ok(!scopeMatches({ kind: 'DISTRICT', county: 'thurston', layer: 'RFADST', value: 'FD01' }, context))
  // 105 W Yelm Ave, Yelm: Yelm Community Schools, SE Thurston Fire Authority.
  mockWave2('105 W YELM AVE, YELM, WA, 98597', '067', 'Thurston County', [
    thurstonFire({ DISPATCH_G: 'FD02', CONSOL_DIS: 'S.E. Thurston Fire Authority', CONSOL_NUM: 'FD02' }),
    { path: 'Jurisdictions/FeatureServer/10', attributes: { SchoolDistrictName: 'YELM' } },
  ])
  context = await lookupBallotContext(wave2Data('thurston'), '105 W Yelm Ave Yelm WA 98597')
  assert.ok(scopeMatches({ kind: 'DISTRICT', county: 'thurston', layer: 'SCHDST', value: 'YELM' }, context))
  assert.ok(!scopeMatches({ kind: 'DISTRICT', county: 'thurston', layer: 'RFADST', value: 'FD01' }, context))
})

// Yakima, Whatcom and Benton (#28). Live point queries 2026-10-08 at the
// Census-geocoded points of the addresses below.
const dorLayer = (n, value) => ({ path: `WADOR_PropertyTax/MapServer/${n}/query`, attributes: { DISTATTRIB: value } })
const bentonPrecinct = (value) => ({ path: 'PrecinctSplits/FeatureServer/6', attributes: { PUD_District: value } })

test('Benton resolves Benton PUD from PrecinctSplits and its school district from DOR SCH2025', async () => {
  // 1009 Dale Ave, Benton City: Benton PUD, Kiona-Benton City SD 52, FD 2.
  const calls = mockWave2('1009 DALE AVE, BENTON CITY, WA, 99320', '005', 'Benton County', [
    { path: 'CommissionerDistrict/FeatureServer/6', attributes: { District: '2' } },
    dorLayer(7, '2'),
    bentonPrecinct('Benton PUD'),
    dorLayer(20, '52'),
  ])
  const context = await lookupBallotContext(wave2Data('benton'), '1009 Dale Ave Benton City WA 99320')
  assert.equal(context.coverageStatus, 'full_county')
  assert.equal(context.districts.PUDDST, 'Benton PUD')
  assert.equal(context.districts.SCHDST, '52')
  assert.deepEqual(context.missingLayers, [])
  assert.ok(scopeMatches({ kind: 'DISTRICT', county: 'benton', layer: 'PUDDST', value: 'Benton PUD' }, context))
  assert.ok(scopeMatches({ kind: 'DISTRICT', county: 'benton', layer: 'SCHDST', value: '52' }, context))
  const pud = calls.filter((u) => u.includes('PrecinctSplits')).map((u) => new URL(u).searchParams)
  assert.deepEqual(pud.map((p) => [p.get('outFields'), p.get('where')]), [['PUD_District', "PUD_District = 'Benton PUD'"]])
})

test('a Kennewick point gets the PUD race but not the Ki-Be levy', async () => {
  // 210 W 6th Ave, Kennewick: Benton PUD, Kennewick SD 17.
  mockWave2('210 W 6TH AVE, KENNEWICK, WA, 99336', '005', 'Benton County', [
    { path: 'CommissionerDistrict/FeatureServer/6', attributes: { District: '3' } },
    bentonPrecinct('Benton PUD'),
    dorLayer(20, '17'),
  ])
  const context = await lookupBallotContext(wave2Data('benton'), '210 W 6th Ave Kennewick WA 99336')
  assert.ok(scopeMatches({ kind: 'DISTRICT', county: 'benton', layer: 'PUDDST', value: 'Benton PUD' }, context))
  assert.ok(!scopeMatches({ kind: 'DISTRICT', county: 'benton', layer: 'SCHDST', value: '52' }, context))
})

test('Richland and West Richland precinct 4017 get no Benton PUD race', async () => {
  // 625 Swift Blvd, Richland: PUD_District null.
  mockWave2('625 SWIFT BLVD, RICHLAND, WA, 99352', '005', 'Benton County', [bentonPrecinct(null), dorLayer(20, '400')])
  let context = await lookupBallotContext(wave2Data('benton'), '625 Swift Blvd Richland WA 99352')
  assert.equal('PUDDST' in context.districts, false)
  assert.deepEqual(context.missingLayers, [])
  assert.ok(!scopeMatches({ kind: 'DISTRICT', county: 'benton', layer: 'PUDDST', value: 'Benton PUD' }, context))
  // Precinct 4017 is coded 'Yes' (no 2024 PUD vote); Richland 6322.1 reads '<Null>'.
  for (const value of ['Yes', '<Null>']) {
    mockWave2('3801 W VAN GIESEN ST, WEST RICHLAND, WA, 99353', '005', 'Benton County', [bentonPrecinct(value)])
    context = await lookupBallotContext(wave2Data('benton'), '3801 W Van Giesen St West Richland WA 99353')
    assert.equal('PUDDST' in context.districts, false, value)
  }
})

test('Yakima Commissioner District 1 shows only inside district 1', async () => {
  const d1 = { kind: 'DISTRICT', county: 'yakima', layer: 'COUNTY_COUNCIL', value: '1' }
  // 115 W Naches Ave, Selah -> ID 1; 128 N 2nd St, Yakima -> ID 2.
  mockWave2('115 W NACHES AVE, SELAH, WA, 98942', '077', 'Yakima County', [
    { path: 'Commissioner_District_Election_2022/FeatureServer/0', attributes: { ID: 1 } },
  ])
  let context = await lookupBallotContext(wave2Data('yakima'), '115 W Naches Ave Selah WA 98942')
  assert.equal(context.coverageStatus, 'full_county')
  assert.equal(context.districts.COUNTY_COUNCIL, '1')
  assert.deepEqual(context.missingLayers, [])
  assert.ok(scopeMatches(d1, context))
  mockWave2('128 N 2ND ST, YAKIMA, WA, 98901', '077', 'Yakima County', [
    { path: 'Commissioner_District_Election_2022/FeatureServer/0', attributes: { ID: 2 } },
  ])
  context = await lookupBallotContext(wave2Data('yakima'), '128 N 2nd St Yakima WA 98901')
  assert.equal(context.districts.COUNTY_COUNCIL, '2')
  assert.ok(!scopeMatches(d1, context))
})

test('Whatcom Fire District 1 resolves from DOR FIR2025 at Everson', async () => {
  // 111 W Main St, Everson -> FIR2025 '1', Port of Bellingham district 4.
  mockWave2('111 W MAIN ST, EVERSON, WA, 98247', '073', 'Whatcom County', [
    { path: '2021ProposedPOBDistricts', attributes: { Council: 4 } },
    dorLayer(7, '1'),
  ])
  const context = await lookupBallotContext(wave2Data('whatcom'), '111 W Main St Everson WA 98247')
  assert.equal(context.coverageStatus, 'full_county')
  assert.equal(context.districts.FIRDST, '1')
  assert.deepEqual(context.missingLayers, [])
  assert.ok(scopeMatches({ kind: 'DISTRICT', county: 'whatcom', layer: 'FIRDST', value: '1' }, context))
})
