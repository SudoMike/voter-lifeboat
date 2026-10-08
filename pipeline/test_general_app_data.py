"""The general's shipped data: the statewide package plus King's schema-2
package at Full County Coverage (issues #9 and #16).

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
STATEWIDE = {"kind": "STATEWIDE"}
GEO_JS = election.ROOT / "app/src/lib/geo.js"


def read(path):
    return json.loads(path.read_text())


class GeneralPackagesTest(unittest.TestCase):
    def test_general_ships_the_statewide_package_and_king(self):
        self.assertTrue(election.ELECTION_META[GENERAL.id]["statewide_complete"])
        self.assertEqual(["king"], election.APP_PACKAGES[GENERAL.id]["counties"])
        self.assertEqual([GENERAL.state, KING], GENERAL.shipped_packages())

    def test_king_adapter_layers_match_geo_js(self):
        block = re.search(r"const KING_LAYERS = \{(.*?)\n\}", GEO_JS.read_text(), re.S).group(1)
        keys = re.findall(r"^\s+([A-Z]+):", block, re.M)
        self.assertEqual(sorted(keys), sorted(election.DISTRICT_ADAPTER_LAYERS["king"]))

    def test_county_elections_urls_are_per_election(self):
        self.assertEqual("https://kingcounty.gov/en/dept/elections",
                         election.county_elections_url(GENERAL.id, "king"))
        self.assertIsNone(election.county_elections_url(GENERAL.id, "spokane"))
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

    def test_king_is_a_full_county_supported_county(self):
        self.assertEqual({
            "statewide_complete": True,
            "supported_counties": [{
                "id": "king", "name": "King County", "state": "WA", "fips": "53033",
                "coverage": "full_county", "elections_url": "https://kingcounty.gov/en/dept/elections",
            }],
        }, self.app["coverage"])

    def test_every_king_scope_is_resolvable(self):
        layers = set(election.DISTRICT_ADAPTER_LAYERS["king"])
        for item in self.app["contests"] + self.app["measures"]:
            scope = item["scope"]
            if scope["kind"] == "DISTRICT":
                self.assertEqual("king", scope["county"], item["slug"])
                self.assertIn(scope["layer"], layers, item["slug"])
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

    def test_ballot_is_the_statewide_package_plus_king_in_kce_order(self):
        self.assertEqual([c["slug"] for c in self.king_contests], [c["slug"] for c in self.app["contests"]])
        self.assertEqual([m["slug"] for m in self.state_measures + self.king_measures],
                         [m["slug"] for m in self.app["measures"]])
        self.assertEqual((97, 18), (len(self.app["contests"]), len(self.app["measures"])))

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

    def test_provenance_names_both_packages(self):
        for path in (f"{election.rel(GENERAL.state)}/**", f"{election.rel(KING)}/**"):
            self.assertIn(path, self.app["derived_from"])
        merged = read(GENERAL.final / "scores.json")["derived_from"] + read(
            GENERAL.final / "measures.json")["derived_from"]
        self.assertTrue([d for d in merged if "/counties/king/" in d])
        self.assertFalse([d for d in merged + self.app["derived_from"]
                          if "/counties/" in d and "/counties/king" not in d])

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
        for measure in self.app["measures"]:
            for field in ("what_it_does", "cost_line", "pro_summary", "con_summary"):
                self.assertTrue(measure[field], f"{measure['slug']}: {field}")
            self.assertTrue(measure["lean_mappings"], measure["slug"])
            self.assertTrue(measure["pamphlet_pages"], measure["slug"])


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
        self.assertEqual({"upheld": 628, "adjust": 61, "refuted": 2, "missing_added": 9, "missing_dropped_low": 2}, stats)


if __name__ == "__main__":
    unittest.main()
