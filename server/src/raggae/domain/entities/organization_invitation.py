from dataclasses import dataclass, replace
from datetime import UTC, datetime
from uuid import UUID

from raggae.domain.value_objects.organization_invitation_status import (
    OrganizationInvitationStatus,
)
from raggae.domain.value_objects.organization_member_role import OrganizationMemberRole


@dataclass(frozen=True)
class OrganizationInvitation:
    """Organization invitation entity."""

    id: UUID
    organization_id: UUID
    email: str
    role: OrganizationMemberRole
    status: OrganizationInvitationStatus
    invited_by_user_id: UUID
    token_hash: str
    expires_at: datetime
    created_at: datetime
    updated_at: datetime

    def with_status(
        self, status: OrganizationInvitationStatus, updated_at: datetime
    ) -> "OrganizationInvitation":
        """Return a new invitation with updated status."""
        return replace(self, status=status, updated_at=updated_at)

    def renew(self, expires_at: datetime, updated_at: datetime) -> "OrganizationInvitation":
        """Return a renewed pending invitation."""
        return replace(
            self,
            status=OrganizationInvitationStatus.PENDING,
            expires_at=expires_at,
            updated_at=updated_at,
        )

    def is_expired(self, now: datetime) -> bool:
        return self._as_utc(self.expires_at) < self._as_utc(now)

    @staticmethod
    def _as_utc(value: datetime) -> datetime:
        if value.tzinfo is None or value.tzinfo.utcoffset(value) is None:
            return value.replace(tzinfo=UTC)
        return value.astimezone(UTC)
