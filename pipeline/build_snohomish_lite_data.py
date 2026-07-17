"""Build app-facing Snohomish County lite data from extracted official PDFs."""

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
COUNTY = ROOT / "data/washington-state/counties/snohomish"
TEXT = COUNTY / "interim/pdf-text/sample-ballot.txt"
OUT = COUNTY / "interim"


def slugify(s: str) -> str:
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", s.lower())).strip("-")


def county_slug(s: str) -> str:
    return f"snohomish-{slugify(s)}"


def dist_scope(layer, value):
    return {"kind": "DISTRICT", "county": "snohomish", "layer": layer, "value": str(value)}


def candidate_rows(block):
    rows = []
    for party, name in re.findall(r"\((Prefers [^)]+ Party|States No Party Preference)\)\s+(.+?)(?=\s+\(|\s+Write-In|\Z)", block):
        rows.append({
            "slug": slugify(name),
            "name": name.strip(),
            "party": party.strip(),
            "evidence_level": "official-ballot-only",
            "withdrawn": False,
            "summary": "Official ballot candidate. Voter Lifeboat has not completed a scored dossier for this candidate yet.",
            "highlights": [],
            "scores": {},
            "sources": [],
        })
    return rows


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


def measure(jurisdiction, proposition, title, scope, page, what_it_does, cost_line):
    return {
        "slug": county_slug(f"{jurisdiction}-{proposition}"),
        "owner": "snohomish",
        "jurisdiction": jurisdiction,
        "proposition": proposition,
        "title": title,
        "scope": scope,
        "pamphlet_pages": [{"edition": "local-voters-pamphlet", "page": page}],
        "what_it_does": what_it_does,
        "cost_line": cost_line,
        "pro_summary": None,
        "con_summary": None,
        "lean_mappings": {"taxes": {"direction": 2, "basis": "YES approves a local tax or bond measure for the listed public service.", "citations": ["Snohomish local voters' pamphlet"]}},
    }


text = TEXT.read_text()
scan = text.split("Election of Political Party Precinct Committee Officer", 1)[0]

patterns = [
    ("Federal", r"Congressional District (\d+)\s+U\.S\. Representative\s+Regular 2 year term - Vote for 1\s+(.*?)(?=(?:Congressional District|Legislative District|Snohomish County Prosecuting Attorney|Supreme Court|Public Utility|City of Everett|$))", "CONGDST"),
    ("State", r"Legislative District (\d+)\s+(State Representative Pos\. [12]|State Senator)\s+Regular [24] year term - Vote for 1\s+(.*?)(?=(?:Congressional District|Legislative District|Snohomish County Prosecuting Attorney|Supreme Court|Public Utility|City of Everett|$))", "LEGDST"),
]

contests = []
for category, pattern, layer in patterns:
    for m in re.finditer(pattern, scan, re.S):
        if category == "Federal":
            district_no, office, block = m.group(1), "U.S. Representative", m.group(2)
            district = f"Congressional District {district_no}"
        else:
            district_no, office, block = m.group(1), m.group(2), m.group(3)
            district = f"Legislative District {district_no}"
        cands = candidate_rows(block)
        if not cands:
            continue
        contests.append({
            "slug": county_slug(f"{district}-{office}"),
            "owner": "snohomish",
            "category": category,
            "office": office,
            "district": district,
            "scope": dist_scope(layer, district_no),
            "office_does": None,
            "race_blurb": "Official ballot listing imported from the Snohomish County sample ballot. Candidate scoring is not complete for this county yet.",
            "uncontested": len(cands) == 1,
            "candidates": cands,
        })

county_block = re.search(r"Snohomish County Prosecuting Attorney\s+Regular 4 year term - Vote for 1\s+(.*?)(?=Legislative District|Public Utility|Supreme Court|City of Everett)", scan, re.S)
if county_block:
    cands = candidate_rows(county_block.group(1))
    if cands:
        contests.append({
            "slug": county_slug("county-prosecuting-attorney"),
            "owner": "snohomish",
            "category": "County",
            "office": "Prosecuting Attorney",
            "district": "Snohomish County",
            "scope": {"kind": "COUNTY", "county": "snohomish"},
            "office_does": None,
            "race_blurb": "Official ballot listing imported from the Snohomish County sample ballot. Candidate scoring is not complete for this county yet.",
            "uncontested": len(cands) == 1,
            "candidates": cands,
        })

