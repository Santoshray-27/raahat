"""
rag_parser.py — ZORO ⚔️ RAG Pipeline — Milestone 1

Parses Saanvi's RAG domain JSON files from RAG/*.json into
structured ParsedDomainFile objects ready for normalization.

Handles all known corpus formats:
  - Format A (DOMAIN-001, DOMAIN-003, DOMAIN-004):
      keys: domain, domain_id, knowledge_requirements, knowledge_records, ...
  - Format B (DOMAIN-006.v2, DOMAIN-007):
      keys: domain, research_summary, knowledge_requirements, source_registry,
            recommended_rag_corpus, knowledge_coverage, query_coverage, ...

Resilience rules:
  - Empty files (0 bytes)           → status="skipped", reason="empty_file"
  - Truncated / invalid JSON        → status="skipped", reason="json_parse_error"
  - Valid JSON, zero knowledge_recs → status="parsed", records=[]
  - Future DOMAIN-x.vN files       → handled automatically by filename parser

OWNERSHIP NOTE: This file is exclusively owned by the RAG pipeline (ZORO).
Do NOT import or call code from emergency, incident, user, or auth modules.
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import re
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Filename version extraction
# ---------------------------------------------------------------------------

def extract_domain_and_version(filename: str) -> tuple[str, str]:
    """
    Extract (domain_id, version) from a RAG corpus filename.

    Examples:
        "DOMAIN-005.v2.json" → ("DOMAIN-005", "v2")
        "DOMAIN-001.json"    → ("DOMAIN-001", "v1")
        "DOMAIN-007.v1.json" → ("DOMAIN-007", "v1")

    The version defaults to "v1" if no explicit version tag is present.
    """
    stem = Path(filename).stem  # e.g. "DOMAIN-005.v2" or "DOMAIN-001"

    # Match DOMAIN-NNN.vX pattern
    match = re.fullmatch(r"(DOMAIN-\d+)\.(v\d+)", stem, re.IGNORECASE)
    if match:
        return match.group(1).upper(), match.group(2).lower()

    # Match bare DOMAIN-NNN pattern
    match = re.fullmatch(r"(DOMAIN-\d+)", stem, re.IGNORECASE)
    if match:
        return match.group(1).upper(), "v1"

    # Unknown filename pattern — preserve full stem as domain_id
    logger.warning("Unexpected RAG filename pattern: %s — using stem as domain_id", filename)
    return stem, "v1"


# ---------------------------------------------------------------------------
# Raw parsed data structures
# ---------------------------------------------------------------------------

class ParseStatus(str, Enum):
    PARSED = "parsed"
    SKIPPED = "skipped"
    ERROR = "error"


@dataclass
class RawKnowledgeRecord:
    """
    Minimal, schema-agnostic representation of a single knowledge record
    as it appears in the raw JSON file.

    Fields are preserved exactly as found — the normalizer is responsible
    for mapping them to the canonical schema.
    """
    raw: Dict[str, Any]  # The complete original record dict, unmodified


@dataclass
class RawSource:
    """A source entry from recommended_rag_corpus or source_registry."""
    raw: Dict[str, Any]


@dataclass
class ParsedDomainFile:
    """
    Result of parsing a single RAG domain JSON file.
    Contains structured access to content alongside original raw data.
    """

    # File identity
    filepath: str
    filename: str
    domain_id: str
    version: str

    # Parse outcome
    status: ParseStatus
    reason: Optional[str]  # e.g. "empty_file", "json_parse_error"

    # Content — empty lists when status=SKIPPED
    raw_domain_name: Optional[str]
    knowledge_records: List[RawKnowledgeRecord]
    sources: List[RawSource]

    # Corpus-level metadata
    knowledge_requirements: List[Dict[str, Any]]
    knowledge_gaps: List[Dict[str, Any]]
    research_summary: Optional[Dict[str, Any]]

    # Full raw JSON for provenance — None when file couldn't be parsed
    raw_json: Optional[Dict[str, Any]]

    # SHA-256 of the raw file bytes (for idempotent ingestion)
    file_hash: Optional[str]

    @property
    def has_records(self) -> bool:
        return len(self.knowledge_records) > 0

    @property
    def is_parseable(self) -> bool:
        return self.status == ParseStatus.PARSED

    @classmethod
    def skipped(
        cls,
        filepath: str,
        filename: str,
        domain_id: str,
        version: str,
        reason: str,
        file_hash: Optional[str] = None,
    ) -> "ParsedDomainFile":
        return cls(
            filepath=filepath,
            filename=filename,
            domain_id=domain_id,
            version=version,
            status=ParseStatus.SKIPPED,
            reason=reason,
            raw_domain_name=None,
            knowledge_records=[],
            sources=[],
            knowledge_requirements=[],
            knowledge_gaps=[],
            research_summary=None,
            raw_json=None,
            file_hash=file_hash,
        )


# ---------------------------------------------------------------------------
# Source extraction helpers  (handle both corpus formats)
# ---------------------------------------------------------------------------

def _extract_sources(data: Dict[str, Any]) -> List[RawSource]:
    """
    Extract source entries from either:
      - Format A: recommended_rag_corpus (list of source dicts)
      - Format B: source_registry (list of source dicts)
    Returns an empty list if neither key is present.
    """
    for key in ("recommended_rag_corpus", "source_registry"):
        entries = data.get(key)
        if isinstance(entries, list):
            return [RawSource(raw=entry) for entry in entries if isinstance(entry, dict)]
    return []


def _extract_knowledge_records(data: Dict[str, Any]) -> List[RawKnowledgeRecord]:
    """
    Extract knowledge_records list from Format A files.
    Format B files do not have a knowledge_records key — they capture
    structured coverage metadata only (no actionable instruction records).
    Returns an empty list if not present or not a list.
    """
    records = data.get("knowledge_records")
    if not isinstance(records, list):
        return []
    return [RawKnowledgeRecord(raw=r) for r in records if isinstance(r, dict)]


def _extract_knowledge_gaps(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Return knowledge_gaps or critical_knowledge_gaps list, whichever is present."""
    for key in ("knowledge_gaps", "critical_knowledge_gaps"):
        gaps = data.get(key)
        if isinstance(gaps, list):
            return [g for g in gaps if isinstance(g, dict)]
    return []


