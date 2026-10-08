"""Stage: raw -> interim. Parse King County Elections (KCE) contest and measure pages.

Usage: python3 pipeline/parse_candidates.py [--election <id>]

Which raw files are read comes from ``election.KCE_SOURCES[<id>]`` (KCE's
election id, the candidate/measure list pages, the candidate CSV). Inputs
(K = data/washington-state/elections/<id>/counties/king):
  K/raw/kce/<candidates_html>          contest structure with KCE ids
  K/raw/kce/<candidates_csv>           campaign website/email (+ ballot order)
  K/raw/kce/<measures_html>            measure list
  K/raw/kce/measures/*.html            measure detail pages (schema 2)
  K/raw/votewa/*.json                  VoteWA measure JSON (schema 2)

Outputs:
  K/interim/contests.json
  K/interim/measures.json

Schema 1 (the primary) is frozen: its outputs must not change. Schema 2 adds
per-contest ``owner``/``scope``/``uncontested`` hints and per-measure ballot
title, explanatory statement, pro/con statements and ``scope``, so assembly
can scope King contests without hand-written rules. Scopes use the
assemble_app_data.py model ({"kind": "STATEWIDE"}, {"kind": "COUNTY", ...},
{"kind": "DISTRICT", "county": "king", "layer": ..., "value": ...}).

Every output record carries ``derived_from`` pointing at its raw sources.
"""

import csv
import json
import re
from html import unescape

import election
from election import rel


def slugify(s: str) -> str:
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", s.lower())).strip("-")


def norm(s):
    return re.sub(r"[^a-z]", "", s.lower())


def strip_tags(s: str) -> str:
    return unescape(re.sub(r"<[^>]+>", "", s))


# --- contest list (candidates.aspx?eid=N) -----------------------------------

# KCE group ids are mostly CamelCase words; the Court of Appeals group id
# carries its whole district ("CourtofAppeals,Division1,District1") and its
# contests have no district line, only "Judge Position No. N".
CATEGORY_ALIASES = {
    "CourtofAppeals,Division1,District1": ("CourtOfAppeals", "Court of Appeals, Division 1, District 1"),
}


def parse_contest_list(html: str) -> list[dict]:
    contests = []
    for cat_m in re.finditer(
        r'<div class="list-group pull-left candidate-list-group" id="([^"]+)">(.*?)(?=<div class="list-group pull-left candidate-list-group"|\Z)',
        html, re.S,
    ):
        category, block = cat_m.group(1), cat_m.group(2)
        category, default_district = CATEGORY_ALIASES.get(category, (category, ""))
        for item in re.split(r'<div class="list-group-item candidatelist-div">', block)[1:]:
            head_m = re.search(
                r'<span class="sp-bt-title-1">(.*?)</span>(?:<span class="sp-bt-title-2">(.*?)</span>)?\s*</h5>',
                item, re.S,
            )
            list_m = re.search(r'<ul class="ul-candidatelist">(.*?)</ul>', item, re.S)
            if not head_m or not list_m:
                continue
            office = strip_tags(head_m.group(1)).strip()
            district = strip_tags(head_m.group(2) or "").strip().lstrip(", ").strip() or default_district
            cands = []
            for c_m in re.finditer(
                r'href="candidates\.aspx\?cid=(\d+)&amp;candidateid=(\d+)[^"]*"[^>]*>'
                r'<span class="ballotname"[^>]*>(.*?)</span></a>'
                r'(?:<span class="small candidateparty party">\s*(.*?)</span>)?',
                list_m.group(1), re.S,
            ):
                name = strip_tags(c_m.group(3)).strip()
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
    return contests


def merge_csv(contests: list[dict], rows: list[dict], ballot_order_from_csv: bool) -> set:
    """Attach CSV contact fields to candidates; return unmatched CSV names."""
    csv_by_name = {}
    for r in rows:
        csv_by_name.setdefault(norm(r["Candidate"]), []).append(r)
    unmatched_csv = {norm(r["Candidate"]) for r in rows}
    for con in contests:
        for position, c in enumerate(con["candidates"], start=1):
            matches = csv_by_name.get(norm(c["name"]), [])
            # disambiguate same-name filings by jurisdiction match
            row = None
            if len(matches) == 1:
                row = matches[0]
            elif len(matches) > 1:
                for r in matches:
                    if slugify(r["Jurisdiction Name"]) in con["slug"] or slugify(con["district"]) in slugify(r["Jurisdiction Name"]):
                        row = r
                        break
            if not ballot_order_from_csv:
                c["ballot_order"] = position
            if row:
                unmatched_csv.discard(norm(c["name"]))
                if ballot_order_from_csv:
                    c["ballot_order"] = int(row["Ballot Order"]) if row["Ballot Order"].isdigit() else None
                c["campaign_website"] = row["Campaign Website"] or None
                c["campaign_email"] = row["Campaign Email"] or None
                c["csv_jurisdiction"] = row["Jurisdiction Name"]
    return unmatched_csv


