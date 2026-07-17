"""Build app-facing Clark County lite data from extracted official PDFs."""

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
COUNTY = ROOT / "data/washington-state/counties/clark"
OUT = COUNTY / "interim"


def slugify(s: str) -> str:
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", s.lower())).strip("-")


def county_slug(s: str) -> str:
    return f"clark-{slugify(s)}"


def dist_scope(layer, value):
    return {"kind": "DISTRICT", "county": "clark", "layer": layer, "value": str(value)}


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
        "owner": "clark",
        "category": category,
        "office": office,
        "district": district,
        "scope": scope,
        "office_does": None,
        "race_blurb": "Official ballot listing imported from the Clark County sample ballot. Candidate scoring is not complete for this county yet.",
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
    contest("State", "Legislative District 17", "State Representative Pos. 1", [
        cand("Kevin Waters", "Prefers Republican Party"),
        cand("Thomas Everett Haynes", "Prefers Pro Gun Liberal Party"),
        cand("Ben Christly", "Prefers Democratic Party"),
    ], dist_scope("LEGDST", 17)),
    contest("State", "Legislative District 17", "State Representative Pos. 2", [
        cand("Diana H. Perez", "Prefers Democratic Party"),
        cand("David Stuebe", "Prefers Republican Party"),
    ], dist_scope("LEGDST", 17)),
    contest("State", "Legislative District 18", "State Representative Pos. 1", [
        cand("Stephanie McClintock", "Prefers Republican Party"),
        cand("Randi L. Knott", "Prefers Democratic Party"),
    ], dist_scope("LEGDST", 18)),
    contest("State", "Legislative District 18", "State Representative Pos. 2", [
        cand("John Ley", "Prefers Republican Party"),
        cand("Deken Letinich", "Prefers Democratic Party"),
    ], dist_scope("LEGDST", 18)),
    contest("State", "Legislative District 20", "State Representative Pos. 1", [
        cand("Peter Abbarno", "Prefers Republican Party"),
        cand("Andy Zahn", "Prefers Democratic Party"),
    ], dist_scope("LEGDST", 20)),
    contest("State", "Legislative District 20", "State Representative Pos. 2", [
        cand("Evan Jones", "Prefers Democratic Party"),
        cand("Ed Orcutt", "Prefers Republican Party"),
    ], dist_scope("LEGDST", 20)),
    contest("State", "Legislative District 49", "State Representative Pos. 1", [
        cand("Kim D. Harless", "Prefers Democratic Party"),
        cand("Sarah Mittelman", "Prefers Republican Party"),
        cand("Mike Pond", "Prefers Democratic Party"),
    ], dist_scope("LEGDST", 49)),
    contest("State", "Legislative District 49", "State Representative Pos. 2", [
        cand("Monica Jurado Stonier", "Prefers Democratic Party"),
        cand("Derek Thompson", "Prefers Republican Party"),
    ], dist_scope("LEGDST", 49)),
    contest("County", "Clark County", "Assessor", [
        cand("Tyler Thoune"),
        cand("Peter Van Nortwick"),
    ], {"kind": "COUNTY", "county": "clark"}),
    contest("County", "Clark County", "Auditor", [
        cand("Mitchell Kelly"),
        cand("Eileen Quiring O'Brien"),
        cand("Sharon Wylie"),
        cand("Ty Stober"),
    ], {"kind": "COUNTY", "county": "clark"}),
    contest("County", "Clark County", "Clerk", [
        cand("Scott G Weber"),
        cand("Rachel Shapiro"),
        cand("Gerald E. Gray"),
    ], {"kind": "COUNTY", "county": "clark"}),
    contest("County", "Clark County", "Prosecuting Attorney", [
        cand("Laurel Smith"),
    ], {"kind": "COUNTY", "county": "clark"}),
    contest("County", "Clark County", "Sheriff", [
        cand("John Horch"),
    ], {"kind": "COUNTY", "county": "clark"}),
    contest("County", "Clark County", "Treasurer", [
        cand("Alishia Topper"),
    ], {"kind": "COUNTY", "county": "clark"}),
]

OUT.mkdir(parents=True, exist_ok=True)
(OUT / "app-contests.json").write_text(json.dumps({
    "county": "clark",
    "script": "pipeline/build_clark_lite_data.py",
    "derived_from": ["data/washington-state/counties/clark/interim/pdf-text/sample-ballot.txt"],
    "coverage": "partial_county",
    "contests": contests,
}, indent=2))
(OUT / "app-measures.json").write_text(json.dumps({
    "county": "clark",
    "script": "pipeline/build_clark_lite_data.py",
    "derived_from": ["data/washington-state/counties/clark/interim/pdf-text/sample-ballot.txt"],
    "coverage": "partial_county",
    "measures": [],
}, indent=2))
print(f"clark contests: {len(contests)} measures: 0")
