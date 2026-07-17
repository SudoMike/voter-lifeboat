"""Build app-facing Thurston County lite data from extracted official PDFs."""

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
COUNTY = ROOT / "data/washington-state/counties/thurston"
OUT = COUNTY / "interim"


def slugify(s: str) -> str:
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", s.lower())).strip("-")


def county_slug(s: str) -> str:
    return f"thurston-{slugify(s)}"


def dist_scope(layer, value):
    return {"kind": "DISTRICT", "county": "thurston", "layer": layer, "value": str(value)}


def cand(name, party=None):
    return {
        "slug": slugify(name),
        "name": name,
        "party": party,
        "evidence_level": "official-ballot-only",
        "withdrawn": False,
        "summary": "Official ballot candidate. Voter Lifeboat has not completed a scored dossier for this candidate yet.",
        "highlights": [],
        "scores": {},
        "sources": [],
    }


def contest(category, district, office, candidates, scope):
    return {
        "slug": county_slug(f"{district}-{office}"),
        "owner": "thurston",
        "category": category,
        "office": office,
        "district": district,
        "scope": scope,
        "office_does": None,
        "race_blurb": "Official ballot listing imported from the Thurston County sample ballot. Candidate scoring is not complete for this county yet.",
        "uncontested": len(candidates) == 1,
        "candidates": candidates,
    }


