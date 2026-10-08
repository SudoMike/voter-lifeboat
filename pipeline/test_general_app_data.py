"""The general's shipped data is the statewide package only (issue #9).

These read the committed outputs of merge_scores.py and assemble_app_data.py,
so they fail if the general is re-assembled from the wrong packages or the
refutation verdicts stop being applied.
"""

import json
import unittest

import election

GENERAL = election.Election("2026-11-03-general")
STATEWIDE = {"kind": "STATEWIDE"}


def read(path):
    return json.loads(path.read_text())


class GeneralPackagesTest(unittest.TestCase):
    def test_general_is_statewide_complete_with_no_county_packages(self):
        self.assertTrue(election.ELECTION_META[GENERAL.id]["statewide_complete"])
        self.assertEqual([], election.APP_PACKAGES[GENERAL.id]["counties"])
        self.assertEqual([GENERAL.state], GENERAL.shipped_packages())

    def test_primary_keeps_every_package(self):
        primary = election.Election("2026-08-04-primary")
        self.assertEqual(primary.packages(), primary.shipped_packages())


class GeneralAppDataTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = read(GENERAL.final / "app-data.json")
        cls.contests = read(GENERAL.state / "interim/contests.json")["contests"]
        cls.measures = read(GENERAL.state / "interim/measures.json")["measures"]

    def test_coverage_is_statewide_only(self):
        self.assertEqual({"statewide_complete": True, "supported_counties": []}, self.app["coverage"])

    def test_ballot_is_exactly_the_statewide_package(self):
        self.assertEqual([c["slug"] for c in self.contests], [c["slug"] for c in self.app["contests"]])
        self.assertEqual([m["slug"] for m in self.measures], [m["slug"] for m in self.app["measures"]])
        self.assertEqual(5, len(self.app["contests"]))
        self.assertEqual(3, len(self.app["measures"]))
        for item in self.app["contests"] + self.app["measures"]:
            self.assertEqual("statewide", item["owner"], item["slug"])
            self.assertEqual(STATEWIDE, item["scope"], item["slug"])

    def test_no_county_package_in_provenance(self):
        self.assertFalse([d for d in self.app["derived_from"] if "/counties/" in d])
        merged = read(GENERAL.final / "scores.json")["derived_from"] + read(
            GENERAL.final / "measures.json")["derived_from"]
        self.assertFalse([d for d in merged if "/counties/" in d])

    def test_candidates_carry_ballot_order_pamphlet_pages_and_sources(self):
        for contest, source in zip(self.app["contests"], self.contests):
            by_slug = {c["slug"]: c for c in source["candidates"]}
            for cand in contest["candidates"]:
                self.assertEqual(by_slug[cand["slug"]]["ballot_order"], cand["ballot_order"])
                self.assertEqual(by_slug[cand["slug"]]["pamphlet_pages"], cand["pamphlet_pages"])
                self.assertTrue(cand["sources"], cand["slug"])

    def test_every_measure_is_researched(self):
        for measure in self.app["measures"]:
            for field in ("what_it_does", "cost_line", "pro_summary", "con_summary"):
                self.assertTrue(measure[field], f"{measure['slug']}: {field}")
            self.assertTrue(measure["lean_mappings"], measure["slug"])


class GeneralRefutationsAppliedTest(unittest.TestCase):
    """merge_scores.py applies `adjust` and medium/high `missing` verdicts."""

    @classmethod
    def setUpClass(cls):
        app = read(GENERAL.final / "app-data.json")
        cls.cands = {
            (con["slug"], cand["slug"]): cand for con in app["contests"] for cand in con["candidates"]
        }

    def score(self, position, cand, axis):
        return self.cands[(f"justice-position-no-{position}-supreme-court", cand)]["scores"].get(axis)

    def test_adjust_verdicts(self):
        hawk = self.score(3, "jaime-michelle-hawk", "judicial")
        self.assertEqual((1, "low", True), (hawk["score"], hawk["confidence"], hawk["adjusted_by_refutation"]))
        bloom = self.score(7, "todd-a-bloom", "judicial")
        self.assertEqual((-1, "high", True), (bloom["score"], bloom["confidence"], bloom["adjusted_by_refutation"]))

    def test_missing_verdict_adds_score(self):
        birk = self.score(4, "ian-birk", "safety")
        self.assertEqual((1, "medium", True), (birk["score"], birk["confidence"], birk["added_by_refutation"]))

    def test_verdict_counts(self):
        stats = read(GENERAL.final / "scores.json")["verdict_stats"]
        self.assertEqual({"adjust": 2, "refuted": 0, "missing_added": 1, "missing_dropped_low": 0},
                         {k: v for k, v in stats.items() if k != "upheld"})


if __name__ == "__main__":
    unittest.main()
