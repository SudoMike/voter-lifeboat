"""Build app-facing Pierce County lite data from official sample ballot facts.

Pierce County's DocumentCenter PDFs are Cloudflare-challenged from this data
environment, so this package is keyed to the official sample ballot URL pointer
and includes only scopes the current non-King resolver can match: CONGDST,
LEGDST, CITY, and countywide. County council, district court, fire district,
and PCO items remain out until a Pierce district adapter exists.
"""

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
COUNTY = ROOT / "data/washington-state/counties/pierce"
OUT = COUNTY / "interim"


def slugify(s: str) -> str:
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", s.lower())).strip("-")


def county_slug(s: str) -> str:
    return f"pierce-{slugify(s)}"


def dist_scope(layer, value):
    return {"kind": "DISTRICT", "county": "pierce", "layer": layer, "value": str(value)}


def candidate(name, party=None):
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


def contest(category, district_no, office, candidates, layer):
    district = ("Congressional District" if layer == "CONGDST" else "Legislative District") + f" {district_no}"
    return {
        "slug": county_slug(f"{district}-{office}"),
        "owner": "pierce",
        "category": category,
        "office": office,
        "district": district,
        "scope": dist_scope(layer, district_no),
        "office_does": None,
        "race_blurb": "Official ballot listing imported from the Pierce County sample ballot. Candidate scoring is not complete for this county yet.",
        "uncontested": len(candidates) == 1,
        "candidates": candidates,
    }


contests = [
    contest("Federal", 6, "U.S. Representative", [
        candidate("Emily Randall", "Prefers Democratic Party"),
        candidate("Brian P. O'Gorman", "Prefers Independent Party"),
        candidate("Teresa Fox", "Prefers Republican Party"),
        candidate("Macy Jones", "States No Party Preference"),
        candidate("Leon Lawson", "Prefers Trump Republican Party"),
    ], "CONGDST"),
    contest("Federal", 8, "U.S. Representative", [
        candidate("Kim Schrier", "Prefers Democratic Party"),
        candidate("Trinh Ha", "Prefers Republican Party"),
        candidate("Spencer Meline", "Prefers Republican Party"),
        candidate("Keith Arnold", "Prefers Democratic Party"),
        candidate("Andres Valleza", "Prefers Republican Party"),
        candidate("Bob Hagglund", "Prefers Republican Party"),
    ], "CONGDST"),
    contest("Federal", 10, "U.S. Representative", [
        candidate("Adam Arafat", "Prefers Democratic Party"),
        candidate("Marilyn Strickland", "Prefers Democratic Party"),
        candidate("Kurtis Engle", "Prefers Union Party"),
        candidate("Alex Scheel", "Prefers Democratic Party"),
        candidate("Derek Maynes", "States No Party Preference"),
        candidate("Chris D. Chung", "Prefers Republican Party"),
    ], "CONGDST"),
    contest("State", 2, "State Representative Pos. 1", [
        candidate("William Dehnel", "Prefers Labor Democrat Party"),
        candidate("Andrew Barkis", "Prefers Republican Party"),
    ], "LEGDST"),
    contest("State", 2, "State Representative Pos. 2", [
        candidate("Angela Taylor", "Prefers Democratic Party"),
        candidate("Martin L Miller", "Prefers Democratic Party"),
        candidate("Matt Marshall", "Prefers Republican Party"),
    ], "LEGDST"),
    contest("State", 25, "State Representative Pos. 1", [
        candidate("David Berg", "Prefers Democratic Party"),
        candidate("Nick Oloo", "Prefers Democratic Party"),
        candidate("Michael Keaton", "Prefers Republican Party"),
    ], "LEGDST"),
    contest("State", 25, "State Representative Pos. 2", [
        candidate("Jenn Marie Strickling", "Prefers Democratic Party"),
        candidate("Ren Fanony", "Prefers Republican Party"),
        candidate("Cyndy Jacobsen", "Prefers Republican Party"),
    ], "LEGDST"),
    contest("State", 26, "State Senator", [
        candidate("Deborah Krishnadasan", "Prefers Democratic Party"),
        candidate("Gary Parker", "Prefers Republican Party"),
    ], "LEGDST"),
    contest("State", 26, "State Representative Pos. 1", [
        candidate("David Olson", "Prefers Republican Party"),
        candidate("Natalie Bornfleth", "Prefers Democratic Party"),
        candidate("Adison Richards", "Prefers Democratic Party"),
    ], "LEGDST"),
    contest("State", 26, "State Representative Pos. 2", [
        candidate("Randy Phillips", "States No Party Preference"),
        candidate("Tedd Wetherbee", "Prefers Democratic Party"),
        candidate("Renee Hernandez Greenfield", "Prefers Democratic Party"),
        candidate("Katy Cornell", "Prefers Republican Party"),
    ], "LEGDST"),
    contest("State", 27, "State Representative Pos. 1", [
        candidate("Laurie Jinkins", "Prefers Democratic Party"),
        candidate("Carole Sue Braaten", "Prefers Republican Party"),
    ], "LEGDST"),
    contest("State", 27, "State Representative Pos. 2", [
        candidate("Jake Fey", "Prefers Democratic Party"),
    ], "LEGDST"),
    contest("State", 28, "State Representative Pos. 1", [
        candidate("Mari Leavitt", "Prefers Democratic Party"),
        candidate("Kathy Richardson", "Prefers Republican Party"),
    ], "LEGDST"),
    contest("State", 28, "State Representative Pos. 2", [
        candidate("Dan Bronoske", "Prefers Democratic Party"),
    ], "LEGDST"),
    contest("State", 29, "State Senator", [
        candidate("Sharlett Mena", "Prefers Democratic Party"),
        candidate("David Anderson", "Prefers Democratic Party"),
    ], "LEGDST"),
    contest("State", 29, "State Representative Pos. 1", [
        candidate("Melanie Morgan", "Prefers Democratic Party"),
        candidate("Krista Perez", "Prefers Democratic Party"),
    ], "LEGDST"),
    contest("State", 29, "State Representative Pos. 2", [
        candidate("Darek Blum", "Prefers Republican Party"),
        candidate("Patrick Stickney", "Prefers Democratic Party"),
        candidate("Erin Chapman-Smith", "Prefers Democratic Party"),
        candidate("Natasha Laitila", "Prefers Democratic Party"),
        candidate("Sheri Hayes", "Prefers Republican Party"),
        candidate("Joe Bushnell", "Prefers Democratic Party"),
    ], "LEGDST"),
    contest("State", 31, "State Senator", [
        candidate("Tamara Stramel", "Prefers Democratic Party"),
        candidate("Phil Fortunato", "Prefers Republican Party"),
    ], "LEGDST"),
    contest("State", 31, "State Representative Pos. 1", [
        candidate("Drew Stokesbary", "Prefers Republican Party"),
        candidate("Stephen Szczurko-Walton", "Prefers Democratic Party"),
    ], "LEGDST"),
    contest("State", 31, "State Representative Pos. 2", [
        candidate("John Bielka", "Prefers Democrat Party"),
        candidate("Joshua Penner", "Prefers Republican Party"),
    ], "LEGDST"),
]

