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

As of the builder runs on 2026-10-08, the six counties' general packages
are `partial_county` for: Kitsap `PUDDST` (PUD No. 1 District 2), Pierce
`KCDISTCRT` (King County District Court, Southeast Electoral District; the
Pierce `Election_Precincts` layer's `KING_DISTRICT` attribute could resolve
it), Snohomish `DISTCRT` (District Court electoral districts), Spokane
`PUDDST`. Clark and Thurston are `full_county`.

Snohomish shipped on 2026-10-08 (#21) as `partial_county` for `DISTCRT`
alone (`snohomish/DISTCRT` is in `UNRESOLVABLE_SCOPES`): its nine District
Court seats (Cascade, Everett, Evergreen, South) stay hidden. Its South
County Fire RFA measure (`RFADST` `SCRFA`) resolves: `geo.js` reads DOR
FIR2025 (layer 7) `DISTATTRIB` with `where DISTATTRIB = 'SCRFA'`, because
that layer mixes fire-district numbers and RFA codes (see
`counties/snohomish/COMPLETENESS.md`). A layer config may carry such a
`where` when a shared layer holds more than the key means.

Spokane shipped on 2026-10-08 (#21) as `partial_county` for `PUDDST` alone
(`spokane/PUDDST` is in `UNRESOLVABLE_SCOPES`): its Stevens County PUD
seat stays hidden, because the only candidate layer (county Water
Districts) maps water service, not an electoral boundary. Its school and
fire levies resolve from the county's `OpenData/Boundary` layers 6
(`DISTRCTNAME`) and 1 (`NAME`; not `CODE`, which contract towns share). See
`counties/spokane/COMPLETENESS.md`, including the Town of Fairfield fire
district discrepancy with DOR.

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
