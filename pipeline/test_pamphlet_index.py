import json
import unittest

import build_pamphlet_index as bpi
import election

PRIMARY = election.Election("2026-08-04-primary")
GENERAL = election.Election("2026-11-03-general")


class PamphletIndexTest(unittest.TestCase):
    def test_primary_index_is_byte_identical(self):
        committed = (PRIMARY.county("king") / "interim/pamphlet-index.json").read_text()
        self.assertEqual(committed, json.dumps(bpi.build(PRIMARY.id), indent=2))

    def test_split_pages(self):
        text = "--- page 1 ---\nalpha\n\n--- page 2 ---\nbeta gamma\n"
        self.assertEqual({1: "alpha\n\n", 2: "beta gamma\n"}, bpi.split_pages(text))

    def test_general_reads_pamphlets_but_not_the_sample_ballot(self):
        index = bpi.build(GENERAL.id)
        sources = [d for d in index["derived_from"] if "/pdf-text/" in d]
        self.assertEqual(4, len(sources))
        self.assertFalse(any("sample-ballot" in d for d in sources))
        editions = {hit["edition"] for hits in index["candidates"].values() for hit in hits}
        self.assertIn("local-edition", editions)
        self.assertNotIn("sample-ballot", editions)
        # Seattle Prop 1 is in the local pamphlet; legislative candidates are in the SOS editions.
        self.assertIn("local-edition", {h["edition"] for h in index["measures"]["city-of-seattle-proposition-no-1"]})
        self.assertEqual(15, len(index["measures"]))


if __name__ == "__main__":
    unittest.main()