contests = [
    contest("Federal", "Congressional District 3", "U.S. Representative", [
        cand("Marie Gluesenkamp Perez", "Prefers Democratic Party"),
        cand("Brent Hennrich", "Prefers Democratic Party"),
        cand("John P. Roco", "Prefers Republican Party"),
        cand("John Saulie-Rohman", "Prefers Independent Party"),
        cand("Troy Rasband", "Prefers Democratic Party"),
        cand("John Braun", "Prefers Republican Party"),
        cand("Antony Barran", "Prefers Cascade Party"),
        cand("Austin Braswell", "Prefers Democratic Party"),
        cand("Lawrence Kellogg", "Prefers Republican Party"),
    ], dist_scope("CONGDST", 3)),
    contest("Federal", "Congressional District 10", "U.S. Representative", [
        cand("Adam Arafat", "Prefers Democratic Party"),
        cand("Marilyn Strickland", "Prefers Democratic Party"),
        cand("Kurtis Engle", "Prefers Union Party"),
        cand("Alex Scheel", "Prefers Democratic Party"),
        cand("Derek Maynes", "States No Party Preference"),
        cand("Chris D. Chung", "Prefers Republican Party"),
    ], dist_scope("CONGDST", 10)),
    contest("State", "Legislative District 2", "State Representative Pos. 1", [
        cand("William Dehnel", "Prefers Labor Democrat Party"),
        cand("Andrew Barkis", "Prefers Republican Party"),
    ], dist_scope("LEGDST", 2)),
    contest("State", "Legislative District 2", "State Representative Pos. 2", [
        cand("Angela Taylor", "Prefers Democratic Party"),
        cand("Martin L Miller", "Prefers Democratic Party"),
        cand("Matt Marshall", "Prefers Republican Party"),
    ], dist_scope("LEGDST", 2)),
    contest("State", "Legislative District 19", "State Representative Pos. 1", [
        cand("Jim Walsh", "Prefers Republican Party"),
        cand("Kevin Moynihan", "Prefers Democratic Party"),
    ], dist_scope("LEGDST", 19)),
    contest("State", "Legislative District 19", "State Representative Pos. 2", [
        cand("Daniel William Bradley", "Prefers Republican Party"),
        cand("Jimi O'Hagan", "Prefers Republican Party"),
        cand("Terry Carlson", "Prefers Democratic Party"),
        cand("Joel McEntire", "Prefers Republican Party"),
    ], dist_scope("LEGDST", 19)),
    contest("State", "Legislative District 20", "State Representative Pos. 1", [
        cand("Peter Abbarno", "Prefers Republican Party"),
        cand("Andy Zahn", "Prefers Democratic Party"),
    ], dist_scope("LEGDST", 20)),
    contest("State", "Legislative District 20", "State Representative Pos. 2", [
        cand("Evan Jones", "Prefers Democratic Party"),
        cand("Ed Orcutt", "Prefers Republican Party"),
    ], dist_scope("LEGDST", 20)),
    contest("State", "Legislative District 22", "State Representative Pos. 1", [
        cand("Beth Doglio", "Prefers Democratic Party"),
        cand("Don Hewett", "Prefers Republican Party"),
    ], dist_scope("LEGDST", 22)),
    contest("State", "Legislative District 22", "State Representative Pos. 2", [
        cand("Lisa Parshley", "Prefers Democratic Party"),
        cand("Jamie Keenan-deVargas", "Prefers Democratic Party"),
    ], dist_scope("LEGDST", 22)),
    contest("State", "Legislative District 35", "State Senator", [
        cand("Carolina Mejia", "Prefers Democratic Party"),
        cand("Drew C MacEwen", "Prefers Republican Party"),
    ], dist_scope("LEGDST", 35)),
    contest("State", "Legislative District 35", "State Representative Pos. 1", [
        cand("Dan Griffey", "Prefers Republican Party"),
        cand("Shaena Garberich", "Prefers Democratic Party"),
        cand("Jim Pierson", "Prefers Democratic Party"),
    ], dist_scope("LEGDST", 35)),
    contest("State", "Legislative District 35", "State Representative Pos. 2", [
        cand("Travis Couture", "Prefers Republican Party"),
        cand("Maria Littlesun", "Prefers Democratic Party"),
    ], dist_scope("LEGDST", 35)),
    contest("County", "Thurston County", "Assessor", [
        cand("JJ Olson", "Prefers Democratic Party"),
        cand("Lynda Nashed Zeman", "Prefers Democratic Party"),
    ], {"kind": "COUNTY", "county": "thurston"}),
    contest("County", "Thurston County", "Auditor", [
        cand("Tillie Naputi-Pullar", "Prefers Democratic Party"),
    ], {"kind": "COUNTY", "county": "thurston"}),
    contest("County", "Thurston County", "Clerk", [
        cand("Nicole Miller", "Prefers Democratic Party"),
        cand("Garrett Cady", "Prefers Independent Party"),
    ], {"kind": "COUNTY", "county": "thurston"}),
    contest("County", "Thurston County", "Coroner", [
        cand("Gary Warnock", "Prefers Democratic Party"),
    ], {"kind": "COUNTY", "county": "thurston"}),
    contest("County", "Thurston County", "Prosecuting Attorney", [
        cand("Christy Peters", "Prefers Democratic Party"),
    ], {"kind": "COUNTY", "county": "thurston"}),
    contest("County", "Thurston County", "Sheriff", [
        cand("Kevin Burton-Crow", "Prefers Democratic Party"),
        cand("Derek Sanders", "Prefers Independent Party"),
    ], {"kind": "COUNTY", "county": "thurston"}),
    contest("County", "Thurston County", "Treasurer", [
        cand("Jeff Gadman", "Prefers Democratic Party"),
    ], {"kind": "COUNTY", "county": "thurston"}),
]

OUT.mkdir(parents=True, exist_ok=True)
(OUT / "app-contests.json").write_text(json.dumps({
    "county": "thurston",
    "script": "pipeline/build_thurston_lite_data.py",
    "derived_from": [
        "data/washington-state/counties/thurston/interim/pdf-text/sample-ballot.txt",
        "data/washington-state/counties/thurston/interim/pdf-text/primary-candidates-ballot-order.txt",
    ],
    "coverage": "partial_county",
    "contests": contests,
}, indent=2))
(OUT / "app-measures.json").write_text(json.dumps({
    "county": "thurston",
    "script": "pipeline/build_thurston_lite_data.py",
    "derived_from": ["data/washington-state/counties/thurston/interim/pdf-text/sample-ballot.txt"],
    "coverage": "partial_county",
    "measures": [],
}, indent=2))
print(f"thurston contests: {len(contests)} measures: 0")
