"""Election-scoped paths shared by every pipeline script.

Each election is a self-contained data package:

  data/washington-state/elections/<id>/{statewide,counties/*}   package inputs
  data/final/<id>/                                              generated outputs
  app/public/data/<id>/app-data.json                            app copy

Scripts take ``--election <id>``; without it they use the active election
named in ``data/washington-state/elections/ACTIVE`` (a one-line file).
"""

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ELECTIONS = ROOT / "data/washington-state/elections"
ACTIVE_FILE = ELECTIONS / "ACTIVE"
FINAL_ROOT = ROOT / "data/final"
APP_DATA_ROOT = ROOT / "app/public/data"

# Display metadata for each election, keyed by package id. `app_id` is the id
# baked into app-data.json and report links (codec.js); it predates the
# package ids and must not change for an election that has shipped.
# `statewide_complete` is a declared coverage fact: True once every Statewide
# Contest for the election is in its app data (app-data `coverage`).
ELECTION_META = {
    "2026-08-04-primary": {
        "app_id": "2026-08-04-primary-special",
        "name": "August 4, 2026 Primary and Special Election",
        "day": "2026-08-04",
        "scope": "Washington State",
        "statewide_complete": True,
    },
    "2026-11-03-general": {
        "app_id": "2026-11-03-general",
        "name": "November 3, 2026 General Election",
        "day": "2026-11-03",
        "scope": "Washington State",
        "statewide_complete": True,
    },
}


# Which packages each election's app data is assembled from, and who owns
# congressional/legislative (district) contests.
#
# `statewide_ballot`: True when statewide/interim/{contests,measures}.json is
#   the ballot source for Statewide Contests and measures (hand-built, with
#   explicit scope). The primary predates this: its Supreme Court contests
#   come from King's interim files, and its statewide contests.json holds
#   research-only deduplicated district contests.
# `counties`: county packages declared complete enough to ship, in order.
#   None keeps the primary's rule (King's interim files plus every county
#   package with interim/app-*.json). merge_scores.py merges scoring only
#   from the statewide package and these counties.
# `district_contests`: "statewide" when normalize_research_inputs.py writes
#   deduplicated congressional/legislative contests into the statewide
#   package (the primary); "county" when they stay in the county packages
#   (the general onward, see statewide/COMPLETENESS.md).
APP_PACKAGES = {
    "2026-08-04-primary": {
        "statewide_ballot": False,
        "counties": None,
        "district_contests": "statewide",
    },
    "2026-11-03-general": {
        "statewide_ballot": True,
        "counties": ["king", "snohomish", "spokane", "pierce", "clark", "kitsap", "thurston", "yakima", "whatcom",
                     "benton", "skagit", "cowlitz", "grant", "island", "lewis", "franklin", "chelan", "clallam",
                     "grays-harbor", "mason", "walla-walla", "stevens", "whitman", "douglas", "okanogan",
                     "jefferson", "kittitas"],
        "district_contests": "county",
    },
}


