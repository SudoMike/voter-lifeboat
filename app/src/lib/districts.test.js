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

test('Clark, Kitsap and Thurston school and WTRFA values read as names', () => {
  // Live 2026-10-08 (#22): Battle Ground (Clark, integer 119), Port Orchard
  // and Bremerton (Kitsap), Lacey and Rochester (Thurston).
  assert.equal(describeDistrict('SCHDST', '119'), 'School District 119')
  assert.equal(describeDistrict('SCHDST', '402'), 'School District 402')
  assert.equal(describeDistrict('SCHDST', '100-C'), 'School District 100-C')
  assert.equal(describeDistrict('SCHDST', 'NORTH THURSTON'), 'North Thurston School District')
  assert.equal(describeDistrict('SCHDST', 'YELM'), 'Yelm School District')
  assert.equal(describeDistrict('RFADST', 'FD01'), 'West Thurston Regional Fire Authority')
})

test('Benton PUD and Yakima, Whatcom and Benton district numbers read as names', () => {
  // Live 2026-10-08 (#28): Kennewick (Benton PUD, SD 17), Benton City (SD 52),
  // Everson (Whatcom FD 1).
  assert.equal(describeDistrict('PUDDST', 'Benton PUD'), 'Benton County Public Utility District')
  assert.equal(describeDistrict('SCHDST', '52'), 'School District 52')
  assert.equal(describeDistrict('FIRDST', '1'), 'Fire District 1')
})

test('Skagit and Grant DOR district numbers read as names', () => {
  // Live 2026-10-08 (#28): La Conner (SD 311), Bow (FD 5), Coulee City
  // (FD 7), Wilson Creek (Cemetery District 2), Soap Lake (Hospital District 4).
  assert.equal(describeDistrict('SCHDST', '311'), 'School District 311')
  assert.equal(describeDistrict('FIRDST', '5'), 'Fire District 5')
  assert.equal(describeDistrict('FIRDST', '7'), 'Fire District 7')
  assert.equal(describeDistrict('CEMDST', '2'), 'Cemetery District 2')
  assert.equal(describeDistrict('HOSPDST', '4'), 'Hospital District 4')
})

test('Island PUD, port and unincorporated codes and Lewis districts read as names', () => {
  // Live 2026-10-08 (#29): Camano Island (precinct County code 53029, TCA
  // 0590), Langley (PRT2025 'S WHIDBEY'), Coupeville ('COUPE'); Chehalis
  // (PUD2025 '1', LIB2025 'L').
  assert.equal(describeDistrict('PUDDST', '53029'), 'Snohomish County Public Utility District No. 1 (Camano Island)')
  assert.equal(describeDistrict('PORTDST', 'S WHIDBEY'), 'Port of South Whidbey Island')
  assert.equal(describeDistrict('PORTDST', 'COUPE'), 'Port of Coupeville')
  assert.equal(describeDistrict('UNINC', 'ISLAND'), 'Unincorporated Island County')
  assert.equal(layerLabel('UNINC'), 'Unincorporated County')
  assert.equal(describeDistrict('PUDDST', '1'), 'Public Utility District 1')
  assert.equal(describeDistrict('LIBDST', 'L'), 'Library District L')
})

test('Franklin port and commissioner codes and Clallam PUD membership read as names', () => {
  // Live 2026-10-08 (#29): 5600 N Rd 68, Pasco (Special_tax_districts/7
  // 'PoP3', Commissioner_Districts 'COM3'); Forks (PUDALL '1', PUDDST '3').
  assert.equal(describeDistrict('PORTDST', 'PoP3'), 'Port of Pasco Commissioner District 3')
  assert.equal(describeDistrict('PORTDST', 'PoK1'), 'Port of Kahlotus Commissioner District 1')
  const contests = [
    { scope: { layer: 'COUNTY_COUNCIL', county: 'franklin' }, district: 'Franklin County Commissioner District 3' },
  ]
  assert.equal(describeDistricts({ COUNTY_COUNCIL: 'COM2' }, { contests, county: 'franklin' })[0].text,
    'Franklin County Commissioner District 2')
  assert.equal(describeDistrict('PUDALL', '1'), 'Public Utility District No. 1')
  assert.deepEqual(describeDistricts({ PUDALL: '1', PUDDST: '3' }).map((d) => d.text),
    ['Public Utility District 3', 'Public Utility District No. 1'])
})

test('Douglas proposed Rimrock fire district reads as its name; other county fire codes stay hidden', () => {
  // Live 2026-10-08 (#30): All_Districts_Temporary/MapServer/4 FireNumber
  // '009' at 1005 Ashcroft Dr, Ephrata; '001' at 448 Belmont Pl, Ephrata,
  // where DOR FIRDST already names Fire District 1.
  assert.equal(layerLabel('PROPFIRDST'), 'Proposed fire protection district')
  assert.equal(describeDistrict('PROPFIRDST', '009'), 'Proposed Rimrock Meadows Fire Protection District No. 9')
  assert.equal(describeDistrict('PROPFIRDST', '001'), null)
  assert.equal(describeDistrict('PROPFIRDST', '000'), null)
  assert.deepEqual(describeDistricts({ FIRDST: '1', PROPFIRDST: '001' }).map((d) => d.text), ['Fire District 1'])
  assert.deepEqual(describeDistricts({ SCHDST: '209', PROPFIRDST: '009' }).map((d) => d.text),
    ['Proposed Rimrock Meadows Fire Protection District No. 9', 'School District 209'])
})

test('Kittitas Upper and Lower District Court read with the county name', () => {
  // Live 2026-10-08 (#31): Court_Districts court_district_name 'Lower
  // District Court' at 205 W 5th Ave, Ellensburg; 'Upper District Court' at
  // 719 E 3rd St, Cle Elum. Clallam's DISTCRT reads '1'/'2'.
  assert.equal(describeDistrict('DISTCRT', 'Lower District Court'), 'Lower Kittitas County District Court')
  assert.equal(describeDistrict('DISTCRT', 'Upper District Court'), 'Upper Kittitas County District Court')
  assert.equal(describeDistrict('DISTCRT', '1'), 'District Court 1')
  assert.equal(layerLabel('DISTCRT'), 'District Court')
  assert.deepEqual(describeDistricts({ CONGDST: '8', LEGDST: '13', DISTCRT: 'Upper District Court', CITY: 'Cle Elum' })
    .map((d) => d.text),
  ['City of Cle Elum', 'Congressional District 8', 'Legislative District 13', 'Upper Kittitas County District Court'])
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
