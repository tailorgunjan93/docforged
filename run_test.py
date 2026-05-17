"""
DocNest end-to-end test script.

Tests the full pipeline on:
  - GunjanTailor.pdf        (resume PDF)
  - LIC_NEFT_Policy.docx    (policy Word document)

Uses SentenceTransformerEmbedder (all-MiniLM-L6-v2, local, free, 384-dim).
Runs in --fast mode (no LLM required).

Run:
    python run_test.py
"""

import os
import sys
from pathlib import Path

# Force UTF-8 on stdout/stderr BEFORE Rich opens the stream.
# Windows defaults to cp1252 which can't encode LLM responses with
# characters like ‑ (non-breaking hyphen). Must happen first.
os.environ["PYTHONIOENCODING"] = "utf-8"
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]

# ── Groq API key ──────────────────────────────────────────────────────────────
# Set GROQ_API_KEY env var before running, OR paste it here (never commit to git):
#   $env:GROQ_API_KEY = "gsk_..."          (PowerShell)
#   set GROQ_API_KEY=gsk_...               (CMD)
# ─────────────────────────────────────────────────────────────────────────────

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

console = Console(force_terminal=True, legacy_windows=False)

# Map tricky Unicode look-alikes to their ASCII equivalents so the table
# never crashes on Windows cp1252 (non-breaking hyphens, smart quotes, etc.)
_UNICODE_MAP = str.maketrans({
    "‑": "-",   # non-breaking hyphen
    "–": "-",   # en dash
    "—": "-",   # em dash
    "‘": "'",   # left single quote
    "’": "'",   # right single quote
    "“": '"',   # left double quote
    "”": '"',   # right double quote
    "…": "...", # ellipsis
    " ": " ",   # non-breaking space
})

def _safe_text(text: str) -> str:
    """Replace Unicode chars that Windows cp1252 can't encode."""
    return text.translate(_UNICODE_MAP).encode("ascii", errors="replace").decode("ascii")

PDF_PATH   = r"C:\Users\tailo\Downloads\Documents\GunjanTailor.pdf"
DOCX_PATH  = r"C:\Users\tailo\Downloads\Documents\LIC_NEFT_Policy_140952536.docx"
CLAIM_PATH = r"C:\Users\tailo\Downloads\Documents\claim form PartA.docx"
OUT_DIR    = Path(__file__).parent / "test_output"

OUT_DIR.mkdir(exist_ok=True)

SEP = "=" * 62


def print_header(msg: str) -> None:
    console.print(f"\n[bold cyan]{SEP}[/bold cyan]")
    console.print(f"[bold cyan]  {msg}[/bold cyan]")
    console.print(f"[bold cyan]{SEP}[/bold cyan]")


