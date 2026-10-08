"""Stage: QA. Audit dossier frontmatter for one or every research package.

Usage: python3 pipeline/verify_dossiers.py [<package> | --all] [--election <id>] [--check-photos]

Research plans are incremental work queues, so untouched contests/measures are
reported but do not fail the command. A started contest directory must contain
its overview and every planned candidate dossier.

A candidate dossier's optional Candidate Photo block (dossier_photo.py) is
checked offline on every run: url, page and kind present, both URLs https,
kind one of the four values, and no photo on a measure dossier or
_contest.md. ``--check-photos`` also fetches each url (HEAD, then GET) and
requires 200 with an image/* content type. The audit counts dossiers with
and without a photo (``photos: {present, missing}``) so the backfill can be
tracked per package.
"""

import argparse
import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

import dossier_photo
import election
from election import ROOT

PHOTO_USER_AGENT = "VoterLifeboat/1.0 (candidate photo check; pipeline/verify_dossiers.py)"


def frontmatter(path: Path):
    return dossier_photo.frontmatter(path.read_text())


def package_path(e: election.Election, name: str) -> Path:
    return e.state if name == "statewide" else e.county(name)


def photo_url_problem(url: str, timeout: int = 20):
    """None when ``url`` answers 200 with an image/* content type (HEAD,
    falling back to GET), else a short reason."""
    reason = "not fetched"
    for method in ("HEAD", "GET"):
        request = urllib.request.Request(url, method=method, headers={"User-Agent": PHOTO_USER_AGENT})
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                content_type = (response.headers.get("Content-Type") or "").split(";")[0].strip().lower()
                if response.status != 200:
                    reason = f"HTTP {response.status}"
                elif not content_type.startswith("image/"):
                    reason = f"content type {content_type or 'missing'}"
                else:
                    return None
        except urllib.error.HTTPError as error:
            reason = f"HTTP {error.code}"
        except (urllib.error.URLError, TimeoutError, OSError, ValueError) as error:
            reason = f"fetch failed: {getattr(error, 'reason', error)}"
    return reason


def audit_photo(audit, label: str, fm: str, check_photos: bool):
    """Count and check one candidate dossier's photo block."""
    block = dossier_photo.parse_photo_block(fm)
    if block is None:
        audit["photos"]["missing"] += 1
        return
    audit["photos"]["present"] += 1
    problems = dossier_photo.photo_problems(block)
    if not problems and check_photos:
        reason = photo_url_problem(block["url"])
        if reason:
            problems.append(f"photo.url {reason}")
    for problem in problems:
        audit["invalid_photos"].append(f"{label}: {problem}")


