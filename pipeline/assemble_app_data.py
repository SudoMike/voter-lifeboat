"""Stage: final assembly. Merge contests, refutation-hardened scores, dossier
source lists, measures, rubric, interview, and district-scoping rules into
the single JSON the app ships.

Inputs:  data/interim/contests.json, data/final/{scores,measures,rubric,interview}.json,
         data/interim/pamphlet-index.json, data/dossiers/**（frontmatter sources）
Outputs: data/final/app-data.json  (canonical)
         app/public/data/app-data.json  (build copy, identical)

District scoping: each contest/measure carries a `scope` the app matches
against the voter's GIS lookup results:
  {"layer": "CONGDST"|"LEGDST"|"KCCDST"|"SCCDST"|"JUDDST"|"FIRDST"|"SCHDST"|"CITY", "value": "..."}
  or {"layer": "ALL"} for countywide/statewide contests.
"""

import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INTERIM = ROOT / "data/interim"
FINAL = ROOT / "data/final"
DOSS = ROOT / "data/dossiers"

contests = json.load(open(INTERIM / "contests.json"))["contests"]
scores = {c["contest_slug"]: c for c in json.load(open(FINAL / "scores.json"))["contests"]}
measures_scored = {m["slug"]: m for m in json.load(open(FINAL / "measures.json"))["measures"]}
measures_meta = json.load(open(INTERIM / "measures.json"))["measures"]
pidx = json.load(open(INTERIM / "pamphlet-index.json"))
rubric = json.load(open(FINAL / "rubric.json"))
interview = json.load(open(FINAL / "interview.json"))


def parse_sources(contest_slug: str, cand_slug: str):
    """Parse the frontmatter sources list of a dossier into dicts."""
    f = DOSS / contest_slug / f"{cand_slug}.md"
    if not f.exists():
        return []
    fm_m = re.match(r"^---\n(.*?)\n---", f.read_text(), re.S)
    if not fm_m:
        return []
    fm = fm_m.group(1)
    m = re.search(r"^sources:\s*\n(.*)\Z", fm, re.S | re.M)
    if not m:
        return []
    out, cur = [], None
    for line in m.group(1).split("\n"):
        if re.match(r"\s*-\s+id:", line):
            if cur:
                out.append(cur)
            cur = {"id": line.split("id:", 1)[1].strip()}
        elif cur is not None:
            kv = re.match(r"\s+(\w[\w-]*):\s*(.+?)\s*$", line)
            if kv:
                v = kv.group(2).strip().strip('"').strip("'")
                cur[kv.group(1)] = v
    if cur:
        out.append(cur)
    return out


def contest_scope(con):
    cat, district, office = con["category"], con["district"], con["office"]
    if cat == "Federal":
        n = re.search(r"Congressional District (\d+)", district).group(1)
        return {"layer": "CONGDST", "value": n}
    if cat == "State":
        n = re.search(r"Legislative District No\.\s*(\d+)", office + " " + district)
        return {"layer": "LEGDST", "value": n.group(1)}
    if cat == "StateSupremeCourt":
        return {"layer": "ALL"}
    if cat == "County":
        m = re.search(r"Council District No\.\s*(\d+)", district)
        return {"layer": "KCCDST", "value": m.group(1)} if m else {"layer": "ALL"}
    if cat == "DistrictCourt":
        return {"layer": "JUDDST", "value": "NE"}
    if cat == "City":
        m = re.search(r"Council District No\.\s*(\d+)", district)
        if m:
            return {"layer": "SCCDST", "value": f"SCC{m.group(1)}"}
        return {"layer": "CITY", "value": "Seattle"}
    raise ValueError(f"no scope rule for {con['slug']}")