def run_pipeline(
    source: str,
    out_name: str,
    use_pymupdf: bool = False,
    # LLM — provider / model / api_key
    llm_provider: str = "groq",
    llm_model: str = "llama-3.3-70b-versatile",
    llm_api_key: str | None = None,
    # Embeddings — same three-param pattern
    emb_provider: str = "huggingface",
    emb_model: str = "all-MiniLM-L6-v2",
    emb_api_key: str | None = None,
) -> Path:
    """Run the full DocNest pipeline on a file and return the .udf path."""
    from docnest.pipeline import DocNestPipeline
    from docnest.parsers.pymupdf_pdf import PyMuPDFParser
    from docnest.normalizer import SectionNormaliser
    from docnest.intelligence import IntelligenceEngine
    from docnest.embedder import LangChainEmbedder
    from docnest.writer import UDFWriter
    from docnest.quantizer import Quantizer

    out_path = OUT_DIR / out_name
    stages: list[str] = []

    def on_stage(stage: str, data: object) -> None:
        stages.append(stage)
        console.print(f"  [green]OK[/green] Stage: [yellow]{stage}[/yellow]")

    skip_llm = not bool(llm_api_key or llm_provider == "ollama")

    # ── PyMuPDF fast path for PDFs ────────────────────────────────────────────
    if use_pymupdf and source.lower().endswith(".pdf"):
        embedder = LangChainEmbedder(emb_provider, emb_model, api_key=emb_api_key)
        writer   = UDFWriter(embedder, Quantizer("float16"))
        normaliser = SectionNormaliser()
        parser = PyMuPDFParser()

        console.print(f"  [dim]Parser   : PyMuPDFParser (fast, no ML)[/dim]")
        console.print(f"  [dim]Embedding: {emb_provider}/{emb_model}[/dim]")

        raw = parser.parse(source)
        on_stage("parse", raw)
        doc = normaliser.normalise(raw)
        on_stage("normalise", doc)

        if not skip_llm:
            console.print(f"  [dim]LLM      : {llm_provider}/{llm_model}[/dim]")
            engine = IntelligenceEngine(llm_provider, llm_model, api_key=llm_api_key)
            doc = engine.enrich_sections(doc);  on_stage("enrich_sections", doc)
            doc = engine.enrich_document(doc);  on_stage("enrich_document", doc)
        else:
            console.print(f"  [dim]LLM      : skipped (no api_key)[/dim]")

        on_stage("embed", doc)
        result_path = writer.write(doc, str(out_path))
        on_stage("write", result_path)
        size_kb = Path(result_path).stat().st_size // 1024
        console.print(f"\n  [bold green]Written:[/bold green] {result_path}  ({size_kb:,} KB)")
        return Path(result_path)

    # ── Default pipeline (DocxParser / DoclingPDFParser) ─────────────────────
    console.print(f"  [dim]Embedding: {emb_provider}/{emb_model}[/dim]")
    if not skip_llm:
        console.print(f"  [dim]LLM      : {llm_provider}/{llm_model}[/dim]")
    else:
        console.print(f"  [dim]LLM      : skipped (no api_key)[/dim]")

    pipeline = DocNestPipeline(
        llm_provider=llm_provider, llm_model=llm_model, llm_api_key=llm_api_key,
        emb_provider=emb_provider, emb_model=emb_model, emb_api_key=emb_api_key,
        quantization="float16",
        skip_intelligence=skip_llm,
        on_stage_complete=on_stage,
    )
    result = pipeline.convert(source, output=str(out_path))
    size_kb = Path(result).stat().st_size // 1024
    console.print(f"\n  [bold green]Written:[/bold green] {result}  ({size_kb:,} KB)")
    return Path(result)


def inspect_udf(udf_path: Path) -> None:
    """Load the .udf and print catalogue info."""
    from docnest.reader import UDFIndex

    index = UDFIndex.load(str(udf_path))
    cat = index._catalogue

    section_index = cat.get("section_index", [])
    total_tokens = sum(e.get("token_count", 0) for e in section_index)

    # Summary panel
    console.print(
        Panel(
            f"[bold]{cat.get('title', 'Untitled')}[/bold]\n\n"
            f"Sections : [cyan]{len(section_index)}[/cyan]\n"
            f"Tokens   : [cyan]~{total_tokens:,}[/cyan]\n"
            f"Embedding: [cyan]{cat.get('embedding_model', '?')}[/cyan]  "
            f"([cyan]{cat.get('embedding_dims', '?')}[/cyan] dims)\n"
            f"Quant    : [cyan]{cat.get('quantization', '?')}[/cyan]",
            title=f"[green]{udf_path.name}[/green]",
            border_style="green",
        )
    )

    # Section tree (first 20)
    tbl = Table(title="Section Tree", box=box.SIMPLE, show_header=True, header_style="bold")
    tbl.add_column("id", style="dim", width=10)
    tbl.add_column("Lvl", width=4)
    tbl.add_column("Title", min_width=30)
    tbl.add_column("Tokens", justify="right", width=8)

    for entry in section_index[:20]:
        indent = "  " * (entry.get("level", 1) - 1)
        tbl.add_row(
            entry.get("id", ""),
            str(entry.get("level", "")),
            indent + entry.get("title", ""),
            str(entry.get("token_count", 0)),
        )

    if len(section_index) > 20:
        tbl.add_row("...", "", f"({len(section_index) - 20} more sections)", "")

    console.print(tbl)


def run_queries(
    udf_path: Path,
    queries: list[str],
    llm_provider: str = "groq",
    llm_model: str = "llama-3.3-70b-versatile",
    llm_api_key: str | None = None,
) -> None:
    """Run test queries through the 5-layer engine."""
    from docnest.reader import UDFIndex

    index = UDFIndex.load(str(udf_path))

    tbl = Table(title="Query Results", box=box.ROUNDED, show_header=True, header_style="bold")
    tbl.add_column("Question", width=34)
    tbl.add_column("Answer", width=42)
    tbl.add_column("Layer", width=14)
    tbl.add_column("Cite", width=8)

    layer_labels = {
        0: "[green]L0 pre-comp[/green]",
        1: "[cyan]L1 BM25+cos[/cyan]",
        2: "[yellow]L2 LLM sec[/yellow]",
        3: "[orange1]L3 LLM multi[/orange1]",
        4: "[red]L4 full doc[/red]",
    }

    for q in queries:
        result = index.query(q, llm_provider=llm_provider, llm_model=llm_model, llm_api_key=llm_api_key)
        layer_str = layer_labels.get(result.layer_used, f"L{result.layer_used}")
        cite = result.citations[0] if result.citations else "-"
        raw_ans = result.answer[:80] + "..." if len(result.answer) > 80 else result.answer
        # Sanitise: replace Unicode chars that cp1252 can't render
        ans = _safe_text(raw_ans)
        tbl.add_row(q, ans, layer_str, cite)

    console.print(tbl)


