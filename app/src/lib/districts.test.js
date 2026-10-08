import test from 'node:test'
import assert from 'node:assert/strict'
import { describeDistrict, describeDistricts, layerLabel } from './districts.js'

// Every value shape below was taken from a live resolver response, so these
// cases document what the county GIS services actually return.

test('numeric layer values read as a numbered district', () => {
  assert.equal(describeDistrict('LEGDST', '5'), 'Legislative District 5')
  assert.equal(describeDistrict('CONGDST', '8'), 'Congressional District 8')
  assert.equal(describeDistrict('SCHDST', '411'), 'School District 411')
})

test('presence flags drop the meaningless value', () => {
  assert.equal(describeDistrict('DISTCRT', 'YES'), 'District Court')
  assert.equal(describeDistrict('PTBA', 'Y'), 'Public Transportation Benefit Area')
  assert.equal(describeDistrict('AQUIFER', 'yes'), 'Aquifer Protection Area')
  // '1' is a real district number, not a flag.
  assert.equal(describeDistrict('HOSPDST', '1'), 'Hospital District 1')
})

test('values that already read as a name stand alone', () => {
  assert.equal(describeDistrict('SCHDST', 'Everett School District 2'), 'Everett School District 2')
  assert.equal(describeDistrict('PUDDST', 'PUD Commissioner District 1'), 'PUD Commissioner District 1')
  assert.equal(describeDistrict('LIBDST', 'Sno - Isle Library District'), 'Sno - Isle Library District')
  assert.equal(describeDistrict('FIRE_AUTH', 'S.E. Thurston Fire Authority'), 'S.E. Thurston Fire Authority')
  assert.equal(describeDistrict('RFADST', 'SCRFA'), 'South Snohomish County Fire & Rescue Regional Fire Authority')
})

test('Spokane school and fire layer values read as names', () => {
  assert.equal(describeDistrict('SCHDST', 'Spokane #81'), 'Spokane School District No. 81')
  assert.equal(describeDistrict('SCHDST', 'Reardan/Edwall #9'), 'Reardan/Edwall School District No. 9')
  assert.equal(describeDistrict('FIRDST', 'Fire District 9'), 'Fire District 9')
  assert.equal(describeDistrict('FIRDST', 'City of Spokane'), 'City of Spokane Fire Department')
  assert.equal(describeDistrict('FIRDST', 'Spokane Valley Fire'), 'Spokane Valley Fire Department (Fire District 1)')
  assert.equal(describeDistrict('FIRDST', 'Unserved'), 'No fire district')
})

test('Pierce Election_Precincts values read as names; NO flags drop out', () => {
  // Live 2026-10-08 (#21): 1402 Lake Tapps Pkwy SE, Auburn.
  assert.equal(describeDistrict('SCHDST', 'AUBURN SCHOOL DISTRICT NO. 408'), 'Auburn School District No. 408')
  assert.equal(describeDistrict('SCHDST', 'YELM COMMUNITY SCHOOLS'), 'Yelm Community Schools')
  assert.equal(describeDistrict('KCDISTCRT', 'YES'), 'King County District Court, Southeast Electoral District')
  assert.equal(describeDistrict('PTBA', 'YES'), 'Public Transportation Benefit Area')
  assert.equal(describeDistrict('DISTCRT', 'NO'), null)
  assert.equal(describeDistrict('KCDISTCRT', 'NO'), null)
  // Snohomish's Court_Districts layer names the district outright (#27).
  assert.equal(describeDistrict('DISTCRT', 'Everett District Court'), 'Everett District Court')
  const lines = describeDistricts({
    CONGDST: '8', LEGDST: '31', COUNTY_COUNCIL: '1', DISTCRT: 'NO', KCDISTCRT: 'YES', PTBA: 'YES',
    SCHDST: 'AUBURN SCHOOL DISTRICT NO. 408', CITY: 'Auburn',
  }).map((d) => d.key)
  assert.deepEqual(lines, ['CITY', 'CONGDST', 'LEGDST', 'COUNTY_COUNCIL', 'KCDISTCRT', 'SCHDST', 'PTBA'])
})

