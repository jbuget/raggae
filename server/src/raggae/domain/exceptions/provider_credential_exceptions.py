class MultipleActiveProviderCredentialsError(ValueError):
    """Raised when more than one active credential exists for a user and provider."""


class ProviderCredentialNotFoundError(ValueError):
    """Raised when a provider credential does not exist for a user."""
