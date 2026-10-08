"""Stage: interim -> interim. Map every King candidate and measure to the
pamphlet pages that mention them.

Usage: python3 pipeline/build_pamphlet_index.py [--election <id>]

Inputs (K = data/washington-state/elections/<id>/counties/king):
  K/interim/contests.json
  K/interim/measures.json
  pamphlet page text, either
    K/interim/pdf-text/<name>.txt  (extract_pdf_text.mjs, "--- page N ---"
                                    separators; only files whose manifest
                                    source pointer is under raw/pamphlet/ or
                                    raw/sos/, so the sample ballot is skipped)
  or, when there is no pdf-text manifest,
    K/interim/pamphlet-text/edition-*/page-NNN.txt  (extract_pamphlet_text.py)

Output:
  K/interim/pamphlet-index.json  ({candidate_slug: [{edition, page}...]},
                                  {measure_slug: [...]})

PDF extraction inserts soft breaks and ligature spaces, so matching is done on
a whitespace-normalized, lowercased haystack.
"""

import json
import re

import election
from election import ROOT, rel

PAMPHLET_POINTER_DIRS = ("/raw/pamphlet/", "/raw/sos/")


def norm(s: str) -> str:
    for lig, plain in [("ﬁ", "fi"), ("ﬂ", "fl"), ("ﬀ", "ff"), ("ﬃ", "ffi"), ("ﬄ", "ffl")]:
        s = s.replace(lig, plain)
    return re.sub(r"\s+", " ", s.lower())


def squash(s: str) -> str:
    """Aggressive: drop all non-letters. Survives 'Pramila \nJayapal' and 'ﬁ  ght'."""
    return re.sub(r"[^a-z]", "", norm(s))


def split_pages(text: str) -> dict[int, str]:
    """Pages of an extract_pdf_text.mjs file, keyed by 1-based page number."""
    return {int(m.group(1)): m.group(2)
            for m in re.finditer(r"^--- page (\d+) ---\n(.*?)(?=^--- page \d+ ---|\Z)", text, re.S | re.M)}


def load_pages(interim):
    """((edition, page) -> squashed text, derived_from entries for the page text)."""
    pages = {}
    manifest = interim / "pdf-text/manifest.json"
    if manifest.exists():
        derived = []
        for entry in json.loads(manifest.read_text())["files"]:
            if "output" not in entry or not any(d in entry["source_pointer"] for d in PAMPHLET_POINTER_DIRS):
                continue
            out = ROOT / entry["output"]
            for page, text in split_pages(out.read_text()).items():
                pages[(out.stem, page)] = squash(text)
            derived.append(entry["output"])
        return pages, derived
    page_dir = interim / "pamphlet-text"
    for ed_dir in sorted(page_dir.glob("edition-*")):
        for pf in sorted(ed_dir.glob("page-*.txt")):
            pages[(ed_dir.name, int(pf.stem.split("-")[1]))] = squash(pf.read_text())
    return pages, [rel(page_dir) + "/"]


def build(election_id: str | None = None) -> dict:
    interim = election.Election(election_id).county("king") / "interim"
    pages, page_sources = load_pages(interim)
    contests = json.loads((interim / "contests.json").read_text())
    measures = json.loads((interim / "measures.json").read_text())

    index = {"derived_from": [rel(interim / "contests.json"), rel(interim / "measures.json"), *page_sources],
             "script": "pipeline/build_pamphlet_index.py",
             "candidates": {}, "measures": {}, "unmatched": []}

    def hits_for(needle):
        return [{"edition": ed, "page": p} for (ed, p), text in sorted(pages.items()) if needle in text]

    for con in contests["contests"]:
        for c in con["candidates"]:
            hits = hits_for(squash(c["name"]))
            if hits:
                index["candidates"][c["slug"]] = hits
            else:
                index["unmatched"].append({"type": "candidate", "slug": c["slug"], "name": c["name"]})

    for m in measures["measures"]:
        hits = hits_for(squash(m["title"]))
        if hits:
            index["measures"][m["slug"]] = hits
        else:
            index["unmatched"].append({"type": "measure", "slug": m["slug"], "title": m["title"]})
    return index


def main():
    e = election.Election(election.from_argv())
    index = build(e.id)
    interim = e.county("king") / "interim"
    contests = json.loads((interim / "contests.json").read_text())
    measures = json.loads((interim / "measures.json").read_text())
    (interim / "pamphlet-index.json").write_text(json.dumps(index, indent=2))
    print(f"candidates indexed: {len(index['candidates'])}/{sum(len(c['candidates']) for c in contests['contests'])}")
    print(f"measures indexed:   {len(index['measures'])}/{len(measures['measures'])}")
    for u in index["unmatched"]:
        print("  UNMATCHED:", u)


if __name__ == "__main__":
    main()
