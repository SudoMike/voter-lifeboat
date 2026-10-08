"""HTML extraction and ranking of propose_candidate_photos.py, on inline
fixtures; no network. The review-copy resize runs only when Pillow is
installed (pipeline/requirements.txt)."""

import importlib.util
import io
import tempfile
import unittest
from pathlib import Path

import propose_candidate_photos as photos

PAGE = "https://www.example-campaign.org/about"

CAMPAIGN_HTML = """<!doctype html><html><head>
<meta property="og:image" content="http://cdn.example-campaign.org/share/headshot.jpg">
<meta name="twitter:image" content="/img/tw-card.png">
</head><body>
<img src="/img/logo.png" width="1500" height="256">
<img src="//cdn.example-campaign.org/img/jane-800.jpg" width="800" height="1000" alt="Jane">
<img src="/img/jane-400.jpg" width="400" height="400">
<img src="/img/tiny.jpg" width="120" height="150">
<img src="/img/wide-banner.jpg" width="2160" height="400">
<img src="data:image/gif;base64,R0lGOD" data-src="/img/lazy-600.jpg" width="600" height="700">
<img src="/img/unsized.jpg">
</body></html>"""


class ImageCandidatesTest(unittest.TestCase):
    def test_meta_images_first_then_largest_portrait_imgs(self):
        found = photos.image_candidates(CAMPAIGN_HTML, PAGE, limit=10)
        self.assertEqual(
            [
                ("https://cdn.example-campaign.org/share/headshot.jpg", "og:image"),
                ("https://www.example-campaign.org/img/tw-card.png", "twitter:image"),
                ("https://cdn.example-campaign.org/img/jane-800.jpg", "img 800x1000"),
                ("https://www.example-campaign.org/img/lazy-600.jpg", "img 600x700"),
                ("https://www.example-campaign.org/img/jane-400.jpg", "img 400x400"),
            ],
            [(c["url"], c["why"]) for c in found],
        )
        for entry in found:
            self.assertEqual(PAGE, entry["page"])
            self.assertEqual("campaign-website", entry["kind"])
        self.assertEqual((800, 1000), (found[2]["width"], found[2]["height"]))

    def test_at_most_three_candidates_by_default(self):
        found = photos.image_candidates(CAMPAIGN_HTML, PAGE)
        self.assertEqual(3, len(found))
        self.assertEqual("img 800x1000", found[2]["why"])

    def test_logos_banners_small_and_unsized_images_are_excluded(self):
        urls = [c["url"] for c in photos.image_candidates(CAMPAIGN_HTML, PAGE, limit=10)]
        for excluded in ("logo.png", "tiny.jpg", "wide-banner.jpg", "unsized.jpg"):
            self.assertFalse(any(excluded in u for u in urls), excluded)

    def test_og_image_with_declared_banner_shape_is_skipped(self):
        html = """<meta property="og:image" content="/logo-wide.png">
        <meta property="og:image:width" content="1500"><meta property="og:image:height" content="256">
        <img src="/me.jpg" width="500" height="600">"""
        found = photos.image_candidates(html, PAGE)
        self.assertEqual(["https://www.example-campaign.org/me.jpg"], [c["url"] for c in found])

    def test_og_image_with_declared_portrait_shape_keeps_its_dimensions(self):
        html = """<meta property="og:image" content="/me.jpg">
        <meta property="og:image:width" content="600"><meta property="og:image:height" content="800">"""
        [found] = photos.image_candidates(html, PAGE)
        self.assertEqual((600, 800, "og:image"), (found["width"], found["height"], found["why"]))

    def test_squarespace_dimensions_and_data_image(self):
        html = """<img data-src="https://images.example-cdn.com/a.png" data-image="https://images.example-cdn.com/a.png"
        data-image-dimensions="900x1080" src="https://images.example-cdn.com/a.png?format=100w">"""
        [found] = photos.image_candidates(html, PAGE)
        self.assertEqual(("https://images.example-cdn.com/a.png", "img 900x1080"), (found["url"], found["why"]))

    def test_duplicate_urls_and_non_web_urls_are_dropped(self):
        html = """<meta property="og:image" content="https://www.example-campaign.org/me.jpg">
        <img src="/me.jpg" width="500" height="500"><img src="javascript:void(0)" width="500" height="500">"""
        found = photos.image_candidates(html, PAGE)
        self.assertEqual(["https://www.example-campaign.org/me.jpg"], [c["url"] for c in found])

    def test_empty_or_broken_html(self):
        self.assertEqual([], photos.image_candidates("", PAGE))
        self.assertEqual([], photos.image_candidates("<html><body><p>no images</p></body>", PAGE))


