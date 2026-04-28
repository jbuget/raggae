import pytest

from raggae.application.services.slide_chunker import SlideChunk, SlideChunker


class TestSlideChunker:
    @pytest.fixture
    def chunker(self) -> SlideChunker:
        return SlideChunker()

    def test_chunk_returns_one_chunk_per_slide(self, chunker: SlideChunker) -> None:
        # Given
        text = "[SLIDE:1]\n# Intro\n\nHello world.\n[SLIDE:2]\n# Conclusion\n\nThat's all."

        # When
        result = chunker.chunk(text)

        # Then
        assert len(result) == 2

    def test_chunk_contains_slide_number(self, chunker: SlideChunker) -> None:
        # Given
        text = "[SLIDE:1]\n# First\n\nContent A.\n[SLIDE:3]\n# Third\n\nContent C."

        # When
        result = chunker.chunk(text)

        # Then
        assert result[0].slide_number == 1
        assert result[1].slide_number == 3

    def test_chunk_contains_slide_title(self, chunker: SlideChunker) -> None:
        # Given
        text = "[SLIDE:1]\n# Architecture Overview\n\nSome content."

        # When
        result = chunker.chunk(text)

        # Then
        assert result[0].slide_title == "Architecture Overview"

    def test_chunk_index_is_zero_based(self, chunker: SlideChunker) -> None:
        # Given
        text = "[SLIDE:1]\n# A\n\nX\n[SLIDE:2]\n# B\n\nY"

        # When
        result = chunker.chunk(text)

        # Then
        assert result[0].chunk_index == 0
        assert result[1].chunk_index == 1

    def test_chunk_content_includes_title_and_body(self, chunker: SlideChunker) -> None:
        # Given
        text = "[SLIDE:1]\n# My Title\n\nBody text here."

        # When
        result = chunker.chunk(text)

        # Then
        assert "My Title" in result[0].content
        assert "Body text here." in result[0].content

    def test_chunk_content_includes_notes(self, chunker: SlideChunker) -> None:
        # Given
        text = "[SLIDE:1]\n# Title\n\nBody.\n\n[NOTES]\nSpeaker notes here."

        # When
        result = chunker.chunk(text)

        # Then
        assert "Speaker notes here." in result[0].content

    def test_chunk_slide_without_title_still_produces_chunk(self, chunker: SlideChunker) -> None:
        # Given
        text = "[SLIDE:1]\n\nNo heading here, just body text."

        # When
        result = chunker.chunk(text)

        # Then
        assert len(result) == 1
        assert result[0].slide_title == ""

    def test_chunk_empty_text_returns_empty_list(self, chunker: SlideChunker) -> None:
        # Given / When
        result = chunker.chunk("")

        # Then
        assert result == []

    def test_chunk_result_has_correct_type(self, chunker: SlideChunker) -> None:
        # Given
        text = "[SLIDE:1]\n# Title\n\nContent."

        # When
        result = chunker.chunk(text)

        # Then
        assert isinstance(result[0], SlideChunk)
        assert result[0].slide_number == 1
        assert result[0].slide_title == "Title"

    def test_chunk_whitespace_only_text_returns_empty_list(self, chunker: SlideChunker) -> None:
        # Given / When
        result = chunker.chunk("   \n  \t  ")

        # Then
        assert result == []
