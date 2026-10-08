"""Build lite county packages for the 32 counties covered from VoteWA data.

Contests: parsed (pipeline/votewa.py) from the official VoteWA candidate list
export for the election (election.VOTEWA_SOURCES): for the primary, the
verbatim PRIMARY 2026 CSV in counties/<county>/raw/votewa/candidate-list.csv,
rows with Election Status 'In Primary' (validated against the six hand-built
county packages, which this parser reproduced contest-for-contest); for the
general, the GENERAL 2026 export (VoteWA election 899) pinned by the pointer
counties/<county>/raw/votewa/candidate-list.csv.{url,meta.json}, rows with a
blank Election Status. PCO races and the statewide Supreme Court contests are
excluded by convention.

Measures: curated below from official county election pages, sample ballots,
and local voters' pamphlets (source_url on each measure). District scoping
uses each county's commissioner-district GIS layer and the WA Dept of
Revenue statewide taxing-district boundary layers (tax year 2025), each
verified with live point-in-polygon queries during research on 2026-07-17.

A county package claims full_county only when every contest and measure on
its ballot carries a scope the resolver in app/src/lib/geo.js can produce.
Counties with a commissioner/PUD race but no queryable district boundary
stay partial_county and the affected contest is hidden rather than shown to
the wrong voters.

Usage: python3 pipeline/build_votewa_lite_data.py [--election <id>] [--county <id> ...]

Without --county: the primary builds all 32 configured counties; later
elections build every configured county that has a VoteWA raw pointer for
that election (fetch_votewa_candidate_list.py --write-pointer adds one).
"""

import json

import election
import votewa
from election import rel
from votewa import scope_json, slugify

# DOR statewide taxing-district layer ids (2025 group) -> resolver layer key.
# Re-verified 2026-10-08 (#20): MapServer?f=json still lists tax year 2025 as
# the newest group (layer 0) and 3 CEM2025, 6 EMS2025, 7 FIR2025, 11 HSP2025,
# 12 LIB2025, 14 PKR2025 (park and recreation districts; 15 PRK2025 is a
# different layer), 20 SCH2025, 22 WAT2025; one live point query per layer
# returned the expected DISTATTRIB (table in docs/county-wave-playbook.md).
DOR_LAYER_KEYS = {
    3: "CEMDST",
    6: "EMSDST",
    7: "FIRDST",
    11: "HOSPDST",
    12: "LIBDST",
    14: "PARKDST",
    20: "SCHDST",
    22: "WATDST",
}

TAX_BASIS = "YES approves a local tax, levy, bond, or annexation measure for the listed public service."


def m(jurisdiction, proposition, title, scope, what_it_does, cost_line, source_url, pages=()):
    """Measure entry. scope is (layer, value), ('COUNTY', None), or ('CITY', name).
    pages: PDF pages of the county's local-voters-pamphlet pointer that print
    the measure (officialLinks.js pamphletPdfs links them); none by default."""
    return {
        "jurisdiction": jurisdiction,
        "proposition": proposition,
        "title": title,
        "scope": scope,
        "what_it_does": what_it_does,
        "cost_line": cost_line,
        "source_url": source_url,
        "pages": tuple(pages),
    }


