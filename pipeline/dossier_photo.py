"""The Candidate Photo block of a candidate dossier's frontmatter (issue #33).

    photo:
      url: https://...   # direct https image URL (image/* content type)
      page: https://...  # the page a human sees the photo on
      kind: government   # pamphlet | government | campaign-website | other

One parser shared by assemble_app_data.py (which ships the block) and
verify_dossiers.py (which checks it). The block is optional; a Candidate
without one gets an Initials Portrait in the app.
"""

import re

PHOTO_KINDS = ("pamphlet", "government", "campaign-website", "other")
PHOTO_KEYS = ("url", "page", "kind")

_BLOCK = re.compile(r"^photo:[ \t]*(?P<inline>\S.*)?\n(?P<body>(?:[ \t]+\S.*\n?)*)", re.M)


def frontmatter(text: str):
    """The frontmatter text of a dossier, or None when it has none."""
    match = re.match(r"^---\n(.*?)\n---", text, re.S)
    return match.group(1) if match else None


def has_photo_key(fm: str) -> bool:
    return bool(re.search(r"^photo:", fm, re.M))


def parse_photo_block(fm: str):
    """The ``photo`` block of a frontmatter as a dict of its scalar keys.

    Returns None when the frontmatter has no top-level ``photo:`` key. A
    malformed block (``photo: x`` inline, or no indented keys) returns an
    empty dict so a verifier can report it; ``photo_problems`` does the
    rule check.
    """
    match = _BLOCK.search(fm)
    if not match:
        return None
    block = {}
    if match.group("inline"):
        return block
    for line in match.group("body").splitlines():
        kv = re.match(r"[ \t]+(\w[\w-]*):[ \t]*(.*?)[ \t]*$", line)
        if kv:
            value = kv.group(2).strip().strip('"').strip("'")
            block[kv.group(1)] = value
    return block


def photo_problems(block) -> list:
    """Offline rule violations of a parsed block (empty when it is valid)."""
    if not block:
        return ["photo block has no url/page/kind"]
    problems = []
    for key in PHOTO_KEYS:
        if not block.get(key):
            problems.append(f"photo.{key} missing")
    for key in ("url", "page"):
        value = block.get(key)
        if value and not value.startswith("https://"):
            problems.append(f"photo.{key} is not https://")
    url = block.get("url", "")
    if url.lower().split("?")[0].endswith(".pdf"):
        problems.append("photo.url is a PDF")
    kind = block.get("kind")
    if kind and kind not in PHOTO_KINDS:
        problems.append(f"photo.kind {kind!r} not one of {', '.join(PHOTO_KINDS)}")
    return problems


def shipped_photo(block):
    """The ``{url, page, kind}`` the app ships, or None when the block is
    absent or invalid (an invalid block is a verifier error, not app data)."""
    if not block or photo_problems(block):
        return None
    return {key: block[key] for key in PHOTO_KEYS}
