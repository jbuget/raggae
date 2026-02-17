import re
from datetime import date, datetime
from io import BytesIO

from raggae.application.interfaces.services.file_metadata_extractor import (
    FileMetadata,
)

_AUTHOR_SPLIT_RE = re.compile(r"[;,]")


class PdfDocxFileMetadataExtractor:
    """Extract metadata from PDF and DOCX properties."""

    async def extract_metadata(
        self,
        file_name: str,
        content: bytes,
        content_type: str,
    ) -> FileMetadata:
        del content_type
        extension = file_name.rsplit(".", maxsplit=1)[-1].lower() if "." in file_name else ""
        if extension == "pdf":
            return self._extract_pdf(content)
        if extension == "docx":
            return self._extract_docx(content)
        return FileMetadata()

    def _extract_pdf(self, content: bytes) -> FileMetadata:
        try:
            from pypdf import PdfReader
        except ModuleNotFoundError:
            return FileMetadata()

        try:
            reader = PdfReader(BytesIO(content))
            info = reader.metadata
            if info is None:
                return FileMetadata()
            title = self._clean_text(getattr(info, "title", None))
            author = self._clean_text(getattr(info, "author", None))
            creation_raw = self._clean_text(getattr(info, "creation_date", None))
            return FileMetadata(
                title=title,
                authors=self._parse_authors(author),
                document_date=self._parse_pdf_date(creation_raw),
            )
        except Exception:
            return FileMetadata()

    def _extract_docx(self, content: bytes) -> FileMetadata:
        try:
            from docx import Document as DocxDocument
        except ModuleNotFoundError:
            return FileMetadata()

        try:
            document = DocxDocument(BytesIO(content))
            props = document.core_properties
            author = self._clean_text(props.author)
            created = props.created.date() if props.created is not None else None
            return FileMetadata(
                title=self._clean_text(props.title),
                authors=self._parse_authors(author),
                document_date=created,
            )
        except Exception:
            return FileMetadata()

    def _clean_text(self, value: object) -> str | None:
        if not isinstance(value, str):
            return None
        normalized = value.strip()
        return normalized or None

    def _parse_authors(self, value: str | None) -> list[str] | None:
        if value is None:
            return None
        authors = [part.strip() for part in _AUTHOR_SPLIT_RE.split(value) if part.strip()]
        return authors or None

    def _parse_pdf_date(self, value: str | None) -> date | None:
        if not value:
            return None
        # Common PDF format: D:YYYYMMDDHHmmSS...
        cleaned = value[2:] if value.startswith("D:") else value
        if len(cleaned) < 8:
            return None
        try:
            return datetime.strptime(cleaned[:8], "%Y%m%d").date()
        except ValueError:
            return None
