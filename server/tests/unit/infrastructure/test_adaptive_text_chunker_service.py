from unittest.mock import AsyncMock

from raggae.domain.value_objects.chunking_strategy import ChunkingStrategy
from raggae.infrastructure.services.adaptive_text_chunker_service import AdaptiveTextChunkerService


class TestAdaptiveTextChunkerService:
    async def test_chunk_text_routes_to_paragraph_chunker(self) -> None:
        # Given
        fixed_window_chunker = AsyncMock()
        paragraph_chunker = AsyncMock()
        heading_section_chunker = AsyncMock()
        paragraph_chunker.chunk_text.return_value = ["paragraph chunk"]
        chunker = AdaptiveTextChunkerService(
            fixed_window_chunker=fixed_window_chunker,
            paragraph_chunker=paragraph_chunker,
            heading_section_chunker=heading_section_chunker,
        )

        # When
        result = await chunker.chunk_text("text", ChunkingStrategy.PARAGRAPH)

        # Then
        assert result == ["paragraph chunk"]
        paragraph_chunker.chunk_text.assert_called_once_with("text", ChunkingStrategy.PARAGRAPH)
        heading_section_chunker.chunk_text.assert_not_called()
        fixed_window_chunker.chunk_text.assert_not_called()

    async def test_chunk_text_routes_to_heading_section_chunker(self) -> None:
        # Given
        fixed_window_chunker = AsyncMock()
        paragraph_chunker = AsyncMock()
        heading_section_chunker = AsyncMock()
        heading_section_chunker.chunk_text.return_value = ["section chunk"]
        chunker = AdaptiveTextChunkerService(
            fixed_window_chunker=fixed_window_chunker,
            paragraph_chunker=paragraph_chunker,
            heading_section_chunker=heading_section_chunker,
        )

        # When
        result = await chunker.chunk_text("text", ChunkingStrategy.HEADING_SECTION)

        # Then
        assert result == ["section chunk"]
        heading_section_chunker.chunk_text.assert_called_once_with(
            "text",
            ChunkingStrategy.HEADING_SECTION,
        )
        paragraph_chunker.chunk_text.assert_not_called()
        fixed_window_chunker.chunk_text.assert_not_called()

    async def test_chunk_text_routes_to_fixed_window_by_default(self) -> None:
        # Given
        fixed_window_chunker = AsyncMock()
        paragraph_chunker = AsyncMock()
        heading_section_chunker = AsyncMock()
        fixed_window_chunker.chunk_text.return_value = ["fixed chunk"]
        chunker = AdaptiveTextChunkerService(
            fixed_window_chunker=fixed_window_chunker,
            paragraph_chunker=paragraph_chunker,
            heading_section_chunker=heading_section_chunker,
        )

        # When
        result = await chunker.chunk_text("text")

        # Then
        assert result == ["fixed chunk"]
        fixed_window_chunker.chunk_text.assert_called_once_with(
            "text",
            ChunkingStrategy.FIXED_WINDOW,
        )
        paragraph_chunker.chunk_text.assert_not_called()
        heading_section_chunker.chunk_text.assert_not_called()
