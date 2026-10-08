"""Pamphlet pages named by a dossier's pamphlet citation.

A dossier cites the pamphlet as a `type: pamphlet` source whose `ref` is
free text written by the researcher, for example

    local-edition page 14 (duties of offices) and page 21 (candidate statement)
    edition-04 page 24 (identical statement at edition-06 page 24)
    voters-pamphlet-edition-05-king-north-eastside page 34 (same statement in voters-pamphlet-edition-06-king-south-southeast page 32)
    local-edition pages 76-80 (full text of Ordinance No. 127474)
    local-voters-pamphlet page 33 (2026 General Election Voters' Pamphlet, Snohomish County edition, ...)

(`local-voters-pamphlet` is the edition id of a non-King county's pamphlet
pointer, raw/<county>/local-voters-pamphlet.pdf.url.)

assemble_app_data.py turns those into the app's `pamphlet_pages`
([{edition, page}], PDF page numbers), because they name the statement page
itself, unlike the name search in pamphlet-index.json, which also matches
endorsement lists on other candidates' pages.
"""

import re

PAMPHLET_REF = re.compile(
    r"(?:\b(?P<ed>local-edition|local-voters-pamphlet|voters-pamphlet-edition-\d+(?:-[a-z]+)+|edition-\d+)\s+)?"
    r"\bpages?\s+(?P<p>\d+)(?:-(?P<q>\d+))?(?:\s*\((?P<note>[^)]*)\))?"
)
SAME_STATEMENT = re.compile(r"^\s*(same|identical) statements? (in|at)\b", re.I)


def edition_id(name, editions):
    """A ref's edition name as one of `editions` (the package's pamphlet
    pointer names): 'edition-04' -> 'voters-pamphlet-edition-04-king-seattle'.
    None when it names no known edition."""
    if name in editions:
        return name
    m = re.fullmatch(r"edition-(\d+)", name or "")
    if m:
        found = [e for e in editions if e.startswith(f"voters-pamphlet-edition-{int(m.group(1)):02d}-")]
        if len(found) == 1:
            return found[0]
    return None


def ref_pages(ref, editions):
    """[{edition, page}] named by one pamphlet `ref`, in the order written.

    A page whose note starts with "duties" (the offices' duties page, not the
    candidate's statement) is skipped; a "(same/identical statement in/at
    ...)" note adds the other edition's page after it. A page with no edition
    of its own takes the previous one. Refs to another election's pamphlet
    ("2026 primary local pamphlet, ...") and unknown editions give nothing.
    """
    if "primary" in ref.lower():
        return []
    out, edition = [], None
    for m in PAMPHLET_REF.finditer(ref):
        if m.group("ed"):
            edition = edition_id(m.group("ed"), editions)
        note = m.group("note") or ""
        if edition is None or note.lower().startswith("dut"):
            continue
        first, last = int(m.group("p")), int(m.group("q") or m.group("p"))
        out += [{"edition": edition, "page": n} for n in range(first, last + 1)]
        if SAME_STATEMENT.match(note):
            out += ref_pages(SAME_STATEMENT.sub("", note), editions)
    return out


def sources_pages(sources, editions):
    """Distinct pages of every `type: pamphlet` source, in source order."""
    pages = []
    for source in sources:
        if source.get("type") == "pamphlet" and source.get("ref"):
            for page in ref_pages(source["ref"], editions):
                if page not in pages:
                    pages.append(page)
    return pages
