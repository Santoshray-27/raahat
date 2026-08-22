"""
M3-G — Focused tests for the RAG Context Builder.

Tests:
1. Empty input → has_content=False, no text
2. Single chunk produces correct section markers
3. Metadata fields are correctly included/excluded
4. Multi-chunk output is deterministic and properly separated
5. max_chunks is enforced
6. top_score is the maximum score across chunks
"""
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from app.services.rag_context_builder import RagContextBuilder, BuiltContext, rag_context_builder


CHUNK_BLEEDING = (
    "[EMERGENCY PROTOCOL | First Aid | KR-001: Severe bleeding]\n\nApply firm pressure.",
    0.78,
    {
        "domain_id": "DOMAIN-003",
        "domain_name": "First Aid",
        "requirement_id": "KR-001",
        "topic": "Severe bleeding control",
        "authority": "Official",
        "confidence": "High",
        "india_specific": False,
    },
)

CHUNK_FRACTURE = (
    "[EMERGENCY PROTOCOL | First Aid | KR-005: Fracture]\n\nImmobilize the limb.",
    0.62,
    {
        "domain_id": "DOMAIN-003",
        "domain_name": "First Aid",
        "requirement_id": "KR-005",
        "topic": "Suspected fracture immobilization",
        "authority": "Official",
        "confidence": "Medium",
        "india_specific": False,
    },
)

CHUNK_MINIMAL = (
    "Minimal chunk, no metadata.",
    0.55,
    {},
)


# ---------------------------------------------------------------------------
# 1. Empty input
# ---------------------------------------------------------------------------

def test_empty_chunks_returns_no_content():
    builder = RagContextBuilder()
    result = builder.build([])
    assert result.has_content is False
    assert result.chunks_used == 0
    assert result.top_score is None
    assert result.context_text == ""


# ---------------------------------------------------------------------------
# 2. Single chunk produces required structure markers
# ---------------------------------------------------------------------------

def test_single_chunk_has_section_markers():
    builder = RagContextBuilder()
    result = builder.build([CHUNK_BLEEDING])
    assert result.has_content is True
    assert result.chunks_used == 1
    assert "[RAAHAT VERIFIED KNOWLEDGE]" in result.context_text
    assert "[END RAAHAT VERIFIED KNOWLEDGE]" in result.context_text


def test_single_chunk_includes_knowledge_header():
    builder = RagContextBuilder()
    result = builder.build([CHUNK_BLEEDING])
    assert "[Knowledge 1]" in result.context_text


def test_single_chunk_preserves_content():
    builder = RagContextBuilder()
    result = builder.build([CHUNK_BLEEDING])
    assert "Apply firm pressure." in result.context_text


# ---------------------------------------------------------------------------
# 3. Metadata fields
# ---------------------------------------------------------------------------

def test_metadata_domain_name_included():
    builder = RagContextBuilder()
    result = builder.build([CHUNK_BLEEDING])
    assert "First Aid" in result.context_text


def test_metadata_requirement_id_included():
    builder = RagContextBuilder()
    result = builder.build([CHUNK_BLEEDING])
    assert "KR-001" in result.context_text


def test_metadata_authority_included():
    builder = RagContextBuilder()
    result = builder.build([CHUNK_BLEEDING])
    assert "Official" in result.context_text


def test_metadata_confidence_included():
    builder = RagContextBuilder()
    result = builder.build([CHUNK_BLEEDING])
    assert "High" in result.context_text


def test_metadata_topic_included():
    builder = RagContextBuilder()
    result = builder.build([CHUNK_BLEEDING])
    assert "Severe bleeding control" in result.context_text


def test_minimal_metadata_does_not_crash():
    """Chunk with empty metadata must still produce valid output."""
    builder = RagContextBuilder()
    result = builder.build([CHUNK_MINIMAL])
    assert result.has_content is True
    assert "Minimal chunk" in result.context_text
    assert "RAAHAT Corpus" in result.context_text  # default source


# ---------------------------------------------------------------------------
# 4. Multi-chunk output
# ---------------------------------------------------------------------------

def test_two_chunks_both_numbered():
    builder = RagContextBuilder()
    result = builder.build([CHUNK_BLEEDING, CHUNK_FRACTURE])
    assert "[Knowledge 1]" in result.context_text
    assert "[Knowledge 2]" in result.context_text


def test_two_chunks_separator_present():
    builder = RagContextBuilder()
    result = builder.build([CHUNK_BLEEDING, CHUNK_FRACTURE])
    assert "---" in result.context_text


def test_two_chunks_both_contents_present():
    builder = RagContextBuilder()
    result = builder.build([CHUNK_BLEEDING, CHUNK_FRACTURE])
    assert "Apply firm pressure." in result.context_text
    assert "Immobilize the limb." in result.context_text


def test_output_is_deterministic():
    """Same inputs must produce identical output."""
    builder = RagContextBuilder()
    result_a = builder.build([CHUNK_BLEEDING, CHUNK_FRACTURE])
    result_b = builder.build([CHUNK_BLEEDING, CHUNK_FRACTURE])
    assert result_a.context_text == result_b.context_text


# ---------------------------------------------------------------------------
# 5. max_chunks enforcement
# ---------------------------------------------------------------------------

def test_max_chunks_limits_output():
    builder = RagContextBuilder()
    many = [CHUNK_BLEEDING, CHUNK_FRACTURE, CHUNK_MINIMAL]
    result = builder.build(many, max_chunks=2)
    assert result.chunks_used == 2
    assert "[Knowledge 3]" not in result.context_text


# ---------------------------------------------------------------------------
# 6. top_score is the max score
# ---------------------------------------------------------------------------

def test_top_score_is_maximum():
    builder = RagContextBuilder()
    result = builder.build([CHUNK_BLEEDING, CHUNK_FRACTURE])
    assert result.top_score == pytest.approx(0.78, abs=1e-6)


# ---------------------------------------------------------------------------
# 7. Query header (optional)
# ---------------------------------------------------------------------------

def test_query_included_when_provided():
    builder = RagContextBuilder()
    result = builder.build([CHUNK_BLEEDING], query="How to stop bleeding?")
    assert "How to stop bleeding?" in result.context_text


def test_module_level_singleton_works():
    result = rag_context_builder.build([CHUNK_BLEEDING])
    assert result.has_content is True
