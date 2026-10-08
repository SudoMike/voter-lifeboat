import json
import unittest

import election
import validate_scoring

GENERAL = election.Election("2026-11-03-general")
PRIMARY = election.Election("2026-08-04-primary")


def applies_for(e):
    return validate_scoring.load_applies(json.loads((e.final / "rubric.json").read_text()))


class RubricAxesTest(unittest.TestCase):
    def test_general_has_fifteen_axes_and_primary_keeps_fourteen(self):
        self.assertEqual(15, len(applies_for(GENERAL)))
        self.assertIn("parental-rights", applies_for(GENERAL))
        self.assertEqual(14, len(applies_for(PRIMARY)))
        self.assertNotIn("parental-rights", applies_for(PRIMARY))

    def test_parental_rights_scores_on_state_legislative_contests(self):
        applies = applies_for(GENERAL)
        self.assertEqual([], validate_scoring.axis_errors(applies, "parental-rights", "State", False))
        self.assertEqual([], validate_scoring.axis_errors(applies, "social", "State", False))

    def test_judges_are_never_scored_on_social_or_parental_rights(self):
        applies = applies_for(GENERAL)
        for axis in ("social", "parental-rights"):
            for category in ("StateSupremeCourt", "DistrictCourt", "Judicial"):
                self.assertTrue(validate_scoring.axis_errors(applies, axis, category, True), (axis, category))
        self.assertEqual([], validate_scoring.axis_errors(applies, "judicial", "StateSupremeCourt", True))

    def test_unknown_axis_is_rejected(self):
        self.assertEqual(
            ["unknown axis nonsense"],
            validate_scoring.axis_errors(applies_for(GENERAL), "nonsense", "State", False),
        )


if __name__ == "__main__":
    unittest.main()
