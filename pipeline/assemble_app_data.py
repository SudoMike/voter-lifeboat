"""Stage: final assembly. Merge package data into the single JSON the app ships.

Inputs:
  data/washington-state/counties/king/interim/{contests,measures,pamphlet-index}.json
  data/final/{scores,measures,rubric,interview}.json
  data/washington-state/{statewide,counties/king}/dossiers/**

Outputs:
  data/final/app-data.json
  app/public/data/app-data.json

Scope model:
  {"kind": "STATEWIDE"}
  {"kind": "COUNTY", "county": "king"}
  {"kind": "DISTRICT", "county": "king", "layer": "...", "value": "..."}
"""

import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WA = ROOT / "data/washington-state"
STATE = WA / "statewide"
KING = WA / "counties/king"
INTERIM = KING / "interim"
FINAL = ROOT / "data/final"
DOSSIER_DIRS = [STATE / "dossiers", KING / "dossiers"]
COUNTY_NAMES = {
    "clark": ("Clark County", "53011"),
    "king": ("King County", "53033"),
    "kitsap": ("Kitsap County", "53035"),
    "pierce": ("Pierce County", "53053"),
    "snohomish": ("Snohomish County", "53061"),
    "spokane": ("Spokane County", "53063"),
    "thurston": ("Thurston County", "53067"),
}

contests = json.load(open(INTERIM / "contests.json"))["contests"]
scores = {c["contest_slug"]: c for c in json.load(open(FINAL / "scores.json"))["contests"]}
measures_scored = {m["slug"]: m for m in json.load(open(FINAL / "measures.json"))["measures"]}
measures_meta = json.load(open(INTERIM / "measures.json"))["measures"]
pidx = json.load(open(INTERIM / "pamphlet-index.json"))
rubric = json.load(open(FINAL / "rubric.json"))
interview = json.load(open(FINAL / "interview.json"))

STATEWIDE_CATEGORIES = {"StateSupremeCourt"}


def parse_sources(contest_slug: str, cand_slug: str):
    """Parse the frontmatter sources list of a dossier into dicts."""
    f = next((d / contest_slug / f"{cand_slug}.md" for d in DOSSIER_DIRS if (d / contest_slug / f"{cand_slug}.md").exists()), None)
    if f is None:
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


def district_scope(layer: str, value: str):
    return {"kind": "DISTRICT", "county": "king", "layer": layer, "value": str(value)}


def contest_scope(con):
    cat, district, office = con["category"], con["district"], con["office"]
    if cat in STATEWIDE_CATEGORIES:
        return {"kind": "STATEWIDE"}
    if cat == "Federal":
        n = re.search(r"Congressional District (\d+)", district).group(1)
        return district_scope("CONGDST", n)
    if cat == "State":
        n = re.search(r"Legislative District No\.\s*(\d+)", office + " " + district)
        return district_scope("LEGDST", n.group(1))
    if cat == "County":
        m = re.search(r"Council District No\.\s*(\d+)", district)
        return district_scope("KCCDST", m.group(1)) if m else {"kind": "COUNTY", "county": "king"}
    if cat == "DistrictCourt":
        return district_scope("JUDDST", "NE")
    if cat == "City":
        m = re.search(r"Council District No\.\s*(\d+)", district)
        if m:
            return district_scope("SCCDST", f"SCC{m.group(1)}")
        return district_scope("CITY", "Seattle")
    raise ValueError(f"no scope rule for {con['slug']}")


MEASURE_SCOPES = {
    "city-of-black-diamond-proposition-no-1": district_scope("CITY", "Black Diamond"),
    "city-of-covington-proposition-no-1": district_scope("CITY", "Covington"),
    "city-of-seattle-proposition-no-1": district_scope("CITY", "Seattle"),
    "skykomish-school-district-no-404-proposition-no-1": district_scope("SCHDST", "404"),
    "king-county-fire-protection-district-no-43-proposition-no-1": district_scope("FIRDST", "43"),
    "king-county-fire-protection-district-no-47-proposition-no-1": district_scope("FIRDST", "47"),
    "snoqualmie-pass-fire-and-rescue-proposition-no-1": district_scope("FIRDST", "51"),
}

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
    owner = "statewide" if con["category"] in STATEWIDE_CATEGORIES else "king"
    out_contests.append({
        "slug": con["slug"],
        "owner": owner,
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
        "owner": "king",
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

supported_counties = [{"id": "king", "name": "King County", "state": "WA", "fips": "53033"}]
for county_dir in sorted((WA / "counties").iterdir()):
    if county_dir.name == "king" or not county_dir.is_dir():
        continue
    cfile = county_dir / "interim/app-contests.json"
    mfile = county_dir / "interim/app-measures.json"
    if cfile.exists():
        pack = json.load(open(cfile))
        out_contests.extend(pack.get("contests", []))
    if mfile.exists():
        pack = json.load(open(mfile))
        out_measures.extend(pack.get("measures", []))
    if cfile.exists() or mfile.exists():
        name, fips = COUNTY_NAMES.get(county_dir.name, (county_dir.name.title(), None))
        supported_counties.append({"id": county_dir.name, "name": name, "state": "WA", "fips": fips})

contest_slugs = [c["slug"] for c in out_contests]
measure_slugs = [m["slug"] for m in out_measures]
duplicate_contests = sorted({s for s in contest_slugs if contest_slugs.count(s) > 1})
duplicate_measures = sorted({s for s in measure_slugs if measure_slugs.count(s) > 1})
if duplicate_contests or duplicate_measures:
    raise SystemExit(f"duplicate app slugs: contests={duplicate_contests} measures={duplicate_measures}")

sha = subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True,
                     text=True, cwd=ROOT).stdout.strip() or "dev"

app_data = {
    "derived_from": [
        "data/washington-state/statewide/**",
        "data/washington-state/counties/king/**",
        "data/washington-state/counties/*/interim/app-*.json",
        "data/final/scores.json",
        "data/final/measures.json",
        "data/final/rubric.json",
        "data/final/interview.json",
    ],
    "script": "pipeline/assemble_app_data.py",
    "data_version": sha,
    "election": {
        "id": "2026-08-04-primary-special",
        "name": "August 4, 2026 Primary and Special Election",
        "day": "2026-08-04",
        "scope": "Washington State",
    },
    "coverage": {
        "statewide_complete": True,
        "supported_counties": supported_counties,
    },
    "rubric": {"scale": rubric["scale"], "axes": rubric["axes"]},
    "interview": interview,
    "contests": out_contests,
    "measures": out_measures,
}

payload = json.dumps(app_data, separators=(",", ":"))
FINAL.mkdir(exist_ok=True)
(FINAL / "app-data.json").write_text(payload)
appdir = ROOT / "app/public/data"
appdir.mkdir(parents=True, exist_ok=True)
(appdir / "app-data.json").write_text(payload)

n_src = sum(len(c["sources"]) for con in out_contests for c in con["candidates"])
no_src = [
    f"{con['slug']}/{c['slug']}"
    for con in out_contests
    for c in con["candidates"]
    if not c["sources"] and c.get("evidence_level") != "official-ballot-only"
]
print(f"contests: {len(out_contests)}  measures: {len(out_measures)}  size: {len(payload)//1024}KB")
print(f"candidate sources parsed: {n_src}  dossier candidates with zero sources: {len(no_src)}")
for x in no_src[:10]:
    print("  NO SOURCES:", x)
