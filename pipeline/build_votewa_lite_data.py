"""Build lite county packages for the 32 counties covered from VoteWA data.

Contests: parsed from the official VoteWA PRIMARY 2026 candidate list CSV in
data/washington-state/counties/<county>/raw/votewa/candidate-list.csv.
Rows with Election Status 'In Primary' are exactly the races printed on the
Aug 4, 2026 primary ballot (validated against the six hand-built county
packages, which this parser reproduces contest-for-contest). PCO races and
the statewide Supreme Court contests are excluded by convention.

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
"""

import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WA = ROOT / "data/washington-state/counties"

# DOR statewide taxing-district layer ids (2025 group) -> resolver layer key.
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


def m(jurisdiction, proposition, title, scope, what_it_does, cost_line, source_url):
    """Measure entry. scope is (layer, value), ('COUNTY', None), or ('CITY', name)."""
    return {
        "jurisdiction": jurisdiction,
        "proposition": proposition,
        "title": title,
        "scope": scope,
        "what_it_does": what_it_does,
        "cost_line": cost_line,
        "source_url": source_url,
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


def slugify(s: str) -> str:
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", s.lower())).strip("-")


def titleish(s: str) -> str:
    """Title-case fully-uppercase ballot strings; leave mixed case alone."""
    if s != s.upper():
        return s
    small = {"of", "the", "and", "for", "no", "at"}
    out = []
    for i, w in enumerate(s.lower().split()):
        if re.fullmatch(r"[0-9#.]+", w):
            out.append(w)
        elif w in ("no.", "pos.", "dist.", "u.s."):
            out.append(w.capitalize() if w != "u.s." else "U.S.")
        elif w in small and i:
            out.append(w)
        else:
            out.append(w.capitalize())
    return " ".join(out)


PARTY_MAP = {
    "DEMOCRATIC": "Prefers Democratic Party",
    "DEMOCRAT": "Prefers Democrat Party",
    "REPUBLICAN": "Prefers Republican Party",
    "INDEPENDENT": "Prefers Independent Party",
    "STATES NO PARTY PREFERENCE": "States No Party Preference",
    "": None,
}


def party_label(raw: str):
    raw = (raw or "").strip().upper()
    if raw in PARTY_MAP:
        return PARTY_MAP[raw]
    return f"Prefers {titleish(raw)} Party"


def district_number(*texts):
    for t in texts:
        n = re.search(r"(\d+)", t)
        if n:
            return int(n.group(1))
    raise ValueError(f"no district number in {texts!r}")


def load_contests(county, cfg, unresolvable):
    csv_path = WA / county / "raw/votewa/candidate-list.csv"
    rows = [r for r in csv.DictReader(open(csv_path, encoding="utf-8-sig")) if r["Election Status"] == "In Primary"]
    contests, order = {}, []
    for r in rows:
        dtype = r["District Type"].strip().upper()
        district, race = r["District"].strip(), r["Race"].strip()
        if dtype == "PRECINCT" or district.upper() == "SUPREME COURT":
            continue
        key = (district.upper(), race.upper())
        if key not in contests:
            if dtype == "CONGRESSIONAL":
                n = district_number(district)
                category, disp_district, scope = "Federal", f"Congressional District {n}", ("CONGDST", str(n))
            elif dtype == "LEGISLATIVE":
                n = district_number(district)
                category, disp_district, scope = "State", f"Legislative District {n}", ("LEGDST", str(n))
            elif dtype in ("COMMISSIONER", "COUNCIL"):
                n = district_number(race, district)
                fmt = cfg.get("commissioner")
                category = "County"
                disp_district = f"{cfg['name']} Commissioner District {n}"
                scope = ("COUNTY_COUNCIL", fmt.format(n=n) if fmt else str(n))
                if fmt is None:
                    unresolvable.add("COUNTY_COUNCIL")
            elif dtype in ("COUNTYWIDE", "COUNTY"):
                category, disp_district, scope = "County", cfg["name"], ("COUNTY", None)
            elif dtype == "JUDICIAL":
                # Superior/district courts and Court of Appeals divisions are
                # county-wide electorates for a single county's package.
                category, disp_district, scope = "Judicial", titleish(district), ("COUNTY", None)
            elif dtype == "PUBLIC UTILITY":
                n = district_number(district, race)
                fmt = cfg.get("pud")
                layer = cfg.get("pud_layer_key", "PUDDST")
                category = "PublicUtility"
                disp_district = f"Public Utility District Commissioner District {n}"
                scope = (layer, fmt.format(n=n) if fmt else str(n))
                if fmt is None:
                    unresolvable.add("PUDDST")
            elif dtype == "PORT":
                n = district_number(district, race)
                fmt = cfg.get("port")
                category = "Port"
                disp_district = titleish(district)
                scope = ("PORTDST", fmt.format(n=n) if fmt else str(n))
                if fmt is None:
                    unresolvable.add("PORTDST")
            elif dtype == "CITY/TOWN":
                city = re.sub(r"^(city|town) of ", "", district, flags=re.I).strip()
                category, disp_district, scope = "City", titleish(district), ("CITY", titleish(city))
            else:
                raise ValueError(f"{county}: unmapped district type {dtype!r} ({district} / {race})")
            contests[key] = {
                "category": category,
                "district": disp_district,
                "office": titleish(race),
                "scope": scope,
                "candidates": [],
            }
            order.append(key)
        contests[key]["candidates"].append({
            "slug": slugify(r["Name"]),
            "name": r["Name"].strip(),
            "party": party_label(r["Party Preference"]),
            "evidence_level": "official-ballot-only",
            "withdrawn": r["Status"].strip() != "Active",
            "summary": "Official ballot candidate. Voter Lifeboat has not completed a scored dossier for this candidate yet.",
            "highlights": [],
            "scores": {},
            "sources": [],
        })
    return [contests[k] for k in order]


def scope_json(county, scope):
    layer, value = scope
    if layer == "COUNTY":
        return {"kind": "COUNTY", "county": county}
    return {"kind": "DISTRICT", "county": county, "layer": layer, "value": str(value)}


def build_county(county, cfg):
    unresolvable = set()
    raw_contests = load_contests(county, cfg, unresolvable)
    out_contests = []
    for c in raw_contests:
        out_contests.append({
            "slug": f"{county}-" + slugify(f"{c['district']}-{c['office']}"),
            "owner": county,
            "category": c["category"],
            "office": c["office"],
            "district": c["district"],
            "scope": scope_json(county, c["scope"]),
            "office_does": None,
            "race_blurb": f"Official ballot listing imported from the VoteWA PRIMARY 2026 candidate list for {cfg['name']}. Candidate scoring is not complete for this county yet.",
            "uncontested": len(c["candidates"]) == 1,
            "candidates": c["candidates"],
        })

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
            "pamphlet_pages": [],
            "what_it_does": mm["what_it_does"],
            "cost_line": mm["cost_line"],
            "pro_summary": None,
            "con_summary": None,
            "lean_mappings": {"taxes": {"direction": 2, "basis": TAX_BASIS, "citations": [mm["source_url"]]}},
        })

    coverage = "partial_county" if unresolvable else "full_county"
    notes = list(cfg.get("extra_notes", []))
    if unresolvable:
        notes.append(
            "Unresolvable district scopes (no queryable official boundary): "
            + ", ".join(sorted(unresolvable))
            + ". Contests/measures scoped to them are hidden rather than shown to the wrong voters."
        )
    outdir = WA / county / "interim"
    outdir.mkdir(parents=True, exist_ok=True)
    common = {
        "county": county,
        "script": "pipeline/build_votewa_lite_data.py",
        "derived_from": [
            f"data/washington-state/counties/{county}/raw/votewa/candidate-list.csv",
            *sorted({mm["source_url"] for mm in cfg["measures"]}),
        ],
        "coverage": coverage,
        "notes": notes,
    }
    (outdir / "app-contests.json").write_text(json.dumps({**common, "contests": out_contests}, indent=2))
    (outdir / "app-measures.json").write_text(json.dumps({**common, "measures": out_measures}, indent=2))
    return len(out_contests), len(out_measures), coverage, sorted(unresolvable)


if __name__ == "__main__":
    total_c = total_m = 0
    for county, cfg in sorted(COUNTY_CONFIG.items()):
        nc, nm, coverage, unresolvable = build_county(county, cfg)
        total_c += nc
        total_m += nm
        flag = f"  UNRESOLVABLE: {','.join(unresolvable)}" if unresolvable else ""
        print(f"{county:14s} contests: {nc:3d}  measures: {nm}  {coverage}{flag}")
    print(f"total: {len(COUNTY_CONFIG)} counties, {total_c} contests, {total_m} measures")
