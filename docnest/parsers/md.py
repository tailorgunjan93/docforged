"""
Markdown parser — pure stdlib, no extra dependencies.

Walks ATX headings (# / ## / ###…) to build the section hierarchy.
Body text between headings is accumulated into each section's `text`.
Fenced code blocks, blockquotes, and lists are preserved as plain text.

Phase: 1  |  Spec: docs/SPEC_DOCNEST_PYPI.md — Section 10
"""

from __future__ import annotations
import re
from pathlib import Path

from docnest.parsers.base import IParser
from docnest.models import RawDocument, Section
from docnest.exceptions import ParseError

# Matches ATX headings:  ## My Title
_HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")


class MarkdownParser(IParser):
    """Parses Markdown files into structured sections.

    Uses a simple line-by-line ATX heading scan — no extra dependencies.
    Fenced code blocks are preserved verbatim inside section text.
    """

    def supports(self, file_path: str) -> bool:
        return file_path.lower().endswith((".md", ".markdown"))

    def parse(self, file_path: str) -> RawDocument:
        """Parse a Markdown file into a RawDocument."""
        path = Path(file_path)
        try:
            source_text = path.read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            raise ParseError(f"Cannot read {file_path}: {exc}") from exc

        doc_id = self._make_doc_id(file_path)
        sections: list[Section] = []
        current_title: str | None = None
        current_level: int = 0
        current_lines: list[str] = []
        doc_title: str = path.stem  # fallback title

        def _flush(title: str, level: int, lines: list[str]) -> None:
            text = "\n".join(lines).strip()
            sections.append(
                Section(
                    id="",            # assigned by Normaliser
                    title=title,
                    level=level,
                    text=text,
                    token_count=max(1, len(text.split())),
                )
            )

        in_fence = False
        for line in source_text.splitlines():
            # Track fenced code blocks — headings inside them are not headings
            stripped = line.strip()
            if stripped.startswith("```") or stripped.startswith("~~~"):
                in_fence = not in_fence

            if not in_fence:
                m = _HEADING_RE.match(line)
                if m:
                    # Save previous section
                    if current_title is not None:
                        _flush(current_title, current_level, current_lines)
                    else:
                        # Text before the first heading becomes a preamble section
                        if any(l.strip() for l in current_lines):
                            _flush(doc_id.replace("-", " ").title(), 1, current_lines)

                    current_level = len(m.group(1))
                    current_title = m.group(2)
                    current_lines = []

                    # Use the first H1 as the document title
                    if current_level == 1 and doc_title == path.stem:
                        doc_title = current_title
                    continue

            current_lines.append(line)

        # Flush last section
        if current_title is not None:
            _flush(current_title, current_level, current_lines)
        elif any(l.strip() for l in current_lines):
            # File has no headings at all — treat whole file as one section
            _flush(doc_title, 1, current_lines)

        if not sections:
            # Edge case: empty file
            sections.append(Section(id="", title=doc_title, level=1, text="", token_count=0))

        return RawDocument(
            doc_id=doc_id,
            title=doc_title,
            source=str(path.resolve()),
            format="md",
            sections=sections,
        )
