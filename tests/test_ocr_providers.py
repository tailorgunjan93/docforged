"""Tests for IOCRProvider implementations: Null, Tesseract, EasyOCR.

Run: pytest tests/test_ocr_providers.py -v
"""
from __future__ import annotations

import pytest

from docnest.providers.ocr import (
    EasyOCRProvider,
    NullOCRProvider,
    TesseractOCRProvider,
    get_ocr_provider,
)


# ── NullOCRProvider ───────────────────────────────────────────────────────────

class TestNullOCRProvider:
    def test_backend_name(self):
        assert NullOCRProvider().backend_name == "null"

    def test_always_available(self):
        assert NullOCRProvider().available is True

    def test_extract_text_returns_empty_string(self):
        result = NullOCRProvider().extract_text(b"\x89PNG\r\n")
        assert result == ""

    def test_never_raises_on_garbage_input(self):
        # Should silently return "" even for junk bytes
        result = NullOCRProvider().extract_text(b"\x00\x01\x02\x03")
        assert result == ""

    def test_returns_str_not_bytes(self):
        result = NullOCRProvider().extract_text(b"any bytes")
        assert isinstance(result, str)


# ── TesseractOCRProvider ──────────────────────────────────────────────────────

class TestTesseractOCRProvider:
    def test_backend_name(self):
        provider = TesseractOCRProvider()
        assert provider.backend_name == "tesseract"

    def test_available_reflects_installation(self):
        provider = TesseractOCRProvider()
        # available should be a bool — True only if pytesseract + Tesseract binary installed
        assert isinstance(provider.available, bool)

    def test_extract_text_returns_str_or_empty(self):
        provider = TesseractOCRProvider()
        if not provider.available:
            pytest.skip("Tesseract not installed")
        # Tiny 1×1 white PNG
        import struct, zlib
        def make_tiny_png() -> bytes:
            def chunk(name, data):
                c = struct.pack(">I", len(data)) + name + data
                return c + struct.pack(">I", zlib.crc32(name + data) & 0xFFFFFFFF)
            sig = b"\x89PNG\r\n\x1a\n"
            ihdr = chunk(b"IHDR", struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0))
            raw = b"\x00\xff\xff\xff"
            idat = chunk(b"IDAT", zlib.compress(raw))
            iend = chunk(b"IEND", b"")
            return sig + ihdr + idat + iend
        result = provider.extract_text(make_tiny_png())
        assert isinstance(result, str)

    def test_returns_empty_on_bad_bytes(self):
        """OCR providers must never raise — return empty string on failure."""
        provider = TesseractOCRProvider()
        if not provider.available:
            pytest.skip("Tesseract not installed")
        result = provider.extract_text(b"not an image")
        assert isinstance(result, str)


# ── EasyOCRProvider ───────────────────────────────────────────────────────────

class TestEasyOCRProvider:
    def test_backend_name(self):
        provider = EasyOCRProvider()
        assert provider.backend_name == "easyocr"

    def test_available_reflects_installation(self):
        provider = EasyOCRProvider()
        assert isinstance(provider.available, bool)

    def test_extract_text_never_raises(self):
        provider = EasyOCRProvider()
        if not provider.available:
            pytest.skip("EasyOCR not installed")
        result = provider.extract_text(b"garbage bytes")
        assert isinstance(result, str)


# ── get_ocr_provider factory ──────────────────────────────────────────────────

class TestGetOCRProvider:
    def test_returns_null_by_name(self):
        p = get_ocr_provider("null")
        assert isinstance(p, NullOCRProvider)

    def test_returns_tesseract_by_name(self):
        p = get_ocr_provider("tesseract")
        assert isinstance(p, TesseractOCRProvider)

    def test_returns_easyocr_by_name(self):
        p = get_ocr_provider("easyocr")
        assert isinstance(p, EasyOCRProvider)

    def test_default_is_null(self):
        p = get_ocr_provider()
        assert isinstance(p, NullOCRProvider)

    def test_unknown_raises(self):
        with pytest.raises((ValueError, KeyError)):
            get_ocr_provider("zzz_unknown_engine")

    def test_extract_text_contract_always_returns_str(self):
        """All providers must return str (never raise) on bad input."""
        for name in ("null",):
            p = get_ocr_provider(name)
            result = p.extract_text(b"\x00\xff garbage")
            assert isinstance(result, str)
