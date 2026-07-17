"""Normalize ballot packages into the small research-pipeline schema.

County app files retain presentation and scope fields.  Research only needs
contest identity plus candidate identity, so this produces the same core shape
as King County's ``parse_candidates.py`` output.  Congressional and legislative
contests are additionally deduplicated into one statewide research package.
"""

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
COUNTIES = ROOT / "data/washington-state/counties"
STATEWIDE = ROOT / "data/washington-state/statewide/interim"


def _write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n")


def _contest(row):
    return {
        "category": row["category"],
        "office": row["office"],
        "district": row["district"],
        "slug": row["slug"],
        "candidates": [
            {
                "slug": candidate["slug"],
                "name": candidate["name"],
                "party_preference": candidate.get("party_preference", candidate.get("party")),
            }
            for candidate in row["candidates"]
        ],
    }


def _measure(row):
    return {
        key: row[key]
        for key in ("jurisdiction", "proposition", "title", "slug")
        if key in row
    }


def _shared_key(contest):
    if contest["category"] == "Federal":
        match = re.search(r"Congressional District\s*(\d+)", contest["district"], re.I)
        return ("Federal", int(match.group(1)), "representative") if match else None
    if contest["category"] != "State":
        return None
    match = re.search(r"Legislative District(?: No\.)?\s*(\d+)", contest["district"], re.I)
    if not match:
        return None
    blob = f'{contest["office"]} {contest["district"]}'
    seat = "senator" if re.search(r"senat", blob, re.I) else (
        "representative-position-1" if re.search(r"(?:pos(?:ition)?\.?|no\.?)\s*1", blob, re.I)
        else "representative-position-2"
    )
    return ("State", int(match.group(1)), seat)


def normalize():
    shared = {}
    normalized_counties = 0
    for county_dir in sorted(path for path in COUNTIES.iterdir() if path.is_dir()):
        interim = county_dir / "interim"
        app_contests = interim / "app-contests.json"
        app_measures = interim / "app-measures.json"
        # King is already the reference format, produced directly from raw data.
        if not app_contests.exists():
            continue
        contest_source = json.loads(app_contests.read_text())
        contests = [_contest(row) for row in contest_source["contests"]]
        _write(interim / "contests.json", {
            "derived_from": [str(app_contests.relative_to(ROOT))],
            "script": "pipeline/normalize_research_inputs.py",
            "contests": contests,
        })
        measure_rows = json.loads(app_measures.read_text())["measures"] if app_measures.exists() else []
        _write(interim / "measures.json", {
            "derived_from": [str(app_measures.relative_to(ROOT))] if app_measures.exists() else [],
            "script": "pipeline/normalize_research_inputs.py",
            "measures": [_measure(row) for row in measure_rows],
        })
        normalized_counties += 1

        for contest in contests:
            key = _shared_key(contest)
            if key is None:
                continue
            unit = shared.setdefault(key, {**contest, "counties": []})
            unit["counties"].append(county_dir.name)
            known = {candidate["slug"] for candidate in unit["candidates"]}
            unit["candidates"].extend(c for c in contest["candidates"] if c["slug"] not in known)

    statewide_contests = []
    for key, contest in sorted(shared.items()):
        category, district_number, seat = key
        district = (f"Congressional District {district_number}" if category == "Federal"
                    else f"Legislative District {district_number}")
        office = "U.S. Representative" if category == "Federal" else (
            "State Senator" if seat == "senator" else
            f"State Representative Position {seat[-1]}"
        )
        contest.update({
            "district": district,
            "office": office,
            "slug": re.sub(r"[^a-z0-9]+", "-", f"{district}-{office}".lower()).strip("-"),
            "counties": sorted(set(contest["counties"])),
            "candidates": sorted(contest["candidates"], key=lambda c: c["slug"]),
        })
        statewide_contests.append(contest)

    sources = sorted(
        str(path.relative_to(ROOT)) for path in COUNTIES.glob("*/interim/app-contests.json")
    )
    _write(STATEWIDE / "contests.json", {
        "derived_from": sources,
        "script": "pipeline/normalize_research_inputs.py",
        "contests": statewide_contests,
    })
    _write(STATEWIDE / "measures.json", {
        "derived_from": [],
        "script": "pipeline/normalize_research_inputs.py",
        "measures": [],
    })
    print(f"normalized counties: {normalized_counties}; statewide shared contests: {len(statewide_contests)}")


if __name__ == "__main__":
    normalize()
