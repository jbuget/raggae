import sys
import types
from io import BytesIO

import pytest
from docx import Document as DocxDocument

from raggae.domain.exceptions.document_exceptions import DocumentExtractionError
from raggae.infrastructure.services.multiformat_document_text_extractor import (
    MultiFormatDocumentTextExtractor,
)


class TestMultiFormatDocumentTextExtractor:
    @pytest.fixture
    def extractor(self) -> MultiFormatDocumentTextExtractor:
        return MultiFormatDocumentTextExtractor()

    async def test_extract_text_txt_success(
        self,
        extractor: MultiFormatDocumentTextExtractor,
    ) -> None:
        # Given
        content = b"hello\nworld"

        # When
        result = await extractor.extract_text(
            file_name="notes.txt",
            content=content,
            content_type="text/plain",
        )

        # Then
        assert result == "hello\nworld"

    async def test_extract_text_md_normalizes_whitespace(
        self,
        extractor: MultiFormatDocumentTextExtractor,
    ) -> None:
        # Given
        content = b"  # Title\r\n\r\ncontent   "

        # When
        result = await extractor.extract_text(
            file_name="README.md",
            content=content,
            content_type="text/markdown",
        )

        # Then
        assert result == "# Title\n\ncontent"

    async def test_extract_text_pdf_uses_pdf_extractor(
        self,
        extractor: MultiFormatDocumentTextExtractor,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        # Given
        monkeypatch.setattr(extractor, "_extract_pdf", lambda _: "pdf text")

        # When
        result = await extractor.extract_text(
            file_name="file.pdf",
            content=b"%PDF-1.7",
            content_type="application/pdf",
        )

        # Then
        assert result == "pdf text"

    async def test_extract_pdf_includes_page_markers(
        self,
        extractor: MultiFormatDocumentTextExtractor,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        # Given
        class _FakePage:
            def __init__(self, value: str) -> None:
                self._value = value

            def extract_text(self) -> str:
                return self._value

        class _FakeReader:
            def __init__(self, _buffer: BytesIO) -> None:
                self.pages = [_FakePage("page one"), _FakePage("page two")]

        fake_module = types.SimpleNamespace(PdfReader=_FakeReader)
        monkeypatch.setitem(sys.modules, "pypdf", fake_module)

        # When
        result = extractor._extract_pdf(b"%PDF-1.7")

        # Then
        assert result == "[[PAGE:1]]\npage one\n[[PAGE:2]]\npage two"

    async def test_extract_text_docx_uses_docx_extractor(
        self,
        extractor: MultiFormatDocumentTextExtractor,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        # Given
        monkeypatch.setattr(extractor, "_extract_docx", lambda _: "docx text")

        # When
        result = await extractor.extract_text(
            file_name="file.docx",
            content=b"PK...",
            content_type=("application/vnd.openxmlformats-officedocument.wordprocessingml.document"),
        )

        # Then
        assert result == "docx text"

    async def test_extract_text_docx_extracts_paragraphs_and_tables(
        self,
        extractor: MultiFormatDocumentTextExtractor,
    ) -> None:
        # Given
        document = DocxDocument()
        document.add_paragraph("Transcript intro")
        table = document.add_table(rows=1, cols=2)
        table.cell(0, 0).text = "Action item"
        table.cell(0, 1).text = "Prepare demo for next meeting"
        buffer = BytesIO()
        document.save(buffer)
        content = buffer.getvalue()

        # When
        result = await extractor.extract_text(
            file_name="meeting.docx",
            content=content,
            content_type=("application/vnd.openxmlformats-officedocument.wordprocessingml.document"),
        )

        # Then
        assert "Transcript intro" in result
        assert "Action item" in result
        assert "Prepare demo for next meeting" in result

    async def test_extract_text_doc_raises_not_supported_error(
        self,
        extractor: MultiFormatDocumentTextExtractor,
    ) -> None:
        # When / Then
        with pytest.raises(DocumentExtractionError):
            await extractor.extract_text(
                file_name="legacy.doc",
                content=b"DOC",
                content_type="application/msword",
            )

    async def test_extract_text_unknown_extension_raises_error(
        self,
        extractor: MultiFormatDocumentTextExtractor,
    ) -> None:
        # When / Then
        with pytest.raises(DocumentExtractionError):
            await extractor.extract_text(
                file_name="file.bin",
                content=b"binary",
                content_type="application/octet-stream",
            )

    async def test_extract_png_delegates_to_standalone_extractor(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        # Given
        from unittest.mock import AsyncMock

        mock_standalone = AsyncMock()
        mock_standalone.extract.return_value = "[IMAGE]\n\nUne capture d'écran d'un tableau de bord."
        extractor = MultiFormatDocumentTextExtractor(standalone_image_extractor=mock_standalone)

        # When
        result = await extractor.extract_text(
            file_name="screenshot.png",
            content=b"\x89PNG",
            content_type="image/png",
        )

        # Then
        assert "[IMAGE]" in result
        assert "tableau de bord" in result
        mock_standalone.extract.assert_called_once_with(b"\x89PNG", "image/png")

    async def test_extract_image_no_vision_raises_extraction_error(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        # Given: standalone extractor returns empty string (no vision)
        from unittest.mock import AsyncMock

        mock_standalone = AsyncMock()
        mock_standalone.extract.return_value = ""
        extractor = MultiFormatDocumentTextExtractor(standalone_image_extractor=mock_standalone)

        # When / Then
        with pytest.raises(DocumentExtractionError):
            await extractor.extract_text(
                file_name="photo.jpg",
                content=b"\xff\xd8\xff",
                content_type="image/jpeg",
            )

    async def test_extract_image_without_standalone_extractor_raises_error(self) -> None:
        # Given: no standalone extractor injected
        extractor = MultiFormatDocumentTextExtractor()

        # When / Then
        with pytest.raises(DocumentExtractionError):
            await extractor.extract_text(
                file_name="photo.jpg",
                content=b"\xff\xd8\xff",
                content_type="image/jpeg",
            )
