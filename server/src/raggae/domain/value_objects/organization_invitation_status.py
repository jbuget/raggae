from enum import StrEnum


class OrganizationInvitationStatus(StrEnum):
    """Lifecycle states for organization invitations."""

    PENDING = "pending"
    ACCEPTED = "accepted"
    REVOKED = "revoked"
    EXPIRED = "expired"