def audit_package(package: Path, check_photos: bool = False):
    plan_file = package / "interim/research-plan.json"
    if not plan_file.exists():
        raise SystemExit(f"no research plan for {package.name}: {plan_file}")
    plan = json.load(open(plan_file))
    dossiers = package / "dossiers"
    audit = {
        "script": "pipeline/verify_dossiers.py",
        "derived_from": [str(plan_file.relative_to(ROOT)), str(dossiers.relative_to(ROOT)) + "/"],
        "missing": [],
        "no_frontmatter": [],
        "invalid_evidence_levels": [],
        "invalid_source_formats": [],
        "evidence_levels": {},
        "contest_overviews_missing": [],
        "untouched_contests": [],
        "untouched_measures": [],
        "invalid_photos": [],
        "photos": {"present": 0, "missing": 0},
    }

    elsewhere = []
    for contest in plan.get("contests", []):
        slug = contest["contest_slug"]
        researched_in = (contest.get("shared") or {}).get("researched_in")
        if researched_in:
            # Researched once in another package (build_research_plan.py); its
            # dossiers are audited there, never copied here.
            elsewhere.append(f"{slug} -> {researched_in['package']}/{researched_in['contest_slug']}")
            if (dossiers / slug).exists():
                audit["missing"].append(f"{slug}: researched in {researched_in['package']}; remove this copy")
            continue
        contest_dir = dossiers / slug
        if not contest_dir.is_dir():
            audit["untouched_contests"].append(slug)
            continue
        overview = contest_dir / "_contest.md"
        if not overview.exists():
            audit["contest_overviews_missing"].append(slug)
        else:
            overview_fm = frontmatter(overview)
            if overview_fm and dossier_photo.has_photo_key(overview_fm):
                audit["invalid_photos"].append(f"{slug}/_contest: a contest overview never carries photo")
        for candidate in contest["candidates"]:
            path = contest_dir / f"{candidate['slug']}.md"
            if not path.exists():
                audit["missing"].append(f"{slug}/{candidate['slug']}")
                continue
            fm = frontmatter(path)
            if not fm:
                audit["no_frontmatter"].append(f"{slug}/{candidate['slug']}")
                continue
            if re.search(r"^sources:[ \t]+\S", fm, re.M) or re.search(r"^[ \t]*-[ \t]*\{[ \t]*id:", fm, re.M):
                audit["invalid_source_formats"].append(
                    f"{slug}/{candidate['slug']}: sources must use standard multiline '- id:' blocks"
                )
            if not re.search(r"^\s*-\s+id:\s*\S+", fm, re.M):
                audit["invalid_source_formats"].append(
                    f"{slug}/{candidate['slug']}: no parseable source ids"
                )
            level_match = re.search(r"^evidence_level:\s*(\S+)", fm, re.M)
            level = level_match.group(1) if level_match else "MISSING"
            audit["evidence_levels"][level] = audit["evidence_levels"].get(level, 0) + 1
            if level not in {"rich", "moderate", "pamphlet-only"}:
                audit["invalid_evidence_levels"].append(f"{slug}/{candidate['slug']}: {level}")
            audit_photo(audit, f"{slug}/{candidate['slug']}", fm, check_photos)

    measure_dir = dossiers / "measures"
    for measure in plan.get("measures", []):
        path = measure_dir / f"{measure['slug']}.md"
        if not measure_dir.is_dir():
            audit["untouched_measures"].append(measure["slug"])
        elif not path.exists():
            audit["missing"].append(f"measures/{measure['slug']}")
        elif not frontmatter(path):
            audit["no_frontmatter"].append(f"measures/{measure['slug']}")
        elif dossier_photo.has_photo_key(frontmatter(path)):
            audit["invalid_photos"].append(f"measures/{measure['slug']}: a measure dossier never carries photo")

    if elsewhere:
        audit["researched_elsewhere"] = elsewhere
    output = package / "interim/dossier-audit.json"
    output.write_text(json.dumps(audit, indent=2) + "\n")
    return audit


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("package", nargs="?", default="king", help="county id, statewide, or --all")
    parser.add_argument("--all", action="store_true", help="audit every package with a research plan")
    parser.add_argument("--check-photos", action="store_true",
                        help="also fetch every Candidate Photo url (200 + image/* required); default runs are offline")
    election.add_election_arg(parser)
    args = parser.parse_args()
    e = election.Election(args.election)
    packages = e.packages() if args.all else [package_path(e, args.package)]
    failed = False
    for package in packages:
        if not (package / "interim/research-plan.json").exists():
            continue
        audit = audit_package(package, check_photos=args.check_photos)
        hard_errors = (
            audit["missing"]
            + audit["no_frontmatter"]
            + audit["invalid_evidence_levels"]
            + audit["invalid_source_formats"]
            + audit["contest_overviews_missing"]
            + audit["invalid_photos"]
        )
        failed |= bool(hard_errors)
        print(
            f"{package.name}: errors={len(hard_errors)} started={sum(audit['evidence_levels'].values())} "
            f"untouched_contests={len(audit['untouched_contests'])} "
            f"researched_elsewhere={len(audit.get('researched_elsewhere', []))} evidence={audit['evidence_levels']} "
            f"photos={audit['photos']}"
        )
        for error in hard_errors:
            print("  E:", error)
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
