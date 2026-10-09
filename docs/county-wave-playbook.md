# County wave playbook

How one agent takes one Washington county from "Statewide-Only Guide" to a
county package the director can ship in the November 3, 2026 General
Election (`2026-11-03-general`). King is done (#16). This covers the other
38. It was written for issue #20 and dry-run on Pierce through step 3.

Throughout, `E` = `data/washington-state/elections/2026-11-03-general`,
`F` = `data/final/2026-11-03-general`, and `<county>` is the county id used
in `pipeline/election.py` (`grays-harbor`, `pend-oreille`, `walla-walla`,
`san-juan` keep their hyphens). Run everything from the repo root with
`python3` (there is no `python`), and always pass `--election
2026-11-03-general`.

## Contents

1. [Rules that apply to every step](#1-rules-that-apply-to-every-step)
2. [Step 1: Export the VoteWA candidate list](#2-step-1-export-the-votewa-candidate-list)
3. [Step 2: Build the county package](#3-step-2-build-the-county-package)
4. [Step 3: Normalize and plan](#4-step-3-normalize-and-plan)
5. [Step 4: Read the plan: already researched vs new](#5-step-4-read-the-plan-already-researched-vs-new)
6. [Step 5: Research dossiers](#6-step-5-research-dossiers)
7. [Step 6: Score](#7-step-6-score)
8. [Step 7: Refute](#8-step-7-refute)
9. [Step 8: Self-check](#9-step-8-self-check)
10. [Step 9: Report to the director](#10-step-9-report-to-the-director)
11. [Director: verify, assemble, ship](#11-director-verify-assemble-ship)
12. [Partial county coverage and `UNRESOLVABLE_SCOPES`](#12-partial-county-coverage-and-unresolvable_scopes)
13. [Reference](#13-reference)

## 1. Rules that apply to every step

**Write fence.** A county agent writes only under `E/counties/<county>/**`,
plus that county's entries in its builder (`pipeline/build_<county>_lite_data.py`
for clark, kitsap, pierce, snohomish, spokane, thurston; `COUNTY_CONFIG` and
`ELECTION_MEASURES` in `pipeline/build_votewa_lite_data.py` for the other 32).
Never edit:

- another package's `dossiers/` or `scoring/`, even to fix a typo in a race
  you share. Shared research is reused in place (step 4). Report the problem
  instead.
- `E/statewide/**`, anything under `data/washington-state/elections/2026-08-04-primary/`,
  `data/final/`, `app/public/data/`, `pipeline/election.py` `APP_PACKAGES`.
  The director ships counties; agents do not.
- `app/src/**`. A missing GIS layer is reported, not added (section 12).

**Provenance.** Every new file under `data/` is either a raw source (verbatim,
or a `.url` pointer plus `.meta.json` saying how it was fetched) or carries
`derived_from` naming the raw or interim files it came from. See
`data/washington-state/README.md`.

**Interim shape changes need re-assembly.** If you change the shape or
wording of a shipped package's interim files (as #20 did to King's
`interim/contests.json`, moving the seat into `office`), the app data does
not change until the director re-runs `merge_scores.py` and
`assemble_app_data.py`. Say so in your report.

**Never run** `assemble_app_data.py` or `merge_scores.py` yourself. They
rewrite shipped files (`F/`, `app/public/data/`).

## 2. Step 1: Export the VoteWA candidate list

The general's candidate list is VoteWA election **899** ("GENERAL 2026
(11/03/2026) (General)"). Its CSV has no direct URL; the export is a form
post, scripted by `pipeline/fetch_votewa_candidate_list.py`:

```bash
python3 pipeline/fetch_votewa_candidate_list.py --election 2026-11-03-general --refresh --write-pointer <county>
```

This:

1. GETs `https://voter.votewa.gov/candidatelist.aspx?c=<code>&e=899` and
   stops unless the page's County and Election dropdowns show the county and
   election asked for. County codes are in `election.VOTEWA_COUNTY_CODES`:
   mostly alphabetical, but **Thurston is 31 and Snohomish 34**.
2. Posts the form back with the grid's "Export to CSV" field and caches the
   CSV, verbatim, at `data/.cache/votewa/candidatelist-c<code>-e899.csv`
   (gitignored).
3. Writes `E/counties/<county>/raw/votewa/candidate-list.csv.url` and
   `.meta.json` (URL, manual and scripted export steps, byte count,
   `sha256`, row count, the Election Status values found).

Facts about the general export (checked 2026-10-08 on all 38 non-King
county exports, 1,435 rows; #5 recorded the same for the State list):

- **Election Status is blank on every row.** The primary's export said
  `In Primary`; the general's says nothing. `election.VOTEWA_SOURCES` holds
  the filter per election (`("In Primary",)` for the primary, `("",)` for
  the general). If a later export starts filling the column, the builder
  will drop every row and say so in its contest count: re-check the column
  and update `ballot_status`.
- It lists only general-election candidates (top-two survivors plus offices
  filed only for the general) and has no Ballot Order column.
- Supreme Court rows appear in every county's list; the builders drop them
  (the statewide package owns them). PCO rows (District Type `Precinct`)
  are dropped too.

The builders read the cache and refuse to run if it matches neither digest
in the committed meta. If VoteWA changed (a withdrawal, a correction), re-run
the command above, read the diff of the meta and the interim files, and
commit both.

**The export is not byte-reproducible.** Between two fetches of the same
list, VoteWA flips the case of the `District Type` and `District` values row
by row (`"LEGISLATIVE","LEGISLATIVE DISTRICT 10"` in one fetch,
`"Legislative","Legislative District 10"` in the next; Snohomish, 2026-10-08,
same 15,065 bytes, different `sha256`). The parsers upper-case those two
columns before matching, so the meta also records `sha256_case_normalized`:
the sha256 of the parsed rows as compact JSON with those two columns
upper-cased and every other value verbatim (`votewa.case_normalized_sha256`).
The builders accept a cache that matches either `sha256` or
`sha256_case_normalized`; a different name, a dropped row or a reordered row
still stops them. A meta written before this field existed (every county's
as of 2026-10-08) still needs the exact bytes: re-run `--write-pointer` once
on a cache that matches its `sha256` to add the field. The primary keeps its
CSVs verbatim in the package and is not affected.

## 3. Step 2: Build the county package

```bash
# clark, kitsap, pierce, snohomish, spokane, thurston:
python3 pipeline/build_<county>_lite_data.py --election 2026-11-03-general
# every other county except king:
python3 pipeline/build_votewa_lite_data.py --election 2026-11-03-general --county <county>
```

Both write `E/counties/<county>/interim/app-contests.json` and
`app-measures.json`, citing the raw pointer in `derived_from`. The line they
print ends with `UNRESOLVABLE: <layers>` when some scope has no GIS layer
(section 12) and `MEASURES NOT CURATED` while the county's measures are
empty because nobody has transcribed them.

Contest naming and scope come from `pipeline/votewa.py` `classify()`:

| VoteWA District Type | Scope | Notes |
|---|---|---|
| Congressional, Legislative | `CONGDST`, `LEGDST` (Census) | |
| Commissioner, Council | `COUNTY_COUNCIL` with `COUNTY_CONFIG[<county>]["commissioner"]` format | District text `COMMISSIONER DISTRICT ALL COUNTY` means nominated by district, **elected county-wide in the general** (RCW 36.32.040): scope `COUNTY` |
| Countywide, County | `COUNTY` | |
| Judicial | `COUNTY` | Superior Court, Court of Appeals districts and single-district District Courts are whole-county electorates |
| Public Utility | `PUDDST` with the `pud` format; `None` = unresolvable | |
| Port | `PORTDST` with the `port` format | |
| City/Town | `CITY` (Census place name) | |
| anything else | the build stops: `unmapped district type` | add a county override |

**Check every row the generic rules map, against the county's own sample
ballot or local pamphlet**, before trusting it. In the general this matters
more than in the primary:

- Commissioners in most non-charter counties are elected county-wide in the
  general. VoteWA says so either with the `ALL COUNTY` district text or by
  listing the race as `Countywide` (Kitsap). Spokane's five commissioners are
  still elected by district.
- District courts with electoral districts (King, Snohomish: Cascade,
  Everett, Evergreen, South) are not county-wide.
- PUD commissioner races are on almost every county's general list. Check on
  the sample ballot whether the general electorate is the commissioner
  district or the whole PUD.
- A race from a neighbouring county can appear on your list because some of
  your voters vote in it (Pierce lists King County District Court's
  Southeast Electoral District for Pierce-side Auburn). Name it exactly as
  the owning package names it so step 4 finds it.

**County overrides.** For the six counties with their own builder, edit
`general_override(row, unresolvable)` in `pipeline/build_<county>_lite_data.py`:
return `(category, district, office, (layer, value))` for a row, or `None`
for the generic rule. Keep the primary's contest names where the race is
the same, so slugs match and primary dossiers carry forward. For the other
32, adjust `COUNTY_CONFIG[<county>]` (scope formats) and, if a row type
needs naming or scoping the generic rules cannot express, add an override
the same way (`votewa.parse_contests(..., override=...)`). The primary path
of every builder is frozen: after any builder edit, re-run it for the
primary and check that `git status` shows nothing under
`2026-08-04-primary/` (section 11).

**Measures.** VoteWA's candidate list has no measures. Transcribe them from
the county's official local voters' pamphlet or sample ballot:

1. Add raw pointers (`.pdf.url` + `.meta.json`) under
   `E/counties/<county>/raw/<county>/` for the pamphlet or sample ballot.
2. Add the measures: for the six, set
   `GENERAL_MEASURES["2026-11-03-general"] = {"sources": [<raw pointer paths>], "measures": [<app-measures rows>]}`
   in the county builder (row shape: the primary's `measure()` rows in the
   same file); for the other 32, add
   `ELECTION_MEASURES["2026-11-03-general"]["<county>"] = {"measures": [m(...), ...]}`
   in `build_votewa_lite_data.py` (`m()` takes the source URL).
3. Scope each measure to a layer the county's District Adapter resolves
   (`app/src/lib/geo.js` `COUNTY_LAYERS[<county>]`, or Census `CITY`), and
   point-query one address inside the district: geocode it
   (`geocoding.geo.census.gov/geocoder/locations/onelineaddress`), then
   `<layer url>?geometry=<x>,<y>&geometryType=esriGeometryPoint&inSR=4326&spatialRel=esriSpatialRelIntersects&outFields=<attr>&returnGeometry=false&f=json`;
   the value it returns is the scope value. Record the address and result
   in the measure's comment.
4. A county with no measures on its general ballot still gets an entry
   (`"measures": []`), plus an `extra_notes` line naming the official page
   that shows none, so it is never confused with "not curated".

## 4. Step 3: Normalize and plan

```bash
python3 pipeline/normalize_research_inputs.py --election 2026-11-03-general
python3 pipeline/build_research_plan.py <county> --election 2026-11-03-general
```

The normalizer writes `interim/contests.json` and `interim/measures.json`
for every county package that has `app-contests.json` (it never touches
`E/statewide/` in the general). The plan writer prints the contested races
in two lists, and writes `interim/research-plan.json`.

## 5. Step 4: Read the plan: already researched vs new

From the general on, congressional and legislative contests belong to the
county packages (ADR-0004, #9), so a district that crosses a county line is
listed by every county it touches. **Each race is researched once.**
`pipeline/shared_contests.py` identifies a race across packages:

- congressional: `("CONGDST", n)`; legislative: `("LEGDST", n, seat)`,
  whatever each source calls the seat ("Pos. 1", "Position No. 1");
- anything else: the normalized district plus office text, only when the
  district names its jurisdiction.

For each contested race the plan's `shared` field says:

- `researched_in`: `{package, contest_slug, scoring, candidates_missing}`
  when the statewide package, a shipped county (King), or any other county
  package already has a scoring file for the same race. **Do not research
  it.** At assembly the county's contest ships with that package's scoring
  and dossiers (`assemble_app_data.py`, county-owned district contests). If
  `candidates_missing` is not empty, the other package's scoring lacks one
  of your candidates (a name spelled differently, or a roster change):
  report it; do not copy or edit the other package.
- `also_listed_by`: other county packages that list the same race but have
  not researched it. Only one package researches it. The director assigns it
  (default: the county that ships first). If you were not assigned a shared
  race, leave it.

Everything else is yours: county-only legislative districts, county
offices, county-wide and local judicial races, PUD/port/city races, and
local measures. Uncontested races are not in the plan; they ship as the
official ballot entry (or info-only from an empty-score scoring file if you
choose to write `office_does`/`race_blurb` for them).

Each planned candidate also has `carry_forward`: `"primary"` with
`primary_dossier` when a primary dossier exists for the same race and name.
For district races it points at the primary's statewide dossiers (the
primary owned them statewide). Start from it, refresh it, and re-score: the
general's rubric differs (`social` narrowed, `parental-rights` added), so
primary scores are never copied.

## 6. Step 5: Research dossiers

Follow `E/counties/king/dossiers/RESEARCH-GUIDE.md`; it covers every package
in this election. One file per candidate at
`E/counties/<county>/dossiers/<contest-slug>/<candidate-slug>.md` plus
`_contest.md` per contest, and one file per measure at
`E/counties/<county>/dossiers/measures/<measure-slug>.md`. The rules that
trip people up:

- Every factual claim cites a listed source; Tier 1 = pamphlet, candidate's
  own site, filings, votes; Tier 2 = endorsements, established news.
- `evidence_level` honestly: `rich`, `moderate`, `pamphlet-only`.
- **Judges** (Superior, District, Municipal Court, Court of Appeals):
  experience, ratings, notable rulings only. No partisan inference. Never
  research or record positions on `social` or `parental-rights` topics.
- **`social` vs `parental-rights`**: separate headings in Positions. Gender,
  LGBTQ+, sports eligibility, reproductive policy under one; parental
  notification, record access, curricula opt-outs, school services under
  the other. School governance goes under parents and schools, not local
  control.
- **The lone ESSB 6346 vote**: if a legislator's only `taxes` evidence would
  be the floor vote on ESSB 6346 (the 9.9% tax on income over $1M), look for
  a second independent source (another vote, a sponsored bill, a statement, a
  platform plank) and record it if found.

## 7. Step 6: Score

Follow `E/counties/king/scoring/SCORING-GUIDE.md`. Scoring reads only the
dossiers. Output: `E/counties/<county>/scoring/<contest-slug>.json` and
`scoring/measures.json`.

- Read `F/rubric.json` first (15 axes and the categories each applies to).
- Omit an axis without dossier evidence; never infer from party.
- Judges: only `judicial`, `safety`, `experience`.
- `parental-rights` is scored only for State legislative contests and
  measures (scope rule).
- Lone ESSB 6346 vote: magnitude 1, `medium` confidence, unless a second
  independent taxes source exists.
- Uncontested races you chose to describe: a scoring file with empty
  `scores`.

## 8. Step 7: Refute

A second agent, who did not score the contest, re-reads the dossiers and
writes `E/counties/<county>/scoring/refutations/<contest-slug>.json` (and
`refutations/measures.json`) in the SCORING-GUIDE format: a verdict
(`upheld`, `adjust`, `refuted`) for every scored candidate-axis pair, and
`missing` scores with citations. `merge_scores.py` applies the verdicts at
ship time; do not edit scoring files to match them.

## 9. Step 8: Self-check

```bash
python3 pipeline/validate_scoring.py --election 2026-11-03-general
python3 pipeline/verify_dossiers.py <county> --election 2026-11-03-general
python3 -m unittest discover -s pipeline -p "test_*.py"
```

`validate_scoring.py` must print `errors: 0`. `verify_dossiers.py` must show
`errors=0` and `untouched_contests=0`; races researched in another package
are counted as `researched_elsewhere` and must have no copy in your
`dossiers/`.

## 10. Step 9: Report to the director

- The commits, and the output of every command in step 8.
- The builder's line (contests, measures, coverage, UNRESOLVABLE layers).
- Races reused from other packages (from the plan), races you researched,
  and shared races you were assigned.
- Every contest or measure scoped to a layer the District Adapter cannot
  resolve, with the reason (section 12), and any GIS layer you found that
  could resolve it (service URL, attribute, one point query result).
- Anything you noticed outside the fence.

## 11. Director: verify, assemble, ship

1. **Builders are reproducible and the primary is frozen.**

   ```bash
   python3 pipeline/build_<county>_lite_data.py --election 2026-11-03-general   # or build_votewa_lite_data.py --county <county>
   python3 pipeline/build_<county>_lite_data.py --election 2026-08-04-primary
   python3 pipeline/build_votewa_lite_data.py --election 2026-08-04-primary
   python3 pipeline/normalize_research_inputs.py --election 2026-11-03-general
   python3 pipeline/build_research_plan.py <county> --election 2026-11-03-general
   git status --short    # nothing changed: byte-identical
   ```

2. **Research checks:** `validate_scoring.py` (both elections),
   `verify_dossiers.py <county> --election 2026-11-03-general`, the pipeline
   tests, and a read of a sample of dossiers against the guides.
3. **Declare and assemble.** Add the county to
   `APP_PACKAGES["2026-11-03-general"]["counties"]` and its elections office
   URL to `COUNTY_ELECTIONS_URLS` (check it answers HTTP 200), then:

   ```bash
   python3 pipeline/merge_scores.py --election 2026-11-03-general
   python3 pipeline/assemble_app_data.py --election 2026-11-03-general
   python3 pipeline/build_dossier_batches.py --election 2026-11-03-general
   ```

   Assembly ships the county's contests from `app-contests.json`, applying
   its own scoring or, for a race researched elsewhere, the owning package's
   scoring and dossiers.
4. **Two live ballots.** One address in the county's main city and one in a
   different commissioner/council district or special district:

   ```bash
   node pipeline/live_ballot.mjs data/final/2026-11-03-general/app-data.json \
     "930 Tacoma Ave S, Tacoma, WA 98402" "1402 Lake Tapps Pkwy SE, Auburn, WA 98092"
   ```

   It geocodes with the Census API and queries the county's live GIS layers
   through the app's own `lookupBallotContext`. Check: `county`, the
   coverage status, `missing=[]` (any entry is a failed or absent layer),
   the resolved districts, and that every contest and measure listed is on
   that address's official sample ballot. To check before declaring, run
   steps 3 and 4 and then `git checkout -- data/final app/public/data`.

   The Census geocoder's `Current` vintage renamed its layers to `120th
   Congressional Districts` and `2026 State Legislative Districts -
   Lower/Upper` on 2026-10-08; `geo.js` matches them by suffix since #26,
   so non-King addresses resolve `CONGDST` and `LEGDST` again (Snohomish
   live checks, #21).
5. **Declare the adapter's layers.** Add the county to
   `election.DISTRICT_ADAPTER_LAYERS`: `CONGDST`, `LEGDST`, `CITY` plus every
   `key` in `geo.js` `COUNTY_LAYERS[<county>]` (`test_general_app_data.py`
   checks the two agree). The assembler then marks the county
   `partial_county` if any shipped DISTRICT scope uses another layer, even
   if the package claims `full_county`, and prints each such scope.
6. **Pamphlet links.** Add the county's general pamphlet PDF to
   `app/src/lib/officialLinks.js` `pamphletPdfs` as
   `'<county>/<edition>'` (edition = the raw pointer's name, e.g.
   `local-voters-pamphlet`), checked live (200, a PDF, PDF pages equal the
   cited pages). Candidate pages come from the county's own dossiers'
   pamphlet citations; `pamphlet_refs.PAMPHLET_REF` must recognize the
   edition id.
   If the county's dossiers cite VoteWA's online voters' guide instead
   (`candidate.ashx`/`measure.ashx` URLs, no pages), its records ship no
   pages: add the county's guide
   (`voter.votewa.gov/genericvoterguide.aspx?e=<e>&c=<c>`, checked 200) to
   `countyGuides` in the same file, and `pamphletLink` links it (Spokane).
   A county can do both (Pierce: SOS Edition 09 pages for federal and
   legislative candidates, its VoteWA guide for the rest).
   `verify_dossiers.py` rewrites the county's `interim/dossier-audit.json`;
   that file belongs to the research package, so commit it with the
   research or restore it, not with the ship.
   If the elections office URL answers 403 to scripts, use the address
   the county's own pamphlet prints and say so in `election.py`.
7. `cd app && npm ci && npm test && npm run build`. `data-consistency.test.js`
   fails if a shipped DISTRICT scope uses a layer the county's adapter lacks
   and is not in `UNRESOLVABLE_SCOPES` (section 12).

## 12. Partial county coverage and `UNRESOLVABLE_SCOPES`

A county ships `full_county` only when every contest and measure scope is
one its District Adapter resolves from an address: Census `CONGDST`,
`LEGDST`, `CITY`, plus the layers in `app/src/lib/geo.js`
`COUNTY_LAYERS[<county>]` (King: `KING_LAYERS`, mirrored in
`election.DISTRICT_ADAPTER_LAYERS["king"]`).

When a race's district has **no queryable official boundary** (no county or
DOR GIS layer, a PDF-only map, a layer that is not public), the rule is:

1. Keep the race in the package with its true scope (`DISTRICT`, an honest
   layer name such as `PUDDST` or `DISTCRT`, the value the ballot uses). The
   builder adds the layer to `unresolvable` and the package becomes
   `partial_county` with a note naming the layer.
2. The app hides contests whose scope it cannot match, rather than showing
   them to the wrong voters, and tells those voters their ballot may be
   incomplete (`coverageAdvice` → `degraded`).
3. The director adds `'<county>/<LAYER>'` to `UNRESOLVABLE_SCOPES` in
   `app/src/lib/data-consistency.test.js`, with a one-line reason, when the
   county ships. Keep that set short and deliberate.
4. If a layer exists, propose it instead (service URL, attribute, distinct
   values, one live point query); the director adds it to `COUNTY_LAYERS`
   and the race resolves.

Never scope a district race `COUNTY` to make it appear: that shows it to
voters outside the district.

As of the builder runs on 2026-10-08 (#22, #28, #29, #30, #31, #32), the shipped
general packages that are `partial_county` are Spokane and Okanogan (both
`PUDDST`) and Klickitat and Pacific (both `DISTCRT`). Benton,
Clark, Kitsap, Pierce, Snohomish (since #27), Thurston, Whatcom, Yakima,
Skagit, Cowlitz, Grant, Island, Lewis, Franklin, Chelan, Clallam, Grays
Harbor, Mason, Walla Walla, Stevens, Whitman, Douglas, Jefferson, Kittitas,
Asotin, Adams, Skamania, San Juan, Lincoln, Pend Oreille, Ferry,
Wahkiakum, Columbia and Garfield are `full_county`; all thirty-eight ship
with King, so every Washington county ships (#32). A PUD
commissioner is nominated by district but elected by the whole PUD in the
general (RCW 54.12.010(3)), so a countywide PUD's seat is scoped `COUNTY`
(Clark, Kitsap, Thurston), not `PUDDST`.

Before calling a scope unresolvable, look for a precinct-built district
layer from the county Auditor: ArcGIS Online items whose description says
the district is built from voter precincts or precinct portions and VoteWA
district data are the election's own geography (Snohomish
`Court_Districts`, found in #27 after wave 1 missed it). Searching the
county's ArcGIS org (`arcgis.com/sharing/rest/search?q=... orgid:<id>`)
finds them faster than browsing services.

Snohomish shipped on 2026-10-08 (#21) as `partial_county` for `DISTCRT`
alone, and became `full_county` in #27: its nine District Court seats
(Cascade, Everett, Evergreen, South) resolve from the Auditor's
`Court_Districts/FeatureServer/0` layer (services6, `District` =
`Everett District Court`, ...), and the builder scopes the seats to that
string. Its South
County Fire RFA measure (`RFADST` `SCRFA`) resolves: `geo.js` reads DOR
FIR2025 (layer 7) `DISTATTRIB` with `where DISTATTRIB = 'SCRFA'`, because
that layer mixes fire-district numbers and RFA codes (see
`counties/snohomish/COMPLETENESS.md`). A layer config may carry such a
`where` when a shared layer holds more than the key means.

Spokane shipped on 2026-10-08 (#21) as `partial_county` for `PUDDST` alone
(`spokane/PUDDST` is in `UNRESOLVABLE_SCOPES`): its Stevens County PUD
seat stays hidden, because the only candidate layer (county Water
Districts) maps water service, not an electoral boundary. #27 re-searched
(DOR PUD layers 2007-2025, county and Stevens PUD GIS, 2020 precinct
results) and found no authoritative boundary. Its school and
fire levies resolve from the county's `OpenData/Boundary` layers 6
(`DISTRCTNAME`) and 1 (`NAME`; not `CODE`, which contract towns share). See
`counties/spokane/COMPLETENESS.md`, including the Town of Fairfield fire
district discrepancy with DOR.

Pierce shipped on 2026-10-08 (#21) as `full_county`. Its King County
District Court Southeast seats (`KCDISTCRT`), Pierce Transit measure
(`PTBA`) and school measures (`SCHDST`) resolve from attributes of the
`Election_Precincts` layer that `DISTCRT` already reads (`KING_DISTRICT`,
`PIERCE_TRANSIT`, `SCHOOL`). The adapter queries once per key, so the same
layer is queried four times per Pierce address; a shared-layer read would
need a change to `lookupCountyDistricts`. See
`counties/pierce/COMPLETENESS.md`.

Clark, Kitsap and Thurston shipped on 2026-10-08 (#22) as `full_county`.
Each researcher proposed the layer its measures needed and the director
added it after a live point query: Clark `SCHDST` from the county's
`ClarkView_Public/SchoolDistrict/MapServer/0` (`SCHDST`, an integer: `119`
Battle Ground); Kitsap `SCHDST` from `School_District_Outlines/FeatureServer/0`
(`DISTRICT`: `402` South Kitsap, `100-C` Bremerton); Thurston `SCHDST` from
`Common_Layers/Jurisdictions/FeatureServer/10` (`SchoolDistrictName`:
`YELM`, `NORTH THURSTON`) and `RFADST` from the fire layer `FIRDST` and
`FIRE_AUTH` already read, `CONSOL_NUM` with `where CONSOL_DIS LIKE
'WTRFA%'` (`FD01`), because West Thurston RFA is two polygons there and
every other polygon has a `CONSOL_NUM` too. Shared races ship with the
researching package's scoring: Kitsap's CD 6 and LD 26 with Pierce's,
Thurston's CD 10 and LD 2 with Pierce's, CD 3 and LD 20 with Clark's, LD
35 with Kitsap's (13 races). See each county's `COMPLETENESS.md`.

Yakima, Whatcom and Benton shipped on 2026-10-08 (#28) as `full_county`.
Yakima needs only its commissioner layer (Commissioner District 1 is
elected by district, `COUNTY_COUNCIL` `1`); Whatcom's port and PUD seats
are countywide in the general and its Fire District 1 levy reads DOR
FIR2025 (`1`). Benton's PUD is not the whole county (Richland and most of
West Richland are outside it), so its seat is scoped `PUDDST` `Benton PUD`
and resolves from the Auditor's precinct layer
`PrecinctSplits/FeatureServer/6` (`PUD_District`, with `where PUD_District
= 'Benton PUD'` because the field also reads `'<Null>'` and, for precinct
4017, `'Yes'`); its Ki-Be levy reads DOR SCH2025 (`52`). Shared races:
Yakima's CD 4 with Benton's scoring, Benton's LD 14 and LD 15 House seats
with Yakima's, Whatcom's CD 2 with Snohomish's (6 races). The live checks
found that `geo.js` stripped a trailing "City" from the Census place
`BASENAME` (Benton City resolved as `Benton`); it now strips the suffix
from `NAME` only. The bulk builder files Yakima's and Benton's District
Court seats under category `County` (VoteWA District Type `Countywide`);
the category is display-only and `validate_scoring.py` treats the seats as
judicial by slug. Whatcom's override hook in `ELECTION_MEASURES` could
rename them `Judicial`.

Skagit, Cowlitz and Grant shipped on 2026-10-08 (#28, second half) as
`full_county`. Skagit's levies read the DOR layers `COUNTY_LAYERS.skagit`
already listed (FIR2025 `5` at Bow, SCH2025 `311` at La Conner); its PUD No.
1 and Commissioner District 3 seats are countywide in the general. Cowlitz
needs only Census layers (its one measure is Longview's); its commissioner,
District Court and PUD seats are countywide. Grant gained DOR FIR2025
(`FIRDST`, `7` at Coulee City) and CEM2025 (`CEMDST`, `2` at Wilson Creek)
next to HSP2025 (`4` at Soap Lake). Shared races (15): Skagit's CD 2, LD
10 and LD 39 with Snohomish's scoring and LD 40 with Whatcom's; Cowlitz's
CD 3 and LD 20 with Clark's and LD 19 with Thurston's; Grant's CD 4 and LD
16 with Benton's. Grant ships its own county-scoped information-only copy
of the uncontested Court of Appeals III-2 Pos. 1, as Benton does. Skagit's
and Cowlitz's measure records carry their local pamphlet's PDF pages
through the builder's `m(..., pages=)` argument (the bulk builder otherwise
ships measures with no pages); Grant prints no pamphlet and links its
VoteWA guide. Skagit's District Court seats keep category `County`;
Cowlitz's and Grant's overrides make theirs `Judicial`.

Island and Lewis shipped on 2026-10-08 (#29) as `full_county`. Island's
PUD race is Snohomish County PUD No. 1's District 1 seat, which Camano
Island elects with all of Snohomish County; the builder keeps Snohomish's
contest names so it ships with Snohomish's research, scoped `PUDDST`
`53029`. DOR PUD2025 has no Island polygon and the Auditor's precinct layer
(`Geocortex/Elections/MapServer/2`) has no PUD attribute, so `geo.js` reads
its constant `County` attribute with `where PrecinctNa LIKE 'Camano%'`.
The fireworks advisory vote is for unincorporated voters only: `UNINC`
`ISLAND` reads DOR TCA2025 (layer 23) `COUNTYNAME` with `where COUNTYNAME
= 'ISLAND' AND DISTATTRIB NOT IN ('0100','0300','0700')`, the tax code
areas of Oak Harbor, Coupeville and Langley (a city annexation that DOR's
2025 tax code areas do not yet carry would be missed). The Port of South
Whidbey levy reads DOR PRT2025 (layer 16, `S WHIDBEY`). Lewis's PUD No. 1
is the county minus Centralia: its at-large seat is scoped `PUDDST` `1`
through a builder override that keeps the generic contest name, and reads
DOR PUD2025 (layer 17); the Timberland Regional Library levy reads LIB2025
(`L`; Pe Ell, Mossyrock, Napavine and Vader are outside). Shared races (9):
Island's CD 2, LD 10 and the PUD seat with Snohomish's scoring; Lewis's CD
3 and LD 20 with Clark's and LD 19 with Thurston's (Chehalis and Centralia
are LD 20, Pe Ell LD 19). Neither county prints a general pamphlet; both
link their VoteWA guide. A `NAMED` shared-race key such as Island's
`("public utility district 1", "commissioner district 1")` matches any
package that names a PUD seat exactly that way, so check a new county's
research plan for an unintended match.

Franklin, Chelan, Clallam and Grays Harbor shipped on 2026-10-08 (#29, part
2) as `full_county`. Franklin's Port of Pasco elects by district from 2026:
its District 3 seat is `PORTDST` `PoP3`, read from the county portal's
`districts/Special_tax_districts/MapServer/7` `DISTRICT_CODE` (which also
holds the Port of Kahlotus's `PoK1`-`PoK3`); its commissioner race is
`COUNTY_COUNCIL` `COM3`, the value form of the `Commissioner_Districts`
layer the hotfix moved to, and its FPD 3 levy reads DOR FIR2025. Chelan's
Wenatchee SD 246 bonds read DOR SCH2025. Chelan's commissioner layer
(`PW/Commissioner_Districts`, used by the primary only) answered its
metadata but 500ed or timed out on every query on 2026-10-08, so
`COUNTY_LAYERS.chelan` reads `GIS/CM_districts/MapServer/0` (`DIST_NO`, the
same three districts) instead: re-probe every existing layer of a county you
ship. Clallam's District Court 1 and 2 are separate electorates
(`DISTCRT`, the Auditor's `District_Court/FeatureServer/0` `DISTRICT`); its
PUD No. 1 is elected PUD-wide but leaves out the City of Port Angeles, so
the seat is scoped `PUDALL` `1`, and `geo.js` reads it with a layer
`value`: any feature of `PUD_Commissioner_District_dissolve` reports the
constant `'1'`, no feature is no district (not a missing layer). Use
`value` for any presence-only district whose layer has no single attribute
for membership. Grays Harbor's Timberland levy reads DOR LIB2025 (Ocean
Shores is outside) and McCleary SD 65 SCH2025. Shared races (17):
Franklin's CD 4, LD 8 Senate and LD 16 with Benton's scoring, CD 5 with
Spokane's, LD 14 with Yakima's; Chelan's CD 8 and LD 12 with King's, LD 7
Senate with Spokane's; Clallam's and Grays Harbor's CD 6 with Pierce's;
Grays Harbor's LD 19 with Thurston's and LD 24 with Clallam's (Clallam owns
LD 24). Franklin, Chelan and Clallam link their local pamphlets at the cited
PDF page and their VoteWA guides otherwise; Grays Harbor posts no pamphlet
and links its guide. The archived primary scoped Clallam's PUD District 2
race `PUDDST` `1` (the generic parse), which the adapter reads as
commissioner district 1; the primary is frozen, so that stays.

Mason shipped on 2026-10-08 (#30) as `full_county`. The county is split
between two PUDs, each electing its commissioners PUD-wide in the general:
PUD No. 1 (Hood Canal, Hoodsport) and PUD No. 3 (the rest). The seats are
scoped `PUDDST` `1` and `3` and read DOR PUD2025 (layer 17) `DISTATTRIB`.
Its Southside SD 42, McCleary SD 65 and Pioneer SD 402 measures read DOR
SCH2025. McCleary SD 65 straddles the Grays Harbor line, so its bond ships
twice, once per county, each copy scoped to its own county: a voter sees
one. The commissioner and FIRDST layers re-probed alive; neither is used
by a general scope. Shared races (5): CD 6 with Pierce's scoring, LD 35 and
the Court of Appeals II-2 Pos. 1 seat with Kitsap's. Mason links its local
pamphlet at the cited PDF page and its VoteWA guide otherwise.

Walla Walla and Stevens shipped on 2026-10-08 (#30) as `full_county`.
Walla Walla's Dixie SD 101 levy reads DOR SCH2025 (`101`; no Dixie street
address geocodes, so the live check used the interior point -118.153,
46.140) and its Prescott park levy DOR PKR2025 (`PRES`; the district is
joint with Columbia County, which is not shipped). Its Commissioner
District 3 race is elected county-wide in the general and its District
Court is one county-wide district. CD 5 ships with Spokane's scoring, LD 16
with Benton's. Stevens's library levy reads DOR LIB2025 (`L`; the Cities of
Colville and Kettle Falls are outside the district), its Fire District 10
levy DOR FIR2025 and its Nine Mile Falls SD measures DOR SCH2025 (`179J`,
the district's Stevens side). Stevens PUD No. 1 covers the whole county, so
Stevens's copy of the PUD seat is scoped `COUNTY` and ships with Spokane's
research (no applicable axis); Spokane's own copy stays `PUDDST`. CD 5, LD
7 Senate and the two uncontested LD 7 House seats ship with Spokane's
research too. Each county's Court of Appeals seat is its own information-
only copy. Walla Walla links its local pamphlet at the cited page and its
VoteWA guide otherwise; Stevens links its VoteWA guide only.
stevenscountywa.gov answers 403 to a bare scripted User-Agent and 200 to a
browser one, so its elections URL was checked with a browser User-Agent.

Whitman and Douglas shipped on 2026-10-08 (#30) as `full_county`.
Whitman's library levy reads DOR LIB2025 (`L`; Pullman, Rosalia, Garfield,
Endicott, Colton and Uniontown are outside), its four cemetery levies DOR
CEM2025 (`1`-`4`), and Cheney SD 360's two levies DOR SCH2025 (`316`, the
district's thin Whitman strip north of St. John; no street address there
geocodes, so the live check used the interior point -117.70, 47.24). Its
town, fire and park measures read Census places and the DOR FIR2025 and
PKR2025 layers the county already listed. Eight of its measures filed
hardship waivers and are not in the printed pamphlet; they link the VoteWA
guide. The Census geocoder places some Colfax Main St addresses in Albion
(see `counties/whitman/COMPLETENESS.md`). The #37 override in `geo.js` leaves
`CITY` unresolved for Whitman matches with postal city COLFAX and Incorporated
Place Albion, giving Partial County Coverage instead of Albion's Measures.
Douglas's Eastmont SD 206 bonds
read DOR SCH2025 and its Cemetery District 2 levy CEM2025. Its proposed
Rimrock Meadows Fire Protection District No. 9 (formation and three initial
commissioners, voted on inside the proposed boundary only) has no DOR
polygon, since the district does not exist yet: the new key `PROPFIRDST`
reads the county's own `All_Districts_Temporary/MapServer/4` `FireNumber`
(`009`). It is a separate key so the archived primary's Douglas `FIRDST`
scope keeps reading DOR, and `districts.js` shows only `009` for it (the
layer's other values repeat existing fire districts). The service is named
"Temporary": re-probe it before relying on it after this election. Shared
races (13): Whitman's CD 5 and LD 9 Pos. 1 and 2 with Spokane's scoring;
Douglas's CD 4 with Benton's, CD 8 with King's, LD 7 Senate and House with
Spokane's, LD 13 Senate and House with Grant's. Whitman links its local
pamphlet at the cited page and its VoteWA guide otherwise; Douglas prints no
pamphlet and links its VoteWA guide.

Okanogan shipped on 2026-10-08 (#30) as `partial_county` for `PUDDST`
alone (`okanogan/PUDDST` is in `UNRESOLVABLE_SCOPES`). Okanogan County PUD
elects its commissioner PUD-wide, but the PUD is the county minus eight
northeastern precincts (Bodie, Buckhorn Mtn, Chesaw, Myers Creek, San Poil,
Sourdough, Toroda, Wauconda; about 325 voters), which are in Ferry County
PUD No. 1 and vote in its Commissioner #3 race instead (SOS precinct
exports 2020-2024). DOR PUD2025 has one Okanogan polygon over the whole
county and no Auditor precinct layer is public, so both seats keep their
true `PUDDST` scopes and stay hidden; scoping the Okanogan PUD seat
`COUNTY` would show it to the Ferry PUD voters. Its Methow Valley EMS
District levy reads DOR EMS2025 (layer 6, `MV`; the towns of Twisp `TC`
and Winthrop `WC` are outside it and run their own levies, scoped `CITY`),
its Fire District 1 lid lift DOR FIR2025 (`1`) and the Three Rivers
Hospital bonds DOR HSP2025 (`1J`). Commissioner District 3 and both
District Court seats are county-wide in the general. Shared races (4): CD
4 with Benton's scoring, LD 7 Senate and House with Spokane's; its Court
of Appeals III-1 Pos. 2 seat is its own information-only copy. Okanogan
prints no pamphlet and links its VoteWA guide.

Jefferson and Kittitas shipped on 2026-10-08 (#31) as `full_county`.
Jefferson's two measures belong to Clallam-based districts that reach into
its West End: Quillayute Valley SD 402's bonds read DOR SCH2025 (`402`), and
Clallam County Fire District 1's levy reads DOR FIR2025, which numbers the
district's Jefferson part `9` (Jefferson's own Fire District 1 is `1`, so
the scope cannot be `1`). Each copy is scoped to its own county, so Clallam
voters see Clallam's copies and West End voters Jefferson's. Jefferson's
commissioner layer host (`gisweb.jeffcowa.us`) answered 503 on every
request on 2026-10-08; `COUNTY_LAYERS.jefferson` now reads the county's
hosted `FindMyDistrictsInstantApp_WFL1/FeatureServer/1` (`DISTID`, the same
three districts). Only the archived primary's District 3 race uses that key.
Kittitas elects its Upper and Lower District Court judges by district (KCC
2.08.010-.020): `DISTCRT` reads the Auditor's precinct-built
`Court_Districts/FeatureServer/0` `court_district_name` (`Upper District
Court`, `Lower District Court`), and `districts.js` names them as the ballot
does (`Lower Kittitas County District Court`). Both counties' commissioner
and PUD seats are elected county-wide in the general. Shared races (8):
Jefferson's CD 6 with Pierce's scoring and LD 24 with Clallam's; Kittitas's
CD 8 with King's and LD 13 Senate and House with Grant's. Each county's
Court of Appeals seat is its own information-only copy. Both link their
local pamphlet at the cited page (PDF page = printed page) and their VoteWA
guide otherwise.

Klickitat and Pacific shipped on 2026-10-08 (#31) as `partial_county` for
`DISTCRT` alone (`klickitat/DISTCRT` and `pacific/DISTCRT` are in
`UNRESOLVABLE_SCOPES`). Each elects its two District Court judges by
district: Klickitat's East and West courts (Auditor's 2025 Votes by
District: 7,550 and 8,871 voters, precincts split between them), Pacific's
North and South (2022: 23 and 18 precincts, some straddling). No county,
DOR or ArcGIS Online layer of either pair exists, so the four uncontested
seats ship with their true `DISTCRT` scopes and stay hidden. The bulk
builder's override hook cannot report a layer unresolvable, so the
county's `ELECTION_MEASURES` block now names it in `unresolvable_layers`
and the package itself says `partial_county`; use it whenever an override
scopes a race to a layer no adapter reads. Both counties' EMS levies read
DOR EMS2025 (layer 6, `1`; Klickitat's district leaves out Bickleton,
Pacific's North Pacific district the Ocean Beach, Ocosta and North River
school districts, where Ocean Park reads `OB`); Pacific's Fire District 3
and 6 levies read FIR2025, and its Timberland levy is county-wide (LIB2025
has one Pacific polygon). Commissioner and PUD seats in both are elected
county-wide in the general. Pacific's county site (`co.pacific.wa.us`) did
not answer and `pacificcountywa.gov` does not resolve, so Pacific ships no
elections office URL (the app falls back to the statewide office list) and
links its VoteWA guide only; Klickitat links its combined SOS and local
pamphlet (PDF page = printed page) and its guide.

Asotin shipped on 2026-10-08 (#31) as `full_county`. Its PUD No. 1 is
Clarkston and Clarkston Heights, not the county, and elects PUD-wide: the
seat is `PUDDST` `1` and reads DOR PUD2025. Its Rural EMS District No. 2
levy has no DOR EMS polygon (EMS2025's Asotin `1` is EMS District #1, the
same area as Fire District 1, and the archived primary's `EMSDST` `1` scope
for this levy was wrong; the primary is frozen). The new key `RURALEMSDST`
is a presence layer on DOR TCA2025 (layer 23) with `where COUNTYNAME =
'ASOTIN' AND DISTATTRIB IN ('0025','0030','0030F')` and `value: '2'`: the
district's 2025 tax code areas, identified from DOR's levy detail, the
county's rate table and the precinct parts that voted on it. A boundary
change after tax year 2025 would be missed; re-check the TCAs when DOR
publishes 2026. Shared races (11 across the three): Klickitat's CD 4 with
Benton's scoring, LD 14 with Yakima's, LD 17 with Clark's; Pacific's CD 3
with Clark's and LD 19 with Thurston's; Asotin's CD 5 and LD 9 with
Spokane's. Klickitat's and Asotin's Court of Appeals seats are their own
information-only copies. Asotin links its local pamphlet by PDF page (the
printed numbers run 36 ahead) and its VoteWA guide otherwise.

Adams shipped on 2026-10-08 (#31) as `full_county`. `COUNTY_LAYERS.adams`
gained `FIRDST` (DOR FIR2025, layer 7) for Fire District 4's levy beside
`CEMDST` and `PARKDST` (Park District 2's Washtucna Pool levy reads
PKR2025 `2`). Fire District 4 (Ritzville Rural SE) has no address the
Census geocoder matches, so its live check is an interior point,
(-118.02, 47.15), run through `lookupBallotContext` with the Census
coordinates endpoint's geographies for that point. The commissioner and
both District Court seats are elected county-wide. Shared races (7): CD 4
with Benton's scoring, CD 5 and LD 9 Pos. 1/2 with Spokane's, LD 13
Senator and Pos. 1/2 with Grant's; its Court of Appeals seat is its own
information-only copy. Adams prints no local pamphlet, so every record
links its VoteWA guide (`c=01`). Shipping it moved two pipeline fixtures
that used Adams as "a county with no general package" to Garfield
(`test_votewa`, `test_research_inputs`); pick a still-unshipped county
for such fixtures.

Skamania and San Juan shipped on 2026-10-08 (#32) as `full_county`.
Skamania needs no county layer: every scope is `COUNTY` or a Census layer
(the commissioner and PUD seats are nominated by district and elected
county-wide; `COUNTY_COUNCIL` and `WATDST` were re-probed and stay for the
archived primary). Its CD 3 and LD 17 Pos. 1/2 ship with Clark's scoring.
skamaniacounty.gov answers 403 to a bare scripted User-Agent and 200 to full
browser request headers; its pamphlet's PDF pages run 34 behind the printed
ones. `COUNTY_LAYERS['san-juan']` gained `FIRDST`, `PORTDST` and `PARKDST`
(DOR layers 7, 16, 14) and `SWDDST`, a presence layer for the Lopez Solid
Waste Disposal District, which has no DOR polygon: DOR PRT2025 `where:
"DISTATTRIB = 'LOPEZ'"`, `value: 'LOPEZ'` (the research's 425-point grid
showed the Port of Lopez polygon equals the three Lopez precincts that vote
the levy). San Juan's council residency district is a candidate
qualification; the seat is voted on county-wide. Its CD 2 ships with
Snohomish's scoring and LD 40 Pos. 1/2 with Whatcom's.

Lincoln and Pend Oreille shipped on 2026-10-08 (#32) as `full_county`.
Lincoln needs no county layer: every scope is `COUNTY`, CD 5 or LD 9 (its
Commissioner District 3 is elected county-wide), and `CEMDST` (DOR CEM2025)
was re-probed and stays for the archived primary. It prints a local
pamphlet (PDF page = printed page) but has no local measure. Its CD 5 and LD
9 Pos. 1/2 ship with Spokane's scoring. `COUNTY_LAYERS['pend-oreille']`
gained `SCHDST` (DOR SCH2025, `62` for Riverside SD 416-62's strip near Elk)
and a new key `SEWDST`, DOR's sewer-district layer SEW2025 (layer 21), for
the Sacheen Lake Water and Sewer District's levy (`3`; DOR's 2025 levy
detail lists it as the county's only sewer levy); `districts.js` labels the
key "Water and sewer district" and names `3`. Its Hospital District No. 1
bonds read `HOSPDST` `1` (Ione and Metaline Falls are District No. 2). The
commissioner and PUD No. 1 seats are elected county-wide (the PUD is the
whole county). CD 5 and LD 7 Senate and Pos. 1/2 ship with Spokane's
scoring, the Superior Court (Ferry, Pend Oreille, Stevens) Pos. 2 seat with
Stevens's. Its pamphlet's PDF pages run 38 behind the printed ones.

Ferry and Wahkiakum shipped on 2026-10-08 (#32) as `full_county`. Ferry
needs no county layer: every scope is `COUNTY`, CD 5 or LD 7, and its
`COUNTY_COUNCIL` and `EMSDST` layers were re-probed and stay for the
archived primary. Its Ferry County PUD No. 1 #3 seat is scoped `COUNTY`
although DOR PUD2025 leaves out part of Inchelium (tax code area `8888`,
no taxing district): the SOS precinct exports put every PUD race on all 19
precincts. The seat's contest names are Okanogan's, so it ships with
Okanogan's research (where the same seat stays `PUDDST` and hidden); the
ship pass rewrote two display lines of that scoring that spoke of
Okanogan's ballot, so a shared race's `office_does` and candidate summaries
must read right on every ballot that shows them. CD 5 and LD 7 Senate and
Pos. 1/2 ship with Spokane's scoring; its Superior Court (Ferry, Pend
Oreille, Stevens) Pos. 2 and Court of Appeals seats are its own
information-only copies (a package's own scoring file wins over the shared
key). `COUNTY_LAYERS.wahkiakum` gained `FIRDST` (DOR FIR2025, layer 7) for
Fire District 2 (Skamokawa)'s EMS levy (`2`; the Town of Cathlamet has no
fire district feature); the county-wide EMS levy is `COUNTY`. Its
commissioner, PUD No. 1 and District Court seats are elected county-wide.
CD 3 ships with Clark's scoring and LD 19 Pos. 1/2 with Thurston's. Neither
county prints a general pamphlet; both link their VoteWA guide, though
Wahkiakum's carries no county race (its Auditor's sample ballot is the only
official listing).

Columbia and Garfield shipped on 2026-10-08 (#32) as `full_county`, the last
two counties. `COUNTY_LAYERS.columbia` gained `PARKDST` (DOR PKR2025, layer
14) for the Columbia County Park and Recreation Pool District levy (`CPR`;
the Town of Starbuck is in no park district) and Columbia's copy of the
Prescott Joint Park and Recreation District levy (`PRES`, the county's
western strip). Walla Walla ships the same Prescott measure scoped to its own
county, so each voter sees only their county's copy (as with McCleary SD 65,
Grays Harbor/Mason); both lean `taxes` +2. `districts.js` names the PKR2025
codes `CPR`, `PRES` and Walla Walla's `WAIT`. Garfield needs no county layer:
every scope is `COUNTY`, CD 5 or LD 9 (both commissioner seats are elected
county-wide), and `DISTRICT_ADAPTER_LAYERS["garfield"]` is the Census keys
alone; `garfield/COUNTY_COUNCIL` stays in `UNRESOLVABLE_SCOPES` for the
archived primary. Both counties' CD 5 and LD 9 Pos. 1/2 ship with Spokane's
scoring. Columbia's pamphlet PDF pages run one ahead of the printed ones;
Garfield's site answers 403 to scripts, so its records link its VoteWA guide
and its elections office is the SOS directory's link, unchecked. A pamphlet
ref's note must not nest parentheses: `PAMPHLET_REF` closes the note at the
first `)` and reads any later `page N` as another page (Columbia's
Prosecutor ref, fixed in the ship pass). With no county left unshipped, tests
that need an unshipped county use a synthetic one (`test-unshipped`,
`testcounty`), never a real county.

## 13. Reference

### Election facts used here

- VoteWA election value 899 (general), 898 (primary). Ballot-status filter
  per election in `election.VOTEWA_SOURCES`.
- `election.PREDECESSOR["2026-11-03-general"] = "2026-08-04-primary"`.
- Supporting tools: `pipeline/fetch_votewa_candidate_list.py`,
  `pipeline/votewa.py`, `pipeline/shared_contests.py`,
  `pipeline/live_ballot.mjs`.

### WA DOR tax-district layers (re-verified 2026-10-08)

`https://webgis.dor.wa.gov/arcgis/rest/services/Programs/WADOR_PropertyTax/MapServer`
still lists tax year 2025 as its newest group (layer 0). Layer ids shift when
DOR publishes a new tax year: re-list `MapServer?f=json` and repeat these
point queries before each election.

| Layer | Name | Used as | Point query (Census-geocoded address or interior point) | Result `DISTATTRIB` |
|---|---|---|---|---|
| 3 | CEM2025 | `CEMDST` | 10105 SW Bank Rd, Vashon (King) | `1` |
| 6 | EMS2025 | `EMSDST` | 290 E Tessie Ave, Republic (Ferry) | `REP` |
| 6 | EMS2025 | `EMSDST` | interior point (-117.10819, 46.38577), Asotin | `1` |
| 7 | FIR2025 | `FIRDST` | 3801 W Van Giesen St, West Richland (Benton) | `4` |
| 11 | HSP2025 | `HOSPDST` | 714 W Pine St, Newport (Pend Oreille) | `1` |
| 11 | HSP2025 | `HOSPDST` | interior point (-119.70278, 48.00619), Douglas | `1` |
| 12 | LIB2025 | `LIBDST` | 1 NE 7th St, Coupeville (Island) | `L` |
| 14 | PKR2025 | `PARKDST` | 155 W Main St, Washtucna (Adams) | `2` |
| 15 | PRK2025 | not used | 155 W Main St, Washtucna | no feature |
| 20 | SCH2025 | `SCHDST` | 350 Court St, Friday Harbor (San Juan) | `149` |
| 22 | WAT2025 | `WATDST` | interior point (-121.77392, 45.71730), Skamania | `1` |

No id changed, so `COUNTY_LAYERS` was not edited; the `geo.js` comment said
"14 PRK2025", but layer 14 is PKR2025 (park and recreation districts) and
PRK2025 is layer 15. The comment is corrected.

Pierce's own layers, live at 930 Tacoma Ave S, Tacoma: Council
`District_Number` 4, `Fire_Districts` `FIRE_DIS` `TACOMA`,
`Election_Precincts` `PC_DISTRICT` `YES`. At 1402 Lake Tapps Pkwy SE
(Pierce-side Auburn): `PC_DISTRICT` `NO`, `KING_DISTRICT` `YES`.

### Pierce dry run (2026-10-08)

| Step | Command | Wall clock |
|---|---|---|
| 1. Export | `fetch_votewa_candidate_list.py --refresh --write-pointer pierce` | 1.4 s |
| 2. Build | `build_pierce_lite_data.py` | 0.03 s |
| 3a. Normalize | `normalize_research_inputs.py` (all six county packages) | 0.03 s |
| 3b. Plan | `build_research_plan.py pierce` | 0.04 s |

The scripts are not the cost. The agent time went into checking the
generic mapping against the ballot: Pierce needed overrides for its council
names, its District Court (`DISTCRT` `YES`) and the King County District
Court rows.

Result: 43 contests (27 contested, 16 uncontested), 0 measures (not
curated), `partial_county` (`KCDISTCRT`).

Already researched in King's package (5): Congressional District 8; LD 31
State Senator, Representative Pos. 1 and Pos. 2; King County District Court
Southeast Electoral District Judge Position 5.

To research in Pierce (22): CD 6 (also listed by Kitsap), CD 10 (also
Thurston); LD 2 Pos. 1 and 2 (also Thurston); LD 25 Pos. 1 and 2; LD 26
Senator, Pos. 1 and 2 (also Kitsap); LD 27 Pos. 1; LD 28 Pos. 1 and 2;
LD 29 Senator, Pos. 1 and 2; Pierce County Auditor; Prosecuting Attorney;
Council Districts 1, 5 and 7; District Court No. 7 and No. 8. All but four
(LD 28 Pos. 2, Auditor, Prosecuting Attorney, District Court No. 8) have
primary dossiers to carry forward for both candidates.

LD 25, 27, 28 and 29 do not reach King County, so King has no research for
them.

### The other 32 counties (parsed in memory, 2026-10-08)

`build_votewa_lite_data.py`'s generic rules parse 29 of the 32 general
exports. Three stop on rows that need a county override: Chelan (`PUD ALL` /
`PUBLIC UTILITY DIST COMMISSIONER DIST B`), Grant (`Grant County PUD All` /
`Commissioner Dist #B AL`), Douglas (District Type `FIRE`, a fire
commissioner race). Most of the 29 have a PUD race with no PUD layer
(`PUDDST` unresolvable); Franklin also has a port race (`PORTDST`).
