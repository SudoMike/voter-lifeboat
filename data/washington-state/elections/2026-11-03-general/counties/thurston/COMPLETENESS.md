# Thurston County Completeness Note

Election: 2026 Washington general election, November 3, 2026 (VoteWA
election 899, county code 31).

Shipped 2026-10-08 (#22) at **Full County Coverage** (`full_county`):
`pipeline/election.py` declares it in
`APP_PACKAGES["2026-11-03-general"]["counties"]` with its elections office
(`https://www.thurstoncountywa.gov/departments/auditor/elections`). Every
scope resolves: `app/src/lib/geo.js` `COUNTY_LAYERS.thurston` gained
`SCHDST` and `RFADST` in #22 (see below), and the builder
(`pipeline/build_thurston_lite_data.py`) lists no unresolvable layer. The
app links both cited editions at the cited PDF page (`officialLinks.js`
`pamphletPdfs` `thurston/local-voters-pamphlet`, whose PDF pages run 46
behind its printed numbers, and `thurston/voters-pamphlet-edition-27-thurston`).
CD 10 and LD 2 ship with Pierce's scoring and dossiers, CD 3 and LD 20
with Clark's, LD 35 with Kitsap's.

## Sources

- Contests: the VoteWA candidate list
  (`raw/votewa/candidate-list.csv.{url,meta.json}`, now pinned by
  `sha256` and `sha256_case_normalized`).
- Ballot check: the county's composite sample ballot (Rev. 08/24/2026,
  `raw/thurston/sample-ballot.pdf.url`); every VoteWA contest and every
  measure is on it.
- Local candidate statements and measures: Thurston County Local Voters'
  Pamphlet (`raw/thurston/local-voters-pamphlet.pdf.url`, edition id
  `local-voters-pamphlet`, PDF pages 1-30 = printed pages 47-76).
- Legislative and Court of Appeals statements: SOS Voters' Pamphlet
  Edition 27, Thurston (`raw/sos/voters-pamphlet-edition-27-thurston.pdf.url`,
  edition id `voters-pamphlet-edition-27-thurston`). Edition 27 binds the
  local pamphlet in as its pages 47-76; the SOS erratum for page 63
  (`raw/sos/voters-pamphlet-edition-27-page-63-update.pdf.url`, Treasurer)
  matches the county's own PDF.
- Extracted text: `interim/pdf-text/` (`pipeline/extract_pdf_text.mjs`).
  The four measure resolutions are scanned images with no text layer.

## What the package holds

28 contests (19 contested, 9 uncontested) and 4 measures. Supreme Court
contests are dropped by the builder and ship from the statewide package.

| Kind | Contests | Researched here | Scope |
|---|---|---|---|
| CD 3 | 1 | no: Clark lists it (shared-race rule) | `CONGDST` |
| CD 10; LD 2 Pos. 1, Pos. 2 | 3 | no: researched in Pierce | `CONGDST`, `LEGDST` |
| LD 19 Pos. 1, Pos. 2 | 2 | yes | `LEGDST` |
| LD 20 Pos. 1, Pos. 2 | 2 | no: Clark lists it | `LEGDST` |
| LD 22 Pos. 1, Pos. 2 | 2 | yes | `LEGDST` |
| LD 35 Senator, Pos. 1, Pos. 2 | 3 | no: Kitsap (shared-race rule) | `LEGDST` |
| Assessor, Clerk, Sheriff | 3 | yes | `COUNTY` |
| Commissioner District 5 | 1 | yes | `COUNTY` (see below) |
| PUD Commissioner Districts 1 and 3 | 2 | yes, no scores (no rubric axis applies) | `COUNTY` (see below) |
| Auditor, Coroner, Prosecuting Attorney, Treasurer, Commissioner District 3 | 5 uncontested | info-only | `COUNTY` |
| Court of Appeals Div. 2 Dist. 2 Pos. 1; District Court Pos. 1-3 | 4 uncontested | info-only | `COUNTY` |

