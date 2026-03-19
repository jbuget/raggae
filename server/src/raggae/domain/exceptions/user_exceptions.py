class UserAlreadyInactiveError(Exception):
    """Raised when trying to deactivate an already inactive user."""


class UserAlreadyExistsError(Exception):
    """Raised when trying to register with an already used email."""


class UserNotFoundError(Exception):
    """Raised when a user cannot be found."""


class InvalidCredentialsError(Exception):
    """Raised when login credentials are invalid."""


class OAuthDomainNotAllowedError(Exception):
    """Raised when an OAuth user's email domain is not in the allowed list."""


class OAuthProviderError(Exception):
    """Raised when an OAuth provider returns an unexpected error."""
