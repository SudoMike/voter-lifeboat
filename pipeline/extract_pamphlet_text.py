"""Stage: raw -> interim. Extract per-page text from the voters pamphlet PDFs.

Input:  data/raw/pamphlet/edition-{1,2}.pdf
Output: data/interim/pamphlet-text/edition-{1,2}/page-NNN.txt
        data/interim/pamphlet-text/extraction.meta.json
"""

import json
from datetime import datetime, timezone
from pathlib import Path

from pypdf import PdfReader

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data/raw/pamphlet"
OUT = ROOT / "data/interim/pamphlet-text"

manifest = {"stage": "interim", "script": "pipeline/extract_pamphlet_text.py",
            "derived_from": [], "extracted_at": datetime.now(timezone.utc).isoformat(),
            "editions": {}}

for pdf in sorted(RAW.glob("edition-*.pdf")):
    name = pdf.stem
    outdir = OUT / name
    outdir.mkdir(parents=True, exist_ok=True)
    reader = PdfReader(pdf)
    for i, page in enumerate(reader.pages, start=1):
        (outdir / f"page-{i:03d}.txt").write_text(page.extract_text() or "")
    manifest["derived_from"].append(f"data/raw/pamphlet/{pdf.name}")
    manifest["editions"][name] = {"pages": len(reader.pages)}
    print(f"{name}: {len(reader.pages)} pages extracted")

OUT.mkdir(parents=True, exist_ok=True)
(OUT / "extraction.meta.json").write_text(json.dumps(manifest, indent=2))
