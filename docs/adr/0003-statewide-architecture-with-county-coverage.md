# Statewide architecture with county-by-county coverage

Voter Lifeboat will be organized as a general product with Washington State
living under `/washington-state`; the root may redirect there while Washington
is the only supported election scope. The experience remains address-first:
the address determines whether the voter is in Washington, which county they
are in, whether that county is fully supported, and which contests belong in
their report and Ballot Brief.

`/washington-state` is a stable public entry route, not the identity of a
particular election. Behind that route, the app should load an explicit Active
Election dataset such as the August 4, 2026 Primary and Special Election, and
report links should carry enough election or data-version information to detect
stale or incompatible reports.
Backwards compatibility with old King County entry links is not required for
the statewide migration, but the new link format should be stable enough to
survive future election and coverage changes without routine redesign.
Routes should stay human-readable for election scope, while report/session
state should live in a versioned encoded payload rather than ad hoc district
query parameters. The payload should carry election id, data version, Coverage
Status, county, resolved Districts, and Values Profile as needed, but must not
include the voter's street address.
Old links should restore exactly the election/data version, Coverage Status,
Districts, and answers encoded in the payload. If the current app data is newer
or coverage has changed, the app may show a non-blocking notice offering to
start over for the latest coverage; it should not auto-upgrade old links.

We chose statewide architecture with county-by-county coverage instead of
renaming the current King County dataset as statewide coverage. For Supported
Counties, the guide may show the voter their local ballot subset. For
Unsupported Counties, the guide may offer a clearly labeled Statewide-Only
Guide covering the complete set of Washington-wide contests for the Active
Election; it must warn that county, city, school, fire, judicial district, and
other local contests may be missing.
King County must remain a fully supported county throughout the migration; the
statewide architecture work should not temporarily remove or degrade the
existing King County guide.

Coverage has three statuses. Full County Coverage means the county is supported
and all required district lookups succeeded. Partial County Coverage means the
county is supported but some local district lookup is missing or failed, so the
guide should show confidently matched contests while warning that local contests
may be omitted. Statewide-Only coverage means the county is unsupported and the
guide is limited to Washington-wide contests.

Washington-wide fallback data should be sourced from Washington State official
sources, not from a county's copy of statewide races. County sources contribute
county and local ballot coverage; state-level official sources are canonical
for contests every Washington voter receives. Unsupported Counties should only
receive Statewide-Only coverage once that state-sourced package exists; until
then they should receive a clear "not covered yet" message rather than a
fallback synthesized from King County data. Statewide-Only coverage should not
be enabled until the state package contains the complete set of statewide
Contests for the Active Election; completing that package is launch-critical
because unsupported counties otherwise cannot receive a useful fallback guide.
Completeness is defined by electorate: every candidate contest and measure
whose electorate is all Washington voters must be present, regardless of which
official state publication carries it.

Data should be organized as independently buildable packages: one state-level
package for Washington-wide sources and one package per Supported County for
county/local sources, dossiers, scores, and scoping. The final Washington app
dataset is assembled from the state package plus whichever county packages are
ready, so adding or fixing one county does not require rewriting every other
county.
The statewide migration should move the existing King County data into the new
county package layout rather than preserving the current layout behind a
compatibility adapter.
Statewide Contests are owned by the state-level package. County packages should
not duplicate statewide contest records or scores, though they may attach
supplemental county pamphlet references or provenance for those contests.
Countywide Contests belong to the relevant county package, not the state
package. Contest scope should distinguish at least Statewide, Countywide, and
District-scoped contests so the current overloaded `ALL` scope does not blur
"all Washington voters" with "all voters in one supported county."

Address lookup should be hybrid. A shared geocode step determines whether the
address is in Washington and which county contains it. Unsupported Counties can
stop there and use Statewide-Only coverage. Supported Counties then use their
own District Adapter to resolve the local district layers needed for county
coverage, allowing King County to keep using King County GIS while future
counties use their own official GIS sources or a shared state source where that
is reliable.
Addresses outside Washington hard stop with a clear unsupported message and do
not enter the Interview.
The public flow should not include a manual county or district picker. After a
successful address lookup, resolved county, Coverage Status, and District data
may be encoded in the URL and accepted later to restore the same state, even on
the public site; that restore path is not a user-facing manual selection flow
and should behave like a normal address-resolved session without extra
confirmation UI.

Local contests require exact resolved scope matches. In Partial County Coverage
the app may include statewide contests, countywide contests when the supported
county is known, and local contests whose required district value was resolved
exactly; it must not infer or guess local contest membership from incomplete
district data.

The Interview should be generated from the voter's Covered Ballot. A voter in a
Supported County may see questions relevant to both statewide and local
contests; a voter using the Statewide-Only Guide should only see Issue Axes
that can affect the statewide contests included in that partial guide.
The Rubric should be package-aware: the state package defines axes needed for
Statewide Contests, county packages may add axes needed for their local
contests, and shared axes should keep stable IDs when they represent the same
meaning.

The Ballot Brief should export only Covered Ballot contest data, preceded by a
short coverage warning that tells the receiving chatbot whether the packet is
Full County Coverage, Partial County Coverage, or Statewide-Only coverage.
The brief should start the chatbot in Orientation Mode: it should welcome the
voter, state what data and coverage limits it has, offer to generate an HTML
report, and wait for the voter to ask before producing that report.

Anonymous Report Records should include election/data-version, Coverage Status,
county, resolved Districts when present, and the Values Profile, while still
excluding the address. Aggregates must be able to distinguish Full County,
Partial County, and Statewide-Only reports.

Large official source artifacts should not be committed when a URL record is
sufficient. For large pamphlet PDFs or similar raw source files, store a small
`.url` text file with the canonical source URL and keep provenance metadata,
rather than adding the binary artifact to the repository. The existing King
County pamphlet PDFs should be replaced during the statewide-architecture
migration by `.pdf.url` pointer files, with extraction scripts adjusted to
download or read those artifacts from an ignored cache when needed.
