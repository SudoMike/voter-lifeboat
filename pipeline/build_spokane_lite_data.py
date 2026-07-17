"""Build app-facing Spokane County lite data from extracted official PDFs."""

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
COUNTY = ROOT / "data/washington-state/counties/spokane"
OUT = COUNTY / "interim"


def slugify(s: str) -> str:
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", s.lower())).strip("-")


def county_slug(s: str) -> str:
    return f"spokane-{slugify(s)}"


def dist_scope(layer, value):
    return {"kind": "DISTRICT", "county": "spokane", "layer": layer, "value": str(value)}


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
        "owner": "spokane",
        "category": category,
        "office": office,
        "district": district,
        "scope": scope,
        "office_does": None,
        "race_blurb": "Official ballot listing imported from the Spokane County sample ballot. Candidate scoring is not complete for this county yet.",
        "uncontested": len(candidates) == 1,
        "candidates": candidates,
    }


contests = [
    contest("Federal", "Congressional District 5", "U.S. Representative", [
        cand("Nate Powell", "Prefers Independent Party"),
        cand("Carmela Conroy", "Prefers Democratic Party"),
        cand("Matthew Hayes", "Prefers Independent Party"),
        cand("Bajun R. Mavalwalla", "Prefers Democratic Party"),
        cand("Michael McGarr", "Prefers Democratic Party"),
        cand("Kevin Fagan", "Prefers Democratic Party"),
        cand("Michael Baumgartner", "Prefers Republican Party"),
        cand("Kyle Usrey", "Prefers Independent Party"),
        cand("Andrew Bartleson", "Prefers Independent Party"),
        cand("Ann Marie Danimus", "Prefers Independent Party"),
        cand("Richard Freudenberg", "Prefers Democratic Party"),
        cand("David Womack", "Prefers Democratic Party"),
    ], dist_scope("CONGDST", 5)),
    contest("State", "Legislative District 3", "State Representative Pos. 1", [
        cand("Natasha Hill", "Prefers Democrat Party"),
        cand("John Kness", "States No Party Preference"),
        cand("Tony Kiepe", "Prefers Republican Party"),
    ], dist_scope("LEGDST", 3)),
    contest("State", "Legislative District 3", "State Representative Pos. 2", [
        cand("Natalie Poulson", "Prefers Republican Party"),
        cand("Pam Kohlmeier", "Prefers Democratic Party"),
        cand("Luc Jasmin III", "Prefers Democratic Party"),
        cand("Donovan Arnold DeLeon", "Prefers Democratic Party"),
    ], dist_scope("LEGDST", 3)),
    contest("State", "Legislative District 4", "State Representative Pos. 1", [
        cand("Trent Maier", "Prefers Republican Party"),
        cand("Hillary Q. Pham", "Prefers Republican Party"),
        cand("Debra Long", "Prefers Republican Party"),
        cand("George Wagner", "Prefers Republican Party"),
    ], dist_scope("LEGDST", 4)),
    contest("State", "Legislative District 4", "State Representative Pos. 2", [
        cand("Rob Chase", "Prefers Republican Party"),
        cand("Bob Curtis", "Prefers Republican Party"),
        cand("Rob Tupper", "Prefers Democratic Party"),
    ], dist_scope("LEGDST", 4)),
    contest("State", "Legislative District 6", "State Senator", [
        cand("Jeff Holy", "Prefers Republican Party"),
    ], dist_scope("LEGDST", 6)),
    contest("State", "Legislative District 6", "State Representative Pos. 1", [
        cand("Sueann Davis", "Prefers Republican Party"),
        cand("Isaiah Paine", "Prefers Republican Party"),
        cand("Michaela Kelso", "Prefers Democratic Party"),
        cand("Jennifer Morton", "Prefers Republican Party"),
        cand("Nicolette Ocheltree", "Prefers Democratic Party"),
        cand("Alan Nolan", "Prefers Republican Party"),
    ], dist_scope("LEGDST", 6)),
    contest("State", "Legislative District 6", "State Representative Pos. 2", [
        cand("Jonathan Bingle", "Prefers Republican Party"),
        cand("Julia Payne", "Prefers Democratic Party"),
        cand("Aaron M. Croft", "Prefers Independent Party"),
    ], dist_scope("LEGDST", 6)),
    contest("State", "Legislative District 7", "State Senator", [
        cand("Shelly Short", "Prefers Republican Party"),
        cand("Ronald L McCoy", "Prefers Independent Party"),
        cand("Brandon Ray Medina", "Prefers Republican Party"),
        cand("David Swoap", "Prefers Republican Party"),
    ], dist_scope("LEGDST", 7)),
    contest("State", "Legislative District 7", "State Representative Pos. 1", [
        cand("Andrew Engell", "Prefers Republican Party"),
    ], dist_scope("LEGDST", 7)),
    contest("State", "Legislative District 7", "State Representative Pos. 2", [
        cand("Hunter Abell", "Prefers Republican Party"),
    ], dist_scope("LEGDST", 7)),
    contest("State", "Legislative District 9", "State Representative Pos. 1", [
        cand("Mary Dye", "Prefers Republican Party"),
    ], dist_scope("LEGDST", 9)),
    contest("State", "Legislative District 9", "State Representative Pos. 2", [
        cand("Joe Schmick", "Prefers Republican Party"),
        cand("Karina Wallace", "Prefers Democratic Party"),
    ], dist_scope("LEGDST", 9)),
    contest("County", "Spokane County", "Assessor", [
        cand("Tom Konis", "Prefers Republican Party"),
    ], {"kind": "COUNTY", "county": "spokane"}),
    contest("County", "Spokane County", "Auditor", [
        cand("Callie Gee", "Prefers Democratic Party"),
        cand("Dale Whitaker", "Prefers Republican Party"),
        cand("Michael Cathcart", "Prefers Republican Party"),
    ], {"kind": "COUNTY", "county": "spokane"}),
    contest("County", "Spokane County", "Clerk", [
        cand("Elliot Robison", "Prefers Democratic Party"),
        cand("Dave Lucas", "Prefers Republican Party"),
    ], {"kind": "COUNTY", "county": "spokane"}),
    contest("County", "Spokane County", "Prosecuting Attorney", [
        cand("Danny Tarkenton", "States No Party Preference"),
        cand("Preston McCollam", "Prefers Republican Party"),
    ], {"kind": "COUNTY", "county": "spokane"}),
    contest("County", "Spokane County", "Sheriff", [
        cand("John F. Nowels", "Prefers Republican Party"),
    ], {"kind": "COUNTY", "county": "spokane"}),
    contest("County", "Spokane County", "Treasurer", [
        cand("Mike Volz", "Prefers Republican Party"),
    ], {"kind": "COUNTY", "county": "spokane"}),
]

