"""
M3-C — RAG Context Builder

Responsibility: Convert a list of (RagChunk, similarity_score) pairs into a
compact, deterministic, clearly-delimited context block suitable for injection
into the Gemini generation prompt.

Design principles:
- Retrieved knowledge is clearly marked as VERIFIED KNOWLEDGE, not instructions.
- User input is never modified or mixed into this block.
- The block has a deterministic format so tests can assert on it.
- Source metadata is preserved for grounding.
- If no chunks are provided, an empty string is returned (caller must handle fallback).
"""

from typing import List, Tuple, Optional
from dataclasses import dataclass

# We accept raw tuples here to keep the builder decoupled from SQLAlchemy models.
# Each tuple is (content: str, score: float, metadata: dict)
RagChunkTuple = Tuple[str, float, dict]


@dataclass
class BuiltContext:
    """Output of the context builder."""
    context_text: str           # Full delimited block for prompt injection
    chunks_used: int            # How many chunks made it in
    top_score: Optional[float]  # Highest similarity score among used chunks
    has_content: bool           # False if no usable chunks were provided


class RagContextBuilder:
    """
    Converts retrieved RAG tuples into a grounded context block for prompts.
    """

    SECTION_HEADER = "[RAAHAT VERIFIED KNOWLEDGE]"
    SECTION_FOOTER = "[END RAAHAT VERIFIED KNOWLEDGE]"
    CHUNK_SEPARATOR = "---"

    def build(
        self,
        chunks: List[RagChunkTuple],
        query: Optional[str] = None,
        max_chunks: int = 5,
    ) -> BuiltContext:
        """
        Build a formatted context block from retrieved chunks.

        Args:
            chunks:     List of (content, similarity_score, metadata) tuples.
            query:      Original query, used only for debug/logging header.
            max_chunks: Hard cap on chunks included in context.

        Returns:
            BuiltContext with formatted text and stats.
        """
        if not chunks:
            return BuiltContext(
                context_text="",
                chunks_used=0,
                top_score=None,
                has_content=False,
            )

        usable = chunks[:max_chunks]
        top_score = max(score for _, score, _ in usable) if usable else None

        lines = [self.SECTION_HEADER]
        if query:
            lines.append(f"Query context: {query}")
        lines.append("")

        for idx, (content, score, metadata) in enumerate(usable, start=1):
            # Extract key metadata fields that are useful for emergency grounding
            domain_id = metadata.get("domain_id", "")
            req_id = metadata.get("requirement_id", "")
            authority = metadata.get("authority", "")
            confidence = metadata.get("confidence", "")
            india_specific = metadata.get("india_specific", None)
            domain_name = metadata.get("domain_name", "")
            topic = metadata.get("topic", "")

            # Build source attribution line
            source_parts = []
            if domain_name:
                source_parts.append(domain_name)
            if req_id:
                source_parts.append(req_id)
            if domain_id:
                source_parts.append(f"({domain_id})")
            source_line = " | ".join(source_parts) if source_parts else "RAAHAT Corpus"

            lines.append(f"[Knowledge {idx}]")
            lines.append(f"Source: {source_line}")
            if topic:
                lines.append(f"Topic: {topic}")
            if authority:
                lines.append(f"Authority: {authority}")
            if confidence:
                lines.append(f"Confidence: {confidence}")
            if india_specific is not None:
                lines.append(f"India-specific: {'Yes' if india_specific else 'No'}")
            lines.append(f"Relevance score: {score:.4f}")
            lines.append("Knowledge:")
            lines.append(content.strip())

            if idx < len(usable):
                lines.append(self.CHUNK_SEPARATOR)
            lines.append("")

        lines.append(self.SECTION_FOOTER)

        return BuiltContext(
            context_text="\n".join(lines),
            chunks_used=len(usable),
            top_score=top_score,
            has_content=True,
        )


# Module-level singleton
rag_context_builder = RagContextBuilder()
