import json
import shutil
import tempfile
import unittest
from pathlib import Path

import build_research_plan
import election
import normalize_research_inputs


# These assertions pin the Aug 4 primary's counts, so they read that package
# explicitly rather than whichever election is active.
PRIMARY = election.Election("2026-08-04-primary")
GENERAL = election.Election("2026-11-03-general")

# Files normalize() reads or writes, relative to an election package root.
NORMALIZER_FILES = ("contests.json", "measures.json", "app-contests.json", "app-measures.json")


def copy_inputs(e, tmp):
    """Copy an election's normalizer inputs/outputs into a temp repo layout.

    The copy keeps the repo-relative layout (``<tmp>/data/washington-state/
    elections/<id>``) so derived_from paths match the real package, and the
    real package files are never written.
    """
    root = Path(tmp) / e.root.relative_to(election.ROOT)
    for package in e.packages():
        for name in NORMALIZER_FILES:
            source = package / "interim" / name
            if source.exists():
                target = root / source.relative_to(e.root)
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(source, target)
    return root


def read(path):
    return json.loads(path.read_text())


class ResearchInputTest(unittest.TestCase):
    def test_all_counties_have_normalized_king_compatible_shape(self):
        packages = list(PRIMARY.counties.glob("*/interim/contests.json"))
        self.assertEqual(39, len(packages))
        for path in packages:
            for contest in json.loads(path.read_text())["contests"]:
                self.assertTrue({"category", "office", "district", "slug", "candidates"} <= contest.keys())
                for candidate in contest["candidates"]:
                    self.assertTrue({"slug", "name", "party_preference"} <= candidate.keys())

    def test_statewide_is_deduped_district_races(self):
        path = PRIMARY.state / "interim/contests.json"
        contests = json.loads(path.read_text())["contests"]
        self.assertEqual(94, len(contests))
        self.assertEqual(276, sum(len(c["candidates"]) for c in contests))
        self.assertEqual(len(contests), len({normalize_research_inputs._shared_key(c) for c in contests}))
        self.assertTrue(all(c["counties"] == sorted(set(c["counties"])) for c in contests))

    def test_shared_contest_unions_partial_county_rosters(self):
        shared = {}
        key = ("State", 99, "representative-position-1")
        first = {
            "category": "State", "office": "State Representative Pos. 1",
            "district": "Legislative District 99", "slug": "first",
            "candidates": [{"slug": "alpha", "name": "Alpha", "party_preference": None}],
        }
        second = {
            **first, "slug": "second",
            "candidates": [{"slug": "beta", "name": "Beta", "party_preference": None}],
        }
        normalize_research_inputs._merge_shared_contest(shared, key, first, "alpha-county")
        normalize_research_inputs._merge_shared_contest(shared, key, second, "beta-county")
        self.assertEqual(["alpha", "beta"], [c["slug"] for c in shared[key]["candidates"]])
        self.assertEqual(["alpha-county", "beta-county"], shared[key]["counties"])
        self.assertEqual(["alpha"], [c["slug"] for c in first["candidates"]])

    def test_research_plan_omits_uncontested(self):
        build_research_plan.build("statewide", PRIMARY.id)
        plan = json.loads((PRIMARY.state / "interim/research-plan.json").read_text())
        self.assertTrue(all(len(c["candidates"]) >= 2 for c in plan["contests"]))
        self.assertTrue(all(c["depth"] == ("deep" if len(c["candidates"]) >= 3 else "light")
                            for c in plan["contests"]))


