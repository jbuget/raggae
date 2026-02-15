from raggae.infrastructure.services.heading_section_text_chunker_service import (
    HeadingSectionTextChunkerService,
)
from raggae.infrastructure.services.simple_text_chunker_service import SimpleTextChunkerService


class TestHeadingSectionTextChunkerService:
    async def test_chunk_text_splits_by_headings(self) -> None:
        # Given
        chunker = HeadingSectionTextChunkerService(
            fallback_chunker=SimpleTextChunkerService(chunk_size=1000, chunk_overlap=0)
        )
        text = (
            "# Title\nLine one.\nLine two.\n\n"
            "## Section\nSection body.\n\n"
            "### Details\nDetails body."
        )

        # When
        chunks = await chunker.chunk_text(text)

        # Then
        assert len(chunks) == 3
        assert chunks[0].startswith("# Title")
        assert chunks[1].startswith("## Section")
        assert chunks[2].startswith("### Details")

    async def test_chunk_text_falls_back_to_fixed_window_for_large_sections(self) -> None:
        # Given
        chunker = HeadingSectionTextChunkerService(
            fallback_chunker=SimpleTextChunkerService(chunk_size=20, chunk_overlap=0)
        )
        text = "# Heading\n" + ("A" * 70)

        # When
        chunks = await chunker.chunk_text(text)

        # Then
        assert len(chunks) >= 2
