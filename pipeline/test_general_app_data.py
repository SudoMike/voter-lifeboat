"""The general's shipped data: the statewide package, King's schema-2
package at Full County Coverage (issues #9 and #16), Spokane's app-*.json
package at partial coverage, Pierce's (#21) and Snohomish's (#27) at full
coverage, Clark's, Kitsap's and Thurston's at full coverage (#22), and
Yakima's, Whatcom's and Benton's at full coverage (#28).

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
SHIPPED = ("king", "snohomish", "spokane", "pierce", "clark", "kitsap", "thurston", "yakima", "whatcom", "benton")
STATEWIDE = {"kind": "STATEWIDE"}
GEO_JS = election.ROOT / "app/src/lib/geo.js"


def read(path):
    return json.loads(path.read_text())


class GeneralPackagesTest(unittest.TestCase):
    def test_general_ships_the_statewide_package_and_ten_counties(self):
        self.assertTrue(election.ELECTION_META[GENERAL.id]["statewide_complete"])
        self.assertEqual(list(SHIPPED), election.APP_PACKAGES[GENERAL.id]["counties"])
        self.assertEqual([GENERAL.state, KING, SNOHOMISH, SPOKANE, PIERCE, CLARK, KITSAP, THURSTON,
                          YAKIMA, WHATCOM, BENTON], GENERAL.shipped_packages())

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
            block = re.search(rf"\n  {county}: \[(.*?)\n  \],", text, re.S).group(1)
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
        self.assertIsNone(election.county_elections_url(GENERAL.id, "walla-walla"))
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

    def test_nine_counties_are_full_spokane_partial(self):
        # Spokane is partial_county because its Stevens County PUD seat is
        # scoped to PUDDST, which no public layer resolves. Snohomish's nine
        # District Court seats resolve from the Auditor's Court_Districts
        # layer (DISTCRT, #27). Pierce's KCDISTCRT, PTBA and SCHDST read the
        # Election_Precincts layer. Clark's, Kitsap's and Thurston's school
        # levies and Thurston's WTRFA levy read county layers (#22). Benton's
        # PUD race reads the Auditor's PrecinctSplits layer and its Ki-Be
        # levy DOR SCH2025 (#28).
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
            }],
        }, self.app["coverage"])

    def test_every_scope_is_resolvable_except_spokane_pud(self):
        unresolved = []
        for item in self.app["contests"] + self.app["measures"]:
            scope = item["scope"]
            if scope["kind"] == "DISTRICT":
                self.assertIn(scope["county"], SHIPPED, item["slug"])
                if scope["layer"] not in election.DISTRICT_ADAPTER_LAYERS[scope["county"]]:
                    unresolved.append((scope["county"], scope["layer"], item["slug"]))
        self.assertEqual({("spokane", "PUDDST")}, {u[:2] for u in unresolved})
        self.assertEqual(1, len(unresolved))
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
        ):
            self.assertEqual({"kind": "DISTRICT", "county": slug.split("-")[0], "layer": layer, "value": value},
                             self.measures[slug]["scope"])
        self.assertEqual({"kind": "DISTRICT", "county": "benton", "layer": "PUDDST", "value": "Benton PUD"},
                         self.contests["benton-public-utility-district-commissioner-district-2-commissioner-pos-2"]["scope"])
        self.assertEqual({"kind": "DISTRICT", "county": "yakima", "layer": "COUNTY_COUNCIL", "value": "1"},
                         self.contests["yakima-yakima-county-commissioner-district-1-county-commissioner-district-1"]["scope"])
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
                          + self.pie_contests + self.wave2_contests + self.wave3_contests],
                         [c["slug"] for c in self.app["contests"]])
        self.assertEqual([m["slug"] for m in self.state_measures + self.king_measures + self.sno_measures
                          + self.spo_measures + self.pie_measures + self.wave2_measures + self.wave3_measures],
                         [m["slug"] for m in self.app["measures"]])
        self.assertEqual((339, 95), (len(self.app["contests"]), len(self.app["measures"])))

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
        for d in (GENERAL.state, KING, SNOHOMISH, SPOKANE, PIERCE, CLARK, KITSAP, THURSTON, YAKIMA, WHATCOM, BENTON):
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
            # Spokane's, Pierce's, Kitsap's, Whatcom's and Benton's measures
            # cite VoteWA's unpaged online guide (officialLinks.js
            # countyGuides), so they carry no pages.
            if measure["owner"] in ("spokane", "pierce", "kitsap", "whatcom", "benton"):
                self.assertEqual([], measure["pamphlet_pages"], measure["slug"])
            else:
                self.assertTrue(measure["pamphlet_pages"], measure["slug"])
        # Five Pierce charter amendments (52-55, 58: council meetings,
        # appointed sheriff, ombuds, initiative deadline, juvenile detention
        # office) carry none either, nor do seven Clark charter amendments
        # (19-24, 26) and Kitsap PUD's electric-authority question (#22),
        # nor the two Bellingham charter amendments, Bellingham Initiative
        # 26-01 and Benton City's council-manager proposition (#28).
        self.assertEqual(24, len(no_axis), no_axis)
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
        others = {shared_contests.contest_key(c) for c in self.app["contests"] if c["owner"] != "spokane"}
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
        self.assertEqual({"upheld": 1789, "adjust": 149, "refuted": 6, "missing_added": 24, "missing_dropped_low": 9}, stats)


if __name__ == "__main__":
    unittest.main()
