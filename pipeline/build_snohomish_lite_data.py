"""Build app-facing Snohomish County lite data from extracted official PDFs."""

import json
import re

import election
import votewa
from election import rel

# Usage: python3 pipeline/build_snohomish_lite_data.py [--election <id>]
ELECTION = election.Election(election.from_argv())
COUNTY = ELECTION.county("snohomish")
TEXT = COUNTY / "interim/pdf-text/sample-ballot.txt"
OUT = COUNTY / "interim"


# --- From the November 3, 2026 general on ----------------------------------
# Contests come from the county's VoteWA candidate-list export
# (counties/snohomish/raw/votewa/candidate-list.csv.{url,meta.json}, parsed by
# pipeline/votewa.py). general_override keeps this county's contest names
# (so slugs match the primary's and its dossiers carry forward) and the
# District Adapter layers in app/src/lib/geo.js COUNTY_LAYERS["snohomish"].
# GENERAL_MEASURES holds the county's curated measures per election, as
# {"sources": [raw pointer paths or official URLs], "measures": [app-measures
# rows]}; None means not curated yet. Everything below this block is the primary's
# sample-ballot transcription, frozen byte-identical.
PRIMARY = "2026-08-04-primary"

# RFADST: South Snohomish County Fire & Rescue RFA. The county's
# Fire_Districts layer (geo.js FIRDST) has no RFA polygon, so geo.js
# COUNTY_LAYERS["snohomish"] reads RFADST from the WA DOR FIR2025 layer
# (WADOR_PropertyTax/MapServer/7, DISTATTRIB, filtered to 'SCRFA'; 'SCRFA' at
# 19100 44th Ave W, Lynnwood, live 2026-10-08, #21). DISTCRT (District Court
# electoral districts) reads the Auditor's Court_Districts layer, whose
# District values are '<Name> District Court' (#27); general_override scopes
# the seats to those values.
GENERAL_CFG = {"name": "Snohomish County", "unresolvable_layers": []}

_GEN = "data/washington-state/elections/2026-11-03-general/counties/snohomish"
_LVP = f"{_GEN}/raw/snohomish/local-voters-pamphlet.pdf.url"
_BALLOT = f"{_GEN}/raw/snohomish/sample-ballot.pdf.url"
_COUNTY = {"kind": "COUNTY", "county": "snohomish"}
_NO_CON = "No statement against was filed; the pamphlet says no one in the jurisdiction contacted the Auditor's office to write one."


