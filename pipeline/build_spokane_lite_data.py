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


def measure(jurisdiction, proposition, title, scope, page, what_it_does, cost_line):
    return {
        "slug": county_slug(f"{jurisdiction}-{proposition}"),
        "owner": "spokane",
        "jurisdiction": jurisdiction,
        "proposition": proposition,
        "title": title,
        "scope": scope,
        "pamphlet_pages": [{"edition": "local-voters-pamphlet", "page": page}],
        "what_it_does": what_it_does,
        "cost_line": cost_line,
        "pro_summary": None,
        "con_summary": None,
        "lean_mappings": {"taxes": {"direction": 2, "basis": "YES approves a local tax or fee measure for the listed public service.", "citations": ["Spokane local voters' pamphlet"]}},
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
    contest("County", "Spokane County Commissioner District 2", "Commissioner", [
        cand("Amber Waldref", "Prefers Democratic Party"),
    ], dist_scope("COUNTY_COUNCIL", 2)),
    contest("County", "Spokane County Commissioner District 4", "Commissioner", [
        cand("Suzanne Schmidt", "Prefers Republican Party"),
    ], dist_scope("COUNTY_COUNCIL", 4)),
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
    measure("Spokane Transit Authority", "Proposition No. 1", "Maintenance and Enhancement of Public Transportation Services", dist_scope("PTBA", "Y"), 41, "Reauthorizes an existing voter-approved sales and use tax for public transportation services, transit system maintenance and enhancement, expansion, and support facilities.", "Reauthorizes up to 0.2% sales and use tax from January 1, 2029 through no later than December 31, 2048."),
    measure("Spokane County Library District", "Proposition No. 1", "Regular Library Operations and Maintenance Levy", dist_scope("LIBDST", "Spokane County Library District"), 43, "Restores the library district's regular property tax levy rate to support library operations, maintenance, services, materials, staffing, and facilities.", "Restores the levy rate to $0.45 per $1,000 of assessed value for collection in 2027."),
    # No public GIS boundary exists for the PROPOSED West Plains APA (the only
    # public "Aquifer" service is the Spokane Valley-Rathdrum Prairie aquifer,
    # a different geography). The AQUIFER layer is intentionally unresolvable,
    # so this measure is never shown to the wrong voters; it is why Spokane
    # remains partial_county.
    measure("West Plains Aquifer Protection Area", "Measure No. 1", "Spokane County West Plains Aquifer Protection Area", dist_scope("AQUIFER", "yes"), 44, "Authorizes monthly fees to fund aquifer protection activities including planning, water quality improvements, sewage and stormwater facilities, monitoring, inspections, and public education.", "Authorizes monthly fees up to $1.25 per household unit for water withdrawal and $1.25 for on-site sewage disposal for up to 20 years."),
    measure("City of Cheney", "Proposition No. 1", "Renewal of Residential Street Utility Tax", dist_scope("CITY", "Cheney"), 46, "Renews Cheney's tax on electrical energy and natural gas businesses to 16.75% of gross revenue for 14 years, with proceeds used to repair streets and sidewalks.", "Renews a utility tax rate six percentage points above the otherwise authorized 10.75% rate for 14 years."),
    # Rosalia Park & Recreation District #5 spans the Whitman county line; the
    # WA DOR park & recreation district layer (PKR2025) answers point queries
    # with DISTATTRIB 'ROSA' on the Spokane side (the Whitman side is '5').
    measure("Rosalia Park & Recreation District", "Proposition No. 1", "Two Year Maintenance and Operations Levy for the Rosalia Pool", dist_scope("PARKDST", "ROSA"), 47, "Authorizes the Rosalia Park and Recreation District No. 5 to levy regular property taxes in 2027 and 2028 to fund operating, maintaining, and improving the Rosalia Pool, including maintenance, supplies, salaries, and utilities. Requires a 60% supermajority to pass.", "Levies of $85,000.00 per year, approximately $0.39 (maximum $0.60) per $1,000 of assessed value, collected in 2027 and 2028."),
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
