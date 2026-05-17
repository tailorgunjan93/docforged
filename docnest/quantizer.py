"""
Embedding quantiser — Stage 6b of the DocNest pipeline.

Compresses float32 embedding vectors to smaller byte representations for
storage inside .udf files.

Modes:
    float32 — baseline, 4 bytes/dim
    float16 — 2× smaller, negligible loss  ← default
    int8    — 4× smaller, ~1-2% loss
    binary  — 32× smaller, ~5-8% loss

Phase: 2  |  Spec: docs/SPEC_DOCNEST_PYPI.md — Section 11
"""

from __future__ import annotations
import numpy as np
from docnest.exceptions import QuantizationError


class Quantizer:
    """Compress and decompress embedding vectors.

    Usage:
        q = Quantizer("float16")
        compressed = q.quantize(vector)             # bytes
        recovered  = q.dequantize(compressed, 768)  # np.ndarray float32
    """

    SUPPORTED_MODES = ("float32", "float16", "int8", "binary")

    def __init__(self, mode: str = "float16") -> None:
        if mode not in self.SUPPORTED_MODES:
            raise ValueError(
                f"Unsupported quantization mode '{mode}'. "
                f"Choose from: {self.SUPPORTED_MODES}"
            )
        self.mode = mode

    def quantize(self, vector: np.ndarray) -> bytes:
        """Compress a float32 vector to bytes.

        Args:
            vector: 1D float32 numpy array of shape (dims,).

        Returns:
            Compressed bytes whose length depends on mode and dims.

        Raises:
            QuantizationError: If compression fails.
        """
        try:
            v = np.asarray(vector, dtype=np.float32).flatten()
            if self.mode == "float32":
                return v.tobytes()
            if self.mode == "float16":
                return v.astype(np.float16).tobytes()
            if self.mode == "int8":
                abs_max = float(np.abs(v).max())
                scale = 127.0 / (abs_max + 1e-8)
                return (v * scale).clip(-127, 127).astype(np.int8).tobytes()
            if self.mode == "binary":
                bits = (v > 0).astype(np.uint8)
                return np.packbits(bits).tobytes()
        except Exception as exc:
            raise QuantizationError(
                f"Quantization ({self.mode}) failed: {exc}"
            ) from exc
        raise QuantizationError(f"Unknown mode: {self.mode}")

    def dequantize(self, data: bytes, dims: int) -> np.ndarray:
        """Decompress bytes back to an approximate float32 vector.

        Args:
            data: Compressed bytes from quantize().
            dims: Original vector dimensionality.

        Returns:
            Approximated float32 numpy array of shape (dims,).

        Raises:
            QuantizationError: If decompression fails.
        """
        try:
            if self.mode == "float32":
                return np.frombuffer(data, dtype=np.float32).copy()
            if self.mode == "float16":
                return np.frombuffer(data, dtype=np.float16).astype(np.float32)
            if self.mode == "int8":
                return np.frombuffer(data, dtype=np.int8).astype(np.float32) / 127.0
            if self.mode == "binary":
                bits = np.unpackbits(np.frombuffer(data, dtype=np.uint8))[:dims]
                return bits.astype(np.float32) * 2.0 - 1.0
        except Exception as exc:
            raise QuantizationError(
                f"Dequantization ({self.mode}) failed: {exc}"
            ) from exc
        raise QuantizationError(f"Unknown mode: {self.mode}")

    def stride(self, dims: int) -> int:
        """Total bytes for one embedding vector of `dims` dimensions."""
        if self.mode == "binary":
            import math
            return math.ceil(dims / 8)
        return dims * self.bytes_per_element

    @property
    def bytes_per_element(self) -> int:
        """Bytes per dimension (binary returns 0 — use stride() instead)."""
        return {"float32": 4, "float16": 2, "int8": 1, "binary": 0}[self.mode]

    @property
    def numpy_dtype(self) -> np.dtype:
        """NumPy dtype for direct frombuffer decoding of this quantization mode.

        Note: binary mode is stored as uint8 bit-packed; use np.unpackbits after
        frombuffer — it cannot be directly frombuffer'd as float.
        """
        return np.dtype({
            "float32": "float32",
            "float16": "float16",
            "int8":    "int8",
            "binary":  "uint8",
        }[self.mode])

    @staticmethod
    def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
        """Compute cosine similarity between two float32 vectors."""
        norm_a = float(np.linalg.norm(a))
        norm_b = float(np.linalg.norm(b))
        if norm_a == 0.0 or norm_b == 0.0:
            return 0.0
        return float(np.dot(a, b) / (norm_a * norm_b))
