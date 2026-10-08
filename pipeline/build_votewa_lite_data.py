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
        # Adams (#31). Measures: the Adams County Auditor's general sample
        # ballot (counties/adams/raw/adams/sample-ballot.pdf.url,
        # DocumentCenter 2684, linked from co.adams.wa.gov/162/Elections-
        # Elecciones) and VoteWA's online voters' guide for county 01
        # (raw/votewa/voter-guide/guide.json.url, read 2026-10-08) both list
        # two local measures and no others. Adams prints no local pamphlet.
        # Scopes point-checked 2026-10-08 (Census geocoder, Current vintage;
        # WA DOR 2025 layers 7 FIR2025 and 14 PKR2025, DISTATTRIB):
        # 155 W Main St, Washtucna -> PKR2025 '2' (210 W Broadway Ave,
        # Ritzville -> '4'; 107 E 2nd St, Lind -> '3'; 425 E Main St,
        # Othello -> '1'); FD 4 has no geocodable street address, so its
        # interior points (-118.02, 47.15) and (-118.05, 47.10) -> FIR2025
        # '4' (1780 E Templin Rd, Ritzville -> '1'; Ritzville, Lind,
        # Washtucna and Othello -> no fire district). FIRDST is not in
        # COUNTY_LAYERS.adams yet (it reads CEMDST and PARKDST); see
        # counties/adams/COMPLETENESS.md.
        # Overrides: the commissioner race (District Type Countywide) is
        # nominated by district and elected county-wide in the general (RCW
        # 36.32.040, 36.32.050(1); SOS 2022 general precinct export: 'Adams
        # County Commissioner District 3' on all 28 precincts, the 2026
        # primary on 5 of 30 reporting units); it keeps the primary's contest
        # name so primary dossiers carry forward. The two District Court
        # seats are judicial seats of one county-wide court (2022: both on
        # all 28 precincts).
        "adams": {
            "overrides": {
                ("COUNTY", "COUNTY COMMISSIONER DISTRICT 3"): (
                    "County", "Adams County Commissioner District 3", "County Commissioner District 3", ("COUNTY", None)),
                ("COUNTY", "DISTRICT COURT JUDGE POSITION 1"): (
                    "Judicial", "Adams County District Court", "Judge Position No. 1", ("COUNTY", None)),
                ("COUNTY", "DISTRICT COURT JUDGE POSITION 2"): (
                    "Judicial", "Adams County District Court", "Judge Position No. 2", ("COUNTY", None)),
            },
            "measures": [
                m("Adams County Fire Protection District No. 4", "Proposition No. 1", "Maintenance and Operation Levy",
                  ("FIRDST", "4"),
                  "Authorizes a one-year special (excess) property tax levy for the construction, maintenance and operation of the fire district's pumper equipment in 2027. Needs 60% yes.",
                  "$11,000, an estimated $0.42 per $1,000 of assessed value, collected in 2027.",
                  "https://voter.votewa.gov/elections/measure.ashx?m=7368&e=899&la=en&c=01"),
                m("Adams County Park and Recreation District No. 2", "Proposition No. 1", "Maintenance and Operation Levy (Washtucna Pool)",
                  ("PARKDST", "2"),
                  "Authorizes a one-year special (excess) property tax levy for the maintenance and operation of the Washtucna Pool in 2027. Needs 60% yes; the same levy drew 57% yes in the August 4, 2026 primary.",
                  "$85,000, an estimated $0.83 per $1,000 of assessed value, collected in 2027.",
                  "https://voter.votewa.gov/elections/measure.ashx?m=7371&e=899&la=en&c=01"),
            ],
            "extra_notes": [
                "Adams County prints no local voters' pamphlet for the general; candidate statements and measure "
                "ballot titles are in VoteWA's online voters' guide (genericvoterguide.aspx?e=899&c=01).",
                "Adams County Commissioner District 3 is nominated by district and elected county-wide in the general "
                "(RCW 36.32.040; SOS 2022 general precinct results: on all 28 precincts).",
            ],
        },
        # Asotin (#31): checked against the Asotin County Auditor's general
        # sample ballot (precinct 001.02 Anatone) and local voters' pamphlet
        # (counties/asotin/raw/asotin/{sample-ballot,local-voters-pamphlet}.pdf.url,
        # linked from asotincountywa.gov/186/Current-Election) and VoteWA's
        # online guide for county 02 (raw/votewa/voter-guide/guide.json.url),
        # which list one local measure (guide record 7276; pamphlet PDF page 12).
        # Overrides: County Commissioner 3 is nominated by district and elected
        # county-wide in the general (RCW 36.32.040, 36.32.050(1)): the SOS
        # precinct exports put Commissioner 1, 2 and 3 (2020) on all 26
        # precincts, while the 2026 primary's District No. 3 race reported 7
        # units (raw/asotin/). It keeps the primary's contest name so its slug
        # matches. The District Court is one county-wide court. Asotin County
        # PUD No. 1 is not the whole county: its commissioners are elected
        # PUD-wide (RCW 54.12.010(3)) by 22 of 26 precincts (SOS exports for
        # Commissioner 1 in 2020, 3 in 2022 and 2 in 2024; Anatone, Asotin #1
        # and #2 and Rural Asotin are outside), so the seat is scoped PUDDST
        # '1' read from WA DOR PUD2025 (layer 17), whose single Asotin polygon
        # ('1') covers Clarkston and the Clarkston Heights tax code areas:
        # '1' at 829 5th St, Clarkston and 1406 16th Ave, Clarkston; no
        # feature in the City of Asotin (-117.0482, 46.3393) or at Anatone
        # (-117.1335, 46.1347).
        # Measure scope: Rural EMS District No. 2 is not DOR EMS2025's
        # Asotin '1' polygon (that is EMS District #1, the Fire District 1
        # area: '1' at 1406 16th Ave, Clarkston; no feature at Anatone). The
        # county's 2025 tax rates by tax code area and DOR's 2025 levy detail
        # ('EMS Dist #1 Special', $0.12084) put the rural EMS levy in TCAs 25,
        # 30 and 30F, the Anatone and Rural Asotin precinct parts that voted
        # on it in 2020 and August 2026. It is scoped RURALEMSDST '2', read
        # from DOR TCA2025 (layer 23) with where COUNTYNAME = 'ASOTIN' AND
        # DISTATTRIB IN ('0025','0030','0030F') (see counties/asotin/COMPLETENESS.md).
        "asotin": {
            "overrides": {
                ("COUNTY", "COUNTY COMMISSIONER 3"): (
                    "County", "Asotin County Commissioner District 3", "County Commissioner 3", ("COUNTY", None)),
                ("COUNTY", "DISTRICT COURT JUDGE"): (
                    "Judicial", "Asotin County District Court", "District Court Judge", ("COUNTY", None)),
                ("PUBLIC UTILITY DISTRICT", "PUBLIC UTILITY COMMISSIONER 1"): (
                    "PublicUtility", "Asotin County Public Utility District", "Commissioner District No. 1",
                    ("PUDDST", "1")),
            },
            "measures": [
                m("Asotin County Rural EMS District No. 2", "Proposition No. 1",
                  "Emergency Medical Services Regular Property Tax Levy",
                  ("RURALEMSDST", "2"),
                  "Authorizes Asotin County Rural Emergency Medical Service District No. 2 (the Anatone and rural southern county area) to levy a regular property tax for six years starting in 2027 to pay for contracted emergency medical services, replacing the levy that expires at the end of 2026 (Resolution No. 26-27; RCW 84.52.069). The same proposition failed in the August 4, 2026 primary.",
                  "Up to $0.28 per $1,000 of assessed value a year for 2027-2032, up from a current limit of $0.15 (the 2025 rate was about $0.12).",
                  "https://voter.votewa.gov/elections/measure.ashx?m=7276&e=899&la=en&c=02",
                  pages=(12,)),
            ],
            "extra_notes": [
                "Asotin County Rural EMS District No. 2 Proposition No. 1 is scoped RURALEMSDST '2': the district is tax code areas "
                "0025, 0030 and 0030F (WA DOR TCA2025, layer 23), the Anatone and rural southern county area; it is not the DOR "
                "EMS2025 Asotin '1' polygon, which is EMS District #1 (the Fire District 1 area around Clarkston Heights).",
                "Asotin County Commissioner District 3 is nominated by district and elected county-wide in the general "
                "(RCW 36.32.040, RCW 36.32.050(1)); Asotin County PUD No. 1 covers Clarkston and the Clarkston Heights area, not "
                "the whole county, and every PUD voter elects each commissioner (RCW 54.12.010(3)): scoped PUDDST '1' (WA DOR PUD2025, layer 17).",
            ],
        },
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
        # Columbia (#32). Measures: the Columbia County Auditor's local voters'
        # pamphlet (counties/columbia/raw/columbia/local-voters-pamphlet.pdf.url,
        # DocumentCenter 8822, linked from columbiaco.com/616/2026-General-
        # Election; PDF page = printed page + 1) and VoteWA's online guide for
        # county 07 (raw/votewa/voter-guide/) both list two local measures,
        # guide records 7423 and 7379 (PDF pp. 10 and 11); the Brooklyn
        # precinct sample ballot (raw/columbia/sample-ballot-page-{1,2}.jpg.url)
        # carries the pool levy only. Scopes point-checked 2026-10-08 (Census
        # geocoder, Current vintage; WA DOR PKR2025, layer 14, DISTATTRIB;
        # Columbia has two polygons, 'CPR' and 'PRES'):
        # - PARKDST 'CPR' (Columbia County Park and Recreation Pool District,
        #   VoteWA jurisdiction PKR070004): 341 E Main St, Dayton; 650 Wagon
        #   Rd, Dayton; 100 Hogeye Hollow Rd, Dayton; rural points (-117.75,
        #   46.45) and (-117.80, 46.10); and (-118.20, 46.45) in the rural
        #   Starbuck school district. No feature at 101 and 401 Main St,
        #   Starbuck: the district is the county minus the Town of Starbuck and
        #   the Prescott park district (explanatory statement); the 2024 pool
        #   levy was on every precinct but STARBUCK CITY (raw/columbia/sos-*).
        # - PARKDST 'PRES' (Prescott Joint Park and Recreation District, joint
        #   with Walla Walla County): the interior point (-118.21, 46.40) on
        #   the county's western edge (bbox -118.242..-118.179, 46.331..46.500);
        #   no Columbia street address there geocodes. SOS exports put the
        #   2022 and 2024 Prescott levies on the ALTO and STARBUCK COUNTRY
        #   precinct parts only (7 and 10 votes). Walla Walla's package carries
        #   its own copy scoped to Walla Walla County (same guide record 7379),
        #   so each county's voters see one copy.
        # Overrides: Commissioner No. 3 is nominated by district and elected
        # county-wide in the general (RCW 36.32.040, 36.32.050(1); Columbia is
        # a non-charter county): the 2026 primary race drew 417 votes against
        # about 1,050 in county-wide races (raw/columbia/votewa-2026-08-04-
        # primary-results.json.url), while the SOS precinct exports put
        # Commissioner #3 (2022) and #1 and #2 (2024) on all 13 voting
        # precincts, the same 13 as Sheriff and Governor. It keeps the
        # primary's contest name so its slug and primary dossiers carry
        # forward. The District Court is one county-wide district (2022 judge
        # race on all 13 precincts).
        "columbia": {
            "overrides": {
                ("COUNTY", "COLUMBIA COUNTY COMMISSIONER NO. 3"): (
                    "County", "Columbia County Commissioner District 3", "Columbia County Commissioner No. 3",
                    ("COUNTY", None)),
                ("COURT DISTRICT", "COLUMBIA COUNTY DISTRICT COURT JUDGE"): (
                    "Judicial", "Columbia County District Court", "District Court Judge", ("COUNTY", None)),
            },
            "measures": [
                m("Columbia County Park and Recreation Pool District", "Proposition No. 1", "Operation Excess Levy",
                  ("PARKDST", "CPR"),
                  "Authorizes a one-year excess property tax levy in 2026 for collection in 2027 to fund operation and maintenance of the pool the district plans to build in Dayton (the old Dayton pool closed in 2017). The district, formed by voters in 2023, covers the county except the Town of Starbuck and the Prescott park district's area.",
                  "$200,000 collected in 2027, approximately $0.20 per $1,000 of assessed value.",
                  "https://voter.votewa.gov/elections/measure.ashx?m=7423&e=899&la=en&c=07",
                  pages=(10,)),
                m("Prescott Joint Park and Recreation District", "Proposition No. 1",
                  "Maintenance & Operation Excess Levy",
                  ("PARKDST", "PRES"),
                  "Authorizes a one-year excess property tax levy for the park and recreation district's maintenance and operation expenses in 2027, its main source of operating money (chiefly the Prescott pool). The district is joint with Walla Walla County; only a thinly settled strip of western Columbia County is in it.",
                  "$175,000 collected in 2027 across the whole district, approximately $0.35 per $1,000 of assessed value.",
                  "https://voter.votewa.gov/elections/measure.ashx?m=7379&e=899&la=en&c=07",
                  pages=(11,)),
            ],
            "extra_notes": [
                "Columbia County Commissioner No. 3 is nominated by district and elected county-wide in the general "
                "(RCW 36.32.040, RCW 36.32.050(1); SOS precinct results 2022 and 2024: commissioner races on all 13 precincts).",
                "Both local measures are park and recreation district levies read from WA DOR PKR2025 (layer 14): 'CPR' is the "
                "Columbia County Park and Recreation Pool District (the county minus the Town of Starbuck and the Prescott "
                "district), 'PRES' the Columbia County part of the Prescott Joint Park and Recreation District.",
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
        # Jefferson (#31): checked against the Jefferson County Auditor's Local
        # Voters' Pamphlet (counties/jefferson/raw/jefferson/local-voters-pamphlet.pdf.url,
        # which "contains all races and issues in this election"), its sample
        # ballot (raw/jefferson/sample-ballot.pdf.url) and VoteWA's online guide
        # for county 16 (raw/votewa/voter-guide/guide.json.url): the same 13
        # contests and two local measures, both from districts based in Clallam
        # County that reach into Jefferson's West End. Jefferson is not a charter
        # county. Commissioner District 3: nominated by district, elected
        # county-wide in the general (RCW 36.32.040; VoteWA lists it 'Countywide';
        # in the SOS precinct exports the 2022 District 3 and 2020/2024 District 1
        # and 2 races are on every precinct, 37/37 and 39/39). Named as in the
        # primary so its slug and dossiers carry forward. District Court: one
        # county-wide judge (2022 SOS export: 37/37 precincts). Public Utility
        # District No. 1 of Jefferson County covers the whole county, Port
        # Townsend included (DOR PUD2025 layer 17 has one Jefferson polygon,
        # DISTATTRIB '1', equal in area to the sum of Jefferson's SCH2025
        # polygons; '1' at Port Townsend, Port Hadlock, Quilcene, Brinnon, Port
        # Ludlow and Forks-area West End addresses), and its seats are elected
        # PUD-wide in the general (RCW 54.12.010(3); SOS exports: the 2020
        # District 2, 2022 District 1 and 2024 District 3 races on every
        # precinct), so the seat is scoped COUNTY, as Clark's, Kitsap's and
        # Thurston's are.
        # Measure scopes, point-checked 2026-10-08 (Census geocoder, Current):
        # SCHDST '402': DOR SCH2025 (layer 20) DISTATTRIB '402' at 1993 Dowans
        # Creek Rd, Forks (Jefferson side) and 18113 Upper Hoh Rd, Forks; the
        # county's FindMyDistricts layer 8 names it 'Quillayute Valley School
        # District No. 402'. COUNTY_LAYERS.jefferson does not read SCH2025 yet.
        # FIRDST '9': DOR FIR2025 (layer 7) numbers the Jefferson part of
        # Clallam County Fire Protection District No. 1 '9' (1993 Dowans Creek
        # Rd -> '9'; the polygon matches the county FindMyDistricts layer 10
        # feature 'CCFD1' on 8,613 of 8,621 grid points); COUNTY_LAYERS.jefferson
        # already reads FIR2025. Jefferson's own Fire District 1 (East Jefferson
        # Fire Rescue) is '1', so the Clallam district cannot be scoped '1' here.
        "jefferson": {
            "overrides": {
                ("COUNTY", "DISTRICT 3"): (
                    "County", "Jefferson County Commissioner District 3", "District 3", ("COUNTY", None)),
                ("DISTRICT COURT", "JUDGE POSITION NO. 1"): (
                    "Judicial", "Jefferson County District Court", "Judge Position No. 1", ("COUNTY", None)),
                ("PUBLIC UTILITY DISTRICT", "COMMISSIONER, DISTRICT 2"): (
                    "PublicUtility", "Public Utility District No. 1 of Jefferson County", "Commissioner District 2",
                    ("COUNTY", None)),
            },
            "measures": [
                m("Quillayute Valley School District No. 402", "Proposition No. 1", "Bonds to Rebuild Forks Middle School",
                  ("SCHDST", "402"),
                  "Authorizes $34,000,000 of general obligation bonds, maturing within 25 years and repaid by excess property taxes, to build a new Forks Middle School replacing three existing buildings on the site. The district reaches into Jefferson County's West End.",
                  "$34,000,000 in bonds repaid over up to 25 years; the ballot materials give no rate, and the district estimates about $1.94 per $1,000 of assessed value from 2028, as its high school bond ends.",
                  "https://voter.votewa.gov/elections/measure.ashx?m=7296&e=899&la=en&c=16",
                  pages=(14,)),
                m("Clallam County Fire Protection District No. 1", "Proposition No. 1",
                  "Property Tax Levy for Fire Protection and Emergency Medical Services",
                  ("FIRDST", "9"),
                  "Sets the Forks-area fire district's regular levy at $1.00 per $1,000 for 2027 collection and lets it grow each year for nine more years by the greater of 1% or West Region CPI-U; the 2035 maximum becomes the base for later limits. A small part of the district is in Jefferson County.",
                  "$1.00 per $1,000 of assessed value for 2027 collection, up from about $0.47, then CPI-based growth (at least 1%) through 2035.",
                  "https://voter.votewa.gov/elections/measure.ashx?m=7292&e=899&la=en&c=16",
                  pages=(15,)),
            ],
            "extra_notes": [
                "Quillayute Valley School District No. 402 Proposition No. 1 is scoped SCHDST '402' (WA DOR SCH2025, layer 20, "
                "DISTATTRIB), the district's Jefferson County part (West End).",
                "Clallam County Fire Protection District No. 1 Proposition No. 1 is scoped FIRDST '9': WA DOR FIR2025 (layer 7) "
                "numbers the district's Jefferson County part '9'.",
                "County Commissioner District 3 and Public Utility District No. 1 Commissioner District 2 are elected county-wide "
                "in the general; PUD No. 1 of Jefferson County covers the whole county.",
            ],
        },
        # Kittitas (#31): no local measures. The Kittitas County Auditor's
        # general sample ballot and local voters' pamphlet (counties/kittitas/
        # raw/kittitas/{sample-ballot,local-voters-pamphlet}.pdf.url) list only
        # the three statewide measures, the elections page's Ballot Measures &
        # Resolutions table lists no resolution for the general, and VoteWA's
        # online guide for county 19 (raw/votewa/voter-guide/guide.json.url)
        # lists no local measure.
        # Overrides (all checked against the sample ballot):
        # - Commissioner 3: Kittitas is a non-charter county, so commissioners
        #   are nominated by district (RCW 36.32.040) and elected county-wide in
        #   the general (RCW 36.32.050(1)); VoteWA files the race as
        #   'Countywide', and the SOS precinct exports show the 2022 Commissioner
        #   3 race on all 48 precincts and the 2020/2024 Commissioner 1 and 2
        #   races on all 62/48 (raw/kittitas/sos-results-*.csv.url). It keeps
        #   the primary's contest name so its slug matches the primary's.
        # - District Court: two electoral districts, one judge each (Kittitas
        #   County Code 2.08.010-.020), Upper (Cle Elum, Roslyn, Easton, Hyak
        #   precincts) and Lower (Ellensburg, Kittitas, Thorp, Vantage); in 2022 each
        #   race was on its own precincts only (Lower 35 units, Upper 15).
        #   Scoped DISTCRT to the Auditor's precinct-built Court_Districts layer
        #   (services.arcgis.com/eSnyVpqwqWBADfzp/.../Court_Districts/
        #   FeatureServer/0, court_district_name), point-checked 2026-10-08:
        #   'Lower District Court' at 205 W 5th Ave, Ellensburg, 207 Main St,
        #   Kittitas and 10700 Thorp Hwy N, Thorp; 'Upper District Court' at 719
        #   E 3rd St, Cle Elum, 201 S 1st St, Roslyn, 523 Lincoln Ave, South
        #   Cle Elum and 1893 Railroad St, Easton.
        # - PUD No. 1 of Kittitas County covers the whole county (WA DOR
        #   PUD2025, layer 17: one Kittitas polygon, DISTATTRIB '1', area equal
        #   to the sum of Kittitas's SCH2025 polygons; '1' at Ellensburg, Cle
        #   Elum, Kittitas, Roslyn, South Cle Elum, Thorp and Easton) and the
        #   whole PUD elects each commissioner in the general (RCW
        #   54.12.010(3); the 2020 Commissioner 1 race was on all 62 precincts,
        #   the 2022 Commissioner 3 and 2024 Commissioner 2 races on all 48).
        #   Scoped COUNTY.
        "kittitas": {
            "overrides": {
                ("COUNTY", "COMMISSIONER 3"): (
                    "County", "Kittitas County Commissioner District 3", "Commissioner 3", ("COUNTY", None)),
                ("LOWER COUNTY DISTRICT COURT", "DISTRICT COURT JUDGE"): (
                    "Judicial", "Lower Kittitas County District Court", "District Court Judge",
                    ("DISTCRT", "Lower District Court")),
                ("UPPER COUNTY DISTRICT COURT", "DISTRICT COURT JUDGE"): (
                    "Judicial", "Upper Kittitas County District Court", "District Court Judge",
                    ("DISTCRT", "Upper District Court")),
                ("PUBLIC UTILITY DISTRICT 1", "COMMISSIONER 1"): (
                    "PublicUtility", "Public Utility District No. 1 of Kittitas County Commissioner District 1",
                    "Commissioner 1", ("COUNTY", None)),
            },
            "measures": [],
            "extra_notes": [
                "No local measures on the November 3, 2026 ballot: the Kittitas County sample ballot "
                "(https://www.co.kittitas.wa.us/uploads/documents/auditor/elections/election-files/71/sample-ballot.pdf) "
                "and local voters' pamphlet list only the statewide measures IP26-645, IL26-001 and IL26-638, and the "
                "Auditor's Ballot Measures & Resolutions table (https://www.co.kittitas.wa.us/auditor/elections/current/default.aspx) "
                "lists no resolution for the general.",
                "Kittitas County Commissioner District 3 is nominated by district and elected county-wide in the general "
                "(RCW 36.32.040, RCW 36.32.050(1)); Public Utility District No. 1 of Kittitas County covers the whole county "
                "(WA DOR PUD2025, layer 17) and every PUD voter elects each commissioner (RCW 54.12.010(3)). Both are scoped COUNTY.",
                "The Upper and Lower Kittitas County District Court judges are elected by their own district court "
                "district (Kittitas County Code 2.08.010, 2.08.020): scoped DISTCRT, read from the Auditor's Court_Districts layer "
                "(court_district_name 'Upper District Court' / 'Lower District Court').",
            ],
        },
        # Klickitat (#31): checked against the Auditor's general sample ballot
        # and the combined state/local voters' pamphlet (counties/klickitat/raw/
        # klickitat/{sample-ballot,local-voters-pamphlet}.pdf.url; local section
        # pp. 39-57, measure p. 56) and VoteWA's online guide for county 20
        # (raw/votewa/voter-guide/voterguide.json.url): the same 18 non-Supreme
        # Court contests and one local measure; the pamphlet's participating
        # jurisdictions are the State, the County, PUD No. 1 and EMS District
        # No. 1. Overrides: Commissioner 2 (VoteWA District 'County') is
        # nominated by district and elected county-wide in the general (RCW
        # 36.32.040; SOS precinct exports: the 2018 and 2022 Commissioner 2
        # races on all 29 precincts, the 2024 Commissioner 1 and 3 races on all
        # 33); named as in the primary so its dossiers carry forward. PUD No. 1
        # covers the whole county (Auditor's 2025 Votes by District: 16,421
        # registered voters, the county total; DOR PUD2025 layer 17 has one
        # Klickitat polygon, DISTATTRIB '1', at Goldendale, White Salmon,
        # Bingen, Lyle, Bickleton, Trout Lake and Klickitat) and the whole PUD
        # elects each commissioner (RCW 54.12.010(3); 2022 Pos. 2 and 2024
        # Pos. 1 on every precinct), so the seat is COUNTY; the generic rule
        # misreads District 'PUBLIC UTILITY DISTRICT # 1' as commissioner
        # district 1, and the primary's names are kept. The East and West
        # District Courts are separate electorates that partition the county
        # (2025 Votes by District: 7,550 + 8,871 = 16,421; SOS 2022: East on 18
        # and West on 16 of 29 precincts, several split): scoped DISTCRT
        # 'East'/'West'. No county, DOR or ArcGIS Online layer of those
        # districts was found (see counties/klickitat/COMPLETENESS.md), so
        # DISTCRT is unresolvable and the county stays partial_county.
        # Measure scope: EMSDST '1' is DOR EMS2025 (layer 6), one Klickitat
        # polygon: '1' at Goldendale, White Salmon, Bingen, Lyle, Trout Lake and
        # Klickitat, no feature at 100 E Market St, Bickleton (the district has
        # 16,105 of the county's 16,421 voters). 2026-10-08.
        "klickitat": {
            "overrides": {
                ("COUNTY", "COUNTY COMMISSIONER 2"): (
                    "County", "Klickitat County Commissioner District 2", "County Commissioner 2", ("COUNTY", None)),
                ("PUBLIC UTILITY DISTRICT # 1", "PUBLIC UTILITY DISTRICT #1 COMMISSIONER POS. 3"): (
                    "PublicUtility", "Public Utility District Commissioner District 3",
                    "Public Utility District #1 Commissioner Pos. 3", ("COUNTY", None)),
                ("EAST DISTRICT COURT", "KLICKITAT COUNTY EAST DISTRICT COURT JUDGE"): (
                    "Judicial", "Klickitat County East District Court", "Judge", ("DISTCRT", "East")),
                ("WEST DISTRICT COURT", "KLICKITAT COUNTY WEST DISTRICT COURT JUDGE"): (
                    "Judicial", "Klickitat County West District Court", "Judge", ("DISTCRT", "West")),
            },
            # No layer of the East/West court districts exists (#31 ship):
            # the package is partial_county, as app/src/lib/data-consistency.test.js
            # UNRESOLVABLE_SCOPES 'klickitat/DISTCRT' records.
            "unresolvable_layers": ["DISTCRT"],
            "measures": [
                m("Emergency Medical Services District No. 1, Klickitat County", "Proposition No. 1",
                  "Permanent Regular Emergency Medical Services Property Tax Levy",
                  ("EMSDST", "1"),
                  "Makes the EMS district's property tax levy permanent, at up to $0.50 per $1,000 of assessed value, first levied in 2026 for collection in 2027, in place of the six-year renewal voters approved in 2024 (collected 2025-2030). The money pays only for emergency medical services: ambulances, paramedics and EMTs, training, equipment and stations. The district covers the whole county except the Bickleton area.",
                  "Up to $0.50 per $1,000 of assessed value every year with no end date (about $250 a year on a $500,000 home at the full rate); the district's 2026 rate under its current levy is about $0.48, raising $2.56 million.",
                  "https://www.klickitatcounty.gov/DocumentCenter/View/23954",
                  pages=(56,)),
            ],
            "extra_notes": [
                "The East and West District Court judge seats are scoped DISTCRT 'East' and 'West': the two courts are "
                "separate electorates and no queryable boundary layer for them was found, so both stay hidden.",
                "EMS District No. 1 Proposition No. 1 is scoped EMSDST '1' (WA DOR EMS2025, layer 6); the Bickleton area "
                "is outside the district.",
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
        # Mason (#30): checked against the Mason County Auditor's Local Voters'
        # Pamphlet (counties/mason/raw/mason/local-voters-pamphlet.pdf.url, which
        # "contains all races and measures throughout Mason County", pp. 10-30)
        # and VoteWA's online guide for county 23 (raw/votewa/voter-guide/
        # guide.json.url): the same 16 contests and five local measures. The
        # sample ballot (raw/mason/sample-ballot.pdf.url) is vector art with no
        # extractable text. Measure text from the guide records and pamphlet.
        # Commissioner District 3: nominated by district, elected county-wide in
        # the general (RCW 36.32.040; VoteWA lists it 'Countywide'; in the SOS
        # precinct exports the 2020 and 2024 District 1 and 2 races and the 2022
        # District 3 race are on every precinct the statewide races are on).
        # Named as in the primary so its dossiers carry forward. District Court:
        # one county-wide judge (2022 SOS export: every precinct).
        # PUD No. 1 (Hood Canal/Hoodsport, 42.2 sq mi) and PUD No. 3 (the rest
        # of the county, 1,002.7 sq mi) split Mason between them; each seat is
        # elected PUD-wide in the general (RCW 54.12.010(3); SOS exports: PUD 1
        # races on 6-7 precincts, PUD 3 races on 42-55), so they are scoped
        # PUDDST '1' and '3' (WA DOR PUD2025, layer 17, DISTATTRIB: '1' at 24151
        # N US Hwy 101, Hoodsport; '3' at 525 W Cota St, Shelton and 23850 NE
        # State Route 3, Belfair; 2026-10-09). COUNTY_LAYERS.mason does not read
        # PUD2025 yet.
        # Measure scopes, point-checked 2026-10-09 (Census geocoder, Current;
        # DOR layers 12 and 20): Timberland Regional Library covers all of
        # Mason (one LIB2025 polygon, 1,044.9 sq mi, equal to the sum of
        # Mason's SCH2025 polygons; 'L' at Shelton, Belfair, Hoodsport), and
        # the whole five-county district votes, so COUNTY. SCHDST '42' at 161
        # SE Collier Rd, Shelton; '402' at 112 E Spencer Lake Rd, Shelton; '65'
        # at interior point (-123.2614, 47.0894) (Census: McCleary School
        # District, Mason County; 0.8 sq mi of Mason). COUNTY_LAYERS.mason does
        # not read SCH2025 yet. CITY 'Shelton': Census place at 525 W Cota St
        # (the Shelton TBD's tax applies to sales within the city).
        "mason": {
            "overrides": {
                ("COUNTY", "COUNTY COMMISSIONER DISTRICT NO. 3"): (
                    "County", "Mason County Commissioner District 3", "County Commissioner District No. 3",
                    ("COUNTY", None)),
                ("COUNTY", "DISTRICT COURT JUDGE"): (
                    "Judicial", "Mason County District Court", "District Court Judge", ("COUNTY", None)),
                ("PUBLIC UTILITY DIST 1", "COMMISSIONER DISTRICT 2"): (
                    "PublicUtility", "Public Utility District No. 1 of Mason County", "Commissioner District 2",
                    ("PUDDST", "1")),
                ("PUBLIC UTILITY DIST 3", "COMMISSIONER DISTRICT 2"): (
                    "PublicUtility", "Public Utility District No. 3 of Mason County", "Commissioner District 2",
                    ("PUDDST", "3")),
            },
            "measures": [
                m("Timberland Regional Library District", "Proposition No. 1",
                  "Regular Property Tax Levy Lid Lift for Library Services, Operations and Maintenance",
                  ("COUNTY", None),
                  "Restores the Timberland Regional Library District's regular property tax levy from $0.22 to $0.35 per $1,000 of assessed value for 2027 and 2028; the 2028 levy amount becomes the base for later limits (chapter 84.55 RCW).",
                  "From $0.228924 to $0.35 per $1,000 of assessed value in 2027 and 2028; about $40.44 a year on a $334,000 home, per the explanatory statement.",
                  "https://voter.votewa.gov/elections/measure.ashx?m=7284&e=899&la=en&c=23",
                  pages=(24, 25)),
                m("Southside School District No. 42", "Proposition No. 1",
                  "Replacement Educational Programs and Operations Levy",
                  ("SCHDST", "42"),
                  "Replaces Southside School District's expiring educational programs and operations levy for four years (2027-2030), for staffing, health and safety, afterschool, curriculum, technology, nutrition and special education costs the state does not fund.",
                  "$994,006 in 2027 rising to $1,217,701 in 2030, an estimated $1.97 per $1,000 of assessed value each year.",
                  "https://voter.votewa.gov/elections/measure.ashx?m=7383&e=899&la=en&c=23",
                  pages=(26, 27)),
                m("McCleary School District No. 65", "Proposition No. 1",
                  "Bonds to Improve Safety, Security and School Facilities",
                  ("SCHDST", "65"),
                  "Authorizes $12,800,000 of general obligation bonds, maturing within 21 years, for security upgrades, building, HVAC, drainage and parking improvements and modernized playgrounds at the McCleary School, repaid by annual excess property taxes.",
                  "$12.8 million in bonds over up to 21 years, repaid by an excess property tax levy; the ballot materials give no rate.",
                  "https://voter.votewa.gov/elections/measure.ashx?m=7385&e=899&la=en&c=23",
                  pages=(28,)),
                m("Pioneer School District No. 402", "Proposition No. 1",
                  "Replacement of Expiring Educational Programs and Operations Levy",
                  ("SCHDST", "402"),
                  "Replaces Pioneer School District's educational programs and operations levy, which expires at the end of 2027, for four years (2028-2031): class sizes, safety and security, mental health, music and STEM, academic supports, athletics and activities.",
                  "$3,700,000 in 2028 rising to $4,043,090 in 2031, an estimated $1.18 to $1.15 per $1,000 of assessed value.",
                  "https://voter.votewa.gov/elections/measure.ashx?m=7382&e=899&la=en&c=23",
                  pages=(29,)),
                m("City of Shelton", "Proposition No. 1",
                  "Sales and Use Tax for Transportation Improvements",
                  ("CITY", "Shelton"),
                  "Raises the Shelton Transportation Benefit District's sales and use tax from 0.2% to 0.3% for ten years, for street and pedestrian maintenance, repair and construction projects.",
                  "Sales tax for transportation rises from 0.2% to 0.3% (one more cent on a $10 purchase) for ten years.",
                  "https://voter.votewa.gov/elections/measure.ashx?m=7384&e=899&la=en&c=23",
                  pages=(30,)),
            ],
            "extra_notes": [
                "Mason County PUD No. 1 and PUD No. 3 each elect their Commissioner District 2 seat PUD-wide; the seats are "
                "scoped PUDDST '1' and '3' (WA DOR PUD2025, layer 17, DISTATTRIB).",
                "The Southside, McCleary and Pioneer school measures are scoped SCHDST '42', '65' and '402' (WA DOR SCH2025, "
                "layer 20, DISTATTRIB). Timberland Regional Library District covers all of Mason County.",
            ],
        },
        # Okanogan (#30): the six local measures in VoteWA's online voters'
        # guide for Okanogan County (voterguide.ashx?e=899&c=24, read
        # 2026-10-08; counties/okanogan/raw/votewa/voter-guide/), which match
        # the Auditor's District Resolutions page (seven stamped packets; the
        # county's own levy was on the August primary). The county prints no
        # local pamphlet. Scopes point-checked 2026-10-08 (Census geocoder,
        # Current vintage; WA DOR WADOR_PropertyTax layers 6, 7 and 11):
        # 415 Hospital Way, Brewster -> Census place 'Brewster city', HSP2025
        # '1J'; 118 S Glover St, Twisp -> 'Twisp town', HSP2025 '1J', EMS2025
        # 'TC'; 206 Riverside Ave, Winthrop -> 'Winthrop town', EMS2025 'WC';
        # 50 Lost River Rd, Mazama -> EMS2025 'MV' (Methow Valley EMS District,
        # which leaves out the two towns), HSP2025 '1J'; 26 Eastside Oroville
        # Rd and 38 Swanson Mill Rd, Oroville -> FIR2025 '1'; 1308 Ironwood
        # St, Oroville (in the city) -> no FIR2025 feature; 2 S Ash St, Omak
        # -> HSP2025 '3' (Mid-Valley, not Three Rivers).
        # Overrides: Commissioner District 3 is nominated by district and
        # elected county-wide in the general (RCW 36.32.040; the 2022 general's
        # District 3 race was on all 248 Okanogan precincts in the SOS precinct
        # export); the name keeps the primary's so its dossiers carry forward.
        # The District Court is one county-wide district (both seats on all
        # 248 precincts in 2022). The two PUD rows are left to the generic
        # rule (PUDDST, unresolvable): Okanogan PUD's seat is elected by the
        # whole PUD, which is the county minus about 325 voters in the
        # northeast (Bodie, Wauconda, Toroda area) who are in Ferry County PUD
        # No. 1 and vote in its Commissioner #3 race instead; no public layer
        # separates the two (DOR PUD2025 has one Okanogan polygon covering the
        # whole county). See counties/okanogan/COMPLETENESS.md.
        "okanogan": {
            "overrides": {
                ("COUNTY", "COMMISSIONER DISTRICT 3"): (
                    "County", "Okanogan County Commissioner District 3", "Commissioner District 3", ("COUNTY", None)),
                ("DISTRICT COURT JUDGE", "JUDGE POS. 1"): (
                    "Judicial", "Okanogan County District Court", "Judge Position No. 1", ("COUNTY", None)),
                ("DISTRICT COURT JUDGE", "JUDGE POS. 2"): (
                    "Judicial", "Okanogan County District Court", "Judge Position No. 2", ("COUNTY", None)),
            },
            "measures": [
                m("Public Hospital District No. 1, Okanogan and Douglas Counties", "Proposition No. 1",
                  "Bonds for Hospital Renovation and Improvement",
                  ("HOSPDST", "1J"),
                  "Authorizes up to $48,000,000 of general obligation bonds, maturing within 30 years, to renovate, remodel and equip Three Rivers Hospital in Brewster, repaid by annual excess property taxes (Resolution No. 2026-10).",
                  "Up to $48 million in bonds over up to 30 years; an estimated $0.73 per $1,000 of assessed value, about $18 a month on a $300,000 home, per the explanatory statement.",
                  "https://voter.votewa.gov/elections/measure.ashx?e=899&m=7283&la=en&c=24"),
                m("City of Brewster", "Proposition No. 1",
                  "Emergency Medical Care or Emergency Medical Services Continuation Levy",
                  ("CITY", "Brewster"),
                  "Continues Brewster's emergency medical services property tax levy, first approved in 2020, for six years from 2027; the city contracts with Douglas-Okanogan Fire District 15 for EMS (RCW 84.52.069).",
                  "$0.50 or less per $1,000 of assessed value a year for 2027-2032, the same rate as the expiring levy.",
                  "https://voter.votewa.gov/elections/measure.ashx?e=899&m=7278&la=en&c=24"),
                m("Town of Twisp", "Proposition No. 1",
                  "Emergency Medical Care and Services Excess Operations and Maintenance Levy",
                  ("CITY", "Twisp"),
                  "One-year excess levy (RCW 84.52.052) to keep emergency medical and ambulance services from being cut; Aero Methow Rescue Service is the contracted provider. Needs 60% approval and the constitutional turnout minimum.",
                  "$0.10 per $1,000 of assessed value, collected in 2027 only.",
                  "https://voter.votewa.gov/elections/measure.ashx?e=899&m=7279&la=en&c=24"),
                m("Town of Winthrop", "Proposition No. 1",
                  "Emergency Medical Services Excess Operations and Maintenance Levy",
                  ("CITY", "Winthrop"),
                  "One-year excess levy (RCW 84.52.052) to keep emergency medical and ambulance services from being cut; Aero Methow Rescue Service is the contracted provider. Needs 60% approval and the constitutional turnout minimum.",
                  "$0.10 per $1,000 of assessed value, collected in 2027 only.",
                  "https://voter.votewa.gov/elections/measure.ashx?e=899&m=7280&la=en&c=24"),
                m("Methow Valley Emergency Medical Services District", "Proposition No. 1",
                  "Emergency Medical Care and Services Excess Operations and Maintenance Levy",
                  ("EMSDST", "MV"),
                  "One-year excess levy (RCW 84.52.052) across the Methow Valley EMS District (outside the towns of Twisp and Winthrop) to keep emergency medical and ambulance services from being cut; Aero Methow Rescue Service is the contracted provider. Needs 60% approval and the constitutional turnout minimum.",
                  "$0.10 per $1,000 of assessed value, collected in 2027 only.",
                  "https://voter.votewa.gov/elections/measure.ashx?e=899&m=7282&la=en&c=24"),
                m("Okanogan County Fire Protection District No. 1", "Proposition No. 1",
                  "Levy Lid Lift",
                  ("FIRDST", "1"),
                  "Resets the Oroville-area fire district's regular property tax levy to $0.50 per $1,000 for 2027 collection (Resolution No. 97); that 2027 amount becomes the base for later 1% limits (chapter 84.55 RCW).",
                  "From about $0.22 to $0.50 per $1,000 of assessed value for 2027 collection.",
                  "https://voter.votewa.gov/elections/measure.ashx?e=899&m=7281&la=en&c=24"),
            ],
            "extra_notes": [
                "The Okanogan County PUD Commissioner District 1 seat is elected by the whole PUD, which is Okanogan County "
                "except about 325 registered voters in the northeast who are in Ferry County PUD No. 1 (Commissioner #3 race); "
                "no public GIS layer separates the two, so both PUD seats are scoped PUDDST and hidden (partial_county).",
                "The Methow Valley EMS levy is scoped EMSDST 'MV' (WA DOR EMS2025, layer 6, DISTATTRIB); the Fire District 1 "
                "levy FIRDST '1' (layer 7) and the Three Rivers hospital bonds HOSPDST '1J' (layer 11).",
            ],
        },
        # Pacific (#31). Contests: VoteWA GENERAL 2026 export for county 25
        # (counties/pacific/raw/votewa/candidate-list.csv.url); measures: VoteWA's
        # online voters' guide for county 25 (raw/votewa/voter-guide/), which
        # lists exactly the export's races plus four local measures. The
        # county's own site (co.pacific.wa.us / pacificcountywa.gov) did not
        # answer on 2026-10-08, so no local pamphlet or sample ballot was read.
        # Electorates checked against SOS results (counties/pacific/raw/sos/):
        # - Commissioner #03: nominated by district, elected county-wide (RCW
        #   36.32.040): every one of the 39 precincts voted in the 2018 #03 race
        #   (9,231 votes of 11,105 ballots) and the 2022 #03 general, while the
        #   2022 primary for #03 ran in District 3's precincts only.
        # - PUD No. 2: one Pacific polygon in DOR PUD2025 (layer 17,
        #   DISTATTRIB '2') whose area equals the county's (6,737,423,706 sq ft
        #   vs 6,737,558,937 for all TCA2025 polygons); every precinct voted
        #   in the 2018 and 2022 PUD races (RCW 54.12.010(3)). Scope COUNTY.
        # - District Court: two electoral districts. In 2022 the North District
        #   judge drew 3,221 votes (23 Willapa Harbor precincts: Raymond, South
        #   Bend, Menlo, Lebam, Bay Center, North Cove ...) and the South
        #   District 18 precincts (Long Beach peninsula, Ilwaco, Chinook,
        #   Naselle, Nemah); 12,068 ballots. Scoped DISTCRT 'North' / 'South';
        #   no public GIS layer for these districts was found (see
        #   counties/pacific/COMPLETENESS.md), so the layer is unresolvable
        #   until the director adds one.
        # Measure scopes point-checked 2026-10-08 (Census geocoder, Current
        # vintage; DOR WADOR_PropertyTax tax year 2025):
        # - Timberland: DOR LIB2025 (12) has one Pacific polygon, 'L', with the
        #   county's area (South Bend, Raymond, Long Beach, Ilwaco, Ocean Park,
        #   Naselle, Tokeland, Chinook all 'L'): scope COUNTY.
        # - EMSDST '1' (DOR EMS2025, layer 6): 300 Memorial Dr, South Bend; 230
        #   2nd St, Raymond; 793 State Rte 4, Naselle; 38 2nd St, Bay Center ->
        #   '1'. 1511 Bay Ave, Ocean Park -> 'OB'; 2964 Kindred Ave, Tokeland ->
        #   'SBH'; Long Beach, Ilwaco, Chinook -> no feature (the ballot title
        #   excludes the Ocean Beach, Ocosta and North River school districts).
        # - FIRDST '3' (FIR2025, layer 7): 1000 State Rte 6, Raymond (Menlo).
        # - FIRDST '6': 38 2nd St and 3 Park St E, Bay Center.
        "pacific": {
            "overrides": {
                ("COUNTY", "COUNTY COMMISSIONER #03"): (
                    "County", "Pacific County Commissioner District 3", "County Commissioner #03", ("COUNTY", None)),
                ("COURT - NORTH DISTRICT", "DISTRICT COURT JUDGE"): (
                    "Judicial", "Pacific County District Court North District", "District Court Judge",
                    ("DISTCRT", "North")),
                ("COURT - SOUTH DISTRICT", "DISTRICT COURT JUDGE"): (
                    "Judicial", "Pacific County District Court South District", "District Court Judge",
                    ("DISTCRT", "South")),
                ("PUD DISTRICT 2", "PUBLIC UTILITY COMMISSIONER #01"): (
                    "PublicUtility", "Public Utility District No. 2 of Pacific County", "Commissioner District 1",
                    ("COUNTY", None)),
            },
            # No layer of the North/South court districts exists (#31 ship):
            # the package is partial_county, as app/src/lib/data-consistency.test.js
            # UNRESOLVABLE_SCOPES 'pacific/DISTCRT' records.
            "unresolvable_layers": ["DISTCRT"],
            "measures": [
                m("Timberland Regional Library District", "Proposition No. 1",
                  "Regular Property Tax Levy Lid Lift for Library Services, Operations and Maintenance",
                  ("COUNTY", None),
                  "Restores the Timberland Regional Library District's regular property tax levy from about $0.22 to $0.35 per $1,000 of assessed value for 2027 and 2028; the 2028 levy amount becomes the base for later limits (chapter 84.55 RCW).",
                  "From $0.228924 to $0.35 per $1,000 of assessed value in 2027 and 2028; about $40.44 a year on a $334,000 home, per the explanatory statement.",
                  "https://voter.votewa.gov/elections/measure.ashx?m=7284&e=899&la=en&c=25"),
                m("North Pacific County Emergency Medical Services District No. 1", "Proposition No. 1",
                  "Ambulance and Emergency Medical Services Funding",
                  ("EMSDST", "1"),
                  "Renews the EMS district's one-year excess levy for 2027 to subsidize ambulance and emergency medical service in the Naselle, Nemah, Bay Center, South Bend, Raymond and Willapa Valley areas (Resolution 2026-721). Needs 60% approval.",
                  "$0.40 per $1,000 of assessed value, no more than $800,000, collected in 2027 only.",
                  "https://voter.votewa.gov/elections/measure.ashx?m=7388&e=899&la=en&c=25"),
                m("Pacific County Fire Protection District No. 3", "Proposition No. 1",
                  "Property Tax Levy Lid Lift for Fire Protection, Suppression and Prevention",
                  ("FIRDST", "3"),
                  "Raises Fire District 3's regular property tax levy to up to $0.61 per $1,000 for collection in 2027 (Resolution 26-2503-01); that levy becomes the base for later limits. The district serves Menlo, Lebam, Frances, Baleville, Elk Horn Flats, Old Willapa and East Raymond.",
                  "Up to $0.61 per $1,000 of assessed value in 2027, a $0.20 increase per the explanatory statement.",
                  "https://voter.votewa.gov/elections/measure.ashx?m=7389&e=899&la=en&c=25"),
                m("Pacific County Fire Protection District No. 6", "Proposition No. 1",
                  "Authorizing Regular Property Tax Levy",
                  ("FIRDST", "6"),
                  "Restores Fire District 6's regular property tax levy to $0.50 per $1,000 for collection in 2027 and lets it grow up to 6% a year (capped at $1.50 per $1,000) for the next five years (Resolution 2026-7-23-1); the 2031 levy becomes the base for later limits.",
                  "$0.50 per $1,000 of assessed value in 2027, then up to 6% more levy revenue a year through 2032 collection.",
                  "https://voter.votewa.gov/elections/measure.ashx?m=7391&e=899&la=en&c=25"),
            ],
            "extra_notes": [
                "Pacific County's two District Court seats are elected by electoral district (North: the Willapa Harbor "
                "precincts; South: the Long Beach peninsula, Ilwaco, Chinook, Naselle and Nemah precincts) and are scoped "
                "DISTCRT 'North' and 'South'. No public GIS layer for these districts was found; until one is added the "
                "seats cannot be matched to an address.",
                "Pacific County PUD No. 2 and Timberland Regional Library District each cover all of Pacific County "
                "(WA DOR PUD2025 and LIB2025 each have one Pacific polygon with the county's area).",
                "The EMS measure is scoped EMSDST '1' (WA DOR EMS2025, layer 6) and the fire measures FIRDST '3' and '6' "
                "(WA DOR FIR2025, layer 7), DISTATTRIB.",
            ],
        },
        # San Juan (#32): checked against the San Juan County Auditor's
        # sample ballot and its combined state and county voters' pamphlet
        # (counties/san-juan/raw/san-juan/{sample-ballot,local-voters-pamphlet}
        # .pdf.url; county section pp. 35-57, PDF page = printed page) and
        # VoteWA's online guide for county 28 (raw/votewa/voter-guide/), which
        # agree contest for contest: four local measures, text from the guide's
        # measure records 7285-7288 and pamphlet pp. 50-57.
        # Contests: the generic rules already fit. San Juan is a charter
        # county whose three council members must live in their residency
        # district but are voted on county-wide in the primary and the
        # general: VoteWA types the race 'Countywide', the August 4, 2026
        # primary counted Council Residency District 3 on all 23 units, and
        # the SOS precinct exports put the 2022 District 3 and 2024 District 1
        # and 2 races on all 23 precincts (raw/san-juan/sos-results-*.csv.url).
        # The council seat stays COUNTY with the primary's contest name. The
        # District Court is one county-wide judge; the override files it
        # Judicial, keeping the generic slug.
        # Measure scopes, point-checked 2026-10-08 (Census geocoder + DOR
        # WADOR_PropertyTax 2025 layers; county Voter_Precincts layer):
        # - FIRDST '4' (FIR2025, layer 7): 2225 Fisherman Bay Rd, 86 School Rd
        #   and 4102 Mud Bay Rd, Lopez Island -> '4'; Friday Harbor '3';
        #   Eastsound '2'; Shaw (interior point) '5'; Decatur none.
        # - PORTDST 'LOPEZ' (PRT2025, layer 16): the same Lopez addresses ->
        #   'LOPEZ'; 350 Court St, Friday Harbor -> 'FRI HAR'; Eastsound ->
        #   'ORCAS'; Shaw and Decatur none.
        # - PARKDST 'ORCAS' (PKR2025, layer 14): 500 Rose St, Eastsound, 5164
        #   Deer Harbor Rd and 107 Doe Bay Rd, Olga -> 'ORCAS'; Friday Harbor
        #   'S J'; Lopez, Shaw, Blakely and Waldron (interior points) none. The
        #   district's levy and commissioner races were on the seven Orcas
        #   precincts only, not Blakely or Waldron (SOS 2023, 2025 exports).
        # - SWDDST 'LOPEZ': no DOR or county tax-district layer has the Lopez
        #   Solid Waste Disposal District. Its annual levy was on precincts
        #   Lopez North, Lopez Northwest and Lopez South only (SJ031, SJ030,
        #   SJ032) in every general 2022-2025, the same precincts as Fire
        #   District 4 and the Port of Lopez, never Decatur. The county's
        #   Voter_Precincts layer (St_Code) holds those precincts; on a 425-point
        #   grid over Lopez and Decatur every land point inside SJ030-SJ032 is
        #   in DOR PRT2025 'LOPEZ' and FIR2025 '4', and every other land point
        #   is in neither. See counties/san-juan/COMPLETENESS.md for the layer
        #   proposal.
        "san-juan": {
            "overrides": {
                ("COUNTY", "DISTRICT COURT JUDGE"): (
                    "Judicial", "San Juan County District Court", "Judge", ("COUNTY", None)),
            },
            "measures": [
                m("San Juan County Fire Protection District No. 4 (Lopez Island Fire & EMS)", "Proposition No. 1",
                  "Property Tax Levy for Fire Protection and Emergency Medical",
                  ("FIRDST", "4"),
                  "Restores the Lopez Island fire and EMS district's regular property tax levy to $0.74 per $1,000 for 2027 collection (Resolution No. 2026-02) and lets the levy grow up to 3% a year, instead of the usual 1%, for 2027 through 2035; the 2035 maximum becomes the base for later limits.",
                  "$0.74 per $1,000 of assessed value for 2027 collection, up from about $0.47, then up to 3% a year levy growth through 2035.",
                  "https://voter.votewa.gov/elections/measure.ashx?m=7286&e=899&la=en&c=28",
                  pages=(50, 51)),
                m("Port of Lopez", "Proposition No. 1", "Term Length of Port Commissioners",
                  ("PORTDST", "LOPEZ"),
                  "Lengthens the term of Port of Lopez commissioners from four years to six (Resolution No. 2026-2). Current commissioners keep their terms; six-year terms apply to commissioners elected later.",
                  "No tax. The port says six-year terms would put one seat, not two, on the ballot every other cycle and lower its election costs.",
                  "https://voter.votewa.gov/elections/measure.ashx?m=7287&e=899&la=en&c=28",
                  pages=(52, 53)),
                m("Orcas Island Park and Recreation District", "Proposition No. 1", "Six-Year Property Tax Levy",
                  ("PARKDST", "ORCAS"),
                  "Renews the Orcas Island park and recreation district's regular property tax levy for six years at $0.15 per $1,000 (Resolution 2026-07-09), subject to the limits of chapter 84.55 RCW, to fund district programs, services and facilities such as Buck Park.",
                  "$0.15 per $1,000 of assessed value for 2027 collection (the 2025 rate was about $0.10), for six years; about $120 a year on an $800,000 home.",
                  "https://voter.votewa.gov/elections/measure.ashx?m=7288&e=899&la=en&c=28",
                  pages=(54, 55)),
                m("Lopez Solid Waste Disposal District", "Proposition No. 1", "Excess Property Tax Levy for 2027",
                  ("SWDDST", "LOPEZ"),
                  "One-year excess property tax levy of $210,000 for the Lopez Island dump's operations and capital improvements in 2027 (Resolution No. 20-2026); the district may only levy one year at a time, so it asks every year. Needs 60% approval.",
                  "$210,000 for 2027 only, estimated at $0.091 per $1,000 of assessed value (about $45.50 on a $500,000 property), the same amount as the current levy.",
                  "https://voter.votewa.gov/elections/measure.ashx?m=7285&e=899&la=en&c=28",
                  pages=(56, 57)),
            ],
            "extra_notes": [
                "San Juan County Council Residency District 3 is voted on county-wide in the primary and the general (the "
                "residency district is a candidate qualification): scoped COUNTY.",
                "San Juan County Fire Protection District No. 4 Proposition No. 1 is scoped FIRDST '4' (WA DOR FIR2025, layer 7), "
                "Port of Lopez Proposition No. 1 PORTDST 'LOPEZ' (PRT2025, layer 16) and Orcas Island Park and Recreation District "
                "Proposition No. 1 PARKDST 'ORCAS' (PKR2025, layer 14), each DISTATTRIB.",
                "Lopez Solid Waste Disposal District Proposition No. 1 is scoped SWDDST 'LOPEZ': no tax-district layer has the "
                "district; its levy is voted on in precincts Lopez North, Lopez Northwest and Lopez South (county Voter_Precincts "
                "St_Code SJ031, SJ030, SJ032).",
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
        # Skamania (#32): no local measures. The Skamania County Auditor's general
        # sample ballot and local voters' pamphlet (counties/skamania/raw/skamania/
        # {sample-ballot,local-voters-pamphlet}.pdf.url, linked from
        # skamaniacounty.gov/departments-offices/auditor/elections/current-election)
        # list only the three statewide measures; the pamphlet names the
        # participating jurisdictions as the State, Skamania County and Skamania
        # County PUD only, and VoteWA's online guide for county 30
        # (raw/votewa/voter-guide/guide.json.url) lists no local measure. The
        # sample ballot is one ballot style for the whole county.
        # Overrides (checked against the sample ballot):
        # - Commissioner No. 3: Skamania is a non-charter county under 400,000,
        #   so commissioners are nominated by district (RCW 36.32.040) and
        #   elected by the voters of the whole county (RCW 36.32.050(1)); the
        #   sample ballot prints 'Skamania County Commissioner District No. 3'
        #   under 'ONLY REGISTERED VOTERS IN COUNTY ARE ELIGIBLE'. SOS precinct
        #   exports: 2022 Commissioner #3 and 2020/2024 Commissioner #1 and #2 on
        #   all 23 precincts, while the 2026 primary's District No. 3 race
        #   reported 8 of 23 units (raw/skamania/sos-results-*.csv.url,
        #   votewa-2026-08-04-primary-results.json.url). It keeps the primary's
        #   contest name so its slug matches the primary's.
        # - District Court: one county-wide judge (2022: on all 23 precincts).
        # - Public Utility District No. 1 of Skamania County covers the whole
        #   county (WA DOR PUD2025, layer 17: one Skamania polygon, DISTATTRIB
        #   '1', area 9,058,178,385 equal to the sum of Skamania's six SCH2025
        #   polygons; '1' at Stevenson, North Bonneville, Carson and Underwood)
        #   and the whole PUD elects each commissioner in the general (RCW
        #   54.12.010(3); the 2020 Commissioner #3, 2022 #2 and 2024 #1 races were
        #   on all 23 precincts). Scoped COUNTY.
        "skamania": {
            "overrides": {
                ("COUNTY", "COMMISSIONER NO. 3"): (
                    "County", "Skamania County Commissioner District 3", "Commissioner No. 3", ("COUNTY", None)),
                ("COUNTY", "DISTRICT COURT JUDGE"): (
                    "Judicial", "Skamania County District Court", "District Court Judge", ("COUNTY", None)),
                ("PUBLIC UTILITY DISTRICT", "COMMISSIONER #3"): (
                    "PublicUtility", "Public Utility District No. 1 of Skamania County Commissioner District 3",
                    "Commissioner #3", ("COUNTY", None)),
            },
            "measures": [],
            "extra_notes": [
                "No local measures on the November 3, 2026 ballot: the Skamania County sample ballot "
                "(https://www.skamaniacounty.gov/home/showpublisheddocument/19606/639256882368200000) and local voters' "
                "pamphlet (https://www.skamaniacounty.gov/home/showpublisheddocument/19600/639253463106470000) list only "
                "the statewide measures IP26-645, IL26-001 and IL26-638, and VoteWA's online voters' guide for county 30 "
                "lists no local measure.",
                "Skamania County Commissioner District 3 is nominated by district and elected county-wide in the general "
                "(RCW 36.32.040, RCW 36.32.050(1)); Public Utility District No. 1 of Skamania County covers the whole county "
                "(WA DOR PUD2025, layer 17) and every PUD voter elects each commissioner (RCW 54.12.010(3)). Both are scoped COUNTY.",
            ],
        },
        # Stevens (#30). Stevens County's own site (stevenscountywa.gov) answers
        # 403 to scripted requests, so contests and measures were checked against
        # VoteWA's online voters' guide for county 33 (voterguide.ashx?e=899&c=33,
        # counties/stevens/raw/votewa/voter-guide/guide.json.url), which lists the
        # same 16 non-Supreme-Court races as the candidate list and four local
        # measures (7251, 7323, 7330, 7331).
        # Overrides: Stevens is a non-charter county under 400,000, so its
        # commissioners are nominated by district and elected by the voters of
        # the whole county (RCW 36.32.040, RCW 36.32.050(1)); VoteWA's general
        # export lists the race as 'Countywide' and the SOS 2020-11-03 Stevens
        # precinct export has Commissioner #1 and #3 on all 58 precincts. It
        # keeps the primary's contest name so primary dossiers carry forward.
        # District Court: one county-wide court, one seat. PUD: Public Utility
        # District No. 1 of Stevens County is one DOR PUD2025 (layer 17) polygon
        # covering the whole county (DISTATTRIB '1'; its area equals the sum of
        # the county's SCH2025 polygons; '1' at Colville, Chewelah, Kettle Falls,
        # Northport, Springdale, Suncrest and Loon Lake), and the whole PUD elects
        # each commissioner in the general (RCW 54.12.010(3); the 2020 PUD
        # Commissioner #2 race was on all 58 Stevens precincts). Scoped COUNTY,
        # and named as the Spokane package names it, so it ships with Spokane's
        # research (Spokane voters in the PUD's Spokane County portion elect it
        # too).
        # Measure scopes, point-checked 2026-10-08 (Census geocoder, Current;
        # WA DOR 2025 layers 7 FIR, 12 LIB, 20 SCH):
        # - LIBDST 'L' (Stevens County Rural Library District): '1' polygon at
        #   301 E Clay Ave, Chewelah; 406 Center Ave, Northport; 410 N Main St,
        #   Springdale; 3998 State Hwy 292, Loon Lake; 6015 State Route 291,
        #   Nine Mile Falls (Suncrest). No feature at 215 S Oak St, Colville or
        #   605 Meyers St, Kettle Falls: the two cities are outside the district.
        # - FIRDST '10': 2785 Aladdin Rd, Colville (the county's Fire Districts
        #   layer, AdministrativeBoundaries/MapServer/15, reads 'Fire District
        #   10' there too).
        # - SCHDST '179J' (Nine Mile Falls School District No. 325-179, Stevens
        #   side): 6015 State Route 291, Nine Mile Falls (county School Districts
        #   layer 24: 'Nine Mile Falls SD 179').
        "stevens": {
            "overrides": {
                ("COUNTY", "COMMISSIONER #2"): (
                    "County", "Stevens County Commissioner District 2", "Commissioner #2", ("COUNTY", None)),
                ("COUNTY", "DISTRICT COURT JUDGE"): (
                    "Judicial", "Stevens County District Court", "District Court Judge", ("COUNTY", None)),
                ("PUBLIC UTILITY DISTRICT 1", "COMMISSIONER #2"): (
                    "PublicUtility", "Public Utility District No. 1 of Stevens County Commissioner District 2",
                    "PUD Commissioner", ("COUNTY", None)),
            },
            "measures": [
                m("Stevens County Rural Library District", "Proposition No. 2", "Levy Lift For Library Services",
                  ("LIBDST", "L"),
                  "Restores the Stevens County Rural Library District's (Libraries of Stevens County) regular property tax levy from $0.27 to $0.44 per $1,000 of assessed value for 2027 collection, to fund library operations, hours, staff and materials; that amount becomes the base for later limits (chapter 84.55 RCW). Colville and Kettle Falls are outside the district.",
                  "From $0.27 to $0.44 per $1,000 of assessed value for 2027 collection; about $51 a year ($4.25 a month) on a $300,000 home, per the statement for.",
                  "https://voter.votewa.gov/elections/measure.ashx?m=7251&e=899&la=en&c=33"),
                m("Stevens County Fire Protection District No. 10", "Proposition No. 1", "Property Tax Levy For Fire Protection Services",
                  ("FIRDST", "10"),
                  "Sets Fire District 10's regular property tax levy at $0.75 per $1,000 of assessed value for 2027 collection, to keep operating and maintaining its fire vehicles, stations, trained personnel and equipment; that amount becomes the base for later limits (Resolution No. 2-2026).",
                  "$0.75 per $1,000 of assessed value for 2027 collection, up from the current $0.54: about $21 a year more per $100,000 of assessed value.",
                  "https://voter.votewa.gov/elections/measure.ashx?m=7323&e=899&la=en&c=33"),
                m("Nine Mile Falls School District No. 325-179", "Proposition No. 1", "Replacement Educational Programs And Operations Levy",
                  ("SCHDST", "179J"),
                  "Replaces the district's educational programs and operations levy, which expires in 2027, with a three-year levy (2028-2030) for staffing, safety, arts, nurses, counselors, class size, athletics, transportation and other costs the state does not fund (Resolution No. 11-26).",
                  "Estimated $2.10 per $1,000 of assessed value: $4,354,837 in 2028, $4,428,827 in 2029 and $4,504,075 in 2030.",
                  "https://voter.votewa.gov/elections/measure.ashx?m=7330&e=899&la=en&c=33"),
                m("Nine Mile Falls School District No. 325-179", "Proposition No. 2", "Capital Levy for Safety, Security, and Infrastructure Improvements",
                  ("SCHDST", "179J"),
                  "Authorizes a six-year capital levy (2027-2032) to replace a failing roof and condemned portable classrooms at Lakeside High School and modernize security, fire systems, facilities and infrastructure district-wide (Resolution No. 12-26).",
                  "Estimated $0.38 per $1,000 of assessed value: $774,853 in 2027 rising to $842,954 in 2032; the district says it matches the rate of a bond that expires January 1, 2027.",
                  "https://voter.votewa.gov/elections/measure.ashx?m=7331&e=899&la=en&c=33"),
            ],
            "extra_notes": [
                "Stevens County Rural Library District Proposition No. 2 is scoped LIBDST 'L' (WA DOR LIB2025, layer 12): "
                "the Cities of Colville and Kettle Falls are outside the district, so it is not county-wide.",
                "Stevens County Commissioner District 2 is nominated by district and elected county-wide in the general "
                "(RCW 36.32.040, RCW 36.32.050(1)); Public Utility District No. 1 of Stevens County covers the whole county "
                "(WA DOR PUD2025, layer 17) and every PUD voter elects each commissioner (RCW 54.12.010(3)). Both are scoped COUNTY.",
            ],
        },
        # Walla Walla (#30): checked against the Walla Walla County Auditor's
        # general sample ballot and local voters' pamphlet (counties/walla-walla/
        # raw/walla-walla/{sample-ballot,local-voters-pamphlet}.pdf.url, linked
        # from wwcowa.gov/government/auditor/current_election.php) and VoteWA's
        # online guide for county 36 (raw/votewa/voter-guide/), which list two
        # local measures (guide records 7378, 7379; pamphlet pp. 22-25).
        # Measure scopes, point-checked 2026-10-08 (Census geocoder, Current):
        # SCHDST '101': WA DOR SCH2025 (layer 20) DISTATTRIB '101' (COUNTYNAME
        # 'WALLA WALLA') at the interior point (-118.153, 46.140) in the Dixie
        # CDP; the Census geocoder matches no Dixie street address (the school's
        # 10520 E Highway 12 included). Other Walla Walla values: 140 at 315 W
        # Main St, Walla Walla; 250 at 940 SE Harvest Dr, College Place; 401 at
        # 106 Preston Ave, Waitsburg; 402 at 108 S D St, Prescott; 400 at 785
        # Tumbleweed Ln, Burbank. '101' also names districts in Clark, Pacific,
        # Skagit and Whatcom, which a point query never reaches.
        # PARKDST 'PRES': WA DOR PKR2025 (layer 14) DISTATTRIB 'PRES' at 108 S D
        # St, Prescott; 'WAIT' at 106 Preston Ave, Waitsburg; no feature at 315
        # W Main St, Walla Walla. The district is joint with Columbia County
        # (DOR has a 'PRES' polygon in each county; the guide record says
        # 'Columbia, Walla Walla').
        # Overrides: County Commissioner District 3 is nominated by district and
        # elected county-wide in the general (RCW 36.32.040). VoteWA's general
        # export lists it as 'Countywide'; the SOS precinct exports show the
        # 2022 District 3 and 2024 District 1 and 2 general races on all 62
        # voting precincts, while the 2026 primary's District 3 race reported
        # 18 of 62 units (raw/walla-walla/sos-results-*.csv.url). It keeps the
        # primary's contest name so its slug and primary dossiers carry forward.
        # The District Court is one county-wide district with a full-time and
        # a part-time judge; the overrides file both seats as Judicial.
        "walla-walla": {
            "overrides": {
                ("COUNTY", "COUNTY COMMISSIONER DISTRICT 3"): (
                    "County", "Walla Walla County Commissioner District 3", "County Commissioner District 3",
                    ("COUNTY", None)),
                ("COUNTY", "DISTRICT COURT JUDGE - FULL TIME"): (
                    "Judicial", "Walla Walla County District Court", "District Court Judge - Full Time",
                    ("COUNTY", None)),
                ("COUNTY", "DISTRICT COURT JUDGE - PART TIME"): (
                    "Judicial", "Walla Walla County District Court", "District Court Judge - Part Time",
                    ("COUNTY", None)),
            },
            "measures": [
                m("Dixie School District No. 101", "Proposition 1",
                  "Replacement Capital Levy for Health, Safety and Energy Efficiency Improvements",
                  ("SCHDST", "101"),
                  "Replaces Dixie School District's capital levy, which expires at the end of 2026, with a six-year levy for 2027 through 2032 to keep funding health, safety and energy-efficiency repairs and modernization at Dixie School.",
                  "$75,000 a year for 2027 through 2032, an estimated $0.50 per $1,000 of assessed value.",
                  "https://voter.votewa.gov/elections/measure.ashx?m=7378&e=899&la=en&c=36",
                  pages=(22, 23)),
                m("Prescott Joint Park and Recreation District", "Proposition No. 1",
                  "Maintenance & Operation Excess Levy",
                  ("PARKDST", "PRES"),
                  "Authorizes a one-year excess property tax levy for the park and recreation district's maintenance and operation expenses in 2027, its main source of operating money.",
                  "$175,000 collected in 2027, approximately $0.35 per $1,000 of assessed value.",
                  "https://voter.votewa.gov/elections/measure.ashx?m=7379&e=899&la=en&c=36",
                  pages=(24, 25)),
            ],
        },
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
    # Layers an override scopes a contest to that no District Adapter layer
    # resolves (Klickitat's and Pacific's DISTCRT): the override hook cannot
    # report them, so the block names them and the package says partial_county.
    cfg["unresolvable_layers"] = tuple(per.get("unresolvable_layers", ())) if per else ()
    return cfg, per is not None


def county_docs(county, cfg, election_id, measures_curated=True):
    """(app-contests doc, app-measures doc, unresolvable layers) without writing."""
    unresolvable = set()
    rows = votewa.ballot_rows(election_id, county)
    # Per-election overrides: {(District, Race) upper-cased: classify()-shaped tuple}.
    overrides = cfg.get("overrides") or {}
    override = (lambda r, _u: overrides.get((r["District"].strip().upper(), r["Race"].strip().upper()))) if overrides else None
    raw_contests = votewa.parse_contests(rows, county, cfg, unresolvable, override)
    declared = set(cfg.get("unresolvable_layers", ()))
    for c in raw_contests:
        if c["scope"][0] in declared:
            unresolvable.add(c["scope"][0])
    for mm in cfg["measures"]:
        if mm["scope"][0] in declared:
            unresolvable.add(mm["scope"][0])
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
