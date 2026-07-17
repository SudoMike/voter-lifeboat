"""Stage: QA. Verify every planned candidate/measure has a dossier with valid
frontmatter, and report evidence-level distribution.

Input:  data/washington-state/counties/king/interim/research-plan.json,
        data/washington-state/counties/king/dossiers/**
Output: data/washington-state/counties/king/interim/dossier-audit.json (+ console report)
"""

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STATE = ROOT / "data/washington-state/statewide"
KING = ROOT / "data/washington-state/counties/king"
DOSS_DIRS = [STATE / "dossiers", KING / "dossiers"]
plan = json.load(open(KING / "interim/research-plan.json"))

audit = {"script": "pipeline/verify_dossiers.py",
         "derived_from": [
             "data/washington-state/counties/king/interim/research-plan.json",
             "data/washington-state/counties/king/dossiers/",
         ],
         "missing": [], "no_frontmatter": [], "evidence_levels": {}, "contest_overviews_missing": []}

def frontmatter(p: Path):
    t = p.read_text()
    m = re.match(r"^---\n(.*?)\n---", t, re.S)
    return m.group(1) if m else None

for con in plan["contests"]:
    cdir = next((d / con["contest_slug"] for d in DOSS_DIRS if (d / con["contest_slug"]).exists()), None)
    if cdir is None or not (cdir / "_contest.md").exists():
        audit["contest_overviews_missing"].append(con["contest_slug"])
    for c in con["candidates"]:
        f = cdir / f"{c['slug']}.md" if cdir else None
        if f is None or not f.exists():
            audit["missing"].append(f"{con['contest_slug']}/{c['slug']}")
            continue
        fm = frontmatter(f)
        if not fm:
            audit["no_frontmatter"].append(f"{con['contest_slug']}/{c['slug']}")
            continue
        lvl_m = re.search(r"evidence_level:\s*(\S+)", fm)
        lvl = lvl_m.group(1) if lvl_m else "MISSING"
        audit["evidence_levels"][lvl] = audit["evidence_levels"].get(lvl, 0) + 1

for m in plan["measures"]:
    f = KING / "dossiers/measures" / f"{m['slug']}.md"
    if not f.exists():
        audit["missing"].append(f"measures/{m['slug']}")

(KING / "interim/dossier-audit.json").write_text(json.dumps(audit, indent=2))
print("missing:", audit["missing"] or "none")
print("no frontmatter:", audit["no_frontmatter"] or "none")
print("overview missing:", audit["contest_overviews_missing"] or "none")
print("evidence levels:", audit["evidence_levels"])
