"""The general's shipped data: the statewide package, King's schema-2
package at Full County Coverage (issues #9 and #16), Spokane's app-*.json
package at partial coverage, Pierce's (#21) and Snohomish's (#27) at full
coverage, Clark's, Kitsap's and Thurston's at full coverage (#22), and
Yakima's, Whatcom's, Benton's, Skagit's, Cowlitz's and Grant's at full
coverage (#28), Island's, Lewis's, Franklin's, Chelan's, Clallam's and
Grays Harbor's at full coverage (#29), Mason's, Walla Walla's,
Stevens's, Whitman's and Douglas's at full coverage and Okanogan's at
partial coverage (#30), Jefferson's, Kittitas's, Asotin's and Adams's at
full coverage and Klickitat's and Pacific's at partial coverage (#31), and
Skamania's and San Juan's at full coverage (#32).

These read the committed outputs of merge_scores.py and assemble_app_data.py,
so they fail if the general is re-assembled from the wrong packages, King's
owner/scope/uncontested rules drift, or the refutation verdicts stop being
applied.
"""

import json
import re
import unittest

import election

GENERAL = election.Election("2026-11-03-general")
KING = GENERAL.county("king")
SNOHOMISH = GENERAL.county("snohomish")
SPOKANE = GENERAL.county("spokane")
PIERCE = GENERAL.county("pierce")
CLARK = GENERAL.county("clark")
KITSAP = GENERAL.county("kitsap")
THURSTON = GENERAL.county("thurston")
YAKIMA = GENERAL.county("yakima")
WHATCOM = GENERAL.county("whatcom")
BENTON = GENERAL.county("benton")
SKAGIT = GENERAL.county("skagit")
COWLITZ = GENERAL.county("cowlitz")
GRANT = GENERAL.county("grant")
ISLAND = GENERAL.county("island")
LEWIS = GENERAL.county("lewis")
FRANKLIN = GENERAL.county("franklin")
CHELAN = GENERAL.county("chelan")
CLALLAM = GENERAL.county("clallam")
GRAYS_HARBOR = GENERAL.county("grays-harbor")
WAVE4B = (FRANKLIN, CHELAN, CLALLAM, GRAYS_HARBOR)
MASON = GENERAL.county("mason")
WALLA_WALLA = GENERAL.county("walla-walla")
STEVENS = GENERAL.county("stevens")
WHITMAN = GENERAL.county("whitman")
DOUGLAS = GENERAL.county("douglas")
OKANOGAN = GENERAL.county("okanogan")
JEFFERSON = GENERAL.county("jefferson")
KITTITAS = GENERAL.county("kittitas")
KLICKITAT = GENERAL.county("klickitat")
PACIFIC = GENERAL.county("pacific")
ASOTIN = GENERAL.county("asotin")
ADAMS = GENERAL.county("adams")
SKAMANIA = GENERAL.county("skamania")
SAN_JUAN = GENERAL.county("san-juan")
SHIPPED = ("king", "snohomish", "spokane", "pierce", "clark", "kitsap", "thurston", "yakima", "whatcom", "benton",
           "skagit", "cowlitz", "grant", "island", "lewis", "franklin", "chelan", "clallam", "grays-harbor", "mason",
           "walla-walla", "stevens", "whitman", "douglas", "okanogan", "jefferson", "kittitas", "klickitat", "pacific",
           "asotin", "adams", "skamania", "san-juan")
STATEWIDE = {"kind": "STATEWIDE"}
GEO_JS = election.ROOT / "app/src/lib/geo.js"
# Whitman measures that filed hardship waivers: on the ballot and in VoteWA's
# guide, not in the printed local pamphlet (its p. 3 lists them).
WHITMAN_UNPRINTED = {
    "whitman-town-of-oakesdale-proposition-no-1",
    "whitman-town-of-oakesdale-proposition-no-2",
    "whitman-whitman-county-fire-protection-district-no-14-proposition-no-1",
    "whitman-garfield-park-recreation-district-no-2-proposition-no-1",
    "whitman-st-john-park-recreation-district-no-3-proposition-no-1",
    "whitman-oakesdale-park-recreation-district-no-4-proposition-no-1",
    "whitman-endicott-parks-recreation-district-no-7-proposition-no-1",
    "whitman-oakesdale-cemetery-district-no-1-proposition-no-1",
}


def read(path):
    return json.loads(path.read_text())


class GeneralPackagesTest(unittest.TestCase):
    def test_general_ships_the_statewide_package_and_thirty_three_counties(self):
        self.assertTrue(election.ELECTION_META[GENERAL.id]["statewide_complete"])
        self.assertEqual(list(SHIPPED), election.APP_PACKAGES[GENERAL.id]["counties"])
        self.assertEqual([GENERAL.state, KING, SNOHOMISH, SPOKANE, PIERCE, CLARK, KITSAP, THURSTON,
                          YAKIMA, WHATCOM, BENTON, SKAGIT, COWLITZ, GRANT, ISLAND, LEWIS, *WAVE4B, MASON, WALLA_WALLA,
                          STEVENS, WHITMAN, DOUGLAS, OKANOGAN, JEFFERSON, KITTITAS, KLICKITAT, PACIFIC, ASOTIN,
                          ADAMS, SKAMANIA, SAN_JUAN],
                         GENERAL.shipped_packages())

    def test_king_adapter_layers_match_geo_js(self):
        block = re.search(r"const KING_LAYERS = \{(.*?)\n\}", GEO_JS.read_text(), re.S).group(1)
        keys = re.findall(r"^\s+([A-Z]+):", block, re.M)
        self.assertEqual(sorted(keys), sorted(election.DISTRICT_ADAPTER_LAYERS["king"]))

    def test_county_adapter_layers_match_geo_js(self):
        # Census CONGDST/LEGDST/CITY plus geo.js COUNTY_LAYERS[<county>].
        text = GEO_JS.read_text()
        for county, layers in election.DISTRICT_ADAPTER_LAYERS.items():
            if county == "king":
                continue
            # Hyphenated ids are quoted keys ('grays-harbor').
            block = re.search(rf"\n  '?{county}'?: \[(.*?)\n  \],", text, re.S).group(1)
            keys = re.findall(r"key: '([A-Z_]+)'", block)
            self.assertEqual(sorted(["CONGDST", "LEGDST", "CITY"] + keys), sorted(layers), county)

    def test_county_elections_urls_are_per_election(self):
        self.assertEqual("https://kingcounty.gov/en/dept/elections",
                         election.county_elections_url(GENERAL.id, "king"))
        self.assertEqual("https://www.snohomishcountywa.gov/224/Elections-Voter-Registration",
                         election.county_elections_url(GENERAL.id, "snohomish"))
        self.assertEqual("https://www.spokanecounty.gov/elections",
                         election.county_elections_url(GENERAL.id, "spokane"))
        self.assertEqual("https://www.piercecountywa.gov/elections",
                         election.county_elections_url(GENERAL.id, "pierce"))
        self.assertEqual("https://clark.wa.gov/elections", election.county_elections_url(GENERAL.id, "clark"))
        self.assertEqual("https://www.kitsap.gov/auditor/Pages/Elections.aspx",
                         election.county_elections_url(GENERAL.id, "kitsap"))
        self.assertEqual("https://www.thurstoncountywa.gov/departments/auditor/elections",
                         election.county_elections_url(GENERAL.id, "thurston"))
        self.assertEqual("https://www.yakimacounty.us/170/Elections", election.county_elections_url(GENERAL.id, "yakima"))
        self.assertEqual("https://www.whatcomcounty.us/2794/Elections",
                         election.county_elections_url(GENERAL.id, "whatcom"))
        self.assertEqual("https://www.bentoncountywa.gov/government/elected_officials/auditor/elections/index.php",
                         election.county_elections_url(GENERAL.id, "benton"))
        self.assertEqual("https://www.skagitcountywa.gov/government/auditor-s-office/elections-and-voting/",
                         election.county_elections_url(GENERAL.id, "skagit"))
        self.assertEqual("https://www.co.cowlitz.wa.us/2357/Elections", election.county_elections_url(GENERAL.id, "cowlitz"))
        self.assertEqual("https://www.grantcountywa.gov/270/Elections", election.county_elections_url(GENERAL.id, "grant"))
        self.assertEqual("https://www.islandcountywa.gov/423/Elections-Voter-Registration",
                         election.county_elections_url(GENERAL.id, "island"))
        self.assertEqual("https://elections.lewiscountywa.gov/", election.county_elections_url(GENERAL.id, "lewis"))
        self.assertEqual("https://www.franklincountywa.gov/Elections", election.county_elections_url(GENERAL.id, "franklin"))
        self.assertEqual("https://www.co.chelan.wa.us/elections", election.county_elections_url(GENERAL.id, "chelan"))
        self.assertEqual("https://www.clallamcountywa.gov/162/Elections-Voter-Registration",
                         election.county_elections_url(GENERAL.id, "clallam"))
        self.assertEqual("https://www.graysharbor.us/government/Auditors/elections.php",
                         election.county_elections_url(GENERAL.id, "grays-harbor"))
        self.assertEqual("https://www.masoncountywa.gov/departments/auditor/elections/index.php",
                         election.county_elections_url(GENERAL.id, "mason"))
        self.assertEqual("https://www.wwcowa.gov/government/auditor/current_election.php",
                         election.county_elections_url(GENERAL.id, "walla-walla"))
        self.assertEqual("https://www.stevenscountywa.gov/20911/Elections",
                         election.county_elections_url(GENERAL.id, "stevens"))
        self.assertEqual("https://www.whitmancounty.gov/172/Current-Election",
                         election.county_elections_url(GENERAL.id, "whitman"))
        self.assertEqual("https://www.douglascountywa.gov/206/Current-Election",
                         election.county_elections_url(GENERAL.id, "douglas"))
        self.assertEqual("https://www.okanogancounty.gov/337/Elections",
                         election.county_elections_url(GENERAL.id, "okanogan"))
        self.assertEqual("https://www.co.jefferson.wa.us/1266/Elections",
                         election.county_elections_url(GENERAL.id, "jefferson"))
        self.assertEqual("https://www.co.kittitas.wa.us/auditor/elections/default.aspx",
                         election.county_elections_url(GENERAL.id, "kittitas"))
        self.assertEqual("https://www.klickitatcounty.gov/1136/ElectionsVoter-Registration",
                         election.county_elections_url(GENERAL.id, "klickitat"))
        self.assertEqual("https://www.asotincountywa.gov/186/Current-Election",
                         election.county_elections_url(GENERAL.id, "asotin"))
        self.assertEqual("https://www.co.adams.wa.gov/162/Elections-Elecciones",
                         election.county_elections_url(GENERAL.id, "adams"))
        self.assertEqual("https://www.skamaniacounty.gov/departments-offices/auditor/elections/current-election",
                         election.county_elections_url(GENERAL.id, "skamania"))
        self.assertEqual("https://www.sanjuancountywa.gov/1292/Current-Election",
                         election.county_elections_url(GENERAL.id, "san-juan"))
        # Pacific's site did not answer on 2026-10-08 (#31): no office URL, so
        # the app links the statewide county elections office list.
        self.assertIsNone(election.county_elections_url(GENERAL.id, "pacific"))
        self.assertIsNone(election.county_elections_url(GENERAL.id, "garfield"))
        # The primary's shipped app data predates the field.
        self.assertIsNone(election.county_elections_url("2026-08-04-primary", "king"))
        for urls in election.COUNTY_ELECTIONS_URLS.values():
            for url in urls.values():
                self.assertTrue(url.startswith("https://"), url)

    def test_primary_keeps_every_package(self):
        primary = election.Election("2026-08-04-primary")
        self.assertEqual(primary.packages(), primary.shipped_packages())


class GeneralAppDataTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = read(GENERAL.final / "app-data.json")
        cls.contests = {c["slug"]: c for c in cls.app["contests"]}
        cls.measures = {m["slug"]: m for m in cls.app["measures"]}
        cls.state_contests = read(GENERAL.state / "interim/contests.json")["contests"]
        cls.state_measures = read(GENERAL.state / "interim/measures.json")["measures"]
        cls.king_contests = read(KING / "interim/contests.json")["contests"]
        cls.king_measures = read(KING / "interim/measures.json")["measures"]
        cls.sno_contests = read(SNOHOMISH / "interim/app-contests.json")["contests"]
        cls.sno_measures = read(SNOHOMISH / "interim/app-measures.json")["measures"]
        cls.spo_contests = read(SPOKANE / "interim/app-contests.json")["contests"]
        cls.spo_measures = read(SPOKANE / "interim/app-measures.json")["measures"]
        cls.pie_contests = read(PIERCE / "interim/app-contests.json")["contests"]
        cls.pie_measures = read(PIERCE / "interim/app-measures.json")["measures"]
        cls.wave2_contests = [c for d in (CLARK, KITSAP, THURSTON) for c in read(d / "interim/app-contests.json")["contests"]]
        cls.wave2_measures = [m for d in (CLARK, KITSAP, THURSTON) for m in read(d / "interim/app-measures.json")["measures"]]
        cls.wave3_contests = [c for d in (YAKIMA, WHATCOM, BENTON) for c in read(d / "interim/app-contests.json")["contests"]]
        cls.wave3_measures = [m for d in (YAKIMA, WHATCOM, BENTON) for m in read(d / "interim/app-measures.json")["measures"]]
        cls.wave3b_contests = [c for d in (SKAGIT, COWLITZ, GRANT) for c in read(d / "interim/app-contests.json")["contests"]]
        cls.wave3b_measures = [m for d in (SKAGIT, COWLITZ, GRANT) for m in read(d / "interim/app-measures.json")["measures"]]
        cls.wave4_contests = [c for d in (ISLAND, LEWIS) for c in read(d / "interim/app-contests.json")["contests"]]
        cls.wave4_measures = [m for d in (ISLAND, LEWIS) for m in read(d / "interim/app-measures.json")["measures"]]
        cls.wave4b_contests = [c for d in WAVE4B for c in read(d / "interim/app-contests.json")["contests"]]
        cls.wave4b_measures = [m for d in WAVE4B for m in read(d / "interim/app-measures.json")["measures"]]
        cls.mason_contests = read(MASON / "interim/app-contests.json")["contests"]
        cls.mason_measures = read(MASON / "interim/app-measures.json")["measures"]
        cls.wave5_contests = [c for d in (WALLA_WALLA, STEVENS, WHITMAN, DOUGLAS, OKANOGAN)
                              for c in read(d / "interim/app-contests.json")["contests"]]
        cls.wave5_measures = [m for d in (WALLA_WALLA, STEVENS, WHITMAN, DOUGLAS, OKANOGAN)
                              for m in read(d / "interim/app-measures.json")["measures"]]
        wave6 = (JEFFERSON, KITTITAS, KLICKITAT, PACIFIC, ASOTIN, ADAMS)
        cls.wave6_contests = [c for d in wave6 for c in read(d / "interim/app-contests.json")["contests"]]
        cls.wave6_measures = [m for d in wave6 for m in read(d / "interim/app-measures.json")["measures"]]
        wave7 = (SKAMANIA, SAN_JUAN)
        cls.wave7_contests = [c for d in wave7 for c in read(d / "interim/app-contests.json")["contests"]]
        cls.wave7_measures = [m for d in wave7 for m in read(d / "interim/app-measures.json")["measures"]]

    def test_twenty_nine_counties_are_full_four_partial(self):
        # Spokane is partial_county because its Stevens County PUD seat is
        # scoped to PUDDST, which no public layer resolves; Okanogan because
        # its Okanogan PUD and Ferry County PUD No. 1 seats are PUDDST, with
        # no public layer separating the two PUDs' voters (#30); Klickitat and
        # Pacific because their District Court seats (East/West, North/South)
        # are DISTCRT, with no public layer of the court districts (#31). Snohomish's nine
        # District Court seats resolve from the Auditor's Court_Districts
        # layer (DISTCRT, #27). Pierce's KCDISTCRT, PTBA and SCHDST read the
        # Election_Precincts layer. Clark's, Kitsap's and Thurston's school
        # levies and Thurston's WTRFA levy read county layers (#22). Benton's
        # PUD race reads the Auditor's PrecinctSplits layer and its Ki-Be
        # levy DOR SCH2025 (#28). Skagit's fire and school levies and Grant's
        # fire, cemetery and hospital measures read DOR layers; Cowlitz's
        # one measure is a city's (#28). Island's Camano PUD seat reads the
        # Auditor's precinct layer, its port and unincorporated-county
        # measures DOR PRT2025 and TCA2025; Lewis's PUD seat and library levy
        # read DOR PUD2025 and LIB2025 (#29). Franklin's port seat reads the
        # county's port layer and its FPD 3 levy DOR FIR2025; Chelan's and
        # Clallam's school measures DOR SCH2025; Clallam's District Court seats
        # the Auditor's District_Court layer and its PUD seat PUDALL, any
        # feature of the PUD's commissioner-district layer; Grays Harbor's
        # library and school measures DOR LIB2025 and SCH2025 (#29). Mason's
        # PUD No. 1 and No. 3 seats read DOR PUD2025 and its school measures
        # DOR SCH2025 (#30). Walla Walla's Dixie school and Prescott park
        # levies read DOR SCH2025 and PKR2025; Stevens's library, fire and
        # Nine Mile Falls school measures DOR LIB2025, FIR2025 and SCH2025
        # (#30). Whitman's library, cemetery and Cheney school measures read
        # DOR LIB2025, CEM2025 and SCH2025; Douglas's Eastmont and Cemetery
        # District 2 measures DOR SCH2025 and CEM2025, and its proposed Rimrock
        # Meadows fire district the county's own fire layer (PROPFIRDST, #30).
        # Jefferson's West End Quillayute Valley SD 402 bonds and Clallam FD 1
        # levy read DOR SCH2025 ('402') and FIR2025 ('9'); Kittitas's Upper
        # and Lower District Court seats the Auditor's Court_Districts layer
        # (DISTCRT, #31). Klickitat's and Pacific's EMS levies read DOR
        # EMS2025; Asotin's PUD seat DOR PUD2025 and its Rural EMS District
        # No. 2 levy the district's DOR TCA2025 tax code areas (RURALEMSDST,
        # #31). Adams's Fire District 4 and Park District 2 levies read DOR
        # FIR2025 and PKR2025 (#31). Skamania's scopes are all county-wide or
        # Census layers; San Juan's Fire District 4, Port of Lopez and Orcas
        # park measures read DOR FIR2025, PRT2025 and PKR2025, and its Lopez
        # Solid Waste levy SWDDST, a presence layer on DOR PRT2025 (#32).
        self.assertEqual({
            "statewide_complete": True,
            "supported_counties": [{
                "id": "king", "name": "King County", "state": "WA", "fips": "53033",
                "coverage": "full_county", "elections_url": "https://kingcounty.gov/en/dept/elections",
            }, {
                "id": "snohomish", "name": "Snohomish County", "state": "WA", "fips": "53061",
                "coverage": "full_county",
                "elections_url": "https://www.snohomishcountywa.gov/224/Elections-Voter-Registration",
            }, {
                "id": "spokane", "name": "Spokane County", "state": "WA", "fips": "53063",
                "coverage": "partial_county", "elections_url": "https://www.spokanecounty.gov/elections",
            }, {
                "id": "pierce", "name": "Pierce County", "state": "WA", "fips": "53053",
                "coverage": "full_county", "elections_url": "https://www.piercecountywa.gov/elections",
            }, {
                "id": "clark", "name": "Clark County", "state": "WA", "fips": "53011",
                "coverage": "full_county", "elections_url": "https://clark.wa.gov/elections",
            }, {
                "id": "kitsap", "name": "Kitsap County", "state": "WA", "fips": "53035",
                "coverage": "full_county", "elections_url": "https://www.kitsap.gov/auditor/Pages/Elections.aspx",
            }, {
                "id": "thurston", "name": "Thurston County", "state": "WA", "fips": "53067",
                "coverage": "full_county",
                "elections_url": "https://www.thurstoncountywa.gov/departments/auditor/elections",
            }, {
                "id": "yakima", "name": "Yakima County", "state": "WA", "fips": "53077",
                "coverage": "full_county", "elections_url": "https://www.yakimacounty.us/170/Elections",
            }, {
                "id": "whatcom", "name": "Whatcom County", "state": "WA", "fips": "53073",
                "coverage": "full_county", "elections_url": "https://www.whatcomcounty.us/2794/Elections",
            }, {
                "id": "benton", "name": "Benton County", "state": "WA", "fips": "53005",
                "coverage": "full_county",
                "elections_url": "https://www.bentoncountywa.gov/government/elected_officials/auditor/elections/index.php",
            }, {
                "id": "skagit", "name": "Skagit County", "state": "WA", "fips": "53057",
                "coverage": "full_county",
                "elections_url": "https://www.skagitcountywa.gov/government/auditor-s-office/elections-and-voting/",
            }, {
                "id": "cowlitz", "name": "Cowlitz County", "state": "WA", "fips": "53015",
                "coverage": "full_county", "elections_url": "https://www.co.cowlitz.wa.us/2357/Elections",
            }, {
                "id": "grant", "name": "Grant County", "state": "WA", "fips": "53025",
                "coverage": "full_county", "elections_url": "https://www.grantcountywa.gov/270/Elections",
            }, {
                "id": "island", "name": "Island County", "state": "WA", "fips": "53029",
                "coverage": "full_county",
                "elections_url": "https://www.islandcountywa.gov/423/Elections-Voter-Registration",
            }, {
                "id": "lewis", "name": "Lewis County", "state": "WA", "fips": "53041",
                "coverage": "full_county", "elections_url": "https://elections.lewiscountywa.gov/",
            }, {
                "id": "franklin", "name": "Franklin County", "state": "WA", "fips": "53021",
                "coverage": "full_county", "elections_url": "https://www.franklincountywa.gov/Elections",
            }, {
                "id": "chelan", "name": "Chelan County", "state": "WA", "fips": "53007",
                "coverage": "full_county", "elections_url": "https://www.co.chelan.wa.us/elections",
            }, {
                "id": "clallam", "name": "Clallam County", "state": "WA", "fips": "53009",
                "coverage": "full_county",
                "elections_url": "https://www.clallamcountywa.gov/162/Elections-Voter-Registration",
            }, {
                "id": "grays-harbor", "name": "Grays Harbor County", "state": "WA", "fips": "53027",
                "coverage": "full_county",
                "elections_url": "https://www.graysharbor.us/government/Auditors/elections.php",
            }, {
                "id": "mason", "name": "Mason County", "state": "WA", "fips": "53045",
                "coverage": "full_county",
                "elections_url": "https://www.masoncountywa.gov/departments/auditor/elections/index.php",
            }, {
                "id": "walla-walla", "name": "Walla Walla County", "state": "WA", "fips": "53071",
                "coverage": "full_county",
                "elections_url": "https://www.wwcowa.gov/government/auditor/current_election.php",
            }, {
                "id": "stevens", "name": "Stevens County", "state": "WA", "fips": "53065",
                "coverage": "full_county", "elections_url": "https://www.stevenscountywa.gov/20911/Elections",
            }, {
                "id": "whitman", "name": "Whitman County", "state": "WA", "fips": "53075",
                "coverage": "full_county", "elections_url": "https://www.whitmancounty.gov/172/Current-Election",
            }, {
                "id": "douglas", "name": "Douglas County", "state": "WA", "fips": "53017",
                "coverage": "full_county", "elections_url": "https://www.douglascountywa.gov/206/Current-Election",
            }, {
                "id": "okanogan", "name": "Okanogan County", "state": "WA", "fips": "53047",
                "coverage": "partial_county", "elections_url": "https://www.okanogancounty.gov/337/Elections",
            }, {
                "id": "jefferson", "name": "Jefferson County", "state": "WA", "fips": "53031",
                "coverage": "full_county", "elections_url": "https://www.co.jefferson.wa.us/1266/Elections",
            }, {
                "id": "kittitas", "name": "Kittitas County", "state": "WA", "fips": "53037",
                "coverage": "full_county",
                "elections_url": "https://www.co.kittitas.wa.us/auditor/elections/default.aspx",
            }, {
                "id": "klickitat", "name": "Klickitat County", "state": "WA", "fips": "53039",
                "coverage": "partial_county",
                "elections_url": "https://www.klickitatcounty.gov/1136/ElectionsVoter-Registration",
            }, {
                "id": "pacific", "name": "Pacific County", "state": "WA", "fips": "53049",
                "coverage": "partial_county",
            }, {
                "id": "asotin", "name": "Asotin County", "state": "WA", "fips": "53003",
                "coverage": "full_county", "elections_url": "https://www.asotincountywa.gov/186/Current-Election",
            }, {
                "id": "adams", "name": "Adams County", "state": "WA", "fips": "53001",
                "coverage": "full_county", "elections_url": "https://www.co.adams.wa.gov/162/Elections-Elecciones",
            }, {
                "id": "skamania", "name": "Skamania County", "state": "WA", "fips": "53059",
                "coverage": "full_county",
                "elections_url": "https://www.skamaniacounty.gov/departments-offices/auditor/elections/current-election",
            }, {
                "id": "san-juan", "name": "San Juan County", "state": "WA", "fips": "53055",
                "coverage": "full_county", "elections_url": "https://www.sanjuancountywa.gov/1292/Current-Election",
            }],
        }, self.app["coverage"])

    def test_every_scope_is_resolvable_except_the_pud_and_district_court_seats(self):
        unresolved = []
        for item in self.app["contests"] + self.app["measures"]:
            scope = item["scope"]
            if scope["kind"] == "DISTRICT":
                self.assertIn(scope["county"], SHIPPED, item["slug"])
                if scope["layer"] not in election.DISTRICT_ADAPTER_LAYERS[scope["county"]]:
                    unresolved.append((scope["county"], scope["layer"], item["slug"]))
        self.assertEqual({("spokane", "PUDDST"), ("okanogan", "PUDDST"), ("klickitat", "DISTCRT"),
                          ("pacific", "DISTCRT")}, {u[:2] for u in unresolved})
        self.assertEqual(7, len(unresolved))
        everett = self.contests["snohomish-snohomish-county-district-court-everett-district-judge-position-no-1"]
        self.assertEqual({"kind": "DISTRICT", "county": "snohomish", "layer": "DISTCRT",
                          "value": "Everett District Court"}, everett["scope"])
        fd9 = self.measures["spokane-spokane-county-fire-protection-district-no-9-proposition-no-1"]
        self.assertEqual({"kind": "DISTRICT", "county": "spokane", "layer": "FIRDST", "value": "Fire District 9"}, fd9["scope"])
        sd81 = self.measures["spokane-spokane-school-district-no-81-proposition-no-1"]
        self.assertEqual({"kind": "DISTRICT", "county": "spokane", "layer": "SCHDST", "value": "Spokane #81"}, sd81["scope"])
        rfa = self.measures["snohomish-south-snohomish-county-fire-rescue-regional-fire-authority-proposition-no-1"]
        self.assertEqual({"kind": "DISTRICT", "county": "snohomish", "layer": "RFADST", "value": "SCRFA"}, rfa["scope"])
        transit = self.measures["pierce-pierce-transit-proposition-no-1"]
        self.assertEqual({"kind": "DISTRICT", "county": "pierce", "layer": "PTBA", "value": "YES"}, transit["scope"])
        auburn = self.measures["pierce-auburn-school-district-no-408-proposition-no-1"]
        self.assertEqual({"kind": "DISTRICT", "county": "pierce", "layer": "SCHDST",
                          "value": "AUBURN SCHOOL DISTRICT NO. 408"}, auburn["scope"])
        for slug, layer, value in (
            ("clark-battle-ground-school-district-no-119-proposition-no-11", "SCHDST", "119"),
            ("kitsap-south-kitsap-school-district-no-402-proposition-no-1", "SCHDST", "402"),
            ("thurston-yelm-community-schools-proposition-no-1", "SCHDST", "YELM"),
            ("thurston-west-thurston-regional-fire-authority-rochester-littlerock-proposition-no-1", "RFADST", "FD01"),
            ("thurston-thurston-county-fire-protection-district-no-3-lacey-fire-district-3-proposition-no-1",
             "FIRDST", "FD03"),
            ("benton-kiona-benton-city-school-district-no-52-proposition-no-1", "SCHDST", "52"),
            ("whatcom-whatcom-county-fire-protection-district-no-1-proposition-2026-08", "FIRDST", "1"),
            ("skagit-la-conner-school-district-no-311-proposition-no-1", "SCHDST", "311"),
            ("skagit-skagit-county-fire-protection-district-no-5-proposition-no-1", "FIRDST", "5"),
            ("grant-grant-county-fire-protection-district-no-7-proposition-no-1", "FIRDST", "7"),
            ("grant-grant-county-cemetery-district-no-2-wilson-creek-proposition-no-1", "CEMDST", "2"),
            ("grant-grant-county-public-hospital-district-no-4-mckay-healthcare-rehabilitation-proposition-no-1",
             "HOSPDST", "4"),
            ("island-unincorporated-island-county-advisory-vote", "UNINC", "ISLAND"),
            ("island-port-district-of-south-whidbey-island-proposition-no-1", "PORTDST", "S WHIDBEY"),
            ("lewis-timberland-regional-library-district-proposition-no-1", "LIBDST", "L"),
            ("lewis-lewis-county-fire-protection-district-no-6-proposition-no-1", "FIRDST", "6"),
            ("franklin-franklin-county-fire-protection-district-no-3-proposition-no-1", "FIRDST", "3"),
            ("chelan-wenatchee-school-district-no-246-proposition-no-1", "SCHDST", "246"),
            ("clallam-quillayute-valley-school-district-no-402-proposition-no-1", "SCHDST", "402"),
            ("clallam-clallam-county-fire-protection-district-no-6-proposition-no-1", "FIRDST", "6"),
            ("grays-harbor-timberland-regional-library-district-proposition-no-1", "LIBDST", "L"),
            ("grays-harbor-mccleary-school-district-no-65-proposition-no-1", "SCHDST", "65"),
            ("mason-southside-school-district-no-42-proposition-no-1", "SCHDST", "42"),
            ("mason-mccleary-school-district-no-65-proposition-no-1", "SCHDST", "65"),
            ("mason-pioneer-school-district-no-402-proposition-no-1", "SCHDST", "402"),
            ("mason-city-of-shelton-proposition-no-1", "CITY", "Shelton"),
            ("walla-walla-dixie-school-district-no-101-proposition-1", "SCHDST", "101"),
            ("walla-walla-prescott-joint-park-and-recreation-district-proposition-no-1", "PARKDST", "PRES"),
            ("stevens-stevens-county-rural-library-district-proposition-no-2", "LIBDST", "L"),
            ("stevens-stevens-county-fire-protection-district-no-10-proposition-no-1", "FIRDST", "10"),
            ("stevens-nine-mile-falls-school-district-no-325-179-proposition-no-1", "SCHDST", "179J"),
            ("stevens-nine-mile-falls-school-district-no-325-179-proposition-no-2", "SCHDST", "179J"),
            ("whitman-whitman-county-rural-library-district-proposition-no-1", "LIBDST", "L"),
            ("whitman-cheney-school-district-no-360-proposition-no-1", "SCHDST", "316"),
            ("whitman-oakesdale-cemetery-district-no-1-proposition-no-1", "CEMDST", "1"),
            ("whitman-whitman-county-fire-protection-district-no-14-proposition-no-1", "FIRDST", "14"),
            ("whitman-oakesdale-park-recreation-district-no-4-proposition-no-1", "PARKDST", "4"),
            ("whitman-town-of-st-john-proposition-no-1", "CITY", "St. John"),
            ("douglas-eastmont-school-district-no-206-proposition-no-1", "SCHDST", "206"),
            ("douglas-douglas-county-cemetery-district-no-2-proposition-no-1", "CEMDST", "2"),
            ("douglas-douglas-county-public-hospital-district-no-2-proposition-no-1", "HOSPDST", "2"),
            ("douglas-proposed-rimrock-meadows-fire-protection-district-no-9-proposition-no-1", "PROPFIRDST", "009"),
            ("okanogan-methow-valley-emergency-medical-services-district-proposition-no-1", "EMSDST", "MV"),
            ("okanogan-okanogan-county-fire-protection-district-no-1-proposition-no-1", "FIRDST", "1"),
            ("okanogan-public-hospital-district-no-1-okanogan-and-douglas-counties-proposition-no-1", "HOSPDST", "1J"),
            ("okanogan-town-of-twisp-proposition-no-1", "CITY", "Twisp"),
            ("jefferson-quillayute-valley-school-district-no-402-proposition-no-1", "SCHDST", "402"),
            ("jefferson-clallam-county-fire-protection-district-no-1-proposition-no-1", "FIRDST", "9"),
            ("klickitat-emergency-medical-services-district-no-1-klickitat-county-proposition-no-1", "EMSDST", "1"),
            ("pacific-north-pacific-county-emergency-medical-services-district-no-1-proposition-no-1", "EMSDST", "1"),
            ("pacific-pacific-county-fire-protection-district-no-3-proposition-no-1", "FIRDST", "3"),
            ("pacific-pacific-county-fire-protection-district-no-6-proposition-no-1", "FIRDST", "6"),
            ("asotin-asotin-county-rural-ems-district-no-2-proposition-no-1", "RURALEMSDST", "2"),
            ("adams-adams-county-fire-protection-district-no-4-proposition-no-1", "FIRDST", "4"),
            ("adams-adams-county-park-and-recreation-district-no-2-proposition-no-1", "PARKDST", "2"),
            ("san-juan-san-juan-county-fire-protection-district-no-4-lopez-island-fire-ems-proposition-no-1", "FIRDST", "4"),
            ("san-juan-port-of-lopez-proposition-no-1", "PORTDST", "LOPEZ"),
            ("san-juan-orcas-island-park-and-recreation-district-proposition-no-1", "PARKDST", "ORCAS"),
            ("san-juan-lopez-solid-waste-disposal-district-proposition-no-1", "SWDDST", "LOPEZ"),
        ):
            county = next((c for c in ("grays-harbor", "walla-walla", "san-juan") if slug.startswith(f"{c}-")), slug.split("-")[0])
            self.assertEqual({"kind": "DISTRICT", "county": county, "layer": layer, "value": value},
                             self.measures[slug]["scope"])
        self.assertEqual({"kind": "DISTRICT", "county": "benton", "layer": "PUDDST", "value": "Benton PUD"},
                         self.contests["benton-public-utility-district-commissioner-district-2-commissioner-pos-2"]["scope"])
        self.assertEqual({"kind": "DISTRICT", "county": "yakima", "layer": "COUNTY_COUNCIL", "value": "1"},
                         self.contests["yakima-yakima-county-commissioner-district-1-county-commissioner-district-1"]["scope"])
        self.assertEqual({"kind": "DISTRICT", "county": "island", "layer": "PUDDST", "value": "53029"},
                         self.contests["island-public-utility-district-no-1-commissioner-district-1"]["scope"])
        self.assertEqual({"kind": "DISTRICT", "county": "lewis", "layer": "PUDDST", "value": "1"},
                         self.contests["lewis-public-utility-district-commissioner-district-1-commissioner-district-1"]["scope"])
        for slug, layer, value in (
            ("franklin-franklin-county-commissioner-district-3-commissioner-district-3", "COUNTY_COUNCIL", "COM3"),
            ("franklin-port-of-pasco-commissioner-district-3", "PORTDST", "PoP3"),
            ("clallam-clallam-county-district-court-1-judge", "DISTCRT", "1"),
            ("clallam-clallam-county-district-court-2-judge", "DISTCRT", "2"),
            ("clallam-public-utility-district-no-1-of-clallam-county-commissioner-district-no-2", "PUDALL", "1"),
            ("mason-public-utility-district-no-1-of-mason-county-commissioner-district-2", "PUDDST", "1"),
            ("mason-public-utility-district-no-3-of-mason-county-commissioner-district-2", "PUDDST", "3"),
            ("kittitas-lower-kittitas-county-district-court-district-court-judge", "DISTCRT", "Lower District Court"),
            ("kittitas-upper-kittitas-county-district-court-district-court-judge", "DISTCRT", "Upper District Court"),
            ("asotin-asotin-county-public-utility-district-commissioner-district-no-1", "PUDDST", "1"),
        ):
            self.assertEqual({"kind": "DISTRICT", "county": slug.split("-")[0], "layer": layer, "value": value},
                             self.contests[slug]["scope"])
        cemetery = self.measures["king-county-cemetery-district-no-1-proposition-no-1"]
        self.assertEqual({"kind": "DISTRICT", "county": "king", "layer": "CEMDST", "value": "1"}, cemetery["scope"])

    def test_statewide_contests_ship_once_from_the_statewide_package(self):
        slugs = [c["slug"] for c in self.app["contests"]]
        self.assertEqual(len(slugs), len(set(slugs)))
        statewide_owned = [c for c in self.king_contests if c["owner"] == "statewide"]
        self.assertEqual(sorted(c["slug"] for c in self.state_contests), sorted(c["slug"] for c in statewide_owned))
        for source in self.state_contests:
            shipped = self.contests[source["slug"]]
            self.assertEqual("statewide", shipped["owner"])
            self.assertEqual(STATEWIDE, shipped["scope"])
            # The statewide package's own candidates, not King's copies.
            self.assertEqual(sorted(c["slug"] for c in source["candidates"]),
                             sorted(c["slug"] for c in shipped["candidates"]))
        self.assertIn("sean-odonnell", [c["slug"] for c in self.contests["justice-position-no-4-supreme-court"]["candidates"]])

    def test_ballot_is_statewide_plus_king_in_kce_order_then_the_declared_counties(self):
        self.assertEqual([c["slug"] for c in self.king_contests + self.sno_contests + self.spo_contests
                          + self.pie_contests + self.wave2_contests + self.wave3_contests + self.wave3b_contests
                          + self.wave4_contests + self.wave4b_contests + self.mason_contests
                          + self.wave5_contests + self.wave6_contests + self.wave7_contests],
                         [c["slug"] for c in self.app["contests"]])
        self.assertEqual([m["slug"] for m in self.state_measures + self.king_measures + self.sno_measures
                          + self.spo_measures + self.pie_measures + self.wave2_measures + self.wave3_measures
                          + self.wave3b_measures + self.wave4_measures + self.wave4b_measures + self.mason_measures
                          + self.wave5_measures + self.wave6_measures + self.wave7_measures],
                         [m["slug"] for m in self.app["measures"]])
        self.assertEqual((707, 193), (len(self.app["contests"]), len(self.app["measures"])))

    def test_king_records_keep_owner_scope_and_uncontested_verbatim(self):
        for source in self.king_contests:
            if source["owner"] != "king":
                continue
            shipped = self.contests[source["slug"]]
            self.assertEqual("king", shipped["owner"])
            self.assertEqual(source["scope"], shipped["scope"], source["slug"])
            self.assertEqual(source["uncontested"], shipped["uncontested"], source["slug"])
        for source in self.king_measures:
            shipped = self.measures[source["slug"]]
            self.assertEqual(("king", source["scope"]), (shipped["owner"], shipped["scope"]))
        # District Court electoral districts, Seattle courts and council, Court of Appeals.
        self.assertEqual({"kind": "DISTRICT", "county": "king", "layer": "JUDDST", "value": "SH"},
                         self.contests["judge-position-no-1-shoreline-electoral-district"]["scope"])
        self.assertEqual({"kind": "DISTRICT", "county": "king", "layer": "SCCDST", "value": "SCC5"},
                         self.contests["council-district-no-5-city-of-seattle"]["scope"])
        self.assertEqual({"kind": "DISTRICT", "county": "king", "layer": "CITY", "value": "Seattle"},
                         self.contests["municipal-court-judge-position-no-1-city-of-seattle"]["scope"])
        self.assertEqual({"kind": "COUNTY", "county": "king"},
                         self.contests["court-of-appeals-division-1-district-1-judge-position-no-5"]["scope"])

    def test_uncontested_king_contests_are_information_only(self):
        uncontested = [c for c in self.app["contests"] if c["owner"] == "king" and c["uncontested"]]
        self.assertEqual(41, len(uncontested))
        ballot_only = []
        for contest in uncontested:
            (cand,) = contest["candidates"]
            self.assertEqual({}, cand["scores"], contest["slug"])
            scoring = KING / "scoring" / f"{contest['slug']}.json"
            if scoring.exists():
                scored = read(scoring)
                self.assertEqual(scored["office_does"], contest["office_does"])
                self.assertEqual(scored["race_blurb"], contest["race_blurb"])
                self.assertEqual(scored["candidates"][0]["summary"], cand["summary"])
                self.assertEqual(scored["candidates"][0]["highlights"], cand["highlights"])
            else:
                ballot_only.append(contest["slug"])
                self.assertEqual("official-ballot-only", cand["evidence_level"])
                self.assertIsNone(contest["office_does"])
        # The nine uncontested legislative seats have no scoring file in the package.
        self.assertEqual(9, len(ballot_only))
        self.assertTrue(all("legislative-district" in s for s in ballot_only), ballot_only)

    def test_contested_king_candidates_are_researched(self):
        for contest in self.app["contests"]:
            if contest["owner"] != "king" or contest["uncontested"]:
                continue
            self.assertGreaterEqual(len(contest["candidates"]), 2, contest["slug"])
            for cand in contest["candidates"]:
                self.assertNotEqual("official-ballot-only", cand["evidence_level"], cand["slug"])
                self.assertTrue(cand["sources"], cand["slug"])
                self.assertTrue(cand["pamphlet_pages"], cand["slug"])

    def test_pamphlet_pages_come_from_the_dossier_not_endorsement_lists(self):
        def pages(contest, cand):
            found = next(c for c in self.contests[contest]["candidates"] if c["slug"] == cand)
            return [(p["edition"], p["page"]) for p in found["pamphlet_pages"]]
        ed = "voters-pamphlet-edition-0{}-king-{}".format
        self.assertEqual([(ed(4, "seattle"), 24), (ed(6, "south-southeast"), 24)],
                         pages("congressional-district-7-united-states-representative", "pramila-jayapal"))
        # Index false matches (pamphlet-index.json) that must not ship.
        self.assertEqual([(ed(4, "seattle"), 45), (ed(6, "south-southeast"), 44)],
                         pages("state-senator-legislative-district-no-37", "chipalo-street"))
        self.assertEqual([(ed(4, "seattle"), 51)], pages("state-senator-legislative-district-no-46", "javier-valdez"))
        self.assertEqual([(ed(4, "seattle"), 53)],
                         pages("state-representative-position-no-2-legislative-district-no-46", "darya-farivar"))
        self.assertEqual([(ed(4, "seattle"), 48)], pages("state-senator-legislative-district-no-43", "hannah-sabio-howell"))
        self.assertEqual([("local-edition", 37)], pages("judge-position-no-3-west-electoral-district", "rebecca-robertson"))
        self.assertEqual([("local-edition", 43)],
                         pages("municipal-court-judge-position-no-4-city-of-seattle", "anita-crawford-willis"))
        self.assertEqual([("local-edition", 43)],
                         pages("municipal-court-judge-position-no-3-city-of-seattle", "pooja-vaddadi"))
        # The index found no page for these two; their dossiers cite one.
        self.assertEqual([(ed(5, "north-eastside"), 24)],
                         pages("congressional-district-1-united-states-representative", "suzan-delbene"))
        self.assertTrue(pages("congressional-district-8-united-states-representative", "spencer-meline"))
        # No dossier: index pages that carry this contest's own statement heading.
        self.assertEqual([(ed(4, "seattle"), 44)],
                         pages("state-representative-position-no-2-legislative-district-no-36", "liz-berry"))
        self.assertEqual([(ed(5, "north-eastside"), 39)], pages("state-senator-legislative-district-no-45", "manka-dhingra"))
        self.assertEqual([("local-edition", 60), ("local-edition", 61)] + [("local-edition", n) for n in range(76, 81)],
                         [(p["edition"], p["page"]) for p in self.measures["city-of-seattle-proposition-no-1"]["pamphlet_pages"]])

    def test_provenance_names_the_shipped_packages(self):
        for d in (GENERAL.state, KING, SNOHOMISH, SPOKANE, PIERCE, CLARK, KITSAP, THURSTON, YAKIMA, WHATCOM, BENTON,
                  SKAGIT, COWLITZ, GRANT, ISLAND, LEWIS, *WAVE4B, MASON, WALLA_WALLA, STEVENS, WHITMAN, DOUGLAS,
                  OKANOGAN, JEFFERSON, KITTITAS, KLICKITAT, PACIFIC, ASOTIN, ADAMS, SKAMANIA, SAN_JUAN):
            self.assertIn(f"{election.rel(d)}/**", self.app["derived_from"])
        merged = read(GENERAL.final / "scores.json")["derived_from"] + read(
            GENERAL.final / "measures.json")["derived_from"]
        self.assertTrue([d for d in merged if "/counties/king/" in d])
        self.assertTrue([d for d in merged if "/counties/snohomish/" in d])
        self.assertTrue([d for d in merged if "/counties/spokane/" in d])
        for county in SHIPPED:
            self.assertTrue([d for d in merged if f"/counties/{county}/" in d], county)
        self.assertFalse([d for d in merged + self.app["derived_from"]
                          if "/counties/" in d
                          and not any(f"/counties/{c}" in d for c in SHIPPED)])

    def test_statewide_candidates_carry_ballot_order_pamphlet_pages_and_sources(self):
        for source in self.state_contests:
            contest = self.contests[source["slug"]]
            by_slug = {c["slug"]: c for c in source["candidates"]}
            for cand in contest["candidates"]:
                self.assertEqual(by_slug[cand["slug"]]["ballot_order"], cand["ballot_order"])
                self.assertEqual(by_slug[cand["slug"]]["pamphlet_pages"], cand["pamphlet_pages"])
                self.assertTrue(cand["sources"], cand["slug"])

    def test_contests_carry_the_package_term(self):
        for source in self.state_contests:
            self.assertTrue(source["term"], source["slug"])
            self.assertEqual(source["term"], self.contests[source["slug"]]["term"], source["slug"])
        # King's interim contests record no term, so none is invented.
        for source in self.king_contests:
            if source["owner"] == "king":
                self.assertNotIn("term", self.contests[source["slug"]], source["slug"])

    def test_every_measure_is_researched(self):
        # Seven Snohomish charter measures (County Props 3 and 4, Everett
        # 261-265) carry no rubric axis; their scoring says so in sources_note.
        no_axis = []
        for measure in self.app["measures"]:
            for field in ("what_it_does", "cost_line", "pro_summary", "con_summary"):
                self.assertTrue(measure[field], f"{measure['slug']}: {field}")
            if not measure["lean_mappings"]:
                no_axis.append(measure["slug"])
            # Spokane's, Pierce's, Kitsap's, Whatcom's, Benton's, Grant's,
            # Island's, Lewis's, Grays Harbor's, Stevens's, Douglas's,
            # Okanogan's, Pacific's and Adams's (#31) measures cite VoteWA's
            # unpaged online guide (officialLinks.js countyGuides), so they carry no
            # pages; so do Whitman's eight that filed hardship waivers and are
            # not in its printed pamphlet.
            if measure["owner"] in ("spokane", "pierce", "kitsap", "whatcom", "benton", "grant", "island", "lewis",
                                    "grays-harbor", "stevens", "douglas", "okanogan", "pacific", "adams") \
                    or measure["slug"] in WHITMAN_UNPRINTED:
                self.assertEqual([], measure["pamphlet_pages"], measure["slug"])
            else:
                self.assertTrue(measure["pamphlet_pages"], measure["slug"])
        # Five Pierce charter amendments (52-55, 58: council meetings,
        # appointed sheriff, ombuds, initiative deadline, juvenile detention
        # office) carry none either, nor do seven Clark charter amendments
        # (19-24, 26) and Kitsap PUD's electric-authority question (#22),
        # nor the two Bellingham charter amendments, Bellingham Initiative
        # 26-01 and Benton City's council-manager proposition (#28), nor
        # Island's non-binding fireworks advisory vote, nor Clallam's three
        # charter amendments (town halls, ethics board, pamphlet text; #29),
        # nor the Port of Lopez's commissioner term-length question (#32).
        self.assertEqual(29, len(no_axis), no_axis)
        self.assertEqual(["san-juan-port-of-lopez-proposition-no-1"],
                         [s for s in no_axis if s.startswith(("skamania-", "san-juan-"))])
        self.assertEqual([f"clallam-clallam-county-proposed-charter-amendment-no-{n}" for n in (1, 2, 3)],
                         [s for s in no_axis if s.startswith(("franklin-", "chelan-", "clallam-", "grays-harbor-"))])
        self.assertEqual(["island-unincorporated-island-county-advisory-vote"],
                         [s for s in no_axis if s.startswith(("island-", "lewis-"))])
        self.assertEqual(7, sum(s.startswith("snohomish-") for s in no_axis), no_axis)
        self.assertEqual(sorted(f"pierce-pierce-county-charter-amendment-no-{n}" for n in (52, 53, 54, 55, 58)),
                         sorted(s for s in no_axis if s.startswith("pierce-")))
        self.assertEqual(sorted(f"clark-clark-county-proposed-charter-amendment-no-{n}" for n in (19, 20, 21, 22, 23, 24, 26)),
                         sorted(s for s in no_axis if s.startswith("clark-")))
        self.assertEqual(["kitsap-kitsap-county-public-utility-district-no-1-proposition-no-1"],
                         [s for s in no_axis if s.startswith("kitsap-")])
        self.assertEqual(["whatcom-city-of-bellingham-proposition-2026-06", "whatcom-city-of-bellingham-proposition-2026-07",
                          "whatcom-city-of-bellingham-initiative-26-01", "benton-city-of-benton-city-proposition-no-1"],
                         [s for s in no_axis if s.startswith(("whatcom-", "benton-"))])


class GeneralSnohomishTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = read(GENERAL.final / "app-data.json")
        cls.contests = {c["slug"]: c for c in cls.app["contests"]}

    def test_races_researched_in_king_ship_once_with_king_scoring(self):
        import shared_contests
        king = {shared_contests.contest_key(c): c for c in self.app["contests"] if c["owner"] == "king"}
        shared = []
        for contest in self.app["contests"]:
            if contest["owner"] != "snohomish" or shared_contests.contest_key(contest) not in king:
                continue
            source = king[shared_contests.contest_key(contest)]
            shared.append(contest["slug"])
            by_slug = {c["slug"]: c for c in source["candidates"]}
            for cand in contest["candidates"]:
                for field in ("scores", "summary", "highlights", "sources", "evidence_level"):
                    self.assertEqual(by_slug[cand["slug"]][field], cand[field], f"{cand['slug']}: {field}")
                # King's pages are in King's pamphlet editions, not Snohomish's.
                self.assertEqual([], cand["pamphlet_pages"])
        self.assertEqual(sorted([
            "snohomish-congressional-district-1-u-s-representative",
            "snohomish-congressional-district-8-u-s-representative",
            "snohomish-legislative-district-1-state-representative-pos-1",
            "snohomish-legislative-district-1-state-representative-pos-2",
            "snohomish-legislative-district-12-state-representative-pos-1",
            "snohomish-legislative-district-12-state-representative-pos-2",
            "snohomish-legislative-district-32-state-senator",
            "snohomish-legislative-district-32-state-representative-pos-1",
            "snohomish-legislative-district-32-state-representative-pos-2",
        ]), sorted(shared))

    def test_supreme_court_ships_once_from_the_statewide_package(self):
        supreme = [c for c in self.app["contests"] if c["category"] == "StateSupremeCourt"]
        self.assertEqual(5, len(supreme))
        self.assertEqual({"statewide"}, {c["owner"] for c in supreme})
        self.assertFalse([c for c in self.app["contests"] if c["owner"] == "snohomish" and "supreme" in c["slug"]])

    def test_snohomish_candidates_carry_their_own_pamphlet_pages(self):
        larsen = next(c for c in self.contests["snohomish-congressional-district-2-u-s-representative"]["candidates"]
                      if c["slug"] == "rick-larsen")
        self.assertTrue(larsen["pamphlet_pages"])
        self.assertEqual({"local-voters-pamphlet"}, {p["edition"] for p in larsen["pamphlet_pages"]})
        for contest in self.app["contests"]:
            if contest["owner"] != "snohomish":
                continue
            for cand in contest["candidates"]:
                self.assertIn("pamphlet_pages", cand, cand["slug"])


class GeneralSpokaneTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = read(GENERAL.final / "app-data.json")
        cls.measures = {m["slug"]: m for m in cls.app["measures"]}

    def test_spokane_ships_its_own_research_only(self):
        import shared_contests
        # Franklin's CD 5 and Chelan's LD 7 copies ship with Spokane's research
        # (#29), as do Walla Walla's CD 5, Stevens's CD 5, LD 7 and Stevens
        # PUD copies, Whitman's CD 5 and LD 9 House copies and Douglas's and
        # Okanogan's LD 7 copies (#30), and Asotin's and Adams's CD 5 and LD 9
        # copies (#31). Stevens's Court of Appeals III-1 Pos. 2 copy is its own
        # information-only entry, as each county's Court of Appeals copy is.
        others = {shared_contests.contest_key(c) for c in self.app["contests"]
                  if c["owner"] not in ("spokane", "franklin", "chelan", "walla-walla", "stevens", "whitman", "douglas",
                                        "okanogan", "asotin", "adams")}
        spokane = [c for c in self.app["contests"] if c["owner"] == "spokane"]
        self.assertEqual(31, len(spokane))
        self.assertEqual(15, sum(1 for c in spokane if c["uncontested"]))
        self.assertFalse([c["slug"] for c in spokane if shared_contests.contest_key(c) in others])
        self.assertFalse([c for c in spokane if "supreme" in c["slug"]])
        self.assertEqual(20, sum(1 for m in self.app["measures"] if m["owner"] == "spokane"))

    def test_spokane_cites_the_unpaged_votewa_guide(self):
        # pamphlet_refs.py finds no page in a VoteWA guide citation; the app
        # links officialLinks.js countyGuides.spokane instead.
        for contest in self.app["contests"]:
            if contest["owner"] == "spokane":
                for cand in contest["candidates"]:
                    self.assertEqual([], cand["pamphlet_pages"], cand["slug"])

    def test_fire_district_3_spending_mapping_added_by_refutation(self):
        mappings = self.measures["spokane-spokane-county-fire-protection-district-no-3-proposition-no-1"]["lean_mappings"]
        self.assertEqual({"taxes", "spending"}, set(mappings))
        self.assertEqual(1, mappings["spending"]["direction"])
        self.assertTrue(mappings["spending"].get("added_by_refutation"))


class GeneralPierceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = read(GENERAL.final / "app-data.json")
        cls.contests = {c["slug"]: c for c in cls.app["contests"]}
        cls.measures = {m["slug"]: m for m in cls.app["measures"]}

    def test_pierce_counts(self):
        pierce = [c for c in self.app["contests"] if c["owner"] == "pierce"]
        self.assertEqual(43, len(pierce))
        self.assertEqual(16, sum(1 for c in pierce if c["uncontested"]))
        self.assertFalse([c for c in pierce if "supreme" in c["slug"]])
        self.assertEqual(14, sum(1 for m in self.app["measures"] if m["owner"] == "pierce"))

    def test_races_researched_in_king_ship_once_with_king_scoring(self):
        import shared_contests
        king = {shared_contests.contest_key(c): c for c in self.app["contests"] if c["owner"] == "king"}
        shared = []
        for contest in self.app["contests"]:
            if contest["owner"] != "pierce" or shared_contests.contest_key(contest) not in king:
                continue
            source = king[shared_contests.contest_key(contest)]
            shared.append(contest["slug"])
            by_slug = {c["slug"]: c for c in source["candidates"]}
            for cand in contest["candidates"]:
                for field in ("scores", "summary", "highlights", "sources", "evidence_level"):
                    self.assertEqual(by_slug[cand["slug"]][field], cand[field], f"{cand['slug']}: {field}")
                self.assertEqual([], cand["pamphlet_pages"])
        sec = "pierce-king-county-district-court-southeast-electoral-district-judge-position-no-{}".format
        # CD 8, LD 31 and the contested Southeast Position 5, plus the five
        # uncontested Southeast seats, whose King info-only scoring ships too.
        self.assertEqual(sorted([
            "pierce-congressional-district-8-u-s-representative",
            "pierce-legislative-district-31-state-senator",
            "pierce-legislative-district-31-state-representative-pos-1",
            "pierce-legislative-district-31-state-representative-pos-2",
        ] + [sec(n) for n in range(1, 7)]), sorted(shared))
        self.assertEqual({"kind": "DISTRICT", "county": "pierce", "layer": "KCDISTCRT", "value": "YES"},
                         self.contests[sec(5)]["scope"])
        # King's own copy keeps King's scope; a voter sees one or the other.
        self.assertEqual({"kind": "DISTRICT", "county": "king", "layer": "JUDDST", "value": "SE"},
                         self.contests["judge-position-no-5-southeast-electoral-district"]["scope"])

    def test_measures_in_king_and_pierce_are_scoped_to_their_own_county(self):
        for king_slug in ("city-of-milton-proposition-no-1", "auburn-school-district-no-408-proposition-no-1"):
            self.assertEqual("king", self.measures[king_slug]["scope"]["county"])
            self.assertEqual("pierce", self.measures[f"pierce-{king_slug}"]["scope"]["county"])

    def test_pierce_federal_and_legislative_candidates_cite_sos_edition_09(self):
        pages = [(p["edition"], p["page"]) for c in self.contests["pierce-congressional-district-6-u-s-representative"]
                 ["candidates"] for p in c["pamphlet_pages"]]
        self.assertEqual([("voters-pamphlet-edition-09-pierce", 24), ("voters-pamphlet-edition-09-pierce", 25)], pages)
        for contest in self.app["contests"]:
            if contest["owner"] != "pierce":
                continue
            for cand in contest["candidates"]:
                for p in cand["pamphlet_pages"]:
                    self.assertEqual("voters-pamphlet-edition-09-pierce", p["edition"], cand["slug"])


