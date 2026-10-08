# Voter Lifeboat

A free, public, transparently AI-built interactive voter guide. The current
active election scope is **Washington State** for the **November 3, 2026
General Election**, served under `/washington-state`. The archived **August 4,
2026 Primary and Special Election** stays explorable at
`/washington-state/2026-08-04-primary`.

The app asks for a street address, derives county and district context, and
shows the contests Voter Lifeboat can cover for that ballot context. For the
general, the statewide package (Supreme Court races and statewide initiatives)
is complete, and since #32 every one of Washington's 39 counties ships a
county package: 35 `full_county` and 4 `partial_county` (Spokane, Okanogan,
Klickitat, Pacific). An address the app cannot place in a shipped county
would still get a statewide-only guide. In the archived primary all 39 counties
were covered: 28 `full_county` and 11 `partial_county` (a county is partial
when it has a commissioner or PUD race with no queryable official district
boundary — those contests are hidden rather than shown to the wrong voters).

## How it fits together

```
data/washington-state/elections/ACTIVE            id of the Active Election (one line)
data/washington-state/elections/<id>/statewide/   state-level sources, dossiers, scores
data/washington-state/elections/<id>/counties/*/  one local package per WA county
data/final/<id>/                                  rubric, interview, merged scores, app-data.json
data/final/elections.json                         Election Index (copy of the app's)
app/public/data/<id>/app-data.json                the file the app loads for <id>
app/public/data/elections.json                    Election Index: active id + every election
pipeline/                                         package parsing, scoring merge, assembly
pipeline/election.py                              per-election declarations
app/                                              Vite + React SPA + zero-dep server.js
design-mockup/                                    the "Harbor" design system
docs/adr/                                         architecture decisions
CONTEXT.md                                        domain language
```

Each election is its own dataset (ADR-0004). `/washington-state` serves the
election named `active` in `elections.json`; `/washington-state/<id>` serves
any election listed there. Archived elections are read-only: a banner, no
Anonymous Report Records (`server.js` answers 409). Report links carry the
election's app-data `election.id` and `data_version`, so an old link opens
the election it was made for. Rubric axis ids stay stable across elections;
the general split the primary's `social` axis into `social` and
`parental-rights` (see `data/final/2026-11-03-general/rubric-derivation.md`).

Key properties:

- **No runtime AI.** All AI work happens offline in the pipeline; matching is
  transparent client-side arithmetic.
- **Address-first, address-forgotten.** The address goes to the Census geocoder
  through `/api/geocode`; derived county and districts can be stored in report
  links, but the street address is not stored or encoded.
- **Coverage-aware.** Each report is marked `full_county`,
  `partial_county` or `statewide_only`, and the Ballot Brief exports only the
  Covered Ballot.
- **No accuracy claims.** Built and researched by AI; citations are the check.

## Develop

```bash
cd app
npm install
npm run dev             # Vite dev server (proxies /api to :5000)
npm test
node server.js          # feedback + geocode proxy; serves dist/ after `npm run build`
```

Rebuilding data (each script takes `--election <id>`; the default is the id in
`data/washington-state/elections/ACTIVE`):

```bash
python3 pipeline/build_votewa_lite_data.py   # most counties, from VoteWA CSV exports
python3 pipeline/merge_scores.py
python3 pipeline/assemble_app_data.py        # also rewrites app/public/data/elections.json
python3 pipeline/validate_scoring.py         # sanity-check the merged data
python3 -m unittest discover -s pipeline -p "test_*.py"
```

King and the six original counties (clark, kitsap, pierce, snohomish, spokane,
thurston) have their own `build_<county>_lite_data.py` builders. Other pipeline
stages are documented in `data/washington-state/README.md`.

## Archive an election and start the next

The runbook used to move from the primary to the general. `<old>` is the
election being archived, `<new>` the next one.

1. Add `<new>` to `pipeline/election.py`: `ELECTION_META` (`app_id`, name,
   day, scope, `statewide_complete`), `APP_PACKAGES` (`statewide_ballot`,
   `counties: []` until a county is ready, `district_contests`),
   `KCE_SOURCES` (King County Elections `eid` and raw file names),
   `PREDECESSOR[<new>] = <old>` (research plans carry dossiers forward), and
   `COUNTY_ELECTIONS_URLS` for counties as they ship. Never change an
   `app_id` that has shipped: report links carry it.
2. Create the package skeleton under
   `data/washington-state/elections/<new>/` (`statewide/`,
   `counties/<county>/`, each with `raw/`, `interim/`, `dossiers/`,
   `scoring/`).
3. Copy `rubric.json`, `interview.json` and `rubric-derivation.md` from
   `data/final/<old>/` to `data/final/<new>/`, each with provenance
   (`.meta.json` siblings, or `derived_from` inside the JSON) naming the file
   it was copied from and any raw source behind an edit. If the rubric
   changes, add a dated section to the new `rubric-derivation.md` and keep
   existing axis ids where the meaning is unchanged.
4. Write `<new>` into `data/washington-state/elections/ACTIVE`.
5. Run `python3 pipeline/merge_scores.py` and
   `python3 pipeline/assemble_app_data.py`. The latter writes
   `app/public/data/<new>/app-data.json` and rewrites `elections.json`, which
   marks `<new>` active and `<old>` archived. An election with no contests yet
   shows a notice page that links to the archived guide.
6. Add the new election's official links and wording to
   `app/src/lib/officialLinks.js` (keyed by app-data `election.id`). If the
   rubric changed, update `SOURCE_AXIS_TITLES` in `app/src/lib/compare.js`
   (`compare.test.js` pins it to the shipped data).
7. Leave `<old>`'s package, `data/final/<old>/` and its app data untouched
   from here on, so its `data_version` stays stable for old links. Running
   `assemble_app_data.py --election <old>` stamps a new `data_version` (the
   current commit), so do it only for a correction that is worth showing old
   links a "data updated" notice.
8. Run `cd app && npm test && npm run build` and the pipeline tests.

## Deploy

The repo ships a `Dockerfile` that builds the SPA and runs `server.js` on
`:5000`; feedback and anonymous report JSONL files land on the persistent
`/app/data` mount.

Data corrections: edit package dossiers/scoring under
`data/washington-state/elections/<id>/`,
then re-run `pipeline/merge_scores.py` and `pipeline/assemble_app_data.py`.
