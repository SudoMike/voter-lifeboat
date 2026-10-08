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

GENERAL_CFG = {
    "name": "Clark County",
    # Every scope resolves through geo.js COUNTY_LAYERS["clark"] (#22).
    # SCHDST (Battle Ground School District Prop 11) reads Clark's own
    # ClarkView_Public/SchoolDistrict/MapServer/0, attribute SCHDST (values
    # 37 Vancouver ... 119 Battle Ground ... 122 Ridgefield): 119 at 109 SW
    # 1st St, Battle Ground (Census-geocoded -122.53766, 45.78008), live
    # 2026-10-08; DOR SCH2025 (layer 20) returns DISTATTRIB '119' there too.
    "unresolvable_layers": (),
}

# The general's local measures, transcribed 2026-10-08 from Clark County's
# sample ballot (raw/clark/sample-ballot.pdf.url: titles and ballot titles,
# verbatim) and its local voters' pamphlet (raw/clark/local-voters-pamphlet.pdf.url,
# PDF pages below). The pamphlet's local section (pages 41-99) uses fonts
# without a Unicode map, so its statements were read from the same
# statements in Clark's VoteWA online voters' guide
# (raw/votewa/voter-guide/measure-<id>.json.url; interim/voter-guide-text/).
_E = "data/washington-state/elections/2026-11-03-general/counties/clark/raw"
_COUNTY = ("COUNTY", None)
_CHARTER_COST = "No tax or rate in the ballot title; amends the Clark County Home Rule Charter."


def general_measure(jurisdiction, proposition, title, scope, pages, ballot_title, cost_line, pro, con):
    """One general-election app-measures row. `title` and `ballot_title` are
    verbatim from the sample ballot; `pages` are local-voters-pamphlet PDF
    pages (statement for and against, explanatory statement). Display fields
    are overlaid by scoring/measures.json at assembly."""
    return {
        "slug": "clark-" + votewa.slugify(f"{jurisdiction}-{proposition}"),
        "owner": "clark",
        "jurisdiction": jurisdiction,
        "proposition": proposition,
        "title": title,
        "scope": votewa.scope_json("clark", scope),
        "pamphlet_pages": [{"edition": "local-voters-pamphlet", "page": p} for p in pages],
        "what_it_does": ballot_title,
        "cost_line": cost_line,
        "pro_summary": pro,
        "con_summary": con,
        "lean_mappings": {},
    }


def _charter(n, title, pages, ballot_title, pro, con):
    return general_measure("Clark County", f"Proposed Charter Amendment No. {n}", title, _COUNTY, pages,
                           ballot_title, _CHARTER_COST, pro, con)


_NO_CON = "No statement against was filed: after recruitment attempts, no one in the jurisdiction volunteered to write one."

