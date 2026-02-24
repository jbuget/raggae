import sys
import types
from datetime import datetime
from io import BytesIO

import pytest
from docx import Document as DocxDocument
from raggae.application.interfaces.services.file_metadata_extractor import FileMetadata
from raggae.infrastructure.services.pdf_docx_file_metadata_extractor import (
    PdfDocxFileMetadataExtractor,
)


class TestPdfDocxFileMetadataExtractor:
    async def test_extract_metadata_pdf_with_metadata(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # Given
        extractor = PdfDocxFileMetadataExtractor()

        class _FakeMetadata:
            title = "Workflow Review"
            author = "Alice, Bob"
            creation_date = "D:20260127"

        class _FakeReader:
            def __init__(self, _buffer: BytesIO) -> None:
                self.metadata = _FakeMetadata()

        monkeypatch.setitem(sys.modules, "pypdf", types.SimpleNamespace(PdfReader=_FakeReader))

        # When
        result = await extractor.extract_metadata("report.pdf", b"%PDF-1.7", "application/pdf")

        # Then
        assert result.title == "Workflow Review"
        assert result.authors == ["Alice", "Bob"]
        assert result.document_date is not None
        assert result.document_date.isoformat() == "2026-01-27"

    async def test_extract_metadata_pdf_without_metadata(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # Given
        extractor = PdfDocxFileMetadataExtractor()

        class _FakeReader:
            def __init__(self, _buffer: BytesIO) -> None:
                self.metadata = None

        monkeypatch.setitem(sys.modules, "pypdf", types.SimpleNamespace(PdfReader=_FakeReader))

        # When
        result = await extractor.extract_metadata("empty.pdf", b"%PDF-1.7", "application/pdf")

        # Then
        assert result == FileMetadata()

    async def test_extract_metadata_docx_with_core_properties(self) -> None:
        # Given
        extractor = PdfDocxFileMetadataExtractor()
        document = DocxDocument()
        document.core_properties.title = "Meeting Notes"
        document.core_properties.author = "Carol; Dan"
        document.core_properties.created = datetime(2026, 1, 22)
        buffer = BytesIO()
        document.save(buffer)

        # When
        result = await extractor.extract_metadata(
            "meeting.docx",
            buffer.getvalue(),
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )

        # Then
        assert result.title == "Meeting Notes"
        assert result.authors == ["Carol", "Dan"]
        assert result.document_date is not None
        assert result.document_date.isoformat() == "2026-01-22"

    async def test_extract_metadata_txt_returns_empty(self) -> None:
        # Given
        extractor = PdfDocxFileMetadataExtractor()

        # When
        result = await extractor.extract_metadata("notes.txt", b"hello", "text/plain")

        # Then
        assert result == FileMetadata()
