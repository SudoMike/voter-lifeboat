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


class GeneralPiercePlanTest(unittest.TestCase):
    """The county wave dry run (#20): what Pierce reuses and what it researches."""

    @classmethod
    def setUpClass(cls):
        cls.plan = brp.plan_for("pierce", GENERAL.id)
        cls.contests = {c["contest_slug"]: c for c in cls.plan["contests"]}

    def test_committed_plan_is_current(self):
        committed = (brp.interim_for("pierce", GENERAL.id) / "research-plan.json").read_text()
        self.assertEqual(committed, dumped(self.plan))

    def test_races_king_researched_are_not_researched_again(self):
        elsewhere = {slug: c["shared"]["researched_in"] for slug, c in self.contests.items()
                     if (c.get("shared") or {}).get("researched_in")}
        self.assertEqual({
            "pierce-congressional-district-8-u-s-representative": "congressional-district-8-united-states-representative",
            "pierce-legislative-district-31-state-senator": "state-senator-legislative-district-no-31",
            "pierce-legislative-district-31-state-representative-pos-1": "state-representative-position-no-1-legislative-district-no-31",
            "pierce-legislative-district-31-state-representative-pos-2": "state-representative-position-no-2-legislative-district-no-31",
            "pierce-king-county-district-court-southeast-electoral-district-judge-position-no-5": "judge-position-no-5-southeast-electoral-district",
        }, {slug: r["contest_slug"] for slug, r in elsewhere.items()})
        for r in elsewhere.values():
            self.assertEqual("king", r["package"])
            self.assertEqual([], r["candidates_missing"])

    def test_district_contests_carry_forward_from_the_primary_statewide_dossiers(self):
        ld25 = {c["name"]: c for c in self.contests["pierce-legislative-district-25-state-representative-pos-1"]["candidates"]}
        self.assertEqual(
            "data/washington-state/elections/2026-08-04-primary/statewide/dossiers/"
            "legislative-district-25-state-representative-position-1/michael-keaton.md",
            ld25["Michael Keaton"]["primary_dossier"])
        # LD 25 lies wholly in Pierce: no other package lists it.
        self.assertNotIn("shared", self.contests["pierce-legislative-district-25-state-representative-pos-1"])

    def test_county_contests_carry_forward_from_the_primary_county_dossiers(self):
        d1 = {c["name"]: c for c in self.contests["pierce-pierce-county-council-district-1-county-councilmember"]["candidates"]}
        self.assertEqual("primary", d1["Jerome O'Leary"]["carry_forward"])
        self.assertIn("/2026-08-04-primary/counties/pierce/dossiers/", d1["Jerome O'Leary"]["primary_dossier"])

    def test_races_other_county_packages_also_list_are_flagged(self):
        self.assertEqual(["kitsap", "clallam", "grays-harbor", "mason"], self.contests["pierce-congressional-district-6-u-s-representative"]["shared"]["also_listed_by"])
        self.assertIsNone(self.contests["pierce-congressional-district-6-u-s-representative"]["shared"]["researched_in"])


if __name__ == "__main__":
    unittest.main()
