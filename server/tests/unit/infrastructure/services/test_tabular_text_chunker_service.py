import pytest

from raggae.domain.value_objects.chunking_strategy import ChunkingStrategy
from raggae.infrastructure.services.tabular_text_chunker_service import TabularTextChunkerService


class TestTabularTextChunkerService:
    @pytest.fixture
    def chunker(self) -> TabularTextChunkerService:
        return TabularTextChunkerService()

    # ------- helpers -------

    def _csv_text(self) -> str:
        return "[HEADERS]:Produit|Région|Quantité\n[ROW:1]:Widget A|Nord|1200\n[ROW:2]:Gadget B|Sud|500"

    def _xlsx_text(self) -> str:
        return "[SHEET:Ventes 2024]\n[HEADERS]:Produit|Prix\n[ROW:1]:Widget A|48\n[ROW:2]:Gadget B|12"

    # ------- tests -------

    async def test_chunk_text_one_chunk_per_row(self, chunker: TabularTextChunkerService) -> None:
        # When
        chunks = await chunker.chunk_text(self._csv_text(), ChunkingStrategy.TABULAR)

        # Then
        assert len(chunks) == 2

    async def test_chunk_text_headers_repeated_in_each_chunk(
        self, chunker: TabularTextChunkerService
    ) -> None:
        # When
        chunks = await chunker.chunk_text(self._csv_text(), ChunkingStrategy.TABULAR)

        # Then
        for chunk in chunks:
            assert "| Produit |" in chunk
            assert "| Région |" in chunk
            assert "| Quantité |" in chunk

    async def test_chunk_text_markdown_separator_present(self, chunker: TabularTextChunkerService) -> None:
        # When
        chunks = await chunker.chunk_text(self._csv_text(), ChunkingStrategy.TABULAR)

        # Then
        for chunk in chunks:
            assert "| --- |" in chunk or "|---|" in chunk or "---" in chunk

    async def test_chunk_text_row_marker_present(self, chunker: TabularTextChunkerService) -> None:
        # When
        chunks = await chunker.chunk_text(self._csv_text(), ChunkingStrategy.TABULAR)

        # Then
        assert "[ROW:1]" in chunks[0]
        assert "[ROW:2]" in chunks[1]

    async def test_chunk_text_no_sheet_marker_for_csv(self, chunker: TabularTextChunkerService) -> None:
        # When
        chunks = await chunker.chunk_text(self._csv_text(), ChunkingStrategy.TABULAR)

        # Then
        for chunk in chunks:
            assert "[SHEET:" not in chunk

    async def test_chunk_text_sheet_marker_for_xlsx(self, chunker: TabularTextChunkerService) -> None:
        # When
        chunks = await chunker.chunk_text(self._xlsx_text(), ChunkingStrategy.TABULAR)

        # Then
        for chunk in chunks:
            assert "[SHEET:Ventes 2024]" in chunk

    async def test_chunk_text_data_values_in_chunk(self, chunker: TabularTextChunkerService) -> None:
        # When
        chunks = await chunker.chunk_text(self._csv_text(), ChunkingStrategy.TABULAR)

        # Then
        assert "Widget A" in chunks[0]
        assert "1200" in chunks[0]
        assert "Gadget B" in chunks[1]
        assert "500" in chunks[1]

    async def test_chunk_text_empty_text_returns_no_chunks(self, chunker: TabularTextChunkerService) -> None:
        # When
        chunks = await chunker.chunk_text("", ChunkingStrategy.TABULAR)

        # Then
        assert chunks == []

    async def test_chunk_text_headers_only_returns_no_chunks(
        self, chunker: TabularTextChunkerService
    ) -> None:
        # Given — structured text with headers but no data rows
        text = "[HEADERS]:A|B|C"

        # When
        chunks = await chunker.chunk_text(text, ChunkingStrategy.TABULAR)

        # Then
        assert chunks == []

    async def test_chunk_text_pipe_in_cell_unescaped_in_output(
        self, chunker: TabularTextChunkerService
    ) -> None:
        # Given — pipe escaped in extractor output
        text = "[HEADERS]:Col\n[ROW:1]:A&#124;B"

        # When
        chunks = await chunker.chunk_text(text, ChunkingStrategy.TABULAR)

        # Then
        assert "&#124;" not in chunks[0]
        assert "A|B" in chunks[0]

    async def test_chunk_text_multi_sheet_resets_headers_per_sheet(
        self, chunker: TabularTextChunkerService
    ) -> None:
        # Given — two sheets with different headers
        text = (
            "[SHEET:Sheet1]\n[HEADERS]:Name|Value\n[ROW:1]:Alpha|1\n"
            "[SHEET:Sheet2]\n[HEADERS]:Key|Data\n[ROW:1]:X|Y"
        )

        # When
        chunks = await chunker.chunk_text(text, ChunkingStrategy.TABULAR)

        # Then
        assert len(chunks) == 2
        assert "Name" in chunks[0] and "Value" in chunks[0]
        assert "Key" in chunks[1] and "Data" in chunks[1]

    async def test_chunk_text_full_markdown_table_format(self, chunker: TabularTextChunkerService) -> None:
        # Given
        text = "[HEADERS]:H1|H2\n[ROW:1]:V1|V2"

        # When
        chunks = await chunker.chunk_text(text, ChunkingStrategy.TABULAR)

        # Then
        chunk = chunks[0]
        lines = chunk.split("\n")
        assert len(lines) == 4  # marker + header row + sep row + data row
        assert lines[0] == "[ROW:1]"
        assert lines[1] == "| H1 | H2 |"
        assert "---" in lines[2]
        assert lines[3] == "| V1 | V2 |"
