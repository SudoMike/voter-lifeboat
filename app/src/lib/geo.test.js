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
