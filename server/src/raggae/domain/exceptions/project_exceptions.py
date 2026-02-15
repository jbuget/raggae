class ProjectAlreadyPublishedError(Exception):
    """Raised when trying to publish an already published project."""


class ProjectNotFoundError(Exception):
    """Raised when a project cannot be found."""