# The District layers each shipped county's District Adapter resolves from
# an address: app/src/lib/geo.js KING_LAYERS for King; for any other county
# the Census layers (CONGDST, LEGDST, CITY) plus COUNTY_LAYERS[<county>]
# (test_general_app_data.py keeps each entry equal to geo.js).
# assemble_app_data.py gives a county `full_county` coverage only when every
# DISTRICT scope it ships uses one of these layers (and, for a non-King
# county, its package also claims full_county).
DISTRICT_ADAPTER_LAYERS = {
    "king": ("CONGDST", "LEGDST", "KCCDST", "SCCDST", "JUDDST", "FIRDST", "SCHDST", "CITY", "CEMDST"),
    "snohomish": ("CONGDST", "LEGDST", "CITY", "PUDDST", "SCHDST", "FIRDST", "HOSPDST", "LIBDST", "RFADST", "DISTCRT"),
    "spokane": ("CONGDST", "LEGDST", "CITY", "COUNTY_COUNCIL", "PTBA", "LIBDST", "SCHDST", "FIRDST", "PARKDST"),
    "pierce": ("CONGDST", "LEGDST", "CITY", "COUNTY_COUNCIL", "FIRDST", "DISTCRT", "KCDISTCRT", "PTBA", "SCHDST"),
    "clark": ("CONGDST", "LEGDST", "CITY", "COUNTY_COUNCIL", "PUDDST", "FIRDST", "SCHDST"),
    "kitsap": ("CONGDST", "LEGDST", "CITY", "COUNTY_COUNCIL", "FIRDST", "SCHDST"),
    "thurston": ("CONGDST", "LEGDST", "CITY", "COUNTY_COUNCIL", "PUDDST", "FIRDST", "FIRE_AUTH", "RFADST", "SCHDST"),
    "yakima": ("CONGDST", "LEGDST", "CITY", "COUNTY_COUNCIL", "FIRDST"),
    "whatcom": ("CONGDST", "LEGDST", "CITY", "PORTDST", "FIRDST", "HOSPDST"),
    "benton": ("CONGDST", "LEGDST", "CITY", "COUNTY_COUNCIL", "FIRDST", "PUDDST", "SCHDST"),
    "skagit": ("CONGDST", "LEGDST", "CITY", "COUNTY_COUNCIL", "FIRDST", "HOSPDST", "SCHDST"),
    "cowlitz": ("CONGDST", "LEGDST", "CITY", "COUNTY_COUNCIL"),
    "grant": ("CONGDST", "LEGDST", "CITY", "COUNTY_COUNCIL", "HOSPDST", "FIRDST", "CEMDST"),
    "island": ("CONGDST", "LEGDST", "CITY", "COUNTY_COUNCIL", "LIBDST", "PUDDST", "PORTDST", "UNINC"),
    "lewis": ("CONGDST", "LEGDST", "CITY", "COUNTY_COUNCIL", "FIRDST", "PUDDST", "LIBDST"),
    "franklin": ("CONGDST", "LEGDST", "CITY", "COUNTY_COUNCIL", "PORTDST", "FIRDST"),
    "chelan": ("CONGDST", "LEGDST", "CITY", "COUNTY_COUNCIL", "SCHDST"),
    "clallam": ("CONGDST", "LEGDST", "CITY", "COUNTY_COUNCIL", "PUDDST", "FIRDST", "DISTCRT", "SCHDST", "PUDALL"),
    "grays-harbor": ("CONGDST", "LEGDST", "CITY", "FIRDST", "LIBDST", "SCHDST"),
    "mason": ("CONGDST", "LEGDST", "CITY", "COUNTY_COUNCIL", "FIRDST", "PUDDST", "SCHDST"),
    "walla-walla": ("CONGDST", "LEGDST", "CITY", "COUNTY_COUNCIL", "SCHDST", "PARKDST"),
    "stevens": ("CONGDST", "LEGDST", "CITY", "COUNTY_COUNCIL", "FIRDST", "LIBDST", "SCHDST"),
    "whitman": ("CONGDST", "LEGDST", "CITY", "COUNTY_COUNCIL", "FIRDST", "PARKDST", "CEMDST", "LIBDST", "SCHDST"),
    "douglas": ("CONGDST", "LEGDST", "CITY", "FIRDST", "HOSPDST", "SCHDST", "CEMDST", "PROPFIRDST"),
    # Okanogan's two PUD seats stay PUDDST, which no layer resolves (see
    # app/src/lib/data-consistency.test.js UNRESOLVABLE_SCOPES), so the
    # county ships partial_county.
    "okanogan": ("CONGDST", "LEGDST", "CITY", "FIRDST", "HOSPDST", "EMSDST"),
    "jefferson": ("CONGDST", "LEGDST", "CITY", "COUNTY_COUNCIL", "CEMDST", "FIRDST", "SCHDST"),
    "kittitas": ("CONGDST", "LEGDST", "CITY", "COUNTY_COUNCIL", "FIRDST", "DISTCRT"),
    # Klickitat's East/West and Pacific's North/South District Court seats
    # stay DISTCRT, which no layer resolves (see
    # app/src/lib/data-consistency.test.js UNRESOLVABLE_SCOPES), so both
    # counties ship partial_county.
    "klickitat": ("CONGDST", "LEGDST", "CITY", "COUNTY_COUNCIL", "FIRDST", "EMSDST"),
    "pacific": ("CONGDST", "LEGDST", "CITY", "FIRDST", "EMSDST"),
    "asotin": ("CONGDST", "LEGDST", "CITY", "EMSDST", "PUDDST", "RURALEMSDST"),
}


