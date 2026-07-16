"""Stage: interim -> interim. Emit the dossier research work manifest.

Depth rule: contests with 3+ candidates are 'deep' (the primary genuinely
decides something there — WA top-2); 1-2 candidate contests are 'light'
(everyone advances regardless).

Input:  data/interim/contests.json, measures.json, pamphlet-index.json
Output: data/interim/research-plan.json
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INTERIM = ROOT / "data/interim"

contests = json.load(open(INTERIM / "contests.json"))["contests"]
measures = json.load(open(INTERIM / "measures.json"))["measures"]
pidx = json.load(open(INTERIM / "pamphlet-index.json"))

plan = {"derived_from": ["data/interim/contests.json", "data/interim/measures.json",
                         "data/interim/pamphlet-index.json"],
        "script": "pipeline/build_research_plan.py", "contests": [], "measures": []}

for con in contests:
    depth = "deep" if len(con["candidates"]) >= 3 else "light"
    plan["contests"].append({
        "contest_slug": con["slug"],
        "category": con["category"],
        "office": con["office"],
        "district": con["district"],
        "depth": depth,
        "candidates": [{
            "slug": c["slug"],
            "name": c["name"],
            "party_preference": c.get("party_preference"),
            "campaign_website": c.get("campaign_website"),
            "pamphlet_pages": pidx["candidates"].get(c["slug"], []),
        } for c in con["candidates"]],
    })

for m in measures:
    plan["measures"].append({**m, "pamphlet_pages": pidx["measures"].get(m["slug"], [])})

(INTERIM / "research-plan.json").write_text(json.dumps(plan, indent=2))
deep = [c for c in plan["contests"] if c["depth"] == "deep"]
light = [c for c in plan["contests"] if c["depth"] == "light"]
print(f"deep contests: {len(deep)} ({sum(len(c['candidates']) for c in deep)} candidates)")
print(f"light contests: {len(light)} ({sum(len(c['candidates']) for c in light)} candidates)")
