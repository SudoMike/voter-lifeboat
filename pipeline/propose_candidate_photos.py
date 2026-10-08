"""Stage: dossiers -> interim. Propose a Candidate Photo for every candidate
dossier in a package that has none (issue #33).

Usage: python3 pipeline/propose_candidate_photos.py [<package> | --all] [--election <id>]
           [--workers N] [--limit N] [--timeout S]

For each planned candidate whose dossier has no ``photo`` block, take the
candidate's campaign website: ``campaign_website`` in the research plan
(from interim/contests.json; only King's KCE export and the statewide
package carry one, the VoteWA export has no website column), else the first
``type: campaign-website`` source url in the dossier itself. Candidates with
neither are skipped with status ``no-website``.

The site is fetched (https upgrade, one retry, a plain descriptive
User-Agent) and up to three image candidates are listed, best first:
og:image, twitter:image, then the largest <img> by declared size that is
roughly portrait or square (aspect 0.6-1.4) and at least 200 px on the
short side. Each must answer HEAD (fallback GET) with 200 and an image/*
content type. A review copy (longer edge at most 500 px, never upscaled,
JPEG) is written under data/.cache/photos/ (gitignored) so a reviewer looks
at small local files instead of fetching the originals; its path is the
entry's ``review_copy`` and the original ``width``/``height`` are recorded.

Output: E/<package>/interim/photo-proposals.json, ``proposals`` entries of
{contest_slug, candidate_slug, name, website, website_from, status, candidates}
with status proposed | no-website | fetch-failed | no-image-found, plus a
``summary`` of counts per status. The script writes proposals and review
copies only; it never edits a dossier. Rerunning overwrites both.

Dependencies: stdlib plus Pillow for the review copies
(pipeline/requirements.txt). Pillow is imported lazily so the extraction
tests run without it.
"""

import argparse
import io
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from html.parser import HTMLParser
from pathlib import Path

import dossier_photo
import election
from election import ROOT, rel

USER_AGENT = "VoterLifeboat/1.0 (candidate photo proposer; pipeline/propose_candidate_photos.py)"
MIN_SHORT_SIDE = 200
ASPECT_RANGE = (0.6, 1.4)
MAX_CANDIDATES = 3
REVIEW_EDGE = 500
REVIEW_QUALITY = 85
CACHE = ROOT / "data/.cache/photos"
STATUSES = ("proposed", "no-website", "fetch-failed", "no-image-found")

META_IMAGE_KEYS = {
    "og:image": "og:image",
    "og:image:url": "og:image",
    "og:image:secure_url": "og:image",
    "twitter:image": "twitter:image",
    "twitter:image:src": "twitter:image",
}


# --- HTML extraction (pure; unit-tested) --------------------------------------

class ImageCollector(HTMLParser):
    """og/twitter image metas and <img> tags of a page, in document order."""

    def __init__(self):
        super().__init__()
        self.metas = []
        self.imgs = []

    def handle_starttag(self, tag, attrs):
        a = {k.lower(): (v or "") for k, v in attrs}
        if tag == "meta":
            key = (a.get("property") or a.get("name") or "").strip().lower()
            if key in META_IMAGE_KEYS or key in ("og:image:width", "og:image:height"):
                self.metas.append((key, a.get("content", "").strip()))
        elif tag == "img":
            self.imgs.append(a)


def normalize_url(url: str, page_url: str):
    """Absolute https URL for an image reference, or None when it is not a
    web URL (data: URIs, empty, javascript:)."""
    url = (url or "").strip()
    if not url or url.startswith(("data:", "javascript:", "blob:")):
        return None
    if url.startswith("//"):
        url = "https:" + url
    url = urllib.parse.urljoin(page_url, url)
    parts = urllib.parse.urlsplit(url)
    if parts.scheme not in ("http", "https") or not parts.netloc:
        return None
    return urllib.parse.urlunsplit(("https", parts.netloc, parts.path, parts.query, ""))


