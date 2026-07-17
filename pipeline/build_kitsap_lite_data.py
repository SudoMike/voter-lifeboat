"""Build app-facing Kitsap County lite data from extracted official PDFs."""

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
COUNTY = ROOT / "data/washington-state/counties/kitsap"
OUT = COUNTY / "interim"


def slugify(s: str) -> str:
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", s.lower())).strip("-")


def county_slug(s: str) -> str:
    return f"kitsap-{slugify(s)}"


def dist_scope(layer, value):
    return {"kind": "DISTRICT", "county": "kitsap", "layer": layer, "value": str(value)}


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
        "owner": "kitsap",
        "category": category,
        "office": office,
        "district": district,
        "scope": scope,
        "office_does": None,
        "race_blurb": "Official ballot listing imported from the Kitsap County local voters' pamphlet. Candidate scoring is not complete for this county yet.",
        "uncontested": len(candidates) == 1,
        "candidates": candidates,
    }

def measure(slug, jurisdiction, proposition, title, scope, what_it_does, cost_line, basis):
    return {
        "slug": f"kitsap-{slug}",
        "owner": "kitsap",
        "jurisdiction": jurisdiction,
        "proposition": proposition,
        "title": title,
        "scope": scope,
        "pamphlet_pages": [],
        "what_it_does": what_it_does,
        "cost_line": cost_line,
        "pro_summary": None,
        "con_summary": None,
        "lean_mappings": {"taxes": {"direction": 2, "basis": basis, "citations": ["Kitsap local voters' pamphlet"]}},
    }


contests = [
    contest("Federal", "Congressional District 6", "U.S. Representative", [
        cand("Emily Randall", "Prefers Democratic Party"),
        cand("Brian P. O'Gorman", "Prefers Independent Party"),
        cand("Teresa Fox", "Prefers Republican Party"),
        cand("Macy Jones", "States No Party Preference"),
        cand("Leon Lawson", "Prefers Trump Republican Party"),
    ], dist_scope("CONGDST", 6)),
    contest("State", "Legislative District 23", "State Representative Pos. 1", [
        cand("Daria Ilgen", "Prefers Democratic Party"),
        cand("Tarra Simmons", "Prefers Democratic Party"),
    ], dist_scope("LEGDST", 23)),
    contest("State", "Legislative District 23", "State Representative Pos. 2", [
        cand("Greg Nance", "Prefers Democratic Party"),
        cand("Lance Byrd", "Prefers Republican Party"),
        cand("Kristin Lillegard", "Prefers Democratic Party"),
    ], dist_scope("LEGDST", 23)),
    contest("State", "Legislative District 26", "State Senator", [
        cand("Deborah Krishnadasan", "Prefers Democratic Party"),
        cand("Gary Parker", "Prefers Republican Party"),
    ], dist_scope("LEGDST", 26)),
    contest("State", "Legislative District 26", "State Representative Pos. 1", [
        cand("David Olson", "Prefers Republican Party"),
        cand("Natalie Bornfleth", "Prefers Democratic Party"),
        cand("Adison Richards", "Prefers Democratic Party"),
    ], dist_scope("LEGDST", 26)),
    contest("State", "Legislative District 26", "State Representative Pos. 2", [
        cand("Randy Phillips", "States No Party Preference"),
        cand("Tedd Wetherbee", "Prefers Democratic Party"),
        cand("Renee Hernandez Greenfield", "Prefers Democratic Party"),
        cand("Katy Cornell", "Prefers Republican Party"),
    ], dist_scope("LEGDST", 26)),
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
    contest("County", "Kitsap County", "Assessor", [
        cand("Phil Cook", "Prefers Republican Party"),
        cand("Michael Simonds", "Prefers Democratic Party"),
    ], {"kind": "COUNTY", "county": "kitsap"}),
    contest("County", "Kitsap County Commissioner District 3", "County Commissioner", [
        cand("Kevin Tisdel", "Prefers Republican Party"),
        cand("Katie Walters", "Prefers Democratic Party"),
    ], dist_scope("COUNTY_COUNCIL", 3)),
    contest("County", "Kitsap County", "Auditor", [
        cand("Paul Andrews", "Prefers Democratic Party"),
    ], {"kind": "COUNTY", "county": "kitsap"}),
    contest("County", "Kitsap County", "Clerk", [
        cand("David T Lewis III", "Prefers Democratic Party"),
        cand("Brien Kennedy", "Prefers Democratic Party"),
    ], {"kind": "COUNTY", "county": "kitsap"}),
    contest("County", "Kitsap County", "Prosecuting Attorney", [
        cand("Joe Lombardi", "Prefers Democratic Party"),
        cand("Chad M. Enright", "Prefers Democratic Party"),
    ], {"kind": "COUNTY", "county": "kitsap"}),
    contest("County", "Kitsap County", "Sheriff", [
        cand("Rick Kuss", "Prefers Republican Party"),
        cand("Brandon L. Myers", "Prefers Democratic Party"),
    ], {"kind": "COUNTY", "county": "kitsap"}),
    contest("County", "Kitsap County", "Treasurer", [
        cand("Pete Boissonneau", "Prefers Democratic Party"),
    ], {"kind": "COUNTY", "county": "kitsap"}),
]

