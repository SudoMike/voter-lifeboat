import json
import unittest

import build_votewa_lite_data as bv
import election
import votewa

PRIMARY = election.Election("2026-08-04-primary")
GENERAL = election.Election("2026-11-03-general")
HEADER = ["District Type", "District", "Race", "Name", "Party Preference", "Status", "Election Status"]


def row(dtype, district, race, name, status=""):
    return dict(zip(HEADER, [dtype, district, race, name, "DEMOCRATIC", "Active", status]))


class SourcesTest(unittest.TestCase):
    def test_county_codes_follow_the_dropdown_not_the_alphabet(self):
        codes = election.VOTEWA_COUNTY_CODES
        self.assertEqual(39, len(codes))
        self.assertEqual(39, len(set(codes.values())))
        self.assertEqual(("31", "34"), (codes["thurston"], codes["snohomish"]))
        self.assertEqual("Grays Harbor", election.votewa_county_label("grays-harbor"))

    def test_ballot_status_per_election(self):
        self.assertEqual(("In Primary",), election.VOTEWA_SOURCES[PRIMARY.id]["ballot_status"])
        self.assertEqual(("",), election.VOTEWA_SOURCES[GENERAL.id]["ballot_status"])
        self.assertEqual(898, election.VOTEWA_SOURCES[PRIMARY.id]["e"])
        self.assertEqual(899, election.VOTEWA_SOURCES[GENERAL.id]["e"])

    def test_general_pointers_pin_their_export(self):
        for county in ("clark", "kitsap", "pierce", "snohomish", "spokane", "thurston"):
            raw = GENERAL.county(county) / "raw/votewa"
            meta = json.loads((raw / "candidate-list.csv.meta.json").read_text())
            url = (raw / "candidate-list.csv.url").read_text().strip()
            code = election.VOTEWA_COUNTY_CODES[county]
            self.assertEqual(f"https://voter.votewa.gov/candidatelist.aspx?c={code}&e=899", url)
            self.assertEqual(url, meta["url"])
            self.assertEqual(election.votewa_county_label(county), meta["county_dropdown"]["label"])
            self.assertEqual(64, len(meta["sha256"]))
            self.assertEqual(f"data/.cache/votewa/candidatelist-c{code}-e899.csv", meta["cache_file"])
            self.assertEqual({"": meta["csv_rows"]}, meta["election_status_counts"])


class PrimaryFrozenTest(unittest.TestCase):
    def test_every_primary_package_is_byte_identical(self):
        for county in sorted(bv.COUNTY_CONFIG):
            cfg, curated = bv.config_for(county, PRIMARY.id)
            self.assertTrue(curated)
            contests, measures, _ = bv.county_docs(county, cfg, PRIMARY.id, curated)
            interim = PRIMARY.county(county) / "interim"
            self.assertEqual((interim / "app-contests.json").read_text(), json.dumps(contests, indent=2), county)
            self.assertEqual((interim / "app-measures.json").read_text(), json.dumps(measures, indent=2), county)


class ParseTest(unittest.TestCase):
    CFG = {"name": "Thurston County", "commissioner": "{n}"}

    def test_supreme_court_and_pco_rows_are_dropped(self):
        rows = [row("Judicial", "Supreme Court", "Justice Position #01", "A"),
                row("Precinct", "PCO 101", "Precinct Committee Officer", "B"),
                row("Legislative", "Legislative District 22", "State Senator", "C")]
        contests = votewa.parse_contests(rows, "thurston", self.CFG, set())
        self.assertEqual([("State", "Legislative District 22", "State Senator", ("LEGDST", "22"))],
                         [(c["category"], c["district"], c["office"], c["scope"]) for c in contests])

    def test_all_county_commissioners_are_countywide_in_the_general(self):
        unresolvable = set()
        rows = [row("COMMISSIONER", "COMMISSIONER DISTRICT ALL COUNTY", "Commissioner, District No. 3", "A"),
                row("COMMISSIONER", "COMMISSIONER DISTRICT 2", "Commissioner District 2", "B")]
        contests = votewa.parse_contests(rows, "thurston", {"name": "Thurston County", "commissioner": None},
                                         unresolvable)
        self.assertEqual(("COUNTY", None), contests[0]["scope"])
        self.assertEqual(("COUNTY_COUNCIL", "2"), contests[1]["scope"])
        self.assertEqual({"COUNTY_COUNCIL"}, unresolvable)

    def test_override_wins_and_unmapped_types_stop_the_build(self):
        rows = [row("District Court", "SOUTHEAST ELECTORAL DISTRICT", "Judge Position No. 1", "A")]
        with self.assertRaises(ValueError):
            votewa.parse_contests(rows, "pierce", {"name": "Pierce County"}, set())
        contests = votewa.parse_contests(
            rows, "pierce", {"name": "Pierce County"}, set(),
            override=lambda r, u: ("Judicial", "X", "Judge Position No. 1", ("KCDISTCRT", "YES")))
        self.assertEqual(("KCDISTCRT", "YES"), contests[0]["scope"])

    def test_general_without_curated_measures_says_so(self):
        cfg, curated = bv.config_for("adams", GENERAL.id)
        self.assertFalse(curated)
        self.assertEqual([], cfg["measures"])
        self.assertIn("not curated", votewa.MEASURES_NOT_CURATED)


class GeneralPackagesTest(unittest.TestCase):
    def test_six_builders_emit_votewa_packages_with_pointer_provenance(self):
        for county in ("clark", "kitsap", "pierce", "snohomish", "spokane", "thurston"):
            for name in ("app-contests.json", "app-measures.json"):
                doc = json.loads((GENERAL.county(county) / "interim" / name).read_text())
                self.assertEqual(f"pipeline/build_{county}_lite_data.py", doc["script"])
                self.assertEqual([f"data/washington-state/elections/2026-11-03-general/counties/{county}"
                                  "/raw/votewa/candidate-list.csv.url"], doc["derived_from"])
                self.assertIn(votewa.MEASURES_NOT_CURATED, doc["notes"])
            contests = json.loads((GENERAL.county(county) / "interim/app-contests.json").read_text())["contests"]
            self.assertFalse([c for c in contests if "supreme" in c["slug"]], county)
            for c in contests:
                self.assertEqual(county, c["owner"])
                self.assertTrue(c["slug"].startswith(f"{county}-"))

    def test_no_general_county_ships(self):
        self.assertEqual(["king"], election.APP_PACKAGES[GENERAL.id]["counties"])


if __name__ == "__main__":
    unittest.main()
