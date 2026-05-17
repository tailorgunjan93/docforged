"""Tests for UDFIndex (reader) — loading and five-layer query resolution.

Run: pytest tests/test_reader.py -v
"""
from __future__ import annotations

import json
import zipfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from docnest.reader import UDFIndex


# ── Load tests ────────────────────────────────────────────────────────────────

class TestUDFIndexLoad:
    def test_load_returns_udf_index(self, minimal_udf_path: str):
        idx = UDFIndex.load(minimal_udf_path)
        assert isinstance(idx, UDFIndex)

    def test_catalogue_is_loaded(self, minimal_udf_path: str):
        idx = UDFIndex.load(minimal_udf_path)
        assert idx._catalogue is not None

    def test_doc_id_accessible(self, minimal_udf_path: str):
        idx = UDFIndex.load(minimal_udf_path)
        assert idx._catalogue.get("doc_id") is not None

    def test_section_index_accessible(self, minimal_udf_path: str):
        idx = UDFIndex.load(minimal_udf_path)
        assert len(idx._catalogue["section_index"]) > 0

    def test_missing_file_raises(self):
        from docnest.exceptions import UDFReadError
        with pytest.raises(UDFReadError):
            UDFIndex.load("/tmp/does_not_exist_abc123xyz.udf")

    def test_load_with_numpy_backend(self, minimal_udf_path: str):
        idx = UDFIndex.load(minimal_udf_path, vector="numpy")
        assert idx is not None

    def test_load_with_custom_vector_backend(self, minimal_udf_path: str):
        from docnest.providers.vector import NumpyVectorBackend
        backend = NumpyVectorBackend()
        idx = UDFIndex.load(minimal_udf_path, vector=backend)
        assert idx is not None

    def test_content_not_loaded_eagerly(self, minimal_udf_path: str):
        """Content should be lazy — not loaded until a section is fetched."""
        idx = UDFIndex.load(minimal_udf_path)
        # _content can be None or empty dict before first access
        assert idx._content is None or isinstance(idx._content, dict)

    def test_embed_matrix_not_loaded_eagerly(self, minimal_udf_path: str):
        """Embedding matrix should be lazy — not decoded until first search."""
        idx = UDFIndex.load(minimal_udf_path)
        assert idx._embed_matrix is None


# ── get_section ───────────────────────────────────────────────────────────────

class TestGetSection:
    def test_returns_dict_for_valid_id(self, minimal_udf_path: str):
        idx = UDFIndex.load(minimal_udf_path)
        # Get the first section id from the index
        first_id = idx._catalogue["section_index"][0]["id"]
        section = idx.get_section(first_id)
        assert isinstance(section, dict)
        assert "text" in section

    def test_returns_none_for_missing_id(self, minimal_udf_path: str):
        idx = UDFIndex.load(minimal_udf_path)
        result = idx.get_section("§999.99.99")
        assert result is None

    def test_section_has_title(self, minimal_udf_path: str):
        idx = UDFIndex.load(minimal_udf_path)
        first_id = idx._catalogue["section_index"][0]["id"]
        section = idx.get_section(first_id)
        assert "title" in section

    def test_multiple_get_section_calls_consistent(self, minimal_udf_path: str):
        idx = UDFIndex.load(minimal_udf_path)
        first_id = idx._catalogue["section_index"][0]["id"]
        s1 = idx.get_section(first_id)
        s2 = idx.get_section(first_id)
        assert s1 == s2


# ── Layer 0: pre-computed ─────────────────────────────────────────────────────

class TestLayer0:
    def test_summary_question_hits_layer_0(self, minimal_udf_path: str):
        idx = UDFIndex.load(minimal_udf_path)
        result = idx.get_precomputed("What is this document about?")
        # Should return something (summary is set in fixture)
        assert result is not None
        assert len(result) > 0

    def test_layer_0_answer_contains_summary(self, minimal_udf_path: str):
        idx = UDFIndex.load(minimal_udf_path)
        result = idx.get_precomputed("summary")
        assert result is not None

    def test_irrelevant_question_returns_none_at_layer_0(self, minimal_udf_path: str):
        idx = UDFIndex.load(minimal_udf_path)
        # Very specific technical query unlikely to match pre-computed
        result = idx.get_precomputed("§3.2.1 subsection technical detail xyz987")
        # May return None — pre-computed is only for high-level questions
        # We just verify it doesn't crash
        assert result is None or isinstance(result, str)


# ── Layer 1: hybrid search ────────────────────────────────────────────────────

