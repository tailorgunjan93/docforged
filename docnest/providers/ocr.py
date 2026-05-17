"""
OCR provider interface and implementations.

IOCRProvider          — abstract interface for image-to-text extraction
NullOCRProvider       — no-op stub  (default — zero deps, returns "")
TesseractOCRProvider  — pytesseract + Pillow  (pip install pytesseract pillow)
EasyOCRProvider       — easyocr  (pip install easyocr, supports 80+ languages)

get_ocr_provider(name) → IOCRProvider
    "null"      → NullOCRProvider      (default)
    "tesseract" → TesseractOCRProvider
    "easyocr"   → EasyOCRProvider
"""

from __future__ import annotations
from abc import ABC, abstractmethod


# ─────────────────────────────────────────────────────────────────────────────
#  Interface
# ─────────────────────────────────────────────────────────────────────────────

class IOCRProvider(ABC):
    """Abstract interface for OCR text extraction from images.

    Implement this to add a new OCR engine without changing parser code.

    Example custom implementation::

        class MyOCR(IOCRProvider):
            def extract_text(self, image_bytes):
                return my_ocr_api.run(image_bytes)
            @property
            def backend_name(self): return "myocr"
    """

    @abstractmethod
    def extract_text(self, image_bytes: bytes) -> str:
        """Extract text from raw image bytes.

        Args:
            image_bytes: Raw image bytes (PNG, JPEG, TIFF, etc.)

        Returns:
            Extracted text as a plain string (may be empty if no text found).
            Never raises — returns "" on failure.
        """
        ...

    @property
    @abstractmethod
    def backend_name(self) -> str:
        """Backend identifier e.g. 'tesseract', 'easyocr', 'null'."""
        ...

    @property
    def available(self) -> bool:
        """True if this backend's dependencies are installed."""
        return True

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(backend={self.backend_name!r})"


# ─────────────────────────────────────────────────────────────────────────────
#  Implementations
# ─────────────────────────────────────────────────────────────────────────────

class NullOCRProvider(IOCRProvider):
    """No-op OCR — always returns empty string.

    Use when OCR is disabled or not needed (text-native PDFs, DOCX files).
    Zero dependencies required.
    """

    @property
    def backend_name(self) -> str:
        return "null"

    def extract_text(self, image_bytes: bytes) -> str:  # noqa: D102
        return ""


class TesseractOCRProvider(IOCRProvider):
    """OCR via pytesseract + Pillow.

    Requirements:
        - Tesseract binary installed on the system
          (https://github.com/tesseract-ocr/tesseract)
        - ``pip install pytesseract pillow``

    Usage::

        ocr = TesseractOCRProvider(lang="eng")
        text = ocr.extract_text(image_bytes)

        # Multi-language
        ocr = TesseractOCRProvider(lang="eng+hin")
    """

    def __init__(self, lang: str = "eng", config: str = "") -> None:
        """
        Args:
            lang:   Tesseract language code(s), e.g. ``"eng"``, ``"eng+hin"``.
            config: Extra Tesseract config string, e.g. ``"--psm 6"``.
        """
        self._lang   = lang
        self._config = config

    @property
    def backend_name(self) -> str:
        return "tesseract"

    @property
    def available(self) -> bool:
        try:
            import pytesseract  # type: ignore[import]  # noqa: F401
            from PIL import Image  # type: ignore[import]  # noqa: F401
            return True
        except ImportError:
            return False

    def extract_text(self, image_bytes: bytes) -> str:
        try:
            import io
            import pytesseract             # type: ignore[import]
            from PIL import Image          # type: ignore[import]

            img = Image.open(io.BytesIO(image_bytes))
            return pytesseract.image_to_string(
                img, lang=self._lang, config=self._config
            ).strip()
        except ImportError as exc:
            raise ImportError(
                "pytesseract / Pillow not installed. "
                "Run: pip install pytesseract pillow\n"
                "Also install the Tesseract binary: "
                "https://github.com/tesseract-ocr/tesseract"
            ) from exc
        except Exception:
            return ""   # OCR failure → empty string, never crash


class EasyOCRProvider(IOCRProvider):
    """OCR via EasyOCR — supports 80+ languages, no Tesseract binary required.

    Install: ``pip install easyocr``
    Downloads language models on first use (~100 MB each).

    Usage::

        ocr = EasyOCRProvider(languages=["en"])
        text = ocr.extract_text(image_bytes)

        # With GPU acceleration
        ocr = EasyOCRProvider(languages=["en", "hi"], gpu=True)
    """

    def __init__(
        self,
        languages: list[str] | None = None,
        gpu: bool = False,
    ) -> None:
        """
        Args:
            languages: Language codes, e.g. ``["en", "hi"]``. Defaults to ``["en"]``.
            gpu:       Use GPU if available. Default ``False``.
        """
        self._languages = languages or ["en"]
        self._gpu       = gpu
        self._reader: object | None = None   # lazy-loaded

    @property
    def backend_name(self) -> str:
        return "easyocr"

    @property
    def available(self) -> bool:
        try:
            import easyocr  # type: ignore[import]  # noqa: F401
            return True
        except ImportError:
            return False

    def extract_text(self, image_bytes: bytes) -> str:
        try:
            import io
            import numpy as np
            from PIL import Image  # type: ignore[import]

            if self._reader is None:
                import easyocr  # type: ignore[import]
                self._reader = easyocr.Reader(self._languages, gpu=self._gpu)

            img      = Image.open(io.BytesIO(image_bytes))
            img_arr  = np.array(img)
            results  = self._reader.readtext(img_arr, detail=0)  # type: ignore[union-attr]
            return " ".join(str(r) for r in results).strip()
        except ImportError as exc:
            raise ImportError(
                "easyocr is not installed. Run: pip install easyocr"
            ) from exc
        except Exception:
            return ""


# ─────────────────────────────────────────────────────────────────────────────
#  Factory
# ─────────────────────────────────────────────────────────────────────────────

def get_ocr_provider(name: str = "null") -> IOCRProvider:
    """Create an OCR provider by name.

    Args:
        name: ``"null"`` (default), ``"tesseract"``, or ``"easyocr"``.
              ``"null"`` is a no-op — use when OCR is disabled.

    Returns:
        IOCRProvider ready to use.

    Examples::

        ocr = get_ocr_provider()               # null (no OCR)
        ocr = get_ocr_provider("tesseract")    # Tesseract
        ocr = get_ocr_provider("easyocr")      # EasyOCR (80+ languages)
    """
    name = name.lower().strip()
    if name == "null":
        return NullOCRProvider()
    if name == "tesseract":
        return TesseractOCRProvider()
    if name == "easyocr":
        return EasyOCRProvider()
    raise ValueError(
        f"Unknown OCR provider '{name}'. Choose from: null, tesseract, easyocr"
    )
