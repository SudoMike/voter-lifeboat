# Data pipeline — August 4, 2026 King County Primary

Every file in `final/` must be traceable back through `interim/` to verbatim
pulls in `raw/`. Raw files carry a sibling `*.meta.json` with `url`,
`retrieved_at`, and notes. Interim/final JSON carries `derived_from` (input
paths) and `script` (the transformation that produced it, in `pipeline/`).

```
raw/          verbatim pulls, never edited
interim/      mechanical parses of raw (scripted, deterministic)
dossiers/     per-candidate/measure research notes (AI-researched, cited)
final/        what the app consumes
```

## Raw sources

| File | What it is |
|---|---|
| `raw/kce/2026-primary-candidates.csv` | Official KCE list of everyone ON the Aug 4 primary ballot (158 candidates), ballot order, campaign website/contact |
| `raw/kce/2026-candidates.csv` | Official KCE full 2026 filing list (203; includes general-only races) |
| `raw/kce/candidates-eid54.html` | KCE primary contest list (eid=54 = Aug 2026 primary): categories, official contest & candidate ids |
| `raw/kce/ballotmeasures-eid54.html` | The 7 measures on the primary ballot |
| `raw/kce/august-primary.html` | KCE election landing page (source of eid=54 and pamphlet links) |
| `raw/kce/who-has-filed.html` | KCE filing page (source of the CSV urls) |
| `raw/pamphlet/edition-1.pdf` | Official Local Voters' Pamphlet, English ed. 1 (84 pp — Seattle-area districts) |
| `raw/pamphlet/edition-2.pdf` | Official Local Voters' Pamphlet, English ed. 2 (96 pp — rest of county) |
| `raw/kce/candidates-eid26.html` | WRONG ELECTION (2021 primary), kept for the record |
| `raw/kce/sample-candidate-page.html` | Dead-end record: per-candidate "online pamphlet" links just bounce to the VoteWA JS app |

## Transformations

| Script | In → Out |
|---|---|
| `pipeline/extract_pamphlet_text.py` | pamphlet PDFs → `interim/pamphlet-text/edition-*/page-NNN.txt` (one file per page) |
| `pipeline/parse_candidates.py` | eid54 HTML + primary CSV → `interim/contests.json` (60 contests, 158 candidates, ballot order, campaign sites); measures HTML → `interim/measures.json` (7) |
| `pipeline/build_pamphlet_index.py` | contests+measures+page text → `interim/pamphlet-index.json` (candidate/measure → exact pamphlet edition+pages; 158/158, 7/7 matched) |
| `pipeline/build_research_plan.py` | contests+measures+index → `interim/research-plan.json` (per-contest research depth: deep = 3+ candidates, light = 1-2) |
| `pipeline/verify_dossiers.py` | plan + dossiers → `interim/dossier-audit.json` (completeness + evidence-level audit; 158/158 present) |
| `pipeline/extract_axis_notes.py` | all `_contest.md` + measures → `interim/axis-notes.md` (differentiating-axes evidence for rubric synthesis) |
| *(manual synthesis)* | `interim/axis-notes.md` → `final/rubric.json` (14 axes) + `final/rubric-derivation.md` (rationale + scoring conventions) |

## Dossiers (`dossiers/<contest-slug>/<candidate-slug>.md`)

AI-researched under the tiered source policy (see `CONTEXT.md`: Source Tier).
Frontmatter lists every source with url, tier, and access date; body claims
must cite a listed source. `evidence_level` recorded per candidate.
Research depth: deep for contests where the primary actually decides
something (3+ candidates), light for 1-2 candidate contests (in WA's top-2
primary those candidates all advance regardless).

## Election facts (from raw sources)

- Election: August 4, 2026 Primary and Special Election, King County, WA (KCE eid=54)
- 60 contests with candidates on the primary ballot; 158 candidates; 7 measures
- Categories: Federal (4 congressional districts), State (24 legislative
  contests across LDs 1,5,11,12,30,31,32,33,34,36,37,41,43,45,46,47,48),
  County (Assessor + Council Districts 2, 8), State Supreme Court (4
  positions), District Court (NE Electoral District), City of Seattle
  (Council D5 + Municipal Court)
- Pamphlet edition 1 covers Seattle-area districts; edition 2 the rest.
