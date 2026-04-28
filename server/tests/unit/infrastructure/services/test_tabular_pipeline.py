"""Integration tests for the tabular extract → chunk pipeline.

Validates that TabularDocumentTextExtractor and TabularTextChunkerService
produce consistent, parseable output when chained together.
"""

import io

import pytest

from raggae.domain.value_objects.chunking_strategy import ChunkingStrategy
from raggae.infrastructure.services.tabular_document_text_extractor import (
    TabularDocumentTextExtractor,
)
from raggae.infrastructure.services.tabular_text_chunker_service import TabularTextChunkerService


class TestTabularPipeline:
    @pytest.fixture
    def extractor(self) -> TabularDocumentTextExtractor:
        return TabularDocumentTextExtractor()

    @pytest.fixture
    def chunker(self) -> TabularTextChunkerService:
        return TabularTextChunkerService()

    async def test_csv_pipeline_produces_one_chunk_per_row(
        self,
        extractor: TabularDocumentTextExtractor,
        chunker: TabularTextChunkerService,
    ) -> None:
        # Given
        content = "Produit,Région,Quantité\nWidget A,Nord,1200\nGadget B,Sud,500\n".encode()

        # When
        extracted = await extractor.extract_text("data.csv", content, "text/csv")
        chunks = await chunker.chunk_text(extracted, ChunkingStrategy.TABULAR)

        # Then
        assert len(chunks) == 2
        assert "Produit: Widget A" in chunks[0]
        assert "Région: Nord" in chunks[0]
        assert "Quantité: 1200" in chunks[0]
        assert "Produit: Gadget B" in chunks[1]

    async def test_xlsx_pipeline_produces_chunks_with_sheet_marker(
        self,
        extractor: TabularDocumentTextExtractor,
        chunker: TabularTextChunkerService,
    ) -> None:
        # Given
        import openpyxl

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Ventes"
        ws.append(["Article", "Prix"])
        ws.append(["Stylo", "1.50"])
        ws.append(["Cahier", "3.00"])
        buf = io.BytesIO()
        wb.save(buf)
        content = buf.getvalue()

        # When
        extracted = await extractor.extract_text(
            "report.xlsx",
            content,
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        chunks = await chunker.chunk_text(extracted, ChunkingStrategy.TABULAR)

        # Then
        assert len(chunks) == 2
        assert "[SHEET:Ventes]" in chunks[0]
        assert "Article: Stylo" in chunks[0]
        assert "Prix: 1.50" in chunks[0]

    async def test_pipe_in_value_survives_roundtrip(
        self,
        extractor: TabularDocumentTextExtractor,
        chunker: TabularTextChunkerService,
    ) -> None:
        # Given — pipe character in a cell value
        content = b"Colonne\nA|B\n"

        # When
        extracted = await extractor.extract_text("data.csv", content, "text/csv")
        chunks = await chunker.chunk_text(extracted, ChunkingStrategy.TABULAR)

        # Then — pipe must be preserved in the final chunk, not treated as separator
        assert len(chunks) == 1
        assert "&#124;" not in chunks[0]
        assert "A|B" in chunks[0]

    async def test_empty_csv_produces_no_chunks(
        self,
        extractor: TabularDocumentTextExtractor,
        chunker: TabularTextChunkerService,
    ) -> None:
        # Given — only a header row, no data
        content = b"Col1,Col2\n"

        # When
        extracted = await extractor.extract_text("empty.csv", content, "text/csv")
        chunks = await chunker.chunk_text(extracted, ChunkingStrategy.TABULAR)

        # Then
        assert chunks == []