# --- scope hints (schema 2) -------------------------------------------------

STATEWIDE_CATEGORIES = {"StateSupremeCourt"}
COUNTY = {"kind": "COUNTY", "county": "king"}
JUDDST_CODES = {"Northeast": "NE", "Southeast": "SE", "Southwest": "SW", "West": "W", "Shoreline": "SH"}


def district_scope(layer: str, value) -> dict:
    return {"kind": "DISTRICT", "county": "king", "layer": layer, "value": str(value)}


def contest_owner(con: dict) -> str:
    """Statewide Contests belong to the statewide package; assembly dedupes them."""
    return "statewide" if con["category"] in STATEWIDE_CATEGORIES else "king"


def contest_scope(con: dict) -> dict:
    cat, district, office = con["category"], con["district"], con["office"]
    if cat in STATEWIDE_CATEGORIES:
        return {"kind": "STATEWIDE"}
    if cat == "Federal":
        return district_scope("CONGDST", re.search(r"Congressional District (\d+)", district).group(1))
    if cat == "State":
        return district_scope("LEGDST", re.search(r"Legislative District No\.\s*(\d+)", f"{office} {district}").group(1))
    if cat == "County":
        m = re.search(r"Council District No\.\s*(\d+)", district)
        return district_scope("KCCDST", m.group(1)) if m else dict(COUNTY)
    if cat == "CourtOfAppeals":
        # Division 1, District 1 is exactly King County (RCW 2.06.020).
        return dict(COUNTY)
    if cat == "DistrictCourt":
        m = re.match(r"(\w+) Electoral District$", office)
        return district_scope("JUDDST", JUDDST_CODES[m.group(1)])
    if cat == "City" and office == "City of Seattle":
        m = re.search(r"Council District No\.\s*(\d+)", district)
        return district_scope("SCCDST", f"SCC{m.group(1)}") if m else district_scope("CITY", "Seattle")
    raise ValueError(f"no scope rule for {con['slug']}")


# King has no CEMDST layer in its District Adapter; WA DOR tax-district layer 3
# has exactly one King cemetery district, DISTATTRIB "1" (raw/gis/dor-cemdst-king.json).
UNRESOLVED_LAYERS = {
    "CEMDST": "King's District Adapter (app/src/lib/geo.js KING_LAYERS) has no CEMDST layer; "
              "WA DOR tax-district layer 3 has King feature DISTATTRIB=1 (raw/gis/dor-cemdst-king.json).",
}


def measure_scope(jurisdiction: str) -> dict:
    if m := re.fullmatch(r"City of (.+)", jurisdiction):
        return district_scope("CITY", m.group(1))
    if m := re.fullmatch(r".+ School District No\. (\d+)", jurisdiction):
        return district_scope("SCHDST", m.group(1))
    if m := re.fullmatch(r"King County Fire Protection District No\. (\d+)", jurisdiction):
        return district_scope("FIRDST", m.group(1))
    if m := re.fullmatch(r"King County Cemetery District No\. (\d+)", jurisdiction):
        return district_scope("CEMDST", m.group(1))
    raise ValueError(f"no scope rule for measure jurisdiction {jurisdiction!r}")


# --- measure list ------------------------------------------------------------

def parse_measure_list_legacy(mh: str) -> list[dict]:
    """Schema 1 (eid=54) text walk; frozen so the primary's output never changes."""
    measures = []
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
    return measures


def parse_measure_list(html: str) -> list[dict]:
    """Every measure link on ballotmeasures.aspx?eid=N, State Measures included."""
    out = []
    for a in re.finditer(
        r'<a class="list-group-item[^"]*" href="([^"]+)"[^>]*><p class="ballotmeasure-name"><span><span>(.*?)</span></span></p></a>',
        html, re.S,
    ):
        href = unescape(a.group(1))
        parts = [strip_tags(p).strip() for p in re.split(r"<br\s*/?>", a.group(2))]
        cid = re.search(r"[?&]cid=(\d+)", href)
        group = re.search(r"[?&]groupname=(\w+)", href)
        out.append({
            "jurisdiction": parts[0],
            "proposition": parts[1],
            "title": parts[2] if len(parts) > 2 else None,
            "href": href,
            "kce_contest_id": cid.group(1) if cid else None,
            "kce_group": group.group(1) if group else None,
        })
    return out


