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
        # Whitman (#30). Measures: the Whitman County Auditor's general sample
        # ballot and printed Local Voters' Guide (counties/whitman/raw/whitman/
        # {sample-ballot,local-voters-pamphlet}.pdf.url, DocumentCenter 12666
        # and 12618, linked from whitmancounty.gov/172/Current-Election) and
        # VoteWA's online guide for county 38 (raw/votewa/voter-guide/) list
        # 31 local measures; the pamphlet prints 23 of them (pp. 12-31), the
        # other eight filed hardship waivers. Text from the guide's records.
        # Scopes point-checked 2026-10-08 (Census geocoder, Current vintage;
        # WA DOR 2025 layers 3 CEM, 7 FIR, 12 LIB, 14 PKR, 20 SCH):
        # - LIBDST 'L' (Whitman County Rural Library District): one Whitman
        #   polygon; 'L' at 200 S Mill St, Colfax; 123 Crosby St, Tekoa; 120 E
        #   Main St, Palouse; 101 Steptoe Ave, Oakesdale; 101 Front St, St.
        #   John; 201 N Main St, Albion; 102 N Main Ave, LaCrosse. No feature at
        #   325 SE Paradise St, Pullman (Neill Public Library) or in the towns
        #   of Rosalia, Garfield, Endicott, Colton and Uniontown, so it is not
        #   county-wide.
        # - SCHDST '316': DOR SCH2025 numbers Cheney School District No. 360's
        #   Whitman portion '316' (the county's copy of the layer,
        #   Whitman_County_Elections_Precinct_Data FeatureServer/62, labels it
        #   'Cheney School Tax District'); interior point (-117.70, 47.24),
        #   north of St. John, reads '316' and lies in OSPI's Cheney polygon.
        # - CITY: Census places Albion, Colton (705 Broadway St), Endicott
        #   (interior point -117.6858, 46.9268), Garfield, Oakesdale, Palouse,
        #   Rosalia (105 S Whitman Ave), St. John, Tekoa, Uniontown (110 S
        #   Montgomery St).
        # - FIRDST: '8' at (-117.85, 46.80) near LaCrosse (the town itself has
        #   no FIR2025 feature); '14' at 110 S Montgomery St, Uniontown and 705
        #   Broadway St, Colton.
        # - PARKDST: '1' LaCrosse, '2' Garfield, '3' St. John, '4' Oakesdale,
        #   '7' Endicott, each at the address above.
        # - CEMDST: '1' Oakesdale, '2' Garfield (405 E California St), '3' St.
        #   John, '4' Endicott.
        # Overrides: VoteWA files Commissioner 3 as Countywide. Whitman is a
        # non-charter county whose commissioners are nominated by district and
        # elected by the whole county (RCW 36.32.040, 36.32.050(1)): the 2026
        # primary counted the race in 28 of 81 reporting units, while the SOS
        # precinct exports put Commissioner 1 and 2 (2024) and Commissioner 3
        # (2022) on all 80 voting precincts, as for statewide races. It keeps
        # the primary's contest name so primary research carries forward. The
        # District Court seat (VoteWA 'District Court Judge Postion 1') is a
        # judicial seat of the single county-wide district court.
        "whitman": {
            "overrides": {
                ("COUNTY", "COMMISSIONER 3"): (
                    "County", "Whitman County Commissioner District 3", "Commissioner 3", ("COUNTY", None)),
                ("COUNTY", "DISTRICT COURT JUDGE POSTION 1"): (
                    "Judicial", "Whitman County District Court", "Judge Position No. 1", ("COUNTY", None)),
            },
            "measures": [
                m("Whitman County Rural Library District", "Proposition No. 1",
                  "Restoring Regular Property Tax Levy for Library Services",
                  ("LIBDST", "L"),
                  "Restores the Whitman County Rural Library District's regular property tax levy to $0.45 per $1,000 of assessed value for 2027 collection and keeps that maximum for nine more years; the 2036 levy amount becomes the base for later limits (chapter 84.55 RCW).",
                  "From $0.39 to $0.45 per $1,000 of assessed value; the district puts it at $14.30 more a year on a $275,000 home.",
                  "https://voter.votewa.gov/elections/measure.ashx?m=7390&e=899&la=en&c=38",
                  pages=(12,)),
                m("Cheney School District No. 360", "Proposition No. 1",
                  "Replacement Educational Programs and Operation Levy",
                  ("SCHDST", "316"),
                  "Replaces Cheney School District's expiring educational programs and operation levy for three years, paying for school safety, athletics, extracurricular activities, art, music, special education and staffing above the state allocation.",
                  "Estimated $2.10 per $1,000 of assessed value: $18,450,000 in 2028, $19,000,000 in 2029 and $19,550,000 in 2030.",
                  "https://voter.votewa.gov/elections/measure.ashx?m=7328&e=899&la=en&c=38",
                  pages=(13,)),
                m("Cheney School District No. 360", "Proposition No. 2",
                  "Replacement Capital Levy for Technology, Security and Infrastructure Improvements",
                  ("SCHDST", "316"),
                  "Replaces Cheney School District's expiring capital levy for three years, for instructional technology, security cameras and entry controls, and other safety infrastructure.",
                  "Estimated $0.10, $0.15 and $0.20 per $1,000 of assessed value: $880,000 in 2028, $1,350,000 in 2029 and $1,900,000 in 2030.",
                  "https://voter.votewa.gov/elections/measure.ashx?m=7329&e=899&la=en&c=38",
                  pages=(14,)),
                m("Town of Albion", "Proposition No. 1", "Protective Services",
                  ("CITY", "Albion"),
                  "One-year excess property tax levy for fire protection, law enforcement services, emergency response and other public safety purposes in Albion.",
                  "$20,000, an estimated $0.459 per $1,000 of assessed value, collected in 2027.",
                  "https://voter.votewa.gov/elections/measure.ashx?m=7392&e=899&la=en&c=38",
                  pages=(15,)),
                m("Town of Albion", "Proposition No. 2", "Cemetery Maintenance and Hazardous Tree Removal",
                  ("CITY", "Albion"),
                  "One-year excess property tax levy to maintain the Albion town cemetery, including hazardous tree removal and grounds improvements.",
                  "$5,000, an estimated $0.114 per $1,000 of assessed value, collected in 2027.",
                  "https://voter.votewa.gov/elections/measure.ashx?m=7393&e=899&la=en&c=38",
                  pages=(16,)),
                m("Town of Colton", "Proposition No. 880", "Levy of Additional Taxes",
                  ("CITY", "Colton"),
                  "One-year excess property tax levy that continues the town's support for general operations, street improvements and the water and sewer systems.",
                  "$30,000, approximately $0.53 per $1,000 of assessed value, collected in 2027.",
                  "https://voter.votewa.gov/elections/measure.ashx?m=7394&e=899&la=en&c=38",
                  pages=(17,)),
                m("Town of Endicott", "Proposition No. 1", "Fire Protection and Emergency Services Excess Levy",
                  ("CITY", "Endicott"),
                  "One-year excess property tax levy for fire protection and emergency services, including contracted fire protection, equipment and training.",
                  "$13,500, an estimated $0.44 per $1,000 of assessed value, collected in 2027.",
                  "https://voter.votewa.gov/elections/measure.ashx?m=7395&e=899&la=en&c=38",
                  pages=(18,)),
                m("Town of Endicott", "Proposition No. 2", "Park Excess Levy",
                  ("CITY", "Endicott"),
                  "One-year excess property tax levy to maintain and improve Endicott's parks: mowing, trees, playgrounds, irrigation and other park facilities.",
                  "$15,000, an estimated $0.49 per $1,000 of assessed value, collected in 2027.",
                  "https://voter.votewa.gov/elections/measure.ashx?m=7396&e=899&la=en&c=38",
                  pages=(18,)),
                m("Town of Endicott", "Proposition No. 3", "Street Maintenance and Public Safety Excess Levy",
                  ("CITY", "Endicott"),
                  "One-year excess property tax levy for street maintenance and related public safety in Endicott.",
                  "$35,000, an estimated $1.14 per $1,000 of assessed value (explanatory statement), collected in 2027.",
                  "https://voter.votewa.gov/elections/measure.ashx?m=7397&e=899&la=en&c=38",
                  pages=(19,)),
                m("Town of Garfield", "Proposition No. 1", "Street Maintenance and Repair Levy",
                  ("CITY", "Garfield"),
                  "One-year excess property tax levy for street maintenance, repair and improvements in Garfield; the town says its street fund has no other revenue of its own.",
                  "$72,000, an estimated $2.24 per $1,000 of assessed value, collected in 2027.",
                  "https://voter.votewa.gov/elections/measure.ashx?m=7398&e=899&la=en&c=38",
                  pages=(20,)),
                m("Town of Oakesdale", "Proposition No. 1", "Fire Protection and Emergency Medical Service Levy",
                  ("CITY", "Oakesdale"),
                  "One-year special property tax levy to fund fire protection and emergency medical services for Oakesdale.",
                  "$14,000, an estimated $0.46 per $1,000 of assessed value, collected in 2027.",
                  "https://voter.votewa.gov/elections/measure.ashx?m=7399&e=899&la=en&c=38"),
                m("Town of Oakesdale", "Proposition No. 2", "Street Maintenance Levy",
                  ("CITY", "Oakesdale"),
                  "One-year special property tax levy for street work, street lights and street maintenance in Oakesdale.",
                  "$60,000, an estimated $1.93 per $1,000 of assessed value, collected in 2027.",
                  "https://voter.votewa.gov/elections/measure.ashx?m=7400&e=899&la=en&c=38"),
                m("City of Palouse", "Proposition No. 1", "Operation and Maintenance of Infrastructure Levy",
                  ("CITY", "Palouse"),
                  "One-year excess property tax levy for the operation and maintenance of Palouse's city infrastructure (Resolution 2026-08).",
                  "$55,000 collected in 2027: the ballot title estimates $0.73058 per $1,000 of assessed value, the explanatory statement $0.5912.",
                  "https://voter.votewa.gov/elections/measure.ashx?m=7401&e=899&la=en&c=38",
                  pages=(21,)),
                m("City of Palouse", "Proposition No. 2", "Pool Maintenance and Operations Levy",
                  ("CITY", "Palouse"),
                  "One-year excess property tax levy for the operation and maintenance of the Palouse swimming pool (Resolution 2026-09).",
                  "$50,000 collected in 2027: the ballot title estimates $0.6641 per $1,000 of assessed value, the explanatory statement $0.53748.",
                  "https://voter.votewa.gov/elections/measure.ashx?m=7402&e=899&la=en&c=38",
                  pages=(21,)),
                m("City of Palouse", "Proposition No. 3", "Street Improvements and Equipment Levy",
                  ("CITY", "Palouse"),
                  "One-year excess property tax levy for street improvements and the vehicles and equipment used to maintain Palouse's streets (Resolution 2026-10).",
                  "$50,000, an estimated $0.6641 per $1,000 of assessed value, collected in 2027.",
                  "https://voter.votewa.gov/elections/measure.ashx?m=7403&e=899&la=en&c=38",
                  pages=(22,)),
                m("Town of Rosalia", "Proposition No. 1", "Street Levy",
                  ("CITY", "Rosalia"),
                  "One-year special (excess) property tax levy for Rosalia's street fund: street lights, seal coating, shoulder work, equipment and street maintenance.",
                  "$50,000 collected in 2027, at $1.50 per $1,000 of assessed value per the ballot title.",
                  "https://voter.votewa.gov/elections/measure.ashx?m=7404&e=899&la=en&c=38",
                  pages=(23,)),
                m("Town of St. John", "Proposition No. 1", "Street Improvement Levy",
                  ("CITY", "St. John"),
                  "Renews St. John's one-year special property tax levy for the maintenance, repair, improvement and replacement of town streets.",
                  "$90,000, an estimated $1.89 per $1,000 of assessed value, collected in 2027.",
                  "https://voter.votewa.gov/elections/measure.ashx?m=7405&e=899&la=en&c=38",
                  pages=(24,)),
                m("Town of St. John", "Proposition No. 2", "Water and Sewer Levy",
                  ("CITY", "St. John"),
                  "Renews St. John's one-year special property tax levy for water and sewer upgrades and capital improvements.",
                  "$80,000, an estimated $1.68 per $1,000 of assessed value, collected in 2027.",
                  "https://voter.votewa.gov/elections/measure.ashx?m=7406&e=899&la=en&c=38",
                  pages=(25,)),
                m("City of Tekoa", "Proposition No. 1", "Street Levy",
                  ("CITY", "Tekoa"),
                  "One-year special property tax levy for oiling gravel streets, chip sealing, asphalt replacement and sidewalk repair in Tekoa, including grant match.",
                  "$50,000, an estimated $1.23 per $1,000 of assessed value, collected in 2027.",
                  "https://voter.votewa.gov/elections/measure.ashx?m=7407&e=899&la=en&c=38",
                  pages=(26,)),
                m("Town of Uniontown", "Proposition No. 1", "Levy of Additional Taxes",
                  ("CITY", "Uniontown"),
                  "One-year excess property tax levy for Uniontown's general operations, water and sewer improvements and general maintenance, not employee wages.",
                  "About $30,000, approximately $0.64 per $1,000 of assessed value, collected in 2027.",
                  "https://voter.votewa.gov/elections/measure.ashx?m=7408&e=899&la=en&c=38",
                  pages=(27,)),
                m("Whitman County Fire Protection District No. 8", "Proposition No. 1", "Maintenance and Operation Levy",
                  ("FIRDST", "8"),
                  "Four-year excess property tax levy for the maintenance and operation of Fire District No. 8 (LaCrosse area), collected 2027 through 2030 (Resolution No. 2026-1).",
                  "$75,000 a year, an estimated $0.36 per $1,000 of assessed value.",
                  "https://voter.votewa.gov/elections/measure.ashx?m=7409&e=899&la=en&c=38",
                  pages=(28,)),
                m("Whitman County Fire Protection District No. 14", "Proposition No. 1", "Levy Lid Lift",
                  ("FIRDST", "14"),
                  "Sets Fire District No. 14's regular property tax levy at $1.08 per $1,000 of assessed value for 2027 collection, for fire protection, life safety services, apparatus and equipment, and firefighter safety; that amount becomes the base for later limits (Resolution No. 26-03).",
                  "$1.08 per $1,000 of assessed value for 2027 collection; the guide gives no current rate.",
                  "https://voter.votewa.gov/elections/measure.ashx?m=7410&e=899&la=en&c=38"),
                m("LaCrosse Park & Recreation District No. 1", "Proposition No. 1", "Operation and Maintenance Levy",
                  ("PARKDST", "1"),
                  "One-year special levy for the operation, maintenance and capital improvements of the LaCrosse swimming pool and the district's existing buildings.",
                  "$75,000, an estimated $0.31 per $1,000 of assessed value, collected in 2027.",
                  "https://voter.votewa.gov/elections/measure.ashx?m=7411&e=899&la=en&c=38",
                  pages=(29,)),
                m("Garfield Park & Recreation District No. 2", "Proposition No. 1", "Maintenance, Repair and Operating Cost Levy",
                  ("PARKDST", "2"),
                  "One-year property tax levy for pool maintenance, repair, higher operating costs (wages and chemicals) and new pool equipment (Resolution 2026-04).",
                  "$140,000, an estimated $1.05 per $1,000 of assessed value, collected in 2027.",
                  "https://voter.votewa.gov/elections/measure.ashx?m=7412&e=899&la=en&c=38"),
                m("St. John Park & Recreation District No. 3", "Proposition No. 1", "Operating Fund Levy",
                  ("PARKDST", "3"),
                  "One-year special levy for the district's operating fund, swimming pool, capital outlay and cumulative reserve.",
                  "$75,000, an estimated $0.2506 per $1,000 of assessed value, collected in 2027.",
                  "https://voter.votewa.gov/elections/measure.ashx?m=7413&e=899&la=en&c=38"),
                m("Oakesdale Park & Recreation District No. 4", "Proposition No. 1", "Operating, Maintaining and Improving Recreational Facilities",
                  ("PARKDST", "4"),
                  "One-year special levy to operate, maintain and improve the district's recreational facilities.",
                  "$120,000, an estimated $0.53 per $1,000 of assessed value, collected in 2027.",
                  "https://voter.votewa.gov/elections/measure.ashx?m=7414&e=899&la=en&c=38"),
                m("Endicott Parks & Recreation District No. 7", "Proposition No. 1", "Operating, Capital Outlay and Cumulative Reserve Levy",
                  ("PARKDST", "7"),
                  "One-year special levy for the district's operating fund, swimming pool, capital outlay and cumulative reserve.",
                  "$65,000, an estimated $0.42 or less per $1,000 of assessed value, collected in 2027.",
                  "https://voter.votewa.gov/elections/measure.ashx?m=7418&e=899&la=en&c=38"),
                m("Oakesdale Cemetery District No. 1", "Proposition No. 1", "Improvements and Maintenance Levy",
                  ("CEMDST", "1"),
                  "One-year special levy for continued improvements and maintenance of the Oakesdale cemetery.",
                  "$70,000, an estimated $0.35 per $1,000 of assessed value, collected in 2027.",
                  "https://voter.votewa.gov/elections/measure.ashx?m=7419&e=899&la=en&c=38"),
                m("Whitman County (Garfield) Cemetery District No. 2", "Proposition No. 2026-1", "Operation and Maintenance Levy",
                  ("CEMDST", "2"),
                  "One-year levy for equipment, sprinkler-system improvements and other operation and maintenance of the district's cemeteries (Garfield and Silver Creek).",
                  "$105,000, an estimated $0.82 or less per $1,000 of assessed value, collected in 2027.",
                  "https://voter.votewa.gov/elections/measure.ashx?m=7420&e=899&la=en&c=38",
                  pages=(30,)),
                m("St. John Cemetery District No. 3", "Proposition No. 1", "Funds to Maintain & Operate Cemetery",
                  ("CEMDST", "3"),
                  "One-year special property tax levy for the maintenance and operation of the St. John cemetery district.",
                  "$20,000, an estimated $0.16 per $1,000 of assessed value, collected in 2027.",
                  "https://voter.votewa.gov/elections/measure.ashx?m=7421&e=899&la=en&c=38",
                  pages=(31,)),
                m("Whitman County (Endicott) Cemetery District No. 4", "Proposition No. 1", "Maintenance and Operations Levy",
                  ("CEMDST", "4"),
                  "One-year excess property tax levy for the maintenance and operation of the Endicott cemetery district, renewing a levy that expires in 2026 (Resolution No. 2026-1).",
                  "$40,000, an estimated $0.37 per $1,000 of assessed value, collected in 2027.",
                  "https://voter.votewa.gov/elections/measure.ashx?m=7422&e=899&la=en&c=38",
                  pages=(31,)),
            ],
            "extra_notes": [
                "Whitman County Rural Library District Proposition No. 1 is scoped LIBDST 'L' (WA DOR LIB2025, layer 12): "
                "Pullman and the towns of Rosalia, Garfield, Endicott, Colton and Uniontown are outside the district, so it is not county-wide.",
                "Cheney School District No. 360's two levies reach a small Whitman area north of St. John; DOR SCH2025 (layer 20) numbers "
                "that portion '316', so both are scoped SCHDST '316'.",
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
