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
  '53001': 'adams',
  '53003': 'asotin',
  '53005': 'benton',
  '53007': 'chelan',
  '53009': 'clallam',
  '53011': 'clark',
  '53013': 'columbia',
  '53015': 'cowlitz',
  '53017': 'douglas',
  '53019': 'ferry',
  '53021': 'franklin',
  '53023': 'garfield',
  '53025': 'grant',
  '53027': 'grays-harbor',
  '53029': 'island',
  '53031': 'jefferson',
  [KING_COUNTY_FIPS]: 'king',
  '53035': 'kitsap',
  '53037': 'kittitas',
  '53039': 'klickitat',
  '53041': 'lewis',
  '53043': 'lincoln',
  '53045': 'mason',
  '53047': 'okanogan',
  '53049': 'pacific',
  '53051': 'pend-oreille',
  '53053': 'pierce',
  '53055': 'san-juan',
  '53057': 'skagit',
  '53059': 'skamania',
  '53061': 'snohomish',
  '53063': 'spokane',
  '53065': 'stevens',
  '53067': 'thurston',
  '53069': 'wahkiakum',
  '53071': 'walla-walla',
  '53073': 'whatcom',
  '53075': 'whitman',
  '53077': 'yakima',
}

// WA Dept of Revenue statewide taxing-district boundaries (tax year 2025).
// Layer ids shift when DOR publishes a new tax year; re-verify annually.
const DOR_TAX_DISTRICTS =
  'https://webgis.dor.wa.gov/arcgis/rest/services/Programs/WADOR_PropertyTax/MapServer'

