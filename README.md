# Voter Lifeboat

A free, public, transparently AI-built interactive voter guide. The current
active election scope is **Washington State** for the **August 4, 2026 Primary
and Special Election**, served under `/washington-state`.

The app asks for a street address, derives county and district context, and
shows the contests Voter Lifeboat can cover for that ballot context. All 39
Washington counties are covered: 28 are `full_county` and 11 are
`partial_county` (a county is partial when it has a commissioner or PUD race
with no queryable official district boundary — those contests are hidden rather
than shown to the wrong voters). The statewide package is complete for this
active election, so every ballot context also gets the statewide contests.

## How it fits together

```
data/washington-state/statewide/      state-level sources, dossiers, scores
data/washington-state/counties/*/     one local package per WA county
data/final/                           generated app data
pipeline/                             package parsing, scoring merge, assembly
app/                                  Vite + React SPA + zero-dep server.js
design-mockup/                        the "Harbor" design system
docs/adr/                             architecture decisions
CONTEXT.md                            domain language
```

Key properties:

- **No runtime AI.** All AI work happens offline in the pipeline; matching is
  transparent client-side arithmetic.
- **Address-first, address-forgotten.** The address goes to the Census geocoder
  through `/api/geocode`; derived county and districts can be stored in report
  links, but the street address is not stored or encoded.
- **Coverage-aware.** Each county's report is marked `full_county` or
  `partial_county`, and the Ballot Brief exports only the Covered Ballot.
- **No accuracy claims.** Built and researched by AI; citations are the check.

## Develop

```bash
cd app
npm install
npm run dev             # Vite dev server (proxies /api to :5000)
npm test
node server.js          # feedback + geocode proxy; serves dist/ after `npm run build`
```

Rebuilding data:

```bash
python3 pipeline/build_votewa_lite_data.py   # most counties, from VoteWA CSV exports
python3 pipeline/merge_scores.py
python3 pipeline/assemble_app_data.py
python3 pipeline/validate_scoring.py         # sanity-check the merged data
```

King and the six original counties (clark, kitsap, pierce, snohomish, spokane,
thurston) have their own `build_<county>_lite_data.py` builders. Other pipeline
stages are documented in `data/washington-state/README.md`.

## Deploy

The repo ships a `Dockerfile` that builds the SPA and runs `server.js` on
`:5000`; feedback and anonymous report JSONL files land on the persistent
`/app/data` mount.

Data corrections: edit package dossiers/scoring under `data/washington-state/`,
then re-run `pipeline/merge_scores.py` and `pipeline/assemble_app_data.py`.
