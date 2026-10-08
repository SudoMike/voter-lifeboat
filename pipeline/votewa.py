"""Shared VoteWA candidate-list parsing for county packages.

Used by build_votewa_lite_data.py (the 32 counties it configures) and, from
the general on, by the six county builders (build_<county>_lite_data.py).

The raw source per election is declared in election.VOTEWA_SOURCES:

* the primary commits each county's export verbatim at
  counties/<county>/raw/votewa/candidate-list.csv;
* the general commits a pointer pair, counties/<county>/raw/votewa/
  candidate-list.csv.url + .meta.json, whose sha256 pins the export. The CSV
  itself is cached in data/.cache/votewa/ by fetch_votewa_candidate_list.py
  (fetched on a cache miss). A cached or re-fetched export whose sha256
  differs from the pointer's stops the build: re-run the fetcher with
  --refresh --write-pointer, then rebuild, so a changed filing list is a
  visible commit rather than a silent drift.

Rows are kept when their 'Election Status' is one of the election's
`ballot_status` values. PCO races (District Type 'Precinct') and the
statewide Supreme Court contests are dropped by convention: the statewide
package owns the Supreme Court.
"""

import csv
import hashlib
import io
import json
import re

import election
from election import ROOT


def slugify(s: str) -> str:
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", s.lower())).strip("-")


def titleish(s: str) -> str:
    """Title-case fully-uppercase ballot strings; leave mixed case alone."""
    if s != s.upper():
        return s
    small = {"of", "the", "and", "for", "no", "at"}
    out = []
    for i, w in enumerate(s.lower().split()):
        if re.fullmatch(r"[0-9#.]+", w):
            out.append(w)
        elif w in ("no.", "pos.", "dist.", "u.s."):
            out.append(w.capitalize() if w != "u.s." else "U.S.")
        elif w in small and i:
            out.append(w)
        else:
            out.append(w.capitalize())
    return " ".join(out)


PARTY_MAP = {
    "DEMOCRATIC": "Prefers Democratic Party",
    "DEMOCRAT": "Prefers Democrat Party",
    "REPUBLICAN": "Prefers Republican Party",
    "INDEPENDENT": "Prefers Independent Party",
    "STATES NO PARTY PREFERENCE": "States No Party Preference",
    "": None,
}


def party_label(raw: str):
    raw = (raw or "").strip().upper()
    if raw in PARTY_MAP:
        return PARTY_MAP[raw]
    return f"Prefers {titleish(raw)} Party"


def district_number(*texts):
    for t in texts:
        n = re.search(r"(\d+)", t)
        if n:
            return int(n.group(1))
    raise ValueError(f"no district number in {texts!r}")


# --- raw source --------------------------------------------------------------

def raw_dir(election_id: str, county: str):
    return election.Election(election_id).county(county) / "raw/votewa"


def source_path(election_id: str, county: str):
    """The committed raw source a county's interim files cite in derived_from."""
    src = election.VOTEWA_SOURCES[election_id]
    name = "candidate-list.csv" if src["verbatim_csv"] else "candidate-list.csv.url"
    return raw_dir(election_id, county) / name


def has_source(election_id: str, county: str) -> bool:
    if election_id not in election.VOTEWA_SOURCES:
        return False
    return source_path(election_id, county).exists()


def csv_text(election_id: str, county: str) -> str:
    """The county's export as text: verbatim file, or the sha256-checked cache."""
    src = election.VOTEWA_SOURCES[election_id]
    if src["verbatim_csv"]:
        return source_path(election_id, county).read_text(encoding="utf-8-sig")
    meta_path = raw_dir(election_id, county) / "candidate-list.csv.meta.json"
    meta = json.loads(meta_path.read_text())
    cache = ROOT / meta["cache_file"]
    if not cache.exists():
        import fetch_votewa_candidate_list
        fetch_votewa_candidate_list.fetch(county, election_id)
    data = cache.read_bytes()
    digest = hashlib.sha256(data).hexdigest()
    if digest != meta["sha256"]:
        raise SystemExit(
            f"{county}: {meta['cache_file']} sha256 {digest} does not match "
            f"{meta_path.relative_to(ROOT)} ({meta['sha256']}). The VoteWA export changed: run "
            f"python3 pipeline/fetch_votewa_candidate_list.py --election {election_id} "
            f"--refresh --write-pointer {county}, review the diff, and rebuild."
        )
    return data.decode("utf-8-sig")


