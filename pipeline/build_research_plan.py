"""Stage: interim -> interim. Emit a dossier research work manifest.

Depth rule: 3+ candidates are ``deep``, 2 are ``light``, and uncontested
single-candidate contests are omitted because everyone advances.

Contests a county package marks ``"owner": "statewide"`` are left to the
statewide package's plan.

When the election has a predecessor (``election.PREDECESSOR``), every planned
candidate gets ``carry_forward``: ``"primary"`` with ``primary_dossier`` (the
predecessor's dossier path) when the predecessor package has a contest with the
same slug, a candidate with the same name, and that candidate's dossier file;
otherwise ``"new"``. Measures are never carried forward (proposition numbers
are reused across elections for unrelated measures).

Pass a county slug, ``statewide``, or ``--all`` (the default), plus an optional
``--election <id>`` (default: the active election).
"""

import argparse
import json
import re

import election
from election import ROOT

# Plan fields copied from each measure, in this order; measure text (ballot
# title, statements) stays in measures.json.
PLAN_MEASURE_KEYS = ("jurisdiction", "proposition", "title", "slug", "kce_contest_id",
                     "votewa_measure_id", "scope", "scope_unresolved")


def package_dir(package, election_id=None):
    base = election.Election(election_id).root
    return base / ("statewide" if package == "statewide" else f"counties/{package}")


def interim_for(package, election_id=None):
    return package_dir(package, election_id) / "interim"


def _name_key(name):
    return re.sub(r"[^a-z]", "", name.lower())


def predecessor_dossiers(package, election_id=None):
    """{(contest slug, name key): dossier path} from the predecessor election, or None."""
    previous = election.PREDECESSOR.get(election.Election(election_id).id)
    if previous is None:
        return None
    pkg = package_dir(package, previous)
    contests_path = pkg / "interim/contests.json"
    found = {}
    if not contests_path.exists():
        return found
    for contest in json.loads(contests_path.read_text())["contests"]:
        for candidate in contest["candidates"]:
            dossier = pkg / "dossiers" / contest["slug"] / f"{candidate['slug']}.md"
            if dossier.exists():
                found[(contest["slug"], _name_key(candidate["name"]))] = dossier.relative_to(ROOT).as_posix()
    return found


def plan_for(package, election_id=None):
    interim = interim_for(package, election_id)
    rel = interim.relative_to(ROOT)
    contests = json.loads((interim / "contests.json").read_text())["contests"]
    measures = json.loads((interim / "measures.json").read_text())["measures"]
    index_path = interim / "pamphlet-index.json"
    pidx = json.loads(index_path.read_text()) if index_path.exists() else {"candidates": {}, "measures": {}}
    derived = [f"{rel}/contests.json", f"{rel}/measures.json"]
    if index_path.exists():
        derived.append(f"{rel}/pamphlet-index.json")
    carried = predecessor_dossiers(package, election_id)
    plan = {"derived_from": derived, "script": "pipeline/build_research_plan.py", "contests": [], "measures": []}
    if carried is not None:
        plan["carry_forward_from"] = election.PREDECESSOR[election.Election(election_id).id]
    statewide_owned = []

    def plan_candidate(contest, candidate):
        entry = {
            "slug": candidate["slug"], "name": candidate["name"],
            "party_preference": candidate.get("party_preference"),
            "campaign_website": candidate.get("campaign_website"),
            "pamphlet_pages": pidx.get("candidates", {}).get(candidate["slug"], []),
        }
        if carried is not None:
            dossier = carried.get((contest["slug"], _name_key(candidate["name"])))
            entry["carry_forward"] = "primary" if dossier else "new"
            entry["primary_dossier"] = dossier
        return entry

    for contest in contests:
        if len(contest["candidates"]) < 2:
            continue
        if contest.get("owner") == "statewide":
            statewide_owned.append(contest["slug"])
            continue
        plan["contests"].append({
            "contest_slug": contest["slug"], "category": contest["category"],
            "office": contest["office"], "district": contest["district"],
            "depth": "deep" if len(contest["candidates"]) >= 3 else "light",
            "candidates": [plan_candidate(contest, candidate) for candidate in contest["candidates"]],
        })
    for measure in measures:
        entry = {k: measure[k] for k in PLAN_MEASURE_KEYS if k in measure}
        entry["pamphlet_pages"] = pidx.get("measures", {}).get(measure["slug"], [])
        if carried is not None:
            entry["carry_forward"] = "new"
        plan["measures"].append(entry)
    if statewide_owned:
        plan["statewide_owned_contests"] = statewide_owned
    return plan


def build(package, election_id=None):
    plan = plan_for(package, election_id)
    (interim_for(package, election_id) / "research-plan.json").write_text(json.dumps(plan, indent=2) + "\n")
    print(f"{package}: {len(plan['contests'])} contested races, {len(plan['measures'])} measures")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("package", nargs="?")
    parser.add_argument("--all", action="store_true", help="build every normalized package")
    election.add_election_arg(parser)
    args = parser.parse_args()
    e = election.Election(args.election)
    if args.all and args.package:
        parser.error("provide either a package or --all")
    if args.all or args.package is None:
        packages = sorted(path.parent.parent.name for path in
                          e.counties.glob("*/interim/contests.json"))
        packages.append("statewide")
    else:
        packages = [args.package]
    for package in packages:
        build(package, e.id)


if __name__ == "__main__":
    main()
