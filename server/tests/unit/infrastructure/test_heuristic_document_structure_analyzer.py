from raggae.infrastructure.services.heuristic_document_structure_analyzer import (
    HeuristicDocumentStructureAnalyzer,
)


class TestHeuristicDocumentStructureAnalyzer:
    async def test_analyze_text_detects_markdown_headings(self) -> None:
        # Given
        analyzer = HeuristicDocumentStructureAnalyzer()
        text = "# Title\n\nFirst paragraph.\n\n## Section\n\nSecond paragraph."

        # When
        result = await analyzer.analyze_text(text)

        # Then
        assert result.has_headings is True
        assert result.paragraph_count == 4
        assert result.average_paragraph_length > 0

    async def test_analyze_text_reports_narrative_without_headings(self) -> None:
        # Given
        analyzer = HeuristicDocumentStructureAnalyzer()
        text = (
            "This is a first narrative paragraph with enough content.\n\n"
            "This is a second narrative paragraph with enough content.\n\n"
            "This is a third narrative paragraph with enough content."
        )

        # When
        result = await analyzer.analyze_text(text)

        # Then
        assert result.has_headings is False
        assert result.paragraph_count == 3
        assert result.average_paragraph_length >= 40

    async def test_analyze_text_handles_empty_input(self) -> None:
        # Given
        analyzer = HeuristicDocumentStructureAnalyzer()

        # When
        result = await analyzer.analyze_text(" \n\t ")

        # Then
        assert result.has_headings is False
        assert result.paragraph_count == 0
        assert result.average_paragraph_length == 0
