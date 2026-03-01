from uuid import UUID

from raggae.application.dto.org_provider_credential_dto import OrgProviderCredentialDTO
from raggae.application.interfaces.repositories.org_provider_credential_repository import (
    OrgProviderCredentialRepository,
)
from raggae.application.interfaces.repositories.organization_member_repository import (
    OrganizationMemberRepository,
)
from raggae.domain.exceptions.organization_exceptions import OrganizationAccessDeniedError


class ListOrgProviderApiKeys:
    """Use case to list all provider API keys for an organization."""

    def __init__(
        self,
        org_credential_repository: OrgProviderCredentialRepository,
        organization_member_repository: OrganizationMemberRepository,
    ) -> None:
        self._org_credential_repository = org_credential_repository
        self._organization_member_repository = organization_member_repository

    async def execute(self, organization_id: UUID, user_id: UUID) -> list[OrgProviderCredentialDTO]:
        member = await self._organization_member_repository.find_by_organization_and_user(
            organization_id=organization_id,
            user_id=user_id,
        )
        if member is None:
            raise OrganizationAccessDeniedError(
                f"User {user_id} is not a member of organization {organization_id}"
            )
        credentials = await self._org_credential_repository.list_by_org_id(organization_id)
        return [
            OrgProviderCredentialDTO(
                id=c.id,
                organization_id=c.organization_id,
                provider=c.provider.value,
                masked_key=c.masked_key,
                is_active=c.is_active,
                created_at=c.created_at,
                updated_at=c.updated_at,
            )
            for c in credentials
        ]
