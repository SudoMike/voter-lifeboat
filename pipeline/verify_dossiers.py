"""Stage: QA. Audit dossier frontmatter for one or every research package.

Research plans are incremental work queues, so untouched contests/measures are
reported but do not fail the command. A started contest directory must contain
its overview and every planned candidate dossier.
"""

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WA = ROOT / "data/washington-state"
STATE = WA / "statewide"
COUNTIES = WA / "counties"


def frontmatter(path: Path):
    match = re.match(r"^---\n(.*?)\n---", path.read_text(), re.S)
    return match.group(1) if match else None


def package_path(name: str) -> Path:
    return STATE if name == "statewide" else COUNTIES / name


def audit_package(package: Path):
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
    }

    for contest in plan.get("contests", []):
        slug = contest["contest_slug"]
        contest_dir = dossiers / slug
        if not contest_dir.is_dir():
            audit["untouched_contests"].append(slug)
            continue
        if not (contest_dir / "_contest.md").exists():
            audit["contest_overviews_missing"].append(slug)
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

    measure_dir = dossiers / "measures"
    for measure in plan.get("measures", []):
        path = measure_dir / f"{measure['slug']}.md"
        if not measure_dir.is_dir():
            audit["untouched_measures"].append(measure["slug"])
        elif not path.exists():
            audit["missing"].append(f"measures/{measure['slug']}")
        elif not frontmatter(path):
            audit["no_frontmatter"].append(f"measures/{measure['slug']}")

    output = package / "interim/dossier-audit.json"
    output.write_text(json.dumps(audit, indent=2) + "\n")
    return audit


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("package", nargs="?", default="king", help="county id, statewide, or --all")
    parser.add_argument("--all", action="store_true", help="audit every package with a research plan")
    args = parser.parse_args()
    packages = [STATE] + sorted(path for path in COUNTIES.iterdir() if path.is_dir()) if args.all else [package_path(args.package)]
    failed = False
    for package in packages:
        if not (package / "interim/research-plan.json").exists():
            continue
        audit = audit_package(package)
        hard_errors = (
            audit["missing"]
            + audit["no_frontmatter"]
            + audit["invalid_evidence_levels"]
            + audit["invalid_source_formats"]
            + audit["contest_overviews_missing"]
        )
        failed |= bool(hard_errors)
        print(
            f"{package.name}: errors={len(hard_errors)} started={sum(audit['evidence_levels'].values())} "
            f"untouched_contests={len(audit['untouched_contests'])} evidence={audit['evidence_levels']}"
        )
        for error in hard_errors:
            print("  E:", error)
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