class GeneralWave2Test(unittest.TestCase):
    """Clark, Kitsap and Thurston (#22): counts, races shipped with another
    package's research, and pamphlet editions."""

    @classmethod
    def setUpClass(cls):
        cls.app = read(GENERAL.final / "app-data.json")
        cls.contests = {c["slug"]: c for c in cls.app["contests"]}

    def test_counts(self):
        for county, contests, uncontested, measures in (("clark", 25, 9, 12), ("kitsap", 22, 8, 2), ("thurston", 28, 9, 4)):
            own = [c for c in self.app["contests"] if c["owner"] == county]
            self.assertEqual((contests, uncontested, measures),
                             (len(own), sum(c["uncontested"] for c in own),
                              sum(1 for m in self.app["measures"] if m["owner"] == county)), county)
            self.assertFalse([c for c in own if "supreme" in c["slug"]])

    def test_shared_races_ship_with_the_researching_package(self):
        shared = {
            "kitsap-congressional-district-6-u-s-representative": "pierce-congressional-district-6-u-s-representative",
            "thurston-congressional-district-10-u-s-representative": "pierce-congressional-district-10-u-s-representative",
            "thurston-congressional-district-3-u-s-representative": "clark-congressional-district-3-u-s-representative",
        }
        for office in ("state-senator", "state-representative-pos-1", "state-representative-pos-2"):
            shared[f"kitsap-legislative-district-26-{office}"] = f"pierce-legislative-district-26-{office}"
            shared[f"thurston-legislative-district-35-{office}"] = f"kitsap-legislative-district-35-{office}"
        for pos in (1, 2):
            shared[f"thurston-legislative-district-2-state-representative-pos-{pos}"] = \
                f"pierce-legislative-district-2-state-representative-pos-{pos}"
            shared[f"thurston-legislative-district-20-state-representative-pos-{pos}"] = \
                f"clark-legislative-district-20-state-representative-pos-{pos}"
        self.assertEqual(13, len(shared))
        for slug, owner_slug in shared.items():
            shipped, source = self.contests[slug], self.contests[owner_slug]
            by_slug = {c["slug"]: c for c in source["candidates"]}
            self.assertEqual(sorted(by_slug), sorted(c["slug"] for c in shipped["candidates"]), slug)
            for cand in shipped["candidates"]:
                self.assertTrue(cand["scores"], f"{slug}: {cand['slug']}")
                for field in ("scores", "summary", "highlights", "sources", "evidence_level"):
                    self.assertEqual(by_slug[cand["slug"]][field], cand[field], f"{slug}: {cand['slug']}: {field}")
                # The researching package's pages are in its own pamphlet.
                self.assertEqual([], cand["pamphlet_pages"], slug)

    def test_pamphlet_editions(self):
        editions = {county: set() for county in ("clark", "kitsap", "thurston")}
        for contest in self.app["contests"]:
            if contest["owner"] in editions:
                for cand in contest["candidates"]:
                    editions[contest["owner"]] |= {p["edition"] for p in cand["pamphlet_pages"]}
        self.assertEqual({"clark": {"local-voters-pamphlet"}, "kitsap": set(),
                          "thurston": {"local-voters-pamphlet", "voters-pamphlet-edition-27-thurston"}}, editions)
        walsh = next(c for c in self.contests["thurston-legislative-district-19-state-representative-pos-1"]["candidates"]
                     if c["slug"] == "jim-walsh")
        self.assertEqual([{"edition": "voters-pamphlet-edition-27-thurston", "page": 31}], walsh["pamphlet_pages"])


class GeneralWave3Test(unittest.TestCase):
    """Yakima, Whatcom and Benton (#28): counts, races shipped with another
    package's research, and no pamphlet pages (all three cite VoteWA)."""

    @classmethod
    def setUpClass(cls):
        cls.app = read(GENERAL.final / "app-data.json")
        cls.contests = {c["slug"]: c for c in cls.app["contests"]}

    def test_counts(self):
        for county, contests, uncontested, measures in (("yakima", 19, 8, 0), ("whatcom", 12, 2, 5), ("benton", 27, 14, 3)):
            own = [c for c in self.app["contests"] if c["owner"] == county]
            self.assertEqual((contests, uncontested, measures),
                             (len(own), sum(c["uncontested"] for c in own),
                              sum(1 for m in self.app["measures"] if m["owner"] == county)), county)
            self.assertFalse([c for c in own if "supreme" in c["slug"]])

    def test_shared_races_ship_with_the_researching_package(self):
        shared = {
            "yakima-congressional-district-4-u-s-representative": "benton-congressional-district-4-u-s-representative",
            "whatcom-congressional-district-2-u-s-representative": "snohomish-congressional-district-2-u-s-representative",
        }
        for ld in (14, 15):
            for pos in (1, 2):
                shared[f"benton-legislative-district-{ld}-state-representative-pos-{pos}"] = (
                    f"yakima-legislative-district-{ld}-state-representative-pos-{pos}")
        self.assertEqual(6, len(shared))
        for slug, owner_slug in shared.items():
            shipped, source = self.contests[slug], self.contests[owner_slug]
            by_slug = {c["slug"]: c for c in source["candidates"]}
            self.assertEqual(sorted(by_slug), sorted(c["slug"] for c in shipped["candidates"]), slug)
            for cand in shipped["candidates"]:
                self.assertTrue(cand["scores"], f"{slug}: {cand['slug']}")
                for field in ("scores", "summary", "highlights", "sources", "evidence_level"):
                    self.assertEqual(by_slug[cand["slug"]][field], cand[field], f"{slug}: {cand['slug']}: {field}")
                self.assertEqual([], cand["pamphlet_pages"], slug)

    def test_no_pamphlet_pages(self):
        for item in self.app["contests"]:
            if item["owner"] in ("yakima", "whatcom", "benton"):
                for cand in item["candidates"]:
                    self.assertEqual([], cand["pamphlet_pages"], f"{item['slug']}: {cand['slug']}")
        for m in self.app["measures"]:
            if m["owner"] in ("yakima", "whatcom", "benton"):
                self.assertEqual([], m["pamphlet_pages"], m["slug"])


class GeneralWave3bTest(unittest.TestCase):
    """Skagit, Cowlitz and Grant (#28): counts, races shipped with another
    package's research, and pamphlet pages (Skagit and Cowlitz cite their
    local pamphlets; Grant prints none and cites VoteWA)."""

    @classmethod
    def setUpClass(cls):
        cls.app = read(GENERAL.final / "app-data.json")
        cls.contests = {c["slug"]: c for c in cls.app["contests"]}
        cls.measures = {m["slug"]: m for m in cls.app["measures"]}

    def test_counts(self):
        for county, contests, uncontested, measures in (("skagit", 19, 5, 4), ("cowlitz", 18, 9, 1), ("grant", 21, 11, 5)):
            own = [c for c in self.app["contests"] if c["owner"] == county]
            self.assertEqual((contests, uncontested, measures),
                             (len(own), sum(c["uncontested"] for c in own),
                              sum(1 for m in self.app["measures"] if m["owner"] == county)), county)
            self.assertFalse([c for c in own if "supreme" in c["slug"]])

    def test_shared_races_ship_with_the_researching_package(self):
        shared = {
            "skagit-congressional-district-2-u-s-representative": "snohomish-congressional-district-2-u-s-representative",
            "cowlitz-congressional-district-3-u-s-representative": "clark-congressional-district-3-u-s-representative",
            "grant-congressional-district-4-u-s-representative": "benton-congressional-district-4-u-s-representative",
        }
        for county, ld, owner in (("skagit", 10, "snohomish"), ("skagit", 39, "snohomish"), ("skagit", 40, "whatcom"),
                                  ("cowlitz", 19, "thurston"), ("cowlitz", 20, "clark"), ("grant", 16, "benton")):
            for pos in (1, 2):
                shared[f"{county}-legislative-district-{ld}-state-representative-pos-{pos}"] = (
                    f"{owner}-legislative-district-{ld}-state-representative-pos-{pos}")
        self.assertEqual(15, len(shared))
        for slug, owner_slug in shared.items():
            shipped, source = self.contests[slug], self.contests[owner_slug]
            by_slug = {c["slug"]: c for c in source["candidates"]}
            self.assertEqual(sorted(by_slug), sorted(c["slug"] for c in shipped["candidates"]), slug)
            for cand in shipped["candidates"]:
                self.assertTrue(cand["scores"], f"{slug}: {cand['slug']}")
                for field in ("scores", "summary", "highlights", "sources", "evidence_level"):
                    self.assertEqual(by_slug[cand["slug"]][field], cand[field], f"{slug}: {cand['slug']}: {field}")
                # Another package's pages are in its own pamphlet.
                self.assertEqual([], cand["pamphlet_pages"], slug)

    def test_grant_researches_ld_13_and_ships_its_own_court_of_appeals_copy(self):
        for slug in ("grant-legislative-district-13-state-representative-pos-1",
                     "grant-legislative-district-13-state-representative-pos-2"):
            for cand in self.contests[slug]["candidates"]:
                self.assertTrue(cand["scores"], f"{slug}: {cand['slug']}")
        coa = self.contests["grant-court-of-appeals-division-3-district-2-judge-position-1"]
        self.assertEqual({"kind": "COUNTY", "county": "grant"}, coa["scope"])
        self.assertTrue(coa["uncontested"])

    def test_pamphlet_pages(self):
        local = [{"edition": "local-voters-pamphlet", "page": p} for p in (18, 19, 20, 21)]
        self.assertEqual(local, [m["pamphlet_pages"][0] for m in self.app["measures"] if m["owner"] == "skagit"])
        self.assertEqual([{"edition": "local-voters-pamphlet", "page": p} for p in (57, 58)],
                         self.measures["cowlitz-city-of-longview-proposition-1"]["pamphlet_pages"])
        # Skagit Auditor candidates on PDF p. 7 (printed p. 45); Cowlitz Clerk p. 47.
        for slug, page in (("skagit-skagit-county-auditor", 7), ("cowlitz-cowlitz-county-clerk", 47)):
            for cand in self.contests[slug]["candidates"]:
                self.assertIn({"edition": "local-voters-pamphlet", "page": page}, cand["pamphlet_pages"], slug)
        for item in self.app["contests"] + self.app["measures"]:
            if item["owner"] == "grant":
                for pages in [c["pamphlet_pages"] for c in item.get("candidates", [])] + [item.get("pamphlet_pages", [])]:
                    self.assertEqual([], pages, item["slug"])


class GeneralWave4Test(unittest.TestCase):
    """Island and Lewis (#29): counts, races shipped with another package's
    research, and pages (neither prints a general pamphlet; both cite
    VoteWA)."""

    @classmethod
    def setUpClass(cls):
        cls.app = read(GENERAL.final / "app-data.json")
        cls.contests = {c["slug"]: c for c in cls.app["contests"]}

    def test_counts(self):
        for county, contests, uncontested, measures in (("island", 13, 3, 3), ("lewis", 16, 6, 3)):
            own = [c for c in self.app["contests"] if c["owner"] == county]
            self.assertEqual((contests, uncontested, measures),
                             (len(own), sum(c["uncontested"] for c in own),
                              sum(1 for m in self.app["measures"] if m["owner"] == county)), county)
            self.assertFalse([c for c in own if "supreme" in c["slug"]])

    def test_shared_races_ship_with_the_researching_package(self):
        shared = {
            "island-congressional-district-2-u-s-representative": "snohomish-congressional-district-2-u-s-representative",
            "island-public-utility-district-no-1-commissioner-district-1":
                "snohomish-public-utility-district-no-1-commissioner-district-1",
            "lewis-congressional-district-3-u-s-representative": "clark-congressional-district-3-u-s-representative",
        }
        for county, ld, owner in (("island", 10, "snohomish"), ("lewis", 19, "thurston"), ("lewis", 20, "clark")):
            for pos in (1, 2):
                shared[f"{county}-legislative-district-{ld}-state-representative-pos-{pos}"] = (
                    f"{owner}-legislative-district-{ld}-state-representative-pos-{pos}")
        self.assertEqual(9, len(shared))
        for slug, owner_slug in shared.items():
            shipped, source = self.contests[slug], self.contests[owner_slug]
            by_slug = {c["slug"]: c for c in source["candidates"]}
            self.assertEqual(sorted(by_slug), sorted(c["slug"] for c in shipped["candidates"]), slug)
            for cand in shipped["candidates"]:
                # Snohomish's PUD seat has no applicable rubric axis.
                if "public-utility" not in slug:
                    self.assertTrue(cand["scores"], f"{slug}: {cand['slug']}")
                for field in ("scores", "summary", "highlights", "sources", "evidence_level"):
                    self.assertEqual(by_slug[cand["slug"]][field], cand[field], f"{slug}: {cand['slug']}: {field}")
                self.assertEqual([], cand["pamphlet_pages"], slug)

    def test_no_pamphlet_pages(self):
        for item in self.app["contests"] + self.app["measures"]:
            if item["owner"] in ("island", "lewis"):
                for pages in [c["pamphlet_pages"] for c in item.get("candidates", [])] + [item.get("pamphlet_pages", [])]:
                    self.assertEqual([], pages, item["slug"])


