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
DOSSIER_DIRS = [STATE / "dossiers", KING / "dossiers"] + sorted(
    p / "dossiers" for p in (WA / "counties").iterdir()
    if p.is_dir() and p.name != "king"
)
COUNTY_NAMES = {
    "adams": ("Adams County", "53001"),
    "asotin": ("Asotin County", "53003"),
    "benton": ("Benton County", "53005"),
    "chelan": ("Chelan County", "53007"),
    "clallam": ("Clallam County", "53009"),
    "clark": ("Clark County", "53011"),
    "columbia": ("Columbia County", "53013"),
    "cowlitz": ("Cowlitz County", "53015"),
    "douglas": ("Douglas County", "53017"),
    "ferry": ("Ferry County", "53019"),
    "franklin": ("Franklin County", "53021"),
    "garfield": ("Garfield County", "53023"),
    "grant": ("Grant County", "53025"),
    "grays-harbor": ("Grays Harbor County", "53027"),
    "island": ("Island County", "53029"),
    "jefferson": ("Jefferson County", "53031"),
    "king": ("King County", "53033"),
    "kitsap": ("Kitsap County", "53035"),
    "kittitas": ("Kittitas County", "53037"),
    "klickitat": ("Klickitat County", "53039"),
    "lewis": ("Lewis County", "53041"),
    "lincoln": ("Lincoln County", "53043"),
    "mason": ("Mason County", "53045"),
    "okanogan": ("Okanogan County", "53047"),
    "pacific": ("Pacific County", "53049"),
    "pend-oreille": ("Pend Oreille County", "53051"),
    "pierce": ("Pierce County", "53053"),
    "san-juan": ("San Juan County", "53055"),
    "skagit": ("Skagit County", "53057"),
    "skamania": ("Skamania County", "53059"),
    "snohomish": ("Snohomish County", "53061"),
    "spokane": ("Spokane County", "53063"),
    "stevens": ("Stevens County", "53065"),
    "thurston": ("Thurston County", "53067"),
    "wahkiakum": ("Wahkiakum County", "53069"),
    "walla-walla": ("Walla Walla County", "53071"),
    "whatcom": ("Whatcom County", "53073"),
    "whitman": ("Whitman County", "53075"),
    "yakima": ("Yakima County", "53077"),
}

contests = json.load(open(INTERIM / "contests.json"))["contests"]
scores = {c["contest_slug"]: c for c in json.load(open(FINAL / "scores.json"))["contests"]}
measures_scored = {m["slug"]: m for m in json.load(open(FINAL / "measures.json"))["measures"]}
measures_meta = json.load(open(INTERIM / "measures.json"))["measures"]
pidx = json.load(open(INTERIM / "pamphlet-index.json"))
rubric = json.load(open(FINAL / "rubric.json"))
interview = json.load(open(FINAL / "interview.json"))

STATEWIDE_CATEGORIES = {"StateSupremeCourt"}
SHARED_CATEGORIES = {"Federal", "State"}


def shared_contest_key(contest):
    """Canonicalize harmless ballot-source abbreviations for shared races."""
    office = contest["office"].lower().replace("pos.", "position").replace("pos ", "position ")
    office = re.sub(r"\s+", " ", office).strip()
    district = re.sub(r"\s+", " ", contest["district"]).strip().lower()
    return contest["category"], district, office


def apply_scoring(contest, scored, dossier_slug=None):
    """Overlay research fields without disturbing county ballot metadata."""
    if not scored:
        return contest
    scored_by_slug = {c["slug"]: c for c in scored.get("candidates", [])}
    for candidate in contest.get("candidates", []):
        score = scored_by_slug.get(candidate["slug"])
        if not score:
            continue
        for field, default in (
            ("evidence_level", None), ("withdrawn", False), ("summary", None),
            ("highlights", []), ("scores", {}),
        ):
            candidate[field] = score.get(field, default)
        candidate["sources"] = parse_sources(
            dossier_slug or scored["contest_slug"], candidate["slug"]
        )
    contest["office_does"] = scored.get("office_does")
    contest["race_blurb"] = scored.get("race_blurb")
    return contest


def apply_measure_scoring(measure, scored):
    """Overlay researched measure display and lean fields on ballot metadata."""
    if not scored:
        return measure
    for field, default in (
        ("what_it_does", None), ("cost_line", None), ("pro_summary", None),
        ("con_summary", None), ("lean_mappings", {}),
    ):
        measure[field] = scored.get(field, default)
    return measure


def shared_score_index(all_scores):
    """Index shared federal/state scoring via normalized statewide contests."""
    normalized = STATE / "interim/contests.json"
    if not normalized.exists():
        return {}
    by_slug = {c["contest_slug"]: c for c in all_scores.values()}
    result = {}
    for contest in json.load(open(normalized)).get("contests", []):
        if contest.get("category") not in SHARED_CATEGORIES:
            continue
        scored = by_slug.get(contest["slug"])
        if scored:
            key = shared_contest_key(contest)
            result[key] = (scored, contest["slug"])
    return result


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

supported_counties = [{"id": "king", "name": "King County", "state": "WA", "fips": "53033", "coverage": "full_county"}]
shared_scores = shared_score_index(scores)
for county_dir in sorted((WA / "counties").iterdir()):
    if county_dir.name == "king" or not county_dir.is_dir():
        continue
    cfile = county_dir / "interim/app-contests.json"
    mfile = county_dir / "interim/app-measures.json"
    package_coverages = []
    if cfile.exists():
        pack = json.load(open(cfile))
        package_coverages.append(pack.get("coverage", "partial_county"))
        for contest in pack.get("contests", []):
            scored = scores.get(contest["slug"])
            dossier_slug = contest["slug"]
            if contest.get("category") in SHARED_CATEGORIES:
                shared = shared_scores.get(shared_contest_key(contest))
                if shared:
                    scored, dossier_slug = shared
            out_contests.append(apply_scoring(contest, scored, dossier_slug))
    if mfile.exists():
        pack = json.load(open(mfile))
        package_coverages.append(pack.get("coverage", "partial_county"))
        for measure in pack.get("measures", []):
            out_measures.append(apply_measure_scoring(
                measure, measures_scored.get(measure["slug"])
            ))
    if cfile.exists() or mfile.exists():
        name, fips = COUNTY_NAMES.get(county_dir.name, (county_dir.name.title(), None))
        coverage = "full_county" if package_coverages and all(c == "full_county" for c in package_coverages) else "partial_county"
        supported_counties.append({"id": county_dir.name, "name": name, "state": "WA", "fips": fips, "coverage": coverage})

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