measures = [
    {
        "slug": "pierce-town-of-carbonado-proposition-no-1",
        "owner": "pierce",
        "jurisdiction": "Town of Carbonado",
        "proposition": "Proposition No. 1",
        "title": "Emergency Medical Services Property Tax Levy",
        "scope": dist_scope("CITY", "Carbonado"),
        "pamphlet_pages": [],
        "what_it_does": "Re-authorizes regular property tax levies of $0.50 or less per $1,000 of assessed valuation for six consecutive years to continue emergency medical services.",
        "cost_line": "Renews an EMS levy up to $0.50 per $1,000 of assessed value.",
        "pro_summary": None,
        "con_summary": None,
        "lean_mappings": {"taxes": {"direction": 2, "basis": "YES renews a local property tax levy for emergency medical services.", "citations": ["Pierce sample ballot"]}},
    },
    {
        "slug": "pierce-city-of-fircrest-proposition-no-1",
        "owner": "pierce",
        "jurisdiction": "City of Fircrest",
        "proposition": "Proposition No. 1",
        "title": "Emergency Medical Care and Services",
        "scope": dist_scope("CITY", "Fircrest"),
        "pamphlet_pages": [],
        "what_it_does": "Renews Fircrest's authority to impose regular property tax levies of up to $0.50 per $1,000 of assessed valuation for emergency medical care and services for six consecutive years.",
        "cost_line": "Renews an EMS levy up to $0.50 per $1,000 of assessed value.",
        "pro_summary": None,
        "con_summary": None,
        "lean_mappings": {"taxes": {"direction": 2, "basis": "YES renews a local property tax levy for emergency medical care and services.", "citations": ["Pierce sample ballot"]}},
    },
    {
        "slug": "pierce-city-of-tacoma-proposition-no-1",
        "owner": "pierce",
        "jurisdiction": "City of Tacoma",
        "proposition": "Proposition No. 1",
        "title": "Funding Transportation Safety Improvements",
        "scope": dist_scope("CITY", "Tacoma"),
        "pamphlet_pages": [],
        "what_it_does": "Funds street, sidewalk, route, pothole, paving, maintenance, traffic safety, and neighborhood connection improvements through utility and property tax increases for 10 years.",
        "cost_line": "Adds a 1.5% utility tax and raises the regular property tax levy by $0.20 per $1,000 for 2027 collections, with subsequent levies through 2036 based on the 2027 amount.",
        "pro_summary": None,
        "con_summary": None,
        "lean_mappings": {"taxes": {"direction": 2, "basis": "YES raises utility and property taxes for transportation safety improvements.", "citations": ["Pierce sample ballot"]}},
    },
]

OUT.mkdir(parents=True, exist_ok=True)
(OUT / "app-contests.json").write_text(json.dumps({
    "county": "pierce",
    "script": "pipeline/build_pierce_lite_data.py",
    "derived_from": ["data/washington-state/counties/pierce/raw/pierce/sample-ballot.pdf.url"],
    "coverage": "partial_county",
    "contests": contests,
}, indent=2))
(OUT / "app-measures.json").write_text(json.dumps({
    "county": "pierce",
    "script": "pipeline/build_pierce_lite_data.py",
    "derived_from": ["data/washington-state/counties/pierce/raw/pierce/sample-ballot.pdf.url"],
    "coverage": "partial_county",
    "measures": measures,
}, indent=2))
print(f"pierce contests: {len(contests)} measures: {len(measures)}")
