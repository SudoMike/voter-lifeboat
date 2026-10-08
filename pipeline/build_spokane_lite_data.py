"""Build app-facing Spokane County lite data from extracted official PDFs."""

import json
import re

import election
import votewa
from election import rel

# Usage: python3 pipeline/build_spokane_lite_data.py [--election <id>]
ELECTION = election.Election(election.from_argv())
COUNTY = ELECTION.county("spokane")
OUT = COUNTY / "interim"


# --- From the November 3, 2026 general on ----------------------------------
# Contests come from the county's VoteWA candidate-list export
# (counties/spokane/raw/votewa/candidate-list.csv.{url,meta.json}, parsed by
# pipeline/votewa.py). general_override keeps this county's contest names
# (so slugs match the primary's and its dossiers carry forward) and the
# District Adapter layers in app/src/lib/geo.js COUNTY_LAYERS["spokane"].
# GENERAL_MEASURES holds the county's curated measures per election, as
# {"sources": [raw pointer paths or official URLs], "measures": [app-measures
# rows]}; None means not curated yet. Everything below this block is the primary's
# sample-ballot transcription, frozen byte-identical.
PRIMARY = "2026-08-04-primary"

GENERAL_CFG = {
    "name": "Spokane County",
    # Measure scopes on layers COUNTY_LAYERS["spokane"] (app/src/lib/geo.js)
    # does not have yet (#21). Each value below is what a live point query of
    # the proposed layer returns; until the layer is added the measures are
    # hidden and the package is partial_county.
    #   SCHDST: gismo.spokanecounty.org .../OpenData/Boundary/MapServer/6, attr DISTRCTNAME
    #   FIRDST: gismo.spokanecounty.org .../OpenData/Boundary/MapServer/1, attr NAME
    #           (NAME, not CODE/SERVICE/DISTRICTID: towns that contract for
    #           fire service, e.g. Rockford and Spangle, carry their own NAME
    #           with the district's CODE, and the City of Cheney polygon
    #           carries DISTRICTID 32103 like Fire District 3)
    "unresolvable_layers": ["SCHDST", "FIRDST"],
}

# The general's local measures, transcribed 2026-10-08 from Spokane County's
# online voters' guide on VoteWA (voter.votewa.gov/genericvoterguide.aspx?e=899&c=32;
# spokanecounty.gov answered HTTP 403 to scripted requests, so the printed
# local pamphlet PDF could not be fetched). Each row's ballot title is in
# counties/spokane/interim/voter-guide-text/measure-<id>.txt. Scope values
# were checked by a live point query of the layer at the address in the
# comment (Census-geocoded).
GUIDE = "data/washington-state/elections/2026-11-03-general/counties/spokane/raw/votewa/voter-guide"


def general_measure(jurisdiction, proposition, title, scope, what_it_does, cost_line):
    layer, value = scope
    return {
        "slug": f"spokane-{votewa.slugify(f'{jurisdiction}-{proposition}')}",
        "owner": "spokane",
        "jurisdiction": jurisdiction,
        "proposition": proposition,
        "title": title,
        "scope": votewa.scope_json("spokane", (layer, value)),
        "pamphlet_pages": [],
        "what_it_does": what_it_does,
        "cost_line": cost_line,
        "pro_summary": None,
        "con_summary": None,
        "lean_mappings": {},
    }