# King County Elections (KCE) raw sources per election, under
# counties/king/raw/kce/ (read by parse_candidates.py). `eid` is KCE's own
# election id in candidates.aspx?eid= / ballotmeasures.aspx?eid=.
# `csv_ballot_order`: take ballot order from the CSV's Ballot Order column
# (the primary's ballot-specific CSV) rather than from the eid list order.
# `schema` 1 is the primary's frozen output shape; 2 adds owner/scope hints
# and measure details (see parse_candidates.py).
KCE_SOURCES = {
    "2026-08-04-primary": {
        "eid": 54,
        "candidates_html": "candidates-eid54.html",
        "measures_html": "ballotmeasures-eid54.html",
        "candidates_csv": "2026-primary-candidates.csv",
        "csv_ballot_order": True,
        "schema": 1,
    },
    "2026-11-03-general": {
        "eid": 55,
        "candidates_html": "candidates-eid55.html",
        "measures_html": "ballotmeasures-eid55.html",
        "candidates_csv": "2026-candidates.csv",
        "csv_ballot_order": False,
        "schema": 2,
    },
}

# VoteWA candidate list (voter.votewa.gov/candidatelist.aspx) per election,
# read by build_votewa_lite_data.py and the county builders.
# `e`: VoteWA's election dropdown value (candidatelist.aspx?e=).
# `ballot_status`: the "Election Status" values whose rows are printed on this
#   election's ballot. The primary's export marks them 'In Primary'. The
#   general's export leaves the column blank for every row (checked on
#   2026-10-08 for c=99 and every county code exported since), so the general
#   keeps rows whose status is ''.
# `verbatim_csv`: True when each county's export is committed verbatim at
#   counties/<county>/raw/votewa/candidate-list.csv (the primary). Otherwise
#   the committed raw source is the pointer pair candidate-list.csv.url +
#   .meta.json (sha256 pinned) and the CSV itself is cached in data/.cache/
#   by fetch_votewa_candidate_list.py.
VOTEWA_SOURCES = {
    "2026-08-04-primary": {
        "e": 898,
        "label": "PRIMARY 2026",
        "dropdown_label": "PRIMARY 2026 (08/04/2026) (Primary)",
        "ballot_status": ("In Primary",),
        "verbatim_csv": True,
        "notes": "Election Status 'In Primary' marks races printed on the Aug 4, 2026 primary ballot.",
    },
    "2026-11-03-general": {
        "e": 899,
        "label": "GENERAL 2026",
        "dropdown_label": "GENERAL 2026 (11/03/2026) (General)",
        "ballot_status": ("",),
        "verbatim_csv": False,
        "notes": "Official county candidate filing data for the November 3, 2026 general. The 'Election Status' column is blank for every row in the general export, and the export lists only general-election candidates (top-two survivors of partisan and judicial primaries plus offices filed directly for the general). The CSV has no Ballot Order column; the grid's Ballot Order is HTML-only.",
    },
}

# VoteWA county dropdown values (candidatelist.aspx?c=) and labels, read from
# the page's County dropdown on 2026-10-08. Mostly alphabetical, but not
# entirely: Thurston is 31 and Snohomish 34. 99 is "State".
VOTEWA_COUNTY_CODES = {
    "adams": "01", "asotin": "02", "benton": "03", "chelan": "04",
    "clallam": "05", "clark": "06", "columbia": "07", "cowlitz": "08",
    "douglas": "09", "ferry": "10", "franklin": "11", "garfield": "12",
    "grant": "13", "grays-harbor": "14", "island": "15", "jefferson": "16",
    "king": "17", "kitsap": "18", "kittitas": "19", "klickitat": "20",
    "lewis": "21", "lincoln": "22", "mason": "23", "okanogan": "24",
    "pacific": "25", "pend-oreille": "26", "pierce": "27", "san-juan": "28",
    "skagit": "29", "skamania": "30", "thurston": "31", "spokane": "32",
    "stevens": "33", "snohomish": "34", "wahkiakum": "35", "walla-walla": "36",
    "whatcom": "37", "whitman": "38", "yakima": "39",
}


def votewa_county_label(county_id: str) -> str:
    """The County dropdown's label for a county id ('grays-harbor' -> 'Grays Harbor')."""
    return county_id.replace("-", " ").title()


