from raggae.infrastructure.services.paragraph_text_chunker_service import (
    ParagraphTextChunkerService,
)


class TestParagraphTextChunkerService:
    async def test_chunk_text_keeps_paragraph_boundaries(self) -> None:
        # Given
        chunker = ParagraphTextChunkerService(chunk_size=80)
        text = "Paragraph A.\n\nParagraph B.\n\nParagraph C."

        # When
        chunks = await chunker.chunk_text(text)

        # Then
        assert chunks == ["Paragraph A.\n\nParagraph B.\n\nParagraph C."]

    async def test_chunk_text_splits_when_size_limit_is_reached(self) -> None:
        # Given
        chunker = ParagraphTextChunkerService(chunk_size=25)
        text = "Paragraph A content.\n\nParagraph B content.\n\nParagraph C content."

        # When
        chunks = await chunker.chunk_text(text)

        # Then
        assert chunks == [
            "Paragraph A content.",
            "Paragraph B content.",
            "Paragraph C content.",
        ]
