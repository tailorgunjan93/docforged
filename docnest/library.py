"""
DocNest Library — multi-document catalogue.

A library is a folder with a `library.json` index that tracks every .udf file
added to it. It is the "master catalogue" from the library mental model:

    library/
        library.json          ← index of all documents
        hr_onboarding.udf
        q4_budget.udf
        api_architecture.udf

Users and AI both search the library first, then fetch the specific .udf.

Design pattern: Repository
"""

from __future__ import annotations

import json
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

LIBRARY_FILE = "library.json"
LIBRARY_VERSION = "1.0"


class LibraryEntry:
    """Lightweight index entry for one .udf document in the library."""

    def __init__(
        self,
        doc_id: str,
        title: str,
        udf_path: str,
        source_format: str = "",
        owner: str = "",
        department: str = "",
        tags: list[str] | None = None,
        access_roles: list[str] | None = None,
        version: str = "1.0",
        last_updated: str = "",
        summary: str = "",
        section_count: int = 0,
        added_at: str = "",
        keywords: list[str] | None = None,
    ) -> None:
        self.doc_id = doc_id
        self.title = title
        self.udf_path = udf_path           # relative path inside the library folder
        self.source_format = source_format
        self.owner = owner
        self.department = department
        self.tags = tags or []
        self.access_roles = access_roles or ["*"]
        self.version = version
        self.last_updated = last_updated
        self.summary = summary
        self.section_count = section_count
        self.added_at = added_at or datetime.now(timezone.utc).isoformat()
        self.keywords = keywords or []     # aggregated from all section keywords

    def to_dict(self) -> dict:
        return {
            "doc_id":        self.doc_id,
            "title":         self.title,
            "udf_path":      self.udf_path,
            "source_format": self.source_format,
            "owner":         self.owner,
            "department":    self.department,
            "tags":          self.tags,
            "access_roles":  self.access_roles,
            "version":       self.version,
            "last_updated":  self.last_updated,
            "summary":       self.summary,
            "section_count": self.section_count,
            "added_at":      self.added_at,
            "keywords":      self.keywords,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "LibraryEntry":
        return cls(**{k: v for k, v in d.items() if k in cls.__init__.__code__.co_varnames})


class LibraryManager:
    """Manages a library.json index in a given folder.

    Usage::

        lib = LibraryManager("D:/docs/my-library")
        lib.init()                          # create the library
        lib.add("report.udf")              # index a .udf file
        results = lib.search("leave policy")
        for r in results:
            print(r.title, r.udf_path)
    """

    def __init__(self, library_dir: str) -> None:
        self.root = Path(library_dir)
        self._index_path = self.root / LIBRARY_FILE

    # ------------------------------------------------------------------ #
    #  Init / load / save                                                  #
    # ------------------------------------------------------------------ #

    def init(self, name: str = "", description: str = "") -> None:
        """Create a new library in the root folder."""
        self.root.mkdir(parents=True, exist_ok=True)
        if self._index_path.exists():
            return  # already initialised
        index = {
            "library_version": LIBRARY_VERSION,
            "name":            name or self.root.name,
            "description":     description,
            "created_at":      datetime.now(timezone.utc).isoformat(),
            "documents":       [],
        }
        self._index_path.write_text(
            json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    def _load_index(self) -> dict:
        if not self._index_path.exists():
            raise FileNotFoundError(
                f"No library found at '{self.root}'. Run `docnest library init` first."
            )
        return json.loads(self._index_path.read_text(encoding="utf-8"))

    def _save_index(self, index: dict) -> None:
        self._index_path.write_text(
            json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    # ------------------------------------------------------------------ #
    #  Add                                                                 #
    # ------------------------------------------------------------------ #

    def add(self, udf_path: str) -> LibraryEntry:
        """Index a .udf file into the library.

        Reads manifest.json and catalogue.json from the archive to build the
        library entry. The .udf file is NOT copied — the path is stored as-is
        (relative if inside the library folder, absolute otherwise).

        Args:
            udf_path: Path to the .udf file.

        Returns:
            The created LibraryEntry.
        """
        path = Path(udf_path).resolve()
        if not path.exists():
            raise FileNotFoundError(f"File not found: {udf_path}")
        if not zipfile.is_zipfile(str(path)):
            raise ValueError(f"Not a valid .udf archive: {udf_path}")

        # Extract metadata from the archive
        with zipfile.ZipFile(str(path), "r") as zf:
            manifest  = json.loads(zf.read("manifest.json"))
            catalogue = json.loads(zf.read("catalogue.json"))

        # Aggregate keywords from all section entries
        all_keywords: set[str] = set()
        for section in catalogue.get("section_index", []):
            all_keywords.update(section.get("keywords", []))

        # Store relative path if inside library folder, otherwise absolute
        try:
            rel = path.relative_to(self.root)
            stored_path = str(rel)
        except ValueError:
            stored_path = str(path)

        entry = LibraryEntry(
            doc_id        = manifest.get("doc_id", path.stem),
            title         = manifest.get("title", path.stem),
            udf_path      = stored_path,
            source_format = manifest.get("source_format", ""),
            owner         = manifest.get("owner", ""),
            department    = manifest.get("department", ""),
            tags          = manifest.get("tags", []),
            access_roles  = manifest.get("access_roles", ["*"]),
            version       = manifest.get("version", "1.0"),
            last_updated  = manifest.get("last_updated", ""),
            summary       = catalogue.get("summary", ""),
            section_count = manifest.get("section_count", 0),
            keywords      = sorted(all_keywords),
        )

        index = self._load_index()
        # Replace if same doc_id already in library
        docs = [d for d in index["documents"] if d["doc_id"] != entry.doc_id]
        docs.append(entry.to_dict())
        index["documents"] = docs
        self._save_index(index)
        return entry

    # ------------------------------------------------------------------ #
    #  List / search / remove                                              #
    # ------------------------------------------------------------------ #

    def list_docs(self, department: str = "", access_role: str = "*") -> list[LibraryEntry]:
        """Return all documents, optionally filtered by department or access role."""
        index = self._load_index()
        entries = [LibraryEntry.from_dict(d) for d in index["documents"]]
        if department:
            entries = [e for e in entries if e.department.lower() == department.lower()]
        if access_role != "*":
            entries = [
                e for e in entries
                if "*" in e.access_roles or access_role in e.access_roles
            ]
        return entries

    def search(self, query: str, top_k: int = 10) -> list[tuple[LibraryEntry, float]]:
        """Keyword search across library entries.

        Scores each document by how many query tokens match its title, tags,
        department, owner, keywords, and summary. Returns ranked results.

        Args:
            query: Free-text query string.
            top_k: Maximum number of results to return.

        Returns:
            List of (LibraryEntry, score) tuples, highest score first.
        """
        tokens = set(query.lower().split())
        entries = self.list_docs()
        scored: list[tuple[LibraryEntry, float]] = []

        for e in entries:
            # Build searchable text bag
            bag: set[str] = set()
            bag.update(e.title.lower().split())
            bag.update(e.owner.lower().split())
            bag.update(e.department.lower().split())
            bag.update(t.lower() for t in e.tags)
            bag.update(t.lower() for t in e.keywords)
            bag.update(e.summary.lower().split())

            hits = len(tokens & bag)
            if hits > 0:
                scored.append((e, hits / len(tokens)))

        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:top_k]

    def remove(self, doc_id: str) -> bool:
        """Remove a document from the library index (does not delete the .udf file)."""
        index = self._load_index()
        before = len(index["documents"])
        index["documents"] = [d for d in index["documents"] if d["doc_id"] != doc_id]
        self._save_index(index)
        return len(index["documents"]) < before

    def get(self, doc_id: str) -> Optional[LibraryEntry]:
        """Fetch a single entry by doc_id, or None if not found."""
        index = self._load_index()
        for d in index["documents"]:
            if d["doc_id"] == doc_id:
                return LibraryEntry.from_dict(d)
        return None

    def resolve_path(self, entry: LibraryEntry) -> Path:
        """Return the absolute Path to the .udf file for a library entry."""
        p = Path(entry.udf_path)
        if p.is_absolute():
            return p
        return (self.root / p).resolve()

    @property
    def name(self) -> str:
        return self._load_index().get("name", self.root.name)

    @property
    def doc_count(self) -> int:
        return len(self._load_index().get("documents", []))
