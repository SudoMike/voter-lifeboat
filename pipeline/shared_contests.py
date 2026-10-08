"""One race listed by more than one package (#20).

From the general on, congressional and legislative contests are county-owned
(ADR-0004), so a district that crosses a county line is listed by every
county package it touches: Legislative District 31 by King and Pierce,
Congressional District 8 by King, Pierce and Snohomish (and Chelan, Douglas,
Kittitas). The same holds for a few local races, such as King County
District Court's Southeast Electoral District, which is also on the ballot
in Pierce-side Auburn. Each race is researched and scored once, in the first
package that did it; every other package reuses that scoring and those
dossiers, and never edits them in place.

contest_key() identifies the race across packages, whatever each source
calls it ("U.S. Representative" / "United States Representative", "State
Representative Pos. 1" / "State Representative Position No. 1"):

  ("CONGDST", n)                          congressional
  ("LEGDST", n, "senator" | "representative-position-1|2")
  ("NAMED", <district>, <office>)         anything else, by normalized text,
                                          only when the district names its
                                          jurisdiction (a bare office such as
                                          "Assessor" is never shared)

researched_index() maps each key to the package and scoring file that hold
the race's research, so build_research_plan.py can say what is already done
and assemble_app_data.py can ship it from the owning package.
"""

import json
import re

FEDERAL_RE = re.compile(r"Congressional District\s*(?:No\.\s*)?(\d+)", re.I)
LEGISLATIVE_RE = re.compile(r"Legislative District\s*(?:No\.\s*)?(\d+)", re.I)


def _norm(text: str) -> str:
    t = text.lower().replace("&", " and ")
    t = re.sub(r"\bpos\.?(?=\s|\d|$)", "position", t)
    t = re.sub(r"\b(?:no\.|number|#)\s*", " ", t)
    t = re.sub(r"\b0+(\d)", r"\1", t)
    return re.sub(r"[^a-z0-9]+", " ", t).strip()


def contest_key(contest: dict):
    office, district = contest.get("office") or "", contest.get("district") or ""
    blob = f"{office} {district}"
    category = contest.get("category")
    if category == "Federal":
        m = FEDERAL_RE.search(blob)
        return ("CONGDST", int(m.group(1))) if m else None
    if category == "State":
        m = LEGISLATIVE_RE.search(blob)
        if not m:
            return None
        seat_text = LEGISLATIVE_RE.sub(" ", blob)
        if re.search(r"senat", seat_text, re.I):
            return ("LEGDST", int(m.group(1)), "senator")
        p = re.search(r"pos(?:ition)?\.?\s*(?:no\.?\s*)?([12])\b", seat_text, re.I)
        return ("LEGDST", int(m.group(1)), f"representative-position-{p.group(1)}") if p else None
    if not district.strip() or category in ("StateSupremeCourt",):
        return None
    return ("NAMED", _norm(district), _norm(office))


def package_contests(package_dir) -> list[dict]:
    """A package's contests: interim/contests.json (King's schema 2, the
    statewide package, or the normalizer's output for an app-* county)."""
    path = package_dir / "interim/contests.json"
    if not path.exists():
        return []
    return json.loads(path.read_text())["contests"]


def researched_index(package_dirs) -> dict:
    """{key: {"package", "contest_slug", "scoring"}} for every contest that
    has a scoring file, first package wins (pass the owning packages first)."""
    index = {}
    for pkg in package_dirs:
        for contest in package_contests(pkg):
            key = contest_key(contest)
            if key is None or key in index:
                continue
            scoring = pkg / "scoring" / f"{contest['slug']}.json"
            if scoring.exists():
                scored = json.loads(scoring.read_text())
                index[key] = {"package": pkg.name, "contest_slug": contest["slug"], "scoring": scoring,
                              "candidates": [c["slug"] for c in scored.get("candidates", [])]}
    return index


def listing_index(package_dirs) -> dict:
    """{key: [package names that list the contest]} across packages."""
    found = {}
    for pkg in package_dirs:
        for contest in package_contests(pkg):
            key = contest_key(contest)
            if key is not None and pkg.name not in found.setdefault(key, []):
                found[key].append(pkg.name)
    return found