# --- measure details (schema 2) ---------------------------------------------

def html_to_text(fragment: str) -> str:
    """Paragraph-preserving plain text: </p> -> blank line, <br> -> newline."""
    t = re.sub(r"\s+", " ", fragment)  # source newlines are spaces in HTML
    t = re.sub(r"<br\s*/?>", "\n", t)
    t = re.sub(r"</p>", "\n\n", t)
    t = strip_tags(t).replace("\xa0", " ")
    paras = []
    for para in re.split(r"\n\s*\n", t):
        lines = [re.sub(r"[ \t]+", " ", l).strip() for l in para.split("\n")]
        para = "\n".join(l for l in lines if l)
        if para:
            paras.append(para)
    return "\n\n".join(paras)


NOT_SUBMITTED = re.compile(r"^(No statement (was )?submitted|There is no statement)", re.I)
SUBMITTED_BY = re.compile(r"^\W*Stat(e)?ment submitted by:\s*", re.I)


def statement(text: str | None) -> dict | None:
    if text is None:
        return None
    if NOT_SUBMITTED.match(text):
        return {"submitted": False, "text": text}
    paras = text.split("\n\n")
    submitted_by = None
    if SUBMITTED_BY.match(paras[-1]):
        submitted_by = SUBMITTED_BY.sub("", paras.pop())
    return {"submitted": True, "text": "\n\n".join(paras), "submitted_by": submitted_by}


def _section(html: str, ident: str) -> str | None:
    m = re.search(rf'<div[^>]* id="{ident}">(.*?)</div>', html, re.S)
    return m.group(1) if m else None


def parse_measure_detail(html: str) -> dict:
    """Ballot title through contact info from a KCE ballotmeasures.aspx?cid= page."""
    def text(ident):
        frag = _section(html, ident)
        return html_to_text(frag) if frag is not None else None

    full_text = _section(html, "textofresolution")
    full_text_url = re.search(r'href="([^"]+)"', full_text or "")
    title_lines = (text("app-measure-detail-title") or "").split("\n")
    return {
        "jurisdiction": text("app-measure-detail-ballot-title"),
        "proposition": title_lines[0] if title_lines else None,
        "title": " ".join(title_lines[1:]) or None,
        "ballot_title": text("app-measure-detail-description"),
        "explanatory_statement": text("explanatorystatement"),
        "statements": {
            "for": statement(text("statementfor")),
            "against": statement(text("statementagainst")),
            "rebuttal_of_against": statement(text("rebuttalagainst")),
            "rebuttal_of_for": statement(text("rebuttalfor")),
        },
        "passage_requirement": text("validationrules"),
        "full_text_url": unescape(full_text_url.group(1)) if full_text_url else None,
        "contact": text("contactinformation"),
    }


def parse_votewa_measure(doc: dict) -> dict:
    """The same fields from a VoteWA measure.ashx JSON document."""
    def text(key):
        return html_to_text(doc[key]) if doc.get(key) else None

    def committee(key):
        c = text(key)
        return re.sub(r"^Committee Members:\s*", "", c).replace("\n", ", ") if c else None

    pro, con = statement(text("ArgumentFor")), statement(text("ArgumentAgainst"))
    if pro and pro["submitted"]:
        pro["submitted_by"] = committee("CommitteeFor")
    if con and con["submitted"]:
        con["submitted_by"] = committee("CommitteeAgainst")
    return {
        "ballot_title": text("BallotTitle"),
        "explanatory_statement": text("ExplanatoryStatement"),
        "statements": {
            "for": pro,
            "against": con,
            "rebuttal_of_against": statement(text("RebuttalFor")),
            "rebuttal_of_for": statement(text("RebuttalAgainst")),
        },
        "passage_requirement": None,
        "full_text_url": doc.get("FullTextURL") or None,
        "contact": None,
    }


# --- build -------------------------------------------------------------------

