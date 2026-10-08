// Address -> ballot context. Two steps:
// 1. US Census geocoder: address -> lat/lon + county, no key needed but no
//    CORS headers either, so it's proxied through our own /api/geocode.
// 2. Supported counties use their own District Adapter. King County currently
//    uses King County GIS layers on ArcGIS Online, plus the WA DOR cemetery
//    district layer.

const KC = 'https://services.arcgis.com/Ej0PsM5Aw677QF1W/arcgis/rest/services'

const ADDRESS_POINTS = `${KC}/ADDRESS_POINT_642/FeatureServer/0/query`

const KING_COUNTY_FIPS = '53033'
const WASHINGTON_STATE_FIPS = '53'

// WA Dept of Revenue statewide taxing-district boundaries (tax year 2025).
// Layer ids shift when DOR publishes a new tax year; re-verify annually
// (MapServer?f=json lists them). Re-verified 2026-10-08 (#20): tax year 2025
// is still the newest group (layer 0), and every id used below answered a
// live point query with the expected DISTATTRIB: 3 CEM2025 (Vashon '1'),
// 6 EMS2025 (Asotin '1'), 7 FIR2025 (West Richland, Benton '4'), 11 HSP2025
// (Newport, Pend Oreille '1'), 12 LIB2025 (Coupeville, Island 'L'), 14
// PKR2025, park and recreation districts (Washtucna, Adams '2'; 15 PRK2025 is
// a different layer), 20 SCH2025 (Friday Harbor, San Juan '149'), 22 WAT2025
// (Skamania '1'). Table: docs/county-wave-playbook.md. #29 added 16 PRT2025
// (Langley, Island 'S WHIDBEY'), 17 PUD2025 (Chehalis, Lewis '1') and 23
// TCA2025, tax code areas (Camano Island, Island '0590'), each re-listed in
// MapServer?f=json on 2026-10-08.
const DOR_TAX_DISTRICTS =
  'https://webgis.dor.wa.gov/arcgis/rest/services/Programs/WADOR_PropertyTax/MapServer'

// layer key -> [King GIS service name, or a full layer URL; attribute that
// carries the value]
const KING_LAYERS = {
  CONGDST: ['CONGDST_AREA_405', 'CONGDST'],
  LEGDST: ['LEGDST_AREA_410', 'LEGDST'],
  KCCDST: ['KCCDST_AREA_185', 'KCCDST'],
  SCCDST: ['SCCDST_AREA_2237', 'SCCDST'],
  JUDDST: ['JUDDST_AREA_409', 'juddst'],
  FIRDST: ['FIRDST_AREA_407', 'FIRDST'],
  SCHDST: ['SCHDST_AREA_416', 'SCHDST'],
  CITY: ['CITYDST_AREA_337', 'NAME'],
  // King County Cemetery District No. 1 (Vashon-Maury Island). King GIS
  // publishes no cemetery layer, so this reads the DOR layer the other
  // counties use. It has exactly one King feature, DISTATTRIB '1'
  // (raw/gis/dor-cemdst-king.json in the general's King package); a live point
  // query at 10105 SW Bank Rd, Vashon returned '1' and downtown Seattle none
  // (2026-10-08).
  CEMDST: [`${DOR_TAX_DISTRICTS}/3`, 'DISTATTRIB'],
}

