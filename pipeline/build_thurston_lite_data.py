"""Build app-facing Thurston County lite data from extracted official PDFs."""

import json
import re

import election
import votewa
from election import rel

# Usage: python3 pipeline/build_thurston_lite_data.py [--election <id>]
ELECTION = election.Election(election.from_argv())
COUNTY = ELECTION.county("thurston")
OUT = COUNTY / "interim"


# --- From the November 3, 2026 general on ----------------------------------
# Contests come from the county's VoteWA candidate-list export
# (counties/thurston/raw/votewa/candidate-list.csv.{url,meta.json}, parsed by
# pipeline/votewa.py). general_override keeps this county's contest names
# (so slugs match the primary's and its dossiers carry forward) and the
# District Adapter layers in app/src/lib/geo.js COUNTY_LAYERS["thurston"].
# GENERAL_MEASURES holds the county's curated measures per election, as
# {"sources": [raw pointer paths or official URLs], "measures": [app-measures
# rows]}; None means not curated yet. Everything below this block is the primary's
# sample-ballot transcription, frozen byte-identical.
PRIMARY = "2026-08-04-primary"

# SCHDST and RFADST are not in app/src/lib/geo.js COUNTY_LAYERS["thurston"]
# (2026-10-08, #22), so the two measures scoped to them make the package
# partial_county until the director adds a layer for each:
# - SCHDST: Thurston County Elections' school director districts,
#   https://tconline.co.thurston.wa.us/server/rest/services/Common_Layers/Jurisdictions/FeatureServer/10,
#   attr SchoolDistrictName ('YELM' at 105 Yelm Ave W, Yelm; 'OLYMPIA',
#   'NORTH THURSTON', 'ROCHESTER' elsewhere). DOR SCH2025 (layer 20) agrees:
#   DISTATTRIB '2' (Yelm Community Schools No. 2) at the same point.
# - RFADST: West Thurston Regional Fire Authority (former Fire Districts 1,
#   Rochester, and 11, Littlerock). The FIRDST/FIRE_AUTH layer
#   (ThurstonExt/Thurston_FireDistricts_TCOMM/FeatureServer/0) splits it into
#   two polygons (DISPATCH_G 'FD01'/'FD11', CONSOL_DIS 'WTRFA - South Btn'/
#   'WTRFA - North Btn'); both carry CONSOL_NUM 'FD01', and no other polygon
#   does. A layer entry on that service with attr CONSOL_NUM and
#   where "CONSOL_DIS LIKE 'WTRFA%'" resolves it ('FD01' at 18346 Albany St
#   SW, Rochester and 10828 Littlerock Rd SW, Olympia). DOR FIR2025 has two
#   values ('1/WTRFA/1B', '11/WTRFA/11B'), so it cannot match one scope value.
GENERAL_CFG = {"name": "Thurston County", "unresolvable_layers": ["SCHDST", "RFADST"]}

_GEN = "data/washington-state/elections/2026-11-03-general/counties/thurston"
_PAGE = f"{_GEN}/raw/thurston/general-election.html.url"
_LVP = f"{_GEN}/raw/thurston/local-voters-pamphlet.pdf.url"
_BALLOT = f"{_GEN}/raw/thurston/sample-ballot.pdf.url"
_NO_CON = "No statement against was filed; the pamphlet says no one in the jurisdiction contacted the Auditor to write one."


def gen_measure(jurisdiction, proposition, title, scope, pages, ballot_title, cost_line, pro, con):
    """One general-election app-measures row. `jurisdiction`, `title` and
    `ballot_title` are verbatim from the sample ballot
    (raw/thurston/sample-ballot.pdf.url); `pages` are local-voters-pamphlet
    PDF pages (ballot title, explanatory statement, statements for and
    against). Display fields are overlaid by scoring/measures.json at
    assembly."""
    return {
        "slug": "thurston-" + votewa.slugify(f"{jurisdiction}-{proposition}"),
        "owner": "thurston",
        "jurisdiction": jurisdiction,
        "proposition": proposition,
        "title": title,
        "scope": scope,
        "pamphlet_pages": [{"edition": "local-voters-pamphlet", "page": p} for p in pages],
        "what_it_does": ballot_title,
        "cost_line": cost_line,
        "pro_summary": pro,
        "con_summary": con,
        "lean_mappings": {},
    }


def _district(layer, value):
    return {"kind": "DISTRICT", "county": "thurston", "layer": layer, "value": value}


