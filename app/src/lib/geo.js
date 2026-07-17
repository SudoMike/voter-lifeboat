// Address -> ballot context. Two steps:
// 1. US Census geocoder: address -> lat/lon + county, no key needed but no
//    CORS headers either, so it's proxied through our own /api/geocode.
// 2. Supported counties use their own District Adapter. King County currently
//    uses King County GIS layers on ArcGIS Online.

const KC = 'https://services.arcgis.com/Ej0PsM5Aw677QF1W/arcgis/rest/services'

const ADDRESS_POINTS = `${KC}/ADDRESS_POINT_642/FeatureServer/0/query`

const KING_COUNTY_FIPS = '53033'
const WASHINGTON_STATE_FIPS = '53'

// layer key -> [service, attribute that carries the value]
const KING_LAYERS = {
  CONGDST: ['CONGDST_AREA_405', 'CONGDST'],
  LEGDST: ['LEGDST_AREA_410', 'LEGDST'],
  KCCDST: ['KCCDST_AREA_185', 'KCCDST'],
  SCCDST: ['SCCDST_AREA_2237', 'SCCDST'],
  JUDDST: ['JUDDST_AREA_409', 'juddst'],
  FIRDST: ['FIRDST_AREA_407', 'FIRDST'],
  SCHDST: ['SCHDST_AREA_416', 'SCHDST'],
  CITY: ['CITYDST_AREA_337', 'NAME'],
}

const COUNTY_IDS = {
  '53011': 'clark',
  '53035': 'kitsap',
  [KING_COUNTY_FIPS]: 'king',
  '53053': 'pierce',
  '53061': 'snohomish',
  '53063': 'spokane',
  '53067': 'thurston',
}

export class GeoError extends Error {
  constructor(message, kind, details = {}) {
    super(message)
    this.kind = kind // 'no-match' | 'outside-wa' | 'unsupported-county' | 'network'
    this.details = details
  }
}

function countyFromMatch(match) {
  const county = match.geographies?.Counties?.[0]
  if (!county) return null
  const fips = `${county.STATE}${county.COUNTY}`
  return {
    id: COUNTY_IDS[fips] || null,
    fips,
    state: county.STATE,
    county: county.COUNTY,
    name: county.NAME || county.BASENAME || 'Unknown County',
  }
}

export async function geocode(address) {
  const url = `/api/geocode?address=${encodeURIComponent(address)}`
  let res
  try {
    res = await fetch(url)
  } catch {
    throw new GeoError('Could not reach the address lookup service.', 'network')
  }
  if (!res.ok) throw new GeoError('Address lookup failed.', 'network')
  const data = await res.json()
  const match = data?.result?.addressMatches?.[0]
  if (!match) throw new GeoError('No match for that address.', 'no-match')
  const county = countyFromMatch(match)
  if (!county || county.state !== WASHINGTON_STATE_FIPS) {
    throw new GeoError('That address is outside Washington State.', 'outside-wa')
  }
  return {
    x: match.coordinates.x,
    y: match.coordinates.y,
    matched: match.matchedAddress,
    county,
    geographies: match.geographies || {},
  }
}

