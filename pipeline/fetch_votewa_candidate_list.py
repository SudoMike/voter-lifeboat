"""Export a county's VoteWA candidate list CSV for an election.

VoteWA's candidate list (https://voter.votewa.gov/candidatelist.aspx) is an
ASP.NET WebForms page with no direct CSV URL: the grid's "Export to CSV" icon
posts the whole form back. This script replays that post non-interactively:

  1. GET candidatelist.aspx?c=<county code>&e=<election value> (cookie jar).
  2. POST the form back to its action, replaying every hidden input
     (__VIEWSTATE__, __VIEWSTATE, __EVENTVALIDATION, Telerik ClientState
     fields) and every <select> (its selected option, else its first option;
     ctl00$ddlLanguages must be 'en-us' or the server answers with its
     generic error page), plus
     ctl00$ContentPlaceHolder1$grdCandidates$ctl00$ctl02$ctl00$ExportToCsvButton=' '.
  3. The response is text/csv (Content-Disposition CandidateList.csv).

The CSV is cached verbatim in data/.cache/votewa/candidatelist-c<code>-e<e>.csv
(gitignored). The committed raw source is the pointer pair
counties/<county>/raw/votewa/candidate-list.csv.url + .meta.json, whose
sha256 pins the export the interim files were built from. This is the method
issue #5 recorded for the statewide export (c=99&e=899).

Usage:
  python3 pipeline/fetch_votewa_candidate_list.py --election <id> <county> [<county> ...]
  python3 pipeline/fetch_votewa_candidate_list.py --election <id> --refresh <county>

Without --refresh an existing cache file is reused. --write-pointer writes or
updates the county's raw pointer + meta (the step a county agent runs once).
"""

import argparse
import datetime
import hashlib
import http.cookiejar
import json
import sys
import urllib.parse
import urllib.request
from html.parser import HTMLParser

import election
from election import ROOT, rel

BASE = "https://voter.votewa.gov/candidatelist.aspx"
EXPORT_FIELD = "ctl00$ContentPlaceHolder1$grdCandidates$ctl00$ctl02$ctl00$ExportToCsvButton"
CACHE = ROOT / "data/.cache/votewa"
UA = "Mozilla/5.0 (X11; Linux x86_64) voter-lifeboat-pipeline"


class _Form(HTMLParser):
    """Collects the hidden inputs and select values of the page's one form,
    plus each select's chosen option label (to check the page is the one
    asked for)."""

    def __init__(self):
        super().__init__()
        self.fields: dict[str, str] = {}
        self.labels: dict[str, str] = {}
        self.action = None
        self._select = None
        self._options = []  # (value, selected, label)
        self._in_option = False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "form" and self.action is None:
            self.action = a.get("action")
        elif tag == "input" and a.get("type") == "hidden" and a.get("name"):
            self.fields[a["name"]] = a.get("value") or ""
        elif tag == "select":
            self._select, self._options = a.get("name"), []
        elif tag == "option" and self._select:
            self._options.append([a.get("value", ""), "selected" in a, ""])
            self._in_option = True

    def handle_data(self, data):
        if self._in_option and self._options:
            self._options[-1][2] += data

    def handle_endtag(self, tag):
        if tag == "option":
            self._in_option = False
        elif tag == "select" and self._select:
            chosen = next((o for o in self._options if o[1]), self._options[0] if self._options else ["", False, ""])
            self.fields[self._select] = chosen[0]
            self.labels[self._select] = chosen[2].strip()
            self._select = None


def county_code(county: str) -> str:
    return election.VOTEWA_COUNTY_CODES[county]


def page_url(county: str, election_id: str) -> str:
    return f"{BASE}?c={county_code(county)}&e={election.VOTEWA_SOURCES[election_id]['e']}"


def cache_path(county: str, election_id: str):
    return CACHE / f"candidatelist-c{county_code(county)}-e{election.VOTEWA_SOURCES[election_id]['e']}.csv"


def export_csv(url: str, expect_county: str | None = None, expect_election: str | None = None) -> bytes:
    jar = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
    opener.addheaders = [("User-Agent", UA)]
    html = opener.open(url, timeout=60).read().decode("utf-8", "replace")
    form = _Form()
    form.feed(html)
    got_county = form.labels.get("ctl00$ContentPlaceHolder1$ddlCounty")
    got_election = form.labels.get("ctl00$ContentPlaceHolder1$ddlElection")
    if expect_county and got_county != expect_county:
        raise SystemExit(f"{url}: County dropdown shows {got_county!r}, expected {expect_county!r}")
    if expect_election and got_election != expect_election:
        raise SystemExit(f"{url}: Election dropdown shows {got_election!r}, expected {expect_election!r}")
    fields = dict(form.fields)
    fields["ctl00$ddlLanguages"] = "en-us"
    fields[EXPORT_FIELD] = " "
    action = urllib.parse.urljoin(url, (form.action or "").replace("&amp;", "&"))
    body = urllib.parse.urlencode(fields).encode()
    resp = opener.open(urllib.request.Request(action, data=body, headers={
        "Content-Type": "application/x-www-form-urlencoded", "Referer": url}), timeout=120)
    data = resp.read()
    ctype = resp.headers.get("Content-Type", "")
    if "csv" not in ctype and not data.lstrip(b"\xef\xbb\xbf").startswith(b'"District Type"'):
        raise SystemExit(f"VoteWA export did not return CSV ({ctype}) for {url}")
    return data