class GeneralWave4bTest(unittest.TestCase):
    """Franklin, Chelan, Clallam and Grays Harbor (#29): counts, races shipped
    with another package's research, and pages (Franklin, Chelan and Clallam
    cite their local pamphlets; Grays Harbor posts none and cites VoteWA)."""

    @classmethod
    def setUpClass(cls):
        cls.app = read(GENERAL.final / "app-data.json")
        cls.contests = {c["slug"]: c for c in cls.app["contests"]}
        cls.measures = {m["slug"]: m for m in cls.app["measures"]}

    def test_counts(self):
        for county, contests, uncontested, measures in (("franklin", 21, 10, 1), ("chelan", 19, 8, 2),
                                                         ("clallam", 14, 6, 7), ("grays-harbor", 17, 5, 5)):
            own = [c for c in self.app["contests"] if c["owner"] == county]
            self.assertEqual((contests, uncontested, measures),
                             (len(own), sum(c["uncontested"] for c in own),
                              sum(1 for m in self.app["measures"] if m["owner"] == county)), county)
            self.assertFalse([c for c in own if "supreme" in c["slug"]])

    def test_shared_races_ship_with_the_researching_package(self):
        shared = {
            "franklin-congressional-district-4-u-s-representative": "benton-congressional-district-4-u-s-representative",
            "franklin-congressional-district-5-u-s-representative": "spokane-congressional-district-5-u-s-representative",
            "franklin-legislative-district-8-state-senator": "benton-legislative-district-8-state-senator",
            "chelan-congressional-district-8-u-s-representative": "congressional-district-8-united-states-representative",
            "chelan-legislative-district-7-state-senator": "spokane-legislative-district-7-state-senator",
            "clallam-congressional-district-6-u-s-representative": "pierce-congressional-district-6-u-s-representative",
            "grays-harbor-congressional-district-6-u-s-representative": "pierce-congressional-district-6-u-s-representative",
        }
        for county, ld, owner in (("franklin", 14, "yakima"), ("franklin", 16, "benton"), ("grays-harbor", 19, "thurston"),
                                  ("grays-harbor", 24, "clallam")):
            for pos in (1, 2):
                shared[f"{county}-legislative-district-{ld}-state-representative-pos-{pos}"] = (
                    f"{owner}-legislative-district-{ld}-state-representative-pos-{pos}")
        for pos in (1, 2):
            # LD 12 is King's research (#16); King names its own contests.
            shared[f"chelan-legislative-district-12-state-representative-pos-{pos}"] = (
                f"state-representative-position-no-{pos}-legislative-district-no-12")
        self.assertEqual(17, len(shared))
        for slug, owner_slug in shared.items():
            shipped, source = self.contests[slug], self.contests[owner_slug]
            by_slug = {c["slug"]: c for c in source["candidates"]}
            self.assertEqual(sorted(by_slug), sorted(c["slug"] for c in shipped["candidates"]), slug)
            for cand in shipped["candidates"]:
                self.assertTrue(cand["scores"], f"{slug}: {cand['slug']}")
                for field in ("scores", "summary", "highlights", "sources", "evidence_level"):
                    self.assertEqual(by_slug[cand["slug"]][field], cand[field], f"{slug}: {cand['slug']}: {field}")
                self.assertEqual([], cand["pamphlet_pages"], slug)

    def test_clallam_researches_ld_24_for_grays_harbor(self):
        for pos in (1, 2):
            contest = self.contests[f"clallam-legislative-district-24-state-representative-pos-{pos}"]
            self.assertEqual({"kind": "DISTRICT", "county": "clallam", "layer": "LEGDST", "value": "24"}, contest["scope"])
            for cand in contest["candidates"]:
                self.assertTrue(cand["scores"], cand["slug"])
                self.assertTrue(cand["pamphlet_pages"], cand["slug"])

    def test_pamphlet_pages(self):
        self.assertEqual([{"edition": "local-voters-pamphlet", "page": 16}],
                         self.measures["franklin-franklin-county-fire-protection-district-no-3-proposition-no-1"]["pamphlet_pages"])
        self.assertEqual([{"edition": "local-voters-pamphlet", "page": p} for p in (16, 17)],
                         self.measures["chelan-wenatchee-school-district-no-246-proposition-no-1"]["pamphlet_pages"])
        self.assertEqual([{"edition": "local-voters-pamphlet", "page": 58}],
                         self.measures["clallam-quillayute-valley-school-district-no-402-proposition-no-1"]["pamphlet_pages"])
        for cand in self.contests["clallam-clallam-county-district-court-1-judge"]["candidates"]:
            self.assertIn({"edition": "local-voters-pamphlet", "page": 55}, cand["pamphlet_pages"], cand["slug"])
        for item in self.app["contests"] + self.app["measures"]:
            if item["owner"] == "grays-harbor":
                for pages in [c["pamphlet_pages"] for c in item.get("candidates", [])] + [item.get("pamphlet_pages", [])]:
                    self.assertEqual([], pages, item["slug"])


class GeneralMasonTest(unittest.TestCase):
    """Mason (#30): counts, CD 6 and LD 35 shipped with Pierce's and Kitsap's
    research, the two PUDs, and local pamphlet pages."""

    @classmethod
    def setUpClass(cls):
        cls.app = read(GENERAL.final / "app-data.json")
        cls.contests = {c["slug"]: c for c in cls.app["contests"]}
        cls.measures = {m["slug"]: m for m in cls.app["measures"]}

    def test_counts(self):
        own = [c for c in self.app["contests"] if c["owner"] == "mason"]
        self.assertEqual((16, 7, 5), (len(own), sum(c["uncontested"] for c in own),
                                      sum(1 for m in self.app["measures"] if m["owner"] == "mason")))
        self.assertFalse([c for c in own if "supreme" in c["slug"]])

    def test_shared_races_ship_with_the_researching_package(self):
        shared = {
            "mason-congressional-district-6-u-s-representative": "pierce-congressional-district-6-u-s-representative",
            "mason-legislative-district-35-state-senator": "kitsap-legislative-district-35-state-senator",
            "mason-court-of-appeals-division-2-district-2-judge-position-1":
                "kitsap-court-of-appeals-division-2-district-2-judge-position-1",
        }
        for pos in (1, 2):
            shared[f"mason-legislative-district-35-state-representative-pos-{pos}"] = (
                f"kitsap-legislative-district-35-state-representative-pos-{pos}")
        for slug, owner_slug in shared.items():
            shipped, source = self.contests[slug], self.contests[owner_slug]
            by_slug = {c["slug"]: c for c in source["candidates"]}
            self.assertEqual(sorted(by_slug), sorted(c["slug"] for c in shipped["candidates"]), slug)
            for cand in shipped["candidates"]:
                for field in ("scores", "summary", "highlights", "sources", "evidence_level"):
                    self.assertEqual(by_slug[cand["slug"]][field], cand[field], f"{slug}: {cand['slug']}: {field}")
                self.assertEqual([], cand["pamphlet_pages"], slug)
                if not shipped["uncontested"]:
                    self.assertTrue(cand["scores"], f"{slug}: {cand['slug']}")

    def test_pamphlet_pages(self):
        self.assertEqual([{"edition": "local-voters-pamphlet", "page": 28}],
                         self.measures["mason-mccleary-school-district-no-65-proposition-no-1"]["pamphlet_pages"])
        self.assertEqual([{"edition": "local-voters-pamphlet", "page": 30}],
                         self.measures["mason-city-of-shelton-proposition-no-1"]["pamphlet_pages"])
        for cand in self.contests["mason-public-utility-district-no-3-of-mason-county-commissioner-district-2"]["candidates"]:
            self.assertEqual([{"edition": "local-voters-pamphlet", "page": 22}], cand["pamphlet_pages"], cand["slug"])

    def test_mccleary_bond_is_scoped_to_each_county(self):
        # McCleary SD 65 straddles the line; each county's copy is its own.
        for county in ("grays-harbor", "mason"):
            self.assertEqual({"kind": "DISTRICT", "county": county, "layer": "SCHDST", "value": "65"},
                             self.measures[f"{county}-mccleary-school-district-no-65-proposition-no-1"]["scope"])


class GeneralWallaWallaStevensTest(unittest.TestCase):
    """Walla Walla and Stevens (#30): counts, CD 5, LD 16, LD 7 and the Stevens
    PUD seat shipped with Benton's and Spokane's research, and pages."""

    @classmethod
    def setUpClass(cls):
        cls.app = read(GENERAL.final / "app-data.json")
        cls.contests = {c["slug"]: c for c in cls.app["contests"]}
        cls.measures = {m["slug"]: m for m in cls.app["measures"]}

    def test_counts(self):
        for county, counts in (("walla-walla", (14, 7, 2)), ("stevens", (16, 9, 4))):
            own = [c for c in self.app["contests"] if c["owner"] == county]
            self.assertEqual(counts, (len(own), sum(c["uncontested"] for c in own),
                                      sum(1 for m in self.app["measures"] if m["owner"] == county)), county)
            self.assertFalse([c for c in own if "supreme" in c["slug"]])

    def test_shared_races_ship_with_the_researching_package(self):
        shared = {
            "walla-walla-congressional-district-5-u-s-representative": "spokane-congressional-district-5-u-s-representative",
            "stevens-congressional-district-5-u-s-representative": "spokane-congressional-district-5-u-s-representative",
            "stevens-legislative-district-7-state-senator": "spokane-legislative-district-7-state-senator",
            "stevens-public-utility-district-no-1-of-stevens-county-commissioner-district-2-pud-commissioner":
                "spokane-public-utility-district-no-1-of-stevens-county-commissioner-district-2-pud-commissioner",
        }
        for pos in (1, 2):
            shared[f"walla-walla-legislative-district-16-state-representative-pos-{pos}"] = (
                f"benton-legislative-district-16-state-representative-pos-{pos}")
            shared[f"stevens-legislative-district-7-state-representative-pos-{pos}"] = (
                f"spokane-legislative-district-7-state-representative-pos-{pos}")
        for slug, owner_slug in shared.items():
            shipped, source = self.contests[slug], self.contests[owner_slug]
            by_slug = {c["slug"]: c for c in source["candidates"]}
            self.assertEqual(sorted(by_slug), sorted(c["slug"] for c in shipped["candidates"]), slug)
            for cand in shipped["candidates"]:
                for field in ("scores", "summary", "highlights", "sources", "evidence_level"):
                    self.assertEqual(by_slug[cand["slug"]][field], cand[field], f"{slug}: {cand['slug']}: {field}")
                # Spokane scored the PUD seat on no axis (none applies).
                if not shipped["uncontested"] and "public-utility" not in slug:
                    self.assertTrue(cand["scores"], f"{slug}: {cand['slug']}")
        # Stevens PUD No. 1 covers the whole county, so Stevens's copy is
        # county-wide; Spokane's stays PUDDST (unresolvable).
        self.assertEqual({"kind": "COUNTY", "county": "stevens"}, self.contests[
            "stevens-public-utility-district-no-1-of-stevens-county-commissioner-district-2-pud-commissioner"]["scope"])

    def test_pamphlet_pages(self):
        # Walla Walla prints a local pamphlet; Stevens's records cite VoteWA only.
        self.assertEqual([{"edition": "local-voters-pamphlet", "page": 24},
                          {"edition": "local-voters-pamphlet", "page": 25}],
                         self.measures["walla-walla-prescott-joint-park-and-recreation-district-proposition-no-1"][
                             "pamphlet_pages"])
        for cand in self.contests["walla-walla-walla-walla-county-sheriff"]["candidates"]:
            self.assertEqual([{"edition": "local-voters-pamphlet", "page": 17}], cand["pamphlet_pages"], cand["slug"])
        for item in self.app["contests"] + self.app["measures"]:
            if item["owner"] == "stevens":
                for pages in [c["pamphlet_pages"] for c in item.get("candidates", [])] + [item.get("pamphlet_pages", [])]:
                    self.assertEqual([], pages, item["slug"])


class GeneralWhitmanDouglasTest(unittest.TestCase):
    """Whitman and Douglas (#30): counts, the shared federal and legislative
    races shipped with Spokane's, Benton's, King's and Grant's research, the
    proposed Rimrock Meadows fire district's scope, and pages."""

    @classmethod
    def setUpClass(cls):
        cls.app = read(GENERAL.final / "app-data.json")
        cls.contests = {c["slug"]: c for c in cls.app["contests"]}
        cls.measures = {m["slug"]: m for m in cls.app["measures"]}

    def test_counts(self):
        for county, counts in (("whitman", (13, 10, 31)), ("douglas", (22, 12, 5))):
            own = [c for c in self.app["contests"] if c["owner"] == county]
            self.assertEqual(counts, (len(own), sum(c["uncontested"] for c in own),
                                      sum(1 for m in self.app["measures"] if m["owner"] == county)), county)
            self.assertFalse([c for c in own if "supreme" in c["slug"]])

    def test_shared_races_ship_with_the_researching_package(self):
        shared = {
            "whitman-congressional-district-5-u-s-representative": "spokane-congressional-district-5-u-s-representative",
            "douglas-congressional-district-4-u-s-representative": "benton-congressional-district-4-u-s-representative",
            "douglas-congressional-district-8-u-s-representative": "congressional-district-8-united-states-representative",
            "douglas-legislative-district-7-state-senator": "spokane-legislative-district-7-state-senator",
            "douglas-legislative-district-13-state-senator": "grant-legislative-district-13-state-senator",
        }
        for pos in (1, 2):
            shared[f"whitman-legislative-district-9-state-representative-pos-{pos}"] = (
                f"spokane-legislative-district-9-state-representative-pos-{pos}")
            shared[f"douglas-legislative-district-7-state-representative-pos-{pos}"] = (
                f"spokane-legislative-district-7-state-representative-pos-{pos}")
            shared[f"douglas-legislative-district-13-state-representative-pos-{pos}"] = (
                f"grant-legislative-district-13-state-representative-pos-{pos}")
        for slug, owner_slug in shared.items():
            shipped, source = self.contests[slug], self.contests[owner_slug]
            by_slug = {c["slug"]: c for c in source["candidates"]}
            self.assertEqual(sorted(by_slug), sorted(c["slug"] for c in shipped["candidates"]), slug)
            for cand in shipped["candidates"]:
                for field in ("scores", "summary", "highlights", "sources", "evidence_level"):
                    self.assertEqual(by_slug[cand["slug"]][field], cand[field], f"{slug}: {cand['slug']}: {field}")
                if not shipped["uncontested"]:
                    self.assertTrue(cand["scores"], f"{slug}: {cand['slug']}")

    def test_rimrock_meadows_is_scoped_to_the_proposed_district(self):
        # Formation and the three initial commissioners are voted on inside the
        # proposed boundary only; its own layer key keeps the primary's
        # Douglas FIRDST scope on DOR.
        rimrock = {"kind": "DISTRICT", "county": "douglas", "layer": "PROPFIRDST", "value": "009"}
        for n in (1, 2, 3):
            self.assertEqual(rimrock, self.contests[
                f"douglas-proposed-rimrock-meadows-fire-protection-district-no-9-commissioner-no-{n}"]["scope"])
        self.assertEqual(rimrock, self.measures[
            "douglas-proposed-rimrock-meadows-fire-protection-district-no-9-proposition-no-1"]["scope"])
        self.assertEqual({"kind": "COUNTY", "county": "douglas"}, self.contests[
            "douglas-public-utility-district-no-1-of-douglas-county-commissioner-district-2"]["scope"])

    def test_pamphlet_pages(self):
        # Whitman prints a local pamphlet (PDF page = printed page); Douglas's
        # records cite VoteWA only.
        self.assertEqual([{"edition": "local-voters-pamphlet", "page": 11}],
                         self.contests["whitman-whitman-county-sheriff"]["candidates"][0]["pamphlet_pages"])
        self.assertTrue(self.measures["whitman-whitman-county-rural-library-district-proposition-no-1"]["pamphlet_pages"])
        for slug in WHITMAN_UNPRINTED:
            self.assertEqual([], self.measures[slug]["pamphlet_pages"], slug)
        for item in self.app["contests"] + self.app["measures"]:
            if item["owner"] == "douglas":
                for pages in [c["pamphlet_pages"] for c in item.get("candidates", [])] + [item.get("pamphlet_pages", [])]:
                    self.assertEqual([], pages, item["slug"])


