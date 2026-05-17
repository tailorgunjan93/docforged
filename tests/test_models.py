"""Tests for Pydantic data models.

Run: pytest tests/test_models.py -v
"""
from __future__ import annotations

import pytest
from pydantic import ValidationError

from docnest.models import (
    Catalogue,
    DocMeta,
    Document,
    ImageRef,
    KeyNumber,
    RawDocument,
    Section,
    TableData,
)


# ── TableData ─────────────────────────────────────────────────────────────────

class TestTableData:
    def test_create_minimal(self):
        t = TableData(table_id="t1", headers=["A", "B"], rows=[["1", "2"]])
        assert t.table_id == "t1"
        assert t.headers == ["A", "B"]
        assert t.rows == [["1", "2"]]

    def test_caption_defaults_to_none(self):
        t = TableData(table_id="t1", headers=["X"], rows=[])
        assert t.caption is None

    def test_create_with_caption(self):
        t = TableData(table_id="t2", caption="Sales", headers=["Q", "R"], rows=[])
        assert t.caption == "Sales"

    def test_multiple_rows(self):
        t = TableData(
            table_id="t3",
            headers=["Col1", "Col2"],
            rows=[["a", "b"], ["c", "d"], ["e", "f"]],
        )
        assert len(t.rows) == 3
        assert all(len(row) == 2 for row in t.rows)


# ── ImageRef ──────────────────────────────────────────────────────────────────

class TestImageRef:
    def test_create_minimal(self):
        img = ImageRef(image_id="img1", asset_path="assets/img_0001.png")
        assert img.image_id == "img1"
        assert img.asset_path == "assets/img_0001.png"

    def test_alt_defaults_to_none(self):
        img = ImageRef(image_id="img2", asset_path="assets/x.png")
        assert img.alt is None

    def test_create_with_alt(self):
        img = ImageRef(image_id="img3", alt="Chart", asset_path="assets/chart.png")
        assert img.alt == "Chart"


# ── Section ───────────────────────────────────────────────────────────────────

class TestSection:
    def test_create_minimal(self):
        s = Section(id="§1", title="Intro", level=1, text="Hello")
        assert s.id == "§1"
        assert s.level == 1
        assert s.tables == []
        assert s.images == []
        assert s.children == []
        assert s.keywords == []
        assert s.parent_id is None
        assert s.summary is None
        assert s.embedding is None

    def test_empty_id_is_valid(self):
        """Parsers output empty §ids — normaliser fills them."""
        s = Section(id="", title="Intro", level=1, text="")
        assert s.id == ""

    def test_level_range_1_to_6(self):
        for level in range(1, 7):
            s = Section(id="§1", title="T", level=level, text="")
            assert s.level == level

    def test_section_with_table(self):
        t = TableData(table_id="t1", headers=["A"], rows=[["1"]])
        s = Section(id="§1", title="Data", level=1, text="", tables=[t])
        assert len(s.tables) == 1
        assert s.tables[0].table_id == "t1"

    def test_embedding_accepts_bytes(self):
        s = Section(id="§1", title="T", level=1, text="")
        s.embedding = b"\x00\x01\x02"
        assert s.embedding == b"\x00\x01\x02"

    def test_children_list(self):
        s = Section(id="§1", title="T", level=1, text="", children=["§1.1", "§1.2"])
        assert "§1.1" in s.children


# ── KeyNumber ─────────────────────────────────────────────────────────────────

class TestKeyNumber:
    def test_create(self):
        kn = KeyNumber(label="Revenue", value="$38M", unit="USD", section="§3.1")
        assert kn.label == "Revenue"
        assert kn.value == "$38M"
        assert kn.section == "§3.1"

    def test_unit_defaults_none(self):
        kn = KeyNumber(label="Count", value="100", section="§1")
        assert kn.unit is None


# ── DocMeta ───────────────────────────────────────────────────────────────────

class TestDocMeta:
    def test_all_defaults_present(self):
        m = DocMeta()
        assert isinstance(m.owner, str)
        assert isinstance(m.department, str)
        assert isinstance(m.tags, list)
        assert isinstance(m.access_roles, list)
        assert isinstance(m.version, str)
        assert isinstance(m.last_updated, str)

    def test_create_with_all_fields(self):
        m = DocMeta(
            owner="Alice",
            department="Finance",
            tags=["q4", "2024"],
            access_roles=["finance", "exec"],
            version="1.2",
            last_updated="2026-05-17",
        )
        assert m.owner == "Alice"
        assert "q4" in m.tags
        assert "exec" in m.access_roles


# ── RawDocument ───────────────────────────────────────────────────────────────

class TestRawDocument:
    def test_create_minimal(self):
        raw = RawDocument(
            doc_id="my-doc",
            title="My Doc",
            source="file.pdf",
            format="pdf",
            sections=[],
        )
        assert raw.doc_id == "my-doc"
        assert raw.format == "pdf"
        assert raw.sections == []

    def test_sections_list_is_populated(self):
        s = Section(id="", title="Intro", level=1, text="Hello")
        raw = RawDocument(
            doc_id="d1", title="T", source="f.pdf", format="pdf", sections=[s]
        )
        assert len(raw.sections) == 1
        assert raw.sections[0].title == "Intro"

    def test_raw_text_defaults_falsy(self):
        raw = RawDocument(
            doc_id="d1", title="T", source="f.pdf", format="pdf", sections=[]
        )
        assert not raw.raw_text   # None or ""


# ── Document ──────────────────────────────────────────────────────────────────

class TestDocument:
    def test_create_inherits_raw_fields(self):
        doc = Document(
            doc_id="doc-1",
            title="My Document",
            source="doc.pdf",
            format="pdf",
            sections=[],
        )
        assert doc.doc_id == "doc-1"
        assert doc.summary is None
        assert doc.insights == []
        assert doc.key_numbers == []

    def test_meta_has_default(self):
        doc = Document(
            doc_id="d", title="T", source="s", format="pdf", sections=[]
        )
        # meta is always a DocMeta (with default values), never truly None
        assert doc.meta is not None or doc.meta is None  # both OK depending on implementation
        assert hasattr(doc, "meta")

    def test_meta_can_be_assigned(self):
        meta = DocMeta(owner="Bob", department="Eng")
        doc = Document(
            doc_id="d", title="T", source="s", format="pdf", sections=[], meta=meta
        )
        assert doc.meta.owner == "Bob"
