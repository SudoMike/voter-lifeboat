import unittest

import build_dossier_batches


class DossierBatchKeyTest(unittest.TestCase):
    def test_position_two_does_not_match_one_in_district_number(self):
        for district in (16, 18, 21):
            contest = {
                "category": "State",
                "office": "State Representative Pos. 2",
                "district": f"Legislative District {district}",
            }
            self.assertEqual(
                ("State", f"LD{district}", "REP2"),
                build_dossier_batches.fed_state_key(contest),
            )


if __name__ == "__main__":
    unittest.main()
