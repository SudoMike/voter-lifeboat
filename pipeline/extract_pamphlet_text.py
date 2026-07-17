"""Stage: raw -> interim. Extract per-page text from the voters pamphlet PDFs.

Input:  data/washington-state/counties/king/raw/pamphlet/edition-{1,2}.pdf.url
Output: data/washington-state/counties/king/interim/pamphlet-text/edition-{1,2}/page-NNN.txt
        data/washington-state/counties/king/interim/pamphlet-text/extraction.meta.json
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import urlretrieve

from pypdf import PdfReader

ROOT = Path(__file__).resolve().parent.parent
KING = ROOT / "data/washington-state/counties/king"
RAW = KING / "raw/pamphlet"
OUT = KING / "interim/pamphlet-text"
CACHE = ROOT / ".cache/voter-lifeboat/pamphlets/king"
CACHE.mkdir(parents=True, exist_ok=True)

manifest = {"stage": "interim", "script": "pipeline/extract_pamphlet_text.py",
            "derived_from": [], "extracted_at": datetime.now(timezone.utc).isoformat(),
            "editions": {}}

def resolve_pdf(pointer: Path) -> Path:
    if pointer.suffix == ".pdf":
        return pointer
    if pointer.name.endswith(".pdf.url"):
        url = pointer.read_text().strip()
        cached = CACHE / pointer.name.removesuffix(".url")
        if not cached.exists():
            print(f"downloading {url} -> {cached}")
            urlretrieve(url, cached)
        return cached
    raise ValueError(f"unsupported pamphlet source: {pointer}")


for pointer in sorted([*RAW.glob("edition-*.pdf"), *RAW.glob("edition-*.pdf.url")]):
    pdf = resolve_pdf(pointer)
    name = pdf.stem
    outdir = OUT / name
    outdir.mkdir(parents=True, exist_ok=True)
    reader = PdfReader(pdf)
    for i, page in enumerate(reader.pages, start=1):
        (outdir / f"page-{i:03d}.txt").write_text(page.extract_text() or "")
    manifest["derived_from"].append(f"data/washington-state/counties/king/raw/pamphlet/{pointer.name}")
    manifest["editions"][name] = {"pages": len(reader.pages)}
    print(f"{name}: {len(reader.pages)} pages extracted")

OUT.mkdir(parents=True, exist_ok=True)
(OUT / "extraction.meta.json").write_text(json.dumps(manifest, indent=2))
