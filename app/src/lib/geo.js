// Address -> districts. Two steps:
// 1. US Census geocoder: address -> lat/lon + county, no key needed but no
//    CORS headers either, so it's proxied through our own /api/geocode
//    (see server.js) rather than fetched directly from the browser.
// 2. King County GIS layers on ArcGIS Online: point-in-polygon per district,
//    CORS-enabled, fetched straight from the browser.
// The address itself goes ONLY to the Census geocoder (via our proxy); only
// coordinates go to the district layers.

const KC = 'https://services.arcgis.com/Ej0PsM5Aw677QF1W/arcgis/rest/services'

// layer key -> [service, attribute that carries the value]
const LAYERS = {
  CONGDST: ['CONGDST_AREA_405', 'CONGDST'],
  LEGDST: ['LEGDST_AREA_410', 'LEGDST'],
  KCCDST: ['KCCDST_AREA_185', 'KCCDST'],
  SCCDST: ['SCCDST_AREA_2237', 'SCCDST'],
  JUDDST: ['JUDDST_AREA_409', 'juddst'],
  FIRDST: ['FIRDST_AREA_407', 'FIRDST'],
  SCHDST: ['SCHDST_AREA_416', 'SCHDST'],
  CITY: ['CITYDST_AREA_337', 'NAME'],
}

export class GeoError extends Error {
  constructor(message, kind) {
    super(message)
    this.kind = kind // 'no-match' | 'outside-kc' | 'network'
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
  const county = match.geographies?.Counties?.[0]
  if (county && !(county.STATE === '53' && county.COUNTY === '033')) {
    throw new GeoError('That address is outside King County.', 'outside-kc')
  }
  return { x: match.coordinates.x, y: match.coordinates.y, matched: match.matchedAddress }
}

async function queryLayer(key, x, y) {
  const [service, attr] = LAYERS[key]
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
  if (!res.ok) throw new GeoError(`District lookup failed (${key}).`, 'network')
  const data = await res.json()
  if (data.error) throw new GeoError(`District lookup failed (${key}).`, 'network')
  const feat = data.features?.[0]
  return feat ? String(feat.attributes[attr]).trim() : null
}

export async function lookupDistricts(address) {
  const pt = await geocode(address)
  const keys = Object.keys(LAYERS)
  const values = await Promise.all(keys.map((k) => queryLayer(k, pt.x, pt.y)))
  const districts = {}
  keys.forEach((k, i) => {
    if (values[i] != null) districts[k] = values[i]
  })
  // King County GIS "King County" means unincorporated; don't treat as a city
  if (districts.CITY === 'King County') delete districts.CITY
  if (!districts.CONGDST || !districts.LEGDST) {
    throw new GeoError('That point is outside King County voting districts.', 'outside-kc')
  }
  return { districts, matched: pt.matched }
}

export function scopeMatches(scope, districts) {
  if (scope.layer === 'ALL') return true
  const have = districts[scope.layer]
  return have != null && String(have) === String(scope.value)
}