measures = [
    {
        "slug": "kitsap-city-of-bremerton-proposition-no-1",
        "owner": "kitsap",
        "jurisdiction": "City of Bremerton",
        "proposition": "Proposition No. 1",
        "title": "Public Safety and Governmental Services Levy",
        "scope": dist_scope("CITY", "Bremerton"),
        "pamphlet_pages": [{"edition": "local-voters-pamphlet", "page": 48}],
        "what_it_does": "Raises Bremerton's regular property tax rate by $0.48 to a total authorized rate of $1.95 per $1,000 of assessed value for 2027, with the 2027 levy amount used to calculate subsequent levies for public safety and governmental services.",
        "cost_line": "Increases the city property tax rate by $0.48 per $1,000 of assessed value for 2027 collections.",
        "pro_summary": None,
        "con_summary": None,
        "lean_mappings": {"taxes": {"direction": 2, "basis": "YES raises a city property tax levy for public safety and governmental services.", "citations": ["Kitsap local voters' pamphlet"]}},
    },
    measure(
        "kitsap-county-fire-protection-district-no-18-proposition-no-1",
        "Kitsap County Fire Protection District No. 18",
        "Proposition No. 1",
        "Bonds for Fire and Emergency Response Facilities, Vehicles and Equipment",
        dist_scope("FIRDST", 18),
        "Authorizes Poulsbo Fire to acquire, construct, and renovate firefighting and emergency response facilities, vehicles, and equipment, issue up to $7.64 million in general obligation bonds maturing within 6 years, and levy annual excess property taxes to repay the bonds.",
        "Authorizes up to $7,640,000 in bonds repaid by annual excess property taxes.",
        "YES authorizes bond debt and excess property taxes for fire and emergency response facilities, vehicles, and equipment.",
    ),
    measure(
        "north-mason-regional-fire-authority-proposition-no-1",
        "North Mason Regional Fire Authority",
        "Proposition No. 1",
        "Emergency Medical Services Property Tax Levy",
        dist_scope("FIRDST", "MCF2"),
        "Continues North Mason Regional Fire Authority's emergency medical services property tax levy for six consecutive years beginning in 2027.",
        "Continues a regular EMS property tax levy of $0.50 or less per $1,000 of assessed value.",
        "YES continues a property tax levy for emergency medical services.",
    ),
]

OUT.mkdir(parents=True, exist_ok=True)
(OUT / "app-contests.json").write_text(json.dumps({
    "county": "kitsap",
    "script": "pipeline/build_kitsap_lite_data.py",
    "derived_from": ["data/washington-state/counties/kitsap/interim/pdf-text/local-voters-pamphlet.txt"],
    "coverage": "full_county",
    "contests": contests,
}, indent=2))
(OUT / "app-measures.json").write_text(json.dumps({
    "county": "kitsap",
    "script": "pipeline/build_kitsap_lite_data.py",
    "derived_from": ["data/washington-state/counties/kitsap/interim/pdf-text/local-voters-pamphlet.txt"],
    "coverage": "full_county",
    "measures": measures,
}, indent=2))
print(f"kitsap contests: {len(contests)} measures: {len(measures)}")