MEASURE_SCOPES = {
    "city-of-black-diamond-proposition-no-1": {"layer": "CITY", "value": "Black Diamond"},
    "city-of-covington-proposition-no-1": {"layer": "CITY", "value": "Covington"},
    "city-of-seattle-proposition-no-1": {"layer": "CITY", "value": "Seattle"},
    "skykomish-school-district-no-404-proposition-no-1": {"layer": "SCHDST", "value": "404"},
    "king-county-fire-protection-district-no-43-proposition-no-1": {"layer": "FIRDST", "value": "43"},
    "king-county-fire-protection-district-no-47-proposition-no-1": {"layer": "FIRDST", "value": "47"},
    "snoqualmie-pass-fire-and-rescue-proposition-no-1": {"layer": "FIRDST", "value": "51"},
}

# State contests: office string carries the position; district carries the LD.
# Fix contest_scope's State regex to search the district field, which holds
# "State Representative Position No. 1" or the LD depending on parse order.

out_contests = []
for con in contests:
    sc = scores.get(con["slug"])
    if not sc:
        raise SystemExit(f"no scores for {con['slug']}")
    scored_by_slug = {c["slug"]: c for c in sc["candidates"]}
    cands = []
    for c in con["candidates"]:
        s = scored_by_slug[c["slug"]]
        cands.append({
            "slug": c["slug"],
            "name": c["name"],
            "party": c.get("party_preference"),
            "ballot_order": c.get("ballot_order"),
            "website": c.get("campaign_website"),
            "pamphlet_pages": pidx["candidates"].get(c["slug"], []),
            "evidence_level": s.get("evidence_level"),
            "withdrawn": bool(s.get("withdrawn")),
            "summary": s.get("summary"),
            "highlights": s.get("highlights", []),
            "scores": s.get("scores", {}),
            "sources": parse_sources(con["slug"], c["slug"]),
        })
    cands.sort(key=lambda x: (x["ballot_order"] or 99))
    out_contests.append({
        "slug": con["slug"],
        "category": con["category"],
        "office": con["office"],
        "district": con["district"],
        "scope": contest_scope(con),
        "office_does": sc.get("office_does"),
        "race_blurb": sc.get("race_blurb"),
        "uncontested": len(cands) == 1,
        "candidates": cands,
    })

out_measures = []
for m in measures_meta:
    ms = measures_scored[m["slug"]]
    out_measures.append({
        "slug": m["slug"],
        "jurisdiction": m["jurisdiction"],
        "proposition": m["proposition"],
        "title": m["title"],
        "scope": MEASURE_SCOPES[m["slug"]],
        "pamphlet_pages": pidx["measures"].get(m["slug"], []),
        "what_it_does": ms.get("what_it_does"),
        "cost_line": ms.get("cost_line"),
        "pro_summary": ms.get("pro_summary"),
        "con_summary": ms.get("con_summary"),
        "lean_mappings": ms.get("lean_mappings", {}),
    })

sha = subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True,
                     text=True, cwd=ROOT).stdout.strip() or "dev"

app_data = {
    "derived_from": ["data/interim/contests.json", "data/final/scores.json",
                     "data/final/measures.json", "data/final/rubric.json",
                     "data/final/interview.json", "data/dossiers/**"],
    "script": "pipeline/assemble_app_data.py",
    "data_version": sha,
    "election": {"name": "August 4, 2026 Primary and Special Election",
                 "day": "2026-08-04", "county": "King County, WA"},
    "rubric": {"scale": rubric["scale"], "axes": rubric["axes"]},
    "interview": interview,
    "contests": out_contests,
    "measures": out_measures,
}

payload = json.dumps(app_data, separators=(",", ":"))
(FINAL / "app-data.json").write_text(payload)
appdir = ROOT / "app/public/data"
appdir.mkdir(parents=True, exist_ok=True)
(appdir / "app-data.json").write_text(payload)

n_src = sum(len(c["sources"]) for con in out_contests for c in con["candidates"])
no_src = [f"{con['slug']}/{c['slug']}" for con in out_contests for c in con["candidates"] if not c["sources"]]
print(f"contests: {len(out_contests)}  measures: {len(out_measures)}  size: {len(payload)//1024}KB")
print(f"candidate sources parsed: {n_src}  candidates with zero sources: {len(no_src)}")
for x in no_src[:10]:
    print("  NO SOURCES:", x)
