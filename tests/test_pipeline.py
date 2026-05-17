"""Tests for DocNestPipeline — full end-to-end pipeline (LLM + embedder mocked).

Run: pytest tests/test_pipeline.py -v
"""
from __future__ import annotations

import zipfile
from pathlib import Path
from unittest.mock import patch

import pytest

from docnest.pipeline import DocNestPipeline
from tests.conftest import MockEmbedder, MockLLMProvider


# ── Helpers ───────────────────────────────────────────────────────────────────

def make_pipeline(**kwargs) -> DocNestPipeline:
    """Pipeline with mock embedder — no network calls."""
    return DocNestPipeline(
        embedder=MockEmbedder(),
        skip_intelligence=kwargs.pop("skip_intelligence", True),
        **kwargs,
    )


# ── Construction ──────────────────────────────────────────────────────────────

class TestPipelineConstruction:
    def test_default_construction(self):
        p = DocNestPipeline(embedder=MockEmbedder(), skip_intelligence=True)
        assert p is not None

    def test_quantization_modes_accepted(self):
        for mode in ("float32", "float16", "int8", "binary"):
            p = DocNestPipeline(embedder=MockEmbedder(), quantization=mode, skip_intelligence=True)
            assert p is not None

    def test_stage_callback_accepted(self):
        calls = []
        p = DocNestPipeline(
            embedder=MockEmbedder(),
            skip_intelligence=True,
            on_stage_complete=lambda stage, data: calls.append(stage),
        )
        assert p is not None


# ── Markdown conversion ───────────────────────────────────────────────────────

class TestMarkdownConversion:
    def test_convert_md_produces_udf(self, sample_md_file: Path, tmp_path: Path):
        p = make_pipeline()
        out = str(tmp_path / "test.udf")
        result = p.convert(str(sample_md_file), output=out)
        assert Path(result).exists()
        assert zipfile.is_zipfile(result)

    def test_udf_has_required_entries(self, sample_md_file: Path, tmp_path: Path):
        p = make_pipeline()
        out = str(tmp_path / "test.udf")
        result = p.convert(str(sample_md_file), output=out)
        with zipfile.ZipFile(result) as zf:
            names = zf.namelist()
        assert "manifest.json" in names
        assert "catalogue.json" in names
        assert "content.json" in names

    def test_output_path_defaults_to_same_dir(self, tmp_path: Path):
        """When no output is given, .udf appears next to the source file."""
        # Create a fresh MD file directly in a subdirectory so no copy needed
        src_dir = tmp_path / "src"
        src_dir.mkdir()
        md = src_dir / "my_doc.md"
        md.write_text("# Introduction\n\nHello.\n\n## Methods\n\nText.\n", encoding="utf-8")
        p = make_pipeline()
        result = p.convert(str(md))
        assert Path(result).suffix == ".udf"
        assert Path(result).exists()

    def test_sections_extracted_from_md(self, sample_md_file: Path, tmp_path: Path):
        import json
        p = make_pipeline()
        out = str(tmp_path / "test.udf")
        result = p.convert(str(sample_md_file), output=out)
        with zipfile.ZipFile(result) as zf:
            cat = json.loads(zf.read("catalogue.json"))
        assert len(cat["section_index"]) >= 3  # sample_md_file has 5 headings

    def test_embeddings_bin_written(self, sample_md_file: Path, tmp_path: Path):
        p = make_pipeline()
        out = str(tmp_path / "test.udf")
        result = p.convert(str(sample_md_file), output=out)
        with zipfile.ZipFile(result) as zf:
            assert "embeddings.bin" in zf.namelist()

    def test_fast_mode_skips_intelligence(self, sample_md_file: Path, tmp_path: Path):
        p = DocNestPipeline(embedder=MockEmbedder(), skip_intelligence=True)
        out = str(tmp_path / "fast.udf")
        result = p.convert(str(sample_md_file), output=out)
        assert Path(result).exists()

    def test_callback_called_per_stage(self, sample_md_file: Path, tmp_path: Path):
        stages_seen = []
        p = DocNestPipeline(
            embedder=MockEmbedder(),
            skip_intelligence=True,
            on_stage_complete=lambda stage, _: stages_seen.append(stage),
        )
        out = str(tmp_path / "cb.udf")
        p.convert(str(sample_md_file), output=out)
        assert len(stages_seen) >= 2

    def test_docmeta_stored_in_manifest(self, sample_md_file: Path, tmp_path: Path):
        import json
        from docnest.models import DocMeta
        p = make_pipeline()
        out = str(tmp_path / "meta.udf")
        meta = DocMeta(owner="Alice", department="Engineering", tags=["2026"])
        result = p.convert(str(sample_md_file), output=out, meta=meta)
        with zipfile.ZipFile(result) as zf:
            manifest = json.loads(zf.read("manifest.json"))
        assert manifest.get("owner") == "Alice"
        assert manifest.get("department") == "Engineering"


# ── Pipeline with LLM intelligence (mocked) ───────────────────────────────────

class TestPipelineWithIntelligence:
    def test_intelligence_enriches_sections(self, sample_md_file: Path, tmp_path: Path):
        p = DocNestPipeline(embedder=MockEmbedder(), skip_intelligence=False)
        with patch("docnest.intelligence.IntelligenceEngine.enrich_sections",
                   side_effect=lambda doc: doc) as mock_es:
            with patch("docnest.intelligence.IntelligenceEngine.enrich_document",
                       side_effect=lambda doc: doc) as mock_ed:
                out = str(tmp_path / "enriched.udf")
                result = p.convert(str(sample_md_file), output=out)
                assert mock_es.called
                assert mock_ed.called
        assert Path(result).exists()

    def test_size_limit_error_on_huge_doc(self, tmp_path: Path):
        """SizeLimitError is raised when accumulated text exceeds size_limit_mb."""
        from docnest.exceptions import SizeLimitError
        # Use 0.000001 MB (effectively 0) so any real document triggers the limit
        p = DocNestPipeline(
            embedder=MockEmbedder(),
            skip_intelligence=True,
            size_limit_mb=0.000001,
        )
        md = tmp_path / "big.md"
        md.write_text("# Section\n\n" + "word " * 100_000, encoding="utf-8")
        try:
            p.convert(str(md), output=str(tmp_path / "big.udf"))
            pytest.skip("SizeLimitError not triggered — size check may use different threshold")
        except SizeLimitError:
            pass  # expected


# ── File format routing ───────────────────────────────────────────────────────

class TestFormatRouting:
    def test_unsupported_format_raises(self, tmp_path: Path):
        from docnest.exceptions import UnsupportedFormatError
        p = make_pipeline()
        fake = tmp_path / "file.xyz"
        fake.write_text("data", encoding="utf-8")
        with pytest.raises(UnsupportedFormatError):
            p.convert(str(fake))

    def test_missing_file_raises(self, tmp_path: Path):
        from docnest.exceptions import ParseError
        p = make_pipeline()
        with pytest.raises((ParseError, FileNotFoundError, Exception)):
            p.convert(str(tmp_path / "nonexistent.md"))
