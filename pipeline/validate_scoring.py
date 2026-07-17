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
COUNTIES = ROOT / "data/washington-state/counties"
PACKAGES = [STATE] + [p for p in sorted(COUNTIES.iterdir()) if p.is_dir()]
SCORING_DIRS = [p / "scoring" for p in PACKAGES if (p / "scoring").is_dir()]

rubric = json.load(open(ROOT / "data/final/rubric.json"))
applies = {a["id"]: set(a["applies_to"]) for a in rubric["axes"]}

JUDICIAL_OFFICES = re.compile(r"justice|judge|municipal-court")
JUDICIAL_AXES = {"judicial", "safety", "experience"}
EVIDENCE_LEVELS = {"rich", "moderate", "pamphlet-only"}

errors, warnings = [], []

def dossier_sources_and_level(package, contest, cand):
    search_dirs = [package / "dossiers"]
    if package.name == "king":
        search_dirs.append(STATE / "dossiers")
    f = next((d / contest / f"{cand}.md" for d in search_dirs if (d / contest / f"{cand}.md").exists()), None)
    if f is None:
        return None, None
    t = f.read_text()
    fm = re.match(r"^---\n(.*?)\n---", t, re.S)
    ids = set(re.findall(r"-\s+id:\s*(\S+)", fm.group(1))) if fm else set()
    lvl = re.search(r"evidence_level:\s*(\S+)", fm.group(1)) if fm else None
    return ids, (lvl.group(1) if lvl else None)

for package in PACKAGES:
    plan_file = package / "interim/research-plan.json"
    contests_file = package / "interim/contests.json"
    if not plan_file.exists() or not contests_file.exists():
        continue
    plan = json.load(open(plan_file))
    contests_meta = {c["slug"]: c for c in json.load(open(contests_file))["contests"]}
    for con in plan["contests"]:
        slug = con["contest_slug"]
        # Legacy King plans include statewide contests. Prefer the owning
        # package, then fall back to another package during the transition.
        candidates = [package / "scoring" / f"{slug}.json"]
        if package.name == "king":
            candidates.append(STATE / "scoring" / f"{slug}.json")
        f = next((candidate for candidate in candidates if candidate.exists()), None)
        if f is None:
            # Research plans are the full work queue. An untouched contest is
            # valid during incremental rollout; once its dossier exists, its
            # score file is required.
            dossier_started = (package / "dossiers" / slug).is_dir()
            if package.name == "king":
                dossier_started = dossier_started or (STATE / "dossiers" / slug).is_dir()
            if dossier_started:
                errors.append(f"{package.name}: MISSING FILE {slug}")
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
            src_ids, lvl = dossier_sources_and_level(package, slug, cand["slug"])
            if lvl not in EVIDENCE_LEVELS:
                errors.append(f"{slug}/{cand['slug']}: invalid dossier evidence_level {lvl}")
            if cs.get("evidence_level") not in EVIDENCE_LEVELS:
                errors.append(
                    f"{slug}/{cand['slug']}: invalid scoring evidence_level {cs.get('evidence_level')}"
                )
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

    measures_file = package / "scoring/measures.json"
    if not measures_file.exists():
        # Plans describe the full incremental queue. Require scoring only
        # after measure research has actually started for this package.
        if plan.get("measures") and (package / "dossiers/measures").is_dir():
            errors.append(f"{package.name}: MISSING FILE measures.json")
        continue
    m = json.load(open(measures_file))
    mslugs = {x["slug"] for x in m["measures"]}
    planned = {x["slug"] for x in plan.get("measures", [])}
    if mslugs != planned:
        errors.append(f"{package.name} measures mismatch: missing {planned - mslugs}, extra {mslugs - planned}")
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
