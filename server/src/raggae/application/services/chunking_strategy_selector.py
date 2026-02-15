from raggae.domain.value_objects.chunking_strategy import ChunkingStrategy


class ChunkingStrategySelector:
    """Deterministic selector for chunking strategy."""

    def select(
        self,
        has_headings: bool,
        paragraph_count: int,
        average_paragraph_length: int,
    ) -> ChunkingStrategy:
        if has_headings:
            return ChunkingStrategy.HEADING_SECTION

        if paragraph_count >= 3 and average_paragraph_length >= 60:
            return ChunkingStrategy.PARAGRAPH

        return ChunkingStrategy.FIXED_WINDOW
