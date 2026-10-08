# San Juan County Completeness Note

Election: 2026 Washington general election, November 3, 2026 (VoteWA
election 899, county code 28).

Status (#32): shipped at Full County Coverage in
`APP_PACKAGES["2026-11-03-general"]["counties"]`, with its elections office
(`https://www.sanjuancountywa.gov/1292/Current-Election`), its pamphlet
(`pamphletPdfs['san-juan/local-voters-pamphlet']`, PDF page = printed page)
and its VoteWA guide (`countyGuides['san-juan']`, `c=28`).
`COUNTY_LAYERS['san-juan']` gained `FIRDST`, `PORTDST` and `PARKDST` as
proposed below, and `SWDDST` read from DOR PRT2025 (`where: "DISTATTRIB =
'LOPEZ'"`, `value: 'LOPEZ'`), the equivalent alternative named below, rather
than the county precinct layer. CD 2 ships with Snohomish's research, LD 40
with Whatcom's. Live ballots on 2026-10-08, each `full_county` with no
missing layer: 2225 Fisherman Bay Rd, Lopez Island (Fire District 4, Port
of Lopez and Lopez Solid Waste measures), 500 Rose St, Eastsound (the Orcas
park levy only) and 350 Court St, Friday Harbor (no local measure). The
paragraphs below describe the package as researched.

Research package for #32. Contests and measures are
built by `pipeline/build_votewa_lite_data.py --county san-juan` from the
VoteWA candidate list (`raw/votewa/candidate-list.csv.url`, 26 rows) and the
overrides and measures in that script's
`ELECTION_MEASURES["2026-11-03-general"]["san-juan"]`, checked against the
San Juan County Auditor's combined state and county voters' pamphlet
(`raw/san-juan/local-voters-pamphlet.pdf.url`; county section pages 35-57,
PDF page = printed page; text in `interim/pdf-text/local-voters-pamphlet.txt`),
the sample ballot (`raw/san-juan/sample-ballot.pdf.url`, which "includes all
races/measures presented within the county") and VoteWA's online voters'
guide for the county (`https://voter.votewa.gov/genericvoterguide.aspx?e=899&c=28`;
records under `raw/votewa/voter-guide/`, text in `interim/voter-guide-text/`).
All three agree contest for contest, and the county's Oct. 1, 2026 news
release (`raw/san-juan/news-2026-10-01-general-election.html.url`) names the
same four local measures. The Current Election page
(`https://www.sanjuancountywa.gov/1292/Current-Election`, HTTP 200 on
2026-10-08, `raw/san-juan/current-election.html.url`) links the pamphlet
(`DocumentCenter/View/36027`), the sample ballot (`/35947`) and the four
measure resolutions (`/35848`-`/35851`; scanned images, no text layer).

The builder reports `full_county`. The assembler will mark the county
`partial_county` until `COUNTY_LAYERS['san-juan']` reads the four layers
proposed below; today it reads only `SCHDST`, which no general scope uses.

## What is on the ballot

11 contests (5 contested, 6 uncontested) and 4 local measures. The five
Supreme Court contests and the three statewide initiatives are dropped by
the builder and ship from the statewide package.

| Kind | Contests | Contested | Uncontested | Scope | Researched |
|---|---|---|---|---|---|
| U.S. Representative (CD 2) | 1 | 1 | 0 | `CONGDST` `2` | Snohomish package |
| LD 40 Rep. Pos. 1, Pos. 2 | 2 | 2 | 0 | `LEGDST` `40` | Whatcom package |
| Auditor | 1 | 1 | 0 | `COUNTY` | here (new) |
| Council Residency District 3 | 1 | 1 | 0 | `COUNTY` | here (carried from the primary, re-researched) |
| Assessor, Clerk, Prosecuting Attorney, Sheriff, Treasurer | 5 | 0 | 5 | `COUNTY` | here (info-only) |
| District Court Judge | 1 | 0 | 1 | `COUNTY` | here (info-only) |

All of San Juan County is in CD 2 and LD 40. There is no LD 40 Senate race
and no Court of Appeals seat on San Juan's general ballot (none in the
VoteWA export or the pamphlet). The research plan lists CD 2 as researched in
Snohomish and LD 40 Pos. 1 and Pos. 2 as researched in Whatcom, each with
`candidates_missing` empty; no legislative or congressional seat lacks an
owner. No PUD, port commissioner, hospital, fire commissioner or Superior
Court seat is on the general ballot.

Measures (VoteWA guide records 7286, 7287, 7288, 7285; pamphlet pp. 50-57):

| Measure | Scope | Pamphlet pages |
|---|---|---|
| San Juan County Fire Protection District No. 4 (Lopez Island Fire & EMS) Proposition No. 1, levy lid lift to $0.74 per $1,000 with a 103% limit factor through 2035 | `FIRDST` `4` | 50-51 |
| Port of Lopez Proposition No. 1, commissioner terms from four years to six | `PORTDST` `LOPEZ` | 52-53 |
| Orcas Island Park and Recreation District Proposition No. 1, six-year levy at $0.15 per $1,000 | `PARKDST` `ORCAS` | 54-55 |
| Lopez Solid Waste Disposal District Proposition No. 1, $210,000 excess levy for 2027 | `SWDDST` `LOPEZ` | 56-57 |

## District scoping

- **Council.** San Juan is a home-rule charter county with a three-member
  council. Members must live in their residency district, but every county
  voter votes for every seat, in the primary and in the general. Evidence:
  VoteWA types the race `Countywide` / `County`; the certified Aug. 4, 2026
  primary counted Council Residency District 3 on all 23 of 23 units
  (`raw/san-juan/votewa-results-20260804-ballot-items.json.url`); the SOS
  precinct exports put the 2022 District 3 race and the 2024 District 1 and
  2 races on all 23 precincts, and the 2020 District 1 and 2 races on all 19
  (`raw/san-juan/sos-results-*.csv.url`). The charter text itself is
  hosted on ecode360
  (`https://ecode360.com/SA4768`, via codepublishing.com), which answered
  HTTP 403 to every scripted and WebFetch request on 2026-10-08, so no
  charter section is quoted here; the scope rests on the election records
  above. The council seat stays `COUNTY` (generic rule) with the primary's
  contest name, so its slug matches the primary's. The county's
  `Residency_Districts` layer (below) exists but is not needed.
- **District Court:** one county-wide judge; override names it
  `San Juan County District Court` / `Judge`, category `Judicial`, keeping
  the generic slug `san-juan-san-juan-county-district-court-judge`.
- **Fire District 4** is Lopez Island and nearby small islands, not Decatur:
  DOR FIR2025 (layer 7) `4` at every Lopez probe; none on Decatur. The county
  `Junior_Tax_District_Boundaries` layer gives Fire District 4, the Port of
  Lopez and the Lopez Island Library District one polygon (18,992.36 acres);
  DOR's 2025 levy detail gives Fire Dist #4, Port of Lopez, Lopez Island
  Library, Lopez Hospital #2 and EMS - Lopez the same assessed value,
  $2,232,340,908.
- **Port of Lopez:** DOR PRT2025 (layer 16) `LOPEZ`; Friday Harbor reads
  `FRI HAR`, Orcas `ORCAS`. Its commissioner races (2023, 2025) were on
  precincts Lopez North, Northwest and South only.
- **Orcas Island Park and Recreation District:** DOR PKR2025 (layer 14)
  `ORCAS` across Orcas; none on Blakely or Waldron, which are in Orcas Island
  School District but not the park district. Its commissioner races (2023,
  2025) were on the seven Orcas precincts, not Blakely & Outer Is or Waldron
  & Outer Is. (San Juan Island's park district reads `S J`.)
- **Lopez Solid Waste Disposal District:** no DOR layer (the 2025 group has
  no solid-waste layer) and no county tax-district feature. Its annual levy
  was on precincts Lopez North, Lopez Northwest and Lopez South only, never
  Decatur & Outer Islands, in the 2020, 2022, 2023, 2024 and 2025 generals
  (SOS exports), the same precincts as Fire District 4 and the Port of
  Lopez. DOR's levy detail gives it $2,218,902,086 of assessed value, 0.6%
  below the regular-levy districts' $2,232,340,908, which fits an excess
  levy's smaller base (Pierce's Valley RFA and Valley RFA Bond differ by the
  same proportion). Scoped `SWDDST` `LOPEZ`, a new key, to be read from the
  county's precinct layer (below).

## Layers

`app/src/lib/geo.js` `COUNTY_LAYERS['san-juan']` today: `SCHDST` (DOR 20).
Re-probed 2026-10-08: 350 Court St, Friday Harbor -> `149`; 2225 Fisherman
Bay Rd, Lopez -> `144`; 500 Rose St, Eastsound -> `137`; Shaw interior point
-> `10`. No general scope uses it (the archived primary's Lopez Island SD 144
levy does).

The general needs four more keys:

```js
{ key: 'FIRDST', url: `${DOR_TAX_DISTRICTS}/7/query`, attr: 'DISTATTRIB' },
{ key: 'PORTDST', url: `${DOR_TAX_DISTRICTS}/16/query`, attr: 'DISTATTRIB' },
{ key: 'PARKDST', url: `${DOR_TAX_DISTRICTS}/14/query`, attr: 'DISTATTRIB' },
{
  // Lopez Solid Waste Disposal District: no tax-district layer has it. Its
  // levy is voted on in precincts Lopez Northwest, North and South (SOS
  // exports 2020-2025); the county's precinct layer is the election's own
  // geography. Any feature after `where` means the address is in it.
  key: 'SWDDST',
  url: 'https://services.arcgis.com/PNkCg7xWnaf90qde/arcgis/rest/services/Voter_Precincts/FeatureServer/0/query',
  attr: 'St_Code',
  where: "St_Code IN ('SJ030','SJ031','SJ032')",
  value: 'LOPEZ',
},
```

`Voter_Precincts` (San Juan County GIS, ArcGIS Online org
`PNkCg7xWnaf90qde`, public, last edited 2024-02-16) has 40 polygons and 23
distinct `St_Code` values, the 23 reporting units of the 2026 primary
(`raw/san-juan/gis-voter-precincts.json.url`). Lopez: `SJ030` Lopez
Northwest, `SJ031` Lopez North, `SJ032` Lopez South (with sub-precinct
MacKayeHWD); Decatur & Outer Islands is `SJ033`. A grid check over Lopez and
Decatur (425 points at 0.01 degree spacing, 2026-10-08) found every land
point inside `SJ030`-`SJ032` also inside DOR PRT2025 `LOPEZ` and FIR2025 `4`,
and every other land point in neither; the DOR polygons also cover open
water, which the precinct polygons do not. An equivalent alternative is DOR
PRT2025 with `where: "DISTATTRIB = 'LOPEZ'"` and `value: 'LOPEZ'`, which
relies on the district being coterminous with the port rather than on its
own voting precincts.

`districts.js` (display only, outside this package): `SWDDST` needs a label
(e.g. 'Solid Waste Disposal District'); `PORTDST` `LOPEZ` and `SWDDST`
`LOPEZ` would read better with `NAMED_VALUES` entries ('Port of Lopez',
'Lopez Solid Waste Disposal District').

Other county layers found and not needed: `Residency_Districts`
(`Resd_Dist`, 'Residency District 1'-'3'; Lopez and Shaw -> 3, Orcas -> 2,
San Juan Island -> 1) and `Junior_Tax_District_Boundaries` (28 features;
no solid waste or Orcas park district).

### Point queries (2026-10-08, Census geocoder `Public_AR_Current`, DOR 2025 layers)

| Address or point | Precinct (`St_Code`) | FIR (7) | PRT (16) | PKR (14) | SCH (20) | `SWDDST` query |
|---|---|---|---|---|---|---|
| 350 Court St, Friday Harbor | SJ101 | `3` | `FRI HAR` | `S J` | `149` | none |
| 248 Reuben Memorial Dr, Friday Harbor (Roche Harbor) | SJ015 | `3` | `FRI HAR` | `S J` | `149` | none |
| 500 Rose St, Eastsound | SJ025 | `2` | `ORCAS` | `ORCAS` | `137` | none |
| 5164 Deer Harbor Rd, Deer Harbor | SJ022 | `2` | `ORCAS` | `ORCAS` | `137` | none |
| 107 Doe Bay Rd, Olga | SJ027 | `2` | `ORCAS` | `ORCAS` | `137` | none |
| 2225 Fisherman Bay Rd, Lopez Island | SJ030 | `4` | `LOPEZ` | none | `144` | `SJ030` -> `LOPEZ` |
| 86 School Rd, Lopez Island | SJ032 | `4` | `LOPEZ` | none | `144` | `SJ032` -> `LOPEZ` |
| 4102 Mud Bay Rd, Lopez Island | SJ032 | `4` | `LOPEZ` | none | `144` | `SJ032` -> `LOPEZ` |
| point -122.8650, 48.5400 (north Lopez) | SJ031 | `4` | `LOPEZ` | none | `144` | `SJ031` -> `LOPEZ` |
| point -122.8150, 48.5050 (Decatur) | SJ033 | none | none | none | `144` | none |
| point -122.9645, 48.5770 (Shaw) | SJ041 | `5` | none | none | `10` | none |
| point -122.8150, 48.5650 (Blakely) | SJ028 | none | none | none | `137` | none |
| point -123.0350, 48.7020 (Waldron) | SJ020 | none | none | none | `137` | none |

(Shaw Island addresses do not geocode with the Census geocoder; interior
points were used for Shaw, Decatur, Blakely and Waldron.)

Suggested live checks once the four keys are added: 2225 Fisherman Bay Rd,
Lopez Island (the three Lopez measures: Fire District 4, Port of Lopez,
Lopez Solid Waste); 500 Rose St, Eastsound (the Orcas park levy only);
350 Court St, Friday Harbor (no local measure).

## Sources

The county prints one combined state and county pamphlet, mailed to every
household; its PDF pages equal its printed page numbers. Dossiers cite it as
`local-voters-pamphlet page N` (Assessor 42, Auditor 43, Clerk 44, Council
45, Prosecuting Attorney 46, Sheriff 47, Treasurer 48, District Court 49,
measures 50-57) and the VoteWA guide records. Local news: the Journal of the
San Juan Islands (sanjuanjournal.com; it shares stories with the Islands'
Sounder and Islands' Weekly) and theOrcasonian. Candidate-supplied posts on
theOrcasonian are cited as candidate statements, not news.

## Known gaps

- The charter text (ecode360) could not be read by script; see District
  scoping.
- The four measure resolutions are scanned images with no text layer; their
  terms are cited from the pamphlet and VoteWA records. The Lopez Solid Waste
  measure's ballot title cites Resolution No. 20-2026 and its explanatory
  statement Resolution No. 2026-02.
- The Auditor candidates' evidence is their own statements, endorsements
  and county budget coverage; no forum coverage or reporting on Heather
  Lee's criticism of the office was found.
- Both council candidates answered an OPALCO questionnaire on energy
  facilities published in the cooperative's Ruralite magazine (issuu); it
  could not be read by script and is not cited.
- No PDC filings were pulled for this package.
- The uncontested Clerk, Prosecuting Attorney, Treasurer and District Court
  candidates are pamphlet-only.
- The primary's San Juan dossiers were one-line pamphlet summaries; nothing
  from them was carried forward unverified.
