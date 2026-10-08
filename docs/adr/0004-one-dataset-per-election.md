# One dataset per election, archived elections stay read-only

ADR-0003 made `/washington-state` a stable route that loads an explicit
Active Election dataset. When the November 3, 2026 General Election replaced
the August 4, 2026 Primary and Special Election, we had to decide what
happens to the old election. We decided that every election is its own
self-contained dataset, that the newest one is served at the stable route,
and that older ones stay online, read-only, at their own route. The
alternative was one rolling dataset that the general overwrote. It would have
broken every primary report link already shared and would have silently
re-scored old reports against a rubric the voter never answered.

The decisions:

- **Per-election packages and outputs.** Package inputs live under
  `data/washington-state/elections/<id>/` (`statewide/` and
  `counties/<county>/`), generated outputs under `data/final/<id>/`, and the
  app copy at `app/public/data/<id>/app-data.json`. Rubric, interview and
  rubric derivation are hand-authored per election in `data/final/<id>/`,
  copied from the previous election with `.meta.json` provenance when they
  carry over. Nothing is shared between elections at runtime.
- **The `ACTIVE` file names the default election.** Every pipeline script
  reads `data/washington-state/elections/ACTIVE` and accepts
  `--election <id>` to override it. `pipeline/election.py` holds the
  per-election declarations (`ELECTION_META`, `APP_PACKAGES`, `KCE_SOURCES`,
  `PREDECESSOR`, `COUNTY_ELECTIONS_URLS`).
- **An Election Index.** `assemble_app_data.py` writes
  `app/public/data/elections.json` (and the same file in `data/final/`):
  `active` plus one entry per election with app data,
  `{id, app_id, name, day, scope, status, data_version}`, where `status` is
  `active` or `archived`. The app loads the index first, then the
  election's own app data.
- **Routes.** `/washington-state` serves the Active Election;
  `/washington-state/<id>` serves any election in the index. The stable route
  never names an election.
- **Archived elections are read-only.** An archived election's page shows a
  banner, still produces results and Report Links, but writes no Anonymous
  Report Records. `server.js` backs this up by answering 409 to a report
  record for an archived election. An archived election's app data is left
  untouched, so its `data_version` stays stable for old links.
- **Report Links are pinned to their election.** A link carries `e`, the
  app-data `election.id`, and `v`, the `data_version`. That id predates the
  package ids and is never renamed for an election that has shipped: the
  primary's package id is `2026-08-04-primary` but its app id is
  `2026-08-04-primary-special`. The app resolves an election by either id.
- **Rubric axis ids are stable across elections.** An axis that keeps its
  meaning keeps its id. Cross-election comparison (the Results page link to
  the archived ballot) applies an answer only where the other election's
  rubric has the same id; there is no translation table between rubrics.
- **The first split: `social` and `parental-rights`.** The general carries
  I-1 (parental rights in public schools) and I-638 (sex verification for
  girls' school sports), which both landed on the primary's single `social`
  axis. A voter who supports one and opposes the other would have averaged
  to zero and received a confident, wrong lean on both. We kept the `social`
  id, narrowed it to gender, LGBTQ+ and reproductive policy with the same
  pole direction, and added `parental-rights` for parents and public
  schools. Keeping the id keeps old links decodable and keeps the archived
  primary on its own 14-axis rubric. Candidates scored on `social` in the
  primary are re-scored during their general refresh, not copied over.
  Judges are never scored on either axis.

## Consequences

- From the general on, congressional and legislative contests are owned by
  the county packages, even across county lines; the statewide package
  holds only Statewide Contests and statewide measures
  (`APP_PACKAGES[<id>].district_contests`). The county packages that ship
  are declared in `APP_PACKAGES[<id>].counties`, so a package still being
  researched never reaches the app.
- Uncontested contests ship information-only: a scoring file with empty
  `scores`.
- Starting the next election is a runbook, not a migration: see "Archive an
  election and start the next" in `README.md`.
- Splitting or renaming an axis again means a dated section in that
  election's `rubric-derivation.md`, and an update to `compare.js`
  `SOURCE_AXIS_TITLES` so the archived page can name the axes it lacks.
