from uuid import UUID

from raggae.application.dto.organization_member_dto import OrganizationMemberDTO
from raggae.application.interfaces.repositories.organization_member_repository import (
    OrganizationMemberRepository,
)
from raggae.application.interfaces.repositories.organization_repository import (
    OrganizationRepository,
)
from raggae.application.interfaces.repositories.user_repository import UserRepository
from raggae.domain.exceptions.organization_exceptions import (
    OrganizationAccessDeniedError,
    OrganizationNotFoundError,
)


class ListOrganizationMembers:
    """Use Case: List members for an organization."""

    def __init__(
        self,
        organization_repository: OrganizationRepository,
        organization_member_repository: OrganizationMemberRepository,
        user_repository: UserRepository,
    ) -> None:
        self._organization_repository = organization_repository
        self._organization_member_repository = organization_member_repository
        self._user_repository = user_repository

    async def execute(self, organization_id: UUID, user_id: UUID) -> list[OrganizationMemberDTO]:
        organization = await self._organization_repository.find_by_id(organization_id)
        if organization is None:
            raise OrganizationNotFoundError(f"Organization {organization_id} not found")
        requester = await self._organization_member_repository.find_by_organization_and_user(
            organization_id=organization_id,
            user_id=user_id,
        )
        if requester is None:
            raise OrganizationAccessDeniedError(
                f"User {user_id} cannot access organization members for {organization_id}"
            )
        members = await self._organization_member_repository.find_by_organization_id(
            organization_id
        )
        results: list[OrganizationMemberDTO] = []
        for member in members:
            dto = OrganizationMemberDTO.from_entity(member)
            user = await self._user_repository.find_by_id(member.user_id)
            if user is not None:
                first_name, last_name = self._split_full_name(user.full_name)
                dto.user_first_name = first_name
                dto.user_last_name = last_name
            results.append(dto)
        return results

    @staticmethod
    def _split_full_name(full_name: str) -> tuple[str | None, str | None]:
        parts = full_name.strip().split()
        if not parts:
            return None, None
        if len(parts) == 1:
            return parts[0], None
        return parts[0], " ".join(parts[1:])
