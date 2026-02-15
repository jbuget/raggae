class InvalidDocumentTypeError(Exception):
    """Raised when the document extension is not allowed."""


class DocumentTooLargeError(Exception):
    """Raised when the document exceeds max allowed size."""


class DocumentNotFoundError(Exception):
    """Raised when a document cannot be found."""


class DocumentExtractionError(Exception):
    """Raised when text extraction from document content fails."""