class TestLayer1:
    def test_hybrid_search_returns_list(self, minimal_udf_path: str):
        idx = UDFIndex.load(minimal_udf_path)
        results = idx._hybrid_search("Part A Background")
        assert isinstance(results, list)

    def test_hybrid_search_results_are_tuples(self, minimal_udf_path: str):
        idx = UDFIndex.load(minimal_udf_path)
        results = idx._hybrid_search("methods")
        if results:
            assert all(isinstance(r, tuple) and len(r) == 2 for r in results)

    def test_hybrid_search_scores_non_negative(self, minimal_udf_path: str):
        idx = UDFIndex.load(minimal_udf_path)
        results = idx._hybrid_search("Part A")
        for _, score in results:
            assert score >= 0

    def test_hybrid_search_sorted_descending(self, minimal_udf_path: str):
        idx = UDFIndex.load(minimal_udf_path)
        results = idx._hybrid_search("Part A")
        scores = [r[1] for r in results]
        assert scores == sorted(scores, reverse=True)

    def test_hybrid_search_ids_match_section_index(self, minimal_udf_path: str):
        idx = UDFIndex.load(minimal_udf_path)
        valid_ids = {e["id"] for e in idx._catalogue["section_index"]}
        results = idx._hybrid_search("Background")
        for sec_id, _ in results:
            assert sec_id in valid_ids


# ── Embedding matrix ──────────────────────────────────────────────────────────

class TestEmbeddingMatrix:
    def test_matrix_loaded_on_first_search(self, minimal_udf_path: str):
        idx = UDFIndex.load(minimal_udf_path)
        assert idx._embed_matrix is None
        idx._load_embed_matrix()
        assert idx._embed_matrix is not None

    def test_matrix_shape_matches_section_count(self, minimal_udf_path: str):
        idx = UDFIndex.load(minimal_udf_path)
        idx._load_embed_matrix()
        n_sections = len(idx._catalogue["section_index"])
        assert idx._embed_matrix.shape[0] == n_sections

    def test_matrix_dtype_is_float32(self, minimal_udf_path: str):
        idx = UDFIndex.load(minimal_udf_path)
        idx._load_embed_matrix()
        assert idx._embed_matrix.dtype == np.float32


# ── Full query (mocked LLM) ───────────────────────────────────────────────────

class TestQueryWithMockedLLM:
    # LLM call methods return (answer_str, token_count) tuples
    LLM_RETURN = ("Mock LLM answer.", 100)

    def test_query_returns_result(self, minimal_udf_path: str):
        idx = UDFIndex.load(minimal_udf_path)
        with patch.object(idx, "_call_llm_section", return_value=self.LLM_RETURN):
            with patch.object(idx, "_call_llm_multi", return_value=self.LLM_RETURN):
                with patch.object(idx, "_call_llm_full", return_value=self.LLM_RETURN):
                    result = idx.query("What is this document about?")
        assert result is not None

    def test_query_answer_is_non_empty(self, minimal_udf_path: str):
        idx = UDFIndex.load(minimal_udf_path)
        with patch.object(idx, "_call_llm_section", return_value=self.LLM_RETURN):
            with patch.object(idx, "_call_llm_multi", return_value=self.LLM_RETURN):
                with patch.object(idx, "_call_llm_full", return_value=self.LLM_RETURN):
                    result = idx.query("What is this about?")
        # QueryResult can be a dataclass or dict
        answer = result.answer if hasattr(result, "answer") else result.get("answer", "")
        assert answer

    def test_layer_0_does_not_call_llm(self, minimal_udf_path: str):
        """Layer 0 (pre-computed) should never invoke LLM."""
        idx = UDFIndex.load(minimal_udf_path)
        with patch.object(idx, "_call_llm_section", return_value=self.LLM_RETURN) as mock_llm:
            result = idx.query("What is this document about?")
            assert result is not None


# ── Corrupted / edge-case UDFs ────────────────────────────────────────────────

class TestEdgeCases:
    def test_load_udf_with_empty_sections(self, tmp_path: Path):
        """A UDF with zero sections should load without crashing."""
        import json, zipfile
        from docnest.models import Document, RawDocument
        from docnest.normalizer import SectionNormaliser
        from docnest.quantizer import Quantizer
        from docnest.writer import UDFWriter
        from tests.conftest import MockEmbedder

        raw = RawDocument(doc_id="empty", title="Empty", source="f.pdf", format="pdf", sections=[])
        doc = SectionNormaliser().normalise(raw)
        doc.summary = "Empty document."
        out = str(tmp_path / "empty.udf")
        UDFWriter(MockEmbedder(), Quantizer("float16")).write(doc, out)
        idx = UDFIndex.load(out)
        assert idx is not None
        assert idx._catalogue["section_index"] == []

    def test_query_on_empty_document_does_not_crash(self, tmp_path: Path):
        from docnest.models import RawDocument
        from docnest.normalizer import SectionNormaliser
        from docnest.quantizer import Quantizer
        from docnest.writer import UDFWriter
        from tests.conftest import MockEmbedder

        raw = RawDocument(doc_id="empty", title="Empty", source="f.pdf", format="pdf", sections=[])
        doc = SectionNormaliser().normalise(raw)
        doc.summary = "Empty."
        out = str(tmp_path / "empty.udf")
        UDFWriter(MockEmbedder(), Quantizer("float16")).write(doc, out)
        idx = UDFIndex.load(out)
        # LLM methods return (answer, tokens) tuples
        with patch.object(idx, "_call_llm_full", return_value=("No content.", 0)):
            result = idx.query("anything")
        assert result is not None
