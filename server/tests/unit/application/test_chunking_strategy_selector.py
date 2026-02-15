from raggae.application.services.chunking_strategy_selector import ChunkingStrategySelector
from raggae.domain.value_objects.chunking_strategy import ChunkingStrategy


class TestChunkingStrategySelector:
    def test_select_returns_heading_section_when_headings_detected(self) -> None:
        # Given
        selector = ChunkingStrategySelector()

        # When
        strategy = selector.select(
            has_headings=True,
            paragraph_count=2,
            average_paragraph_length=30,
        )

        # Then
        assert strategy == ChunkingStrategy.HEADING_SECTION

    def test_select_returns_paragraph_for_narrative_document(self) -> None:
        # Given
        selector = ChunkingStrategySelector()

        # When
        strategy = selector.select(
            has_headings=False,
            paragraph_count=4,
            average_paragraph_length=120,
        )

        # Then
        assert strategy == ChunkingStrategy.PARAGRAPH

    def test_select_returns_fixed_window_as_fallback(self) -> None:
        # Given
        selector = ChunkingStrategySelector()

        # When
        strategy = selector.select(
            has_headings=False,
            paragraph_count=1,
            average_paragraph_length=20,
        )

        # Then
        assert strategy == ChunkingStrategy.FIXED_WINDOW
