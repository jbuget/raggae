from dataclasses import dataclass
from datetime import date
from typing import Protocol


@dataclass(frozen=True)
class FileMetadata:
    """Structured metadata extracted from file properties."""

    title: str | None = None
    authors: list[str] | None = None
    document_date: date | None = None


class FileMetadataExtractor(Protocol):
    """Interface to extract metadata from a binary document."""

    async def extract_metadata(
        self,
        file_name: str,
        content: bytes,
        content_type: str,
    ) -> FileMetadata: ...
