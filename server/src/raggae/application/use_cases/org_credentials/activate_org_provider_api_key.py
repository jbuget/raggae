from uuid import UUID

from raggae.application.interfaces.repositories.org_provider_credential_repository import (
    OrgProviderCredentialRepository,
)
from raggae.application.interfaces.repositories.organization_member_repository import (
    OrganizationMemberRepository,
)
from raggae.domain.exceptions.organization_exceptions import OrganizationAccessDeniedError
from raggae.domain.exceptions.provider_credential_exceptions import OrgCredentialNotFoundError
from raggae.domain.value_objects.organization_member_role import OrganizationMemberRole


class ActivateOrgProviderApiKey:
    """Use case to activate one organization provider API key."""

    def __init__(
        self,
        org_credential_repository: OrgProviderCredentialRepository,
        organization_member_repository: OrganizationMemberRepository,
    ) -> None:
        self._org_credential_repository = org_credential_repository
        self._organization_member_repository = organization_member_repository

    async def execute(self, credential_id: UUID, organization_id: UUID, user_id: UUID) -> None:
        member = await self._organization_member_repository.find_by_organization_and_user(
            organization_id=organization_id,
            user_id=user_id,
        )
        if member is None or member.role not in {
            OrganizationMemberRole.OWNER,
            OrganizationMemberRole.MAKER,
        }:
            raise OrganizationAccessDeniedError(
                f"User {user_id} cannot manage credentials for organization {organization_id}"
            )
        credentials = await self._org_credential_repository.list_by_org_id(organization_id)
        if not any(c.id == credential_id for c in credentials):
            raise OrgCredentialNotFoundError()
        await self._org_credential_repository.set_active(credential_id, organization_id)