def build(election_id: str | None = None) -> tuple[dict, dict, list[str]]:
    """Return (contests doc, measures doc, report lines) without writing."""
    e = election.Election(election_id)
    cfg = election.KCE_SOURCES[e.id]
    raw = e.county("king") / "raw/kce"
    schema = cfg["schema"]
    report = []

    contests = parse_contest_list((raw / cfg["candidates_html"]).read_text())
    with open(raw / cfg["candidates_csv"], encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    unmatched_csv = merge_csv(contests, rows, cfg["csv_ballot_order"])
    if schema >= 2:
        for con in contests:
            con["owner"] = contest_owner(con)
            con["scope"] = contest_scope(con)
            con["uncontested"] = len(con["candidates"]) == 1

    election_meta = {"name": election.ELECTION_META[e.id]["name"], "kce_eid": cfg["eid"]}
    out = {
        "derived_from": [rel(raw / cfg["candidates_html"]), rel(raw / cfg["candidates_csv"])],
        "script": "pipeline/parse_candidates.py",
        "election": election_meta,
    }
    if schema >= 2:
        out["notes"] = (
            "ballot_order is the candidate's position in the eid list (KCE lists candidates in ballot order); "
            "campaign_website/email come from the candidate CSV. owner 'statewide' marks Statewide Contests that "
            "the statewide package owns (assembly must dedupe them against statewide/interim/contests.json); "
            "scope uses the assemble_app_data.py scope model."
        )
    out["contests"] = contests

    measures_html = (raw / cfg["measures_html"]).read_text()
    if schema == 1:
        measures = parse_measure_list_legacy(measures_html)
        mout = {"derived_from": [rel(raw / cfg["measures_html"])], "script": "pipeline/parse_candidates.py",
                "measures": measures}
    else:
        measures, statewide_owned = [], []
        for item in parse_measure_list(measures_html):
            # State Measures link to VoteWA's statewide guide (c=99); the
            # statewide package owns them.
            if re.search(r"[?&]c=99(&|$)", item["href"]):
                statewide_owned.append(item["proposition"])
                continue
            record = {
                "jurisdiction": item["jurisdiction"],
                "proposition": item["proposition"],
                "title": item["title"],
                "slug": slugify(f"{item['jurisdiction']}-{item['proposition']}"),
                "kce_contest_id": item["kce_contest_id"],
                "kce_group": item["kce_group"],
            }
            if item["kce_contest_id"]:
                src = raw / "measures" / f"ballotmeasures-cid{item['kce_contest_id']}.html"
                detail = parse_measure_detail(src.read_text())
                for key in ("jurisdiction", "proposition", "title"):
                    if detail[key] != record[key]:
                        raise SystemExit(f"{src.name}: {key} {detail[key]!r} != list {record[key]!r}")
                detail = {k: v for k, v in detail.items() if k not in ("jurisdiction", "proposition", "title")}
            else:
                # KCE links measures another county administers to VoteWA's guide.
                mid = re.search(r"/measure/(\d+)", item["href"]).group(1)
                found = sorted((e.county("king") / "raw/votewa").glob(f"*-measure-{mid}.json"))
                if len(found) != 1:
                    raise SystemExit(f"no raw detail source for {item['jurisdiction']} ({item['href']})")
                src = found[0]
                detail = parse_votewa_measure(json.loads(src.read_text()))
                record["votewa_measure_id"] = mid
            scope = measure_scope(item["jurisdiction"])
            record.update(detail)
            record["scope"] = scope
            if scope["layer"] in UNRESOLVED_LAYERS:
                record["scope_unresolved"] = UNRESOLVED_LAYERS[scope["layer"]]
            record["derived_from"] = [rel(raw / cfg["measures_html"]), rel(src)]
            measures.append(record)
        mout = {
            "derived_from": [rel(raw / cfg["measures_html"])],
            "script": "pipeline/parse_candidates.py",
            "election": election_meta,
            "notes": (
                "Local measures only. Ballot title, explanatory statement and pro/con statements come from each "
                "measure's KCE detail page (the text KCE prints in the local voters' pamphlet), or from VoteWA's "
                "measure JSON when KCE links there instead (Milton). rebuttal_of_against is the proponents' "
                "rebuttal; rebuttal_of_for the opponents'. scope_unresolved marks a scope the King District "
                "Adapter cannot resolve yet."
            ),
            "statewide_owned_measures": statewide_owned,
            "measures": measures,
        }

    n_c = sum(len(c["candidates"]) for c in contests)
    n_matched = sum(1 for con in contests for c in con["candidates"] if "csv_jurisdiction" in c)
    report.append(f"contests: {len(contests)}  candidates: {n_c}  csv-matched: {n_matched}")
    report.append(f"measures: {len(mout['measures'])}")
    if unmatched_csv:
        report.append(f"CSV rows not matched to a contest candidate: {len(unmatched_csv)}")
    for con in contests:
        report.append(f"  [{con['category']}] {con['office']} — {con['district']} ({len(con['candidates'])})")
    return out, mout, report


def main():
    e = election.Election(election.from_argv())
    out, mout, report = build(e.id)
    interim = e.county("king") / "interim"
    interim.mkdir(parents=True, exist_ok=True)
    (interim / "contests.json").write_text(json.dumps(out, indent=2))
    (interim / "measures.json").write_text(json.dumps(mout, indent=2))
    print("\n".join(report))


if __name__ == "__main__":
    main()
