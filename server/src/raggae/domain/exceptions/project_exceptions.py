class ProjectAlreadyPublishedError(Exception):
    """Raised when trying to publish an already published project."""


class ProjectNotFoundError(Exception):
    """Raised when a project cannot be found."""


class ProjectReindexInProgressError(Exception):
    """Raised when a project is already in reindexation."""


class ProjectSystemPromptTooLongError(Exception):
    """Raised when project system prompt exceeds maximum allowed length."""


class InvalidProjectEmbeddingBackendError(ValueError):
    """Raised when project embedding backend is unsupported."""


class InvalidProjectLLMBackendError(ValueError):
    """Raised when project LLM backend is unsupported."""


class InvalidProjectRetrievalStrategyError(ValueError):
    """Raised when project retrieval strategy is unsupported."""


class InvalidProjectRetrievalTopKError(ValueError):
    """Raised when project retrieval top-k is unsupported."""


class InvalidProjectRetrievalMinScoreError(ValueError):
    """Raised when project retrieval min-score threshold is unsupported."""


class InvalidProjectChatHistoryWindowSizeError(ValueError):
    """Raised when project chat history window size is unsupported."""


class InvalidProjectChatHistoryMaxCharsError(ValueError):
    """Raised when project chat history max chars is unsupported."""


class ProjectAPIKeyNotOwnedError(ValueError):
    """Raised when project API key is not registered for the current user."""
