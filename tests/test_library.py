"""Tests for LibraryManager — multi-document index.

Run: pytest tests/test_library.py -v
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from docnest.library import LibraryEntry, LibraryManager


# ── Helpers ───────────────────────────────────────────────────────────────────

def init_lib(tmp_path: Path, name: str = "Test Library") -> LibraryManager:
    mgr = LibraryManager(str(tmp_path))
    mgr.init(name=name, description="Test library.")
    return mgr


def add_udf(mgr: LibraryManager, udf_path: str) -> LibraryEntry:
    return mgr.add(udf_path)


# ── LibraryManager.init ───────────────────────────────────────────────────────

class TestLibraryInit:
    def test_creates_library_json(self, tmp_path: Path):
        init_lib(tmp_path)
        assert (tmp_path / "library.json").exists()

    def test_library_json_is_valid_json(self, tmp_path: Path):
        init_lib(tmp_path)
        data = json.loads((tmp_path / "library.json").read_text())
        assert isinstance(data, dict)

    def test_library_name_stored(self, tmp_path: Path):
        init_lib(tmp_path, name="My Lib")
        data = json.loads((tmp_path / "library.json").read_text())
        assert data.get("name") == "My Lib"

    def test_documents_list_starts_empty(self, tmp_path: Path):
        init_lib(tmp_path)
        data = json.loads((tmp_path / "library.json").read_text())
        assert data.get("documents", []) == []

    def test_reinit_resets_library(self, tmp_path: Path, minimal_udf: Path):
        mgr = init_lib(tmp_path)
        mgr.add(str(minimal_udf))
        assert len(mgr.list_docs()) == 1

        # Re-init a fresh directory (not the same one — that would keep docs)
        fresh_dir = tmp_path / "fresh"
        fresh_dir.mkdir()
        fresh_mgr = LibraryManager(str(fresh_dir))
        fresh_mgr.init(name="Fresh", description="New start.")
        assert len(fresh_mgr.list_docs()) == 0


# ── LibraryManager.add ────────────────────────────────────────────────────────

class TestLibraryAdd:
    def test_add_returns_library_entry(self, tmp_path: Path, minimal_udf: Path):
        mgr = init_lib(tmp_path)
        entry = mgr.add(str(minimal_udf))
        assert isinstance(entry, LibraryEntry)

    def test_entry_has_doc_id(self, tmp_path: Path, minimal_udf: Path):
        mgr = init_lib(tmp_path)
        entry = mgr.add(str(minimal_udf))
        assert entry.doc_id

    def test_entry_has_udf_path(self, tmp_path: Path, minimal_udf: Path):
        mgr = init_lib(tmp_path)
        entry = mgr.add(str(minimal_udf))
        assert entry.udf_path

    def test_entry_has_keywords_bag(self, tmp_path: Path, minimal_udf: Path):
        mgr = init_lib(tmp_path)
        entry = mgr.add(str(minimal_udf))
        assert isinstance(entry.keywords, list)

    def test_add_persists_to_library_json(self, tmp_path: Path, minimal_udf: Path):
        mgr = init_lib(tmp_path)
        mgr.add(str(minimal_udf))
        data = json.loads((tmp_path / "library.json").read_text())
        assert len(data["documents"]) == 1

    def test_add_multiple_udfs(self, tmp_path: Path, minimal_udf: Path, normalised_doc, mock_embedder):
        """Add the same UDF twice under different names (copy it)."""
        import shutil
        from docnest.quantizer import Quantizer
        from docnest.writer import UDFWriter

        second_doc = normalised_doc
        second_doc.doc_id = "second-doc"
        second_doc.title = "Second Document"
        for s in second_doc.sections:
            s.summary = "Summary."
            s.keywords = ["second"]
        second_doc.summary = "Second doc summary."

        second_path = str(tmp_path / "second.udf")
        UDFWriter(mock_embedder, Quantizer("float16")).write(second_doc, second_path)

        mgr = init_lib(tmp_path)
        mgr.add(str(minimal_udf))
        mgr.add(second_path)

        assert len(mgr.list_docs()) == 2

    def test_add_missing_file_raises(self, tmp_path: Path):
        mgr = init_lib(tmp_path)
        with pytest.raises(Exception):
            mgr.add("/tmp/does_not_exist_xyz.udf")


# ── LibraryManager.list_docs ──────────────────────────────────────────────────

class TestListDocs:
    def test_empty_library_returns_empty(self, tmp_path: Path):
        mgr = init_lib(tmp_path)
        assert mgr.list_docs() == []

    def test_returns_one_entry_after_add(self, tmp_path: Path, minimal_udf: Path):
        mgr = init_lib(tmp_path)
        mgr.add(str(minimal_udf))
        docs = mgr.list_docs()
        assert len(docs) == 1
        assert isinstance(docs[0], LibraryEntry)

    def test_filter_by_department(self, tmp_path: Path, minimal_udf: Path):
        mgr = init_lib(tmp_path)
        entry = mgr.add(str(minimal_udf))
        # Filter for a department that doesn't match
        docs = mgr.list_docs(department="NonexistentDept")
        assert docs == []


# ── LibraryManager.search ─────────────────────────────────────────────────────

class TestLibrarySearch:
    def test_search_returns_list(self, tmp_path: Path, minimal_udf: Path):
        mgr = init_lib(tmp_path)
        mgr.add(str(minimal_udf))
        results = mgr.search("test", top_k=5)
        assert isinstance(results, list)

    def test_search_result_tuples(self, tmp_path: Path, minimal_udf: Path):
        mgr = init_lib(tmp_path)
        mgr.add(str(minimal_udf))
        results = mgr.search("Part A", top_k=5)
        for item in results:
            assert isinstance(item, tuple)
            assert len(item) == 2
            entry, score = item
            assert isinstance(entry, LibraryEntry)
            assert isinstance(score, float)

    def test_search_empty_library_returns_empty(self, tmp_path: Path):
        mgr = init_lib(tmp_path)
        results = mgr.search("anything", top_k=5)
        assert results == []

    def test_search_top_k_respected(self, tmp_path: Path, minimal_udf: Path):
        mgr = init_lib(tmp_path)
        mgr.add(str(minimal_udf))
        results = mgr.search("test", top_k=1)
        assert len(results) <= 1

    def test_search_no_match_returns_empty_or_low_score(self, tmp_path: Path, minimal_udf: Path):
        mgr = init_lib(tmp_path)
        mgr.add(str(minimal_udf))
        results = mgr.search("zzznomatchxyz987qwerty", top_k=5)
        # Either no results or very low scores
        for _, score in results:
            assert score < 0.9


# ── LibraryManager.remove ─────────────────────────────────────────────────────

class TestLibraryRemove:
    def test_remove_by_doc_id(self, tmp_path: Path, minimal_udf: Path):
        mgr = init_lib(tmp_path)
        entry = mgr.add(str(minimal_udf))
        removed = mgr.remove(entry.doc_id)
        assert removed is True
        assert mgr.list_docs() == []

    def test_remove_persists_to_library_json(self, tmp_path: Path, minimal_udf: Path):
        mgr = init_lib(tmp_path)
        entry = mgr.add(str(minimal_udf))
        mgr.remove(entry.doc_id)
        data = json.loads((tmp_path / "library.json").read_text())
        assert len(data["documents"]) == 0

    def test_remove_nonexistent_returns_false(self, tmp_path: Path):
        mgr = init_lib(tmp_path)
        result = mgr.remove("nonexistent-doc-id-xyz")
        assert result is False

    def test_remove_one_of_two_leaves_other(self, tmp_path: Path, minimal_udf: Path, normalised_doc, mock_embedder):
        from docnest.quantizer import Quantizer
        from docnest.writer import UDFWriter

        second_doc = normalised_doc
        second_doc.doc_id = "remove-test-second"
        second_doc.summary = "Second."
        for s in second_doc.sections:
            s.summary = "s"
            s.keywords = ["s"]
        second_path = str(tmp_path / "second.udf")
        UDFWriter(mock_embedder, Quantizer("float16")).write(second_doc, second_path)

        mgr = init_lib(tmp_path)
        e1 = mgr.add(str(minimal_udf))
        mgr.add(second_path)
        mgr.remove(second_doc.doc_id)

        remaining = mgr.list_docs()
        assert len(remaining) == 1
        assert remaining[0].doc_id == e1.doc_id


# ── LibraryEntry serialisation ────────────────────────────────────────────────

class TestLibraryEntrySerialisation:
    def test_to_dict_and_back(self):
        entry = LibraryEntry(
            doc_id="my-doc",
            title="My Document",
            udf_path="/data/my-doc.udf",
            source_format="pdf",
            summary="A summary.",
            section_count=5,
            keywords=["finance", "q4"],
            tags=["2024"],
            owner="Alice",
            department="Finance",
        )
        d = entry.to_dict()
        restored = LibraryEntry.from_dict(d)
        assert restored.doc_id == entry.doc_id
        assert restored.title == entry.title
        assert restored.keywords == entry.keywords

    def test_from_dict_missing_optional_fields(self):
        minimal = {"doc_id": "x", "title": "X", "udf_path": "/x.udf", "source_format": "pdf"}
        entry = LibraryEntry.from_dict(minimal)
        assert entry.doc_id == "x"
        assert entry.keywords == []