test('codes are tidied without mangling initialisms', () => {
  assert.equal(describeDistrict('FIRDST', 'TACOMA'), 'Fire District Tacoma')
  assert.equal(describeDistrict('SCCDST', 'SCC5'), 'Seattle City Council District 5')
  assert.equal(describeDistrict('CITY', 'Everett'), 'City of Everett')
})

test('empty values are dropped rather than rendered blank', () => {
  assert.equal(describeDistrict('LEGDST', ''), null)
  assert.equal(describeDistrict('LEGDST', null), null)
  assert.equal(describeDistricts({ LEGDST: '5', FIRDST: '' }).length, 1)
})

test('county governing body borrows commissioner-vs-council wording from the data', () => {
  const contests = [
    { scope: { layer: 'COUNTY_COUNCIL', county: 'adams' }, district: 'Adams County Commissioner District 3' },
    { scope: { layer: 'COUNTY_COUNCIL', county: 'clark' }, district: 'Clark County Council District 1' },
    { scope: { layer: 'COUNTY_COUNCIL', county: 'thurston' }, district: 'Thurston County Commissioner District No. 3' },
  ]
  const name = (county, value) =>
    describeDistricts({ COUNTY_COUNCIL: value }, { contests, county })[0].text

  assert.equal(name('adams', '3'), 'Adams County Commissioner District 3')
  assert.equal(name('clark', '1'), 'Clark County Council District 1')
  assert.equal(name('thurston', '5'), 'Thurston County Commissioner District 5')
  // Staggered terms mean the voter's own seat is often not up this cycle; the
  // wording still has to come out right for a district with no live contest.
  assert.equal(name('adams', '1'), 'Adams County Commissioner District 1')
  // A county with no contest at all falls back to the generic label.
  assert.equal(name('garfield', '2'), 'County Council District 2')
})

test('districts that pick candidates sort ahead of levy-only districts', () => {
  const lines = describeDistricts({
    SCHDST: '411', LEGDST: '5', FIRDST: '10', CONGDST: '8', KCCDST: '9',
  })
  assert.deepEqual(lines.map((d) => d.key), ['CONGDST', 'LEGDST', 'KCCDST', 'FIRDST', 'SCHDST'])
})

test('an unconfigured layer is shown rather than silently dropped', () => {
  assert.equal(describeDistrict('NEWDST', '7'), 'NEWDST 7')
})

test('King District Court electoral districts read by name, not code', () => {
  assert.equal(describeDistrict('JUDDST', 'NE'), 'King County District Court, Northeast Electoral District')
  assert.equal(describeDistrict('JUDDST', 'SE'), 'King County District Court, Southeast Electoral District')
  assert.equal(describeDistrict('JUDDST', 'SW'), 'King County District Court, Southwest Electoral District')
  assert.equal(describeDistrict('JUDDST', 'W'), 'King County District Court, West Electoral District')
  assert.equal(describeDistrict('JUDDST', 'SH'), 'King County District Court, Shoreline Electoral District')
  assert.equal(describeDistrict('JUDDST', 'sh'), 'King County District Court, Shoreline Electoral District')
  // A code King has not published before still shows, rather than vanishing.
  assert.equal(describeDistrict('JUDDST', 'XX'), 'King County District Court Electoral District XX')
})

test('the director context for a Seattle address lists every district in words', () => {
  const lines = describeDistricts(
    { CONGDST: '7', LEGDST: '46', KCCDST: '1', SCCDST: 'SCC5', JUDDST: 'W', SCHDST: '1', CITY: 'Seattle' },
    { county: 'king' }
  ).map((d) => d.text)
  assert.deepEqual(lines, [
    'City of Seattle',
    'Congressional District 7',
    'Legislative District 46',
    'King County Council District 1',
    'Seattle City Council District 5',
    'King County District Court, West Electoral District',
    'School District 1',
  ])
})

test('layer ids in coverage warnings read as district names', () => {
  assert.equal(layerLabel('KCCDST'), 'King County Council District')
  assert.equal(layerLabel('SCCDST'), 'Seattle City Council District')
  assert.equal(layerLabel('JUDDST'), 'King County District Court Electoral District')
  assert.equal(layerLabel('CITY'), 'City')
  assert.equal(layerLabel('county-local'), 'local county districts')
  assert.equal(layerLabel('NEWDST'), 'NEWDST')
})
