# Working in this repo

Read these before changing anything, in this order:

1. **`CONTEXT.md`** — the domain language. Use its terms exactly (Contest, not
   race; Report for the on-site page, AI Report for the chatbot's page;
   Candidate Photo, Initials Portrait, Dossier, Covered Ballot, and so on) in
   code identifiers you add, docs, issues, commit messages, and reports back to
   the director. Each entry lists words to avoid. When a task needs a concept
   the glossary lacks, add the entry there first; it is a glossary only, never
   a spec.
2. **`README.md`** — how the data, pipeline, and app fit together, and how to
   build and test.
3. **`docs/adr/`** — architecture decisions. ADR-0002 (pipeline-only
   verification) and ADR-0004 (one dataset per election) constrain most work.
4. **`docs/county-wave-playbook.md`** for county coverage work, and
   `data/washington-state/elections/<id>/counties/king/dossiers/RESEARCH-GUIDE.md`
   for anything that touches a Dossier.

## Conventions

- Run everything from the repo root with `python3`; there is no `python`.
  Pipeline scripts take `--election <id>` (currently `2026-11-03-general`).
- Tests: `python3 -m unittest discover -s pipeline -p "test_*.py"` and
  `cd app && npm test && npm run build`.
- Verification chain after data or resolver changes: the package builder,
  `assemble_app_data.py`, `validate_scoring.py`, `verify_dossiers.py`, then the
  app tests and build.
- Work is tracked in GitHub issues; no pull requests. GitHub access goes
  through the gitignored `.env.github` token (`set -a; . ./.env.github; set +a`
  before any `gh` call); never print it.
- Do not mirror external assets (images, PDFs) into the repo. Link to the
  source and record the pointer under the package's `raw/`.
- Every URL added to code or data was checked live when added; say so in the
  commit or the pointer's `.meta.json`.
