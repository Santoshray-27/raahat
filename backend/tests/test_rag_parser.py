"""
test_rag_parser.py — ZORO ⚔️ RAG Pipeline — Milestone 1 Tests

Tests for the RAG parser, normalizer, and chunker.

Test coverage:
  1.  DOMAIN-003 parses correctly                          (Format A, 13 records)
  2.  DOMAIN-005.v2 is truncated JSON → skipped gracefully (json_parse_error)
  3.  DOMAIN-006.v2 parses correctly with 0 records        (Format B)
  4.  DOMAIN-001 parses correctly with 0 knowledge_records (gap-analysis file)
  5.  DOMAIN-002 empty file → skipped gracefully           (empty_file)
  6.  DOMAIN-004.v2 empty file → skipped gracefully        (empty_file)
  7.  Filename / version extraction
  8.  Canonical field normalization (Schema A and Schema B)
  9.  Source metadata preservation
 10.  Chunk completeness (safe actions + prohibited + escalation together)
 11.  No fabricated content in canonical records or chunks

REQUIREMENTS:
  - No Gemini API calls.
  - No PostgreSQL connections.
  - No modifications to any non-RAG files.
  - Uses actual RAG/*.json files from the project corpus directory.
"""

from __future__ import annotations

import os
import pathlib
import sys

import pytest

# ---------------------------------------------------------------------------
# Ensure backend package is on sys.path so imports resolve correctly when
# pytest is run from the repo root or from backend/
# ---------------------------------------------------------------------------
_BACKEND_DIR = pathlib.Path(__file__).parent.parent.absolute()
if str(_BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(_BACKEND_DIR))

# RAG corpus directory — resolved relative to the repo root
_REPO_ROOT = _BACKEND_DIR.parent
_RAG_DIR = _REPO_ROOT / "RAG"

from app.services.rag_parser import (
    ParseStatus,
    extract_domain_and_version,
    parse_domain_file,
    parse_corpus_directory,
)
from app.services.rag_normalizer import (
    CanonicalRecord,
    NormalizedDomain,
    normalize_domain,
    normalize_record,
)
from app.services.rag_chunker import (
    EmbeddingReadyChunk,
    chunk_canonical_record,
    chunk_normalized_domain,
)


# ===========================================================================
# 7. Filename / Version Extraction
# ===========================================================================

class TestFilenameVersionExtraction:
    """Test extract_domain_and_version() for all known filename patterns."""

    def test_versioned_filename(self):
        domain_id, version = extract_domain_and_version("DOMAIN-005.v2.json")
        assert domain_id == "DOMAIN-005"
        assert version == "v2"

    def test_unversioned_filename_defaults_v1(self):
        domain_id, version = extract_domain_and_version("DOMAIN-001.json")
        assert domain_id == "DOMAIN-001"
        assert version == "v1"

    def test_v1_explicit_filename(self):
        domain_id, version = extract_domain_and_version("DOMAIN-007.v1.json")
        assert domain_id == "DOMAIN-007"
        assert version == "v1"

    def test_high_numbered_domain(self):
        domain_id, version = extract_domain_and_version("DOMAIN-099.v3.json")
        assert domain_id == "DOMAIN-099"
        assert version == "v3"

    def test_case_insensitive(self):
        domain_id, version = extract_domain_and_version("domain-004.v1.json")
        assert domain_id == "DOMAIN-004"
        assert version == "v1"


# ===========================================================================
# 1. DOMAIN-003 — Format A, production-ready records
# ===========================================================================

class TestDomain003Parsing:
    """DOMAIN-003 is the First Aid domain with 13+ knowledge records."""

    @pytest.fixture(scope="class")
    def parsed(self):
        return parse_domain_file(_RAG_DIR / "DOMAIN-003.json")

    def test_status_is_parsed(self, parsed):
        assert parsed.status == ParseStatus.PARSED

    def test_domain_id_is_domain_003(self, parsed):
        assert parsed.domain_id == "DOMAIN-003"

    def test_version_is_v1(self, parsed):
        assert parsed.version == "v1"

    def test_domain_name_is_first_aid(self, parsed):
        assert parsed.raw_domain_name == "First Aid"

    def test_has_knowledge_records(self, parsed):
        assert parsed.has_records
        assert len(parsed.knowledge_records) >= 10

    def test_has_sources(self, parsed):
        assert len(parsed.sources) >= 1

    def test_has_knowledge_requirements(self, parsed):
        assert len(parsed.knowledge_requirements) >= 5

    def test_file_hash_is_set(self, parsed):
        assert parsed.file_hash is not None
        assert len(parsed.file_hash) == 64  # SHA-256 hex

    def test_raw_json_preserved(self, parsed):
        assert parsed.raw_json is not None
        assert "knowledge_records" in parsed.raw_json

    def test_first_record_is_rec_001(self, parsed):
        first = parsed.knowledge_records[0]
        assert first.raw.get("record_id") == "REC-001"

    def test_records_have_expected_schema_a_fields(self, parsed):
        first = parsed.knowledge_records[0].raw
        # Schema A: answer, key_actions, do_not, escalation_criteria
        assert "answer" in first or "evidence_summary" in first
        assert "source_ids" in first

    def test_no_fabricated_records(self, parsed):
        """All record_ids must match the source file — no invented records."""
        rec_ids = {r.raw.get("record_id") for r in parsed.knowledge_records}
        assert "FABRICATED" not in str(rec_ids)
        assert all(rid and rid.startswith("REC-") for rid in rec_ids if rid)


