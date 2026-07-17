"""Order the unscored candidate dossiers into importance-ranked batches of ~50.

Voter Lifeboat scores candidates incrementally: each batch is the next most
valuable ~50 dossiers to research, so the site can be re-released after any
batch with more of the ballot scored. This script is the single source of
truth for batch ordering; regenerate it as scores land (finished candidates
drop out) or when the importance weights change.

Ordering unit = a "research unit": one contest, except congressional and
legislative races, which are DEDUPED across every county their district
touches (researched once, scores fanned out). Uncontested single-candidate
races get no dossier (everyone advances) and are excluded.

Importance = reach / candidates * contested-boost, where reach approximates
the electorate served (federal/state use fixed district sizes; local races
use an approximate county population, discounted for sub-county districts).
Populations are coarse ordering weights, not published figures.

Input:  data/final/app-data.json
Output: data/final/dossier-batches.json
"""

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
APP_DATA = ROOT / "data/final/app-data.json"
OUT = ROOT / "data/final/dossier-batches.json"

BATCH_SIZE = 50
FEDERAL_REACH = 800_000   # ~1 congressional district
STATE_REACH = 160_000     # ~1 legislative district
SUBCOUNTY_DISCOUNT = 0.4  # PUD / port / other sub-county districts

# Approximate WA county populations — ordering weights only.
POP = {
    "king": 2270000, "pierce": 928000, "snohomish": 840000, "spokane": 550000,
    "clark": 516000, "thurston": 300000, "kitsap": 275000, "yakima": 258000,
    "whatcom": 230000, "benton": 213000, "skagit": 131000, "cowlitz": 113000,
    "franklin": 100000, "grant": 100000, "island": 87000, "lewis": 85000,
    "chelan": 82000, "grays-harbor": 78000, "clallam": 77000, "mason": 68000,
    "walla-walla": 63000, "stevens": 48000, "whitman": 48000, "kittitas": 46000,
    "douglas": 45000, "okanogan": 43000, "jefferson": 33000, "asotin": 25000,
    "pacific": 24000, "klickitat": 23000, "adams": 21000, "san-juan": 18000,
    "pend-oreille": 14000, "skamania": 12000, "lincoln": 11000, "ferry": 7500,
    "wahkiakum": 4500, "columbia": 4000, "garfield": 2300,
}


def fed_state_key(c):
    """Cross-county dedup key for congressional/legislative races, or None."""
    if c["category"] == "Federal":
        n = re.search(r"Congressional District\s*(\d+)", c["district"])
        return ("Federal", f"CD{n.group(1)}") if n else None
    if c["category"] == "State":
        n = re.search(r"Legislative District\s*(\d+)", c["district"])
        if not n:
            return None
        blob = c["office"] + " " + c["district"]
        seat = "SEN" if "Senator" in blob else (
            "REP1" if re.search(r"Pos(?:ition)?\.?\s*1\b", blob, re.I) else "REP2"
        )
        return ("State", f"LD{n.group(1)}", seat)
    return None


def build():
    d = json.load(open(APP_DATA))
    units = {}
    for c in d["contests"]:
        if c["owner"] in ("king", "statewide"):
            continue
        # A researched candidate can legitimately have no scoreable axes.
        # `official-ballot-only` is the queue marker; an empty `scores` object
        # is not (omission-over-guessing and withdrawn candidates depend on it).
        unfinished = [
            x for x in c["candidates"]
            if x.get("evidence_level") == "official-ballot-only"
        ]
        if len(c["candidates"]) < 2:  # uncontested -> no dossier
            continue
        if not unfinished:
            continue
        fk = fed_state_key(c)
        if fk:
            uid = ("FS",) + fk
            u = units.setdefault(uid, {
                "id": "/".join(fk), "kind": "shared",
                "reach": FEDERAL_REACH if c["category"] == "Federal" else STATE_REACH,
                "category": c["category"], "label": f"{c['district']} {c['office']}",
                "candidates": set(), "counties": set(),
            })
            u["counties"].add(c["owner"])
            u["candidates"].update(x["slug"] for x in unfinished)
        else:
            reach = POP.get(c["owner"], 10000)
            if c["category"] in ("PublicUtility", "Port"):
                reach = int(reach * SUBCOUNTY_DISCOUNT)
            units[("L", c["owner"], c["slug"])] = {
                "id": c["slug"], "kind": "local", "reach": reach,
                "category": c["category"], "label": f"{c['owner']}: {c['district']} {c['office']}",
                "candidates": set(x["slug"] for x in unfinished), "counties": {c["owner"]},
            }

    def importance(u):
        n = len(u["candidates"]) or 1
        boost = 1.4 if n >= 3 else 1.0
        return u["reach"] / n * boost

    # stable order: importance desc, then id for determinism
    ordered = sorted(units.values(), key=lambda u: (-importance(u), u["id"]))

    batches, cur, cur_n = [], [], 0
    for u in ordered:
        if cur_n >= BATCH_SIZE:
            batches.append((cur, cur_n))
            cur, cur_n = [], 0
        cur.append(u)
        cur_n += len(u["candidates"])
    if cur:
        batches.append((cur, cur_n))

    out = {
        "derived_from": ["data/final/app-data.json"],
        "script": "pipeline/build_dossier_batches.py",
        "batch_size_target": BATCH_SIZE,
        "total_units": len(ordered),
        "total_dossiers": sum(len(u["candidates"]) for u in ordered),
        "total_batches": len(batches),
        "batches": [
            {
                "batch": i,
                "dossiers": n,
                "races": len(b),
                "units": [
                    {
                        "id": u["id"], "kind": u["kind"], "label": u["label"],
                        "candidates": sorted(u["candidates"]),
                        "counties": sorted(u["counties"]),
                    }
                    for u in b
                ],
            }
            for i, (b, n) in enumerate(batches, 1)
        ],
    }
    OUT.write_text(json.dumps(out, indent=2))
    print(f"units: {out['total_units']}  dossiers: {out['total_dossiers']}  batches: {out['total_batches']}")
    for bt in out["batches"]:
        shared = sum(1 for u in bt["units"] if u["kind"] == "shared")
        print(f"  batch {bt['batch']:2d}: {bt['dossiers']:3d} dossiers, {bt['races']:2d} races ({shared} shared federal/state)")


if __name__ == "__main__":
    build()
