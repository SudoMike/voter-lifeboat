import unittest

import election
import shared_contests as sc

GENERAL = election.Election("2026-11-03-general")


def key(category, office, district):
    return sc.contest_key({"category": category, "office": office, "district": district})


class ContestKeyTest(unittest.TestCase):
    def test_congressional_names_from_every_source_agree(self):
        self.assertEqual(("CONGDST", 8), key("Federal", "United States Representative", "Congressional District 8"))
        self.assertEqual(("CONGDST", 8), key("Federal", "U.S. Representative", "Congressional District 8"))

    def test_legislative_seats_from_every_source_agree(self):
        pos1 = ("LEGDST", 31, "representative-position-1")
        self.assertEqual(pos1, key("State", "State Representative Pos. 1", "Legislative District 31"))  # VoteWA
        self.assertEqual(pos1, key("State", "State Representative Position No. 1", "Legislative District 31"))  # King
        self.assertEqual(pos1, key("State", "Legislative District No.  31", "State Representative Position No. 1"))  # King before #20
        self.assertEqual(pos1, key("State", "State Representative Position 1", "Legislative District 31"))  # primary statewide
        self.assertEqual(("LEGDST", 31, "senator"), key("State", "State Senator", "Legislative District 31"))

    def test_the_district_number_is_never_read_as_a_position(self):
        self.assertEqual(("LEGDST", 11, "representative-position-2"),
                         key("State", "Legislative District No.  11", "State Representative Position No. 2"))
        self.assertEqual(("LEGDST", 1, "representative-position-2"),
                         key("State", "State Representative Pos. 2", "Legislative District 1"))

    def test_named_races_match_across_packages(self):
        king = key("DistrictCourt", "Judge Position No. 5", "King County District Court, Southeast Electoral District")
        pierce = key("Judicial", "Judge Position No. 5", "King County District Court, Southeast Electoral District")
        self.assertEqual(king, pierce)
        self.assertEqual(key("Judicial", "Judge Position 1", "Court of Appeals, Division 2, District 2"),
                         key("Judicial", "Judge Position No. 1", "COURT OF APPEALS, DIVISION 2, DISTRICT 2"))

    def test_bare_offices_and_statewide_contests_are_never_shared(self):
        self.assertIsNone(key("County", "Assessor", ""))
        self.assertIsNone(key("StateSupremeCourt", "Justice Position No. 1", "Supreme Court"))


class ResearchedIndexTest(unittest.TestCase):
    def test_king_research_is_found_by_key(self):
        index = sc.researched_index([GENERAL.state, GENERAL.county("king")])
        cd8 = index[("CONGDST", 8)]
        self.assertEqual("king", cd8["package"])
        self.assertEqual("congressional-district-8-united-states-representative", cd8["contest_slug"])
        self.assertEqual(["kim-schrier", "spencer-meline"], sorted(cd8["candidates"]))
        self.assertEqual("king", index[("LEGDST", 31, "senator")]["package"])
        se5 = sc.contest_key({"category": "Judicial", "office": "Judge Position No. 5",
                              "district": "King County District Court, Southeast Electoral District"})
        self.assertEqual("judge-position-no-5-southeast-electoral-district", index[se5]["contest_slug"])


if __name__ == "__main__":
    unittest.main()