measures = [
    {
        "slug": "spokane-city-of-cheney-proposition-no-1",
        "owner": "spokane",
        "jurisdiction": "City of Cheney",
        "proposition": "Proposition No. 1",
        "title": "Renewal of Residential Street Utility Tax",
        "scope": dist_scope("CITY", "Cheney"),
        "pamphlet_pages": [{"edition": "local-voters-pamphlet", "page": 46}],
        "what_it_does": "Renews Cheney's tax on electrical energy and natural gas businesses to 16.75% of gross revenue for 14 years, with proceeds used to repair streets and sidewalks.",
        "cost_line": "Renews a utility tax rate six percentage points above the otherwise authorized 10.75% rate for 14 years.",
        "pro_summary": None,
        "con_summary": None,
        "lean_mappings": {"taxes": {"direction": 2, "basis": "YES renews a utility tax for street and sidewalk repair.", "citations": ["Spokane sample ballot"]}},
    }
]

OUT.mkdir(parents=True, exist_ok=True)
(OUT / "app-contests.json").write_text(json.dumps({
    "county": "spokane",
    "script": "pipeline/build_spokane_lite_data.py",
    "derived_from": [
        "data/washington-state/counties/spokane/interim/pdf-text/sample-ballot.txt",
        "data/washington-state/counties/spokane/interim/pdf-text/local-voters-pamphlet.txt",
    ],
    "coverage": "partial_county",
    "contests": contests,
}, indent=2))
(OUT / "app-measures.json").write_text(json.dumps({
    "county": "spokane",
    "script": "pipeline/build_spokane_lite_data.py",
    "derived_from": [
        "data/washington-state/counties/spokane/interim/pdf-text/sample-ballot.txt",
        "data/washington-state/counties/spokane/interim/pdf-text/local-voters-pamphlet.txt",
    ],
    "coverage": "partial_county",
    "measures": measures,
}, indent=2))
print(f"spokane contests: {len(contests)} measures: {len(measures)}")
