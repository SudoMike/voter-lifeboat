# Spokane County Completeness Note

Election: 2026 Washington general election, November 3, 2026 (VoteWA
election 899, county code 32).

As of 2026-10-08 (#21) this package ships in the general at
`coverage: "partial_county"`: `pipeline/election.py` declares it in
`APP_PACKAGES["2026-11-03-general"]["counties"]` with a
`DISTRICT_ADAPTER_LAYERS["spokane"]` entry, and every contest and measure
scope except the Stevens County PUD seat's `PUDDST` is one the Spokane
District Adapter (Census `CONGDST`/`LEGDST`/`CITY` plus `app/src/lib/geo.js`
`COUNTY_LAYERS.spokane`) resolves from an address. Assembly reads
`interim/app-contests.json` and `interim/app-measures.json`, built by
`pipeline/build_spokane_lite_data.py` from the VoteWA candidate list and
Spokane County's online voters' guide on VoteWA.

## What ships

31 contests (16 contested, 15 uncontested) and 20 measures. The Supreme
Court contests are dropped by the builder and ship once, from the statewide
package. No race is shared with another package: every contest ships with
this package's own research.

| Kind | Contests | Contested | Uncontested (info-only) | Scope |
|---|---|---|---|---|
| U.S. Representative (CD 5) | 1 | 1 | 0 | `CONGDST` |
| State Senator / Representative (LD 3, 4, 6, 7, 9) | 12 | 8 | 4 (LD 6 Senate, LD 7 Rep. Pos. 1 and 2, LD 9 Rep. Pos. 1) | `LEGDST` |
| County Commissioner (Districts 2 and 4) | 2 | 1 (D4) | 1 (D2) | `COUNTY_COUNCIL` |
| Assessor, Auditor, Clerk, Prosecuting Attorney, Sheriff, Treasurer | 6 | 3 | 3 (Assessor, Sheriff, Treasurer) | countywide |
| District Court, Positions 1 to 8 | 8 | 2 (Pos. 2, 4) | 6 | countywide |
| Court of Appeals, Division 3, District 1, Position 2 | 1 | 0 | 1 | countywide |
| Stevens County PUD No. 1 Commissioner District 2 | 1 | 1 | 0 | `PUDDST` (unresolvable) |

30 of the 32 contested candidates are scored; the PUD race has no
scorable rubric axis, so its two candidates ship summaries and sources
without scores.

Measures: Liberty Lake Prop 1, Rockford Prop 1, Spangle Props 1 and 2
(`CITY`); Central Valley, Cheney (2), East Valley, Nine Mile Falls (2),
Riverside, Spokane 81 and West Valley (2) school levies (`SCHDST`); Fire
Districts 2, 3, 9 (2), 11 and 12 (`FIRDST`). All 20 are researched and map
to `taxes`; Fire District 3 Prop 1 also maps to `spending` (+1, added by
refutation).

## Pamphlet links

Spokane's dossiers cite VoteWA's online voters' guide
(`voter.votewa.gov/elections/candidate.ashx` and `measure.ashx` pages,
pointers under `raw/votewa/voter-guide/`): spokanecounty.gov answered 403
to scripted requests, so no printed local pamphlet was fetched. Those
citations have no page numbers, so `pamphlet_refs.py` gives no
`pamphlet_pages` and every Spokane record ships with none. The app links
the county's VoteWA guide instead (`app/src/lib/officialLinks.js`
`countyGuides.spokane`,
`https://voter.votewa.gov/genericvoterguide.aspx?e=899&c=32`).

## District scoping

- `SCHDST`: Spokane County `OpenData/Boundary/MapServer/6`, `DISTRCTNAME`
  (`Spokane #81`, `Central Valley #356`), the strings the measures are
  scoped to. DOR SCH2025 (layer 20) agreed with it at every measure's
  check address on 2026-10-08.
- `FIRDST`: `OpenData/Boundary/MapServer/1`, `NAME` (`Fire District 9`).
  Not `CODE` or `DISTRICTID`: Rockford and Spangle (fire service by
  contract) carry a district's `CODE`, and the City of Cheney polygon
  carries Fire District 3's `DISTRICTID`. Cities with their own department
  read `City of Spokane`, `Cheney`, `Airway Heights`; Spokane Valley Fire
  is Fire District 1.
- `PUDDST`: the Stevens County PUD seat (VoteWA district UTL330001) is
  voted on by the PUD's territory inside Spokane County. The only public
  layer near it, Spokane County Water Districts (layer 10, `NAME` `Stevens
  County PUD`), maps water-service areas, not electoral boundaries, so it
  is not used. `spokane/PUDDST` is in `UNRESOLVABLE_SCOPES`
  (`app/src/lib/data-consistency.test.js`); the seat is hidden and those
  voters see the partial-coverage notice.

## Known gaps

- The Stevens County PUD seat (above) never appears on a Spokane ballot.
- The Town of Fairfield (102 E Main St) is inside `Fire District 2` on the
  county fire layer the app uses, but outside every fire district on DOR
  FIR2025 (layer 7), which places the rest of FD 2 correctly. If the town
  is not in FD 2, its voters are shown FD 2 Prop 1 wrongly. Not resolved.
- The VoteWA pointer meta (`raw/votewa/candidate-list.csv.meta.json`)
  pins the research cache's `sha256` and has no `sha256_case_normalized`.
  The director should run `python3 pipeline/fetch_votewa_candidate_list.py
  --election 2026-11-03-general --write-pointer spokane` once, from a cache
  matching that `sha256`, so a later re-fetch that differs only in case
  still passes the builder's check.
- The county elections office URL (`https://www.spokanecounty.gov/elections`,
  printed in the county's primary pamphlet) answers 403 to scripted
  requests, so it was not checked for HTTP 200.