# The four local measures on the composite sample ballot (Rev. 08/24/2026),
# the Auditor's resolution list and the pamphlet's measure pages agree. The
# pamphlet's PDF page 28 also carries a stray "Thurston County Fire
# Protection District 12 Proposition No. 1" heading and ballot title (a
# leftover; that page's statements are Lacey Fire District 3's): FD 12 is on
# neither the sample ballot nor the resolution list, so it is not a measure.
GENERAL_MEASURES = {"2026-11-03-general": {
    "sources": [_BALLOT, _LVP, _PAGE],
    "measures": [
        # Scope: county-wide. The sample ballot heads it "Countywide Measure";
        # DOR LIB2025 (layer 12) returns 'L' (Timberland) at every check
        # address (Olympia, Lacey, Yelm, Littlerock, Rochester).
        gen_measure("Timberland Regional Library District", "Proposition No. 1",
                    "Regular Property Tax Levy Lid Lift for Library Services, Operations and Maintenance",
                    {"kind": "COUNTY", "county": "thurston"}, [24, 25],
                    "The Timberland Regional Library District's Board of Trustees adopted Resolution No. 26-002 concerning a proposed increase of the District's regular levy rate. If approved, this proposition would restore the District's regular property tax levy rate for library services, operations and maintenance from $0.22 to $0.35 per $1,000 of assessed valuation for both 2027 and 2028, subject to applicable limitations. The resulting 2028 levy dollar amount would be used for the purpose of computing subsequent levy limitations under chapter 84.55 RCW.",
                    "Levy lid lift from $0.22 to $0.35 per $1,000 of assessed value for 2027 and 2028; the 2028 amount becomes the base for later limits (about $40 a year on a $334,000 home, per the explanatory statement).",
                    "TimberStrong Libraries Committee: the levy has not risen in 25 years; restores hours, staffing and collections at Thurston's eight branches (about $69 a year on a median $530,959 home).",
                    "Sean Swope (Citizens for Accountable TR Libraries): property owners already face rising bills; the library should cut costs and show prudent management before asking for more."),
        # Scope: SCHDST (unresolvable today, see GENERAL_CFG). 105 Yelm Ave W,
        # Yelm (Census-geocoded -122.60775, 46.94251) -> Jurisdictions/10
        # SchoolDistrictName 'YELM' (2026-10-08).
        gen_measure("Yelm Community Schools", "Proposition No. 1",
                    "Educational Programs and Operations Maintenance Levy",
                    _district("SCHDST", "YELM"), [26, 27],
                    "The Board of Directors of Yelm Community Schools adopted Resolution No. 09-25-26, authorizing a levy to maintain existing educational program support levels. This proposition would authorize the District to levy the following excess taxes, on taxable property within the District, to maintain essential educational programs, extracurricular activities, and operations not funded by the State (including, but not limited to, teachers, arts, nurses, counselors, classified staff, paraeducators, safety, graduation readiness, technology, athletics, facilities, curriculum): Collection Year Estimated Levy Rate/$1,000 Assessed Value Maximum Levy Amount 2027 $1.50 $11,194,449 2028 $1.50 $12,278,072 all as provided in Resolution No. 09-25-26.",
                    "Two-year excess levy at an estimated $1.50 per $1,000 of assessed value: up to $11,194,449 (2027) and $12,278,072 (2028).",
                    "Yelm Kids First: after several levy failures the district has cut staff, programs and athletics; the levy pays for teachers, nurses, counselors, safety staff and activities the state does not fully fund.",
                    "Martin Miller and Frank Vance: voters have said no four times; the district used one-time money for recurring costs and restores none of the cuts; press Olympia to fund schools instead."),
        # Scope: FIRDST. 420 College St SE, Lacey (Census-geocoded -122.82314,
        # 47.0446) -> DISPATCH_G 'FD03' (DOR FIR2025 '3') (2026-10-08).
        gen_measure("Thurston County Fire Protection District No. 3 (Lacey Fire District 3)", "Proposition No. 1",
                    "Bonds for Fire Stations, Training Facility, Logistics Warehouse",
                    _district("FIRDST", "FD03"), [28],
                    "The Board of Fire Commissioners of Thurston County Fire Protection District No. 3 (Lacey Fire District 3) adopted Resolution No. 903-06-26, concerning emergency services facilities to protect public health, life and property. This proposition would authorize the District to: construct a new community fire station (Britton Pkwy); replace Station 32 (Yelm Hwy); construct a regional live fire training facility and logistics warehouse; acquire property (and pay associated financing costs); make other capital improvements and apparatus acquisitions; issue no more than $98,300,000 of general obligation bonds maturing within 20 years; and levy annual excess property taxes to repay the bonds, all as provided in Resolution No. 903-06-26.",
                    "Up to $98,300,000 in bonds maturing within 20 years, repaid by excess property taxes at an approximate $0.23 per $1,000 of assessed value (about $9.60 a month on a $500,000 home).",
                    "Steve Brooks and Tom Carroll: calls are up 43% in ten years and only one of five stations is north of I-5; a new station and a replaced Station 32 cut response times.",
                    _NO_CON),
        # Scope: RFADST (unresolvable today, see GENERAL_CFG). 18346 Albany St
        # SW, Rochester (-123.09698, 46.82062) and 10828 Littlerock Rd SW,
        # Olympia (-122.99209, 46.93043) -> fire layer CONSOL_NUM 'FD01'
        # (CONSOL_DIS 'WTRFA - South Btn' / 'WTRFA - North Btn') (2026-10-08).
        gen_measure("West Thurston Regional Fire Authority (Rochester & Littlerock)", "Proposition No. 1",
                    "Property Tax for Fire Maintenance and Operations",
                    _district("RFADST", "FD01"), [29],
                    "The Board of Commissioners of West Thurston Regional Fire Authority adopted Resolution No. 2026-005 concerning a proposition to finance maintenance and operation expenses. This proposition, if approved, will authorize the Authority to levy, without regard to the dollar rate and percentage limitations imposed by Chapter 84.52 RCW, a property tax upon all taxable property within the Authority's boundaries of: Collection Year Approximate Levy Rate/$1,000 Assessed Value Levy Amount 2027 $0.36 $1,547,228.00 to be used for maintenance and operations and to maintain the current level of fire services and emergency medical services as provided in Resolution No. 2026-005.",
                    "One-year excess levy of $1,547,228 in 2027, about $0.36 per $1,000 of assessed value (up to $15 a month on a $500,000 home).",
                    "Tyler Mason and Cathe Linn: many frontline vehicles are past their service life and stations need HVAC, roof and plumbing work; levy money goes to apparatus replacement and facility maintenance.",
                    _NO_CON),
    ],
}}


