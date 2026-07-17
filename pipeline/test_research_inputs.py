import json
import unittest
from pathlib import Path

import build_research_plan
import normalize_research_inputs


ROOT = Path(__file__).resolve().parent.parent


class ResearchInputTest(unittest.TestCase):
    def test_all_counties_have_normalized_king_compatible_shape(self):
        packages = list((ROOT / "data/washington-state/counties").glob("*/interim/contests.json"))
        self.assertEqual(39, len(packages))
        for path in packages:
            for contest in json.loads(path.read_text())["contests"]:
                self.assertTrue({"category", "office", "district", "slug", "candidates"} <= contest.keys())
                for candidate in contest["candidates"]:
                    self.assertTrue({"slug", "name", "party_preference"} <= candidate.keys())

    def test_statewide_is_deduped_district_races(self):
        path = ROOT / "data/washington-state/statewide/interim/contests.json"
        contests = json.loads(path.read_text())["contests"]
        self.assertEqual(94, len(contests))
        self.assertEqual(276, sum(len(c["candidates"]) for c in contests))
        self.assertEqual(len(contests), len({normalize_research_inputs._shared_key(c) for c in contests}))
        self.assertTrue(all(c["counties"] == sorted(set(c["counties"])) for c in contests))

    def test_research_plan_omits_uncontested(self):
        build_research_plan.build("statewide")
        plan = json.loads((ROOT / "data/washington-state/statewide/interim/research-plan.json").read_text())
        self.assertTrue(all(len(c["candidates"]) >= 2 for c in plan["contests"]))
        self.assertTrue(all(c["depth"] == ("deep" if len(c["candidates"]) >= 3 else "light")
                            for c in plan["contests"]))


if __name__ == "__main__":
    unittest.main()
