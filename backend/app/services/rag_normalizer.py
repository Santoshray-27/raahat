"""
rag_normalizer.py — ZORO ⚔️ RAG Pipeline — Milestone 1

Converts RawKnowledgeRecord objects (schema-agnostic) into CanonicalRecord
objects (schema-unified, embedding-ready).

The corpus contains two distinct record schemas:

  Schema A — Clinical Format (DOMAIN-003 / First Aid):
    record_id, knowledge_requirement_id, topic, scenario, answer,
    key_actions, do_not, escalation_criteria, source_ids,
    authority, india_specific, confidence, notes

  Schema B — Operational Format (DOMAIN-005.v2 / Tyre, DOMAIN-006):
    record_id, knowledge_requirement, topic, source_ids,
    evidence_summary, safe_action, unsafe_action,
    escalation_condition, india_specific, confidence, limitations

The normalizer maps both schemas into the single CanonicalRecord type
without discarding any provenance information.

DEPENDENCY NOTE:
  Embedding model and vector dimensions are NOT finalized.
  This module produces embedding-ready TEXT only.
  No embeddings are generated here.

OWNERSHIP NOTE: Exclusively owned by the RAG pipeline (ZORO).
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from app.services.rag_parser import ParsedDomainFile, RawKnowledgeRecord

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Canonical Record Schema
# ---------------------------------------------------------------------------

@dataclass
class CanonicalRecord:
    """
    Unified, schema-normalized representation of a single knowledge record.

    This is the authoritative internal format used by the chunker and
    (in Milestone 2) the embedding service.

    All fields are Optional because source corpus records may be incomplete.
    The normalizer preserves what is available without fabricating content.
    """

    # Provenance identity
    domain_id: str
    version: str
    record_id: str
    requirement_id: Optional[str]   # The KR-xxx this record satisfies

    # Human-readable labels
    domain_name: Optional[str]      # e.g. "First Aid", "Tyre / Puncture Emergency"
    topic: Optional[str]            # Short label for this record's specific sub-topic
    scenario: Optional[str]         # The real-world scenario this record addresses

    # Core actionable content
    answer: Optional[str]           # Full answer / evidence summary
    safe_actions: List[str]         # Ordered list of safe/recommended actions
    prohibited_actions: List[str]   # Things explicitly prohibited
    escalation_criteria: List[str]  # When to call emergency services / escalate

    # Source provenance
    source_ids: List[str]           # e.g. ["SRC-003", "SRC-007"]
    authority: Optional[str]        # "Official", "Institutional", "Community"
    india_specific: Optional[bool]  # Whether the record is India-specific
    confidence: Optional[str]       # "High", "Medium", "Low"

    # Supplementary
    limitations: Optional[str]      # Research limitations / gaps / caveats
    notes: Optional[str]            # Researcher's notes (DOMAIN-003 format)

    # Original raw record for full provenance
    original_raw: Dict[str, Any]


# ---------------------------------------------------------------------------
# Field normalizer helpers
# ---------------------------------------------------------------------------

def _str_or_none(raw: Dict, *keys: str) -> Optional[str]:
    """Try multiple field keys and return the first non-empty string value."""
    for k in keys:
        val = raw.get(k)
        if isinstance(val, str) and val.strip():
            return val.strip()
    return None


def _list_of_str(raw: Dict, *keys: str) -> List[str]:
    """
    Return the first found list-of-strings field.
    If the field is a bare string, wrap it in a list.
    """
    for k in keys:
        val = raw.get(k)
        if isinstance(val, list):
            return [str(item).strip() for item in val if item and str(item).strip()]
        if isinstance(val, str) and val.strip():
            return [val.strip()]
    return []


def _bool_or_none(raw: Dict, key: str) -> Optional[bool]:
    val = raw.get(key)
    if isinstance(val, bool):
        return val
    if isinstance(val, str):
        return val.lower() in ("true", "yes", "1")
    return None


def _extract_requirement_id(raw: Dict) -> Optional[str]:
    """
    Extract the knowledge requirement identifier from either schema:
      Schema A: knowledge_requirement_id → "KR-001"
      Schema B: knowledge_requirement    → "KR-001" or "KR-001: topic text"
    """
    # Schema A
    val = raw.get("knowledge_requirement_id")
    if isinstance(val, str) and val.strip():
        return val.strip()

    # Schema B — may be "KR-001" or "KR-001: Some description text"
    val = raw.get("knowledge_requirement")
    if isinstance(val, str) and val.strip():
        # Extract just the KR identifier
        import re
        match = re.match(r"(KR-\d+)", val.strip(), re.IGNORECASE)
        if match:
            return match.group(1).upper()
        return val.strip()

    return None


def _extract_answer(raw: Dict) -> Optional[str]:
    """
    Schema A: answer field
    Schema B: evidence_summary field
    """
    return _str_or_none(raw, "answer", "evidence_summary")


def _extract_safe_actions(raw: Dict) -> List[str]:
    """
    Schema A: key_actions (list)
    Schema B: safe_action (string describing all safe actions)
    """
    # Schema A
    actions = _list_of_str(raw, "key_actions")
    if actions:
        return actions

    # Schema B — safe_action is typically a paragraph
    val = _str_or_none(raw, "safe_action")
    if val:
        return [val]  # Preserve as single item; chunker handles it as prose
    return []


def _extract_prohibited_actions(raw: Dict) -> List[str]:
    """
    Schema A: do_not (list)
    Schema B: unsafe_action (string)
    """
    # Schema A
    prohibited = _list_of_str(raw, "do_not")
    if prohibited:
        return prohibited

    # Schema B
    val = _str_or_none(raw, "unsafe_action")
    if val:
        return [val]
    return []


def _extract_escalation(raw: Dict) -> List[str]:
    """
    Schema A: escalation_criteria (list)
    Schema B: escalation_condition (string)
    """
    escalation = _list_of_str(raw, "escalation_criteria")
    if escalation:
        return escalation

    val = _str_or_none(raw, "escalation_condition")
    if val:
        return [val]
    return []


# ---------------------------------------------------------------------------
# Core record normalizer
# ---------------------------------------------------------------------------

def normalize_record(
    raw_record: RawKnowledgeRecord,
    domain_id: str,
    version: str,
    domain_name: Optional[str] = None,
) -> CanonicalRecord:
    """
    Normalize a single RawKnowledgeRecord into a CanonicalRecord.

    Never fabricates data — missing fields remain None or [].
    Preserves the full original dict for provenance.
    """
    raw = raw_record.raw

    record_id: str = _str_or_none(raw, "record_id") or "REC-UNKNOWN"
    topic = _str_or_none(raw, "topic")
    scenario = _str_or_none(raw, "scenario")

    answer = _extract_answer(raw)
    safe_actions = _extract_safe_actions(raw)
    prohibited_actions = _extract_prohibited_actions(raw)
    escalation_criteria = _extract_escalation(raw)

    source_ids = _list_of_str(raw, "source_ids")
    authority = _str_or_none(raw, "authority")
    india_specific = _bool_or_none(raw, "india_specific")
    confidence = _str_or_none(raw, "confidence")

    # Schema A: notes; Schema B: limitations
    limitations = _str_or_none(raw, "limitations")
    notes = _str_or_none(raw, "notes")

    requirement_id = _extract_requirement_id(raw)

    return CanonicalRecord(
        domain_id=domain_id,
        version=version,
        record_id=record_id,
        requirement_id=requirement_id,
        domain_name=domain_name,
        topic=topic,
        scenario=scenario,
        answer=answer,
        safe_actions=safe_actions,
        prohibited_actions=prohibited_actions,
        escalation_criteria=escalation_criteria,
        source_ids=source_ids,
        authority=authority,
        india_specific=india_specific,
        confidence=confidence,
        limitations=limitations,
        notes=notes,
        original_raw=raw,
    )


# ---------------------------------------------------------------------------
# Domain-level normalization
# ---------------------------------------------------------------------------

@dataclass
class NormalizedDomain:
    """Result of normalizing all records from one ParsedDomainFile."""
    domain_id: str
    version: str
    domain_name: Optional[str]
    filepath: str
    file_hash: Optional[str]
    records: List[CanonicalRecord]
    sources: List[Dict[str, Any]]   # Preserved raw source dicts
    knowledge_requirements: List[Dict[str, Any]]
    knowledge_gaps: List[Dict[str, Any]]
    research_summary: Optional[Dict[str, Any]]

    @property
    def record_count(self) -> int:
        return len(self.records)


def normalize_domain(parsed: ParsedDomainFile) -> Optional[NormalizedDomain]:
    """
    Normalize all records from a ParsedDomainFile.

    Returns None for SKIPPED files (empty / parse error).
    Returns a NormalizedDomain with an empty records list for valid files
    that contain no knowledge_records (e.g. gap-analysis-only files).
    """
    if not parsed.is_parseable:
        logger.debug(
            "Skipping normalization for %s: status=%s reason=%s",
            parsed.filename, parsed.status, parsed.reason,
        )
        return None

    canonical_records: List[CanonicalRecord] = []
    for raw_record in parsed.knowledge_records:
        try:
            canon = normalize_record(
                raw_record,
                domain_id=parsed.domain_id,
                version=parsed.version,
                domain_name=parsed.raw_domain_name,
            )
            canonical_records.append(canon)
        except Exception as exc:
            # Single-record failure must not abort the entire domain
            record_id = raw_record.raw.get("record_id", "UNKNOWN")
            logger.warning(
                "Failed to normalize record %s in %s: %s",
                record_id, parsed.filename, exc,
            )

    raw_sources = [src.raw for src in parsed.sources]

    logger.info(
        "Normalized %s [%s %s]: %d records canonical, %d sources",
        parsed.filename, parsed.domain_id, parsed.version,
        len(canonical_records), len(raw_sources),
    )

    return NormalizedDomain(
        domain_id=parsed.domain_id,
        version=parsed.version,
        domain_name=parsed.raw_domain_name,
        filepath=parsed.filepath,
        file_hash=parsed.file_hash,
        records=canonical_records,
        sources=raw_sources,
        knowledge_requirements=parsed.knowledge_requirements,
        knowledge_gaps=parsed.knowledge_gaps,
        research_summary=parsed.research_summary,
    )
