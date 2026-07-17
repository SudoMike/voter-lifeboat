# Washington Statewide Architecture Plan

This plan implements ADR 0003: Voter Lifeboat becomes a Washington State
architecture under `/washington-state`, with King County preserved as the first
fully supported county and statewide-only fallback enabled only when complete
state-sourced statewide coverage exists.

## Steps

- [ ] Route and app shell
  - Add `/washington-state`.
  - Redirect `/` to `/washington-state`.
  - Keep product name as `Voter Lifeboat`.
  - Do not preserve old King County link compatibility.

- [ ] Data package layout
  - Move current King County data into `data/washington-state/counties/king/...`.
  - Create `data/washington-state/statewide/...`.
  - Assemble final app data from the statewide package plus supported county packages.
  - Keep `data/final/app-data.json` and `app/public/data/app-data.json` as build outputs.

- [ ] Source artifact cleanup
  - Replace committed King County pamphlet PDFs with `.pdf.url` pointer files.
  - Keep provenance metadata.
  - Update extraction scripts to download/read PDFs from an ignored cache.

- [ ] Statewide package
  - Add state-sourced complete statewide contests for the active election.
  - Do not enable statewide-only fallback until this package is complete.
  - Move Supreme Court ownership out of King County package into statewide package.

- [ ] Scope model
  - Replace overloaded `ALL` with explicit scopes: `STATEWIDE`, `COUNTY`, `DISTRICT`.
  - Keep countywide contests in county packages.
  - Require exact district scope matches for local contests.

- [ ] Address and district lookup
  - Shared geocode step determines Washington vs out-of-state and county.
  - Out-of-state addresses hard-stop.
  - Unsupported Washington counties get statewide-only once available.
  - Supported counties use county-specific District Adapters.
  - King County adapter wraps the current King County GIS logic.

- [ ] Coverage statuses
  - Implement `full_county`, `partial_county`, and `statewide_only`.
  - Full county: supported county and all required district lookups resolved.
  - Partial county: supported county, some district lookups missing; show exact matches only.
  - Statewide-only: unsupported county, complete statewide package only.

- [ ] URL state
  - Use `/washington-state` as the stable route.
  - Encode session/report state in one versioned payload.
  - Payload includes election id, data version, coverage status, county, districts, answers.
  - Never include street address.
  - Restored URL state skips address lookup without extra confirmation UI.

- [ ] Package-aware interview
  - Build the active Interview from the Covered Ballot.
  - Statewide-only users only get statewide-relevant axes.
  - County users get statewide and relevant local axes.
  - Rubric axes come from state and county packages with stable shared IDs.

- [ ] Ballot Brief
  - Export only Covered Ballot data.
  - Include coverage warning at the top.
  - Start chatbot in Orientation Mode: welcome, summarize available data, offer an HTML report, and wait for the voter before generating it.

- [ ] Anonymous reports
  - Add election/data version, coverage status, county, districts, and values profile.
  - Continue excluding the address.
  - Update aggregate UI so statewide-only and county reports are not mixed without labels.

- [ ] Verification
  - King County address still produces today's ballot contents.
  - Unsupported Washington county produces statewide-only only after complete state package exists.
  - Out-of-state address hard-stops.
  - URL-restored state works.
  - Clipboard excludes unsupported contests and starts in Orientation Mode.
