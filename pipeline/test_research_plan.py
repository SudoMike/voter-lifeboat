import json
import unittest

import build_research_plan as brp
import election

PRIMARY = election.Election("2026-08-04-primary")
GENERAL = election.Election("2026-11-03-general")


def dumped(plan):
    return json.dumps(plan, indent=2) + "\n"


class PrimaryPlansFrozenTest(unittest.TestCase):
    def test_every_primary_plan_is_byte_identical(self):
        packages = sorted(p.parent.parent.name for p in PRIMARY.counties.glob("*/interim/research-plan.json"))
        self.assertIn("king", packages)
        for package in packages + ["statewide"]:
            committed = (brp.interim_for(package, PRIMARY.id) / "research-plan.json").read_text()
            self.assertEqual(committed, dumped(brp.plan_for(package, PRIMARY.id)), package)


class GeneralKingPlanTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.plan = brp.plan_for("king", GENERAL.id)
        cls.contests = {c["contest_slug"]: c for c in cls.plan["contests"]}

    def test_statewide_owned_contests_are_left_to_the_statewide_plan(self):
        self.assertEqual("2026-08-04-primary", self.plan["carry_forward_from"])
        self.assertFalse(any("supreme-court" in slug for slug in self.contests))
        self.assertEqual(5, len(self.plan["statewide_owned_contests"]))

    def test_uncontested_contests_are_omitted(self):
        self.assertTrue(all(len(c["candidates"]) >= 2 for c in self.plan["contests"]))

    def test_carry_forward_matches_contest_and_name(self):
        assessor = {c["name"]: c for c in self.contests["assessor"]["candidates"]}
        self.assertEqual("primary", assessor["Rob Foxcurran"]["carry_forward"])
        self.assertEqual(
            "data/washington-state/elections/2026-08-04-primary/counties/king/dossiers/assessor/rob-foxcurran.md",
            assessor["Rob Foxcurran"]["primary_dossier"],
        )
        for contest in self.plan["contests"]:
            for c in contest["candidates"]:
                self.assertEqual(c["carry_forward"] == "primary", c["primary_dossier"] is not None)
                if c["primary_dossier"]:
                    self.assertIn(f"/dossiers/{contest['contest_slug']}/", c["primary_dossier"])

    def test_measures_are_new_and_keep_text_out_of_the_plan(self):
        self.assertEqual(15, len(self.plan["measures"]))
        for m in self.plan["measures"]:
            self.assertEqual("new", m["carry_forward"])
            self.assertNotIn("statements", m)
            self.assertIn("scope", m)


if __name__ == "__main__":
    unittest.main()