def ballot_rows(election_id: str, county: str) -> list[dict]:
    statuses = election.VOTEWA_SOURCES[election_id]["ballot_status"]
    rows = csv.DictReader(io.StringIO(csv_text(election_id, county)))
    return [r for r in rows if r["Election Status"] in statuses]


# --- contests ----------------------------------------------------------------

def candidate(r: dict) -> dict:
    return {
        "slug": slugify(r["Name"]),
        "name": r["Name"].strip(),
        "party": party_label(r["Party Preference"]),
        "evidence_level": "official-ballot-only",
        "withdrawn": r["Status"].strip() != "Active",
        "summary": "Official ballot candidate. Voter Lifeboat has not completed a scored dossier for this candidate yet.",
        "highlights": [],
        "scores": {},
        "sources": [],
    }


def classify(r: dict, county: str, cfg: dict, unresolvable: set):
    """(category, display district, office, (layer, value)) for one row, by
    the generic rules build_votewa_lite_data.py has always used. cfg gives
    `name` and the commissioner/pud/port scope-value formats ('{n}'); None
    marks a race with no queryable boundary, recorded in `unresolvable`."""
    dtype = r["District Type"].strip().upper()
    district, race = r["District"].strip(), r["Race"].strip()
    office = titleish(race)
    if dtype == "CONGRESSIONAL":
        n = district_number(district)
        return "Federal", f"Congressional District {n}", office, ("CONGDST", str(n))
    if dtype == "LEGISLATIVE":
        n = district_number(district)
        return "State", f"Legislative District {n}", office, ("LEGDST", str(n))
    if dtype in ("COMMISSIONER", "COUNCIL"):
        n = district_number(race, district)
        if "ALL COUNTY" in district.upper():
            # Nominated by district in the primary, elected county-wide in
            # the general (RCW 36.32.040): VoteWA's general export says so
            # with District 'COMMISSIONER DISTRICT ALL COUNTY' (Thurston).
            return "County", f"{cfg['name']} Commissioner District {n}", office, ("COUNTY", None)
        fmt = cfg.get("commissioner")
        if fmt is None:
            unresolvable.add("COUNTY_COUNCIL")
        return ("County", f"{cfg['name']} Commissioner District {n}", office,
                ("COUNTY_COUNCIL", fmt.format(n=n) if fmt else str(n)))
    if dtype in ("COUNTYWIDE", "COUNTY"):
        return "County", cfg["name"], office, ("COUNTY", None)
    if dtype == "JUDICIAL":
        # Superior/district courts and Court of Appeals divisions are
        # county-wide electorates for a single county's package.
        return "Judicial", titleish(district), office, ("COUNTY", None)
    if dtype == "PUBLIC UTILITY":
        n = district_number(district, race)
        fmt = cfg.get("pud")
        layer = cfg.get("pud_layer_key", "PUDDST")
        if fmt is None:
            unresolvable.add("PUDDST")
        return ("PublicUtility", f"Public Utility District Commissioner District {n}", office,
                (layer, fmt.format(n=n) if fmt else str(n)))
    if dtype == "PORT":
        n = district_number(district, race)
        fmt = cfg.get("port")
        if fmt is None:
            unresolvable.add("PORTDST")
        return "Port", titleish(district), office, ("PORTDST", fmt.format(n=n) if fmt else str(n))
    if dtype == "CITY/TOWN":
        city = re.sub(r"^(city|town) of ", "", district, flags=re.I).strip()
        return "City", titleish(district), office, ("CITY", titleish(city))
    raise ValueError(f"{county}: unmapped district type {dtype!r} ({district} / {race})")


