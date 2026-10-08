// Voter-facing names for the district layers geo.js resolves.
//
// The values these layers return are inconsistent by design, because each one
// comes from a different county's GIS service: some are numbers ('5'), some are
// already full names ('Everett School District 2'), some are codes ('SE',
// 'SCC5', 'TACOMA'), and a few are just flags ('YES' for the Pierce district
// court layer, which only reports whether the point is inside it at all).
// describeDistricts normalizes all four shapes into one readable line.

const DISTRICT_LABELS = {
  CONGDST: 'Congressional District',
  LEGDST: 'Legislative District',
  KCCDST: 'King County Council District',
  SCCDST: 'Seattle City Council District',
  COUNTY_COUNCIL: 'County Council District',
  JUDDST: 'King County District Court Electoral District',
  DISTCRT: 'District Court',
  KCDISTCRT: 'King County District Court, Southeast Electoral District',
  PORTDST: 'Port Commissioner District',
  PUDDST: 'Public Utility District',
  // Clallam PUDALL: membership of the whole PUD, a constant '1' (geo.js).
  PUDALL: 'Public Utility District No.',
  FIRDST: 'Fire District',
  FIRE_AUTH: 'Fire Authority',
  RFADST: 'Regional Fire Authority',
  // Douglas PROPFIRDST: a fire protection district being formed at this
  // election, read from the county's own fire layer (geo.js).
  PROPFIRDST: 'Proposed fire protection district',
  EMSDST: 'Emergency Medical District',
  // Asotin RURALEMSDST: Rural EMS District No. 2, read as a presence layer
  // from its DOR tax code areas (geo.js), a constant '2'.
  RURALEMSDST: 'Rural emergency medical services district',
  SCHDST: 'School District',
  HOSPDST: 'Hospital District',
  LIBDST: 'Library District',
  PARKDST: 'Park District',
  CEMDST: 'Cemetery District',
  WATDST: 'Water District',
  // San Juan SWDDST: the Lopez Solid Waste Disposal District, read as a
  // presence layer on DOR PRT2025 (geo.js), a constant 'LOPEZ'.
  SWDDST: 'Solid waste disposal district',
  PTBA: 'Public Transportation Benefit Area',
  AQUIFER: 'Aquifer Protection Area',
  UNINC: 'Unincorporated County',
}

