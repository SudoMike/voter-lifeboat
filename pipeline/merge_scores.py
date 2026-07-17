"""Stage: scoring + refutations -> final. Apply refutation verdicts and emit
the app-facing score files.

Rules:
  refuted            -> drop that candidate-axis score
  adjust             -> apply adjusted_score and/or adjusted_confidence
  missing (med/high) -> add the proposed score (low-confidence proposals are
                        dropped: the app excludes low anyway)
  measures: same verdict semantics against lean_mappings ("_display" verdicts
  are notes only)

Outputs: data/final/scores.json, data/final/measures.json
Every output carries derived_from + the counts of applied verdicts.
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WA = ROOT / "data/washington-state"
PACKAGES = [WA / "statewide"] + [p for p in sorted((WA / "counties").iterdir()) if p.is_dir()]
SCORING_DIRS = [p / "scoring" for p in PACKAGES if (p / "scoring").is_dir()]
FINAL = ROOT / "data/final"

stats = {"upheld": 0, "adjust": 0, "refuted": 0, "missing_added": 0, "missing_dropped_low": 0}

contests_out = []
for scoring_dir in SCORING_DIRS:
    refut = scoring_dir / "refutations"
    for f in sorted(scoring_dir.glob("*.json")):
        if f.name == "measures.json":
            continue
        data = json.load(open(f))
        slug = data["contest_slug"]
        rf = refut / f"{slug}.json"
        verdicts, missing = [], []
        if rf.exists():
            r = json.load(open(rf))
            verdicts = r.get("verdicts", [])
            missing = r.get("missing", [])
        by_cand = {c["slug"]: c for c in data["candidates"]}
        for v in verdicts:
            cand = by_cand.get(v["candidate"])
            if not cand:
                continue
            s = (cand.get("scores") or {}).get(v["axis"])
            if not s:
                continue
            if v["verdict"] == "refuted":
                del cand["scores"][v["axis"]]
                stats["refuted"] += 1
            elif v["verdict"] == "adjust":
                if "adjusted_score" in v and v["adjusted_score"] is not None:
                    s["score"] = v["adjusted_score"]
                if "adjusted_confidence" in v and v["adjusted_confidence"]:
                    s["confidence"] = v["adjusted_confidence"]
                s["adjusted_by_refutation"] = True
                stats["adjust"] += 1
            else:
                stats["upheld"] += 1
        for m in missing:
            cand = by_cand.get(m["candidate"])
            if not cand:
                continue
            if m.get("confidence") not in ("medium", "high"):
                stats["missing_dropped_low"] += 1
                continue
            cand.setdefault("scores", {})[m["axis"]] = {
                "score": m["proposed_score"],
                "confidence": m["confidence"],
                "citations": m.get("citations", []),
                "basis": m.get("basis", ""),
                "added_by_refutation": True,
            }
            stats["missing_added"] += 1
        contests_out.append(data)

measures_out = []
measure_sources = []
for scoring_dir in SCORING_DIRS:
    measures_file = scoring_dir / "measures.json"
    if not measures_file.exists():
        continue
    meas = json.load(open(measures_file))
    package_path = scoring_dir.relative_to(ROOT).as_posix()
    measure_sources.extend([f"{package_path}/measures.json", f"{package_path}/refutations/measures.json"])
    mrf = scoring_dir / "refutations/measures.json"
    if mrf.exists():
        r = json.load(open(mrf))
        by_slug = {m["slug"]: m for m in meas["measures"]}
        for v in r.get("verdicts", []):
            m = by_slug.get(v.get("measure"))
            if not m:
                continue
            lm = (m.get("lean_mappings") or {}).get(v.get("axis"))
            if not lm:
                continue
            if v.get("verdict") == "refuted":
                del m["lean_mappings"][v["axis"]]
                stats["refuted"] += 1
            elif v.get("verdict") == "adjust":
                if v.get("adjusted_direction") in (-1, 1):
                    lm["direction"] = v["adjusted_direction"]
                lm["adjusted_by_refutation"] = True
                stats["adjust"] += 1
            else:
                stats["upheld"] += 1
    measures_out.extend(meas["measures"])

FINAL.mkdir(exist_ok=True)
(FINAL / "scores.json").write_text(json.dumps({
    "derived_from": [source for scoring_dir in SCORING_DIRS for source in (
        f"{scoring_dir.relative_to(ROOT).as_posix()}/*.json",
        f"{scoring_dir.relative_to(ROOT).as_posix()}/refutations/*.json",
    )],
    "script": "pipeline/merge_scores.py",
    "verdict_stats": stats,
    "contests": contests_out,
}, indent=2))
(FINAL / "measures.json").write_text(json.dumps({
    "derived_from": measure_sources,
    "script": "pipeline/merge_scores.py",
    "measures": measures_out,
}, indent=2))

n = sum(len(c.get("scores") or {}) for con in contests_out for c in con["candidates"])
print("verdicts applied:", stats)
print("final candidate-axis scores:", n)
