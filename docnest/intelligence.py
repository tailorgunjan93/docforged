"""
Intelligence Engine — Stages 4 and 5 of the DocNest pipeline.

Uses an LLM (via LangChain) to enrich documents with:
  Stage 4: One-sentence summary + keywords per section
  Stage 5: Document-level summary, insights[], key_numbers[]

LLM calls happen ONCE per document at ingest time.
Every future query benefits for free — zero extra tokens per query.

LLM provider is fully pluggable — swap provider+model, nothing else changes:
    engine = IntelligenceEngine(provider="groq",      model="llama-3.3-70b-versatile")
    engine = IntelligenceEngine(provider="openai",    model="gpt-4o-mini")
    engine = IntelligenceEngine(provider="ollama",    model="llama3.2")
    engine = IntelligenceEngine(provider="anthropic", model="claude-3-haiku-20240307")
    engine = IntelligenceEngine(provider="google",    model="gemini-1.5-flash")
    engine = IntelligenceEngine(provider="bedrock",   model="amazon.titan-text-lite-v1")

See docnest/llm.py for the full provider list.

Phase: 3  |  Spec: docs/SPEC_DOCNEST_PYPI.md — Section 10
"""

from __future__ import annotations
import json
import re
from typing import Any

from docnest.models import Document, Section, KeyNumber
from docnest.exceptions import IntelligenceError
from docnest.providers.llm import ILLMProvider, get_llm_provider

# System prompt used for all intelligence calls
_SYSTEM = (
    "You are a precise document analyst. "
    "Return ONLY the requested format — no preamble, no explanation."
)

# Max chars to send per section (keeps cost low, avoids context overflow)
_MAX_SECTION_CHARS = 2000
# Max chars of combined summaries to send for document-level enrichment
_MAX_DOC_CONTEXT_CHARS = 8000


