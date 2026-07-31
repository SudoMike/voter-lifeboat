import test from 'node:test'
import assert from 'node:assert/strict'
import { describeDistrict, describeDistricts } from './districts.js'

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
})

test('codes are tidied without mangling initialisms', () => {
  assert.equal(describeDistrict('FIRDST', 'TACOMA'), 'Fire District Tacoma')
  assert.equal(describeDistrict('JUDDST', 'SE'), 'County Judicial District SE')
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