class GeneralOkanoganTest(unittest.TestCase):
    """Okanogan (#30): counts, the shared federal and legislative races shipped
    with Benton's and Spokane's research, the two PUD seats kept at their true
    PUDDST scope (unresolvable, so hidden), and pages."""

    @classmethod
    def setUpClass(cls):
        cls.app = read(GENERAL.final / "app-data.json")
        cls.contests = {c["slug"]: c for c in cls.app["contests"]}
        cls.measures = {m["slug"]: m for m in cls.app["measures"]}

    def test_counts(self):
        own = [c for c in self.app["contests"] if c["owner"] == "okanogan"]
        self.assertEqual((18, 9, 6), (len(own), sum(c["uncontested"] for c in own),
                                      sum(1 for m in self.app["measures"] if m["owner"] == "okanogan")))
        self.assertFalse([c for c in own if "supreme" in c["slug"]])

    def test_shared_races_ship_with_the_researching_package(self):
        shared = {
            "okanogan-congressional-district-4-u-s-representative": "benton-congressional-district-4-u-s-representative",
            "okanogan-legislative-district-7-state-senator": "spokane-legislative-district-7-state-senator",
            "okanogan-legislative-district-7-state-representative-pos-1": "spokane-legislative-district-7-state-representative-pos-1",
            "okanogan-legislative-district-7-state-representative-pos-2": "spokane-legislative-district-7-state-representative-pos-2",
        }
        for slug, owner_slug in shared.items():
            shipped, source = self.contests[slug], self.contests[owner_slug]
            by_slug = {c["slug"]: c for c in source["candidates"]}
            self.assertEqual(sorted(by_slug), sorted(c["slug"] for c in shipped["candidates"]), slug)
            for cand in shipped["candidates"]:
                for field in ("scores", "summary", "highlights", "sources", "evidence_level"):
                    self.assertEqual(by_slug[cand["slug"]][field], cand[field], f"{slug}: {cand['slug']}: {field}")
                if not shipped["uncontested"]:
                    self.assertTrue(cand["scores"], f"{slug}: {cand['slug']}")

    def test_pud_seats_keep_their_unresolvable_scope(self):
        # The Okanogan PUD seat is on 247 of 248 precincts and Ferry County PUD
        # No. 1's on the other 8; no layer separates them, so both stay PUDDST
        # (app/src/lib/data-consistency.test.js UNRESOLVABLE_SCOPES) and no
        # address sees them. Scoping either COUNTY would show it to the wrong
        # voters.
        for slug, value in (
            ("okanogan-public-utility-district-commissioner-district-1-okanogan-commissioner-dist-1", "1"),
            ("okanogan-public-utility-district-commissioner-district-3-public-utility-commissioner-3", "3"),
        ):
            self.assertEqual({"kind": "DISTRICT", "county": "okanogan", "layer": "PUDDST", "value": value},
                             self.contests[slug]["scope"])
            self.assertNotIn("PUDDST", election.DISTRICT_ADAPTER_LAYERS["okanogan"])
        self.assertEqual({"kind": "COUNTY", "county": "okanogan"}, self.contests[
            "okanogan-okanogan-county-commissioner-district-3-commissioner-district-3"]["scope"])

    def test_no_pamphlet_pages(self):
        # Okanogan prints no local pamphlet; its records cite VoteWA only.
        for item in self.app["contests"] + self.app["measures"]:
            if item["owner"] == "okanogan":
                for pages in [c["pamphlet_pages"] for c in item.get("candidates", [])] + [item.get("pamphlet_pages", [])]:
                    self.assertEqual([], pages, item["slug"])


class GeneralJeffersonKittitasTest(unittest.TestCase):
    """Jefferson and Kittitas (#31): counts, the shared federal and legislative
    races shipped with Pierce's, Clallam's, King's and Grant's research, the
    West End measures and the Upper/Lower District Court scopes, the refuted
    scores, and pages."""

    @classmethod
    def setUpClass(cls):
        cls.app = read(GENERAL.final / "app-data.json")
        cls.contests = {c["slug"]: c for c in cls.app["contests"]}
        cls.measures = {m["slug"]: m for m in cls.app["measures"]}

    def test_counts(self):
        for county, counts in (("jefferson", (13, 8, 2)), ("kittitas", (16, 10, 0))):
            own = [c for c in self.app["contests"] if c["owner"] == county]
            self.assertEqual(counts, (len(own), sum(c["uncontested"] for c in own),
                                      sum(1 for m in self.app["measures"] if m["owner"] == county)), county)
            self.assertFalse([c for c in own if "supreme" in c["slug"]])

    def test_shared_races_ship_with_the_researching_package(self):
        shared = {
            "jefferson-congressional-district-6-u-s-representative": "pierce-congressional-district-6-u-s-representative",
            "kittitas-congressional-district-8-u-s-representative": "congressional-district-8-united-states-representative",
            "kittitas-legislative-district-13-state-senator": "grant-legislative-district-13-state-senator",
        }
        for pos in (1, 2):
            shared[f"jefferson-legislative-district-24-state-representative-pos-{pos}"] = (
                f"clallam-legislative-district-24-state-representative-pos-{pos}")
            shared[f"kittitas-legislative-district-13-state-representative-pos-{pos}"] = (
                f"grant-legislative-district-13-state-representative-pos-{pos}")
        for slug, owner_slug in shared.items():
            shipped, source = self.contests[slug], self.contests[owner_slug]
            by_slug = {c["slug"]: c for c in source["candidates"]}
            self.assertEqual(sorted(by_slug), sorted(c["slug"] for c in shipped["candidates"]), slug)
            for cand in shipped["candidates"]:
                for field in ("scores", "summary", "highlights", "sources", "evidence_level"):
                    self.assertEqual(by_slug[cand["slug"]][field], cand[field], f"{slug}: {cand['slug']}: {field}")
                if not shipped["uncontested"]:
                    self.assertTrue(cand["scores"], f"{slug}: {cand['slug']}")

    def test_scopes(self):
        # The two West End measures belong to Clallam-based districts; DOR
        # numbers Clallam FD 1's Jefferson part '9' (Jefferson's own FD 1 is
        # '1'). Clallam's copies stay scoped to Clallam.
        self.assertEqual({"kind": "DISTRICT", "county": "jefferson", "layer": "SCHDST", "value": "402"},
                         self.measures["jefferson-quillayute-valley-school-district-no-402-proposition-no-1"]["scope"])
        self.assertEqual({"kind": "DISTRICT", "county": "jefferson", "layer": "FIRDST", "value": "9"},
                         self.measures["jefferson-clallam-county-fire-protection-district-no-1-proposition-no-1"]["scope"])
        for county in ("jefferson", "kittitas"):
            self.assertEqual({"kind": "COUNTY", "county": county}, self.contests[
                f"{county}-{county}-county-commissioner-district-3-"
                + ("district-3" if county == "jefferson" else "commissioner-3")]["scope"])
        for side in ("lower", "upper"):
            self.assertEqual(
                {"kind": "DISTRICT", "county": "kittitas", "layer": "DISTCRT", "value": f"{side.title()} District Court"},
                self.contests[f"kittitas-{side}-kittitas-county-district-court-district-court-judge"]["scope"])

    def test_refuted_scores_are_dropped(self):
        for contest, cands in (
            ("kittitas-kittitas-county-coroner", ("cori-mckean", "charlie-divine")),
            ("kittitas-kittitas-county-prosecuting-attorney", ("jodi-hammond", "aaron-reiman")),
            ("kittitas-kittitas-county-sheriff", ("ben-kokjer", "darryl-chepoda-jr")),
        ):
            by_slug = {c["slug"]: c for c in self.contests[contest]["candidates"]}
            for cand in cands:
                self.assertNotIn("reform", by_slug[cand]["scores"], f"{contest}: {cand}")
        nieman = next(c for c in self.contests["jefferson-jefferson-county-commissioner-district-3-district-3"]["candidates"]
                      if c["slug"] == "stephen-t-nieman")
        self.assertNotIn("climate", nieman["scores"])
        self.assertNotIn("reform", nieman["scores"])

    def test_pamphlet_pages(self):
        # Both print a local pamphlet (PDF page = printed page); races shipped
        # with another package's research carry no pages.
        self.assertEqual([{"edition": "local-voters-pamphlet", "page": 9}],
                         self.contests["jefferson-jefferson-county-sheriff"]["candidates"][0]["pamphlet_pages"])
        self.assertEqual([{"edition": "local-voters-pamphlet", "page": 14}], self.measures[
            "jefferson-quillayute-valley-school-district-no-402-proposition-no-1"]["pamphlet_pages"])
        self.assertEqual([{"edition": "local-voters-pamphlet", "page": 15}], self.measures[
            "jefferson-clallam-county-fire-protection-district-no-1-proposition-no-1"]["pamphlet_pages"])
        self.assertEqual([{"edition": "local-voters-pamphlet", "page": 10}], self.contests[
            "kittitas-upper-kittitas-county-district-court-district-court-judge"]["candidates"][0]["pamphlet_pages"])
        for slug in ("jefferson-congressional-district-6-u-s-representative",
                     "kittitas-legislative-district-13-state-representative-pos-1"):
            for cand in self.contests[slug]["candidates"]:
                self.assertEqual([], cand["pamphlet_pages"], slug)


class GeneralKlickitatPacificAsotinTest(unittest.TestCase):
    """Klickitat, Pacific and Asotin (#31): counts, the shared federal and
    legislative races shipped with Benton's, Yakima's, Clark's, Thurston's and
    Spokane's research, the hidden District Court seats, the EMS, fire and
    PUD scopes, the refuted scores, and pages."""

    @classmethod
    def setUpClass(cls):
        cls.app = read(GENERAL.final / "app-data.json")
        cls.contests = {c["slug"]: c for c in cls.app["contests"]}
        cls.measures = {m["slug"]: m for m in cls.app["measures"]}

    def test_counts(self):
        for county, counts in (("klickitat", (16, 8, 1)), ("pacific", (13, 5, 4)), ("asotin", (13, 9, 1))):
            own = [c for c in self.app["contests"] if c["owner"] == county]
            self.assertEqual(counts, (len(own), sum(c["uncontested"] for c in own),
                                      sum(1 for m in self.app["measures"] if m["owner"] == county)), county)
            self.assertFalse([c for c in own if "supreme" in c["slug"]])

    def test_shared_races_ship_with_the_researching_package(self):
        shared = {
            "klickitat-congressional-district-4-u-s-representative": "benton-congressional-district-4-u-s-representative",
            "pacific-congressional-district-3-u-s-representative": "clark-congressional-district-3-u-s-representative",
            "asotin-congressional-district-5-u-s-representative": "spokane-congressional-district-5-u-s-representative",
        }
        for pos in (1, 2):
            shared[f"klickitat-legislative-district-14-state-representative-pos-{pos}"] = (
                f"yakima-legislative-district-14-state-representative-pos-{pos}")
            shared[f"klickitat-legislative-district-17-state-representative-pos-{pos}"] = (
                f"clark-legislative-district-17-state-representative-pos-{pos}")
            shared[f"pacific-legislative-district-19-state-representative-pos-{pos}"] = (
                f"thurston-legislative-district-19-state-representative-pos-{pos}")
            shared[f"asotin-legislative-district-9-state-representative-pos-{pos}"] = (
                f"spokane-legislative-district-9-state-representative-pos-{pos}")
        for slug, owner_slug in shared.items():
            shipped, source = self.contests[slug], self.contests[owner_slug]
            self.assertEqual(source["uncontested"], shipped["uncontested"], slug)
            by_slug = {c["slug"]: c for c in source["candidates"]}
            self.assertEqual(sorted(by_slug), sorted(c["slug"] for c in shipped["candidates"]), slug)
            for cand in shipped["candidates"]:
                for field in ("scores", "summary", "highlights", "sources", "evidence_level"):
                    self.assertEqual(by_slug[cand["slug"]][field], cand[field], f"{slug}: {cand['slug']}: {field}")
                if not shipped["uncontested"]:
                    self.assertTrue(cand["scores"], f"{slug}: {cand['slug']}")

    def test_district_court_seats_stay_hidden_with_their_true_scope(self):
        # No layer of Klickitat's East/West or Pacific's North/South court
        # districts exists: the seats ship, scoped DISTCRT, and no address
        # matches them (app UNRESOLVABLE_SCOPES).
        for slug, value in (
            ("klickitat-klickitat-county-east-district-court-judge", "East"),
            ("klickitat-klickitat-county-west-district-court-judge", "West"),
            ("pacific-pacific-county-district-court-north-district-district-court-judge", "North"),
            ("pacific-pacific-county-district-court-south-district-district-court-judge", "South"),
        ):
            county = slug.split("-")[0]
            self.assertEqual({"kind": "DISTRICT", "county": county, "layer": "DISTCRT", "value": value},
                             self.contests[slug]["scope"])
            self.assertNotIn("DISTCRT", election.DISTRICT_ADAPTER_LAYERS[county])
            self.assertTrue(self.contests[slug]["uncontested"], slug)

    def test_county_wide_seats(self):
        # Commissioners are nominated by district and elected county-wide;
        # Klickitat PUD No. 1 and Pacific PUD No. 2 cover their whole county.
        # Asotin's PUD does not (DOR PUD2025, PUDDST '1').
        for slug in ("klickitat-klickitat-county-commissioner-district-2-county-commissioner-2",
                     "klickitat-public-utility-district-commissioner-district-3-public-utility-district-1-commissioner-pos-3",
                     "pacific-pacific-county-commissioner-district-3-county-commissioner-03",
                     "pacific-public-utility-district-no-2-of-pacific-county-commissioner-district-1",
                     "pacific-timberland-regional-library-district-proposition-no-1",
                     "asotin-asotin-county-commissioner-district-3-county-commissioner-3",
                     "asotin-asotin-county-district-court-district-court-judge"):
            item = self.contests.get(slug) or self.measures[slug]
            self.assertEqual({"kind": "COUNTY", "county": slug.split("-")[0]}, item["scope"], slug)
        self.assertEqual({"kind": "DISTRICT", "county": "asotin", "layer": "PUDDST", "value": "1"},
                         self.contests["asotin-asotin-county-public-utility-district-commissioner-district-no-1"]["scope"])

    def test_refuted_scores_are_dropped(self):
        for contest, cands in (
            ("klickitat-klickitat-county-commissioner-district-2-county-commissioner-2", ("andy-kallinen",)),
            ("klickitat-klickitat-county-klickitat-county-sheriff", ("dwayne-t-matulovich", "tony-warren")),
        ):
            by_slug = {c["slug"]: c for c in self.contests[contest]["candidates"]}
            for cand in cands:
                self.assertNotIn("reform", by_slug[cand]["scores"], f"{contest}: {cand}")
                self.assertTrue(by_slug[cand]["scores"], f"{contest}: {cand}")

    def test_pamphlet_pages(self):
        # Klickitat binds the SOS and local pamphlets (PDF page = printed
        # page); Asotin's local pamphlet is cited by PDF page (printed page -
        # 36); Pacific's dossiers cite VoteWA only. Races shipped with another
        # package's research carry no pages.
        self.assertEqual([{"edition": "local-voters-pamphlet", "page": 51}],
                         self.contests["klickitat-klickitat-county-klickitat-county-sheriff"]["candidates"][0]["pamphlet_pages"])
        self.assertEqual([{"edition": "local-voters-pamphlet", "page": 56}], self.measures[
            "klickitat-emergency-medical-services-district-no-1-klickitat-county-proposition-no-1"]["pamphlet_pages"])
        self.assertEqual([{"edition": "local-voters-pamphlet", "page": 8}],
                         self.contests["asotin-asotin-county-county-sheriff"]["candidates"][0]["pamphlet_pages"])
        self.assertEqual([{"edition": "local-voters-pamphlet", "page": 12}], self.measures[
            "asotin-asotin-county-rural-ems-district-no-2-proposition-no-1"]["pamphlet_pages"])
        for item in [c for c in self.app["contests"] if c["owner"] == "pacific"]:
            for cand in item["candidates"]:
                self.assertEqual([], cand["pamphlet_pages"], item["slug"])
        for item in [m for m in self.app["measures"] if m["owner"] == "pacific"]:
            self.assertEqual([], item["pamphlet_pages"], item["slug"])
        for slug in ("klickitat-congressional-district-4-u-s-representative",
                     "klickitat-legislative-district-17-state-representative-pos-1",
                     "asotin-legislative-district-9-state-representative-pos-2"):
            for cand in self.contests[slug]["candidates"]:
                self.assertEqual([], cand["pamphlet_pages"], slug)


