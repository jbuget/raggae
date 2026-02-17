from enum import StrEnum


class DocumentStatus(StrEnum):
    """Lifecycle states of a document."""

    UPLOADED = "uploaded"
    PROCESSING = "processing"
    INDEXED = "indexed"
    ERROR = "error"
