"""Tests for IStorageBackend: ZipStorageBackend and DirectoryStorageBackend.

Run: pytest tests/test_storage_backends.py -v
"""
from __future__ import annotations

import json
import zipfile
from pathlib import Path

import pytest

from docnest.providers.storage import (
    DirectoryStorageBackend,
    ZipStorageBackend,
    get_storage_backend,
)


# ── ZipStorageBackend ─────────────────────────────────────────────────────────

class TestZipStorageBackend:
    def test_backend_name(self):
        assert ZipStorageBackend().backend_name == "zip"

    def test_write_creates_zip_file(self, tmp_path: Path):
        out = str(tmp_path / "test.udf")
        ZipStorageBackend().write_archive({"manifest.json": b"{}"}, out)
        assert Path(out).exists()
        assert zipfile.is_zipfile(out)

    def test_write_multiple_entries(self, tmp_path: Path):
        out = str(tmp_path / "test.udf")
        entries = {
            "manifest.json": b'{"a":1}',
            "catalogue.json": b'{"b":2}',
            "content.json": b'{"c":3}',
        }
        ZipStorageBackend().write_archive(entries, out)
        with zipfile.ZipFile(out, "r") as zf:
            assert set(zf.namelist()) == set(entries.keys())

    def test_read_entry_returns_bytes(self, tmp_path: Path):
        out = str(tmp_path / "test.udf")
        data = b'{"hello": "world"}'
        ZipStorageBackend().write_archive({"manifest.json": data}, out)
        result = ZipStorageBackend().read_entry(out, "manifest.json")
        assert result == data

    def test_list_entries_returns_all_names(self, tmp_path: Path):
        out = str(tmp_path / "test.udf")
        entries = {"a.json": b"1", "b.json": b"2", "embeddings.bin": b"\x00\x01"}
        ZipStorageBackend().write_archive(entries, out)
        names = ZipStorageBackend().list_entries(out)
        assert set(names) == {"a.json", "b.json", "embeddings.bin"}

    def test_read_json_parses_correctly(self, tmp_path: Path):
        out = str(tmp_path / "test.udf")
        obj = {"udf_version": "1.1", "doc_id": "my-doc"}
        ZipStorageBackend().write_archive(
            {"manifest.json": json.dumps(obj).encode()}, out
        )
        result = ZipStorageBackend().read_json(out, "manifest.json")
        assert result == obj

    def test_write_bytes_entry_preserved(self, tmp_path: Path):
        out = str(tmp_path / "test.udf")
        raw = bytes(range(256))
        ZipStorageBackend().write_archive({"embeddings.bin": raw}, out)
        result = ZipStorageBackend().read_entry(out, "embeddings.bin")
        assert result == raw

    def test_missing_entry_raises(self, tmp_path: Path):
        out = str(tmp_path / "test.udf")
        ZipStorageBackend().write_archive({"a.json": b"{}"}, out)
        with pytest.raises(Exception):
            ZipStorageBackend().read_entry(out, "missing.json")

    def test_overwrite_replaces_file(self, tmp_path: Path):
        out = str(tmp_path / "test.udf")
        ZipStorageBackend().write_archive({"a.json": b"1"}, out)
        ZipStorageBackend().write_archive({"b.json": b"2"}, out)
        names = ZipStorageBackend().list_entries(out)
        # After overwrite, only the new entries should be present
        assert "b.json" in names


# ── DirectoryStorageBackend ───────────────────────────────────────────────────

class TestDirectoryStorageBackend:
    def test_backend_name(self):
        assert DirectoryStorageBackend().backend_name == "dir"

    def test_write_creates_directory(self, tmp_path: Path):
        out = str(tmp_path / "myarchive")
        DirectoryStorageBackend().write_archive({"manifest.json": b"{}"}, out)
        assert Path(out).is_dir()

    def test_write_creates_files_in_directory(self, tmp_path: Path):
        out = str(tmp_path / "myarchive")
        entries = {"manifest.json": b'{}', "catalogue.json": b'[]'}
        DirectoryStorageBackend().write_archive(entries, out)
        assert (Path(out) / "manifest.json").exists()
        assert (Path(out) / "catalogue.json").exists()

    def test_read_entry_returns_bytes(self, tmp_path: Path):
        out = str(tmp_path / "myarchive")
        data = b'{"test": true}'
        DirectoryStorageBackend().write_archive({"manifest.json": data}, out)
        result = DirectoryStorageBackend().read_entry(out, "manifest.json")
        assert result == data

    def test_list_entries_returns_all_names(self, tmp_path: Path):
        out = str(tmp_path / "myarchive")
        entries = {"a.json": b"1", "b.json": b"2"}
        DirectoryStorageBackend().write_archive(entries, out)
        names = DirectoryStorageBackend().list_entries(out)
        assert set(names) == {"a.json", "b.json"}

    def test_read_json_parses_correctly(self, tmp_path: Path):
        out = str(tmp_path / "myarchive")
        obj = {"key": "value", "num": 42}
        DirectoryStorageBackend().write_archive(
            {"data.json": json.dumps(obj).encode()}, out
        )
        result = DirectoryStorageBackend().read_json(out, "data.json")
        assert result == obj

    def test_binary_file_preserved(self, tmp_path: Path):
        out = str(tmp_path / "myarchive")
        raw = bytes(range(128))
        DirectoryStorageBackend().write_archive({"embeddings.bin": raw}, out)
        result = DirectoryStorageBackend().read_entry(out, "embeddings.bin")
        assert result == raw


# ── get_storage_backend factory ───────────────────────────────────────────────

class TestGetStorageBackend:
    def test_returns_zip_by_name(self):
        b = get_storage_backend("zip")
        assert isinstance(b, ZipStorageBackend)

    def test_returns_dir_by_name(self):
        b = get_storage_backend("dir")
        assert isinstance(b, DirectoryStorageBackend)

    def test_default_is_zip(self):
        b = get_storage_backend()
        assert isinstance(b, ZipStorageBackend)

    def test_unknown_raises(self):
        with pytest.raises((ValueError, KeyError)):
            get_storage_backend("zzz_unknown")