# Per-county curated config. commissioner/pud/port give the scope-value format
# for district races ('{n}' means the GIS layer's attribute is the bare
# district number); None means no queryable boundary exists and the race is
# knowingly unresolvable (keeps the county partial_county).
COUNTY_CONFIG = {
    "adams": {
        "name": "Adams County", "fips": "53001",
        "commissioner": None,  # no county ArcGIS content; static PDF map only
        "measures": [
            m("Adams County Park and Recreation District No. 2", None, "Maintenance and Operations Levy (Washtucna Pool)",
              ("PARKDST", "2"),
              "Authorizes a one-year maintenance and operations levy for the Washtucna Pool.",
              "$85,000, approximately $0.83 per $1,000 of assessed value, collected in 2027.",
              "https://www.co.adams.wa.us/DocumentCenter/View/2595"),
            m("Adams County Park and Recreation District No. 3", None, "Maintenance and Operations Levy (Lind Swimming Pool)",
              ("PARKDST", "3"),
              "Authorizes a one-year maintenance and operations levy for the Lind Swimming Pool.",
              "$85,000, approximately $0.20 per $1,000 of assessed value, collected in 2027.",
              "https://www.co.adams.wa.us/DocumentCenter/View/2595"),
            m("Adams County Park and Recreation District No. 4", None, "Maintenance and Operations Levy (Ritzville Water Park)",
              ("PARKDST", "4"),
              "Authorizes a one-year maintenance and operations levy for the Ritzville Water Park.",
              "$170,000, approximately $0.30 per $1,000 of assessed value, collected in 2027.",
              "https://www.co.adams.wa.us/DocumentCenter/View/2595"),
            m("Adams County Cemetery District No. 1", None, "Maintenance and Operations Levy",
              ("CEMDST", "1"),
              "Authorizes a one-year maintenance and operations levy for cemetery upkeep.",
              "$55,500, approximately $0.55 per $1,000 of assessed value, collected in 2027.",
              "https://www.co.adams.wa.us/DocumentCenter/View/2595"),
        ],
    },
    "asotin": {
        "name": "Asotin County", "fips": "53003",
        "commissioner": None,  # no districts layer in the county AGOL org
        "measures": [
            # The DOR EMS polygon for the rural district carries DISTATTRIB '1'
            # even though the district's legal number is 2 (point-verified).
            m("Asotin County Rural EMS District No. 2", "Proposition No. 1", "Emergency Medical Services Levy",
              ("EMSDST", "1"),
              "Increases the rural EMS district's regular levy to fund emergency medical services for six years starting in 2027.",
              "Up to $0.28 per $1,000 of assessed value (up from $0.15).",
              "https://www.co.asotin.wa.us/"),
            m("City of Clarkston", "Proposition No. 1", "Emergency Medical Services Excess Levy",
              ("CITY", "Clarkston"),
              "Authorizes a one-year excess property tax levy to fund emergency medical services in Clarkston.",
              "$1,217,828 for collection in 2027, approximately $1.64 per $1,000 of assessed value.",
              "https://www.co.asotin.wa.us/"),
        ],
    },
    "benton": {
        "name": "Benton County", "fips": "53005",
        "commissioner": "{n}",
        # Benton County PUD, general only (the primary's PUD rows are not
        # 'In Primary', so the primary build never reads this). Nominated by
        # commissioner district, elected by the whole PUD in the general (RCW
        # 54.12.010(3); VoteWA's general District is 'Benton County PUD').
        # The PUD is not the whole county: Richland and most of West Richland
        # are in none of its districts (DOR PUD2025's single countywide Benton
        # polygon is a tax layer and is not used). The Auditor's precinct
        # layer PrecinctSplits (services7.arcgis.com/NURlY7V8UHl6XumF/arcgis/
        # rest/services/PrecinctSplits/FeatureServer/6) has PUD_District
        # 'Benton PUD' on exactly the precincts that voted in the 2024 PUD
        # race (SOS 20241105 Benton precinct export), except 4017 (coded
        # 'Yes'; no 2024 PUD vote). Kennewick, Prosser, Benton City: 'Benton
        # PUD'; 625 Swift Blvd, Richland: null (2026-10-08, #28).
        # COUNTY_LAYERS.benton reads that layer with where PUD_District =
        # 'Benton PUD', so 4017's 'Yes' reads as no district.
        "pud": "Benton PUD",
        "measures": [
            m("Benton County Fire Protection District No. 4", "Proposition No. 1", "Restoration of Regular Property Tax Levy",
              ("FIRDST", "4"),
              "Restores the fire district's regular levy rate with a 106% limit factor for nine years (West Richland area).",
              "Restores the levy to $1.50 per $1,000 of assessed value.",
              "https://elections.bentoncountywa.gov/"),
            m("Benton County Fire Protection District No. 6", "Proposition No. 1", "Emergency Medical Services Levy",
              ("FIRDST", "6"),
              "Reestablishes an EMS levy for ten years beginning in 2027.",
              "Up to $0.50 per $1,000 of assessed value.",
              "https://elections.bentoncountywa.gov/"),
        ],
    },
    "chelan": {
        "name": "Chelan County", "fips": "53007",
        "commissioner": "{n}",
        "measures": [],  # confirmed: no measures on the Aug 4, 2026 ballot
    },
    "clallam": {
        "name": "Clallam County", "fips": "53009",
        "commissioner": "{n}",
        "pud": "{n}",
        "measures": [
            m("Clallam County Fire Protection District No. 2", "Proposition No. 1", "Property Tax Levy For Emergency Medical Services",
              ("FIRDST", "2"),
              "Authorizes a ten-year EMS levy collected beginning in 2027; requires a 60% supermajority with validation.",
              "$0.50 per $1,000 of assessed value.",
              "https://www.clallamcountywa.gov/"),
        ],
    },
    "columbia": {
        "name": "Columbia County", "fips": "53013",
        "commissioner": "{n}",
        "measures": [],  # confirmed: candidate races only
    },
    "cowlitz": {
        "name": "Cowlitz County", "fips": "53015",
        "commissioner": "{n}",
        "measures": [],  # confirmed: sample ballot contains no measures
    },
    "douglas": {
        "name": "Douglas County", "fips": "53017",
        "commissioner": None,  # county view layer not shared publicly
        "measures": [
            m("Public Hospital District No. 1, Okanogan and Douglas Counties", "Proposition No. 1", "One-Year Special Levy",
              ("HOSPDST", "1"),
              "Renews a one-year special levy for hospital district operations, levied in 2026 for collection in 2027.",
              "$1,460,000, approximately $0.33 per $1,000 of assessed value.",
              "https://www.douglascountywa.net/"),
            m("Douglas-Okanogan County Fire District No. 15", "Proposition No. 1", "Emergency Medical Services Levy",
              ("FIRDST", "J15"),
              "Continues a six-year EMS levy beginning in 2027.",
              "$0.50 per $1,000 of assessed value.",
              "https://www.douglascountywa.net/"),
        ],
    },
    "ferry": {
        "name": "Ferry County", "fips": "53019",
        "commissioner": "{n}",
        "measures": [
            m("Ferry County Emergency Medical Services District 1", None, "Continuing Emergency Medical Services Levy",
              ("EMSDST", "1"),
              "Continues the EMS district's regular levy for six years, collected 2027 through 2032. The district excludes the City of Republic.",
              "$0.50 per $1,000 of assessed value.",
              "https://www.ferry-county.com/ferry%20county%20primary%202026.pdf"),
            m("City of Republic", None, "Emergency Medical Services Levy",
              ("CITY", "Republic"),
              "Authorizes regular property tax levies for six years to fund emergency medical services in Republic.",
              "$0.50 per $1,000 of assessed value.",
              "https://www.ferry-county.com/ferry%20county%20primary%202026.pdf"),
        ],
    },
    "franklin": {
        "name": "Franklin County", "fips": "53021",
        "commissioner": "COM{n}",
        "measures": [],  # confirmed: "No resolutions were submitted."
    },
    "garfield": {
        "name": "Garfield County", "fips": "53023",
        "commissioner": None,  # static PDF district map only
        # No measures found (VoteWA guide and local press list candidate races
        # only), but the county site blocks automated access so this could not
        # be confirmed against an official county page.
        "measures": [],
        "extra_notes": [
            "Measure absence corroborated by the VoteWA 2026 primary guide and local press but not confirmed on an official county page (site blocks automated access).",
        ],
    },
    "grant": {
        "name": "Grant County", "fips": "53025",
        "commissioner": "{n}",
        "measures": [
            m("Grant County Public Hospital District No. 5", "Proposition No. 1", "Multi-year Levy Lid Lift For Health Care Services",
              ("HOSPDST", "5"),
              "Lifts the hospital district levy lid for health care services at the Mattawa Community Medical Clinic, with up to a 6% limit factor for 2027 through 2035.",
              "Up to $0.75 per $1,000 of assessed value for 2027 collection.",
              "https://www.grantcountywa.gov/DocumentCenter/View/16463"),
        ],
    },
    "grays-harbor": {
        "name": "Grays Harbor County", "fips": "53027",
        "commissioner": None,  # county uses MapGeo; no ArcGIS REST layer
        "measures": [
            m("Mason County Fire Protection District No. 12", "Proposition No. 1", "Emergency Medical Services Levy Renewal",
              ("FIRDST", "12M"),
              "Renews a six-year EMS levy for the cross-county fire district.",
              "$0.50 per $1,000 of assessed value.",
              "https://voter.votewa.gov/genericvoterguide.aspx?e=898&c=14"),
            m("South Beach Regional Fire Authority", "Proposition No. 1", "General Obligation Bonds for Headquarters Fire Station",
              ("FIRDST", "SBRFA"),
              "Authorizes general obligation bonds over 25 years to replace the headquarters fire station.",
              "$10,000,000 in bonds.",
              "https://voter.votewa.gov/genericvoterguide.aspx?e=898&c=14"),
            m("Grays Harbor County Fire Protection District No. 7", "Proposition No. 1", "Ambulance Maintenance and Operations Excess Levy",
              ("FIRDST", "7"),
              "Authorizes a four-year excess levy for ambulance maintenance and operations.",
              "$200,000 per year, approximately $0.45 per $1,000 of assessed value.",
              "https://voter.votewa.gov/genericvoterguide.aspx?e=898&c=14"),
        ],
    },
    "island": {
        "name": "Island County", "fips": "53029",
        "commissioner": "{n}",
        # The PUD race is Snohomish County PUD No. 1 Commissioner District 1
        # (Camano Island); no GIS layer covers the Island County side.
        "pud": None,
        "measures": [
            m("Sno-Isle Intercounty Rural Library District", "Proposition No. 1", "Levy Lid Lift",
              ("LIBDST", "L"),
              "Restores the library district's regular levy rate for 2027 collection.",
              "Restores the levy to $0.47 per $1,000 of assessed value.",
              "https://voter.votewa.gov/genericvoterguide.aspx?e=898&c=15"),
        ],
    },
    "jefferson": {
        "name": "Jefferson County", "fips": "53031",
        "commissioner": "{n}",
        "measures": [
            m("Jefferson County", "Proposition No. 1", "Parks and Recreation Levy",
              ("COUNTY", None),
              "Authorizes a six-year county-wide levy for parks and recreation.",
              "$0.21 per $1,000 of assessed value.",
              "https://www.co.jefferson.wa.us/1266/Elections"),
            m("Jefferson County Fire Protection District No. 2 (Quilcene Fire Rescue)", "Proposition No. 1", "Levy Lid Lift",
              ("FIRDST", "2"),
              "Lifts the fire district's regular levy lid.",
              "$1.25 per $1,000 of assessed value.",
              "https://www.co.jefferson.wa.us/1266/Elections"),
            m("Jefferson County Fire Protection District No. 4 (Brinnon Fire Department)", "Proposition No. 1", "Regular Property Tax Levy",
              ("FIRDST", "4"),
              "Restores the fire district's regular levy with a 104% limit factor for nine years.",
              "$1.50 per $1,000 of assessed value.",
              "https://www.co.jefferson.wa.us/1266/Elections"),
            m("Jefferson County Fire Protection District No. 4 (Brinnon Fire Department)", "Proposition No. 2", "Emergency Medical Services Levy",
              ("FIRDST", "4"),
              "Authorizes an EMS levy with a 104% limit factor for nine years.",
              "$0.50 per $1,000 of assessed value.",
              "https://www.co.jefferson.wa.us/1266/Elections"),
            m("Jefferson County Cemetery District No. 2 (Quilcene Cemetery)", "Proposition No. 1", "Regular Property Tax Levy",
              ("CEMDST", "2"),
              "Authorizes a regular levy for cemetery maintenance.",
              "$0.04 per $1,000 of assessed value.",
              "https://www.co.jefferson.wa.us/1266/Elections"),
        ],
    },
    "kittitas": {
        "name": "Kittitas County", "fips": "53037",
        "commissioner": "{n}",
        "measures": [
            m("Snoqualmie Pass Fire and Rescue", "Proposition No. 1", "Continuation of Benefit Charge",
              ("FIRDST", "51"),
              "Continues the fire district's benefit charge (up to 60% of its budget) for six years.",
              "Benefit charge up to 60% of the district's operating budget.",
              "https://www.co.kittitas.wa.us/auditor/elections/"),
            m("City of Cle Elum", "Proposition No. 1", "Fire Levy Lid Lift",
              ("CITY", "Cle Elum"),
              "Lifts the city levy lid for fire service funding for two years.",
              "An additional $0.98, to $1.87 per $1,000 of assessed value.",
              "https://www.co.kittitas.wa.us/auditor/elections/"),
            m("City of Roslyn", "Proposition No. 1", "Library Levy",
              ("CITY", "Roslyn"),
              "Authorizes a library levy.",
              "Up to $1.50 per $1,000 of assessed value.",
              "https://www.co.kittitas.wa.us/auditor/elections/"),
            m("Kittitas County Fire Protection District No. 2 (Kittitas Valley Fire Rescue)", "Proposition No. 1", "Levy Lid Lift",
              ("FIRDST", "2"),
              "Lifts the fire district's regular levy lid.",
              "Up to $1.50 per $1,000 of assessed value.",
              "https://www.co.kittitas.wa.us/auditor/elections/"),
        ],
    },
    "klickitat": {
        "name": "Klickitat County", "fips": "53039",
        "commissioner": "{n}",
        "pud": None,  # PUD publishes district maps only as PDFs
        "measures": [
            m("Klickitat County Fire Protection District No. 4 (Lyle)", "Proposition No. 1", "Fire Protection and Emergency Medical Services Levy",
              ("FIRDST", "4"),
              "Sets the fire and EMS levy for 2026 with CPI adjustments for nine years (Resolution 2026-04).",
              "$1.15 per $1,000 of assessed value.",
              "https://klickitatcounty.org/DocumentCenter/View/22962"),
        ],
    },
    "lewis": {
        "name": "Lewis County", "fips": "53041",
        "commissioner": "{n}",
        "measures": [
            m("Lewis County Fire Protection District No. 3 (Mossyrock)", "Proposition No. 1", "Restoration of Emergency Medical Services Levy",
              ("FIRDST", "3"),
              "Restores the district's EMS levy.",
              "$0.50 per $1,000 of assessed value.",
              "https://lewiscountywa.gov/offices/auditor/elections/"),
            m("Lewis County Fire Protection District No. 8 (Salkum)", "Proposition No. 1", "Restoration of Fire and EMS Levy",
              ("FIRDST", "8"),
              "Restores the district's fire and EMS levy with nine years of CPI adjustments.",
              "$0.88 per $1,000 of assessed value.",
              "https://lewiscountywa.gov/offices/auditor/elections/"),
            m("Lewis County Fire Protection District No. 15 (Winlock)", "Proposition No. 1", "Continuation of Emergency Medical Services Levy",
              ("FIRDST", "15"),
              "Continues the district's EMS levy for six years.",
              "$0.45 per $1,000 of assessed value.",
              "https://lewiscountywa.gov/offices/auditor/elections/"),
        ],
    },
    "lincoln": {
        "name": "Lincoln County", "fips": "53043",
        "commissioner": None,  # districts exist only inside a web-map feature collection
        "measures": [
            m("Lincoln County Cemetery District No. 7 (Sprague)", "Proposition No. 1", "Excess Levy",
              ("CEMDST", "7"),
              "Authorizes a one-year excess levy for cemetery operations, collected in 2027 (Resolution 2026-01).",
              "$40,000, approximately $0.25 per $1,000 of assessed value.",
              "https://www.co.lincoln.wa.us/auditor/elections/"),
        ],
    },
    "mason": {
        "name": "Mason County", "fips": "53045",
        "commissioner": "{n}",
        "measures": [
            m("Central Mason Fire & EMS", None, "Property Tax Levy for Fire Protection and Emergency Medical Services",
              ("FIRDST", "5"),
              "Restores the fire district's regular levy with a 104% limit factor for three years (Resolution 414).",
              "Up to $1.48 per $1,000 of assessed value.",
              "https://masoncountywa.gov/auditor/elections/"),
            m("Mason County Fire Protection District No. 12 (Matlock)", None, "Renewal and Increase of Emergency Medical Services Levy",
              ("FIRDST", "12"),
              "Renews and increases the district's EMS levy for six years, 2027 through 2032.",
              "Up to $0.50 per $1,000 of assessed value.",
              "https://masoncountywa.gov/auditor/elections/"),
            m("North Mason Regional Fire Authority", None, "Emergency Medical Services Property Tax Levy",
              ("FIRDST", "NMRFA"),
              "Continues the fire authority's EMS levy for six years.",
              "Up to $0.50 per $1,000 of assessed value.",
              "https://masoncountywa.gov/auditor/elections/"),
        ],
    },
    "okanogan": {
        "name": "Okanogan County", "fips": "53047",
        "commissioner": None,  # no public REST layer for commissioner districts
        "measures": [
            m("Okanogan County", "Proposition No. 1", "Levy Lid Lift",
              ("COUNTY", None),
              "Lifts the county's regular levy lid for 2027 collection (Resolution 48-2026).",
              "$1.15 per $1,000 of assessed value.",
              "https://www.okanogancounty.org/government/auditor/district_resolutions.php"),
            m("Douglas Okanogan County Fire District 15", "Proposition No. 1", "Emergency Medical Services Levy",
              ("FIRDST", "J15"),
              "Continues a six-year EMS levy.",
              "$0.50 per $1,000 of assessed value.",
              "https://www.okanogancounty.org/government/auditor/district_resolutions.php"),
            m("City of Pateros", None, "Emergency Medical Services Levy",
              ("CITY", "Pateros"),
              "Continues a six-year EMS levy in the City of Pateros.",
              "$0.50 per $1,000 of assessed value.",
              "https://www.okanogancounty.org/government/auditor/district_resolutions.php"),
            m("Public Hospital District No. 1, Okanogan and Douglas Counties", "Proposition No. 1", "One-Year Special Levy",
              ("HOSPDST", "1J"),
              "Renews a one-year special levy for hospital district operations.",
              "$1,460,000, approximately $0.33 per $1,000 of assessed value.",
              "https://www.okanogancounty.org/government/auditor/district_resolutions.php"),
        ],
    },
    "pacific": {
        "name": "Pacific County", "fips": "53049",
        "commissioner": None,  # political districts published as downloads only
        "measures": [
            m("South Beach Regional Fire Authority", "Proposition No. 1", "General Obligation Bonds for Headquarters Fire Station",
              ("FIRDST", "5 SBRFA"),
              "Authorizes general obligation bonds over 25 years to replace the headquarters fire station.",
              "$10,000,000 in bonds.",
              "https://www.pacificcountywa.gov/"),
        ],
    },
    "pend-oreille": {
        "name": "Pend Oreille County", "fips": "53051",
        "commissioner": "Commissioner - 0{n}",
        # PUD No. 1 is county-wide, so its commissioner districts are the
        # county commissioner districts (RCW 54.12.010) — same layer.
        "pud": "Commissioner - 0{n}",
        "pud_layer_key": "COUNTY_COUNCIL",
        "measures": [
            m("Pend Oreille County Public Hospital District No. 1", "Proposition No. 1", "Hospital Expansion and Renovation Bonds",
              ("HOSPDST", "1"),
              "Authorizes 30-year general obligation bonds to expand and renovate Newport Community Hospital.",
              "$51,000,000 in bonds.",
              "https://pendoreilleco.org/your-government/auditor/elections/"),
        ],
    },
    "san-juan": {
        "name": "San Juan County", "fips": "53055",
        # Council members are elected county-wide (residency districts are a
        # candidate qualification, not an electorate), so no district layer is
        # needed; the CSV types the council race Countywide.
        "commissioner": None,
        "measures": [
            m("Lopez Island School District No. 144", "Proposition No. 1", "Replacement Educational Programs and Operations Levy",
              ("SCHDST", "144"),
              "Replaces the expiring educational programs and operations levy for 2027 through 2030.",
              "Approximately $0.36 per $1,000 of assessed value ($1,115,000 to $1,235,000 per year).",
              "https://www.sanjuancountywa.gov/"),
        ],
    },
    "skagit": {
        "name": "Skagit County", "fips": "53057",
        "commissioner": "{n}",
        # Skagit PUD No. 1 is countywide (VoteWA district 'SKAGIT PUD
        # DISTRICT COUNTYWIDE'; DOR PUD2025 layer 17 polygon DISTATTRIB '1'
        # at Anacortes, Mount Vernon, Concrete and Marblemount) and the whole
        # PUD elects each commissioner in the general (RCW 54.12.010(3)), so
        # the seat is scoped COUNTY. The primary had no PUD race.
        "pud": "{n}", "pud_layer_key": "COUNTY",
        "measures": [
            m("Darrington School District No. 330", "Proposition No. 1", "Replacement Educational Programs and Operations Levy",
              ("SCHDST", "330"),
              "Replaces the expiring educational programs and operations levy, $950,000 per year for 2027 through 2030.",
              "Estimated $1.24 declining to $1.02 per $1,000 of assessed value.",
              "https://www.skagitcounty.net/Departments/Elections"),
            m("Skagit County Public Hospital District No. 304 (United General)", "Proposition No. 1", "Levy Lid Lift",
              ("HOSPDST", "304"),
              "Lifts the hospital district's regular levy lid for 2027 collection.",
              "$0.50 per $1,000 of assessed value.",
              "https://www.skagitcounty.net/Departments/Elections"),
            m("Skagit County Fire Protection District No. 8", "Proposition No. 1", "Levy Restoration",
              ("FIRDST", "8"),
              "Restores the fire district's regular levy with a 103% limit factor for five years.",
              "$1.25 per $1,000 of assessed value.",
              "https://www.skagitcounty.net/Departments/Elections"),
        ],
    },
    "skamania": {
        "name": "Skamania County", "fips": "53059",
        "commissioner": "{n}",
        "measures": [
            m("Home Valley Water District No. 1", "Proposition No. 1", "Maintenance and Capital Improvement Fund Levy",
              ("WATDST", "1"),
              "Authorizes a one-year excess levy replacing an expiring levy for water system maintenance and capital improvements (Resolution 2026-3).",
              "$25,000 for 2027, approximately $0.57 per $1,000 of assessed value.",
              "https://voter.votewa.gov/genericvoterguide.aspx?e=898&c=30"),
        ],
    },
    "stevens": {
        "name": "Stevens County", "fips": "53065",
        "commissioner": "{n}",
        "measures": [
            m("Stevens County Fire Protection District No. 6", "Proposition No. 1", "Property Tax Levy for Fire Protection Services",
              ("FIRDST", "6"),
              "Sets the 2026 fire levy with CPI-based annual growth for nine succeeding years (Resolution 2026-01).",
              "$1.07 per $1,000 of assessed value.",
              "https://voter.votewa.gov/genericvoterguide.aspx?e=898&c=33"),
        ],
    },
    "wahkiakum": {
        "name": "Wahkiakum County", "fips": "53069",
        "commissioner": "{n}",
        "measures": [],  # confirmed: sample ballot has candidates only
    },
    "walla-walla": {
        "name": "Walla Walla County", "fips": "53071",
        "commissioner": "{n}",
        "measures": [],  # confirmed: Notice of Primary Election lists no propositions
    },
    "whatcom": {
        "name": "Whatcom County", "fips": "53073",
        "commissioner": None,  # no council race in this primary; layer not needed
        "port": "{n}",
        "measures": [
            m("Whatcom County Fire Protection District No. 1", "Proposition 2026-02", "Levy Lid Lift",
              ("FIRDST", "1"),
              "Lifts the fire district levy lid with a 106% limit factor for nine years (Everson/Nooksack area).",
              "$1.48 per $1,000 of assessed value.",
              "https://www.whatcomcounty.us/2794/Elections"),
            m("Glacier Fire and Rescue (Whatcom County Fire Protection District No. 19)", "Proposition 2026-04", "Regular Property Tax Levy",
              ("FIRDST", "19"),
              "Sets the fire district's regular levy with a 104% limit factor for six years.",
              "$1.10 per $1,000 of assessed value.",
              "https://www.whatcomcounty.us/2794/Elections"),
            m("Whatcom County Fire Protection District No. 21", "Proposition 2026-03", "Regular Property Tax Levy",
              ("FIRDST", "21"),
              "Sets the fire district's regular levy with a 103% limit factor for five years.",
              "$1.20 per $1,000 of assessed value.",
              "https://www.whatcomcounty.us/2794/Elections"),
            m("Skagit County Public Hospital District No. 304 (United General)", "Proposition No. 1", "Levy Lid Lift",
              ("HOSPDST", "304"),
              "Lifts the cross-county hospital district's regular levy lid for 2027 collection.",
              "$0.50 per $1,000 of assessed value.",
              "https://www.whatcomcounty.us/2794/Elections"),
        ],
    },
    "whitman": {
        "name": "Whitman County", "fips": "53075",
        "commissioner": "{n}",
        "measures": [
            m("Rosalia Park and Recreation District No. 5", "Proposition No. 1", "Two Year Maintenance and Operations Levy for the Rosalia Pool",
              ("PARKDST", "5"),
              "Authorizes regular property tax levies in 2027 and 2028 to fund operating, maintaining, and improving the Rosalia Pool. Requires a 60% supermajority.",
              "$85,000 per year, approximately $0.39 (maximum $0.60) per $1,000 of assessed value.",
              "https://www.whitmancounty.gov/"),
            m("Whitman County Fire Protection District No. 1", "Special Election - Proposition No. 1", "Annexation of the City of Tekoa",
              ("FIRDST", "1"),
              "Asks fire district voters whether the City of Tekoa should be annexed into Fire Protection District No. 1.",
              "Annexed property becomes subject to the district's regular fire levies.",
              "https://www.whitmancounty.gov/"),
            m("City of Tekoa", "Special Election - Proposition No. 1", "Annexation into Fire Protection District No. 1",
              ("CITY", "Tekoa"),
              "Asks Tekoa voters whether the city should be annexed into Whitman County Fire Protection District No. 1.",
              "City property becomes subject to the district's regular fire levies.",
              "https://www.whitmancounty.gov/"),
            m("Town of Farmington", "Special Election - Proposition No. 1", "Excess Levy",
              ("CITY", "Farmington"),
              "Authorizes a one-year excess property tax levy for town operations.",
              "$28,000, approximately $4.18 per $1,000 of assessed value.",
              "https://www.whitmancounty.gov/"),
            m("Whitman County Fire Protection District No. 5", "Special Election - Proposition No. 1", "Maintenance and Operations Levy",
              ("FIRDST", "5"),
              "Authorizes maintenance and operations levies collected 2027 through 2030.",
              "$10,000 per year, approximately $0.21 per $1,000 of assessed value.",
              "https://www.whitmancounty.gov/"),
        ],
    },
    "yakima": {
        "name": "Yakima County", "fips": "53077",
        "commissioner": "{n}",
        "measures": [
            m("Yakima County Fire Protection District No. 6", "Proposition No. 1", "Levy Restoration",
              ("FIRDST", "06"),
              "Restores the fire district's regular levy with a 103% limit factor for nine years.",
              "$1.00 per $1,000 of assessed value.",
              "https://www.yakimacounty.us/149/Elections"),
        ],
    },
}


