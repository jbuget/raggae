from raggae.domain.value_objects.chunking_strategy import ChunkingStrategy


class DeterministicChunkingStrategySelector:
    """Deterministic selector for chunking strategy.

    Improved heuristic: prefers paragraph chunking for well-structured text
    and heading-based chunking for documents with clear sections.
    Falls back to fixed_window only for very short or unstructured content.
    """

    def select(
        self,
        has_headings: bool,
        paragraph_count: int,
        average_paragraph_length: int,
    ) -> ChunkingStrategy:
        if has_headings:
            return ChunkingStrategy.HEADING_SECTION

        if paragraph_count >= 3 and average_paragraph_length >= 40:
            return ChunkingStrategy.PARAGRAPH

        if paragraph_count >= 2:
            return ChunkingStrategy.PARAGRAPH

        return ChunkingStrategy.FIXED_WINDOW
