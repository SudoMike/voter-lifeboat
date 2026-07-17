"""Build app-facing Snohomish County lite data from extracted official PDFs.

This is deliberately conservative: it only emits contests whose scope can be
matched by the current non-King district resolver (CONGDST, LEGDST, CITY, and
countywide). More local district contests remain in the source package until a
district adapter can resolve school, fire, hospital, library, and PUD districts.
"""

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

measures = [
    {
        "slug": "city-of-everett-proposition-no-1",
        "owner": "snohomish",
        "jurisdiction": "City of Everett",
        "proposition": "Proposition No. 1",
        "title": "Emergency Medical Services Levy Lid Lift",
        "scope": dist_scope("CITY", "Everett"),
        "pamphlet_pages": [{"edition": "local-voters-pamphlet", "page": 64}],
        "what_it_does": "Restores Everett's emergency medical services levy to $0.50 per $1,000 of assessed value in 2027 and 2028 for emergency medical care, paramedic services, and related expenses.",
        "cost_line": "Restores the EMS levy rate to $0.50 per $1,000 of assessed value.",
        "pro_summary": None,
        "con_summary": None,
        "lean_mappings": {"taxes": {"direction": 2, "basis": "YES raises/restores a property tax levy for emergency medical services.", "citations": ["Snohomish sample ballot"]}},
    },
    {
        "slug": "city-of-stanwood-proposition-no-1",
        "owner": "snohomish",
        "jurisdiction": "City of Stanwood",
        "proposition": "Proposition No. 1",
        "title": "Sales and Use Tax for Enhanced Public Safety Services",
        "scope": dist_scope("CITY", "Stanwood"),
        "pamphlet_pages": [{"edition": "local-voters-pamphlet", "page": 66}],
        "what_it_does": "Imposes a 0.1% sales and use tax for public safety and criminal justice purposes, including police staffing, dispatch, courts, prosecution, public defense, jail services, and related support.",
        "cost_line": "Adds a one-tenth of one percent (0.1%) sales and use tax.",
        "pro_summary": None,
        "con_summary": None,
        "lean_mappings": {"taxes": {"direction": 2, "basis": "YES adds a local sales and use tax for public safety services.", "citations": ["Snohomish sample ballot"]}},
    },
]

OUT.mkdir(parents=True, exist_ok=True)
(OUT / "app-contests.json").write_text(json.dumps({
    "county": "snohomish",
    "script": "pipeline/build_snohomish_lite_data.py",
    "derived_from": ["data/washington-state/counties/snohomish/interim/pdf-text/sample-ballot.txt"],
    "coverage": "partial_county",
    "contests": contests,
}, indent=2))
(OUT / "app-measures.json").write_text(json.dumps({
    "county": "snohomish",
    "script": "pipeline/build_snohomish_lite_data.py",
    "derived_from": ["data/washington-state/counties/snohomish/interim/pdf-text/sample-ballot.txt"],
    "coverage": "partial_county",
    "measures": measures,
}, indent=2))
print(f"snohomish contests: {len(contests)} measures: {len(measures)}")
