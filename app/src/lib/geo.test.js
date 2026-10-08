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
    // Any other filter: the feature's own predicate (Island PUDDST, UNINC).
    if (attrs && hit.keep && !hit.keep(where)) attrs = null
    return { ok: true, async json() { return { features: attrs ? [{ attributes: attrs }] : [] } } }
  }
  return calls
}

const wave2Data = (id) => ({
  coverage: { statewide_complete: true, supported_counties: [{ id, coverage: 'full_county' }] },
})

test('Franklin commissioner districts resolve from the county portal MapServer', async () => {
  // The ArcGIS Online copy (services3.arcgis.com/S61OMZovc3AIomN2,
  // Districts/FeatureServer/8) answered 400 "Invalid URL" (2026-10-09
  // hotfix). Live 2026-10-08: 1016 N 4th Ave, Pasco -> 'COM2'; 5600 N Rd 68,
  // Pasco -> 'COM3'. The primary's Franklin race is scoped COUNTY_COUNCIL 'COM3'.
  const portal = 'https://gisportal.franklin.co.franklin.wa.us/arcgis2/rest/services/districts/Commissioner_Districts/MapServer/0/query?'
  const layer = { path: '/arcgis2/rest/services/districts/Commissioner_Districts/MapServer/0' }
  const com3 = { kind: 'DISTRICT', county: 'franklin', layer: 'COUNTY_COUNCIL', value: 'COM3' }
  let calls = mockWave2('5600 N RD 68, PASCO, WA, 99301', '021', 'Franklin County', [
    { ...layer, attributes: { DISTRICT_CODE: 'COM3' } },
  ])
  let context = await lookupBallotContext(wave2Data('franklin'), '5600 N Rd 68 Pasco WA 99301')
  assert.equal(context.coverageStatus, 'full_county')
  assert.equal(context.districts.COUNTY_COUNCIL, 'COM3')
  assert.deepEqual(context.missingLayers, [])
  assert.ok(scopeMatches(com3, context))
  // PORTDST and FIRDST (#29) are the county's other layers.
  const layerCalls = calls.filter((u) => u.includes('Commissioner_Districts'))
  assert.equal(layerCalls.length, 1)
  assert.ok(layerCalls[0].startsWith(portal), layerCalls[0])
  assert.equal(new URL(layerCalls[0]).searchParams.get('outFields'), 'DISTRICT_CODE')

  calls = mockWave2('1016 N 4TH AVE, PASCO, WA, 99301', '021', 'Franklin County', [
    { ...layer, attributes: { DISTRICT_CODE: 'COM2' } },
  ])
  context = await lookupBallotContext(wave2Data('franklin'), '1016 N 4th Ave Pasco WA 99301')
  assert.equal(context.districts.COUNTY_COUNCIL, 'COM2')
  assert.deepEqual(context.missingLayers, [])
  assert.ok(!scopeMatches(com3, context))
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

test('a Census place whose name ends in City keeps it; only NAME loses the legal suffix', async () => {
  // 1009 Dale Ave, Benton City (2026-10-08): BASENAME 'Benton City', NAME
  // 'Benton City city'. The Benton City propositions are scoped CITY 'Benton City'.
  const place = (p) => async (url) => {
    if (String(url).startsWith('/api/geocode')) {
      return {
        ok: true,
        async json() {
          return {
            result: {
              addressMatches: [{
                matchedAddress: '1009 DALE AVE, BENTON CITY, WA, 99320',
                coordinates: { x: -119.49, y: 46.26 },
                geographies: {
                  Counties: [{ STATE: '53', COUNTY: '005', NAME: 'Benton County' }],
                  '120th Congressional Districts': [{ BASENAME: '4' }],
                  '2026 State Legislative Districts - Lower': [{ BASENAME: '16' }],
                  'Incorporated Places': [p],
                },
              }],
            },
          }
        },
      }
    }
    return { ok: true, async json() { return { features: [] } } }
  }
  global.fetch = place({ BASENAME: 'Benton City', NAME: 'Benton City city' })
  let context = await lookupBallotContext(wave2Data('benton'), '1009 Dale Ave Benton City WA 99320')
  assert.equal(context.districts.CITY, 'Benton City')
  assert.ok(scopeMatches({ kind: 'DISTRICT', county: 'benton', layer: 'CITY', value: 'Benton City' }, context))
  global.fetch = place({ NAME: 'Benton City city' })
  context = await lookupBallotContext(wave2Data('benton'), '1009 Dale Ave Benton City WA 99320')
  assert.equal(context.districts.CITY, 'Benton City')
})

// Skagit and Grant (#28, wave 3b). Live DOR point queries 2026-10-08 at the
// Census-geocoded points of the addresses below.
test('Skagit Fire District 5 and La Conner School District 311 resolve from DOR', async () => {
  const fd5 = { kind: 'DISTRICT', county: 'skagit', layer: 'FIRDST', value: '5' }
  const sd311 = { kind: 'DISTRICT', county: 'skagit', layer: 'SCHDST', value: '311' }
  // 5800 Main St, Bow: FIR2025 '5', SCH2025 '100' (Burlington-Edison).
  mockWave2('5800 MAIN ST, BOW, WA, 98232', '057', 'Skagit County', [dorLayer(7, '5'), dorLayer(20, '100')])
  let context = await lookupBallotContext(wave2Data('skagit'), '5800 Main St Bow WA 98232')
  assert.equal(context.coverageStatus, 'full_county')
  assert.deepEqual(context.missingLayers, [])
  assert.ok(scopeMatches(fd5, context))
  assert.ok(!scopeMatches(sd311, context))
  // 305 N 6th St, La Conner: SCH2025 '311', no fire district feature.
  mockWave2('305 N 6TH ST, LA CONNER, WA, 98257', '057', 'Skagit County', [dorLayer(20, '311')])
  context = await lookupBallotContext(wave2Data('skagit'), '305 N 6th St La Conner WA 98257')
  assert.equal(context.districts.SCHDST, '311')
  assert.ok(scopeMatches(sd311, context))
  assert.ok(!scopeMatches(fd5, context))
})

test('Grant Fire District 7, Cemetery District 2 and Hospital District 4 resolve from DOR', async () => {
  const fd7 = { kind: 'DISTRICT', county: 'grant', layer: 'FIRDST', value: '7' }
  const cem2 = { kind: 'DISTRICT', county: 'grant', layer: 'CEMDST', value: '2' }
  const hosp4 = { kind: 'DISTRICT', county: 'grant', layer: 'HOSPDST', value: '4' }
  // 34875 Park Lake Rd NE, Coulee City: FIR2025 '7', HSP2025 '4', no cemetery district.
  mockWave2('34875 PARK LAKE RD NE, COULEE CITY, WA, 99115', '025', 'Grant County', [dorLayer(7, '7'), dorLayer(11, '4')])
  let context = await lookupBallotContext(wave2Data('grant'), '34875 Park Lake Rd NE Coulee City WA 99115')
  assert.equal(context.coverageStatus, 'full_county')
  assert.deepEqual(context.missingLayers, [])
  assert.equal(context.districts.FIRDST, '7')
  assert.ok(scopeMatches(fd7, context))
  assert.ok(scopeMatches(hosp4, context))
  assert.ok(!scopeMatches(cem2, context))
  // 103 Railroad St, Wilson Creek: CEM2025 '2', HSP2025 '4', no fire district.
  mockWave2('103 RAILROAD ST, WILSON CREEK, WA, 98860', '025', 'Grant County', [dorLayer(3, '2'), dorLayer(11, '4')])
  context = await lookupBallotContext(wave2Data('grant'), '103 Railroad St Wilson Creek WA 98860')
  assert.equal(context.districts.CEMDST, '2')
  assert.ok(scopeMatches(cem2, context))
  assert.ok(!scopeMatches(fd7, context))
  // 321 S Balsam St, Moses Lake: HSP2025 '1' only.
  mockWave2('321 S BALSAM ST, MOSES LAKE, WA, 98837', '025', 'Grant County', [dorLayer(11, '1')])
  context = await lookupBallotContext(wave2Data('grant'), '321 S Balsam St Moses Lake WA 98837')
  for (const scope of [fd7, cem2, hosp4]) assert.ok(!scopeMatches(scope, context), scope.layer)
})

// Island and Lewis (#29, wave 4). Live point queries 2026-10-08 at the
// Census-geocoded points of the addresses below.
const islandPrecinct = (name) => ({
  path: 'Geocortex/Elections/MapServer/2/query',
  attributes: { County: '53029', PrecinctNa: name },
  keep: (where) => where === "PrecinctNa LIKE 'Camano%'" && name.startsWith('Camano'),
})
const islandTca = (tca) => ({
  path: 'WADOR_PropertyTax/MapServer/23/query',
  attributes: { COUNTYNAME: 'ISLAND', DISTATTRIB: tca },
  keep: (where) =>
    where === "COUNTYNAME = 'ISLAND' AND DISTATTRIB NOT IN ('0100','0300','0700')" && !['0100', '0300', '0700'].includes(tca),
})
const islandCommissioner = (n) => ({ path: 'Geocortex/Elections/MapServer/0/query', attributes: { COMM__DIST___: n } })

test('Island resolves the Camano PUD seat, the South Whidbey port and the unincorporated county', async () => {
  const pud = { kind: 'DISTRICT', county: 'island', layer: 'PUDDST', value: '53029' }
  const port = { kind: 'DISTRICT', county: 'island', layer: 'PORTDST', value: 'S WHIDBEY' }
  const uninc = { kind: 'DISTRICT', county: 'island', layer: 'UNINC', value: 'ISLAND' }
  // 848 N Sunrise Blvd, Camano Island: precinct Camano 01, TCA 0590, no port.
  const calls = mockWave2('848 N SUNRISE BLVD, CAMANO ISLAND, WA, 98282', '029', 'Island County', [
    islandCommissioner('3'), islandPrecinct('Camano 01'), islandTca('0590'),
  ])
  let context = await lookupBallotContext(wave2Data('island'), '848 N Sunrise Blvd Camano Island WA 98282')
  assert.equal(context.coverageStatus, 'full_county')
  assert.deepEqual(context.missingLayers, [])
  assert.equal(context.districts.PUDDST, '53029')
  assert.equal(context.districts.UNINC, 'ISLAND')
  assert.ok(scopeMatches(pud, context))
  assert.ok(scopeMatches(uninc, context))
  assert.ok(!scopeMatches(port, context))
  const where = (path) => calls.filter((u) => u.includes(path)).map((u) => new URL(u).searchParams.get('where'))
  assert.deepEqual(where('Elections/MapServer/2/query'), ["PrecinctNa LIKE 'Camano%'"])
  assert.deepEqual(where('MapServer/23/query'), ["COUNTYNAME = 'ISLAND' AND DISTATTRIB NOT IN ('0100','0300','0700')"])
  // 112 2nd St, Langley: precinct Langley, PRT2025 'S WHIDBEY', TCA 0700 (incorporated).
  mockWave2('112 2ND ST, LANGLEY, WA, 98260', '029', 'Island County', [
    islandCommissioner('1'), islandPrecinct('Langley'), dorLayer(16, 'S WHIDBEY'), islandTca('0700'),
  ])
  context = await lookupBallotContext(wave2Data('island'), '112 2nd St Langley WA 98260')
  assert.ok(scopeMatches(port, context))
  assert.ok(!scopeMatches(pud, context))
  assert.ok(!scopeMatches(uninc, context))
  // 865 SW Barrington Dr, Oak Harbor: precinct Oak Harbor 03, TCA 0100, no port.
  mockWave2('865 SW BARRINGTON DR, OAK HARBOR, WA, 98277', '029', 'Island County', [
    islandCommissioner('2'), islandPrecinct('Oak Harbor 03'), islandTca('0100'),
  ])
  context = await lookupBallotContext(wave2Data('island'), '865 SW Barrington Dr Oak Harbor WA 98277')
  for (const scope of [pud, port, uninc]) assert.ok(!scopeMatches(scope, context), scope.layer)
  // 5476 Harbor Rd, Freeland (unincorporated): port and advisory vote, no PUD.
  mockWave2('5476 HARBOR RD, FREELAND, WA, 98249', '029', 'Island County', [
    islandCommissioner('1'), islandPrecinct('S Whidbey 13'), dorLayer(16, 'S WHIDBEY'), islandTca('0760'),
  ])
  context = await lookupBallotContext(wave2Data('island'), '5476 Harbor Rd Freeland WA 98249')
  assert.ok(scopeMatches(port, context))
  assert.ok(scopeMatches(uninc, context))
  assert.ok(!scopeMatches(pud, context))
})

test('Lewis resolves PUD No. 1 (not Centralia) and Timberland Regional Library (not Pe Ell) from DOR', async () => {
  const pud = { kind: 'DISTRICT', county: 'lewis', layer: 'PUDDST', value: '1' }
  const trl = { kind: 'DISTRICT', county: 'lewis', layer: 'LIBDST', value: 'L' }
  const fd6 = { kind: 'DISTRICT', county: 'lewis', layer: 'FIRDST', value: '6' }
  // 351 NW North St, Chehalis: PUD2025 '1', LIB2025 'L', no fire district.
  mockWave2('351 NW NORTH ST, CHEHALIS, WA, 98532', '041', 'Lewis County', [dorLayer(17, '1'), dorLayer(12, 'L')])
  let context = await lookupBallotContext(wave2Data('lewis'), '351 NW North St Chehalis WA 98532')
  assert.equal(context.coverageStatus, 'full_county')
  assert.deepEqual(context.missingLayers, [])
  assert.ok(scopeMatches(pud, context))
  assert.ok(scopeMatches(trl, context))
  assert.ok(!scopeMatches(fd6, context))
  // 118 W Maple St, Centralia: LIB2025 'L', FIR2025 'RFPSA 1', no PUD feature.
  mockWave2('118 W MAPLE ST, CENTRALIA, WA, 98531', '041', 'Lewis County', [dorLayer(7, 'RFPSA 1'), dorLayer(12, 'L')])
  context = await lookupBallotContext(wave2Data('lewis'), '118 W Maple St Centralia WA 98531')
  assert.ok(!scopeMatches(pud, context))
  assert.ok(scopeMatches(trl, context))
  // 2152 Jackson Hwy, Chehalis: FIR2025 '6', PUD2025 '1', LIB2025 'L'.
  mockWave2('2152 JACKSON HWY, CHEHALIS, WA, 98532', '041', 'Lewis County', [dorLayer(7, '6'), dorLayer(17, '1'), dorLayer(12, 'L')])
  context = await lookupBallotContext(wave2Data('lewis'), '2152 Jackson Hwy Chehalis WA 98532')
  for (const scope of [pud, trl, fd6]) assert.ok(scopeMatches(scope, context), scope.layer)
  // 200 S Main St, Pe Ell: PUD2025 '1', FIR2025 '11', outside Timberland.
  mockWave2('200 MAIN ST, PE ELL, WA, 98572', '041', 'Lewis County', [dorLayer(7, '11'), dorLayer(17, '1')])
  context = await lookupBallotContext(wave2Data('lewis'), '200 S Main St Pe Ell WA 98572')
  assert.ok(scopeMatches(pud, context))
  assert.ok(!scopeMatches(trl, context))
})

// Franklin, Chelan, Clallam and Grays Harbor (#29, wave 4b). Live point
// queries 2026-10-08 at the Census-geocoded points of the addresses below.
const franklinLayer = (path, value) => ({ path, attributes: { DISTRICT_CODE: value } })

test('Franklin resolves the Port of Pasco district and Fire District 3', async () => {
  const port3 = { kind: 'DISTRICT', county: 'franklin', layer: 'PORTDST', value: 'PoP3' }
  const fd3 = { kind: 'DISTRICT', county: 'franklin', layer: 'FIRDST', value: '3' }
  // 5600 N Rd 68, Pasco (unincorporated): COM3, PoP3, FIR2025 '3'.
  const calls = mockWave2('5600 N RD 68, PASCO, WA, 99301', '021', 'Franklin County', [
    franklinLayer('Commissioner_Districts/MapServer/0', 'COM3'),
    franklinLayer('Special_tax_districts/MapServer/7', 'PoP3'),
    dorLayer(7, '3'),
  ])
  let context = await lookupBallotContext(wave2Data('franklin'), '5600 N Rd 68 Pasco WA 99301')
  assert.equal(context.coverageStatus, 'full_county')
  assert.deepEqual(context.missingLayers, [])
  assert.deepEqual([context.districts.PORTDST, context.districts.FIRDST], ['PoP3', '3'])
  assert.ok(scopeMatches(port3, context))
  assert.ok(scopeMatches(fd3, context))
  const port = calls.find((u) => u.includes('Special_tax_districts/MapServer/7/query'))
  assert.equal(new URL(port).searchParams.get('outFields'), 'DISTRICT_CODE')
  // 525 N 3rd Ave, Pasco: COM2, PoP1, no fire district.
  mockWave2('525 N 3RD AVE, PASCO, WA, 99301', '021', 'Franklin County', [
    franklinLayer('Commissioner_Districts/MapServer/0', 'COM2'),
    franklinLayer('Special_tax_districts/MapServer/7', 'PoP1'),
  ])
  context = await lookupBallotContext(wave2Data('franklin'), '525 N 3rd Ave Pasco WA 99301')
  assert.deepEqual(context.missingLayers, [])
  assert.ok(!scopeMatches(port3, context))
  assert.ok(!scopeMatches(fd3, context))
})

test('Chelan reads commissioner districts from GIS/CM_districts and Wenatchee SD 246 from DOR SCH2025', async () => {
  const sd246 = { kind: 'DISTRICT', county: 'chelan', layer: 'SCHDST', value: '246' }
  // 316 Washington St, Wenatchee: district 1, SCH2025 '246'.
  const calls = mockWave2('316 WASHINGTON ST, WENATCHEE, WA, 98801', '007', 'Chelan County', [
    { path: 'GIS/CM_districts/MapServer/0', attributes: { DIST_NO: '1' } },
    dorLayer(20, '246'),
  ])
  let context = await lookupBallotContext(wave2Data('chelan'), '316 Washington St Wenatchee WA 98801')
  assert.equal(context.coverageStatus, 'full_county')
  assert.deepEqual(context.missingLayers, [])
  assert.equal(context.districts.COUNTY_COUNCIL, '1')
  assert.ok(scopeMatches(sd246, context))
  // The PW/Commissioner_Districts service, whose queries fail, is not asked.
  assert.equal(calls.filter((u) => u.includes('PW/Commissioner_Districts')).length, 0)
  // 101 Woodring St, Cashmere: district 2, Cashmere SD 222.
  mockWave2('101 WOODRING ST, CASHMERE, WA, 98815', '007', 'Chelan County', [
    { path: 'GIS/CM_districts/MapServer/0', attributes: { DIST_NO: '2' } },
    dorLayer(20, '222'),
  ])
  context = await lookupBallotContext(wave2Data('chelan'), '101 Woodring St Cashmere WA 98815')
  assert.equal(context.districts.COUNTY_COUNCIL, '2')
  assert.ok(!scopeMatches(sd246, context))
})

const clallamPud = (n) => ({ path: 'PUD_Commissioner_District_dissolve/FeatureServer/0', attributes: { Comm_Dist: n } })
const clallamCourt = (n) => ({ path: 'District_Court/FeatureServer/0', attributes: { DISTRICT: n } })
const clallamPudAll = { kind: 'DISTRICT', county: 'clallam', layer: 'PUDALL', value: '1' }

test('a layer with a constant value reports it when the point has a feature (Clallam PUDALL)', async () => {
  // 500 E Division St, Forks: PUD commissioner district 3, District Court 2,
  // QVSD 402, FIR2025 '1'.
  const calls = mockWave2('500 E DIVISION ST, FORKS, WA, 98331', '009', 'Clallam County', [
    { path: 'Commissioner_Districts/FeatureServer/0', attributes: { COM_DIST: '3' } },
    clallamPud('3'), clallamCourt('2'), dorLayer(7, '1'), dorLayer(20, '402'),
  ])
  const context = await lookupBallotContext(wave2Data('clallam'), '500 E Division St Forks WA 98331')
  assert.equal(context.coverageStatus, 'full_county')
  assert.deepEqual(context.missingLayers, [])
  // PUDDST still reads the commissioner district; PUDALL reads the constant.
  assert.equal(context.districts.PUDDST, '3')
  assert.equal(context.districts.PUDALL, '1')
  assert.equal(context.districts.DISTCRT, '2')
  assert.equal(context.districts.SCHDST, '402')
  assert.ok(scopeMatches(clallamPudAll, context))
  assert.ok(scopeMatches({ kind: 'DISTRICT', county: 'clallam', layer: 'DISTCRT', value: '2' }, context))
  assert.equal(calls.filter((u) => u.includes('PUD_Commissioner_District_dissolve')).length, 2)
})

test('a constant-value layer with no feature is no district, not a missing layer (Port Angeles)', async () => {
  // 223 E 4th St, Port Angeles: outside the PUD's commissioner districts.
  mockWave2('223 E 4TH ST, PORT ANGELES, WA, 98362', '009', 'Clallam County', [
    { path: 'Commissioner_Districts/FeatureServer/0', attributes: { COM_DIST: '2' } },
    clallamCourt('1'), dorLayer(20, '121'),
  ])
  const context = await lookupBallotContext(wave2Data('clallam'), '223 E 4th St Port Angeles WA 98362')
  assert.equal(context.coverageStatus, 'full_county')
  assert.deepEqual(context.missingLayers, [])
  assert.equal('PUDALL' in context.districts, false)
  assert.equal('PUDDST' in context.districts, false)
  assert.equal(context.districts.DISTCRT, '1')
  assert.ok(!scopeMatches(clallamPudAll, context))
})

test('a constant-value layer that fails to answer is reported missing', async () => {
  mockWave2('500 E DIVISION ST, FORKS, WA, 98331', '009', 'Clallam County', [])
  const inner = global.fetch
  global.fetch = async (url) => {
    if (String(url).includes('PUD_Commissioner_District_dissolve')) return { ok: false, async json() { return {} } }
    return inner(url)
  }
  const context = await lookupBallotContext(wave2Data('clallam'), '500 E Division St Forks WA 98331')
  assert.deepEqual([...context.missingLayers].sort(), ['PUDALL', 'PUDDST'])
  assert.equal(context.coverageStatus, 'partial_county')
})

test('Grays Harbor resolves Timberland Regional Library (not Ocean Shores) and McCleary SD 65 from DOR', async () => {
  const trl = { kind: 'DISTRICT', county: 'grays-harbor', layer: 'LIBDST', value: 'L' }
  const sd65 = { kind: 'DISTRICT', county: 'grays-harbor', layer: 'SCHDST', value: '65' }
  const fd1 = { kind: 'DISTRICT', county: 'grays-harbor', layer: 'FIRDST', value: '1' }
  // 100 S 3rd St, McCleary: LIB2025 'L', SCH2025 '65', no fire district.
  mockWave2('100 S 3RD ST, MCCLEARY, WA, 98557', '027', 'Grays Harbor County', [dorLayer(12, 'L'), dorLayer(20, '65')])
  let context = await lookupBallotContext(wave2Data('grays-harbor'), '100 S 3rd St McCleary WA 98557')
  assert.equal(context.coverageStatus, 'full_county')
  assert.deepEqual(context.missingLayers, [])
  assert.ok(scopeMatches(trl, context))
  assert.ok(scopeMatches(sd65, context))
  assert.ok(!scopeMatches(fd1, context))
  // 110 Main St, Oakville: FIR2025 '1', LIB2025 'L', Oakville SD 400.
  mockWave2('110 MAIN ST, OAKVILLE, WA, 98568', '027', 'Grays Harbor County', [
    dorLayer(7, '1'), dorLayer(12, 'L'), dorLayer(20, '400'),
  ])
  context = await lookupBallotContext(wave2Data('grays-harbor'), '110 Main St Oakville WA 98568')
  assert.ok(scopeMatches(fd1, context))
  assert.ok(scopeMatches(trl, context))
  assert.ok(!scopeMatches(sd65, context))
  // 585 Point Brown Ave NW, Ocean Shores: outside Timberland.
  mockWave2('585 POINT BROWN AVE NW, OCEAN SHORES, WA, 98569', '027', 'Grays Harbor County', [dorLayer(20, '64')])
  context = await lookupBallotContext(wave2Data('grays-harbor'), '585 Point Brown Ave NW Ocean Shores WA 98569')
  assert.deepEqual(context.missingLayers, [])
  assert.ok(!scopeMatches(trl, context))
})

// Mason (#30, wave 5). Live point queries 2026-10-08 at the Census-geocoded
// points of the addresses below.
const masonCommissioner = (n) => ({ path: 'MasonCoSite/Districts/MapServer/1', attributes: { DIST_ID: n } })

test('Mason resolves PUD No. 1 or No. 3 and its school districts from DOR', async () => {
  const pud1 = { kind: 'DISTRICT', county: 'mason', layer: 'PUDDST', value: '1' }
  const pud3 = { kind: 'DISTRICT', county: 'mason', layer: 'PUDDST', value: '3' }
  const sd65 = { kind: 'DISTRICT', county: 'mason', layer: 'SCHDST', value: '65' }
  const sd402 = { kind: 'DISTRICT', county: 'mason', layer: 'SCHDST', value: '402' }
  // 525 W Cota St, Shelton: commissioner 3, no fire district, PUD 3, Shelton SD 309.
  const calls = mockWave2('525 W COTA ST, SHELTON, WA, 98584', '045', 'Mason County', [
    masonCommissioner('3'), dorLayer(17, '3'), dorLayer(20, '309'),
  ])
  let context = await lookupBallotContext(wave2Data('mason'), '525 W Cota St Shelton WA 98584')
  assert.equal(context.coverageStatus, 'full_county')
  assert.deepEqual(context.missingLayers, [])
  assert.deepEqual([context.districts.PUDDST, context.districts.SCHDST], ['3', '309'])
  assert.ok(scopeMatches(pud3, context))
  assert.ok(!scopeMatches(pud1, context))
  assert.ok(!scopeMatches(sd402, context))
  for (const n of [17, 20]) {
    const url = calls.find((u) => u.includes(`WADOR_PropertyTax/MapServer/${n}/query`))
    assert.equal(new URL(url).searchParams.get('outFields'), 'DISTATTRIB')
  }
  // 24151 N US Hwy 101, Hoodsport: commissioner 2, FIR2025 '18', PUD 1, Hood Canal SD 404.
  mockWave2('24151 N US HWY 101, HOODSPORT, WA, 98548', '045', 'Mason County', [
    masonCommissioner('2'), dorLayer(7, '18'), dorLayer(17, '1'), dorLayer(20, '404'),
  ])
  context = await lookupBallotContext(wave2Data('mason'), '24151 N US Hwy 101 Hoodsport WA 98548')
  assert.deepEqual(context.missingLayers, [])
  assert.ok(scopeMatches(pud1, context))
  assert.ok(!scopeMatches(pud3, context))
  // 281 W Bonnieview Dr, McCleary (Mason side): PUD 3, McCleary SD 65.
  mockWave2('281 BONNIEVIEW DR, MCCLEARY, WA, 98557', '045', 'Mason County', [
    masonCommissioner('2'), dorLayer(7, '13'), dorLayer(17, '3'), dorLayer(20, '65'),
  ])
  context = await lookupBallotContext(wave2Data('mason'), '281 W Bonnieview Dr McCleary WA 98557')
  assert.ok(scopeMatches(sd65, context))
  assert.ok(scopeMatches(pud3, context))
  assert.ok(!scopeMatches({ ...sd65, county: 'grays-harbor' }, context))
})

// Walla Walla and Stevens (#30, wave 5). Live point queries 2026-10-08 at the
// Census-geocoded points of the addresses below.
const wallaWallaCommissioner = (n) => ({ path: 'Voting_Districts1/FeatureServer/52', attributes: { commis_dis: n } })
const stevensCommissioner = (n) => ({ path: 'AdministrativeBoundaries/MapServer/5', attributes: { districtid: n } })

test('Walla Walla resolves Dixie SD 101 and the Prescott park district from DOR', async () => {
  const dixie = { kind: 'DISTRICT', county: 'walla-walla', layer: 'SCHDST', value: '101' }
  const prescott = { kind: 'DISTRICT', county: 'walla-walla', layer: 'PARKDST', value: 'PRES' }
  // 108 S D St, Prescott: commissioner 2, Prescott SD 402, park district PRES.
  const calls = mockWave2('108 S D ST, PRESCOTT, WA, 99348', '071', 'Walla Walla County', [
    wallaWallaCommissioner('2'), dorLayer(20, '402'), dorLayer(14, 'PRES'),
  ])
  let context = await lookupBallotContext(wave2Data('walla-walla'), '108 S D St Prescott WA 99348')
  assert.equal(context.coverageStatus, 'full_county')
  assert.deepEqual(context.missingLayers, [])
  assert.deepEqual([context.districts.SCHDST, context.districts.PARKDST], ['402', 'PRES'])
  assert.ok(scopeMatches(prescott, context))
  assert.ok(!scopeMatches(dixie, context))
  for (const n of [14, 20]) {
    const url = calls.find((u) => u.includes(`WADOR_PropertyTax/MapServer/${n}/query`))
    assert.equal(new URL(url).searchParams.get('outFields'), 'DISTATTRIB')
  }
  // 315 W Main St, Walla Walla: Walla Walla SD 140, no park district.
  mockWave2('315 W MAIN ST, WALLA WALLA, WA, 99362', '071', 'Walla Walla County', [
    wallaWallaCommissioner('1'), dorLayer(20, '140'),
  ])
  context = await lookupBallotContext(wave2Data('walla-walla'), '315 W Main St Walla Walla WA 99362')
  assert.deepEqual(context.missingLayers, [])
  assert.ok(!scopeMatches(prescott, context))
  assert.ok(!scopeMatches(dixie, context))
  // Dixie (an interior point; the Census geocoder matches no Dixie street
  // address): SCH2025 '101'.
  mockWave2('DIXIE, WA', '071', 'Walla Walla County', [wallaWallaCommissioner('2'), dorLayer(20, '101')])
  context = await lookupBallotContext(wave2Data('walla-walla'), 'Dixie WA')
  assert.ok(scopeMatches(dixie, context))
  assert.ok(!scopeMatches({ ...dixie, county: 'clark' }, context))
})

test('Stevens resolves the rural library district and Nine Mile Falls SD from DOR', async () => {
  const library = { kind: 'DISTRICT', county: 'stevens', layer: 'LIBDST', value: 'L' }
  const fd10 = { kind: 'DISTRICT', county: 'stevens', layer: 'FIRDST', value: '10' }
  const nmf = { kind: 'DISTRICT', county: 'stevens', layer: 'SCHDST', value: '179J' }
  // 6015 State Route 291, Nine Mile Falls: FD 1, library L, SD 179J.
  const calls = mockWave2('6015 STATE RTE 291, NINE MILE FALLS, WA, 99026', '065', 'Stevens County', [
    stevensCommissioner('1'), dorLayer(7, '1'), dorLayer(12, 'L'), dorLayer(20, '179J'),
  ])
  let context = await lookupBallotContext(wave2Data('stevens'), '6015 State Route 291 Nine Mile Falls WA 99026')
  assert.equal(context.coverageStatus, 'full_county')
  assert.deepEqual(context.missingLayers, [])
  assert.ok(scopeMatches(library, context))
  assert.ok(scopeMatches(nmf, context))
  assert.ok(!scopeMatches(fd10, context))
  for (const n of [12, 20]) {
    const url = calls.find((u) => u.includes(`WADOR_PropertyTax/MapServer/${n}/query`))
    assert.equal(new URL(url).searchParams.get('outFields'), 'DISTATTRIB')
  }
  // 2785 Aladdin Rd, Colville: FD 10, library L, SCH2025 '211'.
  mockWave2('2785 ALADDIN RD, COLVILLE, WA, 99114', '065', 'Stevens County', [
    stevensCommissioner('3'), dorLayer(7, '10'), dorLayer(12, 'L'), dorLayer(20, '211'),
  ])
  context = await lookupBallotContext(wave2Data('stevens'), '2785 Aladdin Rd Colville WA 99114')
  assert.ok(scopeMatches(library, context))
  assert.ok(scopeMatches(fd10, context))
  assert.ok(!scopeMatches(nmf, context))
  // 215 S Oak St, Colville: outside the library and fire districts.
  mockWave2('215 S OAK ST, COLVILLE, WA, 99114', '065', 'Stevens County', [
    stevensCommissioner('3'), dorLayer(20, '115'),
  ])
  context = await lookupBallotContext(wave2Data('stevens'), '215 S Oak St Colville WA 99114')
  assert.deepEqual(context.missingLayers, [])
  assert.ok(!scopeMatches(library, context))
  assert.ok(!scopeMatches(fd10, context))
  assert.ok(!scopeMatches(nmf, context))
})

// Whitman and Douglas (#30, wave 5). Live point queries 2026-10-08 at the
// Census-geocoded points of the addresses below.
const whitmanCommissioner = (n) => ({ path: 'Whitman_County_BOCC_Districts___Feb__2026_WFL1/FeatureServer/10', attributes: { BOCC: n } })
const douglasFire = (n) => ({ path: 'All_Districts_Temporary/MapServer/4', attributes: { FireNumber: n } })

test('Whitman resolves its library, cemetery and Cheney school scopes from DOR', async () => {
  const library = { kind: 'DISTRICT', county: 'whitman', layer: 'LIBDST', value: 'L' }
  const oakesdaleCemetery = { kind: 'DISTRICT', county: 'whitman', layer: 'CEMDST', value: '1' }
  const oakesdalePark = { kind: 'DISTRICT', county: 'whitman', layer: 'PARKDST', value: '4' }
  const cheney = { kind: 'DISTRICT', county: 'whitman', layer: 'SCHDST', value: '316' }
  const fd14 = { kind: 'DISTRICT', county: 'whitman', layer: 'FIRDST', value: '14' }
  // 101 Steptoe Ave, Oakesdale: library L, Cemetery 1, Park 4, SD 324.
  const calls = mockWave2('101 STEPTOE AVE, OAKESDALE, WA, 99158', '075', 'Whitman County', [
    whitmanCommissioner(1), dorLayer(14, '4'), dorLayer(3, '1'), dorLayer(12, 'L'), dorLayer(20, '324'),
  ])
  let context = await lookupBallotContext(wave2Data('whitman'), '101 Steptoe Ave Oakesdale WA 99158')
  assert.equal(context.coverageStatus, 'full_county')
  assert.deepEqual(context.missingLayers, [])
  assert.ok(scopeMatches(library, context))
  assert.ok(scopeMatches(oakesdaleCemetery, context))
  assert.ok(scopeMatches(oakesdalePark, context))
  assert.ok(!scopeMatches(cheney, context))
  assert.ok(!scopeMatches(fd14, context))
  for (const n of [3, 12, 20]) {
    const url = calls.find((u) => u.includes(`WADOR_PropertyTax/MapServer/${n}/query`))
    assert.equal(new URL(url).searchParams.get('outFields'), 'DISTATTRIB')
  }
  // 110 S Montgomery St, Uniontown: FD 14, no library, cemetery or park.
  mockWave2('110 S MONTGOMERY ST, UNIONTOWN, WA, 99179', '075', 'Whitman County', [
    whitmanCommissioner(2), dorLayer(7, '14'), dorLayer(20, '306'),
  ])
  context = await lookupBallotContext(wave2Data('whitman'), '110 S Montgomery St Uniontown WA 99179')
  assert.deepEqual(context.missingLayers, [])
  assert.ok(scopeMatches(fd14, context))
  assert.ok(!scopeMatches(library, context))
  assert.ok(!scopeMatches(oakesdaleCemetery, context))
  // Interior point (-117.70, 47.24) north of St. John: Cheney SD's Whitman
  // portion, '316'.
  mockWave2('ST. JOHN RURAL, WA', '075', 'Whitman County', [
    whitmanCommissioner(1), dorLayer(7, '5'), dorLayer(12, 'L'), dorLayer(20, '316'),
  ])
  context = await lookupBallotContext(wave2Data('whitman'), 'St John rural WA')
  assert.ok(scopeMatches(cheney, context))
  assert.ok(!scopeMatches({ ...cheney, county: 'spokane' }, context))
})

test('Douglas resolves Eastmont SD, Cemetery District 2 and the proposed Rimrock fire district', async () => {
  const eastmont = { kind: 'DISTRICT', county: 'douglas', layer: 'SCHDST', value: '206' }
  const cemetery2 = { kind: 'DISTRICT', county: 'douglas', layer: 'CEMDST', value: '2' }
  const hospital2 = { kind: 'DISTRICT', county: 'douglas', layer: 'HOSPDST', value: '2' }
  const rimrock = { kind: 'DISTRICT', county: 'douglas', layer: 'PROPFIRDST', value: '009' }
  // 1005 Ashcroft Dr, Ephrata (Rimrock Meadows): proposed FPD 9, SD 209.
  const calls = mockWave2('1005 ASHCROFT DR, EPHRATA, WA, 98823', '017', 'Douglas County', [
    dorLayer(20, '209'), douglasFire('009'),
  ])
  let context = await lookupBallotContext(wave2Data('douglas'), '1005 Ashcroft Dr Ephrata WA 98823')
  assert.equal(context.coverageStatus, 'full_county')
  assert.deepEqual(context.missingLayers, [])
  assert.equal(context.districts.PROPFIRDST, '009')
  assert.equal(context.districts.FIRDST, undefined)
  assert.ok(scopeMatches(rimrock, context))
  assert.ok(!scopeMatches(eastmont, context))
  const fire = calls.find((u) => u.includes('All_Districts_Temporary/MapServer/4/query'))
  assert.ok(fire.startsWith('https://gis.douglascountywa.gov/server/rest/services/'), fire)
  assert.equal(new URL(fire).searchParams.get('outFields'), 'FireNumber')
  // 448 Belmont Pl, Ephrata: an existing fire district ('001'), not Rimrock;
  // DOR FD 1, Hospital District 2, Cemetery District 2.
  mockWave2('448 BELMONT PL, EPHRATA, WA, 98823', '017', 'Douglas County', [
    dorLayer(7, '1'), dorLayer(11, '2'), dorLayer(20, '209'), dorLayer(3, '2'), douglasFire('001'),
  ])
  context = await lookupBallotContext(wave2Data('douglas'), '448 Belmont Pl Ephrata WA 98823')
  assert.deepEqual(context.missingLayers, [])
  assert.ok(!scopeMatches(rimrock, context))
  assert.ok(scopeMatches(hospital2, context))
  assert.ok(scopeMatches(cemetery2, context))
  // 100 Eastmont Ave, East Wenatchee: Eastmont SD 206, DOR FD 2.
  mockWave2('100 EASTMONT AVE, EAST WENATCHEE, WA, 98802', '017', 'Douglas County', [
    dorLayer(7, '2'), dorLayer(20, '206'), douglasFire('002'),
  ])
  context = await lookupBallotContext(wave2Data('douglas'), '100 Eastmont Ave East Wenatchee WA 98802')
  assert.deepEqual(context.missingLayers, [])
  assert.ok(scopeMatches(eastmont, context))
  assert.ok(!scopeMatches(cemetery2, context))
  assert.ok(!scopeMatches(rimrock, context))
  // The archived primary's Douglas fire scopes still read DOR FIRDST.
  assert.ok(scopeMatches({ kind: 'DISTRICT', county: 'douglas', layer: 'FIRDST', value: '2' }, context))
})
