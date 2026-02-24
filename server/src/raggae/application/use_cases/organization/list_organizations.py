from uuid import UUID

from raggae.application.dto.organization_dto import OrganizationDTO
from raggae.application.interfaces.repositories.organization_repository import (
    OrganizationRepository,
)


class ListOrganizations:
    """Use Case: List organizations created by the user."""

    def __init__(self, organization_repository: OrganizationRepository) -> None:
        self._organization_repository = organization_repository

    async def execute(self, user_id: UUID) -> list[OrganizationDTO]:
        organizations = await self._organization_repository.find_by_user_id(user_id)
        return [OrganizationDTO.from_entity(org) for org in organizations]