def general_override(r, unresolvable):
    dtype, district, race = r["District Type"].strip().upper(), r["District"].strip().upper(), r["Race"].strip()
    if dtype == "COMMISSIONER":
        # 'COMMISSIONER DISTRICT ALL COUNTY': nominated by district in the
        # primary, elected county-wide in the general (RCW 36.32.0556 for a
        # five-member board, as Thurston's is).
        n = votewa.district_number(race)
        scope = ("COUNTY", None) if "ALL COUNTY" in district else ("COUNTY_COUNCIL", str(n))
        return "County", f"Thurston County Commissioner District No. {n}", "County Commissioner", scope
    if dtype == "PUBLIC UTILITY":
        # Nominated by commissioner district in the primary; voters of the
        # entire PUD elect in the general (RCW 54.12.010(3)). Thurston PUD's
        # three commissioner districts (Jurisdictions/FeatureServer/15) tile
        # the whole county: their areas sum to the five county commissioner
        # districts' (4,099,049,658 sq m in both layers, 2026-10-08).
        n = votewa.district_number(race)
        return ("PublicUtility", f"Thurston County Public Utility District Commissioner District No. {n}",
                "Public Utility District Commissioner", ("COUNTY", None))
    if dtype == "COUNTYWIDE" and race.upper().startswith("DISTRICT COURT JUDGE"):
        n = votewa.district_number(race)
        return "Judicial", "Thurston County District Court", f"Judge Position No. {n}", ("COUNTY", None)
    return None


if ELECTION.id != PRIMARY:
    CURATED = GENERAL_MEASURES.get(ELECTION.id)
    votewa.write_county_package(
        "thurston", ELECTION.id, GENERAL_CFG, "pipeline/build_thurston_lite_data.py",
        override=general_override,
        measures=CURATED["measures"] if CURATED else None,
        measure_sources=CURATED["sources"] if CURATED else (),
    )
    raise SystemExit(0)


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
        rel(COUNTY / "interim/pdf-text/sample-ballot.txt"),
        rel(COUNTY / "interim/pdf-text/primary-candidates-ballot-order.txt"),
    ],
    "coverage": "full_county",
    "contests": contests,
}, indent=2))
(OUT / "app-measures.json").write_text(json.dumps({
    "county": "thurston",
    "script": "pipeline/build_thurston_lite_data.py",
    "derived_from": [rel(COUNTY / "interim/pdf-text/sample-ballot.txt")],
    "coverage": "full_county",
    "measures": [
        measure("S.E. Thurston Fire Authority", "Proposition No. 1", "Bonds to Improve Fire Stations and Acquire Apparatus", dist_scope("FIRE_AUTH", "S.E. Thurston Fire Authority"), 66, "Authorizes bonds to renovate and improve Yelm, Lake Lawrence, Rainier, and McIntosh Ridge fire stations and acquire firefighting and emergency response apparatus.", "Authorizes up to $21,010,000 in general obligation bonds maturing within 25 years, repaid through annual excess property taxes."),
        measure("Thurston County Fire Protection District No. 1", "Proposition No. 1", "Property Tax for Fire Maintenance and Operations", dist_scope("FIRDST", "FD01"), 68, "Authorizes a four-year maintenance and operations levy to maintain fire services and emergency medical services in the Rochester-Grand Mound area.", "Authorizes levy amounts from $826,166 in 2027 to $956,500 in 2030, at an approximate rate of $0.38 per $1,000 of assessed value."),
        measure("Thurston County Fire Protection District No. 11", "Proposition No. 1", "Property Tax for Fire Maintenance and Operations", dist_scope("FIRDST", "FD11"), 70, "Authorizes a four-year maintenance and operations levy to maintain fire services and emergency medical services in the Littlerock-Maytown area.", "Authorizes levy amounts from $807,020 in 2027 to $934,226 in 2030, at an approximate rate of $0.38 per $1,000 of assessed value."),
    ],
}, indent=2))
print(f"thurston contests: {len(contests)} measures: 3")
