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
        "statewide_complete": False,
    },
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

    def packages(self) -> list[Path]:
        """Statewide package first, then every county package in name order."""
        return [self.state] + sorted(p for p in self.counties.iterdir() if p.is_dir())


def rel(path: Path) -> str:
    """Repo-relative POSIX path, the form used in every ``derived_from``."""
    return path.relative_to(ROOT).as_posix()