def parse_contests(rows, county, cfg, unresolvable, override=None):
    """Group ballot rows into contests in first-seen order.

    `override(row, unresolvable)` may return a classify()-shaped tuple for a
    county-specific row (the six county builders use it to keep their own
    contest names and District Adapter layers), or None to use classify().
    """
    contests, order = {}, []
    for r in rows:
        dtype = r["District Type"].strip().upper()
        district, race = r["District"].strip(), r["Race"].strip()
        if dtype == "PRECINCT" or district.upper() == "SUPREME COURT":
            continue
        key = (district.upper(), race.upper())
        if key not in contests:
            fields = override(r, unresolvable) if override else None
            category, disp_district, office, scope = fields or classify(r, county, cfg, unresolvable)
            contests[key] = {
                "category": category,
                "district": disp_district,
                "office": office,
                "scope": scope,
                "candidates": [],
            }
            order.append(key)
        contests[key]["candidates"].append(candidate(r))
    return [contests[k] for k in order]


def scope_json(county, scope):
    layer, value = scope
    if layer == "COUNTY":
        return {"kind": "COUNTY", "county": county}
    return {"kind": "DISTRICT", "county": county, "layer": layer, "value": str(value)}


def app_contests(county, contests, blurb):
    """The app-contests.json rows for parse_contests() output."""
    return [{
        "slug": f"{county}-" + slugify(f"{c['district']}-{c['office']}"),
        "owner": county,
        "category": c["category"],
        "office": c["office"],
        "district": c["district"],
        "scope": scope_json(county, c["scope"]),
        "office_does": None,
        "race_blurb": blurb,
        "uncontested": len(c["candidates"]) == 1,
        "candidates": c["candidates"],
    } for c in contests]


MEASURES_NOT_CURATED = (
    "Measures not curated yet for this election: app-measures.json is empty because no one has "
    "transcribed this county's local measures, not because the ballot has none."
)


def unresolvable_note(unresolvable) -> str:
    return ("Unresolvable district scopes (no queryable official boundary): "
            + ", ".join(sorted(unresolvable))
            + ". Contests/measures scoped to them are hidden rather than shown to the wrong voters.")


def write_county_package(county, election_id, cfg, script, override=None, measures=None,
                         measure_sources=(), notes=()):
    """Write counties/<county>/interim/app-{contests,measures}.json from the
    county's VoteWA export: the general-election path of the six county
    builders (build_<county>_lite_data.py).

    `cfg`: `name`, the generic scope formats classify() reads, and
    `unresolvable_layers` (layers the county's District Adapter cannot
    resolve; a measure scoped to one makes the package partial_county).
    `override(row, unresolvable)`: county-specific contest naming/scoping.
    `measures`: the county's curated app-measures rows for this election, or
    None while nobody has curated them (the package then says so in
    `notes`). `measure_sources`: the raw pointers or official URLs those rows
    were transcribed from (added to derived_from).
    """
    unresolvable = set()
    contests = parse_contests(ballot_rows(election_id, county), county, cfg, unresolvable, override)
    label = election.VOTEWA_SOURCES[election_id]["label"]
    rows = app_contests(
        county, contests,
        f"Official ballot listing imported from the VoteWA {label} candidate list for {cfg['name']}. "
        "Candidate scoring is not complete for this county yet.",
    )
    for m in measures or []:
        if m["scope"]["kind"] == "DISTRICT" and m["scope"]["layer"] in cfg.get("unresolvable_layers", ()):
            unresolvable.add(m["scope"]["layer"])
    all_notes = list(notes)
    if measures is None:
        all_notes.append(MEASURES_NOT_CURATED)
    if unresolvable:
        all_notes.append(unresolvable_note(unresolvable))
    common = {
        "county": county,
        "script": script,
        "derived_from": [election.rel(source_path(election_id, county)), *measure_sources],
        "coverage": "partial_county" if unresolvable else "full_county",
        "notes": all_notes,
    }
    out = election.Election(election_id).county(county) / "interim"
    out.mkdir(parents=True, exist_ok=True)
    (out / "app-contests.json").write_text(json.dumps({**common, "contests": rows}, indent=2))
    (out / "app-measures.json").write_text(json.dumps({**common, "measures": measures or []}, indent=2))
    flags = f"  UNRESOLVABLE: {','.join(sorted(unresolvable))}" if unresolvable else ""
    flags += "  MEASURES NOT CURATED" if measures is None else ""
    print(f"{county} contests: {len(rows)} measures: {len(measures or [])}  {common['coverage']}{flags}")
    return common["coverage"], sorted(unresolvable)