# Measures per election. The primary's are the `measures` lists in
# COUNTY_CONFIG above (curated 2026-07-17). From the general on, a county's
# measures are curated here by the agent working that county (see
# docs/county-wave-playbook.md) from its official local pamphlet or sample
# ballot; a county with no entry gets an empty measure list and a note saying
# its measures are not curated yet, so it can never pass for "no measures".
ELECTION_MEASURES = {
    "2026-11-03-general": {
        # Benton (#28): the three local measures on the Benton County Auditor's
        # general sample ballot (counties/benton/raw/benton/sample-ballot.pdf.url),
        # transcribed from VoteWA's online voters' guide records (e=899, c=03).
        # CITY: Census place 'Benton City' at 1009 Dale Ave, Benton City.
        # SCHDST: DOR SCH2025 (layer 20) DISTATTRIB '52' at the same address
        # (2026-10-08), which COUNTY_LAYERS.benton reads; the PUD race's
        # PUDDST reads the Auditor's PrecinctSplits layer (see COUNTY_CONFIG).
        "benton": {
            "measures": [
                m("City of Benton City", "Proposition No. 1", "Adoption of the Council-Manager Form of Government",
                  ("CITY", "Benton City"),
                  "Changes Benton City from the mayor-council to the council-manager form of government, effective March 1, 2027: the council would hire a professional city manager and choose a mayor from among its members.",
                  "No tax change; the city would pay a full-time manager in place of the elected mayor.",
                  "https://voter.votewa.gov/elections/measure.ashx?m=7271&e=899&la=en&c=03"),
                m("City of Benton City", "Proposition No. 2", "Community Safety Levy Lid Lift",
                  ("CITY", "Benton City"),
                  "Restores Benton City's regular property tax levy to $1.60 per $1,000 for 2027 to fund law and code enforcement, with CPI-based increases through 2036 (never above $1.60).",
                  "$1.60 per $1,000 of assessed value for 2027 collection.",
                  "https://voter.votewa.gov/elections/measure.ashx?m=7272&e=899&la=en&c=03"),
                m("Kiona-Benton City School District No. 52", "Proposition No. 1", "Educational Programs and Operation Replacement Levy",
                  ("SCHDST", "52"),
                  "Authorizes a two-year educational programs and operation levy replacing an expired levy.",
                  "Estimated $1.30 per $1,000 of assessed value: $2,208,341 in 2027 and $2,318,758 in 2028.",
                  "https://voter.votewa.gov/elections/measure.ashx?m=7273&e=899&la=en&c=03"),
            ],
        },
        # Chelan (#29). Measures: Chelan County Elections' general sample
        # ballot and Local Voters' Pamphlet (counties/chelan/raw/chelan/
        # {sample-ballot,local-voters-pamphlet}.pdf.url, pamphlet pp. 16-18,
        # linked from co.chelan.wa.us/elections/pages/november-3-2026-general-
        # election) list two local measures; VoteWA's online guide for county
        # 04 (raw/votewa/voter-guide/voterguide.json.url) agrees. Scopes
        # point-checked 2026-10-08 (Census geocoder, Current vintage; WA DOR
        # 2025 layer 20 SCH2025): 101 Woodring St, Cashmere -> CITY
        # 'Cashmere'; 350 Orondo Ave, Wenatchee -> SCH2025 DISTATTRIB '246'
        # (101 Woodring St, Cashmere -> '222', not in the district).
        # Cost and purpose wording also draws on the measure dossiers'
        # sources (counties/chelan/raw/measures/): the district's bond page,
        # City of Cashmere Ordinance 1345 and the Assessor's 2026 levy book.
        # Overrides: VoteWA files the commissioner race as Countywide; it is
        # nominated by district and elected county-wide in the general (RCW
        # 36.32.040; SOS 2022 general: Commissioner District No. 2 drew 33,392
        # votes of 34,530 Chelan ballots) and keeps the primary's contest name
        # so primary dossiers carry forward. The District Court seats
        # (District Type County) are judicial seats of one county-wide court
        # (2022 Judge #1: 29,039 votes). Chelan County PUD (Public Utility
        # District No. 1 of Chelan County) is county-wide (DOR PUD2025 layer
        # 17 DISTATTRIB '1' at Wenatchee, Cashmere, Leavenworth, Chelan and
        # Stehekin alike) and the whole PUD elects each commissioner in the
        # general (RCW 54.12.010(3); 2022 District 3: 28,626 votes), so its
        # rows (District 'PUD ALL', which classify() cannot number) are
        # scoped COUNTY.
        "chelan": {
            "overrides": {
                ("COUNTY", "COMMISSIONER DISTRICT NO. 2"): (
                    "County", "Chelan County Commissioner District 2", "Commissioner District No. 2", ("COUNTY", None)),
                ("CHELAN COUNTY", "DISTRICT COURT JUDGE POSITION 1"): (
                    "Judicial", "Chelan County District Court", "Judge Position No. 1", ("COUNTY", None)),
                ("CHELAN COUNTY", "DISTRICT COURT JUDGE POSITION 2"): (
                    "Judicial", "Chelan County District Court", "Judge Position No. 2", ("COUNTY", None)),
                ("PUD ALL", "PUBLIC UTILITY DIST COMMISSIONER DIST 1"): (
                    "PublicUtility", "Public Utility District No. 1 of Chelan County", "Commissioner District 1",
                    ("COUNTY", None)),
                ("PUD ALL", "PUBLIC UTILITY DIST COMMISSIONER DIST B"): (
                    "PublicUtility", "Public Utility District No. 1 of Chelan County", "Commissioner District B (At Large)",
                    ("COUNTY", None)),
            },
            "measures": [
                m("Wenatchee School District No. 246", "Proposition No. 1",
                  "Bonds to Replace Deteriorating Wenatchee High School and Improve School Air Quality Districtwide",
                  ("SCHDST", "246"),
                  "Authorizes $275,000,000 of general obligation bonds, repaid by excess property taxes over up to 20 years, to replace most of Wenatchee High School with new classrooms on its campus (renovating the gyms, pool and auditorium) and replace HVAC at four elementary and three middle schools; it would also qualify the district for an estimated $83,000,000 in state matching funds. Needs 60% yes.",
                  "$275,000,000 in bonds over up to 20 years; the district estimates $1.46 per $1,000 of assessed value a year (about $584 on a $400,000 home), on top of the current $2.77 school rate, and about $444 million repaid including interest.",
                  "https://voter.votewa.gov/elections/measure.ashx?m=7302&e=899&la=en&c=04",
                  pages=(16, 17)),
                m("City of Cashmere", "Proposition No. 1", "Public Safety and Government Services Levy Lid Lift",
                  ("CITY", "Cashmere"),
                  "Lifts Cashmere's regular property tax levy to continue city services, which Ordinance 1345 names as law enforcement, fire protection and disaster mitigation, and lets the levy rise up to 9% a year from 2028 to 2032; the 2032 levy becomes the base for future levy limits.",
                  "$1.5737 per $1,000 of assessed value in 2027, up from $1.4441 in 2026 (about $52 more a year on a $400,000 home), then up to 9% more a year through 2032.",
                  "https://voter.votewa.gov/elections/measure.ashx?m=7301&e=899&la=en&c=04",
                  pages=(18,)),
            ],
        },
        # Clallam (#29). Measures: the Auditor's general sample ballot and local
        # voters' pamphlet (counties/clallam/raw/clallam/{sample-ballot,
        # local-voters-pamphlet}.pdf.url, linked from clallamcountywa.gov/2002/
        # 2026-November-General-Election) list seven local measures; VoteWA's
        # online guide for county 05 (measures 7289-7294, 7296) agrees. Scopes
        # point-checked 2026-10-09 (Census geocoder, Current vintage; WA DOR
        # 2025 layers 7 FIR and 20 SCH): 500 E Division St, Forks -> FIR2025
        # '1', SCH2025 '402'; 3851 S Mount Angeles Rd, Port Angeles -> FIR2025
        # '2'; 7764 La Push Rd, Forks -> FIR2025 '6'. The county's own
        # Fire_Districts and Precinct_Splits layers agree at each address.
        # Overrides:
        # - Commissioner District 3: nominated by district, elected county-wide
        #   (Home Rule Charter Section 2.20, as amended 2015 and 2020; 2022
        #   general: 39,943 votes in the D3 race vs 37,120 for the county-wide
        #   DCD Director). Keeps the primary's contest name so primary dossiers
        #   carry forward.
        # - District Court 1 and 2 are separate electoral districts (2022
        #   general: 23,704 votes for District Court 1, 1,940 for District
        #   Court 2), scoped DISTCRT to the Auditor's District_Court layer
        #   (services8.arcgis.com/noCZ2SM2C0rVag8y/.../District_Court/
        #   FeatureServer/0, DISTRICT '1' at Port Angeles and Sequim, '2' at
        #   Forks), which COUNTY_LAYERS.clallam reads since #29.
        # - PUD No. 1 Commissioner District No. 2: elected by the whole PUD in
        #   the general (RCW 54.12.010(3)), but the PUD's electorate is not the
        #   county: the City of Port Angeles precincts are in none of the PUD's
        #   commissioner districts (PUD_Commissioner_District_dissolve has no
        #   feature at 223 E 4th St, Port Angeles; 2022 general PUD D1 race
        #   28,129 votes vs 39,943 county-wide). COUNTY would show it to Port
        #   Angeles voters, and the PUDDST key reads the commissioner district
        #   number (1-3), not PUD membership, so the seat is scoped to the
        #   layer PUDALL '1'. COUNTY_LAYERS.clallam resolves it since #29: any
        #   feature of PUD_Commissioner_District_dissolve reads as the
        #   constant '1' (geo.js layer `value`).
        "clallam": {
            "overrides": {
                ("COUNTY", "COUNTY COMMISSIONER DIST. NO. 3"): (
                    "County", "Clallam County Commissioner District 3", "County Commissioner Dist. No. 3",
                    ("COUNTY", None)),
                ("DISTRICT COURT 1", "JUDGE - DISTRICT COURT 1"): (
                    "Judicial", "Clallam County District Court 1", "Judge", ("DISTCRT", "1")),
                ("DISTRICT COURT 2", "JUDGE - DISTRICT COURT 2"): (
                    "Judicial", "Clallam County District Court 2", "Judge", ("DISTCRT", "2")),
                ("PUBLIC UTILITY DISTRICT NO. 1", "COMMISSIONER DISTRICT NO. 2"): (
                    "PublicUtility", "Public Utility District No. 1 of Clallam County", "Commissioner District No. 2",
                    ("PUDALL", "1")),
            },
            "measures": [
                m("Clallam County", "Proposed Charter Amendment No. 1",
                  "Charter Amendment Requiring County Commissioner District Town Hall Meetings",
                  ("COUNTY", None),
                  "Amends Article II of the county charter: each commissioner must hold at least one town hall a year in their own district, and the three commissioners together at least one a year in each district, all outside normal business hours with 30 days' notice.",
                  "No tax or fee; no fiscal statement was filed.",
                  "https://voter.votewa.gov/elections/measure.ashx?m=7289&e=899&la=en&c=05",
                  pages=(42, 43)),
                m("Clallam County", "Proposed Charter Amendment No. 2",
                  "Charter Amendment Establishing an Ethics Review Board",
                  ("COUNTY", None),
                  "Amends Article VIII of the county charter to create a three-member, unpaid ethics review board (one member per commissioner district, appointed by elected county officials) that reviews complaints that elected county officials broke the county code of ethics and publishes written findings; it cannot impose penalties.",
                  "No tax or fee; board members serve without pay (opponents cite staff and process costs; no fiscal statement was filed).",
                  "https://voter.votewa.gov/elections/measure.ashx?m=7290&e=899&la=en&c=05",
                  pages=(44, 45)),
                m("Clallam County", "Proposed Charter Amendment No. 3",
                  "Charter Amendment Requiring Printing of the Full Text of Proposed Charter Amendments in the Local Voters' Pamphlet",
                  ("COUNTY", None),
                  "Amends Article XI of the county charter to require the full text of every proposed charter amendment to be printed in the local voters' pamphlet.",
                  "No tax or fee; affects what the Auditor prints in future pamphlets.",
                  "https://voter.votewa.gov/elections/measure.ashx?m=7291&e=899&la=en&c=05",
                  pages=(46, 47)),
                m("Quillayute Valley School District No. 402", "Proposition No. 1", "Bonds to Rebuild Forks Middle School",
                  ("SCHDST", "402"),
                  "Authorizes $34,000,000 of general obligation bonds, maturing within 25 years and repaid by excess property taxes, to build a new Forks Middle School replacing three existing buildings on the site.",
                  "$34,000,000 in bonds repaid over up to 25 years; the district estimates about $1.94 per $1,000 of assessed value from 2028, as its high school bond ends.",
                  "https://voter.votewa.gov/elections/measure.ashx?m=7296&e=899&la=en&c=05",
                  pages=(58,)),
                m("Clallam County Fire Protection District No. 1", "Proposition No. 1",
                  "Property Tax Levy for Fire Protection and Emergency Medical Services",
                  ("FIRDST", "1"),
                  "Sets the Forks-area fire district's regular levy at $1.00 per $1,000 for 2027 collection and lets it grow each year for nine more years by the greater of 1% or West Region CPI-U; the 2035 maximum becomes the base for later limits.",
                  "$1.00 per $1,000 of assessed value for 2027 collection, up from about $0.47, then CPI-based growth (at least 1%) through 2035.",
                  "https://voter.votewa.gov/elections/measure.ashx?m=7292&e=899&la=en&c=05",
                  pages=(59,)),
                m("Clallam County Fire Protection District No. 2", "Proposition No. 1", "Property Tax Levy For Emergency Medical Services",
                  ("FIRDST", "2"),
                  "Authorizes a ten-year EMS property tax levy for the fire district around Port Angeles, collected from 2027, used only for emergency medical services (the district says it would end transport bills for district residents). Needs 60% yes and minimum turnout; the same levy fell short in the August primary.",
                  "Up to $0.50 per $1,000 of assessed value a year for ten years, starting with 2027 collection.",
                  "https://voter.votewa.gov/elections/measure.ashx?m=7293&e=899&la=en&c=05",
                  pages=(60, 61)),
                m("Clallam County Fire Protection District No. 6", "Proposition No. 1",
                  "Property Tax Levy For Fire Protection and Emergency Services",
                  ("FIRDST", "6"),
                  "Restores the regular levy of the all-volunteer Three Rivers fire district (La Push Road, Quillayute Prairie, Mora) to up to $1.50 per $1,000 for 2027 collection; the amount levied becomes the base for future levy limits.",
                  "Up to $1.50 per $1,000 of assessed value for 2027 collection; the amount levied becomes the base for later years.",
                  "https://voter.votewa.gov/elections/measure.ashx?m=7294&e=899&la=en&c=05",
                  pages=(62, 63)),
            ],
            "extra_notes": [
                "Public Utility District No. 1 of Clallam County Commissioner District No. 2 is scoped PUDALL '1': the whole "
                "PUD votes in the general (RCW 54.12.010(3)), and the City of Port Angeles is outside the PUD's commissioner "
                "districts; COUNTY_LAYERS.clallam reads PUD membership as any feature of the Auditor's "
                "PUD_Commissioner_District_dissolve layer.",
                "District Court 1 and District Court 2 are separate electoral districts, scoped DISTCRT '1' and '2' to the "
                "Auditor's District_Court layer, which COUNTY_LAYERS.clallam reads.",
            ],
        },
        # Cowlitz (#28). Measures: the county's general sample ballot and
        # local voters' pamphlet (counties/cowlitz/raw/cowlitz/
        # {sample-ballot,local-voters-pamphlet}.pdf.url, pamphlet pp. 57-58)
        # list one local measure; VoteWA's online guide for county 08 agrees.
        # CITY 'Longview': Census place at 1525 Broadway, Longview.
        # Overrides: the Commissioner, District Court and PUD seats are voted
        # county-wide in the general (RCW 36.32.040, RCW 54.12.010(3); SOS
        # results: 2024 Commissioner D2 56,821 votes of 59,822 ballots, 2022
        # District Court and PUD D3 about 30,400 each; DOR PUD2025 has one
        # Cowlitz polygon, DISTATTRIB '1'). The commissioner keeps the
        # primary's contest name so primary dossiers carry forward.
        "cowlitz": {
            "overrides": {
                ("COUNTY", "COMMISSIONER DISTRICT 3"): (
                    "County", "Cowlitz County Commissioner District 3", "Commissioner District 3", ("COUNTY", None)),
                ("DISTRICT COURT", "JUDGE POSITION 1"): (
                    "Judicial", "Cowlitz County District Court", "Judge Position No. 1", ("COUNTY", None)),
                ("DISTRICT COURT", "JUDGE POSITION 2"): (
                    "Judicial", "Cowlitz County District Court", "Judge Position No. 2", ("COUNTY", None)),
                ("DISTRICT COURT", "JUDGE POSITION 3"): (
                    "Judicial", "Cowlitz County District Court", "Judge Position No. 3", ("COUNTY", None)),
                ("PUBLIC UTILITY DISTRICT ALL", "COMMISSIONER DISTRICT 1"): (
                    "PublicUtility", "Public Utility District No. 1 of Cowlitz County", "Commissioner District 1",
                    ("COUNTY", None)),
            },
            "measures": [
                m("City of Longview", "Proposition 1", "Levy Lid Lift (Fire and Emergency Medical Services)",
                  ("CITY", "Longview"),
                  "Lifts Longview's regular property tax levy to hire firefighter paramedics/EMTs, replace aging equipment, buy a fire engine and build a third fire station; the 2027 levy becomes the base for future levy limits.",
                  "Raises the city's regular levy rate by $1.15 per $1,000 of assessed value beginning in 2027 (opponents: from $1.955 to $3.105).",
                  "https://voter.votewa.gov/elections/measure.ashx?m=7372&e=899&la=en&c=08",
                  pages=(57, 58)),
            ],
        },
        # Douglas (#30). Measures: the Auditor's general sample ballot
        # (counties/douglas/raw/douglas/sample-ballot.pdf.url, DocumentCenter
        # 13224, linked from douglascountywa.gov/206/Current-Election) lists
        # five local measures; VoteWA's online guide for county 09 (measures
        # 7283, 7320, 7321, 7425, 7322) agrees. Douglas prints no local
        # voters' pamphlet. Scopes point-checked 2026-10-08 (Census geocoder,
        # Current vintage; WA DOR 2025 layers 3 CEM, 11 HSP, 20 SCH):
        # 1206 Columbia Ave, Bridgeport and 50 Main St, Mansfield -> HSP2025
        # '1' (Three Rivers); 213 S Chelan Ave, Waterville -> HSP2025 '2' and
        # CEM2025 '2'; 100 Eastmont Ave, East Wenatchee and 1 Rock Island Dr,
        # Rock Island -> SCH2025 '206' (Waterville '209', Bridgeport '75').
        # The proposed Rimrock Meadows Fire Protection District No. 9 has no
        # DOR polygon (it does not exist until voters form it): PROPFIRDST
        # '009' (a key of its own, since COUNTY_LAYERS.douglas's FIRDST reads
        # DOR FIR2025 for the archived primary's FD 15 'J15') is the county's
        # own Fire Districts layer (gis.douglascountywa.gov/
        # server/rest/services/All_Districts_Temporary/MapServer/4 FireNumber
        # '009', 'Proposed Rimrock Meadows Fire District #9', edited
        # 2026-08-19); 1005 Ashcroft Dr, 431 Murcur Pl and 9005 W Coyote Trl,
        # Ephrata -> '009'; 448 Belmont Pl, Ephrata -> '001'. The formation
        # vote and its three commissioner races share that scope (RCW
        # 52.02.080).
        # Overrides: the commissioner race (District Type Countywide) is
        # nominated by district and elected county-wide in the general (RCW
        # 36.32.040; Douglas is a non-charter county; SOS 2024 general precinct
        # export: Commissioner 1 and 2 on all 49 precincts, 2022 Commissioner
        # 3 on all 49); it keeps the primary's contest name so primary
        # dossiers carry forward. The District Court seat is a single
        # county-wide judicial seat (2022: on all 49 precincts). Douglas
        # County PUD (Public Utility District No. 1 of Douglas County) covers
        # the county (DOR PUD2025 layer 17 has one Douglas polygon,
        # DISTATTRIB '1', at every point above) and the whole PUD elects each
        # commissioner in the general (RCW 54.12.010(3); its 2024 Commissioner
        # No. 1 race was on all 49 precincts), so the seat is COUNTY.
        "douglas": {
            "overrides": {
                ("COUNTY", "COMMISSIONER DISTRICT NO. 3"): (
                    "County", "Douglas County Commissioner District 3", "Commissioner District No. 3", ("COUNTY", None)),
                ("COUNTY", "DISTRICT COURT JUDGE"): (
                    "Judicial", "Douglas County District Court", "Judge", ("COUNTY", None)),
                ("DOUGLAS COUNTY PUBLIC UTILITY DISTRICT", "COMMISSIONER NO. 2"): (
                    "PublicUtility", "Public Utility District No. 1 of Douglas County", "Commissioner District 2",
                    ("COUNTY", None)),
                ("RIMROCK MEADOWS FIRE PROTECTION DISTRICT NO. 9", "COMMISSIONER NO. 1"): (
                    "Local", "Proposed Rimrock Meadows Fire Protection District No. 9", "Commissioner No. 1",
                    ("PROPFIRDST", "009")),
                ("RIMROCK MEADOWS FIRE PROTECTION DISTRICT NO. 9", "COMMISSIONER NO. 2"): (
                    "Local", "Proposed Rimrock Meadows Fire Protection District No. 9", "Commissioner No. 2",
                    ("PROPFIRDST", "009")),
                ("RIMROCK MEADOWS FIRE PROTECTION DISTRICT NO. 9", "COMMISSIONER NO. 3"): (
                    "Local", "Proposed Rimrock Meadows Fire Protection District No. 9", "Commissioner No. 3",
                    ("PROPFIRDST", "009")),
            },
            "measures": [
                m("Public Hospital District No. 1, Okanogan and Douglas Counties (Three Rivers Hospital)", "Proposition No. 1",
                  "Bonds for Hospital Renovation and Improvement",
                  ("HOSPDST", "1"),
                  "Authorizes up to $48,000,000 of general obligation bonds, maturing within 30 years and repaid by an excess property tax levy, to remodel, renovate, equip and improve Three Rivers Hospital in Brewster. Needs 60% yes.",
                  "Estimated $0.73 per $1,000 of assessed value (about $219 a year, or $18 a month, on a $300,000 home); up to $48,000,000 in bonds over up to 30 years.",
                  "https://voter.votewa.gov/elections/measure.ashx?m=7283&e=899&la=en&c=09"),
                m("Douglas County Public Hospital District No. 2", "Proposition No. 1",
                  "Special One-Year Excess Maintenance and Operations Levy",
                  ("HOSPDST", "2"),
                  "Authorizes a one-year excess levy for the Waterville-area hospital district, which runs its own ambulance service and a clinic contracted with Wenatchee Valley Medical Center.",
                  "$80,000, approximately $0.36 per $1,000 of assessed value, collected in 2027.",
                  "https://voter.votewa.gov/elections/measure.ashx?m=7320&e=899&la=en&c=09"),
                m("Eastmont School District No. 206", "Proposition No. 1",
                  "Bonds to Rebuild and Modernize Deteriorating Schools and Improve Safety",
                  ("SCHDST", "206"),
                  "Authorizes $125,000,000 of general obligation bonds, repaid by excess property taxes over up to 20 years, to rebuild the oldest parts of Cascade, Kenroy and Lee elementary schools (replacing 15 portables with permanent classrooms) and fund districtwide roofing, HVAC, lighting, parking, pickup and athletic-facility upgrades; the district expects about $25 million in state construction assistance. Needs 60% yes.",
                  "$125,000,000 in bonds over up to 20 years; the district estimates about $0.79 per $1,000 of assessed value (about $395 a year on a $500,000 home).",
                  "https://voter.votewa.gov/elections/measure.ashx?m=7321&e=899&la=en&c=09"),
                m("Proposed Rimrock Meadows Fire Protection District No. 9", "Proposition No. 1",
                  "Formation of Rimrock Meadows Fire Protection District No. 9",
                  ("PROPFIRDST", "009"),
                  "Forms a fire protection district (RCW 52.02) for the Rimrock Meadows area (Ephrata mailing addresses), which has no fire district today, governed by three elected commissioners and financed by a property tax levy. The commissioner races on the same ballot fill its first board if it forms.",
                  "No levy is set by this vote; once formed, the district's board may levy regular property taxes for fire protection (up to $0.50 per $1,000 under RCW 52.16.130, with further $0.50 levies under RCW 52.16.140 and .160 subject to the statutory limits).",
                  "https://voter.votewa.gov/elections/measure.ashx?m=7425&e=899&la=en&c=09"),
                m("Douglas County Cemetery District No. 2", "Proposition No. 1",
                  "Special One-Year Excess Maintenance and Operations Levy",
                  ("CEMDST", "2"),
                  "Authorizes the cemetery district's one-year excess levy for maintenance, operations and irrigation of its seven cemeteries and one mausoleum around Waterville.",
                  "$50,000, approximately $0.22 per $1,000 of assessed value, collected in 2027.",
                  "https://voter.votewa.gov/elections/measure.ashx?m=7322&e=899&la=en&c=09"),
            ],
            "extra_notes": [
                "Douglas County prints no local voters' pamphlet for the general; candidate statements and measure "
                "texts are in VoteWA's online voters' guide (genericvoterguide.aspx?e=899&c=09).",
                "The proposed Rimrock Meadows Fire Protection District No. 9 and its commissioner races are scoped to "
                "PROPFIRDST '009', the county's Fire Districts layer (FireNumber '009'); DOR's 2025 fire layer has no such district.",
            ],
        },
        # Franklin (#29). Ballot checked against the Auditor's general sample
        # ballot and local voters' pamphlet (counties/franklin/raw/franklin/
        # sample-ballot.pdf.url, local-voters-pamphlet.pdf.url): one local
        # measure, Fire Protection District No. 3 Proposition No. 1.
        # FIRDST: WA DOR FIR2025 (layer 7) DISTATTRIB '3' at 5600 N Rd 68,
        # Pasco (2026-10-08); the Auditor's precinct-split layer
        # (gisportal.franklin.co.franklin.wa.us/arcgis2/rest/services/districts/
        # Voting_Precinct_Group/FeatureServer/12) agrees there (FIRE 'FPD3').
        # Commissioner District 3 keeps the generic scope (COUNTY_COUNCIL
        # 'COM3'): Franklin elects commissioners by district in the general
        # since 2024 (SOS 2024 general precinct export: District 1 on 48 and
        # District 2 on 31 of 123 precincts; the 2026 primary's District 3 on
        # 44 of 123 reporting units). Overrides: the District Court seat is a
        # single county-wide judicial seat (VoteWA District Type 'Countywide');
        # Franklin PUD No. 1 covers the whole county and the whole PUD elects
        # each commissioner (its 2024 District 3 race was on all 123
        # precincts; RCW 54.12.010(3)), so the seat is COUNTY; the Port of
        # Pasco moved to by-district general elections from 2026 (NonStop
        # Local, 2025-10-03; Port Resolution 1577 on the county's port layer),
        # so its seat is PORTDST 'PoP3' (Special_tax_districts/MapServer/7
        # DISTRICT_CODE; 5600 N Rd 68, Pasco and 103 Franklin St, Mesa ->
        # 'PoP3'; 1016 N 4th Ave, Pasco -> 'PoP1'). The Port of Pasco is not
        # the whole county: the Port of Kahlotus covers the east end.
        "franklin": {
            "overrides": {
                ("COUNTY", "DISTRICT COURT JUDGE"): (
                    "Judicial", "Franklin County District Court", "Judge", ("COUNTY", None)),
                ("PUD DISTRICT 2", "COMMISSIONER DISTRICT 2"): (
                    "PublicUtility", "Public Utility District No. 1 of Franklin County", "Commissioner District 2",
                    ("COUNTY", None)),
                ("PASCO PORT DISTRICT 3", "COMMISSIONER, DISTRICT 3"): (
                    "Port", "Port of Pasco", "Commissioner District 3", ("PORTDST", "PoP3")),
            },
            "measures": [
                m("Franklin County Fire Protection District No. 3", "Proposition No. 1",
                  "Authorization for a Single-Year Permanent Levy Lid Lift",
                  ("FIRDST", "3"),
                  "Raises the fire district's regular property tax levy to fund district operations, including emergency medical (ambulance) services; the 2027 levy becomes the base for later years' limits.",
                  "$1.24 per $1,000 of assessed value for assessment in 2026 and collection in 2027 (the district says its current rate is $0.86).",
                  "https://www.franklincountywa.gov/DocumentCenter/View/4553/2611-Franklin-County-Voters-Pamphlet-",
                  pages=(16,)),
            ],
            "extra_notes": [
                "Franklin County Commissioner District 3 is elected by district in the general (VoteWA District "
                "'COUNTY COMMISSION DISTRICT 3'; SOS 2024 general precinct results; 2026 primary results on 44 of "
                "123 reporting units).",
                "The Port of Pasco Commissioner District 3 race is elected by district from 2026 (Port of Pasco "
                "by-district elections, NonStop Local 2025-10-03).",
            ],
        },
        # Grant (#28). Measures: Grant County Elections' November 2026 sample
        # ballot (raw/grant/sample-ballot.pdf.url, DocumentCenter 16964, linked
        # from grantcountywa.gov/1374/Current-Election) and VoteWA's online
        # voters' guide (voterguide.ashx?e=899&c=13, read 2026-10-08) both list
        # five local measures. Scopes point-checked 2026-10-08 (Census
        # geocoder, Current vintage; WA DOR 2025 layers 3 CEM, 7 FIR, 11 HSP):
        # 321 S Balsam St, Moses Lake -> CITY 'Moses Lake'; 127 Main Ave E,
        # Soap Lake -> HSP2025 DISTATTRIB '4'; 34875 Park Lake Rd NE, Coulee
        # City -> FIR2025 '7'; 103 Railroad St, Wilson Creek -> CEM2025 '2'.
        # Overrides: VoteWA files the commissioner race as Countywide (elected
        # county-wide in the general, RCW 36.32.040); it keeps the primary's
        # contest name so primary dossiers carry forward. The District Court
        # seats (District Type Countywide) are judicial seats of one
        # county-wide court. Grant County PUD (Public Utility District No. 2
        # of Grant County) is county-wide (DOR PUD2025 layer 17 has a single
        # Grant polygon, DISTATTRIB '2', at Moses Lake, Soap Lake, Coulee
        # City, Grand Coulee and Wilson Creek alike) and the whole PUD elects
        # each commissioner in the general (RCW 54.12.010(3)), so its rows
        # (District 'Grant County PUD All', which classify() cannot number)
        # are scoped COUNTY.
        "grant": {
            "overrides": {
                ("COUNTY", "COMMISSIONER DISTRICT #3"): (
                    "County", "Grant County Commissioner District 3", "Commissioner District #3", ("COUNTY", None)),
                ("COUNTY", "DISTRICT COURT JUDGE #1"): (
                    "Judicial", "Grant County District Court", "Judge Position No. 1", ("COUNTY", None)),
                ("COUNTY", "DISTRICT COURT JUDGE #2"): (
                    "Judicial", "Grant County District Court", "Judge Position No. 2", ("COUNTY", None)),
                ("COUNTY", "DISTRICT COURT JUDGE #3"): (
                    "Judicial", "Grant County District Court", "Judge Position No. 3", ("COUNTY", None)),
                ("GRANT COUNTY PUD ALL", "COMMISSIONER DIST #3"): (
                    "PublicUtility", "Public Utility District No. 2 of Grant County", "Commissioner District 3",
                    ("COUNTY", None)),
                ("GRANT COUNTY PUD ALL", "COMMISSIONER DIST #B AL"): (
                    "PublicUtility", "Public Utility District No. 2 of Grant County", "Commissioner District B (At Large)",
                    ("COUNTY", None)),
            },
            "measures": [
                m("Grant County", "Advisory Vote Only - Proposition No. 1",
                  "Sales and Use Tax for Mental Health or Chemical Dependency Treatment or Therapeutic Courts",
                  ("COUNTY", None),
                  "Advisory vote: asks whether the county commissioners should adopt a 0.1% sales and use tax (RCW 82.14.460) for chemical dependency and mental health treatment and therapeutic courts. The vote does not itself impose the tax; the board may decide afterwards.",
                  "If the board later adopts it: 0.1% sales and use tax (one cent on a $10 purchase), county-wide.",
                  "https://voter.votewa.gov/elections/measure.ashx?m=7349&e=899&la=en&c=13"),
                m("Grant County Public Hospital District No. 4 (McKay Healthcare & Rehabilitation)", "Proposition No. 1",
                  "Bonds for Expansion of McKay Healthcare & Rehabilitation Center",
                  ("HOSPDST", "4"),
                  "Authorizes up to $9,940,000 of general obligation bonds, maturing within 30 years and repaid by an excess property tax levy, to add a 16-bed assisted living unit, a 16-bed memory care unit and other capital improvements at McKay Healthcare & Rehabilitation Center in Soap Lake.",
                  "Estimated $0.61 per $1,000 of assessed value (about $15.27 a month on a $300,000 home); up to $9,940,000 in bonds.",
                  "https://voter.votewa.gov/elections/measure.ashx?m=7343&e=899&la=en&c=13"),
                m("City of Moses Lake", "Proposition No. 1", "Public Safety Sales and Use Tax",
                  ("CITY", "Moses Lake"),
                  "Raises the city's sales and use tax by 0.1% (RCW 82.14.450) for public safety: police staffing and retention, operations, maintenance and capital, and other criminal justice services.",
                  "0.1% sales and use tax (one cent on a $10 purchase); about $1.2 million in 2027.",
                  "https://voter.votewa.gov/elections/measure.ashx?m=7347&e=899&la=en&c=13"),
                m("Grant County Fire Protection District No. 7", "Proposition No. 1", "Emergency Medical Service Property Tax Levy",
                  ("FIRDST", "7"),
                  "Replaces the last two years of the district's 2022 EMS levy (up to $0.25, suspended in 2024) with a six-year EMS levy first levied in 2026 for collection from 2027.",
                  "Up to $0.50 per $1,000 of assessed value (no more than $150 a year on a $300,000 home).",
                  "https://voter.votewa.gov/elections/measure.ashx?m=7348&e=899&la=en&c=13"),
                m("Grant County Cemetery District No. 2 (Wilson Creek)", "Proposition No. 1", "Special Levy for Maintenance and Operations",
                  ("CEMDST", "2"),
                  "Authorizes the cemetery district's yearly one-year special levy for maintenance and operations of the Wilson Creek cemetery, collected in 2027.",
                  "$12,000, approximately $0.18 per $1,000 of assessed value, collected in 2027.",
                  "https://voter.votewa.gov/elections/measure.ashx?m=7346&e=899&la=en&c=13"),
            ],
        },
        # Grays Harbor (#29). Measures: VoteWA's online voters' guide for county
        # 14 (voterguide.ashx?e=899&c=14, read 2026-10-08; raw pointers under
        # counties/grays-harbor/raw/votewa/voter-guide/) lists five local
        # measures. The Auditor's Current Election page links no printed local
        # pamphlet or sample ballot, only VoteWA and a District Court
        # supplement. Scopes point-checked 2026-10-08 (Census geocoder,
        # Current vintage; WA DOR 2025 layers 7 FIR, 12 LIB, 20 SCH):
        # 112 N Main St, Montesano -> CITY 'Montesano'; 200 W Market St,
        # Aberdeen, 609 8th St, Hoquiam, 112 N Main St, Montesano, 100 S 3rd
        # St, McCleary and 506 S Montesano St, Westport -> LIB2025 'L'
        # (Timberland), but 585 Point Brown Ave NW, Ocean Shores -> none (the
        # city runs its own library), so the TRL levy is LIBDST, not COUNTY;
        # 100 S 3rd St, McCleary -> SCH2025 '65'; 110 Main St, Oakville ->
        # FIR2025 '1'; 500 Wynoochee Valley Rd, Montesano -> FIR2025 '2'.
        # COUNTY_LAYERS['grays-harbor'] reads LIB2025 and SCH2025 since #29.
        # Overrides: the commissioner race (District Type Countywide) is
        # elected county-wide in the general (RCW 36.32.040; SOS 2024 results:
        # Commissioner #1 36,166 votes of 38,102 ballots); it keeps the
        # primary's contest name so primary dossiers carry forward. District
        # Court #1 and #2 are seats of one county-wide court (2022: #1 24,257
        # votes of 29,916 ballots). Grays Harbor PUD No. 1 covers the county
        # (DOR PUD2025 layer 17 has one Grays Harbor polygon, DISTATTRIB '1',
        # at Aberdeen, Hoquiam, Montesano, McCleary, Ocean Shores and
        # Westport) and the whole PUD elects each commissioner in the general
        # (RCW 54.12.010(3); 2022 uncontested PUD Comm (2) 18,505 votes, as
        # many as the uncontested county-wide District Court #2's 18,521).
        "grays-harbor": {
            "overrides": {
                ("COUNTY", "COMMISSIONER #3"): (
                    "County", "Grays Harbor County Commissioner District 3", "Commissioner #3", ("COUNTY", None)),
                ("COUNTY", "DISTRICT COURT #1"): (
                    "Judicial", "Grays Harbor County District Court", "Judge Position No. 1", ("COUNTY", None)),
                ("COUNTY", "DISTRICT COURT #2"): (
                    "Judicial", "Grays Harbor County District Court", "Judge Position No. 2", ("COUNTY", None)),
                ("PUD DISTRICT", "PUD COMM (3)"): (
                    "PublicUtility", "Public Utility District No. 1 of Grays Harbor County", "Commissioner District 3",
                    ("COUNTY", None)),
            },
            "measures": [
                m("Timberland Regional Library District", "Proposition No. 1",
                  "Regular Property Tax Levy Lid Lift for Library Services, Operations and Maintenance",
                  ("LIBDST", "L"),
                  "Restores the library district's regular property tax levy from about $0.22 to $0.35 per $1,000 of assessed value for 2027 and 2028; the 2028 amount becomes the base for later levy limits.",
                  "$0.35 per $1,000 of assessed value (about $40 a year more on a $334,000 home, per the explanatory statement).",
                  "https://voter.votewa.gov/elections/measure.ashx?m=7284&e=899&la=en&c=14"),
                m("City of Montesano", "Proposition No. 1",
                  "Levy to Maintain Essential Services, Public Safety and Emergency Services, Operations and Capital Improvements",
                  ("CITY", "Montesano"),
                  "Lifts Montesano's regular property tax levy to a total rate of up to $3.22 per $1,000 from 2027, with up to 5% yearly increases for six years, to keep current General Fund and public safety and emergency service levels.",
                  "Total city regular levy up to $3.22 per $1,000 of assessed value for 2027 collection.",
                  "https://voter.votewa.gov/elections/measure.ashx?m=7377&e=899&la=en&c=14"),
                m("McCleary School District No. 65", "Proposition No. 1",
                  "Bonds to Improve Safety, Security and School Facilities",
                  ("SCHDST", "65"),
                  "Authorizes $12,800,000 of general obligation bonds, maturing within 21 years and repaid by excess property taxes, for a secure entry vestibule, locks and keycard access, fire alarm, HVAC, exterior, drainage, parking and playground work at McCleary School.",
                  "$12,800,000 in bonds repaid by an excess property tax levy over up to 21 years.",
                  "https://voter.votewa.gov/elections/measure.ashx?m=7385&e=899&la=en&c=14"),
                m("Grays Harbor County Fire Protection District No. 1", "Proposition No. 1", "Emergency Medical Services Levy",
                  ("FIRDST", "1"),
                  "Authorizes a permanent regular property tax levy for emergency medical services.",
                  "Up to $0.50 per $1,000 of assessed value, permanent.",
                  "https://voter.votewa.gov/elections/measure.ashx?m=7387&e=899&la=en&c=14"),
                m("Grays Harbor County Fire Protection District No. 2", "Proposition No. 1", "Two Year Levy Lid Lift",
                  ("FIRDST", "2"),
                  "Restores the fire district's regular property tax levy to $1.50 per $1,000 (from about $1.40 in 2026) for 2026 and 2027 levies; the 2027 amount becomes the base for later levy limits.",
                  "$1.50 per $1,000 of assessed value.",
                  "https://voter.votewa.gov/elections/measure.ashx?m=7386&e=899&la=en&c=14"),
            ],
        },
        # Island (#29). Measures: the Island County Auditor's general sample
        # ballot (counties/island/raw/island/sample-ballot.pdf.url) and VoteWA's
        # online voters' guide for county 15 (raw/votewa/voter-guide/), which the
        # Auditor links as its online voters' guide, list three local measures.
        # Scopes point-checked 2026-10-09 (Census geocoder, Current vintage):
        # - CITY: Census place 'Langley' at 112 2nd St, Langley.
        # - PORTDST: WA DOR PRT2025 (layer 16) DISTATTRIB 'S WHIDBEY' at 112 2nd
        #   St, Langley and 5476 Harbor Rd, Freeland; no feature at 865 SW
        #   Barrington Dr, Oak Harbor or 848 N Sunrise Blvd, Camano Island.
        # - UNINC (unincorporated Island County): WA DOR TCA2025 (layer 23)
        #   COUNTYNAME 'ISLAND' with where DISTATTRIB NOT IN ('0100', '0300',
        #   '0700'). Those three tax code areas are Oak Harbor, Coupeville and
        #   Langley: the only Island TCAs that intersect the Census incorporated
        #   places apart from the surrounding unincorporated TCAs 0110, 0160,
        #   0310 and 0710, which touch them only at their edges, and the county's
        #   Tax Codes layer gives TCA 0100 the fire district 'City of Oak Harbor'.
        #   Live: 865 SW Barrington Dr (Oak Harbor) 0100, 1 7th St NE (Coupeville)
        #   0300, 112 2nd St (Langley) 0700; 5476 Harbor Rd, Freeland 0760, 2795
        #   Heller Rd, Oak Harbor (unincorporated) 0110, 848 N Sunrise Blvd,
        #   Camano 0590.
        # COUNTY_LAYERS.island reads PUDDST, PORTDST and UNINC with exactly
        # these configs since #29 (live-checked again 2026-10-08).
        # Overrides: the PUD race is Snohomish County PUD No. 1's District 1
        # seat, which Camano Island voters elect with all of Snohomish County
        # (RCW 54.12.010(3)). It keeps the Snohomish package's names, so it ships
        # with Snohomish's research, and is scoped to Camano Island's precincts:
        # PUDDST '53029', the County attribute of the Auditor's precinct layer
        # (Geocortex/Elections/MapServer/2) with where PrecinctNa LIKE 'Camano%'
        # (precincts Camano 01-21; live 2026-10-09: 848 N Sunrise Blvd -> Camano
        # 01; Oak Harbor, Coupeville, Freeland -> no Camano precinct). The
        # District Court seat is a single county-wide district, named as the
        # Whatcom block names its seats.
        "island": {
            "overrides": {
                ("COUNTY", "DISTRICT COURT JUDGE"): (
                    "Judicial", "Island County District Court", "Judge", ("COUNTY", None)),
                ("PUBLIC UTILITY DISTRICT NO. 1", "COMMISSIONER DISTRICT 1"): (
                    "PublicUtility", "Public Utility District No. 1", "Commissioner District 1",
                    ("PUDDST", "53029")),
            },
            "measures": [
                m("Unincorporated Island County", "Advisory Vote", "Advisory Vote Regarding the Use of Consumer Fireworks in Unincorporated Island County",
                  ("UNINC", "ISLAND"),
                  "Non-binding advisory vote: asks voters in unincorporated Island County whether the Board of County Commissioners should amend Island County Code Chapter 9.08A to ban consumer fireworks there. Permitted public displays are not affected.",
                  "No tax or fee; the vote does not change the law.",
                  "https://voter.votewa.gov/elections/measure.ashx?m=7304&e=899&la=en&c=15"),
                m("City of Langley", "Proposition No. 1", "Governmental Services and Technology Levy",
                  ("CITY", "Langley"),
                  "Permanently lifts Langley's regular property tax levy to fund continuing city services and update its operating and electronic technology, with the senior and disability exemption.",
                  "Up to $1.66 per $1,000 of assessed value for 2027 collection, $0.65 more than the current $1.01; about $42 a month on a $770,000 home.",
                  "https://voter.votewa.gov/elections/measure.ashx?m=7305&e=899&la=en&c=15"),
                m("Port District of South Whidbey Island", "Proposition No. 1", "Levy for Renovation and Modernization of Port Facilities",
                  ("PORTDST", "S WHIDBEY"),
                  "Lifts the port district's regular property tax levy to renovate and modernize port facilities, including the fairgrounds and waterfront, and support economic development and its small business incubator.",
                  "Up to $0.169 per $1,000 of assessed value for 2027 collection, six cents more than the current $0.109.",
                  "https://voter.votewa.gov/elections/measure.ashx?m=7306&e=899&la=en&c=15"),
            ],
        },
        # Lewis (#29): checked against the Lewis County Auditor's general sample
        # ballot (counties/lewis/raw/lewis/sample-ballot.pdf.url) and VoteWA's
        # online guide for county 21 (raw/votewa/voter-guide/guide.json.url),
        # which list three local measures; text from the guide's measure records.
        # Commissioner District 3: nominated by district, elected county-wide in
        # the general (RCW 36.32.040; VoteWA's general export lists it as
        # 'Countywide'; the SOS 2020-11-03 Lewis precinct export has the District
        # 1 and 2 races in all 96 precincts). Named as in the primary so its
        # dossiers carry forward. District Court: one county-wide district, two
        # departments. The PUD seat (District 'PUD DISTRICT-AT-LARGE') keeps the
        # generic rule's names, so its slug and dossiers are unchanged, and is
        # scoped PUDDST '1': Lewis County PUD No. 1 is the county minus the City
        # of Centralia (the PUD races of 2020, 2022 and 2024 were on no
        # Centralia precinct; DOR PUD2025 layer 17 and the county's
        # VotingTaxingDistricts MapServer layer 8 both return no feature at 118
        # W Maple St, Centralia, and DISTATTRIB '1' at 351 NW North St,
        # Chehalis). COUNTY_LAYERS.lewis reads DOR PUD2025 since #29.
        # Measure scopes, point-checked 2026-10-09 (Census geocoder, Current):
        # LIBDST 'L': DOR LIB2025 (layer 12) at Chehalis, Centralia, Morton,
        # Toledo, Winlock and 2152 Jackson Hwy (unincorporated); Pe Ell (200 S
        # Main St), Mossyrock (243 E State St), Napavine (105 2nd Ave NW) and
        # Vader (509 A St) return no feature, so the measure is not county-wide.
        # COUNTY_LAYERS.lewis reads DOR LIB2025 since #29.
        # CITY 'Chehalis': Census place at 351 NW North St (the TBD's board is the
        # Chehalis City Council). FIRDST '6': DOR FIR2025 (layer 7) DISTATTRIB
        # '6' at 2152 Jackson Hwy, Chehalis (county Precinct Splits layer 12:
        # 'Lewis County FD #6').
        "lewis": {
            "overrides": {
                ("COUNTY", "COUNTY COMMISSIONER, DISTRICT 3"): (
                    "County", "Lewis County Commissioner District 3", "County Commissioner, District 3",
                    ("COUNTY", None)),
                ("DISTRICT COURT", "DISTRICT COURT JUDGE, DEPT 1"): (
                    "Judicial", "Lewis County District Court", "District Court Judge, Dept 1", ("COUNTY", None)),
                ("DISTRICT COURT", "DISTRICT COURT JUDGE, DEPT 2"): (
                    "Judicial", "Lewis County District Court", "District Court Judge, Dept 2", ("COUNTY", None)),
                ("PUD DISTRICT-AT-LARGE", "COMMISSIONER DISTRICT 1"): (
                    "PublicUtility", "Public Utility District Commissioner District 1", "Commissioner District 1",
                    ("PUDDST", "1")),
            },
            "measures": [
                m("Timberland Regional Library District", "Proposition No. 1",
                  "Regular Property Tax Levy Lid Lift for Library Services, Operations and Maintenance",
                  ("LIBDST", "L"),
                  "Restores the Timberland Regional Library District's regular property tax levy from $0.22 to $0.35 per $1,000 of assessed value for 2027 and 2028; the 2028 levy amount becomes the base for later limits (chapter 84.55 RCW).",
                  "From $0.228924 to $0.35 per $1,000 of assessed value in 2027 and 2028; about $40.44 a year on a $334,000 home, per the explanatory statement.",
                  "https://voter.votewa.gov/elections/measure.ashx?m=7284&e=899&la=en&c=21"),
                m("Transportation Benefit District of Chehalis", "Proposition No. 1",
                  "Sales and Use Tax Levy Renewal For Transportation Needs",
                  ("CITY", "Chehalis"),
                  "Renews the Chehalis Transportation Benefit District's 0.2% sales and use tax for ten years (July 1, 2027 to June 30, 2037) for street, bridge and transportation improvements, traffic engineering and street maintenance.",
                  "0.2% sales and use tax (20 cents on each $100 of taxable purchases), the current rate, renewed for ten years.",
                  "https://voter.votewa.gov/elections/measure.ashx?m=7365&e=899&la=en&c=21"),
                m("Lewis County Fire Protection District No. 6", "Proposition No. 1", "Levy Lid Lift",
                  ("FIRDST", "6"),
                  "Sets Fire District 6's regular property tax levy at $1.15 per $1,000 of assessed value for 2027 collection, for fire protection, life safety services, apparatus and equipment, and firefighter safety; that amount becomes the base for later limits.",
                  "$1.15 per $1,000 of assessed value for 2027 collection; the district says its 2026 rate is about $0.79 and would be about $0.99 without the measure.",
                  "https://voter.votewa.gov/elections/measure.ashx?m=7366&e=899&la=en&c=21"),
            ],
            "extra_notes": [
                "Timberland Regional Library District Proposition No. 1 is scoped LIBDST 'L' (WA DOR LIB2025, layer 12). "
                "Pe Ell, Mossyrock, Napavine and Vader are outside the district, so it is not county-wide; "
                "COUNTY_LAYERS.lewis reads LIB2025.",
                "Lewis County PUD No. 1 excludes the City of Centralia; its at-large Commissioner District 1 seat is "
                "scoped PUDDST '1' (WA DOR PUD2025, layer 17, DISTATTRIB '1'), which COUNTY_LAYERS.lewis reads.",
            ],
        },
        # Skagit: the four measures the Auditor's Ballot Measures page lists
        # for the general (counties/skagit/raw/skagit/ballot-measures.html.url),
        # text from the local voters' pamphlet pages 18-21 and VoteWA
        # measures 7426-7429. Scope values point-checked 2026-10-08 (Census
        # geocoder + DOR WADOR_PropertyTax layers 7 and 20).
        "skagit": {"measures": [
            # 700 S 2nd St, Mount Vernon -> Census place 'Mount Vernon city'.
            m("City of Mount Vernon", "Proposition No. 1",
              "Renewal of Sales and Use Tax for Transportation Improvements (Mount Vernon Transportation Benefit District)",
              ("CITY", "Mount Vernon"),
              "Renews the Mount Vernon Transportation Benefit District's 0.2% sales and use tax for ten more years to pay for street repair, preservation and other transportation improvements in the city.",
              "0.2% sales and use tax (2 cents on $10), about $2.3 million a year; the current tax ends in April 2027 unless renewed.",
              "https://voter.votewa.gov/elections/measure.ashx?m=7426&e=899&la=en&c=29",
              pages=(18,)),
            # 325 Metcalf St, Sedro-Woolley -> Census place 'Sedro-Woolley city'.
            m("City of Sedro-Woolley", "Proposition No. 1",
              "Annexation into Central Skagit Rural Partial-County Library District",
              ("CITY", "Sedro-Woolley"),
              "Annexes the City of Sedro-Woolley into the Central Skagit Rural Partial-County Library District, replacing the city's contract for library service with district membership.",
              "District levy estimated at $0.232 per $1,000 of assessed value from 2028; the city plans to cut its own levy by up to $474,115, a net increase of about $11 in 2028 on a $519,450 home.",
              "https://voter.votewa.gov/elections/measure.ashx?m=7427&e=899&la=en&c=29",
              pages=(19,)),
            # 305 N 6th St, La Conner -> DOR SCH2025 (layer 20) DISTATTRIB '311'.
            m("La Conner School District No. 311", "Proposition No. 1",
              "Educational Facility Modernization and Technology Levy",
              ("SCHDST", "311"),
              "Authorizes a four-year capital levy to modernize existing school buildings and replace and upgrade technology systems.",
              "$350,000 to $395,000 a year for 2027 through 2030 ($1,490,000 total), about $0.31 per $1,000 of assessed value.",
              "https://voter.votewa.gov/elections/measure.ashx?m=7428&e=899&la=en&c=29",
              pages=(20,)),
            # 5800 Main St, Bow (Edison) -> DOR FIR2025 (layer 7) DISTATTRIB '5'.
            m("Skagit County Fire Protection District No. 5", "Proposition No. 1",
              "Authorizing Regular Property Tax Levy",
              ("FIRDST", "5"),
              "Restores the fire district's regular property tax levy to $0.78 per $1,000 and lets it grow up to 3% a year for five years (Allen, Bow, Edison, Samish Island, Chuckanut Drive).",
              "$0.78 per $1,000 of assessed value in 2027, then up to 3% more a year (never above $1.50).",
              "https://voter.votewa.gov/elections/measure.ashx?m=7429&e=899&la=en&c=29",
              pages=(21,)),
        ]},
        # Whatcom (#28). Measures: VoteWA's online voters' guide for Whatcom
        # County (voterguide.ashx?e=899&c=37, read 2026-10-08) lists five local
        # measures; whatcomcounty.us answered 403 (Cloudflare) to scripted
        # requests, so the Auditor's own list could not be cross-checked.
        # Scopes point-checked 2026-10-08 (Census geocoder, Current vintage;
        # WA DOR FIR2025 layer 7): 210 Lottie St, Bellingham -> CITY
        # 'Bellingham'; 300 4th St, Lynden -> CITY 'Lynden'; 111 W Main St,
        # Everson -> FIR2025 DISTATTRIB '1'.
        # Overrides: the Port of Bellingham and Whatcom PUD No. 1 are
        # county-wide districts (DOR PRT2025/PUD2025 each have one Whatcom
        # polygon, at Point Roberts, Glacier, Newhalem, Bellingham and Sumas
        # alike), and the whole district elects each commissioner in the
        # general (RCW 53.12.010(1), RCW 54.12.010(3)), so both are scoped
        # COUNTY. The port seats keep the primary's contest names so primary
        # dossiers carry forward. VoteWA files the District Court seats as
        # District Type 'Countywide'; they are judicial seats of a single
        # county-wide district, named as the other county builders name them.
        "whatcom": {
            "overrides": {
                ("COUNTY", "DISTRICT COURT JUDGE POSITION 1"): (
                    "Judicial", "Whatcom County District Court", "Judge Position No. 1", ("COUNTY", None)),
                ("COUNTY", "DISTRICT COURT JUDGE POSITION 2"): (
                    "Judicial", "Whatcom County District Court", "Judge Position No. 2", ("COUNTY", None)),
                ("PORT OF BELLINGHAM", "COMMISSIONER DISTRICT 4"): (
                    "Port", "Port of Bellingham Commissioner District 4", "Commissioner District 4", ("COUNTY", None)),
                ("PORT OF BELLINGHAM", "COMMISSIONER DISTRICT 5"): (
                    "Port", "Port of Bellingham Commissioner District 5", "Commissioner District 5", ("COUNTY", None)),
                ("PUBLIC UTILITY DISTRICT NO. 1", "COMMISSIONER DISTRICT 1"): (
                    "PublicUtility", "Public Utility District No. 1 of Whatcom County", "Commissioner District 1",
                    ("COUNTY", None)),
            },
            "measures": [
                m("City of Bellingham", "Proposition 2026-06", "Authorizing the City's Salary Commission to Set the Mayor's Salary",
                  ("CITY", "Bellingham"),
                  "Charter amendment: removes the rule that the mayor's salary is never less than the highest-paid city official or employee, and has the city's independent salary commission set it.",
                  "No tax or fee; changes how the mayor's salary is set.",
                  "https://voter.votewa.gov/elections/measure.ashx?m=7295&e=899&la=en&c=37"),
                m("City of Bellingham", "Proposition 2026-07", "Streamlining the City's Contract Review Process to Allow Electronic Signatures",
                  ("CITY", "Bellingham"),
                  "Charter amendment: lets the mayor's designee sign city contracts, allows electronic signatures, and drops the finance director's attestation and seal.",
                  "No tax or fee; changes how city contracts are signed.",
                  "https://voter.votewa.gov/elections/measure.ashx?m=7297&e=899&la=en&c=37"),
                m("City of Bellingham", "Initiative 26-01", "Prohibition of Algorithmic Price-Fixing in the Rental Market",
                  ("CITY", "Bellingham"),
                  "Citizen initiative: bans landlord rent-setting agreements and paid algorithmic services that recommend rents or terms to multiple landlords, with a private right of action, tenant and employee anti-retaliation protections, and civil and criminal penalties.",
                  "No tax or fee; enforcement by the City Attorney and private lawsuits.",
                  "https://voter.votewa.gov/elections/measure.ashx?m=7298&e=899&la=en&c=37"),
                m("City of Lynden", "Proposition 2026-05", "Levy Lid Lift for Public Safety and Essential Community Services",
                  ("CITY", "Lynden"),
                  "Lifts Lynden's regular property tax levy for police, fire, streets, parks, the Community/Senior Center, restored staff positions and Friday City Hall hours, with 3% annual increases for 2027-2035.",
                  "Up to $1.54304 per $1,000 of assessed value for 2027 collection, $0.50 per $1,000 more than the 2025 levy rate.",
                  "https://voter.votewa.gov/elections/measure.ashx?m=7299&e=899&la=en&c=37"),
                m("Whatcom County Fire Protection District No. 1", "Proposition 2026-08", "Regular Property Tax Levy Lid Lift",
                  ("FIRDST", "1"),
                  "Resets the fire district's regular levy for fire and EMS (Everson/Nooksack area) with a 106% limit factor for the following nine years.",
                  "Up to $1.48 per $1,000 of assessed value for 2027 collection; the district says its current rate is $1.12.",
                  "https://voter.votewa.gov/elections/measure.ashx?m=7300&e=899&la=en&c=37"),
            ],
        },
        # Yakima (#28): no local measures. The Auditor's "Election at a glance"
        # (raw/yakima/election-at-a-glance-2026-general.pdf.url) lists only the
        # three statewide measures, and so do the sample ballot and VoteWA's
        # online guide for county 39 (raw/votewa/voter-guide/guide.json.url).
        "yakima": {
            "measures": [],
            "extra_notes": [
                "No local measures on the November 3, 2026 ballot: Yakima County's 'Election at a glance' "
                "(https://www.yakimacounty.us/DocumentCenter/View/46553/2026-GENERAL-at-a-glance_ENG) and "
                "sample ballot (https://www.yakimacounty.us/DocumentCenter/View/46525/Sample-Ballot-2026-General) "
                "list only the statewide measures IP26-645, IL26-001 and IL26-638.",
                "County Commissioner District 1 is elected by district in the general (candidates appear only on "
                "ballots within their commissioner district; Aguilar et al. v. Yakima County, Final Order October "
                "2021, RCW 36.32.040(3); 2026 Candidate & Election Guidebook p. 19).",
            ],
        },
    },
}


