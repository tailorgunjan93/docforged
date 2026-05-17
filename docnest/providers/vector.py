"""
Vector search backend interface and implementations.

IVectorBackend          — abstract interface for vector similarity search
NumpyVectorBackend      — pure NumPy brute-force cosine (default, zero deps)
FAISSVectorBackend      — FAISS IndexFlatIP (fast ANN, needs faiss-cpu)
ChromaVectorBackend     — ChromaDB ephemeral/persistent (needs chromadb)

get_vector_backend(name, **kwargs) → IVectorBackend
    "numpy"  → NumpyVectorBackend   (default, always available)
    "faiss"  → FAISSVectorBackend   (requires: pip install faiss-cpu)
    "chroma" → ChromaVectorBackend  (requires: pip install chromadb)

Design notes
------------
All backends share the same two-step lifecycle:

    1.  backend.build(section_ids, matrix)
            Called once per archive open (lazy — only on first search).
            matrix shape: (N, dims), dtype float32.

    2.  backend.search(query_vec, k) → [(section_id, score), ...]
            Returns up to k (section_id, cosine_score) pairs, highest first.
            Scores are normalised to [0, 1].

The reader calls build() the first time _hybrid_search() is triggered,
then caches the backend for all subsequent searches on the same archive.

Choosing a backend
------------------
    • numpy   — correct for almost all use-cases: per-document search is
                brute-force O(N·D) but N is typically < 200; numpy matrix
                multiply beats FAISS overhead below ~10,000 vectors.

    • faiss   — right choice for a library-level merged index across
                thousands of documents (> ~500 docs, > ~10,000 vectors).
                Gives approximate nearest-neighbour in O(N^0.5·D) time.

    • chroma  — right choice when you need metadata-filtered search
                (e.g. "search only documents where department=Finance").
                Persistent: keeps the index on disk across restarts.
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import Any

import numpy as np

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
#  Interface
# ─────────────────────────────────────────────────────────────────────────────

class IVectorBackend(ABC):
    """Abstract interface for vector similarity search.

    Implement this to add a new ANN / vector-DB backend without touching
    any reader or search code.

    Example custom implementation::

        class MyVectorBackend(IVectorBackend):
            def build(self, ids, matrix): ...
            def search(self, query, k): ...
            @property
            def backend_name(self): return "mybackend"
            @staticmethod
            def is_available(): return True
    """

    @abstractmethod
    def build(self, section_ids: list[str], matrix: np.ndarray) -> None:
        """Index a matrix of section embeddings.

        Args:
            section_ids: List of §id strings, parallel to matrix rows.
            matrix:      Float32 array of shape (N, dims).

        Called once per archive open (lazily on first search).
        """
        ...

    @abstractmethod
    def search(
        self,
        query_vec: np.ndarray,
        k: int,
    ) -> list[tuple[str, float]]:
        """Return the top-k most similar sections.

        Args:
            query_vec: 1-D float32 query embedding.
            k:         Maximum number of results to return.

        Returns:
            List of (section_id, cosine_score) tuples, highest score first.
            Scores are in [0, 1].  May return fewer than k results.
        """
        ...

    @property
    @abstractmethod
    def backend_name(self) -> str:
        """Short identifier, e.g. 'numpy', 'faiss', 'chroma'."""
        ...

    @staticmethod
    def is_available() -> bool:
        """Return True if the required dependencies are installed."""
        return True

    def is_ready(self) -> bool:
        """Return True after build() has been called successfully."""
        return self._ready  # type: ignore[attr-defined]

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(backend={self.backend_name!r})"


# ─────────────────────────────────────────────────────────────────────────────
#  NumPy — default, zero extra dependencies
# ─────────────────────────────────────────────────────────────────────────────

class NumpyVectorBackend(IVectorBackend):
    """Brute-force cosine similarity using NumPy matrix multiply.

    Best for:
        - Per-document search (always — even 1,000 sections < 5ms)
        - Library of up to ~500 documents / ~10,000 sections
        - Zero-dependency environments

    How it works:
        build()  → L2-normalise all row vectors, store unit matrix
        search() → unit_mat @ unit_q  (single BLAS GEMV call, O(N·D))

    No extra install required.
    """

    def __init__(self) -> None:
        self._ids: list[str] = []
        self._unit_mat: np.ndarray | None = None
        self._ready = False

    @property
    def backend_name(self) -> str:
        return "numpy"

    @staticmethod
    def is_available() -> bool:
        return True   # numpy is always present

    def build(self, section_ids: list[str], matrix: np.ndarray) -> None:
        self._ids = list(section_ids)
        # Pre-normalise rows so search is a plain dot-product
        norms = np.linalg.norm(matrix, axis=1, keepdims=True)
        norms = np.where(norms == 0, 1.0, norms)
        self._unit_mat = (matrix / norms).astype(np.float32)
        self._ready = True
        logger.debug("NumpyVectorBackend: indexed %d vectors (dims=%d)",
                     len(section_ids), matrix.shape[1])

    def search(self, query_vec: np.ndarray, k: int) -> list[tuple[str, float]]:
        if self._unit_mat is None or not self._ids:
            return []
        q_norm = np.linalg.norm(query_vec)
        if q_norm == 0:
            return []
        unit_q = (query_vec / q_norm).astype(np.float32)
        # Cosine similarity = dot product of unit vectors
        scores: np.ndarray = self._unit_mat @ unit_q        # shape (N,)
        # Normalise [-1, 1] → [0, 1]
        scores = (scores + 1.0) / 2.0
        top_k = int(min(k, len(self._ids)))
        indices = np.argpartition(scores, -top_k)[-top_k:]
        indices = indices[np.argsort(scores[indices])[::-1]]
        return [(self._ids[i], float(scores[i])) for i in indices]


# ─────────────────────────────────────────────────────────────────────────────
#  FAISS — fast ANN for large libraries
# ─────────────────────────────────────────────────────────────────────────────

class FAISSVectorBackend(IVectorBackend):
    """FAISS IndexFlatIP — exact inner-product (cosine on L2-normalised vecs).

    Best for:
        - Library-level search across > 500 documents / > 10,000 sections
        - Batch ingestion pipelines where index can be pre-built
        - When exact results matter more than approximate speed

    Install:
        pip install faiss-cpu          # CPU only
        pip install faiss-gpu          # GPU (requires CUDA)

    Note: IndexFlatIP is exact (not approximate). For ~1M+ vectors,
    switch to IndexIVFFlat or IndexHNSWFlat for true ANN behaviour.
    """

    def __init__(self, use_gpu: bool = False) -> None:
        self._use_gpu = use_gpu
        self._ids: list[str] = []
        self._index: Any = None
        self._dims: int = 0
        self._ready = False

    @property
    def backend_name(self) -> str:
        return "faiss"

    @staticmethod
    def is_available() -> bool:
        try:
            import faiss  # noqa: F401
            return True
        except ImportError:
            return False

    def build(self, section_ids: list[str], matrix: np.ndarray) -> None:
        try:
            import faiss
        except ImportError as exc:
            raise ImportError(
                "FAISS not installed. Run: pip install faiss-cpu"
            ) from exc

        self._ids  = list(section_ids)
        self._dims = matrix.shape[1]

        # L2-normalise so inner product = cosine similarity
        mat = matrix.astype(np.float32).copy()   # faiss needs contiguous float32
        faiss.normalize_L2(mat)

        index = faiss.IndexFlatIP(self._dims)
        if self._use_gpu:
            try:
                res   = faiss.StandardGpuResources()
                index = faiss.index_cpu_to_gpu(res, 0, index)
            except Exception:
                logger.warning("FAISSVectorBackend: GPU unavailable, falling back to CPU")

        index.add(mat)
        self._index = index
        self._ready = True
        logger.debug("FAISSVectorBackend: indexed %d vectors (dims=%d, gpu=%s)",
                     len(section_ids), self._dims, self._use_gpu)

    def search(self, query_vec: np.ndarray, k: int) -> list[tuple[str, float]]:
        if self._index is None or not self._ids:
            return []
        try:
            import faiss
        except ImportError:
            return []

        q = query_vec.astype(np.float32).reshape(1, -1).copy()
        faiss.normalize_L2(q)
        top_k = int(min(k, len(self._ids)))
        scores, indices = self._index.search(q, top_k)

        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < 0:                          # FAISS returns -1 for padding
                continue
            # Inner product of L2-normalised vectors is in [-1, 1]; map to [0, 1]
            results.append((self._ids[idx], float((score + 1.0) / 2.0)))
        return results

    def save(self, path: str) -> None:
        """Persist the FAISS index to disk.  Load with FAISSVectorBackend.load()."""
        try:
            import faiss
            faiss.write_index(self._index, path)
            logger.info("FAISSVectorBackend: saved index to %s", path)
        except Exception as exc:
            raise RuntimeError(f"Failed to save FAISS index: {exc}") from exc

    @classmethod
    def load(cls, path: str, section_ids: list[str]) -> "FAISSVectorBackend":
        """Load a persisted FAISS index from disk."""
        try:
            import faiss
        except ImportError as exc:
            raise ImportError("FAISS not installed. Run: pip install faiss-cpu") from exc
        backend = cls()
        backend._index = faiss.read_index(path)
        backend._ids   = list(section_ids)
        backend._dims  = backend._index.d
        backend._ready = True
        return backend


# ─────────────────────────────────────────────────────────────────────────────
#  ChromaDB — persistent, metadata-filtered search
# ─────────────────────────────────────────────────────────────────────────────

class ChromaVectorBackend(IVectorBackend):
    """ChromaDB backend — persistent vector store with metadata filtering.

    Best for:
        - Metadata-filtered search: "search only docs where department=Finance"
        - Cross-document library search that persists across restarts
        - When you want a simple local vector DB without manual index management

    Install:
        pip install chromadb

    Args:
        persist_dir:     Directory to persist the index.  If None, uses an
                         in-memory (ephemeral) client — data lost on restart.
        collection_name: ChromaDB collection name.  Default: "docnest".

    Metadata filtering example::

        backend = ChromaVectorBackend(persist_dir="./chroma_store")
        backend.build(ids, matrix, metadata=[{"department": "Finance"}] * n)
        results = backend.search(q, k=5, where={"department": "Finance"})
    """

    def __init__(
        self,
        persist_dir: str | None = None,
        collection_name: str = "docnest",
    ) -> None:
        self._persist_dir      = persist_dir
        self._collection_name  = collection_name
        self._collection: Any  = None
        self._ready = False

    @property
    def backend_name(self) -> str:
        return "chroma"

    @staticmethod
    def is_available() -> bool:
        try:
            import chromadb  # noqa: F401
            return True
        except ImportError:
            return False

    def build(
        self,
        section_ids: list[str],
        matrix: np.ndarray,
        metadata: list[dict] | None = None,
    ) -> None:
        """Index vectors into ChromaDB.

        Args:
            section_ids: §id strings for each row.
            matrix:      Float32 array (N, dims).
            metadata:    Optional per-section metadata dicts for filtering
                         (e.g. ``[{"doc_id": "report-2024", "department": "Finance"}]``).
        """
        try:
            import chromadb
        except ImportError as exc:
            raise ImportError(
                "ChromaDB not installed. Run: pip install chromadb"
            ) from exc

        if self._persist_dir:
            client = chromadb.PersistentClient(path=self._persist_dir)
        else:
            client = chromadb.EphemeralClient()

        # cosine distance space — matches our cosine-similarity convention
        self._collection = client.get_or_create_collection(
            name=self._collection_name,
            metadata={"hnsw:space": "cosine"},
        )

        # ChromaDB requires at least one key per metadata dict — use {"_": "1"} as
        # a harmless placeholder when caller provides no metadata.
        default_meta = {"_": "1"}
        metas = [m if m else default_meta for m in (metadata or [])]
        if not metas:
            metas = [default_meta for _ in section_ids]
        self._collection.upsert(
            ids=section_ids,
            embeddings=matrix.tolist(),
            metadatas=metas,
        )
        self._ready = True
        logger.debug("ChromaVectorBackend: upserted %d vectors into collection '%s'",
                     len(section_ids), self._collection_name)

    def search(
        self,
        query_vec: np.ndarray,
        k: int,
        where: dict | None = None,
    ) -> list[tuple[str, float]]:
        """Search for top-k similar sections, with optional metadata filter.

        Args:
            query_vec: 1-D float32 query embedding.
            k:         Max number of results.
            where:     ChromaDB metadata filter, e.g. ``{"department": "Finance"}``.
                       See ChromaDB docs for filter syntax.

        Returns:
            List of (section_id, cosine_score) tuples, highest score first.
        """
        if self._collection is None:
            return []

        kwargs: dict[str, Any] = {
            "query_embeddings": [query_vec.tolist()],
            "n_results": max(1, min(k, self._collection.count())),
        }
        if where:
            kwargs["where"] = where

        try:
            results = self._collection.query(**kwargs)
        except Exception as exc:
            logger.warning("ChromaVectorBackend.search failed: %s", exc)
            return []

        ids       = results["ids"][0]
        distances = results["distances"][0]
        # Chroma cosine distance ∈ [0, 2] (0 = identical, 2 = opposite)
        # → similarity ∈ [0, 1]
        return [(sid, 1.0 - d / 2.0) for sid, d in zip(ids, distances)]

    def delete_collection(self) -> None:
        """Drop the collection (useful in tests or re-index scenarios)."""
        if self._collection is not None:
            try:
                import chromadb
                client = (
                    chromadb.PersistentClient(path=self._persist_dir)
                    if self._persist_dir
                    else chromadb.EphemeralClient()
                )
                client.delete_collection(self._collection_name)
                self._collection = None
                self._ready = False
            except Exception as exc:
                logger.warning("ChromaVectorBackend.delete_collection failed: %s", exc)


# ─────────────────────────────────────────────────────────────────────────────
#  Factory
# ─────────────────────────────────────────────────────────────────────────────

def get_vector_backend(
    name: str = "numpy",
    **kwargs: Any,
) -> IVectorBackend:
    """Create a vector backend by name.

    Args:
        name:    ``"numpy"`` (default), ``"faiss"``, or ``"chroma"``.
        **kwargs: Passed to the backend constructor.
                  - faiss:  ``use_gpu=True``
                  - chroma: ``persist_dir="./chroma_store"``,
                             ``collection_name="myapp"``

    Returns:
        IVectorBackend ready to receive a build() call.

    Raises:
        ValueError:  Unknown backend name.
        ImportError: Required package for the chosen backend is not installed.

    Examples::

        # Default — zero deps, always works
        backend = get_vector_backend()

        # FAISS — pip install faiss-cpu
        backend = get_vector_backend("faiss")

        # ChromaDB persistent — pip install chromadb
        backend = get_vector_backend("chroma", persist_dir="./store")
    """
    name = name.lower().strip()

    if name == "numpy":
        return NumpyVectorBackend()

    if name == "faiss":
        if not FAISSVectorBackend.is_available():
            raise ImportError(
                "FAISS is not installed. Run:  pip install faiss-cpu"
            )
        return FAISSVectorBackend(**kwargs)

    if name in ("chroma", "chromadb"):
        if not ChromaVectorBackend.is_available():
            raise ImportError(
                "ChromaDB is not installed. Run:  pip install chromadb"
            )
        return ChromaVectorBackend(**kwargs)

    raise ValueError(
        f"Unknown vector backend '{name}'. "
        f"Choose from: numpy, faiss, chroma"
    )
