import logging
from io import BytesIO

from raggae.application.services.document_indexing_service import TABULAR_EXTENSIONS
from raggae.domain.exceptions.document_exceptions import DocumentExtractionError
from raggae.infrastructure.services.tabular_document_text_extractor import (
    TabularDocumentTextExtractor,
)

logger = logging.getLogger(__name__)


class MultiFormatDocumentTextExtractor:
    """Extract text from txt/md/pdf/docx/pptx/csv/xlsx/xls files with basic normalization."""

    def __init__(self) -> None:
        self._tabular_extractor = TabularDocumentTextExtractor()

    async def extract_text(self, file_name: str, content: bytes, content_type: str) -> str:
        _ = content_type
        extension = file_name.rsplit(".", maxsplit=1)[-1].lower() if "." in file_name else ""

        if extension in {"txt", "md"}:
            text = self._decode_text(content)
        elif extension == "pdf":
            text = self._extract_pdf(content)
        elif extension == "docx":
            text = self._extract_docx(content)
        elif extension == "doc":
            raise DocumentExtractionError("DOC extraction is not supported in sync mode yet. Use DOCX.")
        elif extension == "pptx":
            text = self._extract_pptx(content)
        elif extension == "ppt":
            raise DocumentExtractionError(
                "PPT (legacy binary format) is not supported. Convert to PPTX first."
            )
        elif extension in TABULAR_EXTENSIONS:
            return await self._tabular_extractor.extract_text(file_name, content, content_type)
        else:
            raise DocumentExtractionError(f"Unsupported extension for extraction: {extension}")

        normalized = self._normalize_text(text)
        if not normalized:
            raise DocumentExtractionError("No extractable text found in document")
        return normalized

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
                parts.extend(self._table_to_markdown(table))
            return "\n".join(parts)
        except Exception as exc:  # pragma: no cover - file dependent
            raise DocumentExtractionError(f"Failed to extract DOCX text: {exc}") from exc

    def _extract_pptx(self, content: bytes) -> str:
        try:
            from pptx import Presentation
        except ModuleNotFoundError as exc:  # pragma: no cover - dependency management
            raise DocumentExtractionError("python-pptx is required for PPTX extraction") from exc

        try:
            prs = Presentation(BytesIO(content))
            slide_parts: list[str] = []
            for index, slide in enumerate(prs.slides):
                parts: list[str] = [f"[SLIDE:{index + 1}]"]
                title_shape = slide.shapes.title
                title_text = (
                    title_shape.text_frame.text.strip() if title_shape and title_shape.has_text_frame else ""
                )
                if title_text:
                    parts.append(f"# {title_text}")

                sorted_shapes = sorted(
                    slide.shapes,
                    key=lambda s: (getattr(s, "top", 0) or 0, getattr(s, "left", 0) or 0),
                )
                for shape in sorted_shapes:
                    if shape is title_shape:
                        continue
                    if shape.has_text_frame:
                        text = shape.text_frame.text.strip()
                        if text:
                            parts.append(text)
                    elif shape.has_table:
                        for row in shape.table.rows:
                            cells = [cell.text.strip() for cell in row.cells if cell.text.strip()]
                            if cells:
                                parts.append("| " + " | ".join(cells) + " |")

                try:
                    notes_text = slide.notes_slide.notes_text_frame.text.strip()
                except Exception as exc:
                    logger.debug("Impossible de lire les notes de la diapositive %d : %s", index + 1, exc)
                    notes_text = ""
                if notes_text:
                    parts.append(f"[NOTES]\n{notes_text}")

                slide_parts.append("\n".join(parts))
            return "\n".join(slide_parts)
        except Exception as exc:  # pragma: no cover - file dependent
            raise DocumentExtractionError(f"Failed to extract PPTX text: {exc}") from exc

    def _table_to_markdown(self, table: object) -> list[str]:
        # Intentionally uses Markdown format: DOCX is not auto-routed to TABULAR
        # strategy, so tables land in paragraph/fixed-window chunkers that handle
        # prose-mixed content — not in TabularTextChunkerService.
        from docx.table import Table as DocxTable

        if not isinstance(table, DocxTable):
            return []
        markdown_rows = []
        for row in table.rows:
            cells = [cell.text.strip() for cell in row.cells]
            if any(cells):
                markdown_rows.append(cells)
        if not markdown_rows:
            return []
        lines: list[str] = []
        header = markdown_rows[0]
        lines.append("| " + " | ".join(header) + " |")
        lines.append("| " + " | ".join("---" for _ in header) + " |")
        for row in markdown_rows[1:]:
            padded = (list(row) + [""] * len(header))[: len(header)]
            lines.append("| " + " | ".join(padded) + " |")
        return lines

    def _normalize_text(self, text: str) -> str:
        return "\n".join(line.rstrip() for line in text.replace("\r\n", "\n").split("\n")).strip()