def gen_measure(jurisdiction, proposition, title, scope, pages, ballot_title, cost_line, pro, con):
    """One general-election app-measures row. `title` and `ballot_title` are
    verbatim from the sample ballot (raw/snohomish/sample-ballot.pdf.url);
    `pages` are local-voters-pamphlet PDF pages (ballot title, explanatory
    statement, statements for and against). Display fields are overlaid by
    scoring/measures.json at assembly."""
    return {
        "slug": "snohomish-" + votewa.slugify(f"{jurisdiction}-{proposition}"),
        "owner": "snohomish",
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


def _charter(n, title, pages, ballot_title, pro, con):
    return gen_measure("Snohomish County", f"Proposition No. {n}", title, _COUNTY, pages, ballot_title,
                       "No tax or rate in the ballot title; amends the county charter.", pro, con)


def _everett(n, title, page, ballot_title, pro):
    # Scope: Census place. 2930 Wetmore Ave, Everett (Census-geocoded
    # -122.20731, 47.97883) -> Incorporated Places 'Everett city' (2026-10-08).
    return gen_measure("City of Everett", f"Proposition No. {n}", title,
                       {"kind": "DISTRICT", "county": "snohomish", "layer": "CITY", "value": "Everett"}, [page],
                       ballot_title, "No tax or rate in the ballot title; amends the city charter.", pro, _NO_CON)


GENERAL_MEASURES = {"2026-11-03-general": {
    "sources": [_BALLOT, _LVP],
    "measures": [
        _charter(1, "Adoption of a Foundational Government Services Policy", [64, 65],
                 "This proposition would require the county legislature and executive branch to prioritize and protect funding for the offices of county Assessor, Auditor, Clerk, Executive, Prosecuting Attorney, Sheriff, Treasurer, and the District and Superior Court Judges. This proposition would add a new section to Article 6 of the County Charter.",
                 "Brian Sullivan: fund essential county services before expanding discretionary programs; it does not raise taxes or set spending levels.",
                 "Christine Eck and Janice Green: the named offices are already required by law; 'foundational' is undefined, inviting litigation and weakening the Council's budget authority."),
        _charter(2, "Prioritize Funding of Budget Stabilization Funds", [66, 67],
                 "This proposition would require the county legislature and executive branch to prioritize the funding of the county budget stabilization funds. The purpose of these funds is to help mitigate the impacts of catastrophic economic downturns and revenue shortfalls and provide resources for emergencies and catastrophic events. This proposition would add a new section to Article 6 of the County Charter.",
                 "Brian Sullivan: builds emergency savings with a catastrophic fund, a replenishment plan and a supermajority to spend, without a new tax.",
                 "Hans Dunshee and Janice R. Greene: unnecessary and rigid; diverts money from services, too small for a real disaster, and lets a Council minority block spending."),
        _charter(3, "Converting All Elected County Offices to Non-partisan Offices", [68, 69],
                 "This proposition would require that all candidates for a Snohomish County elected office appear on the ballot without a political party designation and that all elected county offices be non-partisan offices. This proposition would amend Section 4.15 and Section 4.80 of the County Charter.",
                 "Todd Welch, Mark James and Shawn O'Donnell: county services are not partisan; extends the nonpartisan approach of other county offices and every city, widening the candidate pool.",
                 "Anna Maria Jackson Laurence, Janice R. Greene and James Kenny: removing party labels hides information voters use; keep the disclosure voters chose in I-872."),
        _charter(4, "Increasing Public Access to County Financial Transparency", [70, 71],
                 "This proposition would add a new section to Article 6 of the Snohomish County Charter. This proposition requires Snohomish County to make available, where reasonably practicable through existing systems or future modernization efforts, all financial information legally available within the county.",
                 "Danny Perkins and Janelle M. Cass: searchable, free online access to county budget, contract, grant and audit data, built into future systems.",
                 "Doris Fulton and Janice R. Greene: 'reasonably practicable' has no force; a portal is outside the current system overhaul and should come by funded ordinance instead."),
        _charter(5, "Requiring a 4/5 Supermajority Council Vote to Increase Taxes", [72, 73],
                 "This proposition would require a 4/5 supermajority council vote to assess, levy, or increase any councilmanic tax. This proposition would amend Section 2.20 of the County Charter.",
                 "Todd Welch, Dan Perkins and Janelle Cass: requires broad Council agreement before taxes rise without a public vote, protecting fixed-income and struggling households.",
                 "Paula Rhyne, John Lovick and Mike Sells: lets two of five councilmembers block routine levies for law enforcement, courts, roads and veterans services; minority rule."),
        # Scope: Census place, Snohomish-side Bothell. 22833 Bothell Everett
        # Hwy, Bothell (Census-geocoded -122.21783, 47.79007) -> 'Bothell
        # city', Snohomish County (2026-10-08). King-side Bothell votes on the
        # same measure from King's package.
        gen_measure("City of Bothell", "Proposition No. 1", "Annexation Into Shoreline Fire Department Regional Fire Authority",
                    {"kind": "DISTRICT", "county": "snohomish", "layer": "CITY", "value": "Bothell"}, [80],
                    "The Bothell City Council adopted Resolution No. 1784, approving annexation into the Shoreline Fire Department Regional Fire Authority and related plan amendment. To maintain current fire and emergency medical service levels and provide long-term financial and operational sustainability for such services within Bothell, should Bothell be annexed into and become a part of the Shoreline Fire Department Regional Fire Authority, effective March 1, 2027, pursuant to the plan amendment, as provided in Resolution No. 1784?",
                    "No tax or rate in the ballot title; the RFA's levy and fire benefit charge would apply to Bothell property from 2028.",
                    "Wesley Wang, Brandon Keith and Mason Thompson: regional fire service shares resources and future facility costs; Bothell keeps three of nine RFA board seats; endorsed by IAFF Local 2099.",
                    _NO_CON),
        _everett(261, "Amendment to Everett City Charter Sections 2.2 and 4.10", 81,
                 "The amendment to Section 2.2 would require candidates for Mayor and City Council to have registered to vote in the City of Everett and resided in the City (and district if applicable) for at least one year before the deadline for filing for office; and would prohibit elected officials from holding other elected offices simultaneously. Finally, Section 4.10 would be amended to only require elected officials to take an official oath of office.",
                 "Todd Welch, Randy Bolerjack and Jonathan Peebles: one-year residency and one elected office at a time keep representatives rooted in and focused on Everett."),
        _everett(262, "Amendment to Everett City Charter Section 3.2", 82,
                 "The amendment to Section 3.2 would require the City to have at least two council meetings per month and at least 36 meetings per year; require the City to publish a schedule of those meetings every year in January and revise the procedures for determining who will preside over meetings when the Council President is absent.",
                 "Alan Rubio, Alice Hedges and Marcus Nunez: replaces the decades-old 48-meeting minimum with a flexible 36 that avoids meetings held only to meet a count."),
        _everett(263, "Amendment to Everett City Charter Section 8.3", 83,
                 "The amendment to Section 8.3 would revise the City's Civil Service rules so that the Civil Service Commission's responsibilities are consistent with the requirements of state law.",
                 "Randy Bolerjack and Brent Terry: replaces years-old eligibility lists with hiring for specific openings, keeping civil service for police and fire hiring."),
        _everett(264, "Amendment to Four Sections of the Everett City Charter", 84,
                 "The amendment to Sections 11.1, 11.2, 11.3 and 11.5 would require an initiative or referendum petition be signed by qualified electors in a number equal to ten percent of the total number of votes cast at the last preceding Mayoral election; would allow for 10 days to correct faulty signatures; would streamline the initiative process; and would require the City to prepare a Fiscal Analysis of the measure that would be made available to voters.",
                 "Mason Rutledge and Brent Terry: one uniform signature standard, clearer petition procedures and a fiscal impact statement for voters."),
        _everett(265, "Amendment to Eight Sections of the Everett City Charter", 85,
                 "The Amendments to Sections 3.4, 3.5, 4.13, 11.6, 13.9, 15.5, 16.2, and 16.3 would modernize how the City provides the public notice by allowing the City to publish those notices, appointments, ordinances and proposed ordinances, proposed initiatives and referenda, bid advertisements, and franchise on City's website instead of requiring this information to be published in a newspaper, while also having this information available in the office of the City Clerk for examination by the public.",
                 "Alice Hedges, Mason Rutledge and Todd Welch: online notices are easier to find around the clock and cut print costs."),
        # Scope: geo.js SCHDST. 806 W Main St, Monroe (Census-geocoded
        # -121.98081, 47.85255) -> District 'Monroe School District 103'.
        gen_measure("Monroe School District No. 103", "Proposition No. 1", "Capital Projects Levy for Safety and Facility Improvements",
                    {"kind": "DISTRICT", "county": "snohomish", "layer": "SCHDST", "value": "Monroe School District 103"}, [87],
                    "The Board of Directors of Monroe School District No. 103 adopted Resolution No. 3-2026 authorizing a levy proposition for facility improvements. This proposition would authorize the District to levy the following excess taxes to fund major maintenance projects, safety and security improvements, and construction projects at select schools. Collection Year 2027 2028 2029 2030 Approximate Levy Rate/$1000 Assessed Value $0.95 $0.90 $0.86 $0.82 Levy Amount $12,282,731 $12,282,731 $12,282,731 $12,282,731",
                    "Excess levy of $12,282,731 a year for 2027-2030, an estimated $0.95 to $0.82 per $1,000 of assessed value.",
                    "Kyle Fisher and Molly Barnes: a smaller four-year levy (about $49 million, down from a $152 million bond that failed in February) for secure entrances, fire and security systems, roofs and HVAC.",
                    _NO_CON),
        # Scope: geo.js SCHDST. 11930 Cyrus Way, Mukilteo (Census-geocoded
        # -122.28867, 47.88946) -> District 'Mukilteo School District 6'.
        gen_measure("Mukilteo School District No. 6", "Proposition No. 1", "General Obligation Bonds - $400,000,000",
                    {"kind": "DISTRICT", "county": "snohomish", "layer": "SCHDST", "value": "Mukilteo School District 6"}, [88, 89],
                    "The Board of Directors of Mukilteo School District No. 6 adopted Resolution #12/2025-26 concerning a proposition for bonds. This proposition would authorize the District to add to and replace portions of Mukilteo, Serene Lake and Olivia Park Elementaries and Explorer Middle School; expand the Kamiak High School gymnasium; replace and improve track, field and athletic facilities; update technology systems; make safety and security upgrades; and upgrade building components, by issuing $400,000,000 of general obligation bonds maturing within 21 years; and to levy excess property taxes annually to repay the bonds, as described in Resolution #12/2025-26.",
                    "$400,000,000 in bonds over up to 21 years; the district estimates an average excess levy of $0.57 per $1,000 of assessed value.",
                    "Judith M. Schwab, Nhi Pham and Angela Gottula: replaces failing pre-1970s infrastructure before emergencies and unlocks about $30 million in state matching funds.",
                    "Howard Damoff: the same bond failed in February 2026; enrollment is down, debt and interest are high; use interest-free capital levies instead."),
        # Scope: geo.js SCHDST. 319 Main St, Sultan (Census-geocoded
        # -121.81764, 47.86235) -> District 'Sultan School District 311'.
        gen_measure("Sultan School District No. 311", "Proposition No. 1", "Bonds To Modernize Community Schools, Construct New High School and Improve Safety",
                    {"kind": "DISTRICT", "county": "snohomish", "layer": "SCHDST", "value": "Sultan School District 311"}, [90],
                    "The Board of Directors of Sultan School District No. 311 adopted Resolution No. 25-13, concerning bonds to relieve student overcrowding and provide safe, modern schools. This proposition would authorize the District to: modernize Gold Bar Elementary (pre-K; grades K-2), Sultan Middle (grades 3-5) and Sultan High (grades 6-8) sites; construct a new high school (grades 9-12, expanded career/technical education); repurpose Sultan Elementary (Parent Partnership, educational supports, turf field for student/community use); issue $160,000,000 of general obligation bonds maturing within 21 years; and levy annual excess property taxes to repay the bonds, all as provided in Resolution No. 25-13.",
                    "$160,000,000 in bonds over up to 21 years, repaid by excess property taxes; the pamphlet gives no rate.",
                    "No statement for was filed; the pamphlet says no one contacted the Auditor's office to write one.",
                    _NO_CON),
        # Scope: geo.js FIRDST. Interior point (-122.25141, 47.78530),
        # unincorporated Snohomish County near Bothell -> District 'Fire
        # District 10' (the layer's centroid falls outside the polygon).
        gen_measure("Fire Protection District No. 10", "Proposition No. 1", "Annexation Into Shoreline Fire Department Regional Fire Authority",
                    {"kind": "DISTRICT", "county": "snohomish", "layer": "FIRDST", "value": "Fire District 10"}, [91],
                    "The Board of Commissioners of Snohomish County Fire Protection District No. 10 has approved Resolution No. 2026-02 concerning an annexation into Shoreline Fire Department Regional Fire Authority. This proposition would authorize Snohomish County Fire Protection District No. 10 to annex into Shoreline Fire Department Regional Fire Authority to provide fire and emergency medical services effective March 1, 2027, as described in the Shoreline Fire Department Regional Fire Authority plan amendment attached to Snohomish County Fire Protection District No. 10 Resolution No. 2026-02.",
                    "The RFA levy (estimated $0.45 per $1,000, from 2028) replaces the district's levy (about $0.90), plus a fire benefit charge set in 2028.",
                    "Morris Parrish, Jack Barnes and Craig Bishop: the Bothell-area fire service has not grown with population; a regional authority shares resources and training; endorsed by the Bothell firefighters' union.",
                    _NO_CON),
        # Scope: geo.js RFADST (DOR FIR2025, see GENERAL_CFG). 19100 44th Ave W,
        # Lynnwood (Census-geocoded -122.29251, 47.82559) -> DOR FIR2025
        # DISTATTRIB 'SCRFA'; county RFA_Commissioner 'SCRFA Commissioner Dist 1'.
        gen_measure("South Snohomish County Fire & Rescue Regional Fire Authority", "Proposition No. 1",
                    "Fire and Emergency Medical Services Construction General Obligation Bonds - $420,000,000",
                    {"kind": "DISTRICT", "county": "snohomish", "layer": "RFADST", "value": "SCRFA"}, [92, 93],
                    "The Board of Fire Commissioners of the South Snohomish County Fire & Rescue Regional Fire Authority adopted Resolution No. 06092026- 13 concerning financing for its capital facilities plan. This proposition would authorize South County Fire to replace, renovate and/or make seismic upgrades to aging fire stations, build additional fire stations, and construct, improve, acquire and/or equip facilities to meet the community's emergency response needs, enhance reliability, reduce coverage gaps, and support operations; issue up to $420,000,000 of general obligation bonds maturing within a maximum of 25 years; and levy annual excess property taxes to repay the bonds, as provided in Resolution No. 06092026-13.",
                    "$420,000,000 in bonds over up to 25 years; levies expected to average about $0.194 per $1,000 of assessed value.",
                    "Shannon Sessions, Alex Johnson and Steve Barnes: two-thirds of stations need major work and nearly half could fail in a major earthquake; calls are up more than 30% in a decade.",
                    "Melinda Goforth, Mary Jane Goss and Jim Landers: over half a billion dollars with interest is too much in an affordability crisis; fund the six high-risk station replacements ($136.7 million) first."),
        # Scope: geo.js HOSPDST. 806 W Main St, Monroe and 14701 179th Ave SE,
        # Monroe (Census-geocoded) -> District 'Hospital District 1'.
        gen_measure("Public Hospital District No. 1", "Proposition No. 1", "Bonds for New Replacement Hospital",
                    {"kind": "DISTRICT", "county": "snohomish", "layer": "HOSPDST", "value": "Hospital District 1"}, [94],
                    "The Commission of Public Hospital District No. 1, Snohomish County, Washington (EvergreenHealth Monroe), adopted Resolution No. 2026-04 concerning a proposition for a replacement hospital and related healthcare facilities. If approved, this proposition would authorize the District to construct and equip a new replacement hospital and carry out other capital improvements deemed necessary or advisable by the Commission to address the healthcare needs of the community; issue no more than $382,000,000.00 of general obligation bonds maturing within 30 years; and levy annual excess property taxes to repay the bonds, all as provided in Resolution 2026-04.",
                    "Up to $382,000,000 in bonds over up to 30 years; estimated average $0.437 per $1,000, about $40.75 a month for a $745,000 home.",
                    "Dianne Forth, Michael Eickerman and Ernie Walters: the hospital is aging and overcrowded; a replacement adds capacity and keeps care local, with audits and local oversight.",
                    _NO_CON),
    ],
}}


def general_override(r, unresolvable):
    dtype, district, race = r["District Type"].strip().upper(), r["District"].strip().upper(), r["Race"].strip()
    if dtype == "PUBLIC UTILITY" and district == "PUBLIC UTILITY DISTRICT NO. 1":
        # Nominated by commissioner district in the primary, elected by the
        # whole PUD in the general (RCW 54.12.010(3);
        # raw/snohomish/rcw-54-12-010.html.url). Snohomish PUD No. 1 is
        # countywide (geo.js PUDDST: every Snohomish point is in District
        # 1, 2 or 3), so the general electorate is the county.
        n = votewa.district_number(race)
        return ("PublicUtility", "Public Utility District No. 1", f"Commissioner District {n}", ("COUNTY", None))
    if dtype == "JUDICIAL" and district.endswith(" DISTRICT COURT"):
        # Snohomish County District Court elects judges by electoral
        # district (Cascade, Everett, Evergreen, South). geo.js DISTCRT reads
        # the Auditor's Court_Districts layer (#27), whose District values are
        # 'Cascade District Court' ... 'South District Court'; the scope value
        # is that string.
        name = district[: -len(" DISTRICT COURT")].title()
        n = votewa.district_number(race)
        return ("Judicial", f"Snohomish County District Court, {name} District", f"Judge Position No. {n}",
                ("DISTCRT", f"{name} District Court"))
    return None


if ELECTION.id != PRIMARY:
    CURATED = GENERAL_MEASURES.get(ELECTION.id)
    votewa.write_county_package(
        "snohomish", ELECTION.id, GENERAL_CFG, "pipeline/build_snohomish_lite_data.py",
        override=general_override,
        measures=CURATED["measures"] if CURATED else None,
        measure_sources=CURATED["sources"] if CURATED else (),
    )
    raise SystemExit(0)


def slugify(s: str) -> str:
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", s.lower())).strip("-")


def county_slug(s: str) -> str:
    return f"snohomish-{slugify(s)}"


def dist_scope(layer, value):
    return {"kind": "DISTRICT", "county": "snohomish", "layer": layer, "value": str(value)}


def candidate_rows(block):
    rows = []
    # Names may carry parenthesized nicknames — "Robert (Chili) Hicks" — so a
    # name only ends at the NEXT party-preference paren, not at any paren.
    for party, name in re.findall(r"\((Prefers [^)]+ Party|States No Party Preference)\)\s+(.+?)(?=\s+\((?:Prefers |States No)|\s+Write-In|\Z)", block):
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
    "derived_from": [rel(COUNTY / "interim/pdf-text/sample-ballot.txt")],
    "coverage": "full_county",
    "contests": contests,
}, indent=2))
(OUT / "app-measures.json").write_text(json.dumps({
    "county": "snohomish",
    "script": "pipeline/build_snohomish_lite_data.py",
    "derived_from": [rel(COUNTY / "interim/pdf-text/sample-ballot.txt")],
    "coverage": "full_county",
    "measures": measures,
}, indent=2))
print(f"snohomish contests: {len(contests)} measures: {len(measures)}")
