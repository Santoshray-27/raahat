"""
rag_chunker.py — ZORO ⚔️ RAG Pipeline — Milestone 1

Converts CanonicalRecord objects into EmbeddingReadyChunk objects.

CRITICAL SAFETY RULE:
  Emergency knowledge chunks must NEVER split:
    - safe_actions
    - prohibited_actions
    - escalation_criteria
  if separating them would produce an incomplete or misleading instruction.

  A user querying "what should I do if someone is bleeding?" must receive
  ALL of: what TO do, what NOT to do, and when to escalate — in one chunk.

Strategy: Record-level semantic chunking.
  Each CanonicalRecord becomes exactly one EmbeddingReadyChunk.
  This guarantees completeness of every emergency instruction.

The generated chunk text follows a structured markdown-style format
that clearly delineates sections for embedding and human review.

EMBEDDING NOTE (Milestone 2 dependency):
  - Vector dimension is NOT finalized (VECTOR(1536) in DB).
  - Embedding model has NOT been selected.
  - This module produces TEXT only. No vectors are generated here.
  - chunk.embedding_text is the final string ready for embedding.

OWNERSHIP NOTE: Exclusively owned by the RAG pipeline (ZORO).
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from app.services.rag_normalizer import CanonicalRecord, NormalizedDomain

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Output data structure
# ---------------------------------------------------------------------------

@dataclass
class EmbeddingReadyChunk:
    """
    A single embedding-ready text unit derived from a CanonicalRecord.

    Fields used by Milestone 2 (embedding + pgvector storage):
      - embedding_text : the final text string to be embedded
      - chunk_index    : 0-based position within the parent document
      - chunk_metadata : JSONB metadata dict for rag_chunks.metadata column
    """

    # Source identity
    domain_id: str
    version: str
    record_id: str
    requirement_id: Optional[str]
    chunk_index: int            # 0-based index within this domain document

    # Embedding-ready text (the complete chunk as a single string)
    embedding_text: str

    # Metadata to be stored in rag_chunks.metadata JSONB column
    chunk_metadata: Dict[str, Any]

    # Estimated approximate token count (rough heuristic; not authoritative)
    estimated_tokens: int


# ---------------------------------------------------------------------------
# Chunk text builder
# ---------------------------------------------------------------------------

def _section(heading: str, items: List[str]) -> str:
    """
    Format a list of items under a named section.
    Returns empty string if items list is empty.
    """
    if not items:
        return ""
    lines = [f"**{heading}:**"]
    for item in items:
        lines.append(f"- {item}")
    return "\n".join(lines)


def _prose_section(heading: str, text: Optional[str]) -> str:
    """Format a single prose block under a heading."""
    if not text:
        return ""
    return f"**{heading}:** {text}"


def _build_chunk_text(record: CanonicalRecord) -> str:
    """
    Build the complete embedding-ready text for a CanonicalRecord.

    Structure:
      1. Header — domain, topic, requirement context
      2. Scenario — the specific real-world situation
      3. Full Answer / Evidence Summary
      4. Safe Actions (what to do)
      5. Prohibited Actions (what NOT to do)
      6. Escalation Criteria (when to call emergency services)
      7. Authority & Source metadata

    ALL sections are emitted in the same chunk.
    Sections 4/5/6 are NEVER split into separate chunks.
    """
    parts: List[str] = []

    # ── 1. Header ──────────────────────────────────────────────────────
    domain_label = record.domain_name or record.domain_id
    req_label = record.requirement_id or ""
    topic_label = record.topic or ""

    if req_label and topic_label:
        header = f"[EMERGENCY PROTOCOL | {domain_label} | {req_label}: {topic_label}]"
    elif topic_label:
        header = f"[EMERGENCY PROTOCOL | {domain_label} | {topic_label}]"
    else:
        header = f"[EMERGENCY PROTOCOL | {domain_label}]"

    parts.append(header)

    # ── 2. Scenario ────────────────────────────────────────────────────
    if record.scenario:
        parts.append(_prose_section("Scenario", record.scenario))

    # ── 3. Answer / Evidence ───────────────────────────────────────────
    if record.answer:
        parts.append(_prose_section("Guidance", record.answer))

    # ── 4. Safe Actions ────────────────────────────────────────────────
    safe_section = _section("What To Do", record.safe_actions)
    if safe_section:
        parts.append(safe_section)

    # ── 5. Prohibited Actions ──────────────────────────────────────────
    prohibited_section = _section("Do NOT Do", record.prohibited_actions)
    if prohibited_section:
        parts.append(prohibited_section)

    # ── 6. Escalation Criteria ─────────────────────────────────────────
    escalation_section = _section("Call Emergency Services If", record.escalation_criteria)
    if escalation_section:
        parts.append(escalation_section)

    # ── 7. Limitations / Caveats ───────────────────────────────────────
    limitations_text = record.limitations or record.notes
    if limitations_text:
        parts.append(_prose_section("Limitations", limitations_text))

    # ── 8. Authority / Provenance ──────────────────────────────────────
    authority_parts: List[str] = []
    if record.authority:
        authority_parts.append(f"Authority: {record.authority}")
    if record.confidence:
        authority_parts.append(f"Confidence: {record.confidence}")
    if record.india_specific is not None:
        authority_parts.append(f"India-specific: {record.india_specific}")
    if record.source_ids:
        authority_parts.append(f"Sources: {', '.join(record.source_ids)}")

    if authority_parts:
        parts.append("[" + " | ".join(authority_parts) + "]")

    return "\n\n".join(parts)


# ---------------------------------------------------------------------------
# Token estimation (rough heuristic — NOT authoritative)
# ---------------------------------------------------------------------------

def _estimate_tokens(text: str) -> int:
    """
    Rough heuristic: ~4 characters per token on average for English text.
    Used only for logging / monitoring, not for chunking decisions.
    """
    return max(1, len(text) // 4)


# ---------------------------------------------------------------------------
# Core chunk generator
# ---------------------------------------------------------------------------

def chunk_canonical_record(
    record: CanonicalRecord,
    chunk_index: int,
) -> EmbeddingReadyChunk:
    """
    Convert a single CanonicalRecord into one EmbeddingReadyChunk.

    Each record maps 1:1 to a chunk. The complete actionable context
    (safe actions, prohibitions, escalation) is preserved in every chunk.
    """
    embedding_text = _build_chunk_text(record)
    estimated_tokens = _estimate_tokens(embedding_text)

    # Base provenance metadata — always present
    chunk_metadata: Dict[str, Any] = {
        "domain_id": record.domain_id,
        "version": record.version,
        "record_id": record.record_id,
        "requirement_id": record.requirement_id,
        "domain_name": record.domain_name,
        "topic": record.topic,
        "authority": record.authority,
        "confidence": record.confidence,
        "india_specific": record.india_specific,
        "source_ids": record.source_ids,
    }

    # Extended provenance from raw record — present in DOMAIN-001/002 schemas
    # Safely pull fields from original_raw without fabricating values
    raw = record.original_raw or {}
    for extra_key in ("title", "severity", "verification_status", "languages", "applicability"):
        val = raw.get(extra_key)
        if val is not None:
            chunk_metadata[extra_key] = val

    return EmbeddingReadyChunk(
        domain_id=record.domain_id,
        version=record.version,
        record_id=record.record_id,
        requirement_id=record.requirement_id,
        chunk_index=chunk_index,
        embedding_text=embedding_text,
        chunk_metadata=chunk_metadata,
        estimated_tokens=estimated_tokens,
    )



def chunk_normalized_domain(domain: NormalizedDomain) -> List[EmbeddingReadyChunk]:
    """
    Generate all EmbeddingReadyChunk objects for an entire NormalizedDomain.

    chunk_index is 0-based and sequential within the domain.
    Failures on individual records are logged and skipped; they never
    abort the entire domain's chunk generation.
    """
    chunks: List[EmbeddingReadyChunk] = []

    for idx, record in enumerate(domain.records):
        try:
            chunk = chunk_canonical_record(record, chunk_index=idx)
            chunks.append(chunk)
        except Exception as exc:
            logger.warning(
                "Failed to chunk record %s in domain %s: %s",
                record.record_id, domain.domain_id, exc,
            )

    logger.info(
        "Chunked domain %s %s: %d chunks generated",
        domain.domain_id, domain.version, len(chunks),
    )
    return chunks