class GeneralAdamsTest(unittest.TestCase):
    """Adams (#31): counts, the shared federal and legislative races shipped
    with Benton's, Spokane's and Grant's research, the county-wide seats, the
    Fire District 4 and Park District 2 levy scopes, and the unpaged VoteWA
    citations (Adams prints no local pamphlet)."""

    @classmethod
    def setUpClass(cls):
        cls.app = read(GENERAL.final / "app-data.json")
        cls.contests = {c["slug"]: c for c in cls.app["contests"]}
        cls.measures = {m["slug"]: m for m in cls.app["measures"]}

    def test_counts(self):
        own = [c for c in self.app["contests"] if c["owner"] == "adams"]
        self.assertEqual((17, 8, 2), (len(own), sum(c["uncontested"] for c in own),
                                      sum(1 for m in self.app["measures"] if m["owner"] == "adams")))
        self.assertFalse([c for c in own if "supreme" in c["slug"]])

    def test_shared_races_ship_with_the_researching_package(self):
        shared = {
            "adams-congressional-district-4-u-s-representative": "benton-congressional-district-4-u-s-representative",
            "adams-congressional-district-5-u-s-representative": "spokane-congressional-district-5-u-s-representative",
            "adams-legislative-district-13-state-senator": "grant-legislative-district-13-state-senator",
        }
        for pos in (1, 2):
            shared[f"adams-legislative-district-9-state-representative-pos-{pos}"] = (
                f"spokane-legislative-district-9-state-representative-pos-{pos}")
            shared[f"adams-legislative-district-13-state-representative-pos-{pos}"] = (
                f"grant-legislative-district-13-state-representative-pos-{pos}")
        for slug, owner_slug in shared.items():
            shipped, source = self.contests[slug], self.contests[owner_slug]
            self.assertEqual(source["uncontested"], shipped["uncontested"], slug)
            by_slug = {c["slug"]: c for c in source["candidates"]}
            self.assertEqual(sorted(by_slug), sorted(c["slug"] for c in shipped["candidates"]), slug)
            for cand in shipped["candidates"]:
                for field in ("scores", "summary", "highlights", "sources", "evidence_level"):
                    self.assertEqual(by_slug[cand["slug"]][field], cand[field], f"{slug}: {cand['slug']}: {field}")
                if not shipped["uncontested"]:
                    self.assertTrue(cand["scores"], f"{slug}: {cand['slug']}")

    def test_county_wide_seats_and_levy_scopes(self):
        # The commissioner is nominated by district and elected county-wide;
        # the District Court is one county-wide court.
        for slug in ("adams-adams-county-commissioner-district-3-county-commissioner-district-3",
                     "adams-adams-county-district-court-judge-position-no-1",
                     "adams-adams-county-district-court-judge-position-no-2",
                     "adams-court-of-appeals-division-3-district-2-judge-position-1"):
            self.assertEqual({"kind": "COUNTY", "county": "adams"}, self.contests[slug]["scope"], slug)
        for slug, layer, value in (
            ("adams-adams-county-fire-protection-district-no-4-proposition-no-1", "FIRDST", "4"),
            ("adams-adams-county-park-and-recreation-district-no-2-proposition-no-1", "PARKDST", "2"),
        ):
            measure = self.measures[slug]
            self.assertEqual({"kind": "DISTRICT", "county": "adams", "layer": layer, "value": value}, measure["scope"])
            self.assertIn(layer, election.DISTRICT_ADAPTER_LAYERS["adams"])
            self.assertEqual({"taxes"}, set(measure["lean_mappings"]), slug)
            self.assertEqual(1, measure["lean_mappings"]["taxes"]["direction"], slug)

    def test_votewa_citations_carry_no_pages(self):
        for item in [c for c in self.app["contests"] if c["owner"] == "adams"]:
            for cand in item["candidates"]:
                self.assertEqual([], cand["pamphlet_pages"], f"{item['slug']}: {cand['slug']}")
        for item in [m for m in self.app["measures"] if m["owner"] == "adams"]:
            self.assertEqual([], item["pamphlet_pages"], item["slug"])


class GeneralSkamaniaSanJuanTest(unittest.TestCase):
    """Skamania and San Juan (#32): counts, the shared federal and legislative
    races shipped with Clark's, Snohomish's and Whatcom's research, the
    county-wide seats, San Juan's four measure scopes, and pamphlet pages
    (Skamania's PDF pages run 34 behind the printed ones; San Juan's equal
    them)."""

    @classmethod
    def setUpClass(cls):
        cls.app = read(GENERAL.final / "app-data.json")
        cls.contests = {c["slug"]: c for c in cls.app["contests"]}
        cls.measures = {m["slug"]: m for m in cls.app["measures"]}

    def test_counts(self):
        for county, expected in (("skamania", (12, 5, 0)), ("san-juan", (11, 6, 4))):
            own = [c for c in self.app["contests"] if c["owner"] == county]
            self.assertEqual(expected, (len(own), sum(c["uncontested"] for c in own),
                                        sum(1 for m in self.app["measures"] if m["owner"] == county)), county)
            self.assertFalse([c for c in own if "supreme" in c["slug"]], county)

    def test_shared_races_ship_with_the_researching_package(self):
        shared = {
            "skamania-congressional-district-3-u-s-representative": "clark-congressional-district-3-u-s-representative",
            "san-juan-congressional-district-2-u-s-representative":
                "snohomish-congressional-district-2-u-s-representative",
        }
        for pos in (1, 2):
            shared[f"skamania-legislative-district-17-state-representative-pos-{pos}"] = (
                f"clark-legislative-district-17-state-representative-pos-{pos}")
            shared[f"san-juan-legislative-district-40-state-representative-pos-{pos}"] = (
                f"whatcom-legislative-district-40-state-representative-pos-{pos}")
        for slug, owner_slug in shared.items():
            shipped, source = self.contests[slug], self.contests[owner_slug]
            self.assertEqual(source["uncontested"], shipped["uncontested"], slug)
            by_slug = {c["slug"]: c for c in source["candidates"]}
            self.assertEqual(sorted(by_slug), sorted(c["slug"] for c in shipped["candidates"]), slug)
            for cand in shipped["candidates"]:
                for field in ("scores", "summary", "highlights", "sources", "evidence_level"):
                    self.assertEqual(by_slug[cand["slug"]][field], cand[field], f"{slug}: {cand['slug']}: {field}")
                self.assertTrue(cand["scores"], f"{slug}: {cand['slug']}")

    def test_county_wide_seats_and_measure_scopes(self):
        # Skamania's commissioner and PUD seats are nominated by district and
        # elected county-wide (the PUD is the whole county); San Juan's
        # council residency district is a candidate qualification, voted on
        # county-wide.
        for slug in ("skamania-skamania-county-commissioner-district-3-commissioner-no-3",
                     "skamania-public-utility-district-no-1-of-skamania-county-commissioner-district-3-commissioner-3",
                     "skamania-skamania-county-district-court-district-court-judge",
                     "san-juan-san-juan-county-council-residency-district-3",
                     "san-juan-san-juan-county-district-court-judge"):
            county = "skamania" if slug.startswith("skamania-") else "san-juan"
            self.assertEqual({"kind": "COUNTY", "county": county}, self.contests[slug]["scope"], slug)
        for slug, layer, value, taxes in (
            ("san-juan-san-juan-county-fire-protection-district-no-4-lopez-island-fire-ems-proposition-no-1",
             "FIRDST", "4", 2),
            ("san-juan-port-of-lopez-proposition-no-1", "PORTDST", "LOPEZ", None),
            ("san-juan-orcas-island-park-and-recreation-district-proposition-no-1", "PARKDST", "ORCAS", 1),
            ("san-juan-lopez-solid-waste-disposal-district-proposition-no-1", "SWDDST", "LOPEZ", 1),
        ):
            measure = self.measures[slug]
            self.assertEqual({"kind": "DISTRICT", "county": "san-juan", "layer": layer, "value": value},
                             measure["scope"])
            self.assertIn(layer, election.DISTRICT_ADAPTER_LAYERS["san-juan"])
            if taxes is None:
                self.assertEqual({}, measure["lean_mappings"], slug)
            else:
                self.assertEqual({"taxes"}, set(measure["lean_mappings"]), slug)
                self.assertEqual(taxes, measure["lean_mappings"]["taxes"]["direction"], slug)

    def test_pamphlet_pages(self):
        # Skamania: PDF pp. 6-10 (printed 40-44); San Juan: printed = PDF pp. 42-57.
        assessor = self.contests["skamania-skamania-county-assessor"]
        self.assertEqual([[{"edition": "local-voters-pamphlet", "page": 6}]] * 2,
                         [c["pamphlet_pages"] for c in assessor["candidates"]])
        pud = self.contests["skamania-public-utility-district-no-1-of-skamania-county-commissioner-district-3-commissioner-3"]
        self.assertEqual({10}, {p["page"] for c in pud["candidates"] for p in c["pamphlet_pages"]})
        self.assertEqual([{"edition": "local-voters-pamphlet", "page": 56}, {"edition": "local-voters-pamphlet", "page": 57}],
                         self.measures["san-juan-lopez-solid-waste-disposal-district-proposition-no-1"]["pamphlet_pages"])
        for county in ("skamania", "san-juan"):
            for item in [c for c in self.app["contests"] if c["owner"] == county]:
                local = item["scope"]["kind"] == "COUNTY"
                for cand in item["candidates"]:
                    # County seats cite the local pamphlet; CD and LD copies
                    # drop the owner's pages (another county's pamphlet).
                    self.assertEqual(local, bool(cand["pamphlet_pages"]), f"{item['slug']}: {cand['slug']}")


class GeneralRefutationsAppliedTest(unittest.TestCase):
    """merge_scores.py applies `adjust`, `refuted` and medium/high `missing`
    verdicts, for candidates and measures."""

    @classmethod
    def setUpClass(cls):
        app = read(GENERAL.final / "app-data.json")
        cls.cands = {
            (con["slug"], cand["slug"]): cand for con in app["contests"] for cand in con["candidates"]
        }
        cls.measures = {m["slug"]: m for m in app["measures"]}

    def scores(self, contest, cand):
        return self.cands[(contest, cand)]["scores"]

    def score(self, position, cand, axis):
        return self.scores(f"justice-position-no-{position}-supreme-court", cand).get(axis)

    def test_statewide_adjust_and_missing_verdicts(self):
        hawk = self.score(3, "jaime-michelle-hawk", "judicial")
        self.assertEqual((1, "low", True), (hawk["score"], hawk["confidence"], hawk["adjusted_by_refutation"]))
        bloom = self.score(7, "todd-a-bloom", "judicial")
        self.assertEqual((-1, "high", True), (bloom["score"], bloom["confidence"], bloom["adjusted_by_refutation"]))
        birk = self.score(4, "ian-birk", "safety")
        self.assertEqual((1, "medium", True), (birk["score"], birk["confidence"], birk["added_by_refutation"]))

    def test_king_refuted_scores_are_dropped(self):
        self.assertNotIn("reform", self.scores("state-representative-position-no-1-legislative-district-no-46", "gerry-pollet"))
        self.assertNotIn("spending", self.scores("state-representative-position-no-1-legislative-district-no-48", "osman-salahuddin"))

    def test_king_adjust_and_missing_verdicts(self):
        moon = self.scores("state-representative-position-no-2-legislative-district-no-1", "cliff-moon")["taxes"]
        self.assertEqual((-1, "high", True), (moon["score"], moon["confidence"], moon["adjusted_by_refutation"]))
        goodman = self.scores("state-representative-position-no-1-legislative-district-no-45", "roger-goodman")["immigration"]
        self.assertEqual((1, "medium", True), (goodman["score"], goodman["confidence"], goodman["added_by_refutation"]))

    def test_measure_adjust_verdicts_change_the_direction(self):
        # Both refutations say "adjusted_score": 1 (from 2) on taxes.
        for slug in ("city-of-lake-forest-park-proposition-no-1", "highline-school-district-no-401-proposition-no-1"):
            taxes = self.measures[slug]["lean_mappings"]["taxes"]
            self.assertEqual((1, True), (taxes["direction"], taxes["adjusted_by_refutation"]), slug)

    def test_verdict_counts(self):
        stats = read(GENERAL.final / "scores.json")["verdict_stats"]
        self.assertEqual({"upheld": 2281, "adjust": 199, "refuted": 24, "missing_added": 31, "missing_dropped_low": 12}, stats)


if __name__ == "__main__":
    unittest.main()