# ---------------------------------------------------------------------------
# Core file parser
# ---------------------------------------------------------------------------

def parse_domain_file(filepath: str | Path) -> ParsedDomainFile:
    """
    Parse a single RAG domain JSON file.

    Returns a ParsedDomainFile in all cases — never raises exceptions
    to callers. Parsing failures are captured as status=SKIPPED.
    """
    filepath = Path(filepath)
    filename = filepath.name
    domain_id, version = extract_domain_and_version(filename)

    # ── 1. Empty file guard ──────────────────────────────────────────────
    try:
        file_size = filepath.stat().st_size
    except OSError as exc:
        logger.warning("Cannot stat RAG file %s: %s", filepath, exc)
        return ParsedDomainFile.skipped(
            filepath=str(filepath),
            filename=filename,
            domain_id=domain_id,
            version=version,
            reason="file_not_accessible",
        )

    if file_size == 0:
        logger.info("Skipping empty RAG file: %s", filename)
        return ParsedDomainFile.skipped(
            filepath=str(filepath),
            filename=filename,
            domain_id=domain_id,
            version=version,
            reason="empty_file",
            file_hash=None,
        )

    # ── 2. Read raw bytes & compute hash ────────────────────────────────
    try:
        raw_bytes = filepath.read_bytes()
    except OSError as exc:
        logger.warning("Cannot read RAG file %s: %s", filepath, exc)
        return ParsedDomainFile.skipped(
            filepath=str(filepath),
            filename=filename,
            domain_id=domain_id,
            version=version,
            reason="file_read_error",
        )

    file_hash = hashlib.sha256(raw_bytes).hexdigest()

    # ── 3. JSON parse ────────────────────────────────────────────────────
    try:
        raw_text = raw_bytes.decode("utf-8-sig")  # handles BOM if present
        data: Dict[str, Any] = json.loads(raw_text)
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        logger.warning(
            "Skipping RAG file %s — JSON parse error: %s", filename, exc
        )
        return ParsedDomainFile.skipped(
            filepath=str(filepath),
            filename=filename,
            domain_id=domain_id,
            version=version,
            reason="json_parse_error",
            file_hash=file_hash,
        )

    if not isinstance(data, dict):
        logger.warning("Skipping RAG file %s — top-level JSON is not an object", filename)
        return ParsedDomainFile.skipped(
            filepath=str(filepath),
            filename=filename,
            domain_id=domain_id,
            version=version,
            reason="invalid_structure",
            file_hash=file_hash,
        )

    # ── 4. Extract structured fields ─────────────────────────────────────
    raw_domain_name: Optional[str] = data.get("domain") or data.get("domain_name")

    # Prefer domain_id from JSON if present, otherwise use filename-derived value
    json_domain_id: Optional[str] = data.get("domain_id")
    if json_domain_id and isinstance(json_domain_id, str):
        domain_id = json_domain_id.strip().upper()

    knowledge_records = _extract_knowledge_records(data)
    sources = _extract_sources(data)

    kr_list = data.get("knowledge_requirements", [])
    knowledge_requirements = [kr for kr in kr_list if isinstance(kr, dict)]

    knowledge_gaps = _extract_knowledge_gaps(data)

    research_summary = data.get("research_summary")
    if not isinstance(research_summary, dict):
        research_summary = None

    record_count = len(knowledge_records)
    source_count = len(sources)
    logger.info(
        "Parsed %s [%s %s]: %d records, %d sources, %d requirements",
        filename, domain_id, version, record_count, source_count,
        len(knowledge_requirements),
    )

    return ParsedDomainFile(
        filepath=str(filepath),
        filename=filename,
        domain_id=domain_id,
        version=version,
        status=ParseStatus.PARSED,
        reason=None,
        raw_domain_name=raw_domain_name,
        knowledge_records=knowledge_records,
        sources=sources,
        knowledge_requirements=knowledge_requirements,
        knowledge_gaps=knowledge_gaps,
        research_summary=research_summary,
        raw_json=data,
        file_hash=file_hash,
    )


# ---------------------------------------------------------------------------
# Corpus-level batch parser
# ---------------------------------------------------------------------------

def parse_corpus_directory(corpus_dir: str | Path) -> List[ParsedDomainFile]:
    """
    Parse all *.json files in a directory.

    Files are returned in sorted filename order for reproducibility.
    Errors in individual files never stop the batch — they produce
    a SKIPPED result and the batch continues.
    """
    corpus_dir = Path(corpus_dir)
    if not corpus_dir.is_dir():
        raise ValueError(f"RAG corpus directory not found: {corpus_dir}")

    json_files = sorted(corpus_dir.glob("*.json"))
    if not json_files:
        logger.warning("No JSON files found in RAG corpus directory: %s", corpus_dir)
        return []

    results: List[ParsedDomainFile] = []
    for json_file in json_files:
        result = parse_domain_file(json_file)
        results.append(result)

    parsed = sum(1 for r in results if r.is_parseable)
    skipped = len(results) - parsed
    total_records = sum(len(r.knowledge_records) for r in results)

    logger.info(
        "Corpus parse complete: %d files parsed, %d skipped, %d total records",
        parsed, skipped, total_records,
    )
    return results