class NormalizeUrlTest(unittest.TestCase):
    def test_relative_protocol_relative_and_http_become_absolute_https(self):
        self.assertEqual("https://www.example-campaign.org/img/a.jpg", photos.normalize_url("/img/a.jpg", PAGE))
        self.assertEqual("https://www.example-campaign.org/img/a.jpg", photos.normalize_url("img/a.jpg", PAGE))
        self.assertEqual("https://cdn.x.org/a.jpg", photos.normalize_url("//cdn.x.org/a.jpg", PAGE))
        self.assertEqual("https://cdn.x.org/a.jpg?w=1", photos.normalize_url("http://cdn.x.org/a.jpg?w=1#top", PAGE))

    def test_non_web_references_are_none(self):
        for bad in ("", "   ", "data:image/png;base64,AAAA", "javascript:x", "mailto:a@b.c"):
            self.assertIsNone(photos.normalize_url(bad, PAGE), bad)


class WebsiteForTest(unittest.TestCase):
    FM = """name: Jane Example
slug: jane-example
sources:
  - id: S1
    tier: 1
    type: pamphlet
    ref: edition-1 page 30
  - id: S2
    tier: 2
    type: news
    url: https://news.example.org/story
  - id: S3
    tier: 1
    type: campaign-website
    url: https://www.janeexample.org/
    accessed: 2026-10-08
"""

    def test_plan_website_wins(self):
        self.assertEqual(
            ("https://jane.example/", "contests"),
            photos.website_for({"campaign_website": "https://jane.example/"}, self.FM),
        )

    def test_dossier_campaign_website_source_is_the_fallback(self):
        self.assertEqual(
            ("https://www.janeexample.org/", "dossier"),
            photos.website_for({"campaign_website": None}, self.FM),
        )

    def test_no_website_anywhere(self):
        fm = "name: X\nsources:\n  - id: S1\n    tier: 2\n    type: news\n    url: https://news.example.org/\n"
        self.assertEqual((None, None), photos.website_for({}, fm))


@unittest.skipUnless(importlib.util.find_spec("PIL"), "Pillow not installed")
class ReviewCopyTest(unittest.TestCase):
    def test_large_image_is_resized_to_500_on_the_longer_edge(self):
        from PIL import Image

        buffer = io.BytesIO()
        Image.new("RGBA", (1200, 1600), (200, 30, 30, 255)).save(buffer, "PNG")
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "a" / "b-1.jpg"
            self.assertEqual((1200, 1600), photos.review_copy(buffer.getvalue(), path))
            copy = Image.open(path)
            self.assertEqual(("JPEG", "RGB", (375, 500)), (copy.format, copy.mode, copy.size))

    def test_small_image_is_not_upscaled(self):
        from PIL import Image

        buffer = io.BytesIO()
        Image.new("RGB", (140, 197)).save(buffer, "PNG")
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "c-1.jpg"
            self.assertEqual((140, 197), photos.review_copy(buffer.getvalue(), path))
            self.assertEqual((140, 197), Image.open(path).size)

    def test_undecodable_bytes(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertIsNone(photos.review_copy(b"<html>not an image</html>", Path(tmp) / "x.jpg"))


if __name__ == "__main__":
    unittest.main()
