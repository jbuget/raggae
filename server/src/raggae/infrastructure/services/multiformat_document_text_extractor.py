from __future__ import annotations

from io import BytesIO
from typing import TYPE_CHECKING

from raggae.domain.exceptions.document_exceptions import DocumentExtractionError

if TYPE_CHECKING:
    from raggae.infrastructure.services.standalone_image_document_text_extractor import (
        StandaloneImageDocumentTextExtractor,
    )

_IMAGE_EXTENSIONS = {"jpg", "jpeg", "png", "webp", "tiff", "tif", "gif"}


class MultiFormatDocumentTextExtractor:
    """Extract text from txt/md/pdf/docx/pptx/image files with basic normalization."""

    def __init__(
        self,
        standalone_image_extractor: StandaloneImageDocumentTextExtractor | None = None,
    ) -> None:
        self._standalone_image_extractor = standalone_image_extractor

    async def extract_text(self, file_name: str, content: bytes, content_type: str) -> str:
        extension = file_name.rsplit(".", maxsplit=1)[-1].lower() if "." in file_name else ""

        if extension in {"txt", "md"}:
            text = self._decode_text(content)
        elif extension == "pdf":
            text = self._extract_pdf(content)
        elif extension == "docx":
            text = self._extract_docx(content)
        elif extension == "doc":
            raise DocumentExtractionError("DOC extraction is not supported in sync mode yet. Use DOCX.")
        elif extension in _IMAGE_EXTENSIONS:
            text = await self._extract_standalone_image(content, content_type)
        else:
            raise DocumentExtractionError(f"Unsupported extension for extraction: {extension}")

        normalized = self._normalize_text(text)
        if not normalized:
            raise DocumentExtractionError("No extractable text found in document")
        return normalized

    async def _extract_standalone_image(self, content: bytes, content_type: str) -> str:
        if self._standalone_image_extractor is None:
            raise DocumentExtractionError(
                "No vision service configured; standalone image indexing is unavailable."
            )
        result = await self._standalone_image_extractor.extract(content, content_type)
        if not result:
            raise DocumentExtractionError(
                "Vision is not available for this project; image cannot be indexed."
            )
        return result

    def _decode_text(self, content: bytes) -> str:
        try:
            return content.decode("utf-8")
        except UnicodeDecodeError:
            return content.decode("utf-8", errors="ignore")

    def _extract_pdf(self, content: bytes) -> str:
        try:
            from pypdf import PdfReader
        except ModuleNotFoundError as exc:  # pragma: no cover - dependency management
            raise DocumentExtractionError("pypdf is required for PDF extraction") from exc

        try:
            reader = PdfReader(BytesIO(content))
            parts = [
                f"[[PAGE:{index + 1}]]\n{page.extract_text() or ''}"
                for index, page in enumerate(reader.pages)
            ]
            return "\n".join(parts)
        except Exception as exc:  # pragma: no cover - file dependent
            raise DocumentExtractionError(f"Failed to extract PDF text: {exc}") from exc

    def _extract_docx(self, content: bytes) -> str:
        try:
            from docx import Document as DocxDocument
        except ModuleNotFoundError as exc:  # pragma: no cover - dependency management
            raise DocumentExtractionError("python-docx is required for DOCX extraction") from exc

        try:
            document = DocxDocument(BytesIO(content))
            parts = [paragraph.text for paragraph in document.paragraphs if paragraph.text.strip()]
            for table in document.tables:
                for row in table.rows:
                    row_cells = [cell.text.strip() for cell in row.cells if cell.text.strip()]
                    if row_cells:
                        parts.append(" | ".join(row_cells))
            return "\n".join(parts)
        except Exception as exc:  # pragma: no cover - file dependent
            raise DocumentExtractionError(f"Failed to extract DOCX text: {exc}") from exc

    def _normalize_text(self, text: str) -> str:
        return "\n".join(line.rstrip() for line in text.replace("\r\n", "\n").split("\n")).strip()
