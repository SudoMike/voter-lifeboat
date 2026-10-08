"""Build app-facing Pierce County lite data from official sample ballot facts.

Pierce County's DocumentCenter PDFs are Cloudflare-challenged from this data
environment, so this package is keyed to the official sample ballot URL
pointer and cross-validated against the official VoteWA PRIMARY 2026
candidate list export (data/washington-state/elections/<id>/statewide/raw). Scopes cover
CONGDST, LEGDST, CITY, COUNTY_COUNCIL, FIRDST, DISTCRT, and countywide via
the Pierce district adapter in app/src/lib/geo.js (the general adds KCDISTCRT,
PTBA and SCHDST). PCO races are excluded
(statewide convention).
"""

import json
import re

import election
import votewa
from election import rel

# Usage: python3 pipeline/build_pierce_lite_data.py [--election <id>]
ELECTION = election.Election(election.from_argv())
COUNTY = ELECTION.county("pierce")
OUT = COUNTY / "interim"


# --- From the November 3, 2026 general on ----------------------------------
# Contests come from the county's VoteWA candidate-list export
# (counties/pierce/raw/votewa/candidate-list.csv.{url,meta.json}, parsed by
# pipeline/votewa.py). general_override keeps this county's contest names
# (so slugs match the primary's and its dossiers carry forward) and the
# District Adapter layers in app/src/lib/geo.js COUNTY_LAYERS["pierce"].
# GENERAL_MEASURES holds the county's curated measures per election, as
# {"sources": [raw pointer paths or official URLs], "measures": [app-measures
# rows]}; None means not curated yet. Everything below this block is the primary's
# sample-ballot transcription, frozen byte-identical.
PRIMARY = "2026-08-04-primary"

GENERAL_CFG = {
    "name": "Pierce County",
    # Measure scopes resolve through geo.js COUNTY_LAYERS.pierce (#21): SCHDST
    # and PTBA read the Election_Precincts layer's SCHOOL (school district
    # name) and PIERCE_TRANSIT ('YES'/'NO'), the layer DISTCRT reads
    # PC_DISTRICT from (live point queries 2026-10-08, values in the comments
    # below).
    "unresolvable_layers": (),
}

_GENERAL_RAW = "data/washington-state/elections/2026-11-03-general/counties/pierce/raw"


def _general_measure(slug, votewa_id, jurisdiction, proposition, title, scope, what_it_does, cost_line):
    # Ballot titles, explanatory statements and pro/con statements are kept
    # verbatim in raw/measures/<slug>/votewa-measure-<id>.json (VoteWA online
    # voter guide, the county's own pamphlet text); display text and lean
    # mappings come from scoring/measures.json at assembly.
    return {
        "slug": slug,
        "owner": "pierce",
        "jurisdiction": jurisdiction,
        "proposition": proposition,
        "title": title,
        "votewa_measure_id": votewa_id,
        "scope": scope,
        "pamphlet_pages": [],
        "what_it_does": what_it_does,
        "cost_line": cost_line,
        "pro_summary": None,
        "con_summary": None,
        "lean_mappings": {},
    }


def _charter(n, votewa_id, title, what_it_does):
    return _general_measure(
        f"pierce-pierce-county-charter-amendment-no-{n}", votewa_id, "Pierce County", f"Charter Amendment No. {n}",
        title, {"kind": "COUNTY", "county": "pierce"}, what_it_does,
        "No tax or levy on the ballot; any cost is in county operations.",
    )


def _district(layer, value):
    return {"kind": "DISTRICT", "county": "pierce", "layer": layer, "value": value}