# ===========================================================================
# 2. DOMAIN-005.v2 — Truncated JSON → graceful skip
# ===========================================================================

class TestDomain005v2TruncatedParsing:
    """
    DOMAIN-005.v2.json is confirmed to be a truncated file (cuts off mid-JSON).
    The parser must return status=SKIPPED with reason=json_parse_error.
    It must NOT crash or raise an exception.
    """

    @pytest.fixture(scope="class")
    def parsed(self):
        return parse_domain_file(_RAG_DIR / "DOMAIN-005.v2.json")

    def test_status_is_skipped(self, parsed):
        assert parsed.status == ParseStatus.SKIPPED

    def test_reason_is_json_parse_error(self, parsed):
        assert parsed.reason == "json_parse_error"

    def test_domain_id_extracted_from_filename(self, parsed):
        assert parsed.domain_id == "DOMAIN-005"

    def test_version_extracted_from_filename(self, parsed):
        assert parsed.version == "v2"

    def test_no_knowledge_records(self, parsed):
        assert parsed.knowledge_records == []

    def test_no_sources(self, parsed):
        assert parsed.sources == []

    def test_file_hash_still_computed(self, parsed):
        # Hash is computed from raw bytes BEFORE JSON parsing
        assert parsed.file_hash is not None
        assert len(parsed.file_hash) == 64

    def test_raw_json_is_none(self, parsed):
        # JSON parse failed, so raw_json must be None
        assert parsed.raw_json is None


# ===========================================================================
# 3. DOMAIN-006.v2 — Format B, 0 knowledge_records
# ===========================================================================

class TestDomain006v2Parsing:
    """
    DOMAIN-006.v2 is a Format B file with sources and coverage metadata
    but no knowledge_records key. It should parse successfully with 0 records.
    """

    @pytest.fixture(scope="class")
    def parsed(self):
        return parse_domain_file(_RAG_DIR / "DOMAIN-006.v2.json")

    def test_status_is_parsed(self, parsed):
        assert parsed.status == ParseStatus.PARSED

    def test_domain_id(self, parsed):
        assert parsed.domain_id == "DOMAIN-006"

    def test_version(self, parsed):
        assert parsed.version == "v2"

    def test_zero_knowledge_records(self, parsed):
        assert len(parsed.knowledge_records) == 0

    def test_sources_extracted(self, parsed):
        # Has either recommended_rag_corpus or source_registry
        assert len(parsed.sources) > 0

    def test_knowledge_requirements_present(self, parsed):
        assert len(parsed.knowledge_requirements) > 0

    def test_has_records_is_false(self, parsed):
        assert parsed.has_records is False

    def test_is_parseable_is_true(self, parsed):
        assert parsed.is_parseable is True


# ===========================================================================
# 4. DOMAIN-001 — Format A, 0 knowledge_records (gap-analysis file)
# ===========================================================================

class TestDomain001Parsing:
    """DOMAIN-001 is a Format A gap-analysis file: valid JSON, 0 records."""

    @pytest.fixture(scope="class")
    def parsed(self):
        return parse_domain_file(_RAG_DIR / "DOMAIN-001.json")

    def test_status_is_parsed(self, parsed):
        assert parsed.status == ParseStatus.PARSED

    def test_domain_id(self, parsed):
        assert parsed.domain_id == "DOMAIN-001"

    def test_zero_knowledge_records(self, parsed):
        assert len(parsed.knowledge_records) == 0

    def test_has_records_is_false(self, parsed):
        assert parsed.has_records is False

    def test_has_knowledge_requirements(self, parsed):
        assert len(parsed.knowledge_requirements) > 0

    def test_has_knowledge_gaps(self, parsed):
        assert len(parsed.knowledge_gaps) > 0

    def test_reason_is_none(self, parsed):
        assert parsed.reason is None


