"""Stage: interim -> interim. Map every primary candidate and measure to the
pamphlet pages that mention them.

Inputs:
  data/interim/contests.json
  data/interim/measures.json
  data/interim/pamphlet-text/edition-{1,2}/page-NNN.txt

Output:
  data/interim/pamphlet-index.json  ({candidate_slug: [{edition, page}...]},
                                     {measure_slug: [...]})

PDF extraction inserts soft breaks and ligature spaces, so matching is done on
a whitespace-normalized, lowercased haystack.
"""

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INTERIM = ROOT / "data/interim"
PAGES = INTERIM / "pamphlet-text"


def norm(s: str) -> str:
    for lig, plain in [("ﬁ", "fi"), ("ﬂ", "fl"), ("ﬀ", "ff"), ("ﬃ", "ffi"), ("ﬄ", "ffl")]:
        s = s.replace(lig, plain)
    return re.sub(r"\s+", " ", s.lower())


def squash(s: str) -> str:
    """Aggressive: drop all non-letters. Survives 'Pramila \nJayapal' and 'ﬁ  ght'."""
    return re.sub(r"[^a-z]", "", norm(s))


pages = {}  # (edition, page_no) -> squashed text
for ed_dir in sorted(PAGES.glob("edition-*")):
    for pf in sorted(ed_dir.glob("page-*.txt")):
        pages[(ed_dir.name, int(pf.stem.split("-")[1]))] = squash(pf.read_text())

contests = json.load(open(INTERIM / "contests.json"))
measures = json.load(open(INTERIM / "measures.json"))

index = {"derived_from": ["data/interim/contests.json", "data/interim/measures.json",
                          "data/interim/pamphlet-text/"],
         "script": "pipeline/build_pamphlet_index.py",
         "candidates": {}, "measures": {}, "unmatched": []}

for con in contests["contests"]:
    for c in con["candidates"]:
        needle = squash(c["name"])
        hits = [{"edition": ed, "page": p} for (ed, p), text in sorted(pages.items())
                if needle in text]
        if hits:
            index["candidates"][c["slug"]] = hits
        else:
            index["unmatched"].append({"type": "candidate", "slug": c["slug"], "name": c["name"]})

for m in measures["measures"]:
    needle = squash(m["title"])
    hits = [{"edition": ed, "page": p} for (ed, p), text in sorted(pages.items())
            if needle in text]
    if hits:
        index["measures"][m["slug"]] = hits
    else:
        index["unmatched"].append({"type": "measure", "slug": m["slug"], "title": m["title"]})

(INTERIM / "pamphlet-index.json").write_text(json.dumps(index, indent=2))
print(f"candidates indexed: {len(index['candidates'])}/{sum(len(c['candidates']) for c in contests['contests'])}")
print(f"measures indexed:   {len(index['measures'])}/{len(measures['measures'])}")
for u in index["unmatched"]:
    print("  UNMATCHED:", u)