GENERAL_MEASURES = {"2026-11-03-general": {
    "sources": [
        f"{_GENERAL_RAW}/votewa/voter-guide.json.url",
        f"{_GENERAL_RAW}/measures/",
    ],
    "measures": [
        # Charter amendments 52-58 (2026 Charter Review Commission): county-wide.
        _charter(52, "7313", "County Council Meetings",
                 "Requires the County Council to meet at least 45 times a year (instead of at least once in each of 50 weeks) and to offer remote attendance and public comment at meetings where public comment is required."),
        _charter(53, "7314", "Appointed Sheriff and Termination of Elected Sheriff",
                 "Makes Sheriff an appointed office: the Executive appoints and a Council majority confirms; the current elected Sheriff's term ends January 1, 2027."),
        _charter(54, "7315", "Public Safety Ombuds",
                 "Creates an executive department of Public Safety Ombuds, appointed by the Council from a panel's list, to oversee the Sheriff's Office, plus a Community Advisory Committee."),
        _charter(55, "7316", "Initiative Procedures",
                 "Gives county initiative sponsors 180 days instead of 120 to collect signatures."),
        _charter(56, "7317", "Four Year Budget Outlook",
                 "Requires the Chief Financial Officer to prepare a four-year budget outlook showing projected Current Expense Fund spending will not exceed projected available funds."),
        _charter(57, "7318", "Nondiscrimination",
                 "Rewrites the Charter's nondiscrimination clause to list sex, race, color, national origin or ancestry, creed, disability, sexual orientation, gender identity or expression, age, genetic testing results, family caregiver status, pregnancy, childbirth or lactation, and military or veteran status."),
        _charter(58, "7319", "Juvenile Detention",
                 "Creates a Juvenile Detention Advocate Office to take complaints and monitor conditions, and requires an independent audit or accreditation review of juvenile detention at least every five years."),
        # Census place (geo.js CITY): 1000 Laurel St, Milton -> 'Milton city'
        # (Pierce side; Milton also lies in King, whose package has the same
        # measure as city-of-milton-proposition-no-1).
        _general_measure("pierce-city-of-milton-proposition-no-1", "7310", "City of Milton", "Proposition No. 1",
                         "Additional Sales and Use Tax for Police and Public Safety", _district("CITY", "Milton"),
                         "Raises Milton's sales and use tax by 0.1% from 2027 for public safety purposes allowed by RCW 82.14.450, such as police staffing.",
                         "Sales and use tax up 0.1% (one cent on $10) from 2027; 15% of proceeds go to the county."),
        # 121 Washington St, South Prairie -> Census 'South Prairie town'.
        _general_measure("pierce-town-of-south-prairie-proposition-no-1", "7311", "Town of South Prairie", "Proposition No. 1",
                         "Public Safety and Town Operations and Services Levy", _district("CITY", "South Prairie"),
                         "Lifts South Prairie's regular property tax levy for police, fire, EMS, parks, roads and other town services.",
                         "About $1.33 per $1,000 more (to a maximum $2.90 per $1,000) for 2027, then up to 6% a year through 2032."),
        # Pierce Transit's benefit area: Election_Precincts PIERCE_TRANSIT
        # 'YES' at 930 Tacoma Ave S, Tacoma; 'NO' at 121 Washington St, South
        # Prairie (2026-10-08). geo.js PTBA reads PIERCE_TRANSIT.
        _general_measure("pierce-pierce-transit-proposition-no-1", "7308", "Pierce Transit", "Proposition No. 1",
                         "Maintaining and Expanding Local Transit Service Sales and Use Tax Increase", _district("PTBA", "YES"),
                         "Adds a 0.3% sales and use tax from April 1, 2027 to maintain and expand Pierce Transit bus service and fund fare-free rides for seniors and youth.",
                         "Sales and use tax up 0.3% (three cents on $10) within Pierce Transit's service area."),
        _general_measure("pierce-city-of-tacoma-initiative-no-1", "7309", "City of Tacoma", "Initiative No. 1",
                         "Safe Homes for All Initiative Measure No. 1", _district("CITY", "Tacoma"),
                         "Amends Tacoma's rental housing code: tenant unions and good-faith bargaining, landlord licensing with per-unit fees, City and private enforcement, penalties and business-license revocation.",
                         "No tax; landlords pay new per-unit rental licensing fees, and the City takes on new enforcement and program costs."),
        # Fire_Districts FIRE_DIS at the interior point (-122.36, 47.215):
        # 'FPD #014 RIVERSIDE' (2026-10-08).
        _general_measure("pierce-fire-protection-district-no-14-proposition-no-1", "7312", "Fire Protection District No. 14", "Proposition No. 1",
                         "Emergency Medical Services Property Tax Levy", _district("FIRDST", "FPD #014 RIVERSIDE"),
                         "Renews Riverside Fire & Rescue's EMS property tax levy for six years from 2027.",
                         "Up to $0.50 per $1,000 of assessed value (at most $50 a year per $100,000), the same rate as the expiring 2020 levy."),
        # Election_Precincts SCHOOL at 1402 Lake Tapps Pkwy SE, Auburn:
        # 'AUBURN SCHOOL DISTRICT NO. 408' (2026-10-08). The same measure is in
        # King's package (auburn-school-district-no-408-proposition-no-1).
        _general_measure("pierce-auburn-school-district-no-408-proposition-no-1", "7259", "Auburn School District No. 408", "Proposition No. 1",
                         "School Construction and Replacement Bonds", _district("SCHDST", "AUBURN SCHOOL DISTRICT NO. 408"),
                         "Authorizes up to $491 million in 20-year bonds to build a new middle school and replace Cascade Middle School and Alpac Elementary.",
                         "Up to $491,000,000 in bonds repaid by excess property taxes."),
        # Election_Precincts SCHOOL at the interior point (-122.55764,
        # 46.93652), precinct 02095: 'YELM COMMUNITY SCHOOLS' (2026-10-08).
        _general_measure("pierce-yelm-community-schools-proposition-no-1", "7370", "Yelm Community Schools", "Proposition No. 1",
                         "Educational Programs and Operations Maintenance Levy", _district("SCHDST", "YELM COMMUNITY SCHOOLS"),
                         "Two-year levy (2027-2028) to maintain Yelm Community Schools programs and operations not funded by the State.",
                         "Up to $11,194,449 in 2027 and $12,278,072 in 2028, an estimated $1.50 per $1,000 of assessed value."),
    ],
}}