def config_for(county, election_id):
    """COUNTY_CONFIG's geography (name, scope formats) plus this election's
    measures and notes. Returns (cfg, measures_curated)."""
    cfg = dict(COUNTY_CONFIG[county])
    if election_id not in ELECTION_MEASURES:
        return cfg, True
    per = ELECTION_MEASURES[election_id].get(county)
    cfg["measures"] = list(per["measures"]) if per else []
    cfg["extra_notes"] = list(per.get("extra_notes", [])) if per else []
    cfg["overrides"] = dict(per.get("overrides", {})) if per else {}
    return cfg, per is not None


def county_docs(county, cfg, election_id, measures_curated=True):
    """(app-contests doc, app-measures doc, unresolvable layers) without writing."""
    unresolvable = set()
    rows = votewa.ballot_rows(election_id, county)
    # Per-election overrides: {(District, Race) upper-cased: classify()-shaped tuple}.
    overrides = cfg.get("overrides") or {}
    override = (lambda r, _u: overrides.get((r["District"].strip().upper(), r["Race"].strip().upper()))) if overrides else None
    raw_contests = votewa.parse_contests(rows, county, cfg, unresolvable, override)
    label = election.VOTEWA_SOURCES[election_id]["label"]
    out_contests = votewa.app_contests(
        county, raw_contests,
        f"Official ballot listing imported from the VoteWA {label} candidate list for {cfg['name']}. "
        "Candidate scoring is not complete for this county yet.",
    )

    out_measures = []
    for mm in cfg["measures"]:
        prop = mm["proposition"] or "Ballot Measure"
        out_measures.append({
            "slug": f"{county}-" + slugify(f"{mm['jurisdiction']}-{prop}"),
            "owner": county,
            "jurisdiction": mm["jurisdiction"],
            "proposition": prop,
            "title": mm["title"],
            "scope": scope_json(county, mm["scope"]),
            "pamphlet_pages": [{"edition": "local-voters-pamphlet", "page": p} for p in mm["pages"]],
            "what_it_does": mm["what_it_does"],
            "cost_line": mm["cost_line"],
            "pro_summary": None,
            "con_summary": None,
            "lean_mappings": {"taxes": {"direction": 2, "basis": TAX_BASIS, "citations": [mm["source_url"]]}},
        })

    coverage = "partial_county" if unresolvable else "full_county"
    notes = list(cfg.get("extra_notes", []))
    if not measures_curated:
        notes.append(votewa.MEASURES_NOT_CURATED)
    if unresolvable:
        notes.append(votewa.unresolvable_note(unresolvable))
    common = {
        "county": county,
        "script": "pipeline/build_votewa_lite_data.py",
        "derived_from": [
            rel(votewa.source_path(election_id, county)),
            *sorted({mm["source_url"] for mm in cfg["measures"]}),
        ],
        "coverage": coverage,
        "notes": notes,
    }
    return {**common, "contests": out_contests}, {**common, "measures": out_measures}, sorted(unresolvable)