function kingLayerQueryUrl(service) {
  return service.startsWith('https://') ? `${service}/query` : `${KC}/${service}/FeatureServer/0/query`
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
    {
      // School district number (an integer field; String() makes it '119').
      // Live 2026-10-08 (#22): 109 SW 1st St, Battle Ground -> 119 (DOR
      // SCH2025 DISTATTRIB '119' agrees); 1300 Franklin St, Vancouver -> 37.
      key: 'SCHDST',
      url: 'https://gis.clark.wa.gov/arcgisfed/rest/services/ClarkView_Public/SchoolDistrict/MapServer/0/query',
      attr: 'SCHDST',
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
    {
      // Kitsap County GIS school district outlines, district number as text
      // ('100-C' Bremerton, '303', '400', '401', '402', '403'). Live
      // 2026-10-08 (#22): 2689 Hoover Ave SE and 1700 SE Mile Hill Dr, Port
      // Orchard -> '402' (DOR SCH2025 '402' agrees); 345 6th St, Bremerton ->
      // '100-C'; 15376 Seabeck Hwy NW, Seabeck -> '401'.
      key: 'SCHDST',
      url: 'https://services6.arcgis.com/qt3UCV9x5kB4CwRA/arcgis/rest/services/School_District_Outlines/FeatureServer/0/query',
      attr: 'DISTRICT',
    },
  ],
  // Re-verified 2026-10-08 (#20) at 930 Tacoma Ave S: District_Number 4,
  // FIRE_DIS 'TACOMA', PC_DISTRICT 'YES'. DISTCRT, KCDISTCRT, PTBA and SCHDST
  // all read the same Election_Precincts feature; each key is its own query
  // (the adapter has no shared-layer read), four small requests in parallel.
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
    {
      // King County District Court, Southeast Electoral District, which takes
      // in Pierce-side Auburn. KING_DISTRICT is 'YES'/'NO'. Live 2026-10-08
      // (#21): 1402 Lake Tapps Pkwy SE, Auburn -> 'YES' (PC_DISTRICT 'NO');
      // 930 Tacoma Ave S -> 'NO'.
      key: 'KCDISTCRT',
      url: 'https://services2.arcgis.com/1UvBaQ5y1ubjUPmd/arcgis/rest/services/Election_Precincts/FeatureServer/0/query',
      attr: 'KING_DISTRICT',
    },
    {
      // Pierce Transit's public transportation benefit area, 'YES'/'NO'.
      // Live 2026-10-08 (#21): 930 Tacoma Ave S -> 'YES'; 121 Washington St,
      // South Prairie -> 'NO'.
      key: 'PTBA',
      url: 'https://services2.arcgis.com/1UvBaQ5y1ubjUPmd/arcgis/rest/services/Election_Precincts/FeatureServer/0/query',
      attr: 'PIERCE_TRANSIT',
    },
    {
      // School district by its full name. Live 2026-10-08 (#21): 1402 Lake
      // Tapps Pkwy SE, Auburn -> 'AUBURN SCHOOL DISTRICT NO. 408'; 930 Tacoma
      // Ave S -> 'TACOMA SCHOOL DISTRICT NO. 10'; (-122.55764, 46.93652),
      // precinct 02095 -> 'YELM COMMUNITY SCHOOLS'.
      key: 'SCHDST',
      url: 'https://services2.arcgis.com/1UvBaQ5y1ubjUPmd/arcgis/rest/services/Election_Precincts/FeatureServer/0/query',
      attr: 'SCHOOL',
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
    {
      // South Snohomish County Fire & Rescue RFA (South County Fire). The
      // county's FIRDST layer above has no polygon for it. DOR FIR2025 has,
      // but mixes fire districts and RFAs: its Snohomish DISTATTRIB values
      // are district numbers ('10', '26 NB') and RFA codes ('SCRFA', 'SRF',
      // 'NCRFA', 'MARFA', '12 MARFA', 'NCRFA/19B'). `where` keeps only the RFA
      // a shipped scope names, so no fire-district number is shown to a voter
      // as an RFA. Live 2026-10-08 (#21), unfiltered: 19100 44th Ave W,
      // Lynnwood -> 'SCRFA'; 806 W Main St, Monroe -> 'SRF'; 2930 Wetmore
      // Ave, Everett -> no feature. Filtered: Lynnwood 'SCRFA', Monroe none.
      key: 'RFADST',
      url: `${DOR_TAX_DISTRICTS}/7/query`,
      attr: 'DISTATTRIB',
      where: "DISTATTRIB = 'SCRFA'",
    },
    {
      // District Court electoral districts. The Auditor's Office (Elections)
      // maintains this layer from voter precinct portions joined with VoteWA
      // district data (item aa298eefc0ee4cdb9bfe8d2b02f574d0); four polygons,
      // District 'Cascade District Court', 'Everett District Court',
      // 'Evergreen District Court', 'South District Court'. The county's
      // Districts_and_Boundaries/MapServer/41 copy agreed at every check
      // point. Live 2026-10-08 (#27): 2930 Wetmore Ave, Everett -> 'Everett
      // District Court'; 806 W Main St, Monroe -> 'Evergreen District Court';
      // 19100 44th Ave W, Lynnwood -> 'South District Court'.
      key: 'DISTCRT',
      url: 'https://services6.arcgis.com/z6WYi9VRHfgwgtyW/arcgis/rest/services/Court_Districts/FeatureServer/0/query',
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
      // School districts. DISTRCTNAME is the name the general's measures are
      // scoped to ('Spokane #81', 'Central Valley #356'). Live 2026-10-08
      // (#21): 808 W Spokane Falls Blvd, Spokane -> 'Spokane #81'; 22710 E
      // Country Vista Dr, Liberty Lake -> 'Central Valley #356'; 3801 E
      // Farwell Rd, Mead -> 'Mead #354'. DOR SCH2025 agrees (81, 356, 354).
      key: 'SCHDST',
      url: 'https://gismo.spokanecounty.org/arcgis/rest/services/OpenData/Boundary/MapServer/6/query',
      attr: 'DISTRCTNAME',
    },
    {
      // Fire districts. NAME, not CODE or DISTRICTID: towns that contract
      // for fire service carry their own NAME with the district's CODE
      // (Rockford '11', Spangle '03'), and the City of Cheney polygon carries
      // DISTRICTID 32103 like Fire District 3. Cities with their own fire
      // department read 'City of Spokane', 'Cheney', 'Airway Heights';
      // outside every district, 'Unserved'. Live 2026-10-08 (#21): 3801 E
      // Farwell Rd, Mead -> 'Fire District 9'; 808 W Spokane Falls Blvd ->
      // 'City of Spokane'; 22710 E Country Vista Dr -> 'Spokane Valley Fire'.
      // Known gap: the Town of Fairfield (102 E Main St) is 'Fire District 2'
      // here but outside FD 2 in DOR FIR2025 (layer 7).
      key: 'FIRDST',
      url: 'https://gismo.spokanecounty.org/arcgis/rest/services/OpenData/Boundary/MapServer/1/query',
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
    {
      // West Thurston Regional Fire Authority (former Fire Districts 1,
      // Rochester, and 11, Littlerock). The fire layer above splits it into
      // two polygons (DISPATCH_G 'FD01'/'FD11', CONSOL_DIS 'WTRFA - South
      // Btn'/'WTRFA - North Btn'); both carry CONSOL_NUM 'FD01' and no other
      // polygon does. Every polygon has a CONSOL_NUM ('FD03' Lacey, 'OFD'
      // Olympia), so `where` keeps only the WTRFA polygons and no fire
      // district reads as an RFA. Live 2026-10-08 (#22): 18346 Albany St SW, Rochester
      // and 10828 Littlerock Rd SW, Olympia -> 'FD01'; 420 College St SE,
      // Lacey (FIRDST 'FD03'), 105 W Yelm Ave, Yelm and 601 4th Ave E,
      // Olympia -> no feature.
      key: 'RFADST',
      url: 'https://tconline.co.thurston.wa.us/server/rest/services/ThurstonExt/Thurston_FireDistricts_TCOMM/FeatureServer/0/query',
      attr: 'CONSOL_NUM',
      where: "CONSOL_DIS LIKE 'WTRFA%'",
    },
    {
      // Thurston County school districts by name (Common_Layers/Jurisdictions
      // layer 10). Live 2026-10-08 (#22): 105 W Yelm Ave, Yelm -> 'YELM' (DOR
      // SCH2025 '2', Yelm Community Schools No. 2); 601 4th Ave E, Olympia ->
      // 'OLYMPIA'; 420 College St SE, Lacey -> 'NORTH THURSTON'; 18346 Albany
      // St SW, Rochester -> 'ROCHESTER'; 10828 Littlerock Rd SW -> 'TUMWATER'.
      key: 'SCHDST',
      url: 'https://tconline.co.thurston.wa.us/server/rest/services/Common_Layers/Jurisdictions/FeatureServer/10/query',
      attr: 'SchoolDistrictName',
    },
  ],
  // Counties below were added from verified 2026 research: commissioner
  // district layers are county-published services; special-district layers use
  // the DOR statewide taxing-district boundaries (attrs verified by live
  // point queries on 2026-07-17; DOR layer ids re-verified 2026-10-08, see
  // DOR_TAX_DISTRICTS).
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
    {
      // Benton County PUD, from the Auditor's precinct layer (#28). The PUD
      // excludes Richland and most of West Richland, so DOR PUD2025's single
      // countywide Benton polygon is not used. PUD_District reads 'Benton
      // PUD', null, the string '<Null>' (Richland precinct 6322.1), or 'Yes'
      // (West Richland precinct 4017 alone, which cast no 2024 PUD vote);
      // `where` keeps only 'Benton PUD', so the last two read as no district
      // and the PUD race stays hidden there. Live 2026-10-08: 210 W 6th Ave,
      // Kennewick and 1009 Dale Ave, Benton City -> 'Benton PUD'; 625 Swift
      // Blvd, Richland and 3801 W Van Giesen St, West Richland -> null.
      key: 'PUDDST',
      url: 'https://services7.arcgis.com/NURlY7V8UHl6XumF/arcgis/rest/services/PrecinctSplits/FeatureServer/6/query',
      attr: 'PUD_District',
      where: "PUD_District = 'Benton PUD'",
    },
    {
      // WA DOR SCH2025 school district number (#28). Live 2026-10-08: 1009
      // Dale Ave, Benton City -> '52' (Kiona-Benton City; PrecinctSplits
      // agrees); 210 W 6th Ave, Kennewick -> '17'; 625 Swift Blvd, Richland
      // and 3801 W Van Giesen St, West Richland -> '400'.
      key: 'SCHDST',
      url: `${DOR_TAX_DISTRICTS}/20/query`,
      attr: 'DISTATTRIB',
    },
  ],
  chelan: [
    // GIS/CM_districts, the same three districts with the commissioner's
    // name. The PW/Commissioner_Districts MapServer and FeatureServer it
    // replaced answer their metadata but every query 500s or times out
    // (#29, 2026-10-08). Live: 316 Washington St, Wenatchee -> '1'; 101
    // Woodring St, Cashmere and 700 US Hwy 2, Leavenworth -> '2'; 135 E
    // Johnson Ave, Chelan -> '3'. No general scope uses it (the commissioner
    // race is county-wide); the primary's District 2 race does.
    { key: 'COUNTY_COUNCIL', url: 'https://atlas.co.chelan.wa.us/arcgis/rest/services/GIS/CM_districts/MapServer/0/query', attr: 'DIST_NO' },
    // WA DOR SCH2025 (#29): Wenatchee School District No. 246's bonds. Live
    // 2026-10-08: 316 Washington St, Wenatchee -> '246'; Cashmere '222',
    // Leavenworth '228', Chelan '129J'.
    { key: 'SCHDST', url: `${DOR_TAX_DISTRICTS}/20/query`, attr: 'DISTATTRIB' },
  ],
  clallam: [
    { key: 'COUNTY_COUNCIL', url: 'https://services8.arcgis.com/noCZ2SM2C0rVag8y/arcgis/rest/services/Commissioner_Districts/FeatureServer/0/query', attr: 'COM_DIST' },
    { key: 'PUDDST', url: 'https://services8.arcgis.com/noCZ2SM2C0rVag8y/arcgis/rest/services/PUD_Commissioner_District_dissolve/FeatureServer/0/query', attr: 'Comm_Dist' },
    { key: 'FIRDST', url: `${DOR_TAX_DISTRICTS}/7/query`, attr: 'DISTATTRIB' },
    // The Auditor's District Court electoral districts (#29): District Court 1
    // and 2 are elected separately. Live 2026-10-08: 223 E 4th St, Port
    // Angeles and 152 W Cedar St, Sequim -> '1'; 500 E Division St, Forks
    // and 7764 La Push Rd -> '2'.
    { key: 'DISTCRT', url: 'https://services8.arcgis.com/noCZ2SM2C0rVag8y/arcgis/rest/services/District_Court/FeatureServer/0/query', attr: 'DISTRICT' },
    // WA DOR SCH2025 (#29): Quillayute Valley School District No. 402 bonds.
    // Live 2026-10-08: Forks -> '402'; Port Angeles '121'; Sequim '323'.
    { key: 'SCHDST', url: `${DOR_TAX_DISTRICTS}/20/query`, attr: 'DISTATTRIB' },
    {
      // PUD No. 1 membership (#29). The whole PUD elects each commissioner in
      // the general, but the City of Port Angeles is outside the PUD, so
      // neither the county nor PUDDST (the commissioner district) is the
      // electorate. Any feature of the commissioner-district layer means
      // the address is in the PUD: `value` reports '1' whatever Comm_Dist
      // reads. Live 2026-10-08: 223 E 4th St, Port Angeles -> no feature;
      // Forks, Sequim and 3851 S Mount Angeles Rd -> a feature.
      key: 'PUDALL',
      url: 'https://services8.arcgis.com/noCZ2SM2C0rVag8y/arcgis/rest/services/PUD_Commissioner_District_dissolve/FeatureServer/0/query',
      attr: 'Comm_Dist',
      value: '1',
    },
  ],
  columbia: [
    { key: 'COUNTY_COUNCIL', url: 'https://services9.arcgis.com/zq1Ay6bxXC1T1CBk/arcgis/rest/services/CommissionerDistricts/FeatureServer/0/query', attr: 'District' },
  ],
  cowlitz: [
    { key: 'COUNTY_COUNCIL', url: 'https://gis.cowlitzwa.gov/ccserver/rest/services/County/Political_Administrative_Districts/MapServer/1/query', attr: 'DIST_ID' },
  ],
  douglas: [
    // Re-probed 2026-10-08 (#30): 100 Eastmont Ave, East Wenatchee -> '2';
    // 50 Main St, Mansfield -> '5'; 448 Belmont Pl, Ephrata -> '1'; 213 S
    // Chelan Ave, Waterville -> no feature. The archived primary's FD 15
    // ('J15') scope reads it; no general scope does.
    { key: 'FIRDST', url: `${DOR_TAX_DISTRICTS}/7/query`, attr: 'DISTATTRIB' },
    // Three Rivers Hospital (District 1) bonds and Hospital District 2's
    // levy (#30). Re-probed 2026-10-08: 1206 Columbia Ave, Bridgeport and 50
    // Main St, Mansfield -> '1'; 213 S Chelan Ave, Waterville -> '2'; 100
    // Eastmont Ave, East Wenatchee -> no feature.
    { key: 'HOSPDST', url: `${DOR_TAX_DISTRICTS}/11/query`, attr: 'DISTATTRIB' },
    // WA DOR SCH2025 (#30): Eastmont School District No. 206's bonds. Live
    // 2026-10-08: 100 Eastmont Ave, East Wenatchee and 1 Rock Island Dr,
    // Rock Island -> '206'; Waterville '209'; Bridgeport '75'; Mansfield '207'.
    { key: 'SCHDST', url: `${DOR_TAX_DISTRICTS}/20/query`, attr: 'DISTATTRIB' },
    // WA DOR CEM2025 (#30): Cemetery District No. 2's levy. Live 2026-10-08:
    // 213 S Chelan Ave, Waterville -> '2'; 236 Brays Landing Rd, Orondo ->
    // '1'; 100 Eastmont Ave, East Wenatchee -> no feature.
    { key: 'CEMDST', url: `${DOR_TAX_DISTRICTS}/3/query`, attr: 'DISTATTRIB' },
    // Proposed Rimrock Meadows Fire Protection District No. 9 (#30): its
    // formation measure and three commissioner seats, voted on only inside
    // the proposed boundary (RCW 52.02.080). DOR has no polygon for a
    // district that is only being formed, so this reads the county's own
    // fire layer, from a service the county names "All_Districts_Temporary".
    // The proposed district's feature reads '009' ('Proposed Rimrock Fire',
    // edited 2026-08-19, after the renaming resolution); the others read
    // '001'-'008', '015', 'BPR' and '000' (no district). Its own key, not
    // FIRDST, so the archived primary's Douglas fire scope keeps reading
    // DOR. CORS echoed the Origin. Live 2026-10-08: 1005 Ashcroft Dr,
    // Ephrata -> '009'; 448 Belmont Pl, Ephrata -> '001'; 100 Eastmont Ave,
    // East Wenatchee -> '002'; 213 S Chelan Ave, Waterville -> '000'.
    {
      key: 'PROPFIRDST',
      url: 'https://gis.douglascountywa.gov/server/rest/services/All_Districts_Temporary/MapServer/4/query',
      attr: 'FireNumber',
    },
  ],
  ferry: [
    { key: 'COUNTY_COUNCIL', url: 'https://services8.arcgis.com/BBejpmYP0j5q6NLc/arcgis/rest/services/Political_Boundaries/FeatureServer/0/query', attr: 'DISTRICT' },
    { key: 'EMSDST', url: `${DOR_TAX_DISTRICTS}/6/query`, attr: 'DISTATTRIB' },
  ],
  franklin: [
    // County portal MapServer. The earlier ArcGIS Online copy
    // (services3.arcgis.com/S61OMZovc3AIomN2/.../Districts/FeatureServer/8)
    // went dead (400 "Invalid URL", 2026-10-09 hotfix). Values are 'COM1'..
    // 'COM3', the same form the primary's Franklin scopes use. Live
    // 2026-10-08: 1016 N 4th Ave, Pasco -> 'COM2'; 5600 N Rd 68, Pasco -> 'COM3'.
    { key: 'COUNTY_COUNCIL', url: 'https://gisportal.franklin.co.franklin.wa.us/arcgis2/rest/services/districts/Commissioner_Districts/MapServer/0/query', attr: 'DISTRICT_CODE' },
    // Port of Pasco commissioner districts (#29; the port elects by district
    // from 2026). The county layer also holds the Port of Kahlotus's
    // 'PoK1'..'PoK3'. Live 2026-10-08: 525 N 3rd Ave, Pasco -> 'PoP1'; 2108 N
    // Rd 84, Pasco -> 'PoP2'; 5600 N Rd 68, Pasco, Mesa and Connell -> 'PoP3'.
    { key: 'PORTDST', url: 'https://gisportal.franklin.co.franklin.wa.us/arcgis2/rest/services/districts/Special_tax_districts/MapServer/7/query', attr: 'DISTRICT_CODE' },
    // WA DOR FIR2025 (#29): Fire Protection District No. 3's levy. Live
    // 2026-10-08: 5600 N Rd 68, Pasco -> '3'; downtown Pasco and Connell none.
    { key: 'FIRDST', url: `${DOR_TAX_DISTRICTS}/7/query`, attr: 'DISTATTRIB' },
  ],
  garfield: [],
  grant: [
    { key: 'COUNTY_COUNCIL', url: 'https://services2.arcgis.com/hQZvdtFxRzJpMtdS/arcgis/rest/services/County_Commissioner_Districts/FeatureServer/27/query', attr: 'DistrictNo' },
    // Live 2026-10-08 (#28): 127 Main Ave E, Soap Lake -> HSP2025 '4'
    // (McKay Healthcare); 321 S Balsam St, Moses Lake -> '1'.
    { key: 'HOSPDST', url: `${DOR_TAX_DISTRICTS}/11/query`, attr: 'DISTATTRIB' },
    // WA DOR FIR2025 and CEM2025 (#28). Live 2026-10-08: 34875 Park Lake Rd
    // NE, Coulee City -> FIRDST '7'; 103 Railroad St, Wilson Creek ->
    // CEMDST '2'; 321 S Balsam St, Moses Lake -> neither.
    { key: 'FIRDST', url: `${DOR_TAX_DISTRICTS}/7/query`, attr: 'DISTATTRIB' },
    { key: 'CEMDST', url: `${DOR_TAX_DISTRICTS}/3/query`, attr: 'DISTATTRIB' },
  ],
  'grays-harbor': [
    // Live 2026-10-08: 110 Main St, Oakville -> '1'; 500 Wynoochee Valley Rd,
    // Montesano -> '2'.
    { key: 'FIRDST', url: `${DOR_TAX_DISTRICTS}/7/query`, attr: 'DISTATTRIB' },
    // WA DOR LIB2025 (#29): Timberland Regional Library ('L'). Ocean Shores
    // runs its own library and is outside it. Live 2026-10-08: Aberdeen,
    // McCleary, Oakville and Montesano -> 'L'; 585 Point Brown Ave NW, Ocean
    // Shores -> none.
    { key: 'LIBDST', url: `${DOR_TAX_DISTRICTS}/12/query`, attr: 'DISTATTRIB' },
    // WA DOR SCH2025 (#29): McCleary School District No. 65's bonds. Live
    // 2026-10-08: 100 S 3rd St, McCleary -> '65'; Aberdeen '5'; Montesano '66'.
    { key: 'SCHDST', url: `${DOR_TAX_DISTRICTS}/20/query`, attr: 'DISTATTRIB' },
  ],
  island: [
    { key: 'COUNTY_COUNCIL', url: 'https://maps.islandcountywa.gov/arcgis/rest/services/Geocortex/Elections/MapServer/0/query', attr: 'COMM__DIST___' },
    { key: 'LIBDST', url: `${DOR_TAX_DISTRICTS}/12/query`, attr: 'DISTATTRIB' },
    {
      // Snohomish County PUD No. 1 serves Camano Island; its seats are
      // elected PUD-wide in the general (RCW 54.12.010(3)), so the Island
      // side of the electorate is Camano Island (#29). DOR PUD2025 has no
      // Island polygon. The Auditor's precinct layer has no PUD attribute,
      // so `where` keeps the Camano precincts (Camano 01-21) and the value is
      // the layer's constant County attribute '53029'. Live 2026-10-08: 848
      // N Sunrise Blvd, Camano Island -> '53029' (precinct Camano 01); 865 SW
      // Barrington Dr, Oak Harbor, 112 2nd St, Langley and 5476 Harbor Rd,
      // Freeland -> none.
      key: 'PUDDST',
      url: 'https://maps.islandcountywa.gov/arcgis/rest/services/Geocortex/Elections/MapServer/2/query',
      attr: 'County',
      where: "PrecinctNa LIKE 'Camano%'",
    },
    // WA DOR PRT2025 (#29). Live 2026-10-08: 112 2nd St, Langley and 5476
    // Harbor Rd, Freeland -> 'S WHIDBEY'; 1 7th St NE, Coupeville -> 'COUPE';
    // Oak Harbor and Camano Island -> none.
    { key: 'PORTDST', url: `${DOR_TAX_DISTRICTS}/16/query`, attr: 'DISTATTRIB' },
    {
      // Unincorporated Island County (#29), for the fireworks advisory vote:
      // WA DOR TCA2025 (layer 23) minus the three incorporated tax code
      // areas, 0100 Oak Harbor, 0300 Coupeville and 0700 Langley (the
      // county's Tax Codes layer gives TCA 100 the fire district 'City of
      // Oak Harbor'). Live 2026-10-08: 848 N Sunrise Blvd, Camano (TCA 0590),
      // 5476 Harbor Rd, Freeland (0760) and 2795 Heller Rd, Oak Harbor
      // (0110) -> 'ISLAND'; 865 SW Barrington Dr, Oak Harbor (0100), 1 7th
      // St NE, Coupeville (0300) and 112 2nd St, Langley (0700) -> none.
      key: 'UNINC',
      url: `${DOR_TAX_DISTRICTS}/23/query`,
      attr: 'COUNTYNAME',
      where: "COUNTYNAME = 'ISLAND' AND DISTATTRIB NOT IN ('0100','0300','0700')",
    },
  ],
  jefferson: [
    // Commissioner districts. The county's own server (gisweb.jeffcowa.us,
    // OpenData/MapServer/26) died: HTTP 503 on every request on 2026-10-08
    // (#31). This is the county's hosted copy of the same districts
    // (FindMyDistrictsInstantApp_WFL1 layer 1 "County Commissioners", same
    // DISTID '1'-'3'). Only the archived primary uses this key (its District
    // 3 race); the general elects District 3 county-wide. Live 2026-10-08:
    // 1820 Jefferson St, Port Townsend -> '1'; 620 Cedar Ave, Port Hadlock ->
    // '2'; Quilcene, Brinnon, 9500 Oak Bay Rd, Port Ludlow and 1993 Dowans
    // Creek Rd, Forks -> '3'.
    { key: 'COUNTY_COUNCIL', url: 'https://services3.arcgis.com/RPU019D0wA2T8GMO/arcgis/rest/services/FindMyDistrictsInstantApp_WFL1/FeatureServer/1/query', attr: 'DISTID' },
    // Re-probed 2026-10-08 (#31): 294715 US Hwy 101, Quilcene -> '2'; 272
    // Schoolhouse Rd, Brinnon -> '1'; Port Townsend and Forks-area -> no
    // feature. Only the archived primary's Quilcene cemetery levy uses it.
    { key: 'CEMDST', url: `${DOR_TAX_DISTRICTS}/3/query`, attr: 'DISTATTRIB' },
    // Clallam County Fire District 1's levy (#31): DOR numbers the
    // district's Jefferson part '9' (Jefferson's own FD 1 is '1'). Live
    // 2026-10-08: 1993 Dowans Creek Rd, Forks -> '9'; Port Townsend, Port
    // Hadlock and Port Ludlow '1'; Quilcene '2'; Brinnon '4'; 18113 Upper
    // Hoh Rd, Forks -> no feature.
    { key: 'FIRDST', url: `${DOR_TAX_DISTRICTS}/7/query`, attr: 'DISTATTRIB' },
    // WA DOR SCH2025 (#31): Quillayute Valley School District No. 402's
    // bonds, the Forks district's Jefferson part (West End). Live 2026-10-08:
    // 1993 Dowans Creek Rd and 18113 Upper Hoh Rd, Forks -> '402'; Port
    // Townsend '50'; Port Hadlock '49'; Quilcene '48'; Brinnon '46'.
    { key: 'SCHDST', url: `${DOR_TAX_DISTRICTS}/20/query`, attr: 'DISTATTRIB' },
  ],
  kittitas: [
    // Re-probed 2026-10-08 (#31): 205 W 5th Ave, Ellensburg -> 3; 207 N
    // Main St, Kittitas -> 1; Thorp, Cle Elum, Roslyn and Easton -> 2. Only
    // the archived primary uses it (Commissioner 3 is elected county-wide in
    // the general).
    { key: 'COUNTY_COUNCIL', url: 'https://services.arcgis.com/eSnyVpqwqWBADfzp/arcgis/rest/services/Commissioner_Districts/FeatureServer/7/query', attr: 'commissioner_district_nbr' },
    // Re-probed 2026-10-08 (#31): Ellensburg '2'; 10700 Thorp Hwy N, Thorp
    // '1'; Easton '3'; Kittitas, Cle Elum, Roslyn -> no feature. Only the
    // archived primary's fire levies use it.
    { key: 'FIRDST', url: `${DOR_TAX_DISTRICTS}/7/query`, attr: 'DISTATTRIB' },
    // The Auditor's precinct-built District Court districts (#31): the Upper
    // and Lower Kittitas County District Court judges are elected by their
    // own district (KCC 2.08.010-.020). Live 2026-10-08: 205 W 5th Ave,
    // Ellensburg, 207 N Main St, Kittitas and 10700 Thorp Hwy N, Thorp ->
    // 'Lower District Court'; 719 E 3rd St, Cle Elum, 201 S 1st St, Roslyn,
    // 523 Lincoln Ave, South Cle Elum and 1893 Railroad St, Easton -> 'Upper
    // District Court'.
    { key: 'DISTCRT', url: 'https://services.arcgis.com/eSnyVpqwqWBADfzp/arcgis/rest/services/Court_Districts/FeatureServer/0/query', attr: 'court_district_name' },
  ],
  klickitat: [
    { key: 'COUNTY_COUNCIL', url: 'https://geo.gartrellgroup.com/server/rest/services/Klickitat/Layers/MapServer/21/query', attr: 'NO' },
    { key: 'FIRDST', url: `${DOR_TAX_DISTRICTS}/7/query`, attr: 'DISTATTRIB' },
  ],
  lewis: [
    { key: 'COUNTY_COUNCIL', url: 'https://arcgis.lewiscountywa.gov/arcgispublic/rest/services/VotingTaxingDistricts/MapServer/0/query', attr: 'COMMISSION' },
    // Live 2026-10-08 (#29): 2152 Jackson Hwy, Chehalis -> '6'.
    { key: 'FIRDST', url: `${DOR_TAX_DISTRICTS}/7/query`, attr: 'DISTATTRIB' },
    // WA DOR PUD2025 (#29). Lewis County PUD No. 1 is the county minus the
    // City of Centralia; its seats are elected PUD-wide in the general. Live
    // 2026-10-08: 351 NW North St, Chehalis, 2152 Jackson Hwy and 200 S Main
    // St, Pe Ell -> '1'; 118 W Maple St, Centralia -> none.
    { key: 'PUDDST', url: `${DOR_TAX_DISTRICTS}/17/query`, attr: 'DISTATTRIB' },
    // WA DOR LIB2025, Timberland Regional Library (#29). Live 2026-10-08:
    // Chehalis, Centralia and 2152 Jackson Hwy -> 'L'; 200 S Main St, Pe Ell
    // -> none.
    { key: 'LIBDST', url: `${DOR_TAX_DISTRICTS}/12/query`, attr: 'DISTATTRIB' },
  ],
  lincoln: [
    { key: 'CEMDST', url: `${DOR_TAX_DISTRICTS}/3/query`, attr: 'DISTATTRIB' },
  ],
  mason: [
    // Re-probed 2026-10-08 (#30): 525 W Cota St, Shelton -> '3'; 23850 NE
    // State Route 3, Belfair -> '1'; 24151 N US Hwy 101, Hoodsport -> '2'.
    // No general scope uses it (the commissioner race is county-wide).
    { key: 'COUNTY_COUNCIL', url: 'https://gis.masoncountywa.gov/arcgis/rest/services/MasonCoSite/Districts/MapServer/1/query', attr: 'DIST_ID' },
    // Re-probed 2026-10-08 (#30): Belfair -> 'NMRFA'; Hoodsport -> '18';
    // 525 W Cota St, Shelton -> no feature.
    { key: 'FIRDST', url: `${DOR_TAX_DISTRICTS}/7/query`, attr: 'DISTATTRIB' },
    // WA DOR PUD2025 (#30): Mason is split between PUD No. 1 (Hood Canal,
    // Hoodsport) and PUD No. 3 (the rest of the county); each PUD elects its
    // commissioners PUD-wide in the general, so the seats are scoped '1' and
    // '3'. Live 2026-10-08: 24151 N US Hwy 101, Hoodsport -> '1'; 525 W Cota
    // St, Shelton and 23850 NE State Route 3, Belfair -> '3'.
    { key: 'PUDDST', url: `${DOR_TAX_DISTRICTS}/17/query`, attr: 'DISTATTRIB' },
    // WA DOR SCH2025 (#30): Southside SD 42, McCleary SD 65 (mostly in Grays
    // Harbor) and Pioneer SD 402 measures. Live 2026-10-08: 161 SE Collier
    // Rd, Shelton -> '42'; 281 W Bonnieview Dr, McCleary -> '65'; 112 E
    // Spencer Lake Rd, Shelton -> '402'; 525 W Cota St, Shelton '309'.
    { key: 'SCHDST', url: `${DOR_TAX_DISTRICTS}/20/query`, attr: 'DISTATTRIB' },
  ],
  okanogan: [
    // Fire Protection District No. 1's levy lid lift (#30). Re-probed
    // 2026-10-08: 38 Swanson Mill Rd, Oroville -> '1'; 50 Lost River Rd,
    // Mazama, 206 Riverside Ave, Winthrop and 118 S Glover St, Twisp -> '6';
    // 1308 Ironwood St, Oroville (the city), 415 Hospital Way, Brewster and
    // 2 S Ash St, Omak -> no feature.
    { key: 'FIRDST', url: `${DOR_TAX_DISTRICTS}/7/query`, attr: 'DISTATTRIB' },
    // Three Rivers Hospital (Public Hospital District No. 1, Okanogan and
    // Douglas Counties) bonds, scoped '1J' (#30). Re-probed 2026-10-08:
    // Mazama, Winthrop, Twisp and Brewster -> '1J'; Omak -> '3'; Oroville
    // (city and Swanson Mill Rd) -> '4'.
    { key: 'HOSPDST', url: `${DOR_TAX_DISTRICTS}/11/query`, attr: 'DISTATTRIB' },
    // WA DOR EMS2025 (#30): the Methow Valley EMS District's levy, scoped
    // 'MV' (the district leaves out the towns of Twisp and Winthrop, which
    // run their own levies, scoped CITY). Live 2026-10-08: 50 Lost River
    // Rd, Mazama -> 'MV'; 118 S Glover St, Twisp -> 'TC'; 206 Riverside Ave,
    // Winthrop -> 'WC'; 415 Hospital Way, Brewster -> 'BC'; 1308 Ironwood
    // St, Oroville -> 'OC'; 38 Swanson Mill Rd, Oroville -> 'OR'; 2 S Ash St,
    // Omak -> no feature.
    { key: 'EMSDST', url: `${DOR_TAX_DISTRICTS}/6/query`, attr: 'DISTATTRIB' },
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
    // Live 2026-10-08 (#28): 5800 Main St, Bow -> FIR2025 '5'; 305 N 6th
    // St, La Conner -> SCH2025 '311'; 700 S 2nd St, Mount Vernon -> no fire
    // district, SCH2025 '320'.
    { key: 'FIRDST', url: `${DOR_TAX_DISTRICTS}/7/query`, attr: 'DISTATTRIB' },
    { key: 'HOSPDST', url: `${DOR_TAX_DISTRICTS}/11/query`, attr: 'DISTATTRIB' },
    { key: 'SCHDST', url: `${DOR_TAX_DISTRICTS}/20/query`, attr: 'DISTATTRIB' },
  ],
  skamania: [
    { key: 'COUNTY_COUNCIL', url: 'https://services3.arcgis.com/uKh72TYBlxpm42Cm/arcgis/rest/services/CommissionerDistrict/FeatureServer/0/query', attr: 'CommDist' },
    { key: 'WATDST', url: `${DOR_TAX_DISTRICTS}/22/query`, attr: 'DISTATTRIB' },
  ],
  stevens: [
    // Re-probed 2026-10-08 (#30): 6015 State Route 291, Nine Mile Falls ->
    // '1'; 301 E Clay Ave, Chewelah -> '2'; 215 S Oak St, Colville -> '3'.
    // No general scope uses it (the commissioner race is county-wide).
    { key: 'COUNTY_COUNCIL', url: 'https://gis.stevenscountywa.gov/server/rest/services/AdministrativeBoundaries/MapServer/5/query', attr: 'districtid' },
    // Fire District 10 Prop. 1 (#30). Re-probed 2026-10-08: 2785 Aladdin Rd,
    // Colville -> '10'; Nine Mile Falls and Loon Lake -> '1'; 215 S Oak St,
    // Colville -> no feature.
    { key: 'FIRDST', url: `${DOR_TAX_DISTRICTS}/7/query`, attr: 'DISTATTRIB' },
    // WA DOR LIB2025 (#30): Stevens County Rural Library District Prop. 2 is
    // scoped 'L'; the Cities of Colville and Kettle Falls are outside the
    // district. Live 2026-10-08: 'L' at 301 E Clay Ave, Chewelah; 3998 State
    // Hwy 292, Loon Lake; 6015 State Route 291, Nine Mile Falls; 2785 Aladdin
    // Rd, Colville. No feature at 215 S Oak St, Colville or 605 Meyers St,
    // Kettle Falls.
    { key: 'LIBDST', url: `${DOR_TAX_DISTRICTS}/12/query`, attr: 'DISTATTRIB' },
    // WA DOR SCH2025 (#30): Nine Mile Falls SD 325-179 Props. 1 and 2 are
    // scoped '179J' (the district's Stevens side). Live 2026-10-08: 6015
    // State Route 291, Nine Mile Falls -> '179J'; 215 S Oak St, Colville
    // '115'; Chewelah '36'; Loon Lake '183J'; 2785 Aladdin Rd '211'.
    { key: 'SCHDST', url: `${DOR_TAX_DISTRICTS}/20/query`, attr: 'DISTATTRIB' },
  ],
  wahkiakum: [
    { key: 'COUNTY_COUNCIL', url: 'https://services5.arcgis.com/SQaKrZ90pTH1GKNW/arcgis/rest/services/Commissioner_Districts1/FeatureServer/1/query', attr: 'District_Number' },
  ],
  'walla-walla': [
    // Re-probed 2026-10-08 (#30): 315 W Main St, Walla Walla -> '1'; 108 S D
    // St, Prescott -> '2'; 625 S College Ave, College Place -> '3'. No
    // general scope uses it (Commissioner District 3 is elected county-wide).
    { key: 'COUNTY_COUNCIL', url: 'https://services8.arcgis.com/COL6rRPkF9w28VGX/arcgis/rest/services/Voting_Districts1/FeatureServer/52/query', attr: 'commis_dis' },
    // WA DOR SCH2025 (#30): Dixie SD 101 Prop. 1 is scoped '101' ('101' also
    // names districts in other counties, which a Walla Walla point never
    // reaches). Live 2026-10-08: interior point (-118.153, 46.140) in Dixie
    // -> '101' (the Census geocoder matches no Dixie street address); 315 W
    // Main St, Walla Walla '140'; 106 Preston Ave, Waitsburg '401'; 108 S D
    // St, Prescott '402'.
    { key: 'SCHDST', url: `${DOR_TAX_DISTRICTS}/20/query`, attr: 'DISTATTRIB' },
    // WA DOR PKR2025 (#30): Prescott Joint Park and Recreation District Prop.
    // No. 1 is scoped 'PRES' (joint with Columbia County). Live 2026-10-08:
    // 108 S D St, Prescott -> 'PRES'; 106 Preston Ave, Waitsburg -> 'WAIT';
    // 315 W Main St, Walla Walla -> no feature.
    { key: 'PARKDST', url: `${DOR_TAX_DISTRICTS}/14/query`, attr: 'DISTATTRIB' },
  ],
  whatcom: [
    { key: 'PORTDST', url: 'https://services3.arcgis.com/Qkk60MooanUNTUHp/arcgis/rest/services/2021ProposedPOBDistricts/FeatureServer/0/query', attr: 'Council' },
    { key: 'FIRDST', url: `${DOR_TAX_DISTRICTS}/7/query`, attr: 'DISTATTRIB' },
    { key: 'HOSPDST', url: `${DOR_TAX_DISTRICTS}/11/query`, attr: 'DISTATTRIB' },
  ],
  whitman: [
    // Re-probed 2026-10-08 (#30): 101 Steptoe Ave, Oakesdale -> 1; 325 SE
    // Paradise St, Pullman -> 2; 200 S Mill St, Colfax -> 3. No general
    // scope uses it (Commissioner District 3 is elected county-wide).
    { key: 'COUNTY_COUNCIL', url: 'https://services3.arcgis.com/eoLFybJXLOtInQXJ/arcgis/rest/services/Whitman_County_BOCC_Districts___Feb__2026_WFL1/FeatureServer/10/query', attr: 'BOCC' },
    // Fire Districts 8 and 14 (#30). Re-probed 2026-10-08: 110 S Montgomery
    // St, Uniontown and 705 Broadway St, Colton -> '14'; (-117.85, 46.80)
    // near LaCrosse -> '8'; 102 N Main Ave, LaCrosse (the town itself) and
    // Pullman -> no feature.
    { key: 'FIRDST', url: `${DOR_TAX_DISTRICTS}/7/query`, attr: 'DISTATTRIB' },
    // Park districts 1, 2, 3, 4 and 7 (#30). Re-probed 2026-10-08: LaCrosse
    // '1', 405 E California St, Garfield '2', 101 Front St, St. John '3',
    // Oakesdale '4', Endicott interior point (-117.6858, 46.9268) '7';
    // Pullman -> no feature.
    { key: 'PARKDST', url: `${DOR_TAX_DISTRICTS}/14/query`, attr: 'DISTATTRIB' },
    // WA DOR CEM2025 (#30): Oakesdale 1, Garfield 2, St. John 3 and Endicott
    // 4 cemetery levies. Live 2026-10-08: 101 Steptoe Ave, Oakesdale '1';
    // Garfield '2'; St. John '3'; Endicott interior point '4'; 200 S Mill
    // St, Colfax '6' (no measure); Pullman -> no feature.
    { key: 'CEMDST', url: `${DOR_TAX_DISTRICTS}/3/query`, attr: 'DISTATTRIB' },
    // WA DOR LIB2025 (#30): Whitman County Rural Library District Prop. 1 is
    // scoped 'L'. Live 2026-10-08: 'L' at Colfax (200 S Mill St), Tekoa,
    // Palouse, Oakesdale, St. John, Albion and LaCrosse; no feature at
    // Pullman, Rosalia, Garfield, Endicott, Colton or Uniontown.
    { key: 'LIBDST', url: `${DOR_TAX_DISTRICTS}/12/query`, attr: 'DISTATTRIB' },
    // WA DOR SCH2025 (#30): Cheney School District No. 360's Whitman portion
    // reads '316', a thin strip north of St. John with no geocodable street
    // address. Live 2026-10-08: interior point (-117.70, 47.24) -> '316';
    // Pullman '267', Colfax '300', Oakesdale '324', Uniontown '306'.
    { key: 'SCHDST', url: `${DOR_TAX_DISTRICTS}/20/query`, attr: 'DISTATTRIB' },
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

// The Census geocoder places a street address only when the line also carries a
// city or a ZIP; a bare street returns zero matches no matter how it is spelled.
// A ZIP is the cheaper thing to ask a voter for, so these two support the
// recovery prompt on the Address screen. The trailing anchor matters: a house
// number is often five digits too ("19019 SE 128th St" has no ZIP).
export function hasZip(address) {
  return /\b\d{5}(-\d{4})?\s*$/.test(String(address || '').trim())
}

export function withZip(address, zip) {
  const base = String(address || '').trim().replace(/[,\s]+$/, '')
  return `${base}, WA ${String(zip || '').trim()}`
}

// A no-match on a line carrying no ZIP is a missing city, not a typo, so it is
// worth one targeted question instead of a dead end. Once the retry has a ZIP
// and still fails, this returns false and the standard error screen takes over.
export function shouldAskForZip(err, address) {
  return err?.kind === 'no-match' && !hasZip(address)
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
  const res = await fetch(`${kingLayerQueryUrl(service)}?${params}`)
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
  // Optional attribute filter for a layer that mixes the districts a key
  // means with others (Snohomish RFADST on the DOR fire layer, Thurston
  // RFADST on the county fire layer).
  if (layer.where) params.set('where', layer.where)
  const res = await fetch(`${layer.url}?${params}`)
  if (!res.ok) throw new GeoError(`District lookup failed (${layer.key}).`, 'network', { layer: layer.key })
  const data = await res.json()
  if (data.error) throw new GeoError(`District lookup failed (${layer.key}).`, 'network', { layer: layer.key })
  const feat = data.features?.[0]
  // Optional constant for a presence layer: any feature (after `where`) means
  // the address is in the district, whatever `attr` reads (Clallam PUDALL:
  // the PUD's commissioner-district polygons, which leave out Port Angeles).
  if (layer.value != null) return feat ? String(layer.value) : null
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

// The Census 'Current' vintage renames these layers when it rotates (on
// 2026-10-08 it answered '120th Congressional Districts' and '2026 State
// Legislative Districts - Lower/Upper' where it had answered '119th' and
// '2024'), so match them by suffix rather than by full name.
function firstGeoMatching(pt, pattern) {
  const key = Object.keys(pt.geographies || {}).find((k) => pattern.test(k))
  return key ? firstGeo(pt, key) : null
}

// The district number: BASENAME ('6'), else the vintage's own key (CD119,
// CD120, ...: '06'), else GEOID ('5306'), which leads with the 2-digit state FIPS.
function congressionalNumber(feature) {
  if (!feature) return null
  if (feature.BASENAME) return feature.BASENAME
  const cdKey = Object.keys(feature).find((k) => /^CD\d+$/.test(k) && feature[k])
  if (cdKey) return feature[cdKey]
  return feature.GEOID ? String(feature.GEOID).slice(2) : null
}

function lookupCensusDistricts(pt) {
  const congressional = firstGeoMatching(pt, /Congressional Districts$/)
  const lower = firstGeoMatching(pt, /State Legislative Districts - Lower$/)
  const upper = firstGeoMatching(pt, /State Legislative Districts - Upper$/)
  const place = firstGeo(pt, 'Incorporated Places')
  const districts = {}
  const cd = trimDistrictNumber(congressionalNumber(congressional))
  const ld = trimDistrictNumber(lower?.BASENAME || lower?.SLDL || upper?.BASENAME || upper?.SLDU)
  // BASENAME is the bare place name and may itself end in 'City' ('Benton
  // City', 'Coulee City'); only NAME carries the legal suffix ('Seattle city').
  const city = place?.BASENAME ? String(place.BASENAME).trim() : (place?.NAME || '').replace(/\s+city$/i, '').trim()
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

// Which caveat, if any, a resolved ballot context deserves. Returns a kind
// rather than a sentence so the wording stays with the screen that shows it.
// 'degraded' covers both a data package that is knowingly partial and a county
// GIS layer that failed to answer this time — from the voter's side both mean
// the same thing: the ballot below may be missing something.
export function coverageAdvice(context) {
  if (!context) return null
  if (context.coverageStatus === 'statewide_only') return 'statewide-only'
  if (context.coverageStatus === 'partial_county' || context.missingLayers?.length) return 'degraded'
  return null
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
