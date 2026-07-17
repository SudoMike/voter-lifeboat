"""Stage: interim -> interim. Emit a dossier research work manifest.

Depth rule: 3+ candidates are ``deep``, 2 are ``light``, and uncontested
single-candidate contests are omitted because everyone advances.

Pass a county slug, ``statewide``, or ``--all`` (the default).
"""

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def interim_for(package):
    base = ROOT / "data/washington-state"
    return base / ("statewide/interim" if package == "statewide" else f"counties/{package}/interim")


def build(package):
    interim = interim_for(package)
    rel = interim.relative_to(ROOT)
    contests = json.loads((interim / "contests.json").read_text())["contests"]
    measures = json.loads((interim / "measures.json").read_text())["measures"]
    index_path = interim / "pamphlet-index.json"
    pidx = json.loads(index_path.read_text()) if index_path.exists() else {"candidates": {}, "measures": {}}
    derived = [f"{rel}/contests.json", f"{rel}/measures.json"]
    if index_path.exists():
        derived.append(f"{rel}/pamphlet-index.json")
    plan = {"derived_from": derived, "script": "pipeline/build_research_plan.py", "contests": [], "measures": []}

    for contest in contests:
        if len(contest["candidates"]) < 2:
            continue
        plan["contests"].append({
            "contest_slug": contest["slug"], "category": contest["category"],
            "office": contest["office"], "district": contest["district"],
            "depth": "deep" if len(contest["candidates"]) >= 3 else "light",
            "candidates": [{
                "slug": candidate["slug"], "name": candidate["name"],
                "party_preference": candidate.get("party_preference"),
                "campaign_website": candidate.get("campaign_website"),
                "pamphlet_pages": pidx.get("candidates", {}).get(candidate["slug"], []),
            } for candidate in contest["candidates"]],
        })
    for measure in measures:
        plan["measures"].append({
            **measure, "pamphlet_pages": pidx.get("measures", {}).get(measure["slug"], [])
        })
    (interim / "research-plan.json").write_text(json.dumps(plan, indent=2) + "\n")
    print(f"{package}: {len(plan['contests'])} contested races, {len(plan['measures'])} measures")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("package", nargs="?")
    parser.add_argument("--all", action="store_true", help="build every normalized package")
    args = parser.parse_args()
    if args.all and args.package:
        parser.error("provide either a package or --all")
    if args.all or args.package is None:
        packages = sorted(path.parent.parent.name for path in
                          (ROOT / "data/washington-state/counties").glob("*/interim/contests.json"))
        packages.append("statewide")
    else:
        packages = [args.package]
    for package in packages:
        build(package)


if __name__ == "__main__":
    main()
