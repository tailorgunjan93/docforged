"""
Pre-cache PDF documents using PyMuPDF (lightweight, no neural nets).
Saves as *_docling.pkl so the eval code finds them transparently.

CACHE INVALIDATION NOTES
========================
PKL files store fully-normalised Document objects (sections + §ids + parent links).
They must be deleted and rebuilt whenever ANY of the following change:

  1. docnest/normalizer.py  — §id assignment or parent/child logic changes.
                              Example: PR #7 changed §ids from zero-padded (§1.0.1)
                              to compact (§1.1) for skipped heading levels.

  2. docnest/parsers/       — Parser output changes (new section detection, table
                              extraction improvements, text cleaning, etc.).

  3. Source PDF is updated  — The cache mtime check below handles this automatically.

HOW TO REBUILD
==============
  # Delete stale caches
  del eval\cache\*_docling.pkl          (Windows)
  rm  eval/cache/*_docling.pkl          (Unix)

  # Rebuild (uses PyMuPDF — fast, no GPU/RAM risk)
  python eval/_precache.py

CACHE FILES
===========
  *_docling.pkl   — PDF document caches (this script builds these)
  *_pymupdf.pkl   — Generated-file caches (XLSX/DOCX/HTML/MD, built at eval runtime)

The *_pymupdf.pkl files are rebuilt automatically on each eval run and do NOT
need manual deletion.
"""
import sys, pickle, time
sys.path.insert(0, r"D:\Learning\docnest")
from pathlib import Path
from docnest.normalizer import SectionNormaliser
from docnest.parsers.factory import ParserFactory

DOCS_DIR  = Path(r"D:\Learning\docnest\eval\docs")
CACHE_DIR = Path(r"D:\Learning\docnest\eval\cache")

pdfs = [
    "gpt3_paper.pdf",
    "attention_paper.pdf",
    "llama2_paper.pdf",
    "constitutional_ai.pdf",
    # Add new PDFs here when they are introduced to the eval suite.
    # ipcc_spm.pdf and bis_2024.pdf were cached via docling directly
    # (see eval/cache/) — only rebuild those if docling is available and
    # has enough RAM (~4 GB free recommended).
]

for fname in pdfs:
    path = DOCS_DIR / fname
    if not path.exists():
        print(f"  SKIP (file not found): {fname}")
        continue
    cache_path = CACHE_DIR / f"{path.stem}_docling.pkl"
    if cache_path.exists() and cache_path.stat().st_mtime >= path.stat().st_mtime:
        print(f"  skip (cached): {fname}")
        continue
    print(f"  parsing {fname} with PyMuPDF ...", flush=True)
    t0 = time.perf_counter()
    raw = ParserFactory(pdf_engine="pymupdf").get(str(path)).parse(str(path))
    doc = SectionNormaliser().normalise(raw)
    ms  = (time.perf_counter() - t0) * 1000
    n_t = sum(len(s.tables) for s in doc.sections)
    print(f"  -> {len(doc.sections)} sections, {n_t} tables  ({ms:.0f} ms)")
    with open(cache_path, "wb") as fh:
        pickle.dump(doc, fh)
    print(f"  saved: {cache_path.name}")

print("DONE")
