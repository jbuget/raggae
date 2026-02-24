class OrganizationNotFoundError(Exception):
    """Raised when an organization cannot be found."""


class OrganizationAccessDeniedError(PermissionError):
    """Raised when a user cannot access or modify an organization."""


class LastOrganizationOwnerError(ValueError):
    """Raised when an operation would remove or demote the last organization owner."""


class OrganizationInvitationInvalidError(ValueError):
    """Raised when an organization invitation is invalid."""
