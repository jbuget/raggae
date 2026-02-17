class InvalidEmailError(ValueError):
    """Raised when an email has an invalid format."""


class WeakPasswordError(ValueError):
    """Raised when a password does not meet strength requirements."""


class InvalidModelProviderError(ValueError):
    """Raised when a model provider is not supported."""


class InvalidProviderApiKeyError(ValueError):
    """Raised when an API key is invalid for a provider."""
