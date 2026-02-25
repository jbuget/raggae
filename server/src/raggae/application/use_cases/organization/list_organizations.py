from uuid import UUID

from raggae.application.dto.organization_dto import OrganizationDTO
from raggae.application.interfaces.repositories.organization_member_repository import (
    OrganizationMemberRepository,
)
from raggae.application.interfaces.repositories.organization_repository import (
    OrganizationRepository,
)


class ListOrganizations:
    """Use Case: List organizations visible to the user."""

    def __init__(
        self,
        organization_repository: OrganizationRepository,
        organization_member_repository: OrganizationMemberRepository,
    ) -> None:
        self._organization_repository = organization_repository
        self._organization_member_repository = organization_member_repository

    async def execute(self, user_id: UUID) -> list[OrganizationDTO]:
        created_organizations = await self._organization_repository.find_by_user_id(user_id)
        member_entries = await self._organization_member_repository.find_by_user_id(user_id)
        visible_by_id = {organization.id: organization for organization in created_organizations}
        for member in member_entries:
            if member.organization_id in visible_by_id:
                continue
            organization = await self._organization_repository.find_by_id(member.organization_id)
            if organization is not None:
                visible_by_id[organization.id] = organization
        return [OrganizationDTO.from_entity(org) for org in visible_by_id.values()]
