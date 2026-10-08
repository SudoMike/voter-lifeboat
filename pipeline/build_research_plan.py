"""Stage: interim -> interim. Emit a dossier research work manifest.

Depth rule: 3+ candidates are ``deep``, 2 are ``light``, and uncontested
single-candidate contests are omitted because everyone advances.

Contests a county package marks ``"owner": "statewide"`` are left to the
statewide package's plan.

When the election has a predecessor (``election.PREDECESSOR``), every planned
candidate gets ``carry_forward``: ``"primary"`` with ``primary_dossier`` (the
predecessor's dossier path) when the predecessor package has a contest with the
same slug, a candidate with the same name, and that candidate's dossier file;
otherwise ``"new"``. Where the predecessor's district (congressional and
legislative) contests were statewide-owned (the primary) and this election's
are county-owned (the general), a county's district contest also carries
forward from the predecessor's statewide dossier for the same race
(shared_contests.contest_key) and candidate name. Measures are never carried
forward (proposition numbers are reused across elections for unrelated
measures).

Where district contests are county-owned, a contest one package lists may be
the same race another package lists (shared_contests.py). Each such planned
contest gets ``shared``: ``researched_in`` names the package, contest slug and
scoring file that already hold its research (statewide and the shipped
counties are searched first, then every other county package), or is null
when nobody has researched it yet; ``also_listed_by`` names the other county
packages that list it. A contest researched elsewhere is not researched
again: the county package ships it with that package's scoring and dossiers
(assemble_app_data.py), which are never edited from another package.

Pass a county slug, ``statewide``, or ``--all`` (the default), plus an optional
``--election <id>`` (default: the active election).
"""

import argparse
import json
import re

import election
import shared_contests
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


def predecessor_district_dossiers(election_id=None):
    """{(contest key, name key): dossier path} from the predecessor's
    statewide package, when the predecessor owned district contests there
    and this election does not. Otherwise {}."""
    e = election.Election(election_id)
    previous = election.PREDECESSOR.get(e.id)
    if (previous is None or e.app_packages["district_contests"] != "county"
            or election.APP_PACKAGES[previous]["district_contests"] != "statewide"):
        return {}
    pkg = package_dir("statewide", previous)
    found = {}
    for contest in shared_contests.package_contests(pkg):
        key = shared_contests.contest_key(contest)
        if key is None:
            continue
        for candidate in contest["candidates"]:
            dossier = pkg / "dossiers" / contest["slug"] / f"{candidate['slug']}.md"
            if dossier.exists():
                found[(key, _name_key(candidate["name"]))] = dossier.relative_to(ROOT).as_posix()
    return found


def shared_indexes(package, election_id=None):
    """(researched index, listing index) over every package but this one,
    statewide and the shipped counties first; ({}, {}) where district
    contests are not county-owned."""
    e = election.Election(election_id)
    if e.app_packages["district_contests"] != "county" or package == "statewide":
        return {}, {}
    declared = e.app_packages["counties"] or []
    others = [e.state] + [e.county(c) for c in declared if c != package]
    others += [d for d in sorted(p for p in e.counties.iterdir() if p.is_dir())
               if d.name != package and d.name not in declared]
    counties = [d for d in others if d != e.state]
    return shared_contests.researched_index(others), shared_contests.listing_index(counties)


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
    carried_district = predecessor_district_dossiers(election_id) if package != "statewide" else {}
    researched, listed = shared_indexes(package, election_id)
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
            if dossier is None and carried_district:
                dossier = carried_district.get((shared_contests.contest_key(contest), _name_key(candidate["name"])))
            entry["carry_forward"] = "primary" if dossier else "new"
            entry["primary_dossier"] = dossier
        return entry

    for contest in contests:
        if len(contest["candidates"]) < 2:
            continue
        if contest.get("owner") == "statewide":
            statewide_owned.append(contest["slug"])
            continue
        entry = {
            "contest_slug": contest["slug"], "category": contest["category"],
            "office": contest["office"], "district": contest["district"],
            "depth": "deep" if len(contest["candidates"]) >= 3 else "light",
            "candidates": [plan_candidate(contest, candidate) for candidate in contest["candidates"]],
        }
        key = shared_contests.contest_key(contest)
        if key is not None and (key in researched or key in listed):
            found = researched.get(key)
            entry["shared"] = {
                "researched_in": None if found is None else {
                    "package": found["package"], "contest_slug": found["contest_slug"],
                    "scoring": found["scoring"].relative_to(ROOT).as_posix(),
                    "candidates_missing": sorted({c["slug"] for c in contest["candidates"]}
                                                 - set(found["candidates"])),
                },
                "also_listed_by": listed.get(key, []),
            }
        plan["contests"].append(entry)
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
    elsewhere = [c for c in plan["contests"] if (c.get("shared") or {}).get("researched_in")]
    if not elsewhere:
        return
    print(f"  already researched in another package ({len(elsewhere)}):")
    for c in elsewhere:
        r = c["shared"]["researched_in"]
        missing = f"  CANDIDATES NOT IN ITS SCORING: {r['candidates_missing']}" if r["candidates_missing"] else ""
        print(f"    {c['contest_slug']} -> {r['package']}/{r['contest_slug']}{missing}")
    todo = [c for c in plan["contests"] if c not in elsewhere]
    print(f"  to research here ({len(todo)}):")
    for c in todo:
        carried = sum(1 for x in c["candidates"] if x.get("carry_forward") == "primary")
        others = (c.get("shared") or {}).get("also_listed_by") or []
        also = f"  also listed by {', '.join(others)}" if others else ""
        print(f"    {c['contest_slug']} ({len(c['candidates'])} candidates, {carried} with a primary dossier){also}")


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
