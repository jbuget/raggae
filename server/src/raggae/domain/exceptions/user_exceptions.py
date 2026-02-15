class UserAlreadyInactiveError(Exception):
    """Raised when trying to deactivate an already inactive user."""


class UserAlreadyExistsError(Exception):
    """Raised when trying to register with an already used email."""


class UserNotFoundError(Exception):
    """Raised when a user cannot be found."""


class InvalidCredentialsError(Exception):
    """Raised when login credentials are invalid."""