GENERAL_MEASURES = {"2026-11-03-general": {
    "sources": [f"{GUIDE}/voterguide.json.url"] + [f"{GUIDE}/measure-{m}.json.url" for m in (
        7351, 7352, 7353, 7354, 7350, 7328, 7329, 7355, 7330, 7331, 7332, 7356, 7357, 7358,
        7359, 7360, 7361, 7362, 7363, 7364)],
    "measures": [
        # 7351; 22710 E Country Vista Dr, Liberty Lake: Census place Liberty Lake.
        general_measure("City of Liberty Lake", "Proposition No. 1",
                        "Impose a Sales and Use Tax of One-Tenth of One Percent for the Purpose of Funding Criminal Justice Services",
                        ("CITY", "Liberty Lake"),
                        "Imposes a 0.1% city sales and use tax (RCW 82.14.450) dedicated to public safety and criminal justice services in Liberty Lake.",
                        "0.1% sales and use tax (10 cents on a $100 purchase), projected at about $750,000 a year."),
        # 7352; 20 W Emma St, Rockford: Census place Rockford.
        general_measure("Town of Rockford", "Proposition No. 1", "Property Tax Levy for Fire Protection",
                        ("CITY", "Rockford"),
                        "Replaces an expiring one-year excess property tax levy that pays for the town's fire protection services in 2027.",
                        "About $0.51 per $1,000 of assessed value in 2027, raising $40,934.57."),
        # 7353; 100 N Main St, Spangle: Census place Spangle.
        general_measure("Town of Spangle", "Proposition No. 1", "Fire Protection Service Excess Levy",
                        ("CITY", "Spangle"),
                        "Authorizes a one-year excess property tax levy to pay for the town's fire protection services in 2027.",
                        "About $1.40 per $1,000 of assessed value in 2027, raising $49,000."),
        # 7354; same point.
        general_measure("Town of Spangle", "Proposition No. 2", "Police Protection Service Excess Levy",
                        ("CITY", "Spangle"),
                        "Authorizes a one-year excess property tax levy to pay for the town's police protection services in 2027.",
                        "About $1.19 per $1,000 of assessed value in 2027, raising $28,000."),
        # 7350; 19307 E Cataldo Ave, Spokane Valley: DISTRCTNAME 'Central Valley #356'.
        general_measure("Central Valley School District No. 356", "Proposition No. 1",
                        "Replacement of Expiring Educational Programs and Operations Levy",
                        ("SCHDST", "Central Valley #356"),
                        "Replaces an expiring educational programs and operations levy for expenses the state does not fund, including staff compensation, nurses, counselors, safety staff, music, athletics and advanced courses.",
                        "Estimated $2.50 per $1,000 of assessed value: $48,900,000 (2028), $50,550,000 (2029), $52,400,000 (2030)."),
        # 7328; 12414 S Andrus Rd, Cheney: DISTRCTNAME 'Cheney #360'.
        general_measure("Cheney School District No. 360", "Proposition No. 1",
                        "Replacement Educational Programs and Operation Levy",
                        ("SCHDST", "Cheney #360"),
                        "Replaces an expiring educational programs and operation levy for expenses the state does not fund, including school safety, athletics, art, music, special education and staffing above the state allocation.",
                        "Estimated $2.10 per $1,000 of assessed value: $18,450,000 (2028), $19,000,000 (2029), $19,550,000 (2030)."),
        # 7329; same point.
        general_measure("Cheney School District No. 360", "Proposition No. 2",
                        "Replacement Capital Levy for Technology, Security and Infrastructure Improvements",
                        ("SCHDST", "Cheney #360"),
                        "Replaces an expiring capital levy for instructional technology, security cameras and entry controls, and other safety infrastructure.",
                        "Estimated $0.10, $0.15 and $0.20 per $1,000 of assessed value: $880,000 (2028), $1,350,000 (2029), $1,900,000 (2030)."),
        # 7355; 3830 N Sullivan Rd, Spokane Valley: DISTRCTNAME 'East Valley #361'.
        general_measure("East Valley School District No. 361", "Proposition No. 1",
                        "Replacement Capital Levy for Safety, Security, Infrastructure, and Technology Improvements",
                        ("SCHDST", "East Valley #361"),
                        "Replaces an expiring capital levy for safety, security, parking and traffic improvements, plumbing, HVAC, roof and electrical replacement, and educational technology and cybersecurity.",
                        "Estimated $0.99 per $1,000 of assessed value: $6,793,300 (2027), $6,996,996 (2028)."),
        # 7330; 10110 W Charles Rd, Nine Mile Falls: DISTRCTNAME 'Nine Mile Falls #325'.
        general_measure("Nine Mile Falls School District No. 325-179", "Proposition No. 1",
                        "Replacement Educational Programs And Operations Levy",
                        ("SCHDST", "Nine Mile Falls #325"),
                        "Replaces an expiring educational programs and operations levy for expenses the state does not fund, including safety, music, arts, nurses, counselors, class size reduction, athletics, transportation and technology.",
                        "Estimated $2.10 per $1,000 of assessed value: $4,354,837 (2028), $4,428,827 (2029), $4,504,075 (2030)."),
        # 7331; same point.
        general_measure("Nine Mile Falls School District No. 325-179", "Proposition No. 2",
                        "Capital Levy for Safety, Security, and Infrastructure Improvements",
                        ("SCHDST", "Nine Mile Falls #325"),
                        "A new six-year capital levy to replace a failing roof and condemned portable classrooms at Lakeside High School and modernize security, fire systems, facilities and infrastructure district-wide.",
                        "Estimated $0.38 per $1,000 of assessed value each year 2027-2032, from $774,853 (2027) to $842,954 (2032)."),
        # 7332; 34515 N Newport Hwy, Chattaroy: DISTRCTNAME 'Riverside #416'.
        general_measure("Riverside School District No. 416-62", "Proposition No. 1",
                        "Replacement of Expiring Educational Programs and Operations Levy",
                        ("SCHDST", "Riverside #416"),
                        "Replaces an expiring educational programs and operations levy for programs, services and staff the state does not fund, including electives, vocational education, nurses, counselors, safety, performing arts and athletics.",
                        "Estimated $1.58 per $1,000 of assessed value: $3,996,811 (2028), $4,116,715 (2029), $4,240,217 (2030)."),
        # 7356; 808 W Spokane Falls Blvd, Spokane: DISTRCTNAME 'Spokane #81'.
        general_measure("Spokane School District No. 81", "Proposition No. 1",
                        "Replacement of Expiring Educational Programs and Operation Levy",
                        ("SCHDST", "Spokane #81"),
                        "Replaces Spokane Public Schools' expiring educational programs and operation levy for expenses the state does not fund, including class size, special education, nurses, counselors, safety staff, music and athletics.",
                        "Estimated $2.50 per $1,000 of assessed value: $107,000,000 (2028), $111,000,000 (2029), $115,000,000 (2030)."),
        # 7357; 2805 N Argonne Rd, Spokane Valley (Millwood): DISTRCTNAME 'West Valley #363'.
        general_measure("West Valley School District No. 363", "Proposition No. 1",
                        "Educational Programs and Operations Replacement Levy",
                        ("SCHDST", "West Valley #363"),
                        "Replaces an expiring educational programs and operations levy for expenses the state does not fund, including smaller classes, advanced courses, nurses, counselors, technology, safety, music, athletics and facility maintenance.",
                        "Estimated $2.50 per $1,000 of assessed value: $10,479,522 (2028), $10,793,908 (2029), $10,955,816 (2030)."),
        # 7358; same point.
        general_measure("West Valley School District No. 363", "Proposition No. 2",
                        "Safety, Security and Infrastructure Improvements Replacement Levy",
                        ("SCHDST", "West Valley #363"),
                        "Replaces an expiring capital levy for entrance security, door locks and cameras, HVAC replacement at Spokane Valley High and a library addition at Pasadena Park Elementary.",
                        "Estimated $1.00 per $1,000 of assessed value: $4,191,809 (2028), $4,317,563 (2029)."),
        # 7359; 102 E Main St, Fairfield: NAME 'Fire District 2'.
        general_measure("Spokane County Fire Protection District No. 2", "Proposition No. 1",
                        "Proposition Reauthorizing and Continuing Regular Emergency Medical Services Property Tax Levy",
                        ("FIRDST", "Fire District 2"),
                        "Renews the district's regular emergency medical services property tax levy for six years.",
                        "$0.50 per $1,000 of assessed value a year for six years, collected beginning in 2027."),
        # 7360; 12414 S Andrus Rd, Cheney (unincorporated): NAME 'Fire District 3'.
        general_measure("Spokane County Fire Protection District No. 3", "Proposition No. 1",
                        "Emergency Medical Services Property Tax Levy",
                        ("FIRDST", "Fire District 3"),
                        "Authorizes a regular emergency medical services property tax levy for six years.",
                        "Up to $0.50 per $1,000 of assessed value a year for six years, collected beginning in 2027."),
        # 7361; 3801 E Farwell Rd, Mead: NAME 'Fire District 9'.
        general_measure("Spokane County Fire Protection District No. 9", "Proposition No. 1",
                        "Property Tax Levy for Fire Protection and Emergency Services",
                        ("FIRDST", "Fire District 9"),
                        "Restores (lifts) the district's regular property tax levy to $1.50 per $1,000 and allows levy revenue to grow up to 6% a year for five years, the final amount becoming the base for later limits.",
                        "Levy rate restored to $1.50 per $1,000 of assessed value, with up to 6% annual revenue growth for the next five years."),
        # 7362; same point.
        general_measure("Spokane County Fire Protection District No. 9", "Proposition No. 2",
                        "Fire Station and Firefighter Safety Improvements General Obligation Bonds - $70,000,000",
                        ("FIRDST", "Fire District 9"),
                        "Authorizes $70,000,000 in general obligation bonds to renovate, modernize, construct and replace fire stations and build a training building, repaid by excess property taxes.",
                        "$70,000,000 in bonds maturing within 20 years, repaid by annual excess property taxes (no rate is stated in the ballot title)."),
        # 7363; interior point (-117.1703, 47.43431): NAME 'Fire District 11'.
        general_measure("Spokane County Fire Protection District No. 11", "Proposition No. 1",
                        "Emergency Medical Services Property Tax Levy",
                        ("FIRDST", "Fire District 11"),
                        "Authorizes a regular emergency medical services property tax levy for six years.",
                        "$0.35 per $1,000 of assessed value a year for six years, collected beginning in 2027."),
        # 7364; 300 N Main St, Latah: NAME 'Fire District 12'.
        general_measure("Spokane County Fire Protection District No. 12", "Proposition No. 1",
                        "Emergency Medical Services Regular Property Tax Levy",
                        ("FIRDST", "Fire District 12"),
                        "Authorizes a regular emergency medical services property tax levy for six years.",
                        "$0.50 per $1,000 of assessed value a year for six years, collected 2027 through 2032."),
    ],
}}