def general_override(r, unresolvable):
    dtype, district, race = r["District Type"].strip().upper(), r["District"].strip().upper(), r["Race"].strip()
    if dtype == "COUNCIL":
        n = votewa.district_number(district)
        return "County", f"Pierce County Council District {n}", "County Councilmember", ("COUNTY_COUNCIL", str(n))
    if dtype == "JUDICIAL" and district == "DISTRICT COURT":
        # Pierce County District Court's electorate is the Election_Precincts
        # PC_DISTRICT='YES' area (as in the primary's Position 7).
        n = votewa.district_number(race)
        return "Judicial", f"Pierce County District Court No. {n}", f"Judge Position No. {n}", ("DISTCRT", "YES")
    if dtype == "DISTRICT COURT" and district == "SOUTHEAST ELECTORAL DISTRICT":
        # King County District Court, Southeast Electoral District: the same
        # races as King's package, on the ballot in the Pierce precincts whose
        # Election_Precincts KING_DISTRICT is 'YES' (Pierce-side Auburn:
        # 1402 Lake Tapps Pkwy SE returned KING_DISTRICT YES, PC_DISTRICT NO,
        # 2026-10-08). geo.js KCDISTCRT reads KING_DISTRICT.
        n = votewa.district_number(race)
        return ("Judicial", "King County District Court, Southeast Electoral District", f"Judge Position No. {n}",
                ("KCDISTCRT", "YES"))
    return None


if ELECTION.id != PRIMARY:
    CURATED = GENERAL_MEASURES.get(ELECTION.id)
    votewa.write_county_package(
        "pierce", ELECTION.id, GENERAL_CFG, "pipeline/build_pierce_lite_data.py",
        override=general_override,
        measures=CURATED["measures"] if CURATED else None,
        measure_sources=CURATED["sources"] if CURATED else (),
    )
    raise SystemExit(0)


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


def scoped_contest(category, district, office, candidates, scope):
    return {
        "slug": county_slug(f"{district}-{office}"),
        "owner": "pierce",
        "category": category,
        "office": office,
        "district": district,
        "scope": scope,
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
    scoped_contest("County", "Pierce County Council District 1", "County Councilmember", [
        candidate("Jerome O'Leary", "Prefers Republican Party"),
        candidate("Terrance Mayers", "Prefers Democratic Party"),
        candidate("Kenneth King", "Prefers Democratic Party"),
        candidate("Kelsey Barrans", "Prefers Democratic Party"),
    ], dist_scope("COUNTY_COUNCIL", 1)),
    scoped_contest("County", "Pierce County Council District 5", "County Councilmember", [
        candidate("Bryan Yambe", "Prefers Democratic Party"),
        candidate("Bettina Gese", "Prefers Republican Party"),
    ], dist_scope("COUNTY_COUNCIL", 5)),
    scoped_contest("County", "Pierce County Council District 7", "County Councilmember", [
        candidate("Chuck West", "Prefers Nonpartisan Party"),
        candidate("Brenda Lykins", "Prefers Democratic Party"),
        candidate("Mike Solan", "Prefers Republican Party"),
        candidate("Ann E. Jolie", "Prefers Republican Party"),
    ], dist_scope("COUNTY_COUNCIL", 7)),
    # The Election_Precincts PC_DISTRICT attribute is a YES/NO "inside the
    # district court electoral district" flag, not a district number.
    scoped_contest("Judicial", "Pierce County District Court No. 7", "Judge Position No. 7", [
        candidate("Eric J. Lawless"),
        candidate("Mike Sommerfeld"),
        candidate("Pam Nogueira"),
    ], dist_scope("DISTCRT", "YES")),
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
    {
        "slug": "pierce-fire-protection-district-no-10-proposition-no-1",
        "owner": "pierce",
        "jurisdiction": "Fire Protection District No. 10",
        "proposition": "Proposition No. 1",
        "title": "Bonds to Construct a New Fire Station",
        "scope": dist_scope("FIRDST", "FPD #010 FIFE"),
        "pamphlet_pages": [],
        "what_it_does": "Authorizes Fire Protection District No. 10 to acquire, construct, and equip a new fire station, issue up to $25 million in general obligation bonds maturing within 20 years, and levy annual excess property taxes to repay the bonds.",
        "cost_line": "Authorizes up to $25,000,000 in bonds repaid by annual excess property taxes.",
        "pro_summary": None,
        "con_summary": None,
        "lean_mappings": {"taxes": {"direction": 2, "basis": "YES authorizes bond debt and excess property taxes for a new fire station.", "citations": ["Pierce sample ballot"]}},
    },
]

OUT.mkdir(parents=True, exist_ok=True)
(OUT / "app-contests.json").write_text(json.dumps({
    "county": "pierce",
    "script": "pipeline/build_pierce_lite_data.py",
    "derived_from": [rel(COUNTY / "raw/pierce/sample-ballot.pdf.url")],
    "coverage": "full_county",
    "contests": contests,
}, indent=2))
(OUT / "app-measures.json").write_text(json.dumps({
    "county": "pierce",
    "script": "pipeline/build_pierce_lite_data.py",
    "derived_from": [rel(COUNTY / "raw/pierce/sample-ballot.pdf.url")],
    "coverage": "full_county",
    "measures": measures,
}, indent=2))
print(f"pierce contests: {len(contests)} measures: {len(measures)}")
