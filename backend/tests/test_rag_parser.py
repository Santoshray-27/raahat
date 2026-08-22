"""
test_rag_parser.py — ZORO ⚔️ RAG Pipeline Tests

Tests for the RAG parser, normalizer, and chunker.

Final corpus (5 frozen files):
  DOMAIN-001.json — 12 records (Road Accident, Schema C: evidence_summary + safe_actions list)
  DOMAIN-002.json — 36 records (Fire Emergency, Schema C: content + safe_actions list)
  DOMAIN-003.json — 13 records (First Aid, Schema A: answer + key_actions)
  DOMAIN-004.v2    —  8 records (Vehicle Breakdown, Schema A: answer + key_actions)
  DOMAIN-005.v2   — 30 records (Tyre/Puncture, Schema B: evidence_summary + safe_action string)
  TOTAL = 99 records

Test coverage:
  1.  DOMAIN-003 parses correctly                          (Schema A, 13 records)
  2.  DOMAIN-005.v2 parses correctly                       (Schema B, 30 records)
  3.  DOMAIN-001 parses correctly with 12 knowledge_records (Schema C, Road Accident)
  4.  DOMAIN-002 parses correctly with 36 knowledge_records (Schema C, Fire Emergency)
  5.  Filename / version extraction
  6.  Canonical field normalization (Schema A, B, C)
  7.  Source metadata preservation
  8.  Chunk completeness (safe actions + prohibited + escalation together)
  9.  No fabricated content in canonical records or chunks
  10. 99-record full corpus batch parse

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

def _is_corpus_empty() -> bool:
    for path in [_REPO_ROOT / "data" / "raw", _REPO_ROOT / "ai" / "rag" / "data", _RAG_DIR]:
        if path.exists():
            try:
                if any(f.is_file() and f.stat().st_size > 0 for f in path.iterdir()):
                    return False
            except Exception:
                pass
    return True

pytestmark = pytest.mark.skipif(
    _is_corpus_empty(),
    reason="RAG corpus not present (Satwik's scope)"
)


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
# 2. DOMAIN-005.v2 — Fixed JSON → successful parse
# ===========================================================================

class TestDomain005v2Parsing:
    """
    DOMAIN-005.v2.json was truncated but is now fixed.
    The parser must return status=PARSED and find 30 records.
    """

    @pytest.fixture(scope="class")
    def parsed(self):
        return parse_domain_file(_RAG_DIR / "DOMAIN-005.v2.json")

    def test_status_is_parsed(self, parsed):
        assert parsed.status == ParseStatus.PARSED

    def test_domain_id_extracted_from_filename(self, parsed):
        assert parsed.domain_id == "DOMAIN-005"

    def test_version_extracted_from_filename(self, parsed):
        assert parsed.version == "v2"

    def test_has_knowledge_records(self, parsed):
        assert len(parsed.knowledge_records) == 30

    def test_no_sources(self, parsed):
        assert parsed.sources == []

    def test_file_hash_still_computed(self, parsed):
        assert parsed.file_hash is not None
        assert len(parsed.file_hash) == 64

    def test_raw_json_is_not_none(self, parsed):
        assert parsed.raw_json is not None


# ===========================================================================
# 3. DOMAIN-006.v2 — REMOVED FROM FINAL CORPUS
# ===========================================================================

class TestDomain006v2Parsing:
    """
    DOMAIN-006.v2 was removed from the final corpus during the normalization
    phase. All tests in this class are skipped to prevent false failures.
    """

    @pytest.mark.skip(reason="DOMAIN-006.v2.json removed from final corpus")
    def test_status_is_parsed(self):
        pass

    @pytest.mark.skip(reason="DOMAIN-006.v2.json removed from final corpus")
    def test_domain_id(self):
        pass

    @pytest.mark.skip(reason="DOMAIN-006.v2.json removed from final corpus")
    def test_version(self):
        pass

    @pytest.mark.skip(reason="DOMAIN-006.v2.json removed from final corpus")
    def test_zero_knowledge_records(self):
        pass

    @pytest.mark.skip(reason="DOMAIN-006.v2.json removed from final corpus")
    def test_sources_extracted(self):
        pass

    @pytest.mark.skip(reason="DOMAIN-006.v2.json removed from final corpus")
    def test_knowledge_requirements_present(self):
        pass

    @pytest.mark.skip(reason="DOMAIN-006.v2.json removed from final corpus")
    def test_has_records_is_false(self):
        pass

    @pytest.mark.skip(reason="DOMAIN-006.v2.json removed from final corpus")
    def test_is_parseable_is_true(self):
        pass


# ===========================================================================
# 4. DOMAIN-001 — Schema C, 12 knowledge records (Road Accident)
# ===========================================================================

class TestDomain001Parsing:
    """DOMAIN-001 is the Road Accident domain with 12 knowledge records."""

    @pytest.fixture(scope="class")
    def parsed(self):
        return parse_domain_file(_RAG_DIR / "DOMAIN-001.json")

    def test_status_is_parsed(self, parsed):
        assert parsed.status == ParseStatus.PARSED

    def test_domain_id(self, parsed):
        assert parsed.domain_id == "DOMAIN-001"

    def test_domain_name(self, parsed):
        assert parsed.raw_domain_name == "Road Accident"

    def test_has_12_knowledge_records(self, parsed):
        assert len(parsed.knowledge_records) == 12

    def test_has_records_is_true(self, parsed):
        assert parsed.has_records is True

    def test_reason_is_none(self, parsed):
        assert parsed.reason is None

    def test_first_record_uses_schema_c_fields(self, parsed):
        """Schema C: evidence_summary + safe_actions (list) + unsafe_actions (list)"""
        raw = parsed.knowledge_records[0].raw
        assert "evidence_summary" in raw or "content" in raw
        assert "safe_actions" in raw
        assert "unsafe_actions" in raw

    def test_records_have_requirement_id(self, parsed):
        for rec in parsed.knowledge_records:
            assert "requirement_id" in rec.raw


# ===========================================================================
# 5 & 6. Empty files → graceful skip (REMOVED: files no longer empty)
# ===========================================================================

class TestEmptyFileHandling:
    """
    DOMAIN-002 and DOMAIN-004.v2 were previously empty placeholder files.
    Both are now fully populated. These tests verify the production state.
    """

    def test_domain002_is_now_fully_parsed(self):
        """DOMAIN-002.json is populated with 36 Fire Emergency records."""
        result = parse_domain_file(_RAG_DIR / "DOMAIN-002.json")
        assert result.status == ParseStatus.PARSED
        assert len(result.knowledge_records) == 36

    def test_domain004v2_is_now_fully_parsed(self):
        """DOMAIN-004.v2.json is populated with 8 Vehicle Breakdown records."""
        result = parse_domain_file(_RAG_DIR / "DOMAIN-004.v2.json")
        assert result.status == ParseStatus.PARSED
        assert len(result.knowledge_records) == 8




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
        """A non-existent domain file path returns None from normalize_domain."""
        # DOMAIN-006.v2 was removed. Use a skipped parse as the "no records" scenario.
        import tempfile, pathlib
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            f.write(b"")  # empty file
            tmp = pathlib.Path(f.name)
        try:
            parsed = parse_domain_file(tmp)
            normalized = normalize_domain(parsed)
            assert normalized is None
        finally:
            tmp.unlink(missing_ok=True)

    def test_domain002_normalization_returns_36_records(self):
        """DOMAIN-002 uses Schema C (content field) → 36 canonical records."""
        parsed = parse_domain_file(_RAG_DIR / "DOMAIN-002.json")
        normalized = normalize_domain(parsed)
        assert normalized is not None
        assert len(normalized.records) == 36
        # Verify content field was correctly mapped to answer
        first = normalized.records[0]
        assert first.answer is not None and len(first.answer) > 10

    def test_domain002_safe_actions_correctly_extracted(self):
        """Schema C safe_actions list → canonical record.safe_actions."""
        parsed = parse_domain_file(_RAG_DIR / "DOMAIN-002.json")
        normalized = normalize_domain(parsed)
        assert normalized is not None
        for rec in normalized.records:
            assert len(rec.safe_actions) > 0, (
                f"DOMAIN-002 record {rec.record_id} has no safe_actions"
            )

    def test_domain005_normalization_returns_30_records(self):
        parsed = parse_domain_file(_RAG_DIR / "DOMAIN-005.v2.json")
        normalized = normalize_domain(parsed)
        assert normalized is not None
        assert len(normalized.records) == 30


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

    def test_domain001_sources_extracted(self):
        """DOMAIN-001 uses a sources list — must be extracted correctly."""
        parsed = parse_domain_file(_RAG_DIR / "DOMAIN-001.json")
        normalized = normalize_domain(parsed)
        assert normalized is not None
        # sources are present in DOMAIN-001 source_registry
        assert isinstance(normalized.sources, list)

    def test_domain001_sources_may_be_empty(self):
        """DOMAIN-001 sources list should be a list regardless of length."""
        parsed = parse_domain_file(_RAG_DIR / "DOMAIN-001.json")
        # sources list should be a list — this is correct, not an error
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

    def test_all_5_files_have_no_fabricated_records(self):
        """All 5 final corpus files must produce clean non-fabricated records."""
        final_files = [
            "DOMAIN-001.json", "DOMAIN-002.json", "DOMAIN-003.json",
            "DOMAIN-004.v2.json", "DOMAIN-005.v2.json",
        ]
        for filename in final_files:
            result = parse_domain_file(_RAG_DIR / filename)
            assert result.status == ParseStatus.PARSED, f"{filename} failed to parse"
            assert len(result.knowledge_records) > 0, f"{filename} has no records"
            for rec in result.knowledge_records:
                raw_str = str(rec.raw)
                self._assert_no_fabrication(raw_str, f"{filename} raw record {rec.raw.get('record_id')}")

    def test_all_5_files_normalize_without_fabrication(self):
        """All normalized canonical records must be free of fabricated markers."""
        final_files = [
            "DOMAIN-001.json", "DOMAIN-002.json", "DOMAIN-003.json",
            "DOMAIN-004.v2.json", "DOMAIN-005.v2.json",
        ]
        for filename in final_files:
            result = parse_domain_file(_RAG_DIR / filename)
            normalized = normalize_domain(result)
            assert normalized is not None
            for rec in normalized.records:
                self._assert_no_fabrication(
                    str(rec.safe_actions) + str(rec.prohibited_actions) + str(rec.answer or ""),
                    f"{filename} canonical record {rec.record_id}",
                )


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
        assert len(all_results) == 5  # Exactly 5 final corpus files

    def test_no_empty_files_remain(self, all_results):
        """All 5 files are now fully populated — no empty file skips expected."""
        skipped = [r for r in all_results if r.reason == "empty_file"]
        assert len(skipped) == 0

    def test_json_parse_errors_handled_gracefully(self, all_results):
        parse_error = [r for r in all_results if r.reason == "json_parse_error"]
        assert len(parse_error) == 0  # All 5 files must parse cleanly

    def test_all_5_files_parseable_with_records(self, all_results):
        with_records = [r for r in all_results if r.has_records]
        assert len(with_records) == 5  # All 5 must have records

    def test_total_records_is_exactly_99(self, all_results):
        """Final corpus must produce exactly 99 records."""
        total = sum(len(r.knowledge_records) for r in all_results)
        assert total == 99, f"Expected 99 records, got {total}"

    def test_per_file_record_counts(self, all_results):
        """Verify exact record counts for each of the 5 final files."""
        by_filename = {r.filename: len(r.knowledge_records) for r in all_results}
        assert by_filename.get("DOMAIN-001.json") == 12
        assert by_filename.get("DOMAIN-002.json") == 36
        assert by_filename.get("DOMAIN-003.json") == 13
        assert by_filename.get("DOMAIN-004.v2.json") == 8
        assert by_filename.get("DOMAIN-005.v2.json") == 30

