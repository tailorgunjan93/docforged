"""Tests for ISearchProvider implementations: BM25, TF-IDF, Keyword.

Run: pytest tests/test_search_providers.py -v
"""
from __future__ import annotations

import pytest

from docnest.providers.search import (
    BM25SearchProvider,
    KeywordSearchProvider,
    TFIDFSearchProvider,
    get_search_provider,
)


# ── Shared corpus ─────────────────────────────────────────────────────────────

CORPUS = [
    ["revenue", "quarterly", "growth", "finance"],
    ["machine", "learning", "model", "training", "neural"],
    ["customer", "satisfaction", "feedback", "survey", "nps"],
    ["revenue", "annual", "report", "finance", "budget"],
    ["engineering", "architecture", "deployment", "kubernetes"],
]


def build(provider, corpus=CORPUS):
    provider.build_index(corpus)
    return provider


# ── KeywordSearchProvider ─────────────────────────────────────────────────────

class TestKeywordSearchProvider:
    def test_backend_name(self):
        assert KeywordSearchProvider().backend_name == "keyword"

    def test_returns_scores_same_length_as_corpus(self):
        p = build(KeywordSearchProvider())
        scores = p.get_scores(["revenue"])
        assert len(scores) == len(CORPUS)

    def test_exact_match_has_positive_score(self):
        p = build(KeywordSearchProvider())
        scores = p.get_scores(["revenue"])
        # Docs 0 and 3 contain "revenue"
        assert scores[0] > 0
        assert scores[3] > 0

    def test_no_match_returns_zero(self):
        p = build(KeywordSearchProvider())
        scores = p.get_scores(["zzznomatch"])
        assert all(s == 0 for s in scores)

    def test_scores_are_non_negative(self):
        p = build(KeywordSearchProvider())
        scores = p.get_scores(["machine", "learning"])
        assert all(s >= 0 for s in scores)

    def test_better_match_scores_higher(self):
        p = build(KeywordSearchProvider())
        scores = p.get_scores(["machine", "learning", "neural"])
        # Doc 1 has all three terms — should rank highest
        assert scores[1] == max(scores)

    def test_empty_query_returns_zeros(self):
        p = build(KeywordSearchProvider())
        scores = p.get_scores([])
        assert all(s == 0 for s in scores)

    def test_empty_corpus(self):
        p = KeywordSearchProvider()
        p.build_index([])
        scores = p.get_scores(["anything"])
        assert scores == []


# ── BM25SearchProvider ────────────────────────────────────────────────────────

class TestBM25SearchProvider:
    def test_backend_name(self):
        assert BM25SearchProvider().backend_name == "bm25"

    def test_returns_scores_same_length_as_corpus(self):
        p = build(BM25SearchProvider())
        scores = p.get_scores(["revenue"])
        assert len(scores) == len(CORPUS)

    def test_exact_match_scores_positive(self):
        p = build(BM25SearchProvider())
        scores = p.get_scores(["machine", "learning"])
        assert scores[1] > 0

    def test_non_matching_doc_scores_lower_than_matching(self):
        p = build(BM25SearchProvider())
        scores = p.get_scores(["machine", "learning"])
        assert scores[1] > scores[2]

    def test_scores_are_non_negative(self):
        p = build(BM25SearchProvider())
        assert all(s >= 0 for s in p.get_scores(["revenue"]))

    def test_best_match_is_top_scorer(self):
        p = build(BM25SearchProvider())
        scores = p.get_scores(["machine", "learning", "model", "neural"])
        # Doc 1 has 4 of those 4 terms
        assert scores[1] == max(scores)

    def test_empty_query(self):
        p = build(BM25SearchProvider())
        scores = p.get_scores([])
        assert all(s == 0 for s in scores)

    def test_rebuild_resets_index(self):
        p = BM25SearchProvider()
        p.build_index(CORPUS)
        scores_before = p.get_scores(["revenue"])

        new_corpus = [["revenue", "x"], ["y", "z"]]
        p.build_index(new_corpus)
        scores_after = p.get_scores(["revenue"])
        assert len(scores_after) == 2   # new corpus has 2 docs


# ── TFIDFSearchProvider ───────────────────────────────────────────────────────

class TestTFIDFSearchProvider:
    def test_backend_name(self):
        p = TFIDFSearchProvider()
        assert "tfidf" in p.backend_name.lower() or p.backend_name == "keyword"

    def test_returns_correct_length(self):
        p = build(TFIDFSearchProvider())
        assert len(p.get_scores(["revenue"])) == len(CORPUS)

    def test_non_negative_scores(self):
        p = build(TFIDFSearchProvider())
        assert all(s >= 0 for s in p.get_scores(["engineering", "kubernetes"]))

    def test_best_match_scores_highest(self):
        p = build(TFIDFSearchProvider())
        scores = p.get_scores(["customer", "satisfaction", "nps"])
        assert scores[2] == max(scores)


# ── get_search_provider factory ───────────────────────────────────────────────

class TestGetSearchProvider:
    def test_returns_bm25_by_name(self):
        p = get_search_provider("bm25")
        assert isinstance(p, BM25SearchProvider)

    def test_returns_tfidf_by_name(self):
        p = get_search_provider("tfidf")
        assert isinstance(p, (TFIDFSearchProvider, KeywordSearchProvider))

    def test_returns_keyword_by_name(self):
        p = get_search_provider("keyword")
        assert isinstance(p, KeywordSearchProvider)

    def test_auto_returns_something(self):
        p = get_search_provider("auto")
        assert p is not None
        assert hasattr(p, "get_scores")

    def test_unknown_falls_back_or_raises(self):
        """Unknown provider should either fall back or raise ValueError."""
        try:
            p = get_search_provider("zzznobody")
            # If it doesn't raise, it must still be usable
            assert hasattr(p, "get_scores")
        except (ValueError, KeyError):
            pass  # acceptable