def fetch(county: str, election_id: str, refresh: bool = False):
    path = cache_path(county, election_id)
    if refresh or not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(export_csv(
            page_url(county, election_id),
            expect_county=election.votewa_county_label(county),
            expect_election=election.VOTEWA_SOURCES[election_id]["dropdown_label"],
        ))
    return path


def csv_summary(data: bytes) -> dict:
    import csv
    import io
    rows = list(csv.DictReader(io.StringIO(data.decode("utf-8-sig"))))
    statuses: dict[str, int] = {}
    for r in rows:
        statuses[r.get("Election Status", "")] = statuses.get(r.get("Election Status", ""), 0) + 1
    return {
        "csv_rows": len(rows),
        "csv_columns": list(rows[0].keys()) if rows else [],
        "election_status_counts": dict(sorted(statuses.items())),
    }


def write_pointer(county: str, election_id: str, path) -> None:
    src = election.VOTEWA_SOURCES[election_id]
    e = election.Election(election_id)
    raw = e.county(county) / "raw/votewa"
    raw.mkdir(parents=True, exist_ok=True)
    url = page_url(county, election_id)
    data = path.read_bytes()
    (raw / "candidate-list.csv.url").write_text(url + "\n")
    meta = {
        "url": url,
        "retrieved_at": datetime.date.today().isoformat(),
        "method": (f"CSV export of the official VoteWA candidate list (ASP.NET postback), election "
                   f"{src['label']}, county {election.votewa_county_label(county)}"),
        "stage": "raw",
        "election_dropdown": {"value": str(src["e"]), "label": src["dropdown_label"]},
        "county_dropdown": {"value": county_code(county), "label": election.votewa_county_label(county)},
        "manual_export_steps": [
            "Open https://voter.votewa.gov/candidatelist.aspx",
            f"Election dropdown: choose '{src['dropdown_label']}' (option value {src['e']}); the page posts back",
            f"County dropdown: choose '{election.votewa_county_label(county)}' (option value "
            f"{county_code(county)}); the page posts back. Equivalent direct URL: {url}",
            "Click the grid's 'Export to CSV' icon (input " + EXPORT_FIELD + "); the response is text/csv "
            "with Content-Disposition attachment;filename=\"CandidateList.csv\"",
        ],
        "scripted_export": (
            f"python3 pipeline/fetch_votewa_candidate_list.py --election {election_id} --refresh --write-pointer "
            f"{county}: GET the direct URL with a cookie jar, check the selected Election and County labels, then "
            "POST the form back to its action replaying every hidden input (__VIEWSTATE__, __VIEWSTATE, "
            "__EVENTVALIDATION, Telerik ClientState fields) and every <select> (selected option, else the first; "
            "ctl00$ddlLanguages='en-us'), plus " + EXPORT_FIELD + "=' '."
        ),
        "cache_file": rel(path),
        "bytes": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
        **csv_summary(data),
        "notes": src["notes"],
    }
    (raw / "candidate-list.csv.meta.json").write_text(json.dumps(meta, indent=2) + "\n")


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    election.add_election_arg(p)
    p.add_argument("counties", nargs="+")
    p.add_argument("--refresh", action="store_true", help="re-export even when cached")
    p.add_argument("--write-pointer", action="store_true", help="write counties/<county>/raw/votewa pointer + meta")
    args = p.parse_args(argv)
    election_id = election.resolve(args.election)
    if election.VOTEWA_SOURCES.get(election_id, {}).get("verbatim_csv"):
        raise SystemExit(f"{election_id} keeps its VoteWA CSVs verbatim in the package; nothing to fetch")
    for county in args.counties:
        path = fetch(county, election_id, args.refresh)
        if args.write_pointer:
            write_pointer(county, election_id, path)
        print(f"{county}: {rel(path)} {len(path.read_bytes())} bytes "
              f"{json.dumps(csv_summary(path.read_bytes())['election_status_counts'])}")


if __name__ == "__main__":
    sys.exit(main())
