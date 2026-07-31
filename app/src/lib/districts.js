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
  JUDDST: 'County Judicial District',
  DISTCRT: 'District Court',
  PORTDST: 'Port Commissioner District',
  PUDDST: 'Public Utility District',
  FIRDST: 'Fire District',
  FIRE_AUTH: 'Fire Authority',
  EMSDST: 'Emergency Medical District',
  SCHDST: 'School District',
  HOSPDST: 'Hospital District',
  LIBDST: 'Library District',
  PARKDST: 'Park District',
  CEMDST: 'Cemetery District',
  WATDST: 'Water District',
  PTBA: 'Public Transportation Benefit Area',
  AQUIFER: 'Aquifer Protection Area',
}

// Districts that decide which candidates a voter sees come first, then the
// special districts that only ever carry levies.
const ORDER = [
  'CITY', 'CONGDST', 'LEGDST', 'KCCDST', 'SCCDST', 'COUNTY_COUNCIL', 'JUDDST', 'DISTCRT',
  'PORTDST', 'PUDDST', 'FIRDST', 'FIRE_AUTH', 'EMSDST', 'SCHDST', 'HOSPDST', 'LIBDST',
  'PARKDST', 'CEMDST', 'WATDST', 'PTBA', 'AQUIFER',
]

// Presence flags, not district numbers. '1' is deliberately absent — it is a
// real district number nearly everywhere.
const PRESENCE_FLAGS = new Set(['yes', 'y', 'true'])

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
  if (bodyName) return `${bodyName} ${raw}`
  if (key === 'CITY') return `City of ${tidy(raw)}`
  const label = DISTRICT_LABELS[key]
  // An unconfigured layer is still worth showing; a bare key beats dropping it.
  if (!label) return `${key} ${tidy(raw)}`
  if (PRESENCE_FLAGS.has(raw.toLowerCase())) return label
  if (/^\d+$/.test(raw)) return `${label} ${raw}`
  // Codes that carry a service prefix ('SCC5') still have the number we want.
  const numbered = raw.match(/^[A-Za-z]+(\d+)$/)
  if (numbered) return `${label} ${numbered[1]}`
  // Values that already read as a proper name stand on their own.
  if (/district|authority|area|county/i.test(raw)) return tidy(raw)
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

export { DISTRICT_LABELS }