contests.append({
    "slug": county_slug("public-utility-district-no-1-commissioner-district-1"),
    "owner": "snohomish",
    "category": "PublicUtility",
    "office": "Commissioner District 1",
    "district": "Public Utility District No. 1",
    "scope": dist_scope("PUDDST", "PUD Commissioner District 1"),
    "office_does": None,
    "race_blurb": "Official ballot listing imported from the Snohomish County sample ballot. Candidate scoring is not complete for this county yet.",
    "uncontested": False,
    "candidates": [
        candidate("Sid Logan"),
        candidate("Bruce King"),
        candidate("Janet St Clair"),
    ],
})

measures = [
    measure("City of Everett", "Proposition No. 1", "Emergency Medical Services Levy Lid Lift", dist_scope("CITY", "Everett"), 64, "Restores Everett's emergency medical services levy to $0.50 per $1,000 of assessed value in 2027 and 2028 for emergency medical care, paramedic services, and related expenses.", "Restores the EMS levy rate to $0.50 per $1,000 of assessed value."),
    measure("City of Stanwood", "Proposition No. 1", "Sales and Use Tax for Enhanced Public Safety Services", dist_scope("CITY", "Stanwood"), 66, "Imposes a 0.1% sales and use tax for public safety and criminal justice purposes, including police staffing, dispatch, courts, prosecution, public defense, jail services, and related support.", "Adds a one-tenth of one percent (0.1%) sales and use tax."),
    measure("Darrington School District No. 330", "Proposition No. 1", "Replacement of Expiring Educational Programs and Operations Levy", dist_scope("SCHDST", "Darrington School District 330"), 68, "Replaces an expiring educational programs and operations levy for 2027 through 2030 to fund programs and services not funded by the state.", "Authorizes four annual levies of $950,000, with estimated rates declining from $1.24 to $1.02 per $1,000 of assessed value."),
    measure("Fire Protection District No. 15", "Proposition No. 1", "Tax Levy for Maintenance and Operations", dist_scope("FIRDST", "Fire District 15"), 70, "Authorizes a four-year excess property tax levy for maintenance and operations to maintain fire and emergency medical services.", "Authorizes $450,000 per year from 2027 through 2030, with estimated rates from $0.6214 to $0.6031 per $1,000 of assessed value."),
    measure("Fire Protection District No. 19", "Proposition No. 1", "Emergency Medical Services Levy Lid Lift", dist_scope("FIRDST", "Fire District 19"), 72, "Restores the district's emergency medical services levy and sets a six-year limit factor for levy increases.", "Restores the EMS levy to $0.50 per $1,000 of assessed value in 2027 and allows up to 106% annual increases through 2032."),
    measure("Snohomish Regional Fire and Rescue", "Proposition No. 1", "Emergency Medical Services Levy Lid Lift", dist_scope("FIRDST", "Snohomish Regional Fire & Rescue"), 74, "Restores the district's regular EMS property tax levy and authorizes inflation-indexed increases for five following years.", "Restores the EMS levy to $0.50 per $1,000 of assessed value for collection in 2027."),
    measure("Public Hospital District No. 1", "Proposition No. 1", "Bonds for New Replacement Hospital", dist_scope("HOSPDST", "Hospital District 1"), 76, "Authorizes construction and equipping of a replacement hospital and related capital improvements for EvergreenHealth Monroe.", "Authorizes up to $382,000,000 in general obligation bonds maturing within 30 years, repaid through annual excess property taxes."),
    measure("Sno-Isle Intercounty Rural Library District", "Proposition No. 1", "Regular Property Tax Levy Lid Lift for Support of Public Library Services", dist_scope("LIBDST", "Sno - Isle Library District"), 78, "Restores the library district's regular property tax levy rate for operations, maintenance, and library services.", "Restores the levy rate to $0.47 per $1,000 of assessed value for collection in 2027."),
]

OUT.mkdir(parents=True, exist_ok=True)
(OUT / "app-contests.json").write_text(json.dumps({
    "county": "snohomish",
    "script": "pipeline/build_snohomish_lite_data.py",
    "derived_from": ["data/washington-state/counties/snohomish/interim/pdf-text/sample-ballot.txt"],
    "coverage": "full_county",
    "contests": contests,
}, indent=2))
(OUT / "app-measures.json").write_text(json.dumps({
    "county": "snohomish",
    "script": "pipeline/build_snohomish_lite_data.py",
    "derived_from": ["data/washington-state/counties/snohomish/interim/pdf-text/sample-ballot.txt"],
    "coverage": "full_county",
    "measures": measures,
}, indent=2))
print(f"snohomish contests: {len(contests)} measures: {len(measures)}")
