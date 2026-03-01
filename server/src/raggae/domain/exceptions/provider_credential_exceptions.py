class ProviderCredentialNotFoundError(ValueError):
    """Raised when a provider credential does not exist for a user."""


class DuplicateProviderCredentialError(ValueError):
    """Raised when a credential with the same API key already exists for a user and provider."""


class CredentialInUseError(ValueError):
    """Raised when a credential cannot be deactivated because a project is using it."""


class OrgCredentialNotFoundError(ValueError):
    """Raised when an org provider credential does not exist."""


class OrgDuplicateCredentialError(ValueError):
    """Raised when a credential with the same API key already exists for an org and provider."""


class OrgCredentialInUseError(ValueError):
    """Raised when an org credential cannot be deactivated because a project is using it."""