# ===========================================================================
# 5 & 6. Empty files → graceful skip
# ===========================================================================

class TestEmptyFileHandling:
    """DOMAIN-002.json and DOMAIN-004.v2.json are empty (0 bytes)."""

    @pytest.mark.parametrize("filename,expected_domain,expected_version", [
        ("DOMAIN-002.json", "DOMAIN-002", "v1"),
        ("DOMAIN-004.v2.json", "DOMAIN-004", "v2"),
    ])
    def test_empty_file_is_skipped(self, filename, expected_domain, expected_version):
        result = parse_domain_file(_RAG_DIR / filename)
        assert result.status == ParseStatus.SKIPPED, (
            f"{filename}: expected SKIPPED, got {result.status}"
        )

    @pytest.mark.parametrize("filename,expected_domain,expected_version", [
        ("DOMAIN-002.json", "DOMAIN-002", "v1"),
        ("DOMAIN-004.v2.json", "DOMAIN-004", "v2"),
    ])
    def test_reason_is_empty_file(self, filename, expected_domain, expected_version):
        result = parse_domain_file(_RAG_DIR / filename)
        assert result.reason == "empty_file", (
            f"{filename}: expected reason='empty_file', got reason='{result.reason}'"
        )

    @pytest.mark.parametrize("filename,expected_domain,expected_version", [
        ("DOMAIN-002.json", "DOMAIN-002", "v1"),
        ("DOMAIN-004.v2.json", "DOMAIN-004", "v2"),
    ])
    def test_domain_and_version_from_filename(self, filename, expected_domain, expected_version):
        result = parse_domain_file(_RAG_DIR / filename)
        assert result.domain_id == expected_domain
        assert result.version == expected_version

    @pytest.mark.parametrize("filename,expected_domain,expected_version", [
        ("DOMAIN-002.json", "DOMAIN-002", "v1"),
        ("DOMAIN-004.v2.json", "DOMAIN-004", "v2"),
    ])
    def test_no_records_on_empty_file(self, filename, expected_domain, expected_version):
        result = parse_domain_file(_RAG_DIR / filename)
        assert result.knowledge_records == []
        assert result.sources == []

    @pytest.mark.parametrize("filename,expected_domain,expected_version", [
        ("DOMAIN-002.json", "DOMAIN-002", "v1"),
        ("DOMAIN-004.v2.json", "DOMAIN-004", "v2"),
    ])
    def test_no_fabricated_content_on_skip(self, filename, expected_domain, expected_version):
        result = parse_domain_file(_RAG_DIR / filename)
        assert result.raw_json is None
        assert result.raw_domain_name is None


# ===========================================================================
# 8. Canonical Field Normalization (Schema A and B)
# ===========================================================================

class TestCanonicalNormalization:
    """Test that normalize_record correctly maps both schema formats."""

    @pytest.fixture(scope="class")
    def domain003_normalized(self):
        parsed = parse_domain_file(_RAG_DIR / "DOMAIN-003.json")
        return normalize_domain(parsed)

    def test_normalize_domain003_returns_normalized_domain(self, domain003_normalized):
        assert domain003_normalized is not None
        assert isinstance(domain003_normalized, NormalizedDomain)

    def test_normalize_domain003_record_count(self, domain003_normalized):
        assert domain003_normalized.record_count >= 10

    def test_schema_a_record_has_requirement_id(self, domain003_normalized):
        rec = domain003_normalized.records[0]
        assert rec.requirement_id is not None
        assert rec.requirement_id.startswith("KR-")

    def test_schema_a_record_has_topic(self, domain003_normalized):
        rec = domain003_normalized.records[0]
        assert rec.topic is not None

    def test_schema_a_record_has_safe_actions(self, domain003_normalized):
        """Schema A key_actions → safe_actions"""
        rec = domain003_normalized.records[0]
        assert len(rec.safe_actions) > 0

    def test_schema_a_record_has_prohibited_actions(self, domain003_normalized):
        """Schema A do_not → prohibited_actions"""
        rec = domain003_normalized.records[0]
        assert len(rec.prohibited_actions) > 0

    def test_schema_a_record_has_escalation_criteria(self, domain003_normalized):
        rec = domain003_normalized.records[0]
        assert len(rec.escalation_criteria) > 0

    def test_schema_a_record_has_source_ids(self, domain003_normalized):
        rec = domain003_normalized.records[0]
        assert len(rec.source_ids) > 0

    def test_schema_a_record_preserves_domain_id(self, domain003_normalized):
        for rec in domain003_normalized.records:
            assert rec.domain_id == "DOMAIN-003"

    def test_schema_a_india_specific_is_bool(self, domain003_normalized):
        rec = domain003_normalized.records[0]
        assert isinstance(rec.india_specific, bool)

    def test_original_raw_is_preserved(self, domain003_normalized):
        """original_raw must contain the unmodified source dict."""
        rec = domain003_normalized.records[0]
        assert rec.original_raw.get("record_id") == "REC-001"

    # Schema B: DOMAIN-006.v2 has no knowledge_records → empty list
    def test_schema_b_no_records_returns_empty(self):
        parsed = parse_domain_file(_RAG_DIR / "DOMAIN-006.v2.json")
        normalized = normalize_domain(parsed)
        assert normalized is not None
        assert normalized.record_count == 0

    # Skipped files return None from normalize_domain
    def test_skipped_file_returns_none(self):
        parsed = parse_domain_file(_RAG_DIR / "DOMAIN-002.json")
        normalized = normalize_domain(parsed)
        assert normalized is None

    def test_truncated_file_returns_none(self):
        parsed = parse_domain_file(_RAG_DIR / "DOMAIN-005.v2.json")
        normalized = normalize_domain(parsed)
        assert normalized is None