// Layers whose values are codes for named places. King GIS's JUDDST layer
// returns the King County District Court electoral district as a code; King
// County Elections names the seats by the full name ('Southwest Electoral
// District'). JUDDST is a King-only layer (geo.js KING_LAYERS).
const NAMED_VALUES = {
  JUDDST: {
    NE: 'King County District Court, Northeast Electoral District',
    SE: 'King County District Court, Southeast Electoral District',
    SW: 'King County District Court, Southwest Electoral District',
    W: 'King County District Court, West Electoral District',
    SH: 'King County District Court, Shoreline Electoral District',
  },
  // Snohomish RFADST reads the WA DOR fire layer's RFA code; Thurston's reads
  // the county fire layer's CONSOL_NUM, filtered to the WTRFA polygons (geo.js).
  RFADST: {
    SCRFA: 'South Snohomish County Fire & Rescue Regional Fire Authority',
    FD01: 'West Thurston Regional Fire Authority',
  },
  // Benton PUDDST reads the Auditor's PrecinctSplits PUD_District (geo.js).
  PUDDST: {
    'BENTON PUD': 'Benton County Public Utility District',
    // Island PUDDST reads the Auditor's precinct layer's County code on the
    // Camano precincts, which Snohomish County PUD No. 1 serves (geo.js).
    '53029': 'Snohomish County Public Utility District No. 1 (Camano Island)',
  },
  // Island PORTDST reads WA DOR PRT2025 codes; Franklin's reads the county
  // layer's commissioner-district codes, Port of Pasco and Port of Kahlotus
  // (geo.js; matched upper-cased).
  PORTDST: {
    'S WHIDBEY': 'Port of South Whidbey Island',
    COUPE: 'Port of Coupeville',
    POP1: 'Port of Pasco Commissioner District 1',
    POP2: 'Port of Pasco Commissioner District 2',
    POP3: 'Port of Pasco Commissioner District 3',
    POK1: 'Port of Kahlotus Commissioner District 1',
    POK2: 'Port of Kahlotus Commissioner District 2',
    POK3: 'Port of Kahlotus Commissioner District 3',
    // San Juan PORTDST reads WA DOR PRT2025 codes (geo.js; #32).
    LOPEZ: 'Port of Lopez',
    ORCAS: 'Port of Orcas',
    'FRI HAR': 'Port of Friday Harbor',
  },
  // San Juan PARKDST reads WA DOR PKR2025 codes (geo.js; #32): Orcas Island's
  // and San Juan Island's park and recreation districts.
  PARKDST: {
    ORCAS: 'Orcas Island Park and Recreation District',
    'S J': 'San Juan Island Park and Recreation District',
  },
  // San Juan SWDDST is presence-only: geo.js reports 'LOPEZ' inside the
  // Port of Lopez polygon (the district's three Lopez precincts), nothing
  // elsewhere.
  SWDDST: {
    LOPEZ: 'Lopez Solid Waste Disposal District',
  },
  // Kittitas DISTCRT reads the Auditor's Court_Districts court_district_name
  // (geo.js), which leaves out the county; the ballot names the seats
  // 'Lower Kittitas County District Court' and 'Upper ...'.
  DISTCRT: {
    'LOWER DISTRICT COURT': 'Lower Kittitas County District Court',
    'UPPER DISTRICT COURT': 'Upper Kittitas County District Court',
  },
  // Island UNINC reads the DOR tax code area's county name outside the
  // incorporated tax code areas (geo.js).
  UNINC: {
    ISLAND: 'Unincorporated Island County',
  },
  // Douglas PROPFIRDST reads the county fire layer's FireNumber; only '009',
  // the proposed Rimrock Meadows district, is on the 2026 general ballot.
  PROPFIRDST: {
    '009': 'Proposed Rimrock Meadows Fire Protection District No. 9',
  },
  // Asotin RURALEMSDST is presence-only: geo.js reports '2' inside the
  // district's tax code areas (Anatone and Rural Asotin), nothing elsewhere.
  RURALEMSDST: {
    2: 'Asotin County Rural EMS District No. 2',
  },
  // Spokane FIRDST reads the county fire layer's NAME (geo.js). Districts
  // read 'Fire District 9'; these other polygons are cities with their own
  // department, towns served by contract, and land outside every district.
  FIRDST: {
    'SPOKANE VALLEY FIRE': 'Spokane Valley Fire Department (Fire District 1)',
    'CITY OF SPOKANE': 'City of Spokane Fire Department',
    CHENEY: 'Cheney Fire Department',
    'AIRWAY HEIGHTS': 'Airway Heights Fire Department',
    ROCKFORD: 'Town of Rockford (fire service by contract)',
    SPANGLE: 'Town of Spangle (fire service by contract)',
    'CONTRACT SERVICE': 'Fire service by contract (no fire district)',
    UNSERVED: 'No fire district',
  },
}

// Districts that decide which candidates a voter sees come first, then the
// special districts that only ever carry levies.
const ORDER = [
  'CITY', 'CONGDST', 'LEGDST', 'KCCDST', 'SCCDST', 'COUNTY_COUNCIL', 'JUDDST', 'DISTCRT', 'KCDISTCRT',
  'PORTDST', 'PUDDST', 'PUDALL', 'FIRDST', 'FIRE_AUTH', 'RFADST', 'PROPFIRDST', 'EMSDST', 'RURALEMSDST',
  'SCHDST', 'HOSPDST', 'LIBDST', 'PARKDST', 'CEMDST', 'WATDST', 'SWDDST', 'PTBA', 'AQUIFER', 'UNINC',
]

// Layers that show only their NAMED_VALUES. Douglas's county fire layer also
// carries the existing fire districts ('001', '002', ...) and '000' for no
// district; DOR's FIRDST already names those, so repeating them would show a
// voter the same district twice under a "proposed" label.
const NAMED_ONLY = new Set(['PROPFIRDST'])

// Presence flags, not district numbers. '1' is deliberately absent — it is a
// real district number nearly everywhere.
const PRESENCE_FLAGS = new Set(['yes', 'y', 'true'])
// Their negatives: Pierce's Election_Precincts flags (DISTCRT, KCDISTCRT,
// PTBA) read 'NO' outside the district, which names no district at all.
const ABSENCE_FLAGS = new Set(['no', 'false'])