# Each Supported County's elections office site, per election, carried into
# app data as `coverage.supported_counties[].elections_url` (the results
# footer links it). Checked live (HTTP 200) when added. Add counties as their
# packages ship; the primary predates this field and is left without it.
COUNTY_ELECTIONS_URLS = {
    "2026-11-03-general": {
        "king": "https://kingcounty.gov/en/dept/elections",
        # Snohomish County Auditor, Elections & Voter Registration (200, 2026-10-08).
        "snohomish": "https://www.snohomishcountywa.gov/224/Elections-Voter-Registration",
        # Spokane County Auditor, Elections: the address the county's own
        # 2026 primary voters' pamphlet prints. It answers 403 (Cloudflare) to
        # scripted requests (2026-10-08), so its 200 is unchecked here.
        "spokane": "https://www.spokanecounty.gov/elections",
        # Pierce County Auditor, Elections. piercecountywa.gov answers 403
        # (Cloudflare) to scripted requests (2026-10-08; http://piercecountywa.gov/elections
        # 301s to this address), so its 200 is unchecked here.
        "pierce": "https://www.piercecountywa.gov/elections",
        # Clark County Elections (200, 2026-10-08; clark.wa.gov/auditor/elections
        # answers 404).
        "clark": "https://clark.wa.gov/elections",
        # Kitsap County Auditor, Elections (200 text/html with the page title
        # 'Kitsap County Elections', 2026-10-08; kitsap.gov's WAF answered 403
        # only to scripted requests for its pamphlet PDFs).
        "kitsap": "https://www.kitsap.gov/auditor/Pages/Elections.aspx",
        # Thurston County Auditor, Elections (200, 2026-10-08).
        "thurston": "https://www.thurstoncountywa.gov/departments/auditor/elections",
        # Yakima County Auditor, Elections (200, 2026-10-08; the old /149/Elections
        # now redirects to District Court Probation).
        "yakima": "https://www.yakimacounty.us/170/Elections",
        # Whatcom County Auditor, Elections. whatcomcounty.us answers 403
        # (Cloudflare) to scripted requests (2026-10-08), so its 200 is
        # unchecked here; this is the Elections page the county's own primary
        # measure listings were cited from (accessed 2026-07-17).
        "whatcom": "https://www.whatcomcounty.us/2794/Elections",
        # Benton County Auditor, Elections (200, 2026-10-08;
        # bentoncountywa.gov/elections 302s here).
        "benton": "https://www.bentoncountywa.gov/government/elected_officials/auditor/elections/index.php",
        # Skagit County Auditor, Elections and Voting (200, 2026-10-08;
        # skagitcountywa.gov/elections serves the same page).
        "skagit": "https://www.skagitcountywa.gov/government/auditor-s-office/elections-and-voting/",
        # Cowlitz County Auditor, Elections (200, 2026-10-08; the page that
        # links the general's local voters' pamphlet).
        "cowlitz": "https://www.co.cowlitz.wa.us/2357/Elections",
        # Grant County Auditor, Elections (200, 2026-10-08; grantcountywa.gov/
        # elections answers 404, and /1374/Current-Election sits under it).
        "grant": "https://www.grantcountywa.gov/270/Elections",
        # Island County Auditor, Elections & Voter Registration (200, 2026-10-08;
        # islandcountywa.gov/elections 301s; the page links VoteWA's guide).
        "island": "https://www.islandcountywa.gov/423/Elections-Voter-Registration",
        # Lewis County Elections (200, 2026-10-08; the Auditor's elections site,
        # whose /current-election/ page links VoteWA's guide;
        # lewiscountywa.gov/offices/auditor/elections/ answers 404).
        "lewis": "https://elections.lewiscountywa.gov/",
        # Franklin County Auditor, Elections (200, 2026-10-08; the page that
        # links the general's local voters' pamphlet).
        "franklin": "https://www.franklincountywa.gov/Elections",
        # Chelan County Elections (200, 2026-10-08, "Elections - Home"; its
        # November 3, 2026 General Election page sits under it).
        "chelan": "https://www.co.chelan.wa.us/elections",
        # Clallam County Auditor, Elections & Voter Registration (200,
        # 2026-10-08; clallamcountywa.gov/elections 301s here).
        "clallam": "https://www.clallamcountywa.gov/162/Elections-Voter-Registration",
        # Grays Harbor County Auditor, Elections (200, 2026-10-08; the
        # Auditor's current_election.php, which links VoteWA's guide, sits
        # beside it).
        "grays-harbor": "https://www.graysharbor.us/government/Auditors/elections.php",
        # Mason County Auditor, Elections (200, 2026-10-08;
        # masoncountywa.gov/elections redirects here, and the Current Election
        # page that links the pamphlet and VoteWA's guide sits beside it).
        "mason": "https://www.masoncountywa.gov/departments/auditor/elections/index.php",
        # Walla Walla County Auditor, Current Election (200, 2026-10-08; the
        # page that links the general's local voters' pamphlet and sample
        # ballot).
        "walla-walla": "https://www.wwcowa.gov/government/auditor/current_election.php",
        # Stevens County Auditor, Elections: the page the SOS county elections
        # offices directory links (vote.stevenscountywa.gov serves the same
        # site). stevenscountywa.gov answers 403 to scripted requests with a
        # bare User-Agent and 200 to a browser User-Agent (2026-10-08), so a
        # plain scripted check cannot verify it.
        "stevens": "https://www.stevenscountywa.gov/20911/Elections",
        # Whitman County Auditor, Current Election (200, 2026-10-08; the page
        # that links the general's local voters' pamphlet and sample ballot).
        "whitman": "https://www.whitmancounty.gov/172/Current-Election",
        # Douglas County Auditor, Current Election (200, 2026-10-08; the page
        # that links the general's sample ballot and measure resolutions).
        "douglas": "https://www.douglascountywa.gov/206/Current-Election",
        # Okanogan County Auditor, Elections (200 text/html, "Elections |
        # Okanogan County, WA", 2026-10-08; the package's
        # raw/okanogan/elections-page.html.url).
        "okanogan": "https://www.okanogancounty.gov/337/Elections",
        # Jefferson County Auditor, Elections (200 text/html, 2026-10-08; the
        # page that links the general's local voters' pamphlet, sample ballot
        # and measure resolutions; the package's raw/jefferson/elections.html.url).
        "jefferson": "https://www.co.jefferson.wa.us/1266/Elections",
        # Kittitas County Auditor, Elections (200 text/html, 2026-10-08; the
        # page that links the general's "General Pamphlet" and sample ballot).
        "kittitas": "https://www.co.kittitas.wa.us/auditor/elections/default.aspx",
    },
}