class PrimaryOutputFrozenTest(unittest.TestCase):
    def test_primary_regenerates_byte_identical(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = copy_inputs(PRIMARY, tmp)
            normalize_research_inputs.normalize(PRIMARY.id, package_root=root)
            written = sorted(root.glob("statewide/interim/*.json")) + sorted(
                path for name in ("contests.json", "measures.json")
                for path in root.glob(f"counties/*/interim/{name}")
            )
            self.assertEqual(2 + 2 * 39, len(written))
            for path in written:
                committed = PRIMARY.root / path.relative_to(root)
                self.assertEqual(committed.read_text(), path.read_text(), path.relative_to(root))


class HandBuiltStatewidePackageTest(unittest.TestCase):
    """The general's statewide interim files are hand-built (issue #5)."""

    SUPREME_COURT = [f"justice-position-no-{n}-supreme-court" for n in (1, 3, 4, 5, 7)]
    MEASURES = ["initiative-measure-no-ip26-645", "initiative-measure-no-il26-001",
                "initiative-measure-no-il26-638"]

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = copy_inputs(GENERAL, self._tmp.name)
        self.contests = self.root / "statewide/interim/contests.json"
        self.measures = self.root / "statewide/interim/measures.json"

    def tearDown(self):
        self._tmp.cleanup()

    def add_county(self, name, source_county="adams"):
        """Give the temp general a county with VoteWA-lite app contests."""
        source = PRIMARY.county(source_county) / "interim/app-contests.json"
        target = self.root / "counties" / name / "interim/app-contests.json"
        target.parent.mkdir(parents=True)
        shutil.copyfile(source, target)

    def test_general_package_is_left_in_place(self):
        normalize_research_inputs.normalize(GENERAL.id, package_root=self.root)
        real = GENERAL.state / "interim"
        self.assertEqual((real / "contests.json").read_text(), self.contests.read_text())
        self.assertEqual((real / "measures.json").read_text(), self.measures.read_text())
        self.assertEqual(self.SUPREME_COURT, [c["slug"] for c in read(self.contests)["contests"]])
        self.assertEqual(self.MEASURES, [m["slug"] for m in read(self.measures)["measures"]])

    def test_district_contests_merge_after_hand_built_ones(self):
        original = read(self.contests)
        self.add_county("adams")
        normalize_research_inputs.normalize(GENERAL.id, package_root=self.root)
        merged = read(self.contests)
        self.assertEqual(original["contests"], merged["contests"][:5])
        added = merged["contests"][5:]
        self.assertTrue(added)
        self.assertTrue(all(c["category"] in {"Federal", "State"} for c in added))
        self.assertTrue(all(c["counties"] == ["adams"] for c in added))
        self.assertEqual(original["method"], merged["method"])
        self.assertIsNone(merged["script"])
        source = "data/washington-state/elections/2026-11-03-general/counties/adams/interim/app-contests.json"
        self.assertEqual(original["derived_from"] + [source], merged["derived_from"])
        self.assertEqual({
            "script": "pipeline/normalize_research_inputs.py",
            "derived_from": [source],
            "contests": [c["slug"] for c in added],
        }, merged["normalized"])
        self.assertEqual((GENERAL.state / "interim/measures.json").read_text(), self.measures.read_text())

    def test_merge_is_idempotent_and_drops_stale_district_contests(self):
        original = self.contests.read_text()
        self.add_county("adams")
        normalize_research_inputs.normalize(GENERAL.id, package_root=self.root)
        once = self.contests.read_text()
        normalize_research_inputs.normalize(GENERAL.id, package_root=self.root)
        self.assertEqual(once, self.contests.read_text())
        shutil.rmtree(self.root / "counties/adams")
        normalize_research_inputs.normalize(GENERAL.id, package_root=self.root)
        self.assertEqual(json.loads(original), read(self.contests))

    def test_hand_built_contest_wins_slug_collision(self):
        self.add_county("adams")
        normalize_research_inputs.normalize(GENERAL.id, package_root=self.root)
        slug = read(self.contests)["normalized"]["contests"][0]
        self._tmp.cleanup()
        self.setUp()
        hand = read(self.contests)
        hand["contests"].append({"category": "Federal", "office": "Hand", "district": "Hand",
                                 "slug": slug, "candidates": []})
        self.contests.write_text(json.dumps(hand, indent=2, ensure_ascii=False) + "\n")
        self.add_county("adams")
        normalize_research_inputs.normalize(GENERAL.id, package_root=self.root)
        merged = read(self.contests)
        winners = [c for c in merged["contests"] if c["slug"] == slug]
        self.assertEqual([hand["contests"][-1]], winners)
        self.assertNotIn(slug, merged["normalized"]["contests"])

    def test_refuses_to_overwrite_a_county_file_it_did_not_write(self):
        self.add_county("adams")
        foreign = self.root / "counties/adams/interim/contests.json"
        foreign.write_text(json.dumps({"script": "pipeline/parse_candidates.py", "contests": []}))
        before = foreign.read_text()
        with self.assertRaises(SystemExit):
            normalize_research_inputs.normalize(GENERAL.id, package_root=self.root)
        self.assertEqual(before, foreign.read_text())


if __name__ == "__main__":
    unittest.main()
