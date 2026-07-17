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


def measure(jurisdiction, proposition, title, scope, page, what_it_does, cost_line):
    return {
        "slug": county_slug(f"{jurisdiction}-{proposition}"),
        "owner": "thurston",
        "jurisdiction": jurisdiction,
        "proposition": proposition,
        "title": title,
        "scope": scope,
        "pamphlet_pages": [{"edition": "local-voters-pamphlet", "page": page}],
        "what_it_does": what_it_does,
        "cost_line": cost_line,
        "pro_summary": None,
        "con_summary": None,
        "lean_mappings": {"taxes": {"direction": 2, "basis": "YES approves a local tax or bond measure for fire services.", "citations": ["Thurston local voters' pamphlet"]}},
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
    contest("County", "Thurston County Commissioner District No. 3", "County Commissioner", [
        cand("Tye Menser", "Prefers Democratic Party"),
    ], dist_scope("COUNTY_COUNCIL", 3)),
    contest("County", "Thurston County Commissioner District No. 5", "County Commissioner", [
        cand("Nicolas Martinez-Dunning", "Prefers Moderate Democrat Party"),
        cand("Emily Clouse", "Prefers Democratic Party"),
        cand("Michelle Gipson", "Prefers Democratic Party"),
    ], dist_scope("COUNTY_COUNCIL", 5)),
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
    contest("PublicUtility", "Thurston County Public Utility District Commissioner District No. 1", "Public Utility District Commissioner", [
        cand("Troy Kirby"),
        cand("Bruce D. Wilkinson, Jr."),
        cand("Jim Campbell"),
    ], dist_scope("PUDDST", 1)),
]

OUT.mkdir(parents=True, exist_ok=True)
(OUT / "app-contests.json").write_text(json.dumps({
    "county": "thurston",
    "script": "pipeline/build_thurston_lite_data.py",
    "derived_from": [
        "data/washington-state/counties/thurston/interim/pdf-text/sample-ballot.txt",
        "data/washington-state/counties/thurston/interim/pdf-text/primary-candidates-ballot-order.txt",
    ],
    "coverage": "full_county",
    "contests": contests,
}, indent=2))
(OUT / "app-measures.json").write_text(json.dumps({
    "county": "thurston",
    "script": "pipeline/build_thurston_lite_data.py",
    "derived_from": ["data/washington-state/counties/thurston/interim/pdf-text/sample-ballot.txt"],
    "coverage": "full_county",
    "measures": [
        measure("S.E. Thurston Fire Authority", "Proposition No. 1", "Bonds to Improve Fire Stations and Acquire Apparatus", dist_scope("FIRE_AUTH", "S.E. Thurston Fire Authority"), 66, "Authorizes bonds to renovate and improve Yelm, Lake Lawrence, Rainier, and McIntosh Ridge fire stations and acquire firefighting and emergency response apparatus.", "Authorizes up to $21,010,000 in general obligation bonds maturing within 25 years, repaid through annual excess property taxes."),
        measure("Thurston County Fire Protection District No. 1", "Proposition No. 1", "Property Tax for Fire Maintenance and Operations", dist_scope("FIRDST", "FD01"), 68, "Authorizes a four-year maintenance and operations levy to maintain fire services and emergency medical services in the Rochester-Grand Mound area.", "Authorizes levy amounts from $826,166 in 2027 to $956,500 in 2030, at an approximate rate of $0.38 per $1,000 of assessed value."),
        measure("Thurston County Fire Protection District No. 11", "Proposition No. 1", "Property Tax for Fire Maintenance and Operations", dist_scope("FIRDST", "FD11"), 70, "Authorizes a four-year maintenance and operations levy to maintain fire services and emergency medical services in the Littlerock-Maytown area.", "Authorizes levy amounts from $807,020 in 2027 to $934,226 in 2030, at an approximate rate of $0.38 per $1,000 of assessed value."),
    ],
}, indent=2))
print(f"thurston contests: {len(contests)} measures: 3")
