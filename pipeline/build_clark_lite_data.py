"""Build app-facing Clark County lite data from extracted official PDFs."""

import json
import re

import election
import votewa
from election import rel

# Usage: python3 pipeline/build_clark_lite_data.py [--election <id>]
ELECTION = election.Election(election.from_argv())
COUNTY = ELECTION.county("clark")
OUT = COUNTY / "interim"


# --- From the November 3, 2026 general on ----------------------------------
# Contests come from the county's VoteWA candidate-list export
# (counties/clark/raw/votewa/candidate-list.csv.{url,meta.json}, parsed by
# pipeline/votewa.py). general_override keeps this county's contest names
# (so slugs match the primary's and its dossiers carry forward) and the
# District Adapter layers in app/src/lib/geo.js COUNTY_LAYERS["clark"].
# GENERAL_MEASURES holds the county's curated measures per election, as
# {"sources": [raw pointer paths or official URLs], "measures": [app-measures
# rows]}; None means not curated yet. Everything below this block is the primary's
# sample-ballot transcription, frozen byte-identical.
PRIMARY = "2026-08-04-primary"

GENERAL_CFG = {"name": "Clark County"}
GENERAL_MEASURES = {"2026-11-03-general": None}


def general_override(r, unresolvable):
    dtype, district, race = r["District Type"].strip().upper(), r["District"].strip().upper(), r["Race"].strip()
    if dtype == "COUNCIL":
        n = votewa.district_number(district)
        return "County", f"Clark County Council District {n}", "County Councilor", ("COUNTY_COUNCIL", str(n))
    if dtype == "COUNTYWIDE":
        # 'COUNTY ASSESSOR' -> 'Assessor' (the primary's office names).
        return "County", "Clark County", votewa.titleish(re.sub(r"^COUNTY ", "", race.upper())), ("COUNTY", None)
    if dtype == "PUBLIC UTILITY":
        n = votewa.district_number(race)
        return ("Local", f"Public Utility District No. 1 of Clark County District {n}", "PUD Commissioner",
                ("PUDDST", str(n)))
    if dtype == "JUDICIAL" and district == "DISTRICT COURT JUDGES":
        # Clark County District Court is elected county-wide.
        n = votewa.district_number(race)
        return "Judicial", "Clark County District Court", f"Judge Department No. {n}", ("COUNTY", None)
    return None


if ELECTION.id != PRIMARY:
    CURATED = GENERAL_MEASURES.get(ELECTION.id)
    votewa.write_county_package(
        "clark", ELECTION.id, GENERAL_CFG, "pipeline/build_clark_lite_data.py",
        override=general_override,
        measures=CURATED["measures"] if CURATED else None,
        measure_sources=CURATED["sources"] if CURATED else (),
    )
    raise SystemExit(0)


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

def measure(slug, jurisdiction, proposition, title, scope, what_it_does, cost_line, basis):
    return {
        "slug": f"clark-{slug}",
        "owner": "clark",
        "jurisdiction": jurisdiction,
        "proposition": proposition,
        "title": title,
        "scope": scope,
        "pamphlet_pages": [],
        "what_it_does": what_it_does,
        "cost_line": cost_line,
        "pro_summary": None,
        "con_summary": None,
        "lean_mappings": {"taxes": {"direction": 2, "basis": basis, "citations": ["Clark sample ballot"]}},
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
    contest("County", "Clark County Council District 1", "County Councilor", [
        cand("Dusti Arab"),
        cand("Lukas Bardue"),
        cand("Glen Yung"),
        cand("Bryan Shull"),
    ], dist_scope("COUNTY_COUNCIL", 1)),
    contest("County", "Clark County Council District 2", "County Councilor", [
        cand("Martin Pittioni"),
        cand("Michelle Belkot"),
        cand("John Zingale"),
    ], dist_scope("COUNTY_COUNCIL", 2)),
    contest("County", "Clark County Council District 5", "County Councilor", [
        cand("Peter Silliman"),
        cand("Troy McCoy"),
    ], dist_scope("COUNTY_COUNCIL", 5)),
    contest("County", "Clark County", "Prosecuting Attorney", [
        cand("Laurel Smith"),
    ], {"kind": "COUNTY", "county": "clark"}),
    contest("County", "Clark County", "Sheriff", [
        cand("John Horch"),
    ], {"kind": "COUNTY", "county": "clark"}),
    contest("County", "Clark County", "Treasurer", [
        cand("Alishia Topper"),
    ], {"kind": "COUNTY", "county": "clark"}),
    contest("Local", "Public Utility District No. 1 of Clark County District 3", "PUD Commissioner", [
        cand("Gordon Matthews"),
        cand("Kevin Roegner"),
        cand("Jane A. Van Dyke"),
    ], dist_scope("PUDDST", 3)),
]

measures = [
    measure(
        "east-county-fire-and-rescue-proposition-no-6",
        "East County Fire & Rescue",
        "Proposition No. 6",
        "Emergency Medical Services Property Tax Levy",
        dist_scope("FIRDST", 1),
        "Continues East County Fire & Rescue's regular emergency medical services property tax levy for six consecutive years beginning in 2027.",
        "Authorizes a regular property tax levy of $0.35 or less per $1,000 of assessed value.",
        "YES continues a property tax levy for emergency medical services.",
    ),
    measure(
        "clark-county-fire-protection-district-no-10-proposition-no-3",
        "Clark County Fire Protection District No. 10",
        "Proposition No. 3",
        "New Fire Station General Obligation Bonds",
        dist_scope("FIRDST", 10),
        "Authorizes the district to construct and equip a new fire station, issue $15.2 million in general obligation bonds maturing within 20 years, and levy annual excess property taxes to repay the bonds.",
        "Authorizes $15,200,000 in bonds repaid by annual excess property taxes.",
        "YES authorizes bond debt and excess property taxes for a new fire station.",
    ),
]

OUT.mkdir(parents=True, exist_ok=True)
(OUT / "app-contests.json").write_text(json.dumps({
    "county": "clark",
    "script": "pipeline/build_clark_lite_data.py",
    "derived_from": [rel(COUNTY / "interim/pdf-text/sample-ballot.txt")],
    "coverage": "full_county",
    "contests": contests,
}, indent=2))
(OUT / "app-measures.json").write_text(json.dumps({
    "county": "clark",
    "script": "pipeline/build_clark_lite_data.py",
    "derived_from": [rel(COUNTY / "interim/pdf-text/sample-ballot.txt")],
    "coverage": "full_county",
    "measures": measures,
}, indent=2))
print(f"clark contests: {len(contests)} measures: {len(measures)}")