class IntelligenceEngine:
    """LLM-powered document enrichment via LangChain.

    Supports any LLM provider through LangChain's unified interface:
        groq      — fast cloud, free tier (default)
        openai    — highest quality
        ollama    — fully local, free (needs Ollama running)
        anthropic — Claude models
        google    — Gemini models
        bedrock   — AWS Bedrock
        ... and more (see docnest/llm.py)

    Usage:
        engine = IntelligenceEngine(provider="groq", model="llama-3.3-70b-versatile")
        doc = engine.enrich_sections(doc)   # Stage 4: per-section summaries
        doc = engine.enrich_document(doc)   # Stage 5: doc-level intelligence
    """

    def __init__(
        self,
        provider: str | ILLMProvider = "groq",
        model: str = "llama-3.3-70b-versatile",
        api_key: str | None = None,
        **llm_kwargs: object,
    ) -> None:
        """Initialise the intelligence engine.

        Accepts either an ``ILLMProvider`` instance (preferred) or the legacy
        ``(provider, model, api_key)`` string config (backward-compatible).

        Args:
            provider:     ILLMProvider instance  **or**  provider name string
                          (groq, openai, ollama, anthropic, google, …).
            model:        Model identifier — ignored when ``provider`` is an
                          ILLMProvider instance.
            api_key:      API key — optional, falls back to provider's env var.
                          Ignored when ``provider`` is an ILLMProvider instance.
            **llm_kwargs: Extra kwargs forwarded when building a new provider.
        """
        if isinstance(provider, ILLMProvider):
            # Caller passed a fully-constructed provider object
            self._llm: ILLMProvider = provider
        else:
            # Backward-compatible string config
            self._llm = get_llm_provider(provider, model, api_key=api_key, **llm_kwargs)

        # Keep public attrs for introspection / backward compat
        self.provider = self._llm.provider_name
        self.model    = self._llm.model_name
        self.api_key  = api_key
        self._llm_kwargs = llm_kwargs

    # ------------------------------------------------------------------ #
    #  Public API                                                          #
    # ------------------------------------------------------------------ #

    def enrich_sections(self, doc: Document) -> Document:
        """Stage 4: Generate one-sentence summary + keywords per section.

        Skips sections with fewer than 20 words (too short to summarise).

        Args:
            doc: Document with normalised sections.

        Returns:
            Document with section.summary and section.keywords filled.
        """
        for section in doc.sections:
            if len(section.text.split()) < 20:
                section.summary = section.title
                section.keywords = section.title.lower().split()[:5]
                continue
            try:
                section.summary = self._summarise_section(section)
                section.keywords = self._extract_keywords(section)
            except IntelligenceError:
                # Graceful degradation — skip enrichment for this section
                section.summary = section.title
                section.keywords = []
        return doc

    def enrich_document(self, doc: Document) -> Document:
        """Stage 5: Generate document-level summary, insights, key_numbers.

        Builds a compressed context from all section summaries (not full text)
        to keep LLM costs low, then requests JSON output.

        Args:
            doc: Document with section summaries already filled.

        Returns:
            Document with summary, insights, and key_numbers populated.
        """
        context = self._build_doc_context(doc)
        try:
            result = self._call_doc_intelligence(context, doc.title)
            doc.summary = result.get("summary", "")
            doc.insights = result.get("insights", [])
            raw_kn = result.get("key_numbers", [])
            doc.key_numbers = [
                KeyNumber(
                    label=kn.get("label", ""),
                    value=kn.get("value", ""),
                    unit=kn.get("unit"),
                    section=kn.get("section", "§1"),
                )
                for kn in raw_kn
                if kn.get("label") and kn.get("value")
            ]
        except IntelligenceError:
            doc.summary = f"Document: {doc.title}"
            doc.insights = []
            doc.key_numbers = []
        return doc

    # ------------------------------------------------------------------ #
    #  Private helpers                                                     #
    # ------------------------------------------------------------------ #

    def _summarise_section(self, section: Section) -> str:
        """Generate a one-sentence summary of a section."""
        text = section.text[:_MAX_SECTION_CHARS]
        prompt = (
            f"Summarise the following section titled '{section.title}' "
            f"in exactly ONE sentence (max 150 characters):\n\n{text}"
        )
        return self._call_llm(prompt).strip()[:200]

    def _extract_keywords(self, section: Section) -> list[str]:
        """Extract 5-8 BM25 index keywords from a section."""
        text = (section.summary or section.title) + " " + section.text[:500]
        prompt = (
            f"Extract 5 to 8 important keywords from this text for a search index. "
            f"Return ONLY a JSON array of lowercase strings, e.g. [\"revenue\", \"q3\"]:\n\n{text}"
        )
        raw = self._call_llm(prompt).strip()
        try:
            keywords = json.loads(_extract_json(raw))
            if isinstance(keywords, list):
                return [str(k).lower() for k in keywords[:10]]
        except Exception:
            pass
        # Fallback: split summary into words
        return [w.lower() for w in (section.summary or section.title).split()[:6]]

    def _build_doc_context(self, doc: Document) -> str:
        """Build a compressed context string from section summaries."""
        parts = [f"Document: {doc.title}\n"]
        total = len(parts[0])
        for section in doc.sections:
            line = f"{section.id} {section.title}: {section.summary or section.text[:100]}\n"
            if total + len(line) > _MAX_DOC_CONTEXT_CHARS:
                break
            parts.append(line)
            total += len(line)
        return "".join(parts)

    def _call_doc_intelligence(self, context: str, title: str) -> dict[str, Any]:
        """Call LLM for document-level intelligence. Returns parsed JSON dict."""
        prompt = (
            f"Analyse this document summary and return a JSON object with exactly these fields:\n"
            f'{{"summary": "3-sentence summary", '
            f'"insights": ["finding1", "finding2", "finding3"], '
            f'"key_numbers": [{{"label": "Revenue", "value": "$142M", "unit": "USD", "section": "§2.1"}}]}}\n\n'
            f"Document sections:\n{context}"
        )
        raw = self._call_llm(prompt)
        try:
            return json.loads(_extract_json(raw))
        except Exception as exc:
            raise IntelligenceError(
                f"Failed to parse document intelligence JSON: {exc}\nRaw: {raw[:200]}"
            ) from exc

    def _call_llm(self, prompt: str) -> str:
        """Call the configured ILLMProvider.

        Args:
            prompt: User message.

        Returns:
            LLM response text.

        Raises:
            IntelligenceError: If the provider package is not installed,
                               the API key is missing, or the call fails.
        """
        return self._llm.complete(prompt=prompt, system=_SYSTEM)


# ======================================================================
#  Utility
# ======================================================================

def _extract_json(text: str) -> str:
    """Extract the first JSON object or array from an LLM response string."""
    # Try to find JSON wrapped in code block
    m = re.search(r"```(?:json)?\s*([\[{].*?)\s*```", text, re.DOTALL)
    if m:
        return m.group(1)
    # Try to find raw JSON object or array
    m = re.search(r"([\[{].*[\]}])", text, re.DOTALL)
    if m:
        return m.group(1)
    return text.strip()
