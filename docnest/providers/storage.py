"""
Storage backend interface and implementations.

IStorageBackend         — abstract interface for .udf archive read/write
ZipStorageBackend       — ZIP archive  (standard .udf format, stdlib zipfile)
DirectoryStorageBackend — plain directory  (useful for debugging/inspection)

get_storage_backend(name) → IStorageBackend
    "zip" → ZipStorageBackend  (default)
    "dir" → DirectoryStorageBackend
"""

from __future__ import annotations
import json
import zipfile
from abc import ABC, abstractmethod
from pathlib import Path

from docnest.exceptions import UDFReadError, UDFWriteError


# ─────────────────────────────────────────────────────────────────────────────
#  Interface
# ─────────────────────────────────────────────────────────────────────────────

class IStorageBackend(ABC):
    """Abstract interface for .udf archive read/write.

    Implement this to add a new storage format (S3, database, etc.)
    without changing writer or reader code.

    Example custom implementation::

        class S3StorageBackend(IStorageBackend):
            def write_archive(self, entries, output_path):
                ...
            def read_entry(self, archive_path, name):
                ...
            def list_entries(self, archive_path):
                ...
            @property
            def backend_name(self): return "s3"
    """

    @abstractmethod
    def write_archive(
        self,
        entries: dict[str, str | bytes],
        output_path: str,
    ) -> str:
        """Write multiple named entries to an archive.

        Args:
            entries:     Mapping of entry name → content (str encoded to UTF-8,
                         or raw bytes).
            output_path: Destination path for the archive.

        Returns:
            Absolute path to the created archive.

        Raises:
            UDFWriteError: If writing fails.
        """
        ...

    @abstractmethod
    def read_entry(self, archive_path: str, name: str) -> bytes:
        """Read a single named entry from an archive.

        Args:
            archive_path: Path to the archive file / directory.
            name:         Entry name (e.g. ``"catalogue.json"``).

        Returns:
            Raw bytes of the entry.

        Raises:
            UDFReadError: If the archive or entry is missing / unreadable.
        """
        ...

    @abstractmethod
    def list_entries(self, archive_path: str) -> list[str]:
        """List all entry names in an archive.

        Args:
            archive_path: Path to the archive.

        Returns:
            List of entry name strings.

        Raises:
            UDFReadError: If the archive is missing / unreadable.
        """
        ...

    @property
    @abstractmethod
    def backend_name(self) -> str:
        """Backend identifier e.g. 'zip', 'dir'."""
        ...

    def read_json(self, archive_path: str, name: str) -> dict:
        """Convenience: read a JSON entry and parse it."""
        raw = self.read_entry(archive_path, name)
        return json.loads(raw.decode("utf-8"))

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(backend={self.backend_name!r})"


# ─────────────────────────────────────────────────────────────────────────────
#  Implementations
# ─────────────────────────────────────────────────────────────────────────────