// Type-ahead remains King County-only until a statewide address suggestion
// source is added. Users outside King County can still type and submit.
export async function suggestAddresses(query, { signal } = {}) {
  const q = query.trim()
  if (q.length < 5) return []
  const escaped = q.replace(/'/g, "''")
  const params = new URLSearchParams({
    where: `ADDR_FULL LIKE '${escaped}%'`,
    outFields: 'ADDR_FULL,CTYNAME,ZIP5',
    orderByFields: 'ADDR_FULL',
    returnDistinctValues: 'true',
    returnGeometry: 'false',
    resultRecordCount: '6',
    f: 'json',
  })
  const res = await fetch(`${ADDRESS_POINTS}?${params}`, { signal })
  if (!res.ok) return []
  const data = await res.json()
  if (data.error || !Array.isArray(data.features)) return []
  return data.features.map(({ attributes: a }) => {
    const city = a.CTYNAME || 'Unincorporated King County'
    return {
      full: a.ADDR_FULL,
      label: `${a.ADDR_FULL}, ${city}, WA${a.ZIP5 ? ` ${a.ZIP5}` : ''}`,
    }
  })
}

async function queryKingLayer(key, x, y) {
  const [service, attr] = KING_LAYERS[key]
  const params = new URLSearchParams({
    geometry: `${x},${y}`,
    geometryType: 'esriGeometryPoint',
    inSR: '4326',
    spatialRel: 'esriSpatialRelIntersects',
    outFields: attr,
    returnGeometry: 'false',
    f: 'json',
  })
  const res = await fetch(`${KC}/${service}/FeatureServer/0/query?${params}`)
  if (!res.ok) throw new GeoError(`District lookup failed (${key}).`, 'network', { layer: key })
  const data = await res.json()
  if (data.error) throw new GeoError(`District lookup failed (${key}).`, 'network', { layer: key })
  const feat = data.features?.[0]
  return feat ? String(feat.attributes[attr]).trim() : null
}

async function lookupKingDistricts(pt) {
  const keys = Object.keys(KING_LAYERS)
  const results = await Promise.allSettled(keys.map((k) => queryKingLayer(k, pt.x, pt.y)))
  const districts = {}
  const missingLayers = []
  keys.forEach((k, i) => {
    const r = results[i]
    if (r.status === 'fulfilled') {
      if (r.value != null) districts[k] = r.value
    } else {
      missingLayers.push(k)
    }
  })
  if (districts.CITY === 'King County') delete districts.CITY
  if (!districts.CONGDST && !districts.LEGDST && !missingLayers.length) {
    throw new GeoError('That point is outside King County voting districts.', 'unsupported-county')
  }
  return { districts, missingLayers }
}

function firstGeo(pt, key) {
  return pt.geographies?.[key]?.[0] || null
}

function trimDistrictNumber(value) {
  if (value == null) return null
  const n = String(value).match(/\d+/)?.[0]
  return n ? String(parseInt(n, 10)) : null
}

function lookupCensusDistricts(pt) {
  const congressional = firstGeo(pt, '119th Congressional Districts')
  const lower = firstGeo(pt, '2024 State Legislative Districts - Lower')
  const upper = firstGeo(pt, '2024 State Legislative Districts - Upper')
  const districts = {}
  const cd = trimDistrictNumber(congressional?.BASENAME || congressional?.CD119 || congressional?.GEOID)
  const ld = trimDistrictNumber(lower?.BASENAME || lower?.SLDL || upper?.BASENAME || upper?.SLDU)
  if (cd) districts.CONGDST = cd
  if (ld) districts.LEGDST = ld
  return districts
}

export async function lookupBallotContext(data, address) {
  const pt = await geocode(address)
  const countySupported = data.coverage?.supported_counties?.some((c) => c.id === pt.county.id)
  if (!countySupported) {
    if (!data.coverage?.statewide_complete) {
      throw new GeoError('This Washington county is not covered yet.', 'unsupported-county', { county: pt.county })
    }
    return {
      coverageStatus: 'statewide_only',
      county: pt.county,
      districts: {},
      missingLayers: [],
      matched: pt.matched,
    }
  }
  if (pt.county.id !== 'king') {
    return {
      coverageStatus: 'partial_county',
      county: pt.county,
      districts: lookupCensusDistricts(pt),
      missingLayers: ['county-local'],
      matched: pt.matched,
    }
  }
  const { districts, missingLayers } = await lookupKingDistricts(pt)
  return {
    coverageStatus: missingLayers.length ? 'partial_county' : 'full_county',
    county: pt.county,
    districts,
    missingLayers,
    matched: pt.matched,
  }
}

export function scopeMatches(scope, context) {
  if (!scope) return false
  if (scope.kind === 'STATEWIDE' || scope.layer === 'ALL') return true
  if (scope.kind === 'COUNTY') return context?.county?.id === scope.county
  if (scope.kind === 'DISTRICT') {
    if (context?.county?.id !== scope.county) return false
    const have = context?.districts?.[scope.layer]
    return have != null && String(have) === String(scope.value)
  }
  // Backward compatibility for older report links/data during development.
  const have = context?.districts?.[scope.layer]
  return have != null && String(have) === String(scope.value)
}
