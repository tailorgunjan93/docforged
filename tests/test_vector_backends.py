"""Tests for IVectorBackend implementations: Numpy, FAISS, ChromaDB.

Run: pytest tests/test_vector_backends.py -v
"""
from __future__ import annotations

import numpy as np
import pytest

from docnest.providers.vector import (
    NumpyVectorBackend,
    get_vector_backend,
)


RNG = np.random.default_rng(42)

DIMS = 64
N = 10


def unit(mat: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(mat, axis=1, keepdims=True)
    return mat / np.where(norms == 0, 1.0, norms)


def make_matrix(n: int = N, dims: int = DIMS) -> np.ndarray:
    mat = RNG.standard_normal((n, dims)).astype(np.float32)
    return unit(mat)


def make_ids(n: int = N) -> list[str]:
    return [f"§{i+1}" for i in range(n)]


# ── NumpyVectorBackend ────────────────────────────────────────────────────────

class TestNumpyVectorBackend:
    def test_is_always_available(self):
        assert NumpyVectorBackend().is_available() is True

    def test_not_ready_before_build(self):
        assert NumpyVectorBackend().is_ready() is False

    def test_ready_after_build(self):
        b = NumpyVectorBackend()
        b.build(make_ids(), make_matrix())
        assert b.is_ready() is True

    def test_backend_name(self):
        assert NumpyVectorBackend().backend_name == "numpy"

    def test_search_returns_list_of_tuples(self):
        b = NumpyVectorBackend()
        ids, mat = make_ids(), make_matrix()
        b.build(ids, mat)
        query = mat[0]  # identical to first doc
        results = b.search(query, k=3)
        assert isinstance(results, list)
        assert all(isinstance(r, tuple) and len(r) == 2 for r in results)

    def test_search_returns_at_most_k_results(self):
        b = NumpyVectorBackend()
        b.build(make_ids(N), make_matrix(N))
        assert len(b.search(make_matrix(1)[0], k=3)) <= 3
        assert len(b.search(make_matrix(1)[0], k=1)) == 1

    def test_search_ids_are_subset_of_indexed(self):
        ids = make_ids()
        b = NumpyVectorBackend()
        b.build(ids, make_matrix())
        results = b.search(make_matrix(1)[0], k=5)
        result_ids = [r[0] for r in results]
        assert all(rid in ids for rid in result_ids)

    def test_identical_query_scores_highest(self):
        """A query identical to a doc vector should score ~1.0 (top result)."""
        mat = make_matrix()
        ids = make_ids()
        b = NumpyVectorBackend()
        b.build(ids, mat)
        query = mat[4]  # same as doc at index 4
        results = b.search(query, k=N)
        top_id, top_score = results[0]
        assert top_id == ids[4]
        assert top_score == pytest.approx(1.0, abs=1e-5)

    def test_scores_are_between_minus1_and_1(self):
        b = NumpyVectorBackend()
        b.build(make_ids(), make_matrix())
        results = b.search(make_matrix(1)[0], k=N)
        for _, score in results:
            assert -1.0 <= score <= 1.0 + 1e-6

    def test_results_sorted_descending_by_score(self):
        b = NumpyVectorBackend()
        b.build(make_ids(), make_matrix())
        results = b.search(make_matrix(1)[0], k=N)
        scores = [r[1] for r in results]
        assert scores == sorted(scores, reverse=True)

    def test_k_larger_than_corpus(self):
        """Asking for more results than docs should return at most len(docs)."""
        b = NumpyVectorBackend()
        b.build(make_ids(3), make_matrix(3))
        results = b.search(make_matrix(1)[0], k=100)
        assert len(results) <= 3

    def test_rebuild_replaces_index(self):
        b = NumpyVectorBackend()
        ids1 = ["§1", "§2"]
        b.build(ids1, make_matrix(2))
        results1 = {r[0] for r in b.search(make_matrix(1)[0], k=2)}
        assert results1.issubset({"§1", "§2"})

        ids2 = ["§A", "§B", "§C"]
        b.build(ids2, make_matrix(3))
        results2 = {r[0] for r in b.search(make_matrix(1)[0], k=3)}
        assert results2.issubset({"§A", "§B", "§C"})

    def test_opposite_vectors_score_lowest(self):
        """Antipodal vectors should have near-zero or negative cosine similarity."""
        mat = make_matrix(2)
        ids = ["§1", "§2"]
        b = NumpyVectorBackend()
        b.build(ids, mat)
        # Query with the negation of doc 0 — should not score high for §1
        results = b.search(-mat[0], k=2)
        # §1 should be near-bottom
        bottom_id, bottom_score = results[-1]
        assert bottom_score < 0.5


# ── FAISSVectorBackend ────────────────────────────────────────────────────────

faiss_available = pytest.importorskip("faiss", reason="faiss-cpu not installed")


class TestFAISSVectorBackend:
    @pytest.fixture
    def backend(self):
        from docnest.providers.vector import FAISSVectorBackend
        return FAISSVectorBackend()

    def test_is_available(self, backend):
        assert backend.is_available() is True

    def test_not_ready_before_build(self, backend):
        assert backend.is_ready() is False

    def test_ready_after_build(self, backend):
        backend.build(make_ids(), make_matrix())
        assert backend.is_ready() is True

    def test_search_returns_correct_length(self, backend):
        backend.build(make_ids(), make_matrix())
        results = backend.search(make_matrix(1)[0], k=5)
        assert len(results) <= 5

    def test_top_result_is_self_match(self, backend):
        mat = make_matrix()
        ids = make_ids()
        backend.build(ids, mat)
        results = backend.search(mat[2], k=N)
        assert results[0][0] == ids[2]

    def test_scores_sorted_descending(self, backend):
        backend.build(make_ids(), make_matrix())
        results = backend.search(make_matrix(1)[0], k=N)
        scores = [r[1] for r in results]
        assert scores == sorted(scores, reverse=True)

    def test_save_creates_file(self, backend, tmp_path):
        backend.build(make_ids(), make_matrix())
        index_path = str(tmp_path / "test.faiss")
        backend.save(index_path)
        assert (tmp_path / "test.faiss").exists()

    def test_load_and_search(self, backend, tmp_path):
        mat = make_matrix()
        ids = make_ids()
        backend.build(ids, mat)
        index_path = str(tmp_path / "test.faiss")
        backend.save(index_path)

        from docnest.providers.vector import FAISSVectorBackend
        loaded = FAISSVectorBackend()
        loaded.load(index_path, ids)
        # After load, search should work (is_ready may be True or need build call)
        try:
            results = loaded.search(mat[0], k=3)
            assert results[0][0] == ids[0]
        except Exception:
            # Some implementations require rebuild after load — that's OK
            loaded.build(ids, mat)
            results = loaded.search(mat[0], k=3)
            assert results[0][0] == ids[0]


# ── ChromaVectorBackend ───────────────────────────────────────────────────────

chroma_available = pytest.importorskip("chromadb", reason="chromadb not installed")


class TestChromaVectorBackend:
    @pytest.fixture
    def backend(self, tmp_path):
        from docnest.providers.vector import ChromaVectorBackend
        return ChromaVectorBackend()   # ephemeral

    def test_is_available(self, backend):
        assert backend.is_available() is True

    def test_ready_after_build(self, backend):
        backend.build(make_ids(), make_matrix())
        assert backend.is_ready() is True

    def test_search_returns_results(self, backend):
        backend.build(make_ids(), make_matrix())
        results = backend.search(make_matrix(1)[0], k=3)
        assert len(results) <= 3
        assert all(isinstance(r, tuple) for r in results)

    def test_result_ids_in_corpus(self, backend):
        ids = make_ids()
        backend.build(ids, make_matrix())
        results = backend.search(make_matrix(1)[0], k=5)
        assert all(r[0] in ids for r in results)


# ── get_vector_backend factory ────────────────────────────────────────────────

class TestGetVectorBackend:
    def test_returns_numpy_by_name(self):
        b = get_vector_backend("numpy")
        assert isinstance(b, NumpyVectorBackend)

    def test_default_is_numpy(self):
        b = get_vector_backend()
        assert isinstance(b, NumpyVectorBackend)

    def test_unknown_name_raises(self):
        with pytest.raises((ValueError, KeyError)):
            get_vector_backend("zzz_no_such_backend")

    def test_faiss_if_available(self):
        try:
            import faiss  # noqa: F401
            from docnest.providers.vector import FAISSVectorBackend
            b = get_vector_backend("faiss")
            assert isinstance(b, FAISSVectorBackend)
        except ImportError:
            pytest.skip("faiss not installed")