class ZipStorageBackend(IStorageBackend):
    """ZIP archive backend — standard .udf file format.

    Uses DEFLATE level 9 for JSON/text entries and ZIP_STORED for binary
    blobs (e.g. embeddings.bin) — binary data has high entropy and compresses
    poorly, so storing uncompressed is both smaller and faster to read.
    """

    # Image formats that are already compressed — don't waste CPU trying
    _PRECOMPRESSED = {".png", ".jpg", ".jpeg", ".webp", ".gif"}
    # Compression levels
    _JSON_LEVEL   = 9   # max compression for JSON/text (repetitive content)
    _BINARY_LEVEL = 1   # fast compression for binary blobs (~7% gain, near-zero CPU)

    @property
    def backend_name(self) -> str:
        return "zip"

    def write_archive(
        self,
        entries: dict[str, str | bytes],
        output_path: str,
    ) -> str:
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        try:
            with zipfile.ZipFile(str(out), "w") as zf:
                for name, content in entries.items():
                    data = content.encode("utf-8") if isinstance(content, str) else content
                    ext = Path(name).suffix.lower()
                    if ext in self._PRECOMPRESSED:
                        # Already compressed — storing avoids wasting CPU
                        zf.writestr(
                            zipfile.ZipInfo(name), data,
                            compress_type=zipfile.ZIP_STORED,
                        )
                    elif isinstance(content, bytes):
                        # Binary blobs (embeddings.bin, .npy, etc.) — light compression
                        # Neural net float16 gains ~7% at level 1; higher levels don't help more
                        zf.writestr(
                            zipfile.ZipInfo(name), data,
                            compress_type=zipfile.ZIP_DEFLATED,
                            compresslevel=self._BINARY_LEVEL,
                        )
                    else:
                        # JSON / text — maximum compression; repetitive keys compress very well
                        zf.writestr(
                            zipfile.ZipInfo(name), data,
                            compress_type=zipfile.ZIP_DEFLATED,
                            compresslevel=self._JSON_LEVEL,
                        )
        except Exception as exc:
            raise UDFWriteError(
                f"ZipStorageBackend failed to write '{out.name}': {exc}"
            ) from exc
        return str(out.resolve())

    def read_entry(self, archive_path: str, name: str) -> bytes:
        try:
            with zipfile.ZipFile(archive_path, "r") as zf:
                return zf.read(name)
        except KeyError:
            raise UDFReadError(f"Entry '{name}' not found in '{archive_path}'.")
        except Exception as exc:
            raise UDFReadError(
                f"ZipStorageBackend failed to read '{name}' "
                f"from '{archive_path}': {exc}"
            ) from exc

    def list_entries(self, archive_path: str) -> list[str]:
        try:
            with zipfile.ZipFile(archive_path, "r") as zf:
                return zf.namelist()
        except Exception as exc:
            raise UDFReadError(
                f"ZipStorageBackend failed to list entries "
                f"in '{archive_path}': {exc}"
            ) from exc


class DirectoryStorageBackend(IStorageBackend):
    """Directory backend — each archive entry is a plain file on disk.

    Useful for debugging: open ``catalogue.json`` and ``content.json`` in any
    text editor without unzipping.  The "archive path" is treated as a
    directory (the ``.udf`` extension is replaced by a same-name folder).

    No extra install required.
    """

    @property
    def backend_name(self) -> str:
        return "dir"

    def _dir(self, archive_path: str) -> Path:
        p = Path(archive_path)
        return p.parent / p.stem   # e.g. "out/report.udf" → "out/report/"

    def write_archive(
        self,
        entries: dict[str, str | bytes],
        output_path: str,
    ) -> str:
        d = self._dir(output_path)
        d.mkdir(parents=True, exist_ok=True)
        try:
            for name, content in entries.items():
                dest = d / name
                dest.parent.mkdir(parents=True, exist_ok=True)
                if isinstance(content, str):
                    dest.write_text(content, encoding="utf-8")
                else:
                    dest.write_bytes(content)
        except Exception as exc:
            raise UDFWriteError(
                f"DirectoryStorageBackend failed writing to '{d}': {exc}"
            ) from exc
        # Return a .udf-looking path for API consistency
        return str((d.parent / (d.name + ".udf")).resolve())

    def read_entry(self, archive_path: str, name: str) -> bytes:
        entry = self._dir(archive_path) / name
        if not entry.exists():
            raise UDFReadError(
                f"Entry '{name}' not found in '{self._dir(archive_path)}'."
            )
        try:
            return entry.read_bytes()
        except Exception as exc:
            raise UDFReadError(
                f"DirectoryStorageBackend failed reading '{name}': {exc}"
            ) from exc

    def list_entries(self, archive_path: str) -> list[str]:
        d = self._dir(archive_path)
        if not d.exists():
            raise UDFReadError(f"Archive directory not found: '{d}'.")
        return [
            str(f.relative_to(d)).replace("\\", "/")
            for f in d.rglob("*")
            if f.is_file()
        ]


# ─────────────────────────────────────────────────────────────────────────────
#  Factory
# ─────────────────────────────────────────────────────────────────────────────

def get_storage_backend(name: str = "zip") -> IStorageBackend:
    """Create a storage backend by name.

    Args:
        name: ``"zip"`` (default) or ``"dir"``.

    Returns:
        IStorageBackend ready to use.

    Examples::

        backend = get_storage_backend()        # ZIP (standard .udf)
        backend = get_storage_backend("dir")   # directory (debug)
    """
    name = name.lower().strip()
    if name == "zip":
        return ZipStorageBackend()
    if name in ("dir", "directory"):
        return DirectoryStorageBackend()
    raise ValueError(
        f"Unknown storage backend '{name}'. Choose from: zip, dir"
    )