def _int(value):
    match = re.match(r"\s*(\d+)", value or "")
    return int(match.group(1)) if match else None


def img_dimensions(attrs):
    """Declared (width, height) of an <img>: data-image-dimensions="WxH"
    (Squarespace) or width/height attributes; (None, None) when undeclared."""
    dims = re.match(r"\s*(\d+)\s*x\s*(\d+)", attrs.get("data-image-dimensions", ""))
    if dims:
        return int(dims.group(1)), int(dims.group(2))
    return _int(attrs.get("width")), _int(attrs.get("height"))


def img_source(attrs):
    """The image reference of an <img>, preferring the lazy-load attributes
    that hold the real file over a placeholder src."""
    for key in ("data-image", "data-src", "data-lazy-src", "src"):
        value = (attrs.get(key) or "").strip()
        if value and not value.startswith("data:"):
            return value
    return None


def portrait_like(width, height):
    """Roughly portrait or square and large enough for a headshot."""
    if not width or not height:
        return False
    aspect = width / height
    return ASPECT_RANGE[0] <= aspect <= ASPECT_RANGE[1] and min(width, height) >= MIN_SHORT_SIDE


def image_candidates(html: str, page_url: str, limit: int = MAX_CANDIDATES):
    """Up to ``limit`` image candidates of a page, best first, each
    {url, page, kind, why[, width, height]}."""
    collector = ImageCollector()
    try:
        collector.feed(html)
    except Exception:  # noqa: BLE001 - a broken page yields what was parsed
        pass
    out, seen = [], set()

    def add(url, why, width=None, height=None):
        url = normalize_url(url, page_url)
        if not url or url in seen or len(out) >= limit:
            return
        seen.add(url)
        entry = {"url": url, "page": page_url, "kind": "campaign-website", "why": why}
        if width and height:
            entry["width"], entry["height"] = width, height
        out.append(entry)

    og_width = og_height = None
    for key, value in collector.metas:
        if key == "og:image:width":
            og_width = _int(value)
        elif key == "og:image:height":
            og_height = _int(value)
    for key, value in collector.metas:
        if key not in META_IMAGE_KEYS:
            continue
        why = META_IMAGE_KEYS[key]
        if why == "og:image" and og_width and og_height and not portrait_like(og_width, og_height):
            # A declared banner or logo shape: not a headshot.
            continue
        add(value, why, og_width if why == "og:image" else None, og_height if why == "og:image" else None)

    sized = []
    for attrs in collector.imgs:
        width, height = img_dimensions(attrs)
        source = img_source(attrs)
        if source and portrait_like(width, height):
            sized.append((width * height, width, height, source))
    sized.sort(key=lambda item: -item[0])
    for _, width, height, source in sized:
        add(source, f"img {width}x{height}", width, height)
    return out


def website_for(plan_candidate: dict, fm: str):
    """(website, where it came from) for a candidate: the plan's
    campaign_website, else the dossier's first campaign-website source url."""
    website = (plan_candidate.get("campaign_website") or "").strip()
    if website:
        return website, "contests"
    match = re.search(
        r"^\s*-\s+id:.*?\n(?:[ \t]+(?!-)\S.*\n)*?[ \t]+type:[ \t]*campaign-website[ \t]*\n(?:[ \t]+(?!-)\S.*\n)*?[ \t]+url:[ \t]*(\S+)",
        fm, re.M,
    )
    if match:
        return match.group(1).strip().strip('"').strip("'"), "dossier"
    return None, None


# --- network -----------------------------------------------------------------

def _request(url, method="GET", timeout=20, accept="*/*"):
    request = urllib.request.Request(url, method=method, headers={
        "User-Agent": USER_AGENT,
        "Accept": accept,
        "Accept-Language": "en-US,en;q=0.8",
    })
    return urllib.request.urlopen(request, timeout=timeout)