GENERAL_MEASURES = {"2026-11-03-general": {
    "sources": [f"{_E}/clark/sample-ballot.pdf.url", f"{_E}/clark/local-voters-pamphlet.pdf.url",
                f"{_E}/votewa/voter-guide/voterguide.json.url"]
               + [f"{_E}/votewa/voter-guide/measure-{m}.json.url"
                  for m in (7333, 7334, 7335, 7336, 7337, 7338, 7339, 7340, 7341, 7342, 7344, 7345)],
    "measures": [
        # 7333
        _charter(19, "Concerning a Limitation on Consecutive Terms for County Council Members", [64, 65],
                 "The Clark County Charter Review Commission adopted Resolution No. 26-20 proposing an amendment to the Clark County Home Rule Charter, concerning a limitation on consecutive terms for County Council members. If approved, this amendment would limit the number of consecutive terms a County Council member could sit to three terms, with eligibility restored after one full term out of office.",
                 "Brandon Erickson, Dorothy Gasque and Liz Shaw: open seats widen the field and bring fresh perspectives; twelve years is ample time to serve, and former members may run again after a term away.",
                 "Morgan Holmgren, Liz Cline and Chuck Green: voters already remove councilors who overstay; limits cost institutional knowledge, empower unelected staff and interest groups, and restrict voter choice."),
        # 7334
        _charter(20, "Concerning a Revised Budget Transparency Process", [66, 67],
                 "The Clark County Charter Review Commission adopted Resolution No. 26-10 proposing an amendment to the Clark County Home Rule Charter, concerning a revised budget transparency process. If approved, this amendment would establish a new timeline for the submission of budget information, presentation, and adoption of the Clark County budget earlier than those dates set in Chapter 36.40 RCW.",
                 "Peter Silliman, Liz Cline and Ann Donnelly: moves the first public budget presentation to early September and adoption to November, giving residents time to review a budget of almost $900 million.",
                 "John Latta, Julie Koepp and Janet Landesberg: the charter already lets the county set earlier deadlines; process details do not belong in the charter and would make the budget process harder to improve."),
        # 7335
        _charter(21, "Concerning Revised Council Powers Regarding Boards and Commissions", [68],
                 "The Clark County Charter Review Commission adopted Resolution No. 26-23 proposing an amendment to the Clark County Home Rule Charter, concerning revised Council powers regarding boards and commissions. If approved, this amendment would give the County Council the concurrent authority with the County Manager to nominate members to all boards and commissions, with the exception of the Ethics Review Commission.",
                 "Patrick Adigweme and Eric LaBrant: the Council can now nominate only to three bodies; letting councilors nominate volunteers to the rest could help keep seats filled.",
                 _NO_CON),
        # 7336
        _charter(22, "Concerning a Clarification of Nonpartisan Office Elections", [70, 71],
                 "The Clark County Charter Review Commission adopted Resolution No. 26-01 proposing an amendment to the Clark County Home Rule Charter, concerning a clarification of nonpartisan office elections. If approved, this amendment clarifies if two or less county candidates file for a race in the Primary, that race will bypass the Primary and proceed directly to the General Election. Nonpartisan elections for county offices shall be held in accordance with the procedures established in state law for nonpartisan elections, and shall occur in even numbered years.",
                 "Cathie Garber, Jennifer Wendel and Dorothy Gasque: a primary with one or two candidates narrows nothing; skipping it, as other nonpartisan races already do, saves printing and mailing costs.",
                 "Ann Donnelly, Peter Silliman and Liz Cline: the primary and its pamphlet inform voters for months; skipping it favors incumbents and embeds even-year elections in the charter."),
        # 7337
        _charter(23, "Concerning a Required Annual Report Publication by the County Manager", [72, 73],
                 "The Clark County Charter Review Commission adopted Resolution No. 26-24 proposing an amendment to the Clark County Home Rule Charter, concerning a required annual report publication by the County Manager. If approved, the amendment would require the County Manager to present to the Council in a public meeting and publish broadly an annual statement of the County's fiscal and government affairs, and any other report which the Council may deem necessary as well as annually prepare and present to the Council in a public meeting a budget and budget message setting forth the proposals for the forthcoming fiscal year.",
                 "Patrick Adigweme, Eric LaBrant and Ann Donnelly: makes the annual report mandatory and broadly published, so the public gets it regardless of who holds office.",
                 "Margaret Tweet: the 'publish broadly' mandate has no election-season limit and could fund mailers that favor incumbents or county ballot measures; post reports online instead."),
        # 7338
        _charter(24, "Concerning a Requirement for a Housing Impact Analysis", [74, 75],
                 "The Clark County Charter Review Commission adopted Resolution No. 26-07 proposing an amendment to the Clark County Home Rule Charter, concerning a requirement for a Housing Impact Analysis. If approved, this amendment would require prior to the adoption of any ordinance reasonably likely to have a direct and material impact upon residential housing capacity, density, permitting, subdivision requirements, parking requirements, applicable to residential development, or residential construction costs, the County shall publish a Housing Impact Analysis.",
                 "John Jay, David Stuebe and Justin Wood: councilors and the public should see the housing-cost effects of discretionary land-use rules before adoption; it dictates no outcome.",
                 "Chuck Green, Irene Finley and Morgan Holmgren: policy micromanagement in the charter; reports cost taxpayers and will not fix affordability driven by interest rates and state and federal rules."),
        # 7339
        _charter(25, "Concerning the Requirement of Supermajority Approval by Council for County Taxes", [76, 77],
                 "The Clark County Charter Review Commission adopted Resolution No. 26-08 proposing an amendment to the Clark County Home Rule Charter, concerning the requirement of supermajority approval by Council for County taxes. If approved, after January 1, 2027, this amendment would require any new councilmanic tax assessed, levied, or increased to have a two-third affirmative vote by the Council. Also, if approved, this amendment would not apply to fees, rates and charges, special assessments, or existing taxes levied prior to adoption of the amendment or any renewal or reauthorization of those taxes not seeking an increased tax rate.",
                 "John Jay, Paul Harris and Brian Lewallen: new council-imposed taxes should need broad agreement; it changes no current tax or service.",
                 "Janet Landesberg, Dorothy Gasque and Julie Koepp: on a five-member council two-thirds means four votes, letting two councilors block funding for law and justice, roads and parks."),
        # 7340
        _charter(26, "Concerning the Initiative, Mini-Initiative, and Referenda Process", [78, 79],
                 "The Clark County Charter Review Commission adopted Resolution No. 26-40 proposing an amendment to the Clark County Home Rule Charter, concerning the initiative, mini-initiative, and referenda process. If approved, this amendment would reduce the number of signatures necessary for initiatives and referendums from 10% to 8%; remove calculation requirements of required signatures based on the number of votes cast within unincorporated areas of the County at the date the initiative and referendum is initiated; allow for initiatives without sufficient signatures have possible opportunity to become a mini-initiative; and permit the Auditor's Office to limited use statistical sampling techniques for signature verification.",
                 "Cathie Garber, Liz Cline and Dorothy Gasque: no citizen petition has qualified since 2014; a lower threshold and signature sampling keep safeguards while making the process achievable.",
                 "Janet Landesberg and Chuck Green: voters rejected the same thresholds in 2022 by 59%; every signature should be verified, and lower thresholds elsewhere produced no initiatives."),
        # 7341
        _charter(27, "Concerning Legislative Branch Performance Audits", [80, 81],
                 "The Clark County Charter Review Commission adopted Resolution No. 26-14 proposing an amendment to the Clark County Home Rule Charter, concerning legislative branch performance audits. If approved, the amendment would permit the County Council to conduct, or cause to be conducted, performance and program audits to review the effectiveness and efficiency of the programs and operations of the County. Also, if approved, this amendment would require the County Council to establish by ordinance within the legislative branch an independent county auditing process.",
                 "Peter Silliman, Liz Cline and Ann Donnelly: the body that approves department budgets should be able to commission performance audits, as other charter counties allow.",
                 "John Latta, Dijana Katan and Janet Landesberg: councilors and residents can already request audits and the State Auditor reviews for free; the measure's fiscal analysis says it could cost at least $100,000 more a year."),
        # 7342
        general_measure("Clark County", "Proposition No. 12", "Bonds for Public Safety and Criminal Justice Capital Infrastructure",
                        _COUNTY, [82],
                        "The Clark County Council adopted Resolution 2026-07-08, concerning public safety and criminal justice infrastructure. This proposition would allow Clark County to acquire, construct, remodel, and equip public safety and criminal justice infrastructure in Clark County, including the remodel and expansion of the Clark County Jail and courtrooms and a new or remodeled Sheriff's Office Headquarters; issue no more than $366,204,000 of general obligation bonds maturing within 31 years; and levy annual excess property taxes on all taxable property within Clark County to pay the bonds, pursuant to Resolution 2026-07-08.",
                        "Up to $366,204,000 in general obligation bonds maturing within 31 years, repaid by annual excess property taxes countywide; the statement for puts the cost at about $86 a year per median home.",
                        "Ann Donnelly, Sue Marshall and John Horch: the jail, built more than 40 years ago, is overcrowded and unsafe; expansion would add treatment and reentry space and cut the cost of housing inmates elsewhere.",
                        _NO_CON),
        # 7344
        general_measure("Clark County", "Proposition No. 13", "Levy Lid Lift for Public Safety and Criminal Justice Services",
                        _COUNTY, [84, 85],
                        "The Clark County Council adopted Resolution 2026-07-09, concerning public safety and criminal justice services. This proposition would provide funds for public safety and criminal justice services, including additional correction deputies, sheriff deputies, prosecuting attorney staff, and other services. It authorizes a maximum regular property tax levy for collection in 2027 of $1.15 per $1,000 of assessed value, an increase of approximately $0.44 from 2026. The 2027 levy amount would be used to compute the limitations for subsequent levies under chapter 84.55 RCW. Qualifying persons are exempt under RCW 84.36.381.",
                        "County regular levy up to $1.15 per $1,000 of assessed value in 2027, about $0.44 more than 2026, and the base for later years' limits.",
                        "Ann Donnelly, Sue Marshall and John Horch: the Sheriff's Office has one of the lowest deputy-to-population ratios in the state; the levy funds deputies, corrections officers and prosecutors.",
                        "Margaret Tweet: a 62% jump in the county levy rate, raised to staff a jail expansion voters have not yet approved, on top of a 0.1% criminal justice sales tax the Council adopted in April 2026."),
        # 7345; 109 SW 1st St, Battle Ground (Census-geocoded -122.53766,
        # 45.78008): ClarkView_Public/SchoolDistrict SCHDST 119 (2026-10-08).
        general_measure("Battle Ground School District No. 119", "Proposition No. 11",
                        "Student Safety, Academic Support, Educational Programs and Operations Levy",
                        ("SCHDST", "119"), [86, 87],
                        "The Board of Directors of Battle Ground School District No. 119 adopted Resolution No. I-26, concerning funding for student safety, academic support, educational programs and operations. If approved, this proposition would authorize the District to levy the following excess taxes, replacing an expired levy, on all taxable property within the District for programs not funded by the State, including student safety, smaller classes, special education, reading and math support, curriculum, student activities, and preparing students for postsecondary education, employment, or military: 2027, estimated $1.76 per $1,000 assessed value, $37,025,000; 2028, $1.76, $38,690,000; 2029, $1.76, $40,430,000; as provided in Resolution No. I-26.",
                        "Estimated $1.76 per $1,000 of assessed value: $37,025,000 (2027), $38,690,000 (2028), $40,430,000 (2029).",
                        "Terry Dotson and Sabrena Worthy: replaces the levy that expired in 2025, lowering the amount from the failed proposals as the community asked; failure risks state financial oversight.",
                        "Richard Rylander: the fourth attempt after three failures; about $1,144 a year on a $650,000 home, with no line-item commitment on how the general-fund money is spent."),
    ],
}}


def general_override(r, unresolvable):
    dtype, district, race = r["District Type"].strip().upper(), r["District"].strip().upper(), r["Race"].strip()
    if dtype == "COUNCIL":
        n = votewa.district_number(district)
        return "County", f"Clark County Council District {n}", "County Councilor", ("COUNTY_COUNCIL", str(n))
    if dtype == "COUNTYWIDE":
        # 'COUNTY ASSESSOR' -> 'Assessor' (the primary's office names).
        return "County", "Clark County", votewa.titleish(re.sub(r"^COUNTY ", "", race.upper())), ("COUNTY", None)
    if dtype == "PUBLIC UTILITY":
        # Nominated by commissioner district in the primary, but in the
        # general "voters of the entire public utility district" elect each
        # district's commissioner (RCW 54.12.010(3)), and PUD No. 1 of Clark
        # County is countywide (its CPUCommissionerDistrict layer has the
        # council layer's extent; the 2024 District 1 general drew 222,496
        # votes, results.vote.wa.gov/results/20241105/clark/). So the general
        # electorate is the whole county, not PUDDST (#22).
        n = votewa.district_number(race)
        return ("Local", f"Public Utility District No. 1 of Clark County District {n}", "PUD Commissioner",
                ("COUNTY", None))
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
