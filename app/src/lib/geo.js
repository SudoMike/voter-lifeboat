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

const COUNTY_LAYERS = {
  clark: [
    {
      key: 'COUNTY_COUNCIL',
      url: 'https://gis.clark.wa.gov/arcgisfed/rest/services/ClarkView_Public/BoardofCountyCouncilorsDistrict/MapServer/0/query',
      attr: 'BOCCDistrict',
    },
    {
      key: 'PUDDST',
      url: 'https://gis.clark.wa.gov/arcgisfed/rest/services/ClarkView_Public/CPUCommissionerDistrict/MapServer/0/query',
      attr: 'DISTRICT',
    },
    {
      key: 'FIRDST',
      url: 'https://gis.clark.wa.gov/arcgisfed/rest/services/ClarkView_Public/FireDistrictBoundary/MapServer/0/query',
      attr: 'FIREDST',
    },
  ],
  kitsap: [
    {
      key: 'COUNTY_COUNCIL',
      url: 'https://services6.arcgis.com/qt3UCV9x5kB4CwRA/arcgis/rest/services/County_Commissioner_District_Outlines/FeatureServer/0/query',
      attr: 'DISTRICT',
    },
    {
      key: 'FIRDST',
      url: 'https://services6.arcgis.com/qt3UCV9x5kB4CwRA/arcgis/rest/services/Fire_District_Outlines/FeatureServer/0/query',
      attr: 'DISTRICT',
    },
  ],
  pierce: [
    {
      key: 'COUNTY_COUNCIL',
      url: 'https://services2.arcgis.com/1UvBaQ5y1ubjUPmd/arcgis/rest/services/Pierce_County_Council_Districts/FeatureServer/0/query',
      attr: 'District_Number',
    },
    {
      key: 'FIRDST',
      url: 'https://services2.arcgis.com/1UvBaQ5y1ubjUPmd/arcgis/rest/services/Fire_Districts/FeatureServer/0/query',
      attr: 'FIRE_DIS',
    },
    {
      key: 'DISTCRT',
      url: 'https://services2.arcgis.com/1UvBaQ5y1ubjUPmd/arcgis/rest/services/Election_Precincts/FeatureServer/0/query',
      attr: 'PC_DISTRICT',
    },
  ],
  snohomish: [
    {
      key: 'PUDDST',
      url: 'https://gis.snoco.org/sis/rest/services/Districts/Districts_and_Boundaries/MapServer/22/query',
      attr: 'District',
    },
    {
      key: 'SCHDST',
      url: 'https://services6.arcgis.com/z6WYi9VRHfgwgtyW/arcgis/rest/services/School_Districts/FeatureServer/0/query',
      attr: 'District',
    },
    {
      key: 'FIRDST',
      url: 'https://services6.arcgis.com/z6WYi9VRHfgwgtyW/arcgis/rest/services/Fire_Districts_and_RFAs_in_Snohomish_County/FeatureServer/1/query',
      attr: 'District',
    },
    {
      key: 'HOSPDST',
      url: 'https://services6.arcgis.com/z6WYi9VRHfgwgtyW/arcgis/rest/services/Snohomish_County_Hospital_Districts/FeatureServer/0/query',
      attr: 'District',
    },
    {
      key: 'LIBDST',
      url: 'https://gis.snoco.org/sis/rest/services/Districts/Districts_and_Boundaries/MapServer/16/query',
      attr: 'District',
    },
  ],
  spokane: [
    {
      key: 'COUNTY_COUNCIL',
      url: 'https://services1.arcgis.com/ozNll27nt9ZtPWOn/arcgis/rest/services/Current_Districts/FeatureServer/1/query',
      attr: 'DISTNUM',
    },
    {
      key: 'PTBA',
      url: 'https://services9.arcgis.com/EULiDWk01e6LlXCu/arcgis/rest/services/PTBA/FeatureServer/18/query',
      attr: 'PTBA',
    },
    {
      key: 'LIBDST',
      url: 'https://gismo.spokanecounty.org/arcgis/rest/services/OpenData/Boundary/MapServer/5/query',
      attr: 'NAME',
    },
    {
      key: 'AQUIFER',
      url: 'https://services.arcgis.com/3PDwyTturHqnGCu0/arcgis/rest/services/Aquifer/FeatureServer/0/query',
      attr: 'AQUIFER',
    },
  ],
  thurston: [
    {
      key: 'COUNTY_COUNCIL',
      url: 'https://tconline.co.thurston.wa.us/server/rest/services/Thurston_CommissionerDistricts/FeatureServer/0/query',
      attr: 'CommissionerDistrictNumber',
    },
    {
      key: 'PUDDST',
      url: 'https://tconline.co.thurston.wa.us/server/rest/services/Common_Layers/Jurisdictions/FeatureServer/15/query',
      attr: 'CommissionerDistrictNumber',
    },
    {
      key: 'FIRDST',
      url: 'https://tconline.co.thurston.wa.us/server/rest/services/ThurstonExt/Thurston_FireDistricts_TCOMM/FeatureServer/0/query',
      attr: 'DISPATCH_G',
    },
    {
      key: 'FIRE_AUTH',
      url: 'https://tconline.co.thurston.wa.us/server/rest/services/ThurstonExt/Thurston_FireDistricts_TCOMM/FeatureServer/0/query',
      attr: 'CONSOL_DIS',
    },
  ],
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

async function queryArcgisLayer(layer, x, y) {
  const params = new URLSearchParams({
    geometry: `${x},${y}`,
    geometryType: 'esriGeometryPoint',
    inSR: '4326',
    spatialRel: 'esriSpatialRelIntersects',
    outFields: layer.attr,
    returnGeometry: 'false',
    f: 'json',
  })
  const res = await fetch(`${layer.url}?${params}`)
  if (!res.ok) throw new GeoError(`District lookup failed (${layer.key}).`, 'network', { layer: layer.key })
  const data = await res.json()
  if (data.error) throw new GeoError(`District lookup failed (${layer.key}).`, 'network', { layer: layer.key })
  const feat = data.features?.[0]
  const value = feat?.attributes?.[layer.attr]
  return value == null || value === '' ? null : String(value).trim()
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
  const place = firstGeo(pt, 'Incorporated Places')
  const districts = {}
  const cd = trimDistrictNumber(congressional?.BASENAME || congressional?.CD119 || congressional?.GEOID)
  const ld = trimDistrictNumber(lower?.BASENAME || lower?.SLDL || upper?.BASENAME || upper?.SLDU)
  const city = (place?.BASENAME || place?.NAME || '').replace(/\s+city$/i, '').trim()
  if (cd) districts.CONGDST = cd
  if (ld) districts.LEGDST = ld
  if (city) districts.CITY = city
  return districts
}

async function lookupCountyDistricts(pt) {
  const layers = COUNTY_LAYERS[pt.county.id] || []
  const districts = lookupCensusDistricts(pt)
  if (!layers.length) return { districts, missingLayers: ['county-local'] }
  const results = await Promise.allSettled(layers.map((layer) => queryArcgisLayer(layer, pt.x, pt.y)))
  const missingLayers = []
  layers.forEach((layer, i) => {
    const r = results[i]
    if (r.status === 'fulfilled') {
      if (r.value != null) districts[layer.key] = r.value
    } else {
      missingLayers.push(layer.key)
    }
  })
  return { districts, missingLayers }
}

export async function lookupBallotContext(data, address) {
  const pt = await geocode(address)
  const countyCoverage = data.coverage?.supported_counties?.find((c) => c.id === pt.county.id)
  const countySupported = Boolean(countyCoverage)
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
    const { districts, missingLayers } = await lookupCountyDistricts(pt)
    const packageIsFull = countyCoverage.coverage === 'full_county'
    return {
      coverageStatus: packageIsFull && !missingLayers.length ? 'full_county' : 'partial_county',
      county: pt.county,
      districts,
      missingLayers,
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
