"""
DocNest provider interfaces — one per external dependency category.

Every hard dependency on a third-party library sits behind one of these
interfaces.  To swap the backend, change the provider name string — no
other code changes required.

Interfaces
----------
ILLMProvider     — language model completions (groq, openai, ollama, …)
IEmbedder        — text embeddings          (huggingface, openai, …) ← embedder.py
ISearchProvider  — keyword/BM25 search      (bm25, tfidf, keyword)
IStorageBackend  — archive read/write       (zip, dir)
IVectorBackend   — vector similarity search (numpy, faiss, chroma)
IOCRProvider     — image OCR                (tesseract, easyocr, null)
IParser          — document parsing         (pdf, docx, xlsx, …)    ← parsers/base.py

Factories
---------
get_llm_provider(provider, model, api_key)  → ILLMProvider
get_search_provider(name)                   → ISearchProvider
get_storage_backend(name)                   → IStorageBackend
get_vector_backend(name, **kwargs)          → IVectorBackend
get_ocr_provider(name)                      → IOCRProvider
"""

from docnest.providers.llm import ILLMProvider, LangChainLLMProvider, get_llm_provider
from docnest.providers.search import (
    ISearchProvider,
    BM25SearchProvider,
    TFIDFSearchProvider,
    KeywordSearchProvider,
    get_search_provider,
)
from docnest.providers.storage import (
    IStorageBackend,
    ZipStorageBackend,
    DirectoryStorageBackend,
    get_storage_backend,
)
from docnest.providers.vector import (
    IVectorBackend,
    NumpyVectorBackend,
    FAISSVectorBackend,
    ChromaVectorBackend,
    get_vector_backend,
)
from docnest.providers.ocr import (
    IOCRProvider,
    NullOCRProvider,
    TesseractOCRProvider,
    EasyOCRProvider,
    get_ocr_provider,
)

__all__ = [
    # LLM
    "ILLMProvider", "LangChainLLMProvider", "get_llm_provider",
    # Search
    "ISearchProvider", "BM25SearchProvider", "TFIDFSearchProvider",
    "KeywordSearchProvider", "get_search_provider",
    # Storage
    "IStorageBackend", "ZipStorageBackend", "DirectoryStorageBackend",
    "get_storage_backend",
    # Vector
    "IVectorBackend", "NumpyVectorBackend", "FAISSVectorBackend",
    "ChromaVectorBackend", "get_vector_backend",
    # OCR
    "IOCRProvider", "NullOCRProvider", "TesseractOCRProvider",
    "EasyOCRProvider", "get_ocr_provider",
]