# ================================================================
#  MAIN
# ================================================================

if __name__ == "__main__":

    # ══════════════════════════════════════════════════════════════════
    #  CONFIG — same three-param pattern for LLM and embeddings
    #  api_key is optional: omit for Ollama (local) and HuggingFace (local)
    # ══════════════════════════════════════════════════════════════════

    # ── LLM ───────────────────────────────────────────────────────────
    LLM_PROVIDER = "groq"
    LLM_MODEL    = "openai/gpt-oss-120b"
    LLM_API_KEY  = os.environ.get("GROQ_API_KEY") or None   # gsk_...

    # ── Embeddings ────────────────────────────────────────────────────
    EMB_PROVIDER = "huggingface"                  # local, free, no key needed
    EMB_MODEL    = "all-MiniLM-L6-v2"             # 384-dim sentence-transformers
    EMB_API_KEY  = None                           # not needed for local HuggingFace

    # ══════════════════════════════════════════════════════════════════

    if LLM_API_KEY:
        console.print(
            f"[green]LLM[/green]  {LLM_PROVIDER}/{LLM_MODEL}  [dim](key set)[/dim]\n"
            f"[green]EMB[/green]  {EMB_PROVIDER}/{EMB_MODEL}  [dim](local)[/dim]"
        )
    else:
        console.print(
            f"[yellow]LLM[/yellow]  {LLM_PROVIDER}/{LLM_MODEL}  "
            "[yellow]no api_key — fast mode (no enrichment)[/yellow]\n"
            f"[green]EMB[/green]  {EMB_PROVIDER}/{EMB_MODEL}  [dim](local)[/dim]\n"
            "[dim]Set key:  $env:GROQ_API_KEY = 'gsk_...'[/dim]"
        )

    # ── shared kwargs ─────────────────────────────────────────────────
    llm_kw = dict(llm_provider=LLM_PROVIDER, llm_model=LLM_MODEL, llm_api_key=LLM_API_KEY)
    emb_kw = dict(emb_provider=EMB_PROVIDER, emb_model=EMB_MODEL, emb_api_key=EMB_API_KEY)

    # ---- PDF: GunjanTailor.pdf ----------------------------------
    print_header("TEST 1 - PDF: GunjanTailor.pdf  (PyMuPDF parser)")
    pdf_udf = run_pipeline(PDF_PATH, "GunjanTailor.udf", use_pymupdf=True, **llm_kw, **emb_kw)
    inspect_udf(pdf_udf)
    run_queries(pdf_udf, [
        "What is this document about?",
        "What skills does this person have?",
        "What is the education background?",
        "Summarise",
    ], **llm_kw)

    # ---- DOCX: LIC Policy ---------------------------------------
    print_header("TEST 2 - DOCX: LIC_NEFT_Policy.docx")
    docx_udf = run_pipeline(DOCX_PATH, "LIC_Policy.udf", **llm_kw, **emb_kw)
    inspect_udf(docx_udf)
    run_queries(docx_udf, [
        "What is this document about?",
        "Summarise",
        "What are the policy details?",
        "What is the bank account number?",
    ], **llm_kw)

    # ---- DOCX: Claim Form Part A --------------------------------
    print_header("TEST 3 - DOCX: claim form PartA.docx  (pseudo-heading detection)")
    claim_udf = run_pipeline(CLAIM_PATH, "ClaimFormPartA.udf", **llm_kw, **emb_kw)
    inspect_udf(claim_udf)
    run_queries(claim_udf, [
        "What is this document about?",
        "What are the details of the insured person?",
        "What are the insurance history details?",
        "Summarise",
    ], **llm_kw)

    console.print(f"\n[bold green]All tests complete![/bold green]\n")
    console.print(f"[dim].udf files saved to: {OUT_DIR}[/dim]\n")
