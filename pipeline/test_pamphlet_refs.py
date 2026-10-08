"""Dossier pamphlet refs -> app pamphlet_pages (pamphlet_refs.py)."""

import unittest

from pamphlet_refs import edition_id, ref_pages, sources_pages

EDITIONS = [
    "local-edition",
    "voters-pamphlet-edition-04-king-seattle",
    "voters-pamphlet-edition-05-king-north-eastside",
    "voters-pamphlet-edition-06-king-south-southeast",
]
ED04, ED05, ED06 = EDITIONS[1:]


def pages(ref):
    return [(p["edition"], p["page"]) for p in ref_pages(ref, EDITIONS)]


class PamphletRefsTest(unittest.TestCase):
    def test_short_edition_names_resolve_to_the_pointer_names(self):
        self.assertEqual(ED04, edition_id("edition-04", EDITIONS))
        self.assertEqual(ED06, edition_id("edition-6", EDITIONS))
        self.assertEqual("local-edition", edition_id("local-edition", EDITIONS))
        self.assertIsNone(edition_id("edition-1", EDITIONS))

    def test_statement_page_with_a_same_statement_note(self):
        self.assertEqual([(ED04, 24), (ED06, 24)],
                         pages("edition-04 page 24 (identical statement at edition-06 page 24)"))
        self.assertEqual([(ED05, 34), (ED06, 32)], pages(
            "voters-pamphlet-edition-05-king-north-eastside page 34 "
            "(same statement in voters-pamphlet-edition-06-king-south-southeast page 32)"))
        self.assertEqual([(ED04, 61), (ED05, 52), (ED06, 59)],
                         pages("edition-04 page 61; edition-05 page 52; edition-06 page 59"))

    def test_the_duties_page_is_skipped_and_a_bare_page_takes_the_last_edition(self):
        self.assertEqual([("local-edition", 21)],
                         pages("local-edition page 14 (duties of offices) and page 21 (candidate statement)"))
        self.assertEqual([("local-edition", 44)],
                         pages("local-edition page 44 (candidate statements); page 14 (duties of offices)"))
        # A note that mentions the duties page elsewhere does not drop the statement.
        self.assertEqual([("local-edition", 30)],
                         pages("local-edition page 30 (District Court duties and salary on page 14)"))

    def test_page_ranges_expand(self):
        self.assertEqual([("local-edition", n) for n in range(76, 81)],
                         pages("local-edition pages 76-80 (full text of Ordinance No. 127474)"))

    def test_other_elections_and_unknown_editions_give_nothing(self):
        self.assertEqual([], pages(
            "2026 primary local pamphlet, edition-2 page 80 (data/washington-state/elections/"
            "2026-08-04-primary/counties/king/interim/pamphlet-text/edition-2/page-080.txt)"))
        self.assertEqual([], pages("edition-1 page 30"))

    def test_a_county_local_voters_pamphlet_resolves(self):
        # Snohomish's (and the other county builders') pamphlet pointer is
        # raw/<county>/local-voters-pamphlet.pdf.url; a ref naming it must not
        # fall through to "no edition".
        editions = ["local-voters-pamphlet", "sample-ballot"]
        self.assertEqual([{"edition": "local-voters-pamphlet", "page": 33}], ref_pages(
            "local-voters-pamphlet page 33 (2026 General Election Voters' Pamphlet, Snohomish County edition, "
            "state candidate statement)", editions))
        self.assertEqual([{"edition": "local-voters-pamphlet", "page": 26}],
                         ref_pages("local-voters-pamphlet page 26", editions))
        # King's editions do not include it, so it gives nothing there.
        self.assertEqual([], pages("local-voters-pamphlet page 26"))

    def test_sources_pages_reads_only_pamphlet_sources_and_dedupes(self):
        sources = [
            {"id": "S1", "type": "pamphlet", "ref": "local-edition page 41"},
            {"id": "S2", "type": "campaign-website", "url": "https://example.test", "ref": "page 9"},
            {"id": "S3", "type": "pamphlet", "ref": "local-edition page 41 (statements)"},
            {"id": "S4", "type": "pamphlet"},
        ]
        self.assertEqual([{"edition": "local-edition", "page": 41}], sources_pages(sources, EDITIONS))


if __name__ == "__main__":
    unittest.main()
