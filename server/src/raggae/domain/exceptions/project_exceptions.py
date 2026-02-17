class ProjectAlreadyPublishedError(Exception):
    """Raised when trying to publish an already published project."""


class ProjectNotFoundError(Exception):
    """Raised when a project cannot be found."""


class ProjectReindexInProgressError(Exception):
    """Raised when a project is already in reindexation."""


class ProjectSystemPromptTooLongError(Exception):
    """Raised when project system prompt exceeds maximum allowed length."""