def county_elections_url(election_id: str, county_id: str) -> str | None:
    return COUNTY_ELECTIONS_URLS.get(election_id, {}).get(county_id)


# The election whose dossiers an election's research plan carries forward
# (build_research_plan.py matches contest slug + candidate name).
PREDECESSOR = {
    "2026-11-03-general": "2026-08-04-primary",
}


def active_election() -> str:
    return ACTIVE_FILE.read_text().strip()


def add_election_arg(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--election", default=None,
        help="election package id (default: contents of data/washington-state/elections/ACTIVE)",
    )


def resolve(election_id: str | None = None) -> str:
    election_id = election_id or active_election()
    if not (ELECTIONS / election_id).is_dir():
        raise SystemExit(f"unknown election {election_id!r}: no {ELECTIONS / election_id}")
    return election_id


def from_argv(argv=None) -> str:
    """Resolve ``--election`` for scripts that take no other arguments.

    Unknown arguments are ignored so importing a script under a test runner
    does not trip over the runner's own argv.
    """
    parser = argparse.ArgumentParser(add_help=False)
    add_election_arg(parser)
    args, _ = parser.parse_known_args(sys.argv[1:] if argv is None else argv)
    return resolve(args.election)


class Election:
    """Paths for one election package."""

    def __init__(self, election_id: str | None = None):
        self.id = resolve(election_id)
        self.root = ELECTIONS / self.id
        self.state = self.root / "statewide"
        self.counties = self.root / "counties"
        self.final = FINAL_ROOT / self.id
        self.app_data_dir = APP_DATA_ROOT / self.id

    def county(self, county_id: str) -> Path:
        return self.counties / county_id

    @property
    def app_packages(self) -> dict:
        return APP_PACKAGES[self.id]

    def packages(self) -> list[Path]:
        """Statewide package first, then every county package in name order."""
        return [self.state] + sorted(p for p in self.counties.iterdir() if p.is_dir())

    def shipped_packages(self) -> list[Path]:
        """Packages whose data ships in the app: statewide first, then the
        declared counties (every county package when none are declared)."""
        counties = self.app_packages["counties"]
        if counties is None:
            return self.packages()
        return [self.state] + [self.county(c) for c in counties]


def rel(path: Path) -> str:
    """Repo-relative POSIX path, the form used in every ``derived_from``."""
    return path.relative_to(ROOT).as_posix()
