from io import BytesIO

from raggae.domain.exceptions.document_exceptions import DocumentExtractionError


class MultiFormatDocumentTextExtractor:
    """Extract text from txt/md/pdf/docx files with basic normalization."""

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
            raise DocumentExtractionError(
                "DOC extraction is not supported in sync mode yet. Use DOCX."
            )
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
            parts = [page.extract_text() or "" for page in reader.pages]
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
            return "\n".join(paragraph.text for paragraph in document.paragraphs)
        except Exception as exc:  # pragma: no cover - file dependent
            raise DocumentExtractionError(f"Failed to extract DOCX text: {exc}") from exc

    def _normalize_text(self, text: str) -> str:
        return "\n".join(line.rstrip() for line in text.replace("\r\n", "\n").split("\n")).strip()