Until Clark and Kitsap merge their research, CD 3, LD 20 and LD 35 have no
scoring file anywhere, and `verify_dossiers.py thurston` counts those six
contests as `untouched_contests`.

## District scoping

- **Commissioners** (`COMMISSIONER DISTRICT ALL COUNTY` in VoteWA): a
  five-member board, nominated by district in the primary and elected by
  the whole county in the general (RCW 36.32.0556,
  `data/.cache/thurston/rcw-36-32-0556.html`). Scope `COUNTY`.
- **PUD commissioners**: RCW 54.12.010(3), voters of the entire PUD elect
  in the general. Thurston PUD's three commissioner districts
  (`Common_Layers/Jurisdictions/FeatureServer/15`) cover the whole county:
  their areas sum to the county commissioner districts' total
  (4,099,049,658 sq m in both layers). Scope `COUNTY`. The `PUDDST` layer in
  `COUNTY_LAYERS.thurston` is no longer used by any general scope.
- **Timberland Regional Library Prop. 1**: headed "Countywide Measure" on
  the sample ballot; DOR LIB2025 returns `L` at every check address.
  Scope `COUNTY`.
- **Lacey Fire District 3 Prop. 1**: `FIRDST` `FD03` (DISPATCH_G on
  `ThurstonExt/Thurston_FireDistricts_TCOMM/FeatureServer/0`; 420 College
  St SE, Lacey). Resolves today.
- **Yelm Community Schools Prop. 1**: `SCHDST` `YELM`. Layer (since #22):
  `https://tconline.co.thurston.wa.us/server/rest/services/Common_Layers/Jurisdictions/FeatureServer/10/query`,
  attr `SchoolDistrictName` (105 Yelm Ave W, Yelm -> `YELM`; 601 4th Ave E,
  Olympia -> `OLYMPIA`; 420 College St SE, Lacey -> `NORTH THURSTON`;
  18346 Albany St SW, Rochester -> `ROCHESTER`). DOR SCH2025 (layer 20)
  agrees at Yelm (`2`).
- **West Thurston Regional Fire Authority Prop. 1**: `RFADST` `FD01`,
  resolved since #22. The fire layer splits WTRFA into two polygons (`DISPATCH_G`
  `FD01`/`FD11`, `CONSOL_DIS` `WTRFA - South Btn`/`WTRFA - North Btn`), so
  neither `FIRDST` nor `FIRE_AUTH` can match one value; both polygons carry
  `CONSOL_NUM` `FD01` and no other polygon does. `geo.js` reads the same
  fire layer, attr `CONSOL_NUM`, `where: "CONSOL_DIS LIKE 'WTRFA%'"` (18346
  Albany St SW, Rochester and 10828 Littlerock Rd SW, Olympia -> `FD01`;
  Lacey, Yelm and Olympia -> no feature, while `FIRDST` still reads `FD03`
  at Lacey from the same layer).
  DOR FIR2025 has two values (`1/WTRFA/1B`, `11/WTRFA/11B`).

## Known gaps

- Page 28 of the local pamphlet carries a stray "Thurston County Fire
  Protection District 12 Proposition No. 1" heading and ballot title over
  Lacey Fire District 3's statements (left over from FD 12's November 2025
  measure). FD 12 is on neither the sample ballot nor the Auditor's
  resolution list, so it is not a measure here.
- Web search was unavailable for most of the research (session budget
  exhausted); sources were fetched directly. JOLT News and Nisqually Valley
  News answered 403 to some fetches. Some race-specific news (LD 22
  primary results, Assessor and Clerk forum coverage) was not retrieved.
- Two of JJ Olson's campaign-site sources are tool-extracted summaries, not
  verbatim copies (the site serves a bot check); their pointer metas say so.
- Thin evidence: Don Hewett (LD 22 Pos. 1) and Jeff Curry (PUD D3) are
  pamphlet-only.
