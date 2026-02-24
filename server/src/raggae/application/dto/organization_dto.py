from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from raggae.domain.entities.organization import Organization


@dataclass
class OrganizationDTO:
    """Data Transfer Object for Organization."""

    id: UUID
    name: str
    description: str | None
    logo_url: str | None
    created_by_user_id: UUID
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_entity(cls, organization: Organization) -> "OrganizationDTO":
        return cls(
            id=organization.id,
            name=organization.name,
            description=organization.description,
            logo_url=organization.logo_url,
            created_by_user_id=organization.created_by_user_id,
            created_at=organization.created_at,
            updated_at=organization.updated_at,
        )
