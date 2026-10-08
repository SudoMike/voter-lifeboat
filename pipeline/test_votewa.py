import hashlib
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


class ExportPinTest(unittest.TestCase):
    """VoteWA flips the case of District Type/District between fetches of the
    same list (Snohomish, 2026-10-08); the pointer's case-normalized sha256
    accepts that and nothing else."""

    HEAD = '\ufeff"District Type","District","Race","Name","Election Status"\r\n'
    UPPER = (HEAD + '"LEGISLATIVE","LEGISLATIVE DISTRICT 10","State Senator","Ann Lee",""\r\n'
             '"Congressional","Congressional District 2","U.S. Representative","Bo Ng",""\r\n').encode()
    FLIPPED = (HEAD + '"Legislative","Legislative District 10","State Senator","Ann Lee",""\r\n'
               '"CONGRESSIONAL","CONGRESSIONAL DISTRICT 2","U.S. Representative","Bo Ng",""\r\n').encode()

    def meta(self, data, normalized=True):
        meta = {"sha256": hashlib.sha256(data).hexdigest()}
        if normalized:
            meta["sha256_case_normalized"] = votewa.case_normalized_sha256(data)
        return meta

    def test_a_case_flip_in_the_district_columns_still_matches(self):
        self.assertNotEqual(hashlib.sha256(self.UPPER).digest(), hashlib.sha256(self.FLIPPED).digest())
        self.assertEqual(votewa.case_normalized_sha256(self.UPPER), votewa.case_normalized_sha256(self.FLIPPED))
        self.assertTrue(votewa.export_matches(self.UPPER, self.meta(self.UPPER)))
        self.assertTrue(votewa.export_matches(self.FLIPPED, self.meta(self.UPPER)))

    def test_any_other_change_does_not(self):
        renamed = self.UPPER.replace(b"Ann Lee", b"ANN LEE")
        dropped = self.UPPER.rsplit(b'"Congressional"', 1)[0]
        reordered = (self.HEAD + '"Congressional","Congressional District 2","U.S. Representative","Bo Ng",""\r\n'
                     '"LEGISLATIVE","LEGISLATIVE DISTRICT 10","State Senator","Ann Lee",""\r\n').encode()
        for changed in (renamed, dropped, reordered):
            self.assertFalse(votewa.export_matches(changed, self.meta(self.UPPER)))

    def test_a_meta_without_the_normalized_digest_needs_the_exact_bytes(self):
        self.assertTrue(votewa.export_matches(self.UPPER, self.meta(self.UPPER, normalized=False)))
        self.assertFalse(votewa.export_matches(self.FLIPPED, self.meta(self.UPPER, normalized=False)))


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
        # A county that curates its measures (Snohomish) also cites its sample
        # ballot and pamphlet pointers, so the VoteWA pointer must be present,
        # not the only source; the "not curated" note belongs only to a
        # package whose app-measures.json is empty.
        for county in ("clark", "kitsap", "pierce", "snohomish", "spokane", "thurston"):
            pointer = (f"data/washington-state/elections/2026-11-03-general/counties/{county}"
                       "/raw/votewa/candidate-list.csv.url")
            measures = json.loads((GENERAL.county(county) / "interim/app-measures.json").read_text())["measures"]
            for name in ("app-contests.json", "app-measures.json"):
                doc = json.loads((GENERAL.county(county) / "interim" / name).read_text())
                self.assertEqual(f"pipeline/build_{county}_lite_data.py", doc["script"])
                self.assertIn(pointer, doc["derived_from"], county)
                if measures:
                    self.assertNotIn(votewa.MEASURES_NOT_CURATED, doc["notes"], county)
                else:
                    self.assertIn(votewa.MEASURES_NOT_CURATED, doc["notes"], county)
            contests = json.loads((GENERAL.county(county) / "interim/app-contests.json").read_text())["contests"]
            self.assertFalse([c for c in contests if "supreme" in c["slug"]], county)
            for c in contests:
                self.assertEqual(county, c["owner"])
                self.assertTrue(c["slug"].startswith(f"{county}-"))

    def test_shipped_general_counties(self):
        self.assertEqual(["king", "snohomish", "spokane", "pierce", "clark", "kitsap", "thurston"],
                         election.APP_PACKAGES[GENERAL.id]["counties"])

    def test_wave2_builders_are_full_county(self):
        # Every Clark, Kitsap and Thurston scope resolves through geo.js
        # COUNTY_LAYERS (#22), so the builders list no unresolvable layer.
        for county in ("clark", "kitsap", "thurston"):
            for name in ("app-contests.json", "app-measures.json"):
                doc = json.loads((GENERAL.county(county) / "interim" / name).read_text())
                self.assertEqual(("full_county", []), (doc["coverage"], doc["notes"]), f"{county} {name}")

if __name__ == "__main__":
    unittest.main()
