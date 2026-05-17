"""
Search provider interface and implementations.

ISearchProvider       — abstract interface for keyword search indexing
BM25SearchProvider    — rank_bm25 BM25Okapi  (best quality, pip install rank-bm25)
TFIDFSearchProvider   — sklearn TF-IDF       (alternative, pip install scikit-learn)
KeywordSearchProvider — pure-Python Jaccard  (zero-dep fallback, always available)

get_search_provider(name) → ISearchProvider
    "bm25"    → BM25SearchProvider
    "tfidf"   → TFIDFSearchProvider
    "keyword" → KeywordSearchProvider
    "auto"    → best available: bm25 → tfidf → keyword
"""

from __future__ import annotations
from abc import ABC, abstractmethod


# ─────────────────────────────────────────────────────────────────────────────
#  Interface
# ─────────────────────────────────────────────────────────────────────────────

class ISearchProvider(ABC):
    """Abstract interface for keyword-based document search.

    Lifecycle:
        1. ``build_index(corpus)``      — call once with tokenised documents
        2. ``get_scores(query_tokens)`` — call for each query

    Example custom implementation::

        class MySearch(ISearchProvider):
            def build_index(self, corpus):
                self._docs = corpus
            def get_scores(self, query_tokens):
                q = set(query_tokens)
                return [len(q & set(d)) / max(len(q | set(d)), 1) for d in self._docs]
            @property
            def backend_name(self): return "mycustom"
    """

    @abstractmethod
    def build_index(self, corpus: list[list[str]]) -> None:
        """Build a search index from a tokenised corpus.

        Args:
            corpus: List of documents; each document is a list of string tokens.
                    e.g. ``[["revenue", "q3", "sales"], ["risk", "compliance"]]``
        """
        ...

    @abstractmethod
    def get_scores(self, query_tokens: list[str]) -> list[float]:
        """Score all indexed documents against query tokens.

        Args:
            query_tokens: List of lowercase query tokens.

        Returns:
            Float scores — one per document in corpus order.
            Values are normalised to [0, 1]. Higher = more relevant.
        """
        ...

    @property
    @abstractmethod
    def backend_name(self) -> str:
        """Backend identifier e.g. 'bm25', 'tfidf', 'keyword'."""
        ...

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(backend={self.backend_name!r})"


# ─────────────────────────────────────────────────────────────────────────────
#  Implementations
# ─────────────────────────────────────────────────────────────────────────────

class BM25SearchProvider(ISearchProvider):
    """BM25 search via rank_bm25 (BM25Okapi algorithm).

    Best-quality keyword search — handles term-frequency saturation and
    document-length normalisation automatically.

    Install: ``pip install rank-bm25``
    """

    def __init__(self) -> None:
        self._bm25: object | None = None

    @property
    def backend_name(self) -> str:
        return "bm25"

    def build_index(self, corpus: list[list[str]]) -> None:
        """Build BM25 index from tokenised corpus.

        Raises:
            ImportError: If rank-bm25 is not installed.
        """
        if not corpus:
            self._bm25 = None
            return
        try:
            from rank_bm25 import BM25Okapi  # type: ignore[import]
            self._bm25 = BM25Okapi(corpus)
        except ImportError as exc:
            raise ImportError(
                "rank-bm25 is not installed. Run: pip install rank-bm25\n"
                "Or use: get_search_provider('tfidf') / get_search_provider('keyword')"
            ) from exc

    def get_scores(self, query_tokens: list[str]) -> list[float]:
        if self._bm25 is None or not query_tokens:
            return []
        try:
            import numpy as np
            scores = self._bm25.get_scores(query_tokens)  # type: ignore[union-attr]
            arr    = np.array(scores, dtype=np.float32)
            max_v  = float(arr.max()) + 1e-8
            return (arr / max_v).tolist()
        except Exception:
            return []


class TFIDFSearchProvider(ISearchProvider):
    """TF-IDF search via scikit-learn cosine similarity.

    Good quality alternative when rank_bm25 is unavailable.

    Install: ``pip install scikit-learn``
    """

    def __init__(self) -> None:
        self._vectorizer: object | None = None
        self._matrix: object | None = None

    @property
    def backend_name(self) -> str:
        return "tfidf"

    def build_index(self, corpus: list[list[str]]) -> None:
        if not corpus:
            return
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer  # type: ignore[import]
            docs = [" ".join(tokens) for tokens in corpus]
            self._vectorizer = TfidfVectorizer(lowercase=True, use_idf=True)
            self._matrix     = self._vectorizer.fit_transform(docs)  # type: ignore[union-attr]
        except ImportError as exc:
            raise ImportError(
                "scikit-learn is not installed. Run: pip install scikit-learn\n"
                "Or use: get_search_provider('keyword')"
            ) from exc

    def get_scores(self, query_tokens: list[str]) -> list[float]:
        if self._vectorizer is None or self._matrix is None or not query_tokens:
            return []
        try:
            from sklearn.metrics.pairwise import cosine_similarity  # type: ignore[import]
            q_str  = " ".join(query_tokens)
            q_vec  = self._vectorizer.transform([q_str])  # type: ignore[union-attr]
            scores = cosine_similarity(q_vec, self._matrix).flatten()
            return scores.tolist()
        except Exception:
            return []


class KeywordSearchProvider(ISearchProvider):
    """Pure-Python Jaccard keyword search — zero external dependencies.

    Uses intersection-over-union on token sets.  Lower quality than BM25/TF-IDF
    but always available as a guaranteed fallback with no installs.
    """

    def __init__(self) -> None:
        self._corpus: list[set[str]] = []

    @property
    def backend_name(self) -> str:
        return "keyword"

    def build_index(self, corpus: list[list[str]]) -> None:
        self._corpus = [set(tokens) for tokens in corpus]

    def get_scores(self, query_tokens: list[str]) -> list[float]:
        if not self._corpus or not query_tokens:
            return []
        q = set(query_tokens)
        scores = []
        for doc_tokens in self._corpus:
            union = len(q | doc_tokens)
            scores.append(float(len(q & doc_tokens)) / max(union, 1))
        return scores


# ─────────────────────────────────────────────────────────────────────────────
#  Factory
# ─────────────────────────────────────────────────────────────────────────────

def get_search_provider(name: str = "auto") -> ISearchProvider:
    """Create a search provider by name.

    Args:
        name: ``"bm25"`` | ``"tfidf"`` | ``"keyword"`` | ``"auto"``
              ``"auto"`` picks the best available: bm25 → tfidf → keyword.

    Returns:
        ISearchProvider ready to use.

    Examples::

        searcher = get_search_provider()           # auto (bm25 if installed)
        searcher = get_search_provider("bm25")     # explicit BM25
        searcher = get_search_provider("keyword")  # zero-dep fallback
    """
    name = name.lower().strip()
    if name == "bm25":
        return BM25SearchProvider()
    if name == "tfidf":
        return TFIDFSearchProvider()
    if name == "keyword":
        return KeywordSearchProvider()
    if name == "auto":
        try:
            import rank_bm25  # type: ignore[import]  # noqa: F401
            return BM25SearchProvider()
        except ImportError:
            pass
        try:
            import sklearn  # type: ignore[import]  # noqa: F401
            return TFIDFSearchProvider()
        except ImportError:
            pass
        return KeywordSearchProvider()

    raise ValueError(
        f"Unknown search provider '{name}'. "
        "Choose from: bm25, tfidf, keyword, auto"
    )