const COUNTY_LAYERS = {
  clark: [
    {
      key: 'COUNTY_COUNCIL',
      url: 'https://gis.clark.wa.gov/arcgisfed/rest/services/ClarkView_Public/BoardofCountyCouncilorsDistrict/MapServer/0/query',
      attr: 'BOCCDistrict',
    },
    {
      // Field is `District` (its alias is DISTRICT); responses key by field name.
      key: 'PUDDST',
      url: 'https://gis.clark.wa.gov/arcgisfed/rest/services/ClarkView_Public/CPUCommissionerDistrict/MapServer/0/query',
      attr: 'District',
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
      // Current five-district commissioner map (the services1 Current_Districts
      // layer is the stale pre-2022 three-district map — do not use it).
      key: 'COUNTY_COUNCIL',
      url: 'https://gismo.spokanecounty.org/arcgis/rest/services/OpenData/Boundary/MapServer/8/query',
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
      // Park & recreation districts; the Rosalia district spans the Whitman
      // County line and its Spokane-side value is 'ROSA'.
      key: 'PARKDST',
      url: `${DOR_TAX_DISTRICTS}/14/query`,
      attr: 'DISTATTRIB',
    },
    // No AQUIFER layer: the only public "Aquifer" service is the Spokane
    // Valley–Rathdrum Prairie aquifer, not the proposed West Plains APA, and
    // no official West Plains boundary is published. The APA measure stays
    // unscopable rather than scoped to the wrong geography.
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
  // Counties below were added from verified 2026 research: commissioner
  // district layers are county-published services; special-district layers use
  // the DOR statewide taxing-district boundaries (attrs verified by live
  // point queries on 2026-07-17).
  adams: [
    { key: 'CEMDST', url: `${DOR_TAX_DISTRICTS}/3/query`, attr: 'DISTATTRIB' },
    { key: 'PARKDST', url: `${DOR_TAX_DISTRICTS}/14/query`, attr: 'DISTATTRIB' },
  ],
  asotin: [
    { key: 'EMSDST', url: `${DOR_TAX_DISTRICTS}/6/query`, attr: 'DISTATTRIB' },
  ],
  benton: [
    { key: 'COUNTY_COUNCIL', url: 'https://services7.arcgis.com/NURlY7V8UHl6XumF/arcgis/rest/services/CommissionerDistrict/FeatureServer/6/query', attr: 'District' },
    { key: 'FIRDST', url: `${DOR_TAX_DISTRICTS}/7/query`, attr: 'DISTATTRIB' },
  ],
  chelan: [
    { key: 'COUNTY_COUNCIL', url: 'https://atlas.co.chelan.wa.us/arcgis/rest/services/PW/Commissioner_Districts/MapServer/0/query', attr: 'DIST_NO' },
  ],
  clallam: [
    { key: 'COUNTY_COUNCIL', url: 'https://services8.arcgis.com/noCZ2SM2C0rVag8y/arcgis/rest/services/Commissioner_Districts/FeatureServer/0/query', attr: 'COM_DIST' },
    { key: 'PUDDST', url: 'https://services8.arcgis.com/noCZ2SM2C0rVag8y/arcgis/rest/services/PUD_Commissioner_District_dissolve/FeatureServer/0/query', attr: 'Comm_Dist' },
    { key: 'FIRDST', url: `${DOR_TAX_DISTRICTS}/7/query`, attr: 'DISTATTRIB' },
  ],
  columbia: [
    { key: 'COUNTY_COUNCIL', url: 'https://services9.arcgis.com/zq1Ay6bxXC1T1CBk/arcgis/rest/services/CommissionerDistricts/FeatureServer/0/query', attr: 'District' },
  ],
  cowlitz: [
    { key: 'COUNTY_COUNCIL', url: 'https://gis.cowlitzwa.gov/ccserver/rest/services/County/Political_Administrative_Districts/MapServer/1/query', attr: 'DIST_ID' },
  ],
  douglas: [
    { key: 'FIRDST', url: `${DOR_TAX_DISTRICTS}/7/query`, attr: 'DISTATTRIB' },
    { key: 'HOSPDST', url: `${DOR_TAX_DISTRICTS}/11/query`, attr: 'DISTATTRIB' },
  ],
  ferry: [
    { key: 'COUNTY_COUNCIL', url: 'https://services8.arcgis.com/BBejpmYP0j5q6NLc/arcgis/rest/services/Political_Boundaries/FeatureServer/0/query', attr: 'DISTRICT' },
    { key: 'EMSDST', url: `${DOR_TAX_DISTRICTS}/6/query`, attr: 'DISTATTRIB' },
  ],
  franklin: [
    { key: 'COUNTY_COUNCIL', url: 'https://services3.arcgis.com/S61OMZovc3AIomN2/arcgis/rest/services/Districts/FeatureServer/8/query', attr: 'DISTRICT_CODE' },
  ],
  garfield: [],
  grant: [
    { key: 'COUNTY_COUNCIL', url: 'https://services2.arcgis.com/hQZvdtFxRzJpMtdS/arcgis/rest/services/County_Commissioner_Districts/FeatureServer/27/query', attr: 'DistrictNo' },
    { key: 'HOSPDST', url: `${DOR_TAX_DISTRICTS}/11/query`, attr: 'DISTATTRIB' },
  ],
  'grays-harbor': [
    { key: 'FIRDST', url: `${DOR_TAX_DISTRICTS}/7/query`, attr: 'DISTATTRIB' },
  ],
  island: [
    { key: 'COUNTY_COUNCIL', url: 'https://maps.islandcountywa.gov/arcgis/rest/services/Geocortex/Elections/MapServer/0/query', attr: 'COMM__DIST___' },
    { key: 'LIBDST', url: `${DOR_TAX_DISTRICTS}/12/query`, attr: 'DISTATTRIB' },
  ],
  jefferson: [
    { key: 'COUNTY_COUNCIL', url: 'https://gisweb.jeffcowa.us/server/rest/services/OpenData/OpenData/MapServer/26/query', attr: 'DISTID' },
    { key: 'CEMDST', url: `${DOR_TAX_DISTRICTS}/3/query`, attr: 'DISTATTRIB' },
    { key: 'FIRDST', url: `${DOR_TAX_DISTRICTS}/7/query`, attr: 'DISTATTRIB' },
  ],
  kittitas: [
    { key: 'COUNTY_COUNCIL', url: 'https://services.arcgis.com/eSnyVpqwqWBADfzp/arcgis/rest/services/Commissioner_Districts/FeatureServer/7/query', attr: 'commissioner_district_nbr' },
    { key: 'FIRDST', url: `${DOR_TAX_DISTRICTS}/7/query`, attr: 'DISTATTRIB' },
  ],
  klickitat: [
    { key: 'COUNTY_COUNCIL', url: 'https://geo.gartrellgroup.com/server/rest/services/Klickitat/Layers/MapServer/21/query', attr: 'NO' },
    { key: 'FIRDST', url: `${DOR_TAX_DISTRICTS}/7/query`, attr: 'DISTATTRIB' },
  ],
  lewis: [
    { key: 'COUNTY_COUNCIL', url: 'https://arcgis.lewiscountywa.gov/arcgispublic/rest/services/VotingTaxingDistricts/MapServer/0/query', attr: 'COMMISSION' },
    { key: 'FIRDST', url: `${DOR_TAX_DISTRICTS}/7/query`, attr: 'DISTATTRIB' },
  ],
  lincoln: [
    { key: 'CEMDST', url: `${DOR_TAX_DISTRICTS}/3/query`, attr: 'DISTATTRIB' },
  ],
  mason: [
    { key: 'COUNTY_COUNCIL', url: 'https://gis.masoncountywa.gov/arcgis/rest/services/MasonCoSite/Districts/MapServer/1/query', attr: 'DIST_ID' },
    { key: 'FIRDST', url: `${DOR_TAX_DISTRICTS}/7/query`, attr: 'DISTATTRIB' },
  ],
  okanogan: [
    { key: 'FIRDST', url: `${DOR_TAX_DISTRICTS}/7/query`, attr: 'DISTATTRIB' },
    { key: 'HOSPDST', url: `${DOR_TAX_DISTRICTS}/11/query`, attr: 'DISTATTRIB' },
  ],
  pacific: [
    { key: 'FIRDST', url: `${DOR_TAX_DISTRICTS}/7/query`, attr: 'DISTATTRIB' },
  ],
  'pend-oreille': [
    { key: 'COUNTY_COUNCIL', url: 'https://services1.arcgis.com/o3wuEYcU5N00WpI1/arcgis/rest/services/Commissioner_Districts___Open_Data/FeatureServer/0/query', attr: 'commission' },
    { key: 'HOSPDST', url: `${DOR_TAX_DISTRICTS}/11/query`, attr: 'DISTATTRIB' },
  ],
  'san-juan': [
    { key: 'SCHDST', url: `${DOR_TAX_DISTRICTS}/20/query`, attr: 'DISTATTRIB' },
  ],
  skagit: [
    { key: 'COUNTY_COUNCIL', url: 'https://geo.skagitcountywa.gov/server/rest/services/Districts/CommissionerDistrictWebMap/MapServer/5/query', attr: 'COMMDIST' },
    { key: 'FIRDST', url: `${DOR_TAX_DISTRICTS}/7/query`, attr: 'DISTATTRIB' },
    { key: 'HOSPDST', url: `${DOR_TAX_DISTRICTS}/11/query`, attr: 'DISTATTRIB' },
    { key: 'SCHDST', url: `${DOR_TAX_DISTRICTS}/20/query`, attr: 'DISTATTRIB' },
  ],
  skamania: [
    { key: 'COUNTY_COUNCIL', url: 'https://services3.arcgis.com/uKh72TYBlxpm42Cm/arcgis/rest/services/CommissionerDistrict/FeatureServer/0/query', attr: 'CommDist' },
    { key: 'WATDST', url: `${DOR_TAX_DISTRICTS}/22/query`, attr: 'DISTATTRIB' },
  ],
  stevens: [
    { key: 'COUNTY_COUNCIL', url: 'https://gis.stevenscountywa.gov/server/rest/services/AdministrativeBoundaries/MapServer/5/query', attr: 'districtid' },
    { key: 'FIRDST', url: `${DOR_TAX_DISTRICTS}/7/query`, attr: 'DISTATTRIB' },
  ],
  wahkiakum: [
    { key: 'COUNTY_COUNCIL', url: 'https://services5.arcgis.com/SQaKrZ90pTH1GKNW/arcgis/rest/services/Commissioner_Districts1/FeatureServer/1/query', attr: 'District_Number' },
  ],
  'walla-walla': [
    { key: 'COUNTY_COUNCIL', url: 'https://services8.arcgis.com/COL6rRPkF9w28VGX/arcgis/rest/services/Voting_Districts1/FeatureServer/52/query', attr: 'commis_dis' },
  ],
  whatcom: [
    { key: 'PORTDST', url: 'https://services3.arcgis.com/Qkk60MooanUNTUHp/arcgis/rest/services/2021ProposedPOBDistricts/FeatureServer/0/query', attr: 'Council' },
    { key: 'FIRDST', url: `${DOR_TAX_DISTRICTS}/7/query`, attr: 'DISTATTRIB' },
    { key: 'HOSPDST', url: `${DOR_TAX_DISTRICTS}/11/query`, attr: 'DISTATTRIB' },
  ],
  whitman: [
    { key: 'COUNTY_COUNCIL', url: 'https://services3.arcgis.com/eoLFybJXLOtInQXJ/arcgis/rest/services/Whitman_County_BOCC_Districts___Feb__2026_WFL1/FeatureServer/10/query', attr: 'BOCC' },
    { key: 'FIRDST', url: `${DOR_TAX_DISTRICTS}/7/query`, attr: 'DISTATTRIB' },
    { key: 'PARKDST', url: `${DOR_TAX_DISTRICTS}/14/query`, attr: 'DISTATTRIB' },
  ],
  yakima: [
    { key: 'COUNTY_COUNCIL', url: 'https://services3.arcgis.com/9Qz94N8Zml9hnG84/arcgis/rest/services/Commissioner_District_Election_2022/FeatureServer/0/query', attr: 'ID' },
    { key: 'FIRDST', url: `${DOR_TAX_DISTRICTS}/7/query`, attr: 'DISTATTRIB' },
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
  const value = readAttr(feat?.attributes, attr)
  return value == null || value === '' ? null : String(value).trim()
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
  const value = readAttr(feat?.attributes, layer.attr)
  return value == null || value === '' ? null : String(value).trim()
}

// ArcGIS responses key attributes by true field name, which can differ from
// the requested outFields in case (a field's alias often shadows its name in
// service metadata). Match case-insensitively so a config using the alias
// spelling still resolves.
function readAttr(attributes, attr) {
  if (!attributes) return null
  if (attr in attributes) return attributes[attr]
  const lower = attr.toLowerCase()
  const key = Object.keys(attributes).find((k) => k.toLowerCase() === lower)
  return key == null ? null : attributes[key]
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
    throw new GeoError('That point is outside King County voting districts.', 'no-districts')
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
  const layers = COUNTY_LAYERS[pt.county.id]
  const districts = lookupCensusDistricts(pt)
  const missingLayers = []
  // Every Washington address sits in a congressional and a legislative
  // district; their absence means the census response degraded (e.g. the
  // geography vintage rotated), not that the voter has none.
  if (!districts.CONGDST) missingLayers.push('CONGDST')
  if (!districts.LEGDST) missingLayers.push('LEGDST')
  // A county with no entry has no District Adapter yet; an empty entry means
  // the county's covered ballot needs no county-local layers.
  if (!layers) return { districts, missingLayers: [...missingLayers, 'county-local'] }
  const results = await Promise.allSettled(layers.map((layer) => queryArcgisLayer(layer, pt.x, pt.y)))
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
  const { districts, missingLayers } =
    pt.county.id === 'king' ? await lookupKingDistricts(pt) : await lookupCountyDistricts(pt)
  const packageIsFull = countyCoverage.coverage === 'full_county'
  return {
    coverageStatus: packageIsFull && !missingLayers.length ? 'full_county' : 'partial_county',
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

// For data-consistency tests: the app data's supported counties and district
// scopes must stay reachable through these maps.
export { COUNTY_IDS, COUNTY_LAYERS, KING_LAYERS }
