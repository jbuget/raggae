class InvalidDocumentTypeError(Exception):
    """Raised when the document extension is not allowed."""


class DocumentTooLargeError(Exception):
    """Raised when the document exceeds max allowed size."""


class DocumentNotFoundError(Exception):
    """Raised when a document cannot be found."""


class DocumentExtractionError(Exception):
    """Raised when text extraction from document content fails."""


class EmbeddingGenerationError(Exception):
    """Raised when embeddings cannot be generated."""


class LLMGenerationError(Exception):
    """Raised when an LLM provider cannot generate an answer."""
