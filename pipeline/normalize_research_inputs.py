"""Normalize ballot packages into the small research-pipeline schema.

County app files retain presentation and scope fields.  Research only needs
contest identity plus candidate identity, so this produces the same core shape
as King County's ``parse_candidates.py`` output.  Congressional and legislative
contests are additionally deduplicated into one statewide research package.

Files this script did not write (their ``script`` is not this script) are
never replaced:

* A hand-built statewide ``interim/contests.json`` (e.g. the general's Supreme
  Court contests, issue #5) keeps its contests verbatim and first; normalized
  district contests are appended unless a hand-built contest has the same slug.
  The appended slugs and their sources are recorded under ``normalized`` and
  the sources are added to ``derived_from``, so a rerun replaces exactly that
  part. If nothing changes the file is not rewritten.
* A hand-built statewide ``interim/measures.json`` is left untouched.
* A county ``interim/{contests,measures}.json`` written by another script is a
  conflict: the script exits before writing anything.

Usage: python3 pipeline/normalize_research_inputs.py [--election <id>]
"""

import argparse
import json
import re

import election

SCRIPT = "pipeline/normalize_research_inputs.py"


def _write(path, value, ensure_ascii=True):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=ensure_ascii) + "\n")


def _foreign(path):
    """The parsed file if it exists and this script did not write it, else None."""
    if not path.exists():
        return None
    data = json.loads(path.read_text())
    return None if data.get("script") == SCRIPT else data


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


def _merge_shared_contest(shared, key, contest, county):
    """Union one county's roster into a shared contest without aliasing input.

    County ballot packages can contain only the candidates visible in that
    county.  Shared races therefore need a stable union, not a representative
    county roster.
    """
    unit = shared.get(key)
    if unit is None:
        unit = {
            **contest,
            "candidates": [],
            "counties": [],
        }
        shared[key] = unit
    unit["counties"].append(county)
    known = {candidate["slug"] for candidate in unit["candidates"]}
    unit["candidates"].extend(
        dict(candidate) for candidate in contest["candidates"]
        if candidate["slug"] not in known
    )


def _merge_hand_built(hand, district_contests, sources):
    """Hand-built statewide contests plus normalized district contests.

    ``hand`` may carry a previous merge (its ``normalized`` block); that part
    is dropped and rebuilt, so reruns are idempotent. Hand-built contests win
    a slug collision.
    """
    previous = hand.get("normalized", {})
    stale_slugs = set(previous.get("contests", []))
    stale_sources = set(previous.get("derived_from", []))
    merged = {key: value for key, value in hand.items() if key not in ("normalized", "contests")}
    kept = [c for c in hand["contests"] if c["slug"] not in stale_slugs]
    hand_slugs = {c["slug"] for c in kept}
    added = [c for c in district_contests if c["slug"] not in hand_slugs]
    merged["derived_from"] = [d for d in hand.get("derived_from", []) if d not in stale_sources]
    if added:
        merged["derived_from"] += [d for d in sources if d not in merged["derived_from"]]
        merged["normalized"] = {
            "script": SCRIPT,
            "derived_from": sources,
            "contests": [c["slug"] for c in added],
        }
    merged["contests"] = kept + added
    return merged


def normalize(election_id=None, package_root=None):
    """Normalize one election package.

    ``package_root`` overrides the package directory; tests pass a copy laid
    out as ``<tmp>/data/washington-state/elections/<id>`` so ``derived_from``
    paths match the real package and the real files are never written.
    """
    e = election.Election(election_id)
    root = package_root or e.root
    repo = root.parents[3]

    def rel(path):
        return path.relative_to(repo).as_posix()

    counties = root / "counties"
    statewide_interim = root / "statewide/interim"
    shared = {}
    county_outputs = []
    for county_dir in sorted(path for path in counties.iterdir() if path.is_dir()):
        interim = county_dir / "interim"
        app_contests = interim / "app-contests.json"
        app_measures = interim / "app-measures.json"
        # King is already the reference format, produced directly from raw data.
        if not app_contests.exists():
            continue
        contest_source = json.loads(app_contests.read_text())
        contests = [_contest(row) for row in contest_source["contests"]]
        measure_rows = json.loads(app_measures.read_text())["measures"] if app_measures.exists() else []
        county_outputs.append((interim / "contests.json", {
            "derived_from": [rel(app_contests)],
            "script": SCRIPT,
            "contests": contests,
        }))
        county_outputs.append((interim / "measures.json", {
            "derived_from": [rel(app_measures)] if app_measures.exists() else [],
            "script": SCRIPT,
            "measures": [_measure(row) for row in measure_rows],
        }))

        for contest in contests:
            key = _shared_key(contest)
            if key is None:
                continue
            _merge_shared_contest(shared, key, contest, county_dir.name)

    conflicts = [rel(path) for path, _ in county_outputs if _foreign(path) is not None]
    if conflicts:
        raise SystemExit(
            "refusing to overwrite county files written by another script: "
            + ", ".join(conflicts)
        )

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

    sources = sorted(rel(path) for path in counties.glob("*/interim/app-contests.json"))

    for path, value in county_outputs:
        _write(path, value)

    contests_path = statewide_interim / "contests.json"
    hand_contests = _foreign(contests_path)
    if hand_contests is None:
        _write(contests_path, {
            "derived_from": sources,
            "script": SCRIPT,
            "contests": statewide_contests,
        })
        statewide_note = f"statewide shared contests: {len(statewide_contests)}"
    else:
        merged = _merge_hand_built(hand_contests, statewide_contests, sources)
        if merged != hand_contests:
            _write(contests_path, merged, ensure_ascii=False)
        added = len(merged.get("normalized", {}).get("contests", []))
        statewide_note = (f"statewide contests: kept {len(merged['contests']) - added} hand-built, "
                          f"merged {added} shared district contests")

    measures_path = statewide_interim / "measures.json"
    if _foreign(measures_path) is None:
        _write(measures_path, {
            "derived_from": [],
            "script": SCRIPT,
            "measures": [],
        })
    else:
        statewide_note += "; hand-built statewide measures.json left untouched"
    print(f"normalized counties: {len(county_outputs) // 2}; {statewide_note}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    election.add_election_arg(parser)
    normalize(parser.parse_args().election)