def general_override(r, unresolvable):
    dtype, district, race = r["District Type"].strip().upper(), r["District"].strip().upper(), r["Race"].strip()
    if dtype == "COMMISSIONER":
        # Spokane's five commissioners are elected by district in the
        # general too (VoteWA: 'COUNTY COMMISSIONER DISTRICT NO. N').
        n = votewa.district_number(district)
        return "County", f"Spokane County Commissioner District {n}", "Commissioner", ("COUNTY_COUNCIL", str(n))
    if dtype == "COUNTYWIDE" and race.upper().startswith("DISTRICT COURT JUDGE"):
        n = votewa.district_number(race)
        return "Judicial", "Spokane County District Court", f"Judge Position No. {n}", ("COUNTY", None)
    if dtype == "PUBLIC UTILITY":
        # 'PUBLIC UTILITY DISTRICT 1' is Public Utility District No. 1 of
        # Stevens County (#21): VoteWA's voters' guide gives the race district
        # id UTL330001 (33 = Stevens) with ballot counties 'Spokane, Stevens',
        # and both candidates live in Stevens County. Spokane County has no
        # PUD of its own (the DOR PUD2025 layer has no Spokane feature). In
        # the general the whole PUD votes for each commissioner district's
        # seat (RCW 54.12.010), so the Spokane electorate is the Stevens PUD
        # territory inside Spokane County. No official boundary layer for it
        # is configured; the closest public layer is Spokane County's Water
        # Districts (OpenData/Boundary/MapServer/10, NAME 'Stevens County
        # PUD'), which maps PUD water-service areas, not certified electoral
        # boundaries. The scope value is that NAME.
        n = votewa.district_number(race)
        unresolvable.add("PUDDST")
        return ("PublicUtility", f"Public Utility District No. 1 of Stevens County Commissioner District {n}",
                "PUD Commissioner", ("PUDDST", "Stevens County PUD"))
    return None


if ELECTION.id != PRIMARY:
    CURATED = GENERAL_MEASURES.get(ELECTION.id)
    votewa.write_county_package(
        "spokane", ELECTION.id, GENERAL_CFG, "pipeline/build_spokane_lite_data.py",
        override=general_override,
        measures=CURATED["measures"] if CURATED else None,
        measure_sources=CURATED["sources"] if CURATED else (),
    )
    raise SystemExit(0)


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
        rel(COUNTY / "interim/pdf-text/sample-ballot.txt"),
        rel(COUNTY / "interim/pdf-text/local-voters-pamphlet.txt"),
    ],
    "coverage": "partial_county",
    "contests": contests,
}, indent=2))
(OUT / "app-measures.json").write_text(json.dumps({
    "county": "spokane",
    "script": "pipeline/build_spokane_lite_data.py",
    "derived_from": [
        rel(COUNTY / "interim/pdf-text/sample-ballot.txt"),
        rel(COUNTY / "interim/pdf-text/local-voters-pamphlet.txt"),
    ],
    "coverage": "partial_county",
    "measures": measures,
}, indent=2))
print(f"spokane contests: {len(contests)} measures: {len(measures)}")
