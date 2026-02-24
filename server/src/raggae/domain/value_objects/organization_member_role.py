from enum import StrEnum


class OrganizationMemberRole(StrEnum):
    """Supported organization membership roles."""

    OWNER = "owner"
    MAKER = "maker"
    USER = "user"
