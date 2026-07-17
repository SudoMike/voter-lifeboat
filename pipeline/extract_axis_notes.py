"""Stage: dossiers -> interim. Collect every contest's differentiating-axes
section and every measure's axis notes into one file for rubric synthesis.

Input:  data/washington-state/counties/king/dossiers/*/_contest.md,
        data/washington-state/counties/king/dossiers/measures/*.md
Output: data/washington-state/counties/king/interim/axis-notes.md
"""

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STATE = ROOT / "data/washington-state/statewide"
KING = ROOT / "data/washington-state/counties/king"
DOSS_DIRS = [STATE / "dossiers", KING / "dossiers"]
plan = json.load(open(KING / "interim/research-plan.json"))
depth = {c["contest_slug"]: c["depth"] for c in plan["contests"]}

out = ["# Axis notes extracted from all contest overviews and measures",
       "", "Derived from: data/washington-state/{statewide,counties/king}/dossiers/*/_contest.md and data/washington-state/counties/king/dossiers/measures/*.md",
       "by pipeline/extract_axis_notes.py. Input to rubric design.", ""]

def grab_axes(text: str) -> str | None:
    # take the section whose heading mentions axes/differentiat, up to next heading
    m = re.search(r"^(#{2,3}[^\n]*(?:ax[ei]s|axis|differentiat)[^\n]*)\n(.*?)(?=\n#{1,3} |\Z)",
                  text, re.S | re.M | re.I)
    return (m.group(2).strip() if m else None)

for doss in DOSS_DIRS:
    for cdir in sorted(doss.iterdir()):
        if not cdir.is_dir() or cdir.name == "measures":
            continue
        f = cdir / "_contest.md"
        if not f.exists():
            continue
        text = f.read_text()
        section = grab_axes(text)
        if section is None:
            # no axes heading (e.g., uncontested race): fall back to the whole body
            section = re.sub(r"^---\n.*?\n---\n", "", text, flags=re.S)
            section = re.sub(r"^# [^\n]*\n", "", section).strip()
            section = f"_(no axes section; full overview follows)_\n{section}"
        out.append(f"## {cdir.name}  (depth: {depth.get(cdir.name, '?')})")
        out.append(section)
        out.append("")

out.append("# Measures")
for f in sorted((KING / "dossiers/measures").glob("*.md")):
    section = grab_axes(f.read_text())
    out.append(f"## {f.stem}")
    out.append(section if section else "_no axis notes found — check manually_")
    out.append("")

(KING / "interim/axis-notes.md").write_text("\n".join(out))
n_missing = sum(1 for line in out if line.startswith("_no ax"))
print(f"wrote {KING / 'interim/axis-notes.md'} ({len(out)} lines, {n_missing} sections missing)")
