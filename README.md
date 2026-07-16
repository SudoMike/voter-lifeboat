# Voter Lifeboat

A free, public, transparently AI-built interactive voter guide for the
King County (WA) **August 4, 2026 Primary and Special Election**. It
interviews a voter about their values (~3 minutes), looks up the contests on
*their* ballot from their street address, and shows how every candidate and
measure aligns — every score cited, every gap admitted.

Live at: `king-county-voter-lifeboat.openbudgets.app`

## How it fits together

```
data/raw/        verbatim official sources (KCE CSVs, pamphlet PDFs) + provenance
data/interim/    scripted parses: 60 contests, 158 candidates, 7 measures
data/dossiers/   AI-researched, tiered-source, per-candidate research notes
data/scoring/    rubric scores + adversarial refutation pass
data/final/      rubric (14 axes), interview, merged scores, app-data.json
pipeline/        every transformation, in order (see data/README.md)
app/             Vite + React SPA + zero-dep server.js (feedback + reports endpoints)
design-mockup/   the "Harbor" design system the app implements
docs/adr/        why it's built this way (start with 0001 and 0002)
CONTEXT.md       the project's ubiquitous language
```

Key properties (see the ADRs):

- **No runtime AI.** All AI work happened offline in the pipeline; matching
  is transparent client-side arithmetic. The "chat" is a copy-to-clipboard
  Ballot Brief the voter pastes into their own AI.
- **No accounts, no cookies — open data.** The address is geocoded via our
  own `/api/geocode` proxy (the Census geocoder has no CORS headers, so it
  can't be called straight from the browser) and then only coordinates go to
  the King County GIS layers, directly from the browser; the address itself
  is never stored. The finished report lives in the URL hash fragment
  (Report Link). Each completed report also records an anonymous record —
  interview answers + districts — to `data/reports.jsonl` via `/api/report`;
  the full dataset is public at `/api/reports` and visualized on the `#data`
  page (regenerated live per visit for now; a nightly pre-baked report is the
  planned end state).
- **No accuracy claims.** Built and researched by AI, stated up front;
  citations are the check; a report button feeds fixes, deployed by git push.

## Develop

```bash
cd app
npm install
npm run dev             # Vite dev server (proxies /api to :5000)
node server.js          # feedback + geocode proxy; serves dist/ after `npm run build`
```

Rebuilding data: see `data/README.md` for the stage-by-stage pipeline
(`pipeline/*.py`, run with `.venv/bin/python`).

## Deploy (siteplat)

The repo ships a `Dockerfile` (build the SPA, run `server.js` on :5000, feedback
JSONL lands on the persistent `/app/data` mount):

```bash
siteplat add-site \
    --name voter-lifeboat \
    --domain king-county-voter-lifeboat.openbudgets.app \
    --repo <this-repo> \
    --branch main \
    --port 5000
```

Data corrections: edit `data/scoring/` or dossiers, re-run
`pipeline/merge_scores.py` + `pipeline/assemble_app_data.py`, commit, push —
the siteplat poller redeploys in minutes.

Feedback review: `ssh <host> cat '~/siteplat/sites/voter-lifeboat/data/feedback.jsonl'`