# ===========================================================================
# 9. Source Metadata Preservation
# ===========================================================================

class TestSourceMetadataPreservation:
    """Sources from recommended_rag_corpus or source_registry must be preserved."""

    def test_domain003_sources_preserved(self):
        parsed = parse_domain_file(_RAG_DIR / "DOMAIN-003.json")
        normalized = normalize_domain(parsed)
        assert normalized is not None
        assert len(normalized.sources) > 0
        # Each source should have a source_name
        for src in normalized.sources:
            assert "source_name" in src

    def test_domain006v2_sources_preserved(self):
        """Format B uses source_registry → should be extracted correctly."""
        parsed = parse_domain_file(_RAG_DIR / "DOMAIN-006.v2.json")
        normalized = normalize_domain(parsed)
        assert normalized is not None
        assert len(normalized.sources) > 0

    def test_domain001_sources_may_be_empty(self):
        """DOMAIN-001 has no verified sources — sources=[] is correct."""
        parsed = parse_domain_file(_RAG_DIR / "DOMAIN-001.json")
        # sources list should be [] — this is correct, not an error
        assert isinstance(parsed.sources, list)

    def test_source_url_preserved_where_present(self):
        parsed = parse_domain_file(_RAG_DIR / "DOMAIN-003.json")
        normalized = normalize_domain(parsed)
        assert normalized is not None
        sources_with_urls = [s for s in normalized.sources if s.get("source_url")]
        assert len(sources_with_urls) > 0


# ===========================================================================
# 10. Chunk Completeness — safe actions, prohibited, escalation preserved
# ===========================================================================

class TestChunkCompleteness:
    """
    Chunks must never separate safe actions, prohibited actions, or
    escalation criteria. All must be present in a single chunk text.
    """

    @pytest.fixture(scope="class")
    def first_chunk(self):
        parsed = parse_domain_file(_RAG_DIR / "DOMAIN-003.json")
        normalized = normalize_domain(parsed)
        chunks = chunk_normalized_domain(normalized)
        return chunks[0]  # REC-001: Controlling severe external bleeding

    def test_chunk_text_is_non_empty(self, first_chunk):
        assert first_chunk.embedding_text.strip() != ""

    def test_chunk_contains_safe_actions(self, first_chunk):
        text = first_chunk.embedding_text
        assert "What To Do" in text or "key_actions" in text or "Apply" in text

    def test_chunk_contains_prohibited_actions(self, first_chunk):
        text = first_chunk.embedding_text
        assert "Do NOT Do" in text or "do_not" in text or "Do not" in text.lower()

    def test_chunk_contains_escalation(self, first_chunk):
        text = first_chunk.embedding_text
        assert "Emergency" in text or "escalation" in text.lower() or "Bleeding" in text

    def test_chunk_contains_header_with_domain(self, first_chunk):
        text = first_chunk.embedding_text
        assert "First Aid" in text or "DOMAIN-003" in text

    def test_chunk_contains_source_authority(self, first_chunk):
        text = first_chunk.embedding_text
        assert "Authority" in text or "Official" in text or "SRC-" in text

    def test_chunk_index_is_zero_for_first(self, first_chunk):
        assert first_chunk.chunk_index == 0

    def test_chunk_metadata_has_required_keys(self, first_chunk):
        meta = first_chunk.chunk_metadata
        assert "domain_id" in meta
        assert "record_id" in meta
        assert "requirement_id" in meta
        assert "source_ids" in meta

    def test_chunk_metadata_domain_id_correct(self, first_chunk):
        assert first_chunk.chunk_metadata["domain_id"] == "DOMAIN-003"

    def test_chunk_metadata_record_id_correct(self, first_chunk):
        assert first_chunk.chunk_metadata["record_id"] == "REC-001"

    def test_all_domain003_chunks_have_non_empty_text(self):
        parsed = parse_domain_file(_RAG_DIR / "DOMAIN-003.json")
        normalized = normalize_domain(parsed)
        chunks = chunk_normalized_domain(normalized)
        assert len(chunks) > 0
        for chunk in chunks:
            assert chunk.embedding_text.strip() != "", (
                f"Chunk {chunk.record_id} has empty embedding_text"
            )

    def test_chunk_indices_are_sequential(self):
        parsed = parse_domain_file(_RAG_DIR / "DOMAIN-003.json")
        normalized = normalize_domain(parsed)
        chunks = chunk_normalized_domain(normalized)
        for expected_idx, chunk in enumerate(chunks):
            assert chunk.chunk_index == expected_idx