// Washington counties are governed by a council in some places and a board of
// commissioners in others, so there is no single correct label for
// COUNTY_COUNCIL. The shipped contest data carries the right local name
// ('Adams County Commissioner District 3'), so borrow the wording from it and
// re-number it for the voter. Read from the full contest list rather than the
// voter's ballot: county seats are staggered, so the seat covering a given
// voter is often not up this cycle.
const NAMED_BY_CONTEST = new Set(['COUNTY_COUNCIL'])

// 'Adams County Commissioner District 3' -> 'Adams County Commissioner District'
// Thurston spells it 'District No. 3', so the number part is optional-prefixed.
const DISTRICT_NAME = /^(.*\bDistrict)(?:\s+No\.)?\s+\d+$/i

function bodyNameFor(key, countyId, contests) {
  if (!NAMED_BY_CONTEST.has(key) || !countyId) return null
  for (const c of contests) {
    if (c?.scope?.layer !== key || c.scope.county !== countyId) continue
    const m = DISTRICT_NAME.exec(String(c.district || '').trim())
    if (m) return m[1]
  }
  return null
}

function tidy(value) {
  if (/[a-z]/.test(value)) return value // already mixed case — leave it alone
  if (value.length <= 3) return value // directional or single-letter codes: SE, NE, L
  return value.replace(/\w\S*/g, (w) => w[0].toUpperCase() + w.slice(1).toLowerCase())
}

export function describeDistrict(key, value, bodyName = null) {
  const raw = String(value ?? '').trim()
  if (!raw) return null
  // Franklin's commissioner layer reads 'COM3'; the contest says 'District 3'.
  if (bodyName) return `${bodyName} ${raw.match(/^[A-Za-z]+(\d+)$/)?.[1] ?? raw}`
  if (key === 'CITY') return `City of ${tidy(raw)}`
  const named = NAMED_VALUES[key]?.[raw.toUpperCase()]
  if (named) return named
  if (NAMED_ONLY.has(key)) return null
  const label = DISTRICT_LABELS[key]
  // An unconfigured layer is still worth showing; a bare key beats dropping it.
  if (!label) return `${key} ${tidy(raw)}`
  if (PRESENCE_FLAGS.has(raw.toLowerCase())) return label
  if (ABSENCE_FLAGS.has(raw.toLowerCase())) return null
  // Kitsap's school layer numbers Bremerton '100-C'; keep its suffix as printed.
  if (/^\d+(-[A-Za-z])?$/.test(raw)) return `${label} ${raw}`
  // Codes that carry a service prefix ('SCC5') still have the number we want.
  const numbered = raw.match(/^[A-Za-z]+(\d+)$/)
  if (numbered) return `${label} ${numbered[1]}`
  // Spokane's school layer names districts 'Spokane #81'.
  const hashed = key === 'SCHDST' && raw.match(/^(.*\S)\s*#(\d+)$/)
  if (hashed) return `${hashed[1]} School District No. ${hashed[2]}`
  // Values that already read as a proper name stand on their own (Pierce's
  // school field also reads 'YELM COMMUNITY SCHOOLS').
  if (/district|authority|area|county|schools$/i.test(raw)) return tidy(raw)
  // Thurston's school layer gives the bare place name ('NORTH THURSTON').
  if (key === 'SCHDST' && /^[A-Za-z][A-Za-z .'-]*$/.test(raw)) return `${tidy(raw)} ${label}`
  return `${label} ${tidy(raw)}`
}

// contests: the full shipped contest list; county: the voter's county id. Both
// are used only to name the layers in NAMED_BY_CONTEST correctly.
export function describeDistricts(districts = {}, { contests = [], county = null } = {}) {
  const rank = (k) => (ORDER.indexOf(k) < 0 ? ORDER.length : ORDER.indexOf(k))
  return Object.keys(districts)
    .sort((a, b) => rank(a) - rank(b) || a.localeCompare(b))
    .map((key) => ({ key, text: describeDistrict(key, districts[key], bodyNameFor(key, county, contests)) }))
    .filter((d) => d.text)
}

// Names for the layer ids a ballot context lists in missingLayers, for the
// partial-coverage banner and the Ballot Brief. 'county-local' stands for a
// county with no District Adapter at all (geo.js).
const LAYER_ONLY_LABELS = { CITY: 'City', 'county-local': 'local county districts' }

export function layerLabel(key) {
  return LAYER_ONLY_LABELS[key] || DISTRICT_LABELS[key] || key
}

export { DISTRICT_LABELS, ORDER as DISTRICT_ORDER }
