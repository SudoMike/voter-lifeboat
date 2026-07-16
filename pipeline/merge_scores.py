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
SCORING = ROOT / "data/scoring"
REFUT = SCORING / "refutations"
FINAL = ROOT / "data/final"

stats = {"upheld": 0, "adjust": 0, "refuted": 0, "missing_added": 0, "missing_dropped_low": 0}

contests_out = []
for f in sorted(SCORING.glob("*.json")):
    if f.name == "measures.json":
        continue
    data = json.load(open(f))
    slug = data["contest_slug"]
    rf = REFUT / f"{slug}.json"
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

meas = json.load(open(SCORING / "measures.json"))
mrf = REFUT / "measures.json"
if mrf.exists():
    r = json.load(open(mrf))
    by_slug = {m["slug"]: m for m in meas["measures"]}
    for v in r.get("verdicts", []):
        m = by_slug.get(v["candidate"])
        if not m or v["axis"] == "_display":
            continue
        lm = (m.get("lean_mappings") or {}).get(v["axis"])
        if not lm:
            continue
        if v["verdict"] == "refuted":
            del m["lean_mappings"][v["axis"]]
            stats["refuted"] += 1
        elif v["verdict"] == "adjust":
            if "adjusted_score" in v and v["adjusted_score"] is not None:
                lm["direction"] = v["adjusted_score"]
            lm["adjusted_by_refutation"] = True
            stats["adjust"] += 1
        else:
            stats["upheld"] += 1

FINAL.mkdir(exist_ok=True)
(FINAL / "scores.json").write_text(json.dumps({
    "derived_from": ["data/scoring/*.json", "data/scoring/refutations/*.json"],
    "script": "pipeline/merge_scores.py",
    "verdict_stats": stats,
    "contests": contests_out,
}, indent=2))
(FINAL / "measures.json").write_text(json.dumps({
    "derived_from": ["data/scoring/measures.json", "data/scoring/refutations/measures.json"],
    "script": "pipeline/merge_scores.py",
    "measures": meas["measures"],
}, indent=2))

n = sum(len(c.get("scores") or {}) for con in contests_out for c in con["candidates"])
print("verdicts applied:", stats)
print("final candidate-axis scores:", n)
