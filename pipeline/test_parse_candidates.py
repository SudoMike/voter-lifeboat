import json
import unittest
from collections import Counter

import election
import parse_candidates as pc

PRIMARY = election.Election("2026-08-04-primary")
GENERAL = election.Election("2026-11-03-general")


def committed(e, name):
    return (e.county("king") / "interim" / name).read_text()


class PrimaryFrozenTest(unittest.TestCase):
    def test_primary_outputs_are_byte_identical(self):
        contests, measures, _ = pc.build(PRIMARY.id)
        self.assertEqual(committed(PRIMARY, "contests.json"), json.dumps(contests, indent=2))
        self.assertEqual(committed(PRIMARY, "measures.json"), json.dumps(measures, indent=2))


class ContestListTest(unittest.TestCase):
    HTML = (
        '<div class="list-group pull-left candidate-list-group" id="CourtofAppeals,Division1,District1">'
        '<div class="list-group-item candidatelist-div"><h5><span class="sp-bt-title-1">Judge Position No. 5</span>'
        '</h5><ul class="ul-candidatelist"><li><a href="candidates.aspx?cid=7&amp;candidateid=9&amp;lang=en-US">'
        '<span class="ballotname">David S. Mann</span></a></li></ul></div>'
    )

    def test_court_of_appeals_gets_a_district_and_a_judge_slug(self):
        [con] = pc.parse_contest_list(self.HTML)
        self.assertEqual("CourtOfAppeals", con["category"])
        self.assertEqual("Court of Appeals, Division 1, District 1", con["district"])
        self.assertEqual("court-of-appeals-division-1-district-1-judge-position-no-5", con["slug"])
        self.assertEqual({"kind": "COUNTY", "county": "king"}, pc.contest_scope(con))


class ScopeTest(unittest.TestCase):
    def scope(self, category, office, district):
        return pc.contest_scope({"category": category, "office": office, "district": district, "slug": "x"})

    def test_contest_scopes(self):
        d = pc.district_scope
        self.assertEqual({"kind": "STATEWIDE"}, self.scope("StateSupremeCourt", "Supreme Court", "Justice Position No. 1"))
        self.assertEqual(d("CONGDST", 9), self.scope("Federal", "United States Representative", "Congressional District 9"))
        self.assertEqual(d("LEGDST", 11), self.scope("State", "Legislative District No.  11", "State Senator"))
        self.assertEqual(d("KCCDST", 4), self.scope("County", "Metropolitan King County", "Council District No. 4"))
        self.assertEqual({"kind": "COUNTY", "county": "king"}, self.scope("County", "Assessor", ""))
        self.assertEqual(d("JUDDST", "SH"), self.scope("DistrictCourt", "Shoreline Electoral District", "Judge Position No. 1"))
        self.assertEqual(d("JUDDST", "W"), self.scope("DistrictCourt", "West Electoral District", "Judge Position No. 1"))
        self.assertEqual(d("SCCDST", "SCC5"), self.scope("City", "City of Seattle", "Council District No. 5"))
        self.assertEqual(d("CITY", "Seattle"), self.scope("City", "City of Seattle", "Municipal Court Judge Position No. 1"))

    def test_measure_scopes(self):
        d = pc.district_scope
        self.assertEqual(d("CITY", "Lake Forest Park"), pc.measure_scope("City of Lake Forest Park"))
        self.assertEqual(d("SCHDST", "401"), pc.measure_scope("Highline School District No. 401"))
        self.assertEqual(d("FIRDST", "20"), pc.measure_scope("King County Fire Protection District No. 20"))
        self.assertEqual(d("CEMDST", "1"), pc.measure_scope("King County Cemetery District No. 1"))
        with self.assertRaises(ValueError):
            pc.measure_scope("Port of Seattle")


class StatementTest(unittest.TestCase):
    def test_submitted_by_is_split_off(self):
        s = pc.statement("Vote yes.\n\nIt helps.\n\n​Statment submitted by: A, B, www.x.org")
        self.assertEqual({"submitted": True, "text": "Vote yes.\n\nIt helps.", "submitted_by": "A, B, www.x.org"}, s)

    def test_missing_statement_is_flagged_and_kept_verbatim(self):
        text = "There is no statement against this measure. No one in the jurisdiction volunteered."
        self.assertEqual({"submitted": False, "text": text}, pc.statement(text))
        self.assertFalse(pc.statement("No statement submitted.")["submitted"])
        self.assertIsNone(pc.statement(None))


class GeneralBuildTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contests, cls.measures, _ = pc.build(GENERAL.id)

    def test_contest_counts_by_category(self):
        cs = self.contests["contests"]
        self.assertEqual(55, self.contests["election"]["kce_eid"])
        self.assertEqual(
            {"Federal": 4, "State": 46, "County": 7, "StateSupremeCourt": 5, "CourtOfAppeals": 2,
             "DistrictCourt": 25, "City": 8},
            dict(Counter(c["category"] for c in cs)),
        )
        self.assertEqual(len(cs), len({c["slug"] for c in cs}))
        self.assertTrue(all(c["uncontested"] == (len(c["candidates"]) == 1) for c in cs))

    def test_office_is_the_seat_and_district_the_jurisdiction(self):
        # KCE prints the jurisdiction first for most groups ("Legislative
        # District No.  46" / "State Senator"); schema 2 stores office = seat,
        # district = jurisdiction, whitespace collapsed (#20, from #25).
        # Slugs keep KCE's order so scoring files and dossiers still match.
        by_slug = {c["slug"]: c for c in self.contests["contests"]}

        def heading(slug):
            return by_slug[slug]["office"], by_slug[slug]["district"]

        self.assertEqual(("State Representative Position No. 1", "Legislative District 1"),
                         heading("state-representative-position-no-1-legislative-district-no-1"))
        self.assertEqual(("State Senator", "Legislative District 46"),
                         heading("state-senator-legislative-district-no-46"))
        self.assertEqual(("Council District No. 2", "Metropolitan King County"),
                         heading("council-district-no-2-metropolitan-king-county"))
        self.assertEqual(("Judge Position No. 1", "King County District Court, Southeast Electoral District"),
                         heading("judge-position-no-1-southeast-electoral-district"))
        self.assertEqual(("Council District No. 5", "City of Seattle"),
                         heading("council-district-no-5-city-of-seattle"))
        self.assertEqual(("Justice Position No. 1", "Supreme Court"),
                         heading("justice-position-no-1-supreme-court"))
        # Already seat-first: unchanged.
        self.assertEqual(("United States Representative", "Congressional District 9"),
                         heading("congressional-district-9-united-states-representative"))
        self.assertEqual(("Judge Position No. 5", "Court of Appeals, Division 1, District 1"),
                         heading("court-of-appeals-division-1-district-1-judge-position-no-5"))
        self.assertEqual(("Assessor", ""), heading("assessor"))
        for con in self.contests["contests"]:
            self.assertNotIn("  ", con["office"] + con["district"], con["slug"])

    def test_scopes_survive_the_heading_fix(self):
        by_slug = {c["slug"]: c for c in self.contests["contests"]}
        d = pc.district_scope
        self.assertEqual(d("LEGDST", 46), by_slug["state-senator-legislative-district-no-46"]["scope"])
        self.assertEqual(d("KCCDST", 2), by_slug["council-district-no-2-metropolitan-king-county"]["scope"])
        self.assertEqual(d("JUDDST", "SE"), by_slug["judge-position-no-1-southeast-electoral-district"]["scope"])
        self.assertEqual(d("SCCDST", "SCC5"), by_slug["council-district-no-5-city-of-seattle"]["scope"])

    def test_supreme_court_is_statewide_owned_with_statewide_slugs(self):
        owned = [c for c in self.contests["contests"] if c["owner"] == "statewide"]
        self.assertEqual(
            [f"justice-position-no-{n}-supreme-court" for n in (1, 3, 4, 5, 7)],
            [c["slug"] for c in owned],
        )
        self.assertTrue(all(c["scope"] == {"kind": "STATEWIDE"} for c in owned))

    def test_ballot_order_follows_the_eid_list(self):
        for con in self.contests["contests"]:
            self.assertEqual(list(range(1, len(con["candidates"]) + 1)),
                             [c["ballot_order"] for c in con["candidates"]])

    def test_fifteen_local_measures_with_statements_and_scopes(self):
        ms = self.measures["measures"]
        self.assertEqual(15, len(ms))
        self.assertEqual(3, len(self.measures["statewide_owned_measures"]))
        layers = Counter(m["scope"]["layer"] for m in ms)
        self.assertEqual({"CITY": 9, "SCHDST": 4, "FIRDST": 1, "CEMDST": 1}, dict(layers))
        for m in ms:
            self.assertTrue(m["ballot_title"] and m["explanatory_statement"], m["slug"])
            self.assertIsNotNone(m["statements"]["for"], m["slug"])
            self.assertIsNotNone(m["statements"]["against"], m["slug"])
            self.assertTrue(m["derived_from"], m["slug"])
        unresolved = [m["slug"] for m in ms if "scope_unresolved" in m]
        self.assertEqual(["king-county-cemetery-district-no-1-proposition-no-1"], unresolved)

    def test_seattle_transit_measure_text(self):
        [m] = [m for m in self.measures["measures"] if m["jurisdiction"] == "City of Seattle"]
        self.assertEqual("Seattle Transit Measure", m["title"])
        self.assertTrue(m["ballot_title"].endswith("Should this Proposition be approved?"))
        self.assertEqual("Ari Hoffman", m["statements"]["against"]["submitted_by"])
        self.assertTrue(m["statements"]["rebuttal_of_against"]["text"].startswith("This measure funds bus service"))

    def test_milton_comes_from_votewa(self):
        [m] = [m for m in self.measures["measures"] if m["jurisdiction"] == "City of Milton"]
        self.assertEqual("7310", m["votewa_measure_id"])
        self.assertTrue(m["statements"]["for"]["submitted"])
        self.assertFalse(m["statements"]["against"]["submitted"])


if __name__ == "__main__":
    unittest.main()