def fetch_page(url: str, timeout: int = 20):
    """(final URL, HTML text) of a campaign site, trying https first and
    once more on a transient failure. Raises on failure."""
    parts = urllib.parse.urlsplit(url if "://" in url else "https://" + url)
    attempts = [urllib.parse.urlunsplit(("https", parts.netloc, parts.path or "/", parts.query, ""))]
    if parts.scheme == "http":
        attempts.append(url)
    attempts.append(attempts[0])  # one retry
    last = None
    for attempt in attempts:
        try:
            with _request(attempt, timeout=timeout, accept="text/html,application/xhtml+xml;q=0.9,*/*;q=0.5") as response:
                charset = response.headers.get_content_charset() or "utf-8"
                return response.geturl(), response.read().decode(charset, errors="replace")
        except (urllib.error.URLError, TimeoutError, OSError, ValueError) as error:
            last = error
    raise RuntimeError(f"{type(last).__name__}: {getattr(last, 'reason', last)}")


def probe_image(url: str, timeout: int = 20):
    """(status, content type, size, bytes-or-None) of an image URL: HEAD
    first, then a GET that also returns the bytes."""
    status, content_type, size = None, None, None
    try:
        with _request(url, method="HEAD", timeout=timeout) as response:
            status = response.status
            content_type = (response.headers.get("Content-Type") or "").split(";")[0].strip().lower()
            size = _int(response.headers.get("Content-Length"))
    except urllib.error.HTTPError as error:
        status = error.code
    except (urllib.error.URLError, TimeoutError, OSError, ValueError):
        status = None
    try:
        with _request(url, method="GET", timeout=timeout, accept="image/*,*/*;q=0.5") as response:
            data = response.read()
            content_type = (response.headers.get("Content-Type") or content_type or "").split(";")[0].strip().lower()
            return response.status, content_type, len(data), data
    except urllib.error.HTTPError as error:
        return error.code, content_type, size, None
    except (urllib.error.URLError, TimeoutError, OSError, ValueError):
        return status, content_type, size, None


# --- review copies -------------------------------------------------------------

def review_copy(data: bytes, path: Path):
    """Write ``data`` as a JPEG no larger than REVIEW_EDGE on its longer edge
    (never upscaled) and return the original (width, height), or None when
    the bytes are not a decodable image."""
    from PIL import Image, UnidentifiedImageError  # lazy: Pillow is optional for the tests

    try:
        image = Image.open(io.BytesIO(data))
        image.load()
    except (UnidentifiedImageError, OSError, ValueError):
        return None
    width, height = image.size
    longest = max(width, height)
    if longest > REVIEW_EDGE:
        scale = REVIEW_EDGE / longest
        image = image.resize((max(1, round(width * scale)), max(1, round(height * scale))))
    if image.mode not in ("RGB", "L"):
        image = image.convert("RGB")
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path, "JPEG", quality=REVIEW_QUALITY)
    return width, height


# --- per package -----------------------------------------------------------------

def package_path(e: election.Election, name: str) -> Path:
    return e.state if name == "statewide" else e.county(name)


def candidates_without_photo(package: Path):
    """[(contest slug, plan candidate, dossier frontmatter)] for every planned
    candidate whose dossier exists here and carries no photo block."""
    plan = json.loads((package / "interim/research-plan.json").read_text())
    out = []
    for contest in plan.get("contests", []):
        if (contest.get("shared") or {}).get("researched_in"):
            continue  # researched (and photographed) in the owning package
        for candidate in contest["candidates"]:
            path = package / "dossiers" / contest["contest_slug"] / f"{candidate['slug']}.md"
            if not path.exists():
                continue
            fm = dossier_photo.frontmatter(path.read_text())
            if fm is None or dossier_photo.has_photo_key(fm):
                continue
            out.append((contest["contest_slug"], candidate, fm))
    return out


