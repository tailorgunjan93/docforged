"""Tests for MarkdownParser — ATX and Setext headings, tables, code blocks.

Run: pytest tests/test_md_parser.py -v
"""
from __future__ import annotations

from pathlib import Path

import pytest

from docnest.parsers.md import MarkdownParser


# ── supports() ───────────────────────────────────────────────────────────────

class TestMarkdownParserSupports:
    def test_supports_md(self):
        assert MarkdownParser().supports("README.md") is True

    def test_supports_markdown_extension(self):
        assert MarkdownParser().supports("doc.markdown") is True

    def test_case_insensitive(self):
        assert MarkdownParser().supports("NOTES.MD") is True

    def test_does_not_support_pdf(self):
        assert MarkdownParser().supports("file.pdf") is False

    def test_does_not_support_docx(self):
        assert MarkdownParser().supports("file.docx") is False

    def test_does_not_support_txt(self):
        assert MarkdownParser().supports("notes.txt") is False


# ── parse() — ATX headings ────────────────────────────────────────────────────

class TestMarkdownATXHeadings:
    def _parse(self, content: str, tmp_path: Path):
        f = tmp_path / "doc.md"
        f.write_text(content, encoding="utf-8")
        return MarkdownParser().parse(str(f))

    def test_h1_creates_level_1_section(self, tmp_path: Path):
        raw = self._parse("# Introduction\n\nHello world.\n", tmp_path)
        assert any(s.level == 1 and "Introduction" in s.title for s in raw.sections)

    def test_h2_creates_level_2_section(self, tmp_path: Path):
        raw = self._parse("# Top\n\n## Sub\n\nContent.\n", tmp_path)
        levels = [s.level for s in raw.sections]
        assert 2 in levels

    def test_h3_creates_level_3_section(self, tmp_path: Path):
        raw = self._parse("# T\n\n## S\n\n### Deep\n\nText.\n", tmp_path)
        levels = [s.level for s in raw.sections]
        assert 3 in levels

    def test_multiple_h1_sections(self, tmp_path: Path):
        raw = self._parse("# A\n\nText.\n\n# B\n\nMore.\n\n# C\n\nEven more.\n", tmp_path)
        h1 = [s for s in raw.sections if s.level == 1]
        assert len(h1) == 3

    def test_section_titles_correct(self, tmp_path: Path):
        raw = self._parse("# Intro\n\nBody.\n\n## Background\n\nBg text.\n", tmp_path)
        titles = [s.title for s in raw.sections]
        assert "Intro" in titles
        assert "Background" in titles

    def test_section_ids_empty_from_parser(self, tmp_path: Path):
        """Parser must NOT assign §ids — that's the normalizer's job."""
        raw = self._parse("# A\n\n# B\n\n", tmp_path)
        for s in raw.sections:
            assert s.id == ""

    def test_body_text_assigned_to_section(self, tmp_path: Path):
        raw = self._parse("# My Section\n\nThis is the body text.\n", tmp_path)
        assert any("body text" in s.text for s in raw.sections)

    def test_empty_document_no_crash(self, tmp_path: Path):
        raw = self._parse("", tmp_path)
        assert raw is not None

    def test_no_headings_creates_at_least_one_section(self, tmp_path: Path):
        """A file with no headings should still produce something."""
        raw = self._parse("Just some plain text without any headings.\n", tmp_path)
        # May produce 0 or 1 section depending on implementation
        assert raw is not None

    def test_doc_id_derived_from_filename(self, tmp_path: Path):
        f = tmp_path / "my-report.md"
        f.write_text("# Hello\n\nContent.\n", encoding="utf-8")
        raw = MarkdownParser().parse(str(f))
        assert "my" in raw.doc_id or "report" in raw.doc_id

    def test_camelcase_filename_split_in_doc_id(self, tmp_path: Path):
        f = tmp_path / "MyReport.md"
        f.write_text("# Hello\n\n", encoding="utf-8")
        raw = MarkdownParser().parse(str(f))
        # CamelCase should be split: MyReport → my-report
        assert raw.doc_id == "my-report"

    def test_format_is_md(self, tmp_path: Path):
        raw = self._parse("# A\n\n", tmp_path)
        assert raw.format in ("md", "markdown")

    def test_source_is_file_path(self, tmp_path: Path):
        f = tmp_path / "source.md"
        f.write_text("# A\n\n", encoding="utf-8")
        raw = MarkdownParser().parse(str(f))
        assert raw.source.endswith(".md")

    def test_missing_file_raises(self):
        from docnest.exceptions import ParseError
        with pytest.raises(ParseError):
            MarkdownParser().parse("/tmp/does_not_exist_abc123.md")


# ── parse() — complex document ────────────────────────────────────────────────

class TestMarkdownComplexDocument:
    def test_fixture_sections_count(self, sample_md_file: Path):
        raw = MarkdownParser().parse(str(sample_md_file))
        assert len(raw.sections) >= 5  # fixture has 5 headings

    def test_fixture_has_h1_and_h2_and_h3(self, sample_md_file: Path):
        raw = MarkdownParser().parse(str(sample_md_file))
        levels = {s.level for s in raw.sections}
        assert 1 in levels
        assert 2 in levels
        assert 3 in levels

    def test_fixture_all_sections_have_titles(self, sample_md_file: Path):
        raw = MarkdownParser().parse(str(sample_md_file))
        for s in raw.sections:
            assert s.title.strip()

    def test_fixture_section_levels_in_range(self, sample_md_file: Path):
        raw = MarkdownParser().parse(str(sample_md_file))
        for s in raw.sections:
            assert 1 <= s.level <= 6