# ===========================================================================
# 11. No Fabricated Content
# ===========================================================================

class TestNoFabricatedContent:
    """
    Normalized records and chunks must only contain content derived from
    the source JSON files. No invented data, mock text, or placeholder values.
    """

    FABRICATION_MARKERS = [
        "MOCK", "FAKE", "PLACEHOLDER", "TODO", "SAMPLE_DATA",
        "FABRICATED", "lorem ipsum", "example.com/fake",
    ]

    def _assert_no_fabrication(self, text: str, context: str):
        for marker in self.FABRICATION_MARKERS:
            assert marker.lower() not in text.lower(), (
                f"Fabrication marker '{marker}' found in {context}"
            )

    def test_domain003_records_no_fabrication(self):
        parsed = parse_domain_file(_RAG_DIR / "DOMAIN-003.json")
        normalized = normalize_domain(parsed)
        for rec in normalized.records:
            self._assert_no_fabrication(
                str(rec.safe_actions) + str(rec.prohibited_actions) + str(rec.escalation_criteria),
                f"record {rec.record_id}",
            )

    def test_domain003_chunks_no_fabrication(self):
        parsed = parse_domain_file(_RAG_DIR / "DOMAIN-003.json")
        normalized = normalize_domain(parsed)
        chunks = chunk_normalized_domain(normalized)
        for chunk in chunks:
            self._assert_no_fabrication(chunk.embedding_text, f"chunk {chunk.record_id}")

    def test_empty_file_has_no_fabricated_records(self):
        for filename in ["DOMAIN-002.json", "DOMAIN-004.v2.json"]:
            result = parse_domain_file(_RAG_DIR / filename)
            assert result.knowledge_records == [], (
                f"{filename}: expected no records on empty file, got {len(result.knowledge_records)}"
            )
            assert result.raw_json is None

    def test_skipped_normalized_is_none(self):
        """Skipped files must not produce any canonical records at all."""
        parsed = parse_domain_file(_RAG_DIR / "DOMAIN-002.json")
        assert normalize_domain(parsed) is None


# ===========================================================================
# Corpus batch parse smoke test
# ===========================================================================

class TestCorpusBatchParse:
    """Smoke test for parse_corpus_directory over the full RAG/ directory."""

    @pytest.fixture(scope="class")
    def all_results(self):
        return parse_corpus_directory(_RAG_DIR)

    def test_all_files_return_a_result(self, all_results):
        """Every JSON file must produce a result — no unhandled exceptions."""
        assert len(all_results) >= 9  # At least 9 known files

    def test_empty_files_are_skipped(self, all_results):
        skipped = [r for r in all_results if r.reason == "empty_file"]
        assert len(skipped) >= 2  # DOMAIN-002 and DOMAIN-004.v2

    def test_truncated_file_is_skipped(self, all_results):
        parse_error = [r for r in all_results if r.reason == "json_parse_error"]
        assert len(parse_error) >= 1  # DOMAIN-005.v2

    def test_at_least_one_parseable_file_with_records(self, all_results):
        with_records = [r for r in all_results if r.has_records]
        assert len(with_records) >= 1

    def test_total_records_reasonable(self, all_results):
        total = sum(len(r.knowledge_records) for r in all_results)
        # At minimum DOMAIN-003 has 13 records
        assert total >= 13
