from typing import Protocol

from raggae.domain.value_objects.chunking_strategy import ChunkingStrategy


class ChunkingStrategySelector(Protocol):
    """Interface for deterministic chunking strategy selection."""

    def select(
        self,
        has_headings: bool,
        paragraph_count: int,
        average_paragraph_length: int,
    ) -> ChunkingStrategy: ...
