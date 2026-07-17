"""Stage: QA. Mechanically validate package scoring JSON against the plan,
the rubric, and the dossiers.

Checks: file/candidate completeness, integer scores in [-2,2], axis
applicability (category + judicial restriction), citations exist in the
cited dossier's frontmatter, evidence_level matches the dossier.
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STATE = ROOT / "data/washington-state/statewide"
KING = ROOT / "data/washington-state/counties/king"
SCORING_DIRS = [STATE / "scoring", KING / "scoring"]
DOSS_DIRS = [STATE / "dossiers", KING / "dossiers"]

plan = json.load(open(KING / "interim/research-plan.json"))
rubric = json.load(open(ROOT / "data/final/rubric.json"))
applies = {a["id"]: set(a["applies_to"]) for a in rubric["axes"]}
contests_meta = {c["slug"]: c for c in json.load(open(KING / "interim/contests.json"))["contests"]}

JUDICIAL_OFFICES = re.compile(r"justice|judge|municipal-court")
JUDICIAL_AXES = {"judicial", "safety", "experience"}

errors, warnings = [], []

def dossier_sources_and_level(contest, cand):
    f = next((d / contest / f"{cand}.md" for d in DOSS_DIRS if (d / contest / f"{cand}.md").exists()), None)
    if f is None:
        return None, None
    t = f.read_text()
    fm = re.match(r"^---\n(.*?)\n---", t, re.S)
    ids = set(re.findall(r"-\s+id:\s*(\S+)", fm.group(1))) if fm else set()
    lvl = re.search(r"evidence_level:\s*(\S+)", fm.group(1)) if fm else None
    return ids, (lvl.group(1) if lvl else None)

for con in plan["contests"]:
    slug = con["contest_slug"]
    f = next((d / f"{slug}.json" for d in SCORING_DIRS if (d / f"{slug}.json").exists()), None)
    if f is None:
        errors.append(f"MISSING FILE {slug}")
        continue
    data = json.load(open(f))
    category = contests_meta[slug]["category"]
    is_judicial = bool(JUDICIAL_OFFICES.search(slug))
    scored = {c["slug"]: c for c in data["candidates"]}
    for cand in con["candidates"]:
        cs = scored.get(cand["slug"])
        if not cs:
            errors.append(f"{slug}: candidate missing {cand['slug']}")
            continue
        src_ids, lvl = dossier_sources_and_level(slug, cand["slug"])
        if lvl and cs.get("evidence_level") != lvl:
            warnings.append(f"{slug}/{cand['slug']}: evidence_level {cs.get('evidence_level')} != dossier {lvl}")
        for axis, s in (cs.get("scores") or {}).items():
            if axis not in applies:
                errors.append(f"{slug}/{cand['slug']}: unknown axis {axis}")
                continue
            if category not in applies[axis] and not (is_judicial and axis in JUDICIAL_AXES):
                errors.append(f"{slug}/{cand['slug']}: axis {axis} not applicable to {category}")
            if is_judicial and axis not in JUDICIAL_AXES:
                errors.append(f"{slug}/{cand['slug']}: judicial contest scored on {axis}")
            if not isinstance(s.get("score"), int) or not -2 <= s["score"] <= 2:
                errors.append(f"{slug}/{cand['slug']}/{axis}: bad score {s.get('score')}")
            if s.get("confidence") not in ("high", "medium", "low"):
                errors.append(f"{slug}/{cand['slug']}/{axis}: bad confidence")
            for cit in s.get("citations", []):
                if src_ids is not None and cit not in src_ids:
                    errors.append(f"{slug}/{cand['slug']}/{axis}: citation {cit} not in dossier")
            if not s.get("citations"):
                errors.append(f"{slug}/{cand['slug']}/{axis}: no citations")
        if cs.get("withdrawn") and cs.get("scores"):
            errors.append(f"{slug}/{cand['slug']}: withdrawn but has scores")

m = json.load(open(KING / "scoring/measures.json"))
mslugs = {x["slug"] for x in m["measures"]}
planned = {x["slug"] for x in plan["measures"]}
if mslugs != planned:
    errors.append(f"measures mismatch: missing {planned - mslugs}, extra {mslugs - planned}")
for meas in m["measures"]:
    for axis, lm in (meas.get("lean_mappings") or {}).items():
        if axis not in applies:
            errors.append(f"measure {meas['slug']}: unknown axis {axis}")
        d = lm.get("direction")
        if d not in (-2, -1, 1, 2):
            errors.append(f"measure {meas['slug']}/{axis}: bad direction {d}")

n_scores = 0
for scoring_dir in SCORING_DIRS:
    for f in scoring_dir.glob("*.json"):
        if f.name == "measures.json":
            continue
        d = json.load(open(f))
        n_scores += sum(len(c.get("scores") or {}) for c in d["candidates"])

print(f"errors: {len(errors)}")
for e in errors:
    print("  E:", e)
print(f"warnings: {len(warnings)}")
for w in warnings:
    print("  W:", w)
print(f"total candidate-axis scores: {n_scores}")
sys.exit(1 if errors else 0)
