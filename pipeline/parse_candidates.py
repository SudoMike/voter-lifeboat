"""Stage: raw -> interim. Parse official candidate CSVs and the eid=54 contest pages.

Inputs:
  data/washington-state/counties/king/raw/kce/2026-primary-candidates.csv
  data/washington-state/counties/king/raw/kce/2026-candidates.csv
  data/washington-state/counties/king/raw/kce/candidates-eid54.html
  data/washington-state/counties/king/raw/kce/ballotmeasures-eid54.html

Outputs:
  data/washington-state/counties/king/interim/contests.json
  data/washington-state/counties/king/interim/measures.json

Every output record carries `derived_from` pointing at its raw sources.
"""

import csv
import json
import re
from html import unescape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KING = ROOT / "data/washington-state/counties/king"
RAW = KING / "raw/kce"
OUT = KING / "interim"
OUT.mkdir(parents=True, exist_ok=True)


def slugify(s: str) -> str:
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", s.lower())).strip("-")


# --- 1. eid=54 HTML: contest structure with official ids -------------------

html = (RAW / "candidates-eid54.html").read_text()

contests = []
for cat_m in re.finditer(
    r'<div class="list-group pull-left candidate-list-group" id="(\w+)">(.*?)(?=<div class="list-group pull-left candidate-list-group"|\Z)',
    html, re.S,
):
    category, block = cat_m.group(1), cat_m.group(2)
    for item in re.split(r'<div class="list-group-item candidatelist-div">', block)[1:]:
        head_m = re.search(
            r'<span class="sp-bt-title-1">(.*?)</span>(?:<span class="sp-bt-title-2">(.*?)</span>)?\s*</h5>',
            item, re.S,
        )
        list_m = re.search(r'<ul class="ul-candidatelist">(.*?)</ul>', item, re.S)
        if not head_m or not list_m:
            continue
        office = unescape(re.sub(r"<[^>]+>", "", head_m.group(1))).strip()
        district = unescape(re.sub(r"<[^>]+>", "", head_m.group(2) or "")).strip().lstrip(", ").strip()
        cands = []
        for c_m in re.finditer(
            r'href="candidates\.aspx\?cid=(\d+)&amp;candidateid=(\d+)[^"]*"[^>]*>'
            r'<span class="ballotname"[^>]*>(.*?)</span></a>'
            r'(?:<span class="small candidateparty party">\s*(.*?)</span>)?',
            list_m.group(1), re.S,
        ):
            name = unescape(re.sub(r"<[^>]+>", "", c_m.group(3))).strip()
            party = unescape((c_m.group(4) or "").strip()).strip("() ")
            cands.append({
                "kce_candidate_id": c_m.group(2),
                "name": name,
                "party_preference": party or None,
                "slug": slugify(name),
            })
        if cands:
            cid_m = re.search(r"cid=(\d+)", list_m.group(1))
            contests.append({
                "kce_contest_id": cid_m.group(1) if cid_m else None,
                "category": category,
                "office": office,
                "district": district,
                "slug": slugify(f"{district}-{office}") if district else slugify(office),
                "candidates": cands,
            })

# --- 2. primary CSV: ballot order + campaign contact ------------------------

with open(RAW / "2026-primary-candidates.csv", encoding="utf-8-sig") as f:
    primary_rows = list(csv.DictReader(f))

# index CSV rows by (normalized name) for merge
def norm(s):
    return re.sub(r"[^a-z]", "", s.lower())

csv_by_name = {}
for r in primary_rows:
    csv_by_name.setdefault(norm(r["Candidate"]), []).append(r)

unmatched_csv = {norm(r["Candidate"]) for r in primary_rows}
for con in contests:
    for c in con["candidates"]:
        rows = csv_by_name.get(norm(c["name"]), [])
        # disambiguate same-name filings by jurisdiction match
        row = None
        if len(rows) == 1:
            row = rows[0]
        elif len(rows) > 1:
            for r in rows:
                if slugify(r["Jurisdiction Name"]) in con["slug"] or slugify(con["district"]) in slugify(r["Jurisdiction Name"]):
                    row = r
                    break
        if row:
            unmatched_csv.discard(norm(c["name"]))
            c["ballot_order"] = int(row["Ballot Order"]) if row["Ballot Order"].isdigit() else None
            c["campaign_website"] = row["Campaign Website"] or None
            c["campaign_email"] = row["Campaign Email"] or None
            c["csv_jurisdiction"] = row["Jurisdiction Name"]

# --- 3. measures HTML --------------------------------------------------------

mh = (RAW / "ballotmeasures-eid54.html").read_text()
measures = []
m_body = re.search(r"PRIMARY 2026(.*?)Back to top\s*</a>\s*</div>\s*</div>\s*<[^>]*>\s*54", mh, re.S)
m_text = re.sub(r"<script.*?</script>", "", mh, flags=re.S)
m_text = re.sub(r"<[^>]+>", "\n", m_text)
m_lines = [l.strip() for l in unescape(m_text).split("\n") if l.strip()]
start = m_lines.index("PRIMARY 2026")
jurisdiction = None
i = start
while i < len(m_lines) - 1:
    line = m_lines[i]
    if re.match(r"^Proposition No\. \d+$", line) or line == "Intent to Continue Voter Authorized Benefit Charge":
        # jurisdiction is the previous non-navigation line; title the next line
        prop = line if line.startswith("Proposition") else "Proposition No. 1"
        title = line if not line.startswith("Proposition") else m_lines[i + 1]
        if line == "Intent to Continue Voter Authorized Benefit Charge":
            title = line
            i += 1  # following line is "Proposition No. 1"
        measures.append({
            "jurisdiction": jurisdiction,
            "proposition": prop,
            "title": title,
            "slug": slugify(f"{jurisdiction}-{prop}"),
        })
        i += 2
        continue
    if line not in ("Back to top", "City", "School", "Special Purpose District", "Official list",
                    "Select a district...") and not line.startswith("PRIMARY"):
        jurisdiction = line
    i += 1

out = {
    "derived_from": [
        "data/washington-state/counties/king/raw/kce/candidates-eid54.html",
        "data/washington-state/counties/king/raw/kce/2026-primary-candidates.csv",
    ],
    "script": "pipeline/parse_candidates.py",
    "election": {"name": "August 4, 2026 Primary and Special Election", "kce_eid": 54},
    "contests": contests,
}
(OUT / "contests.json").write_text(json.dumps(out, indent=2))

mout = {
    "derived_from": ["data/washington-state/counties/king/raw/kce/ballotmeasures-eid54.html"],
    "script": "pipeline/parse_candidates.py",
    "measures": measures,
}
(OUT / "measures.json").write_text(json.dumps(mout, indent=2))

n_c = sum(len(c["candidates"]) for c in contests)
n_matched = sum(1 for con in contests for c in con["candidates"] if "ballot_order" in c)
print(f"contests: {len(contests)}  candidates: {n_c}  csv-matched: {n_matched}")
print(f"measures: {len(measures)}")
if unmatched_csv:
    print("CSV rows not matched to a contest candidate:", len(unmatched_csv))
for con in contests:
    print(f"  [{con['category']}] {con['office']} — {con['district']} ({len(con['candidates'])})")