def build_county(county, cfg, election_id, measures_curated=True):
    contests, measures, unresolvable = county_docs(county, cfg, election_id, measures_curated)
    outdir = election.Election(election_id).county(county) / "interim"
    outdir.mkdir(parents=True, exist_ok=True)
    (outdir / "app-contests.json").write_text(json.dumps(contests, indent=2))
    (outdir / "app-measures.json").write_text(json.dumps(measures, indent=2))
    return len(contests["contests"]), len(measures["measures"]), contests["coverage"], unresolvable


def counties_for(election_id, requested):
    """The counties to build: `requested`, else every configured county for
    an election whose exports are committed verbatim (the primary), else
    every configured county that has a VoteWA raw pointer for this election."""
    if requested:
        unknown = sorted(set(requested) - set(COUNTY_CONFIG))
        if unknown:
            raise SystemExit(f"not configured in COUNTY_CONFIG: {', '.join(unknown)} "
                             "(the six hand-built counties have their own build_<county>_lite_data.py)")
        missing = [c for c in requested if not votewa.has_source(election_id, c)]
        if missing:
            raise SystemExit(f"no VoteWA raw source for {', '.join(missing)} in {election_id}: run "
                             f"python3 pipeline/fetch_votewa_candidate_list.py --election {election_id} "
                             f"--write-pointer {' '.join(missing)}")
        return sorted(requested)
    if election.VOTEWA_SOURCES[election_id]["verbatim_csv"]:
        return sorted(COUNTY_CONFIG)
    return sorted(c for c in COUNTY_CONFIG if votewa.has_source(election_id, c))


def main(argv=None):
    import argparse
    parser = argparse.ArgumentParser(description="Build VoteWA-derived county lite packages.")
    election.add_election_arg(parser)
    parser.add_argument("--county", action="append", default=[],
                        help="build only this county (repeatable)")
    args = parser.parse_args(argv)
    election_id = election.resolve(args.election)
    counties = counties_for(election_id, args.county)
    total_c = total_m = 0
    for county in counties:
        cfg, curated = config_for(county, election_id)
        nc, nm, coverage, unresolvable = build_county(county, cfg, election_id, curated)
        total_c += nc
        total_m += nm
        flag = f"  UNRESOLVABLE: {','.join(unresolvable)}" if unresolvable else ""
        flag += "" if curated else "  MEASURES NOT CURATED"
        print(f"{county:14s} contests: {nc:3d}  measures: {nm}  {coverage}{flag}")
    print(f"total: {len(counties)} counties, {total_c} contests, {total_m} measures")


if __name__ == "__main__":
    main()