def propose_for(package: Path, election_id: str, contest_slug: str, candidate: dict, fm: str, timeout: int):
    entry = {
        "contest_slug": contest_slug,
        "candidate_slug": candidate["slug"],
        "name": candidate.get("name") or candidate["slug"],
        "website": None,
        "website_from": None,
        "status": "no-website",
        "candidates": [],
    }
    website, website_from = website_for(candidate, fm)
    if not website:
        return entry
    entry["website"], entry["website_from"] = website, website_from
    try:
        page_url, html = fetch_page(website, timeout)
    except RuntimeError as error:
        entry["status"] = "fetch-failed"
        entry["error"] = str(error)
        return entry
    found = image_candidates(html, page_url)
    if not found:
        entry["status"] = "no-image-found"
        return entry
    kept = []
    for n, image in enumerate(found, 1):
        status, content_type, size, data = probe_image(image["url"], timeout)
        image["http_status"], image["content_type"], image["bytes"] = status, content_type, size
        if status != 200 or not (content_type or "").startswith("image/") or data is None:
            image["status"] = "fetch-failed"
            kept.append(image)
            continue
        copy = CACHE / election_id / package.name / contest_slug / f"{candidate['slug']}-{n}.jpg"
        dims = review_copy(data, copy)
        if dims is None:
            image["status"] = "fetch-failed"
            image["error"] = "not a decodable image"
        else:
            image["status"] = "ok"
            image["width"], image["height"] = dims
            # Actual shape, for the reviewer: a landscape share card or a
            # banner is not a headshot even when it answered as an image.
            image["portrait_like"] = portrait_like(*dims)
            image["review_copy"] = rel(copy)
        kept.append(image)
    entry["candidates"] = kept
    entry["status"] = "proposed" if any(i["status"] == "ok" for i in kept) else "fetch-failed"
    return entry


def propose_package(package: Path, election_id: str, workers: int = 6, limit: int = None, timeout: int = 20):
    plan_file = package / "interim/research-plan.json"
    if not plan_file.exists():
        raise SystemExit(f"no research plan for {package.name}: {plan_file}")
    todo = candidates_without_photo(package)
    if limit:
        todo = todo[:limit]
    with ThreadPoolExecutor(max_workers=max(1, workers)) as pool:
        proposals = list(pool.map(
            lambda item: propose_for(package, election_id, item[0], item[1], item[2], timeout), todo
        ))
    summary = {status: sum(p["status"] == status for p in proposals) for status in STATUSES}
    summary["images_ok"] = sum(sum(i.get("status") == "ok" for i in p["candidates"]) for p in proposals)
    output = {
        "script": "pipeline/propose_candidate_photos.py",
        "derived_from": [rel(plan_file), rel(package / "dossiers") + "/"],
        "election": election_id,
        "package": package.name,
        "review_copies": rel(CACHE / election_id / package.name) + "/",
        "summary": summary,
        "proposals": proposals,
    }
    (package / "interim/photo-proposals.json").write_text(json.dumps(output, indent=2) + "\n")
    print(f"{package.name}: {summary}")
    return output


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("package", nargs="?", default="king", help="county id, statewide, or --all")
    parser.add_argument("--all", action="store_true", help="every package with a research plan")
    parser.add_argument("--workers", type=int, default=6, help="parallel fetches (default 6)")
    parser.add_argument("--limit", type=int, default=None, help="only the first N candidates (smoke test)")
    parser.add_argument("--timeout", type=int, default=20, help="seconds per request (default 20)")
    election.add_election_arg(parser)
    args = parser.parse_args(argv)
    e = election.Election(args.election)
    packages = e.packages() if args.all else [package_path(e, args.package)]
    for package in packages:
        if not (package / "interim/research-plan.json").exists():
            continue
        propose_package(package, e.id, args.workers, args.limit, args.timeout)


if __name__ == "__main__":
    sys.exit(main())
