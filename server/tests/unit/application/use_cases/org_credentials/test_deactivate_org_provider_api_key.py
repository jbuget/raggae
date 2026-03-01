from datetime import UTC, datetime
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from raggae.application.use_cases.org_credentials.deactivate_org_provider_api_key import (
    DeactivateOrgProviderApiKey,
)
from raggae.domain.entities.org_model_provider_credential import OrgModelProviderCredential
from raggae.domain.exceptions.organization_exceptions import OrganizationAccessDeniedError
from raggae.domain.exceptions.provider_credential_exceptions import (
    OrgCredentialInUseError,
    OrgCredentialNotFoundError,
)
from raggae.domain.value_objects.model_provider import ModelProvider
from raggae.domain.value_objects.organization_member_role import OrganizationMemberRole


def _make_member(role: OrganizationMemberRole) -> object:
    return type("Member", (), {"role": role})()


def _make_credential(org_id: object, credential_id: object) -> OrgModelProviderCredential:
    now = datetime.now(UTC)
    return OrgModelProviderCredential(
        id=credential_id,
        organization_id=org_id,
        provider=ModelProvider("openai"),
        encrypted_api_key="enc",
        key_fingerprint="fp",
        key_suffix="1234",
        is_active=True,
        created_at=now,
        updated_at=now,
    )


class TestDeactivateOrgProviderApiKey:
    async def test_deactivate_org_provider_api_key_success(self) -> None:
        # Given
        org_id = uuid4()
        credential_id = uuid4()
        member_repo = AsyncMock()
        member_repo.find_by_organization_and_user = AsyncMock(
            return_value=_make_member(OrganizationMemberRole.OWNER)
        )
        cred_repo = AsyncMock()
        cred_repo.list_by_org_id = AsyncMock(return_value=[_make_credential(org_id, credential_id)])
        project_repo = AsyncMock()
        project_repo.find_by_organization_id = AsyncMock(return_value=[])
        use_case = DeactivateOrgProviderApiKey(
            org_credential_repository=cred_repo,
            organization_member_repository=member_repo,
            project_repository=project_repo,
        )

        # When
        await use_case.execute(credential_id=credential_id, organization_id=org_id, user_id=uuid4())

        # Then
        cred_repo.set_inactive.assert_awaited_once_with(credential_id, org_id)

    async def test_deactivate_org_provider_api_key_not_found_raises_error(self) -> None:
        # Given
        member_repo = AsyncMock()
        member_repo.find_by_organization_and_user = AsyncMock(
            return_value=_make_member(OrganizationMemberRole.OWNER)
        )
        cred_repo = AsyncMock()
        cred_repo.list_by_org_id = AsyncMock(return_value=[])
        use_case = DeactivateOrgProviderApiKey(
            org_credential_repository=cred_repo,
            organization_member_repository=member_repo,
            project_repository=AsyncMock(),
        )

        # When / Then
        with pytest.raises(OrgCredentialNotFoundError):
            await use_case.execute(credential_id=uuid4(), organization_id=uuid4(), user_id=uuid4())

    async def test_deactivate_org_provider_api_key_access_denied(self) -> None:
        # Given
        member_repo = AsyncMock()
        member_repo.find_by_organization_and_user = AsyncMock(
            return_value=_make_member(OrganizationMemberRole.USER)
        )
        use_case = DeactivateOrgProviderApiKey(
            org_credential_repository=AsyncMock(),
            organization_member_repository=member_repo,
            project_repository=AsyncMock(),
        )

        # When / Then
        with pytest.raises(OrganizationAccessDeniedError):
            await use_case.execute(credential_id=uuid4(), organization_id=uuid4(), user_id=uuid4())

    async def test_deactivate_org_provider_api_key_in_use_by_embedding_raises_error(self) -> None:
        # Given
        org_id = uuid4()
        credential_id = uuid4()
        member_repo = AsyncMock()
        member_repo.find_by_organization_and_user = AsyncMock(
            return_value=_make_member(OrganizationMemberRole.OWNER)
        )
        cred_repo = AsyncMock()
        cred_repo.list_by_org_id = AsyncMock(return_value=[_make_credential(org_id, credential_id)])
        project = type(
            "P",
            (),
            {
                "org_embedding_api_key_credential_id": credential_id,
                "org_llm_api_key_credential_id": None,
            },
        )()
        project_repo = AsyncMock()
        project_repo.find_by_organization_id = AsyncMock(return_value=[project])
        use_case = DeactivateOrgProviderApiKey(
            org_credential_repository=cred_repo,
            organization_member_repository=member_repo,
            project_repository=project_repo,
        )

        # When / Then
        with pytest.raises(OrgCredentialInUseError):
            await use_case.execute(
                credential_id=credential_id, organization_id=org_id, user_id=uuid4()
            )

    async def test_deactivate_org_provider_api_key_in_use_by_llm_raises_error(self) -> None:
        # Given
        org_id = uuid4()
        credential_id = uuid4()
        member_repo = AsyncMock()
        member_repo.find_by_organization_and_user = AsyncMock(
            return_value=_make_member(OrganizationMemberRole.OWNER)
        )
        cred_repo = AsyncMock()
        cred_repo.list_by_org_id = AsyncMock(return_value=[_make_credential(org_id, credential_id)])
        project = type(
            "P",
            (),
            {
                "org_embedding_api_key_credential_id": None,
                "org_llm_api_key_credential_id": credential_id,
            },
        )()
        project_repo = AsyncMock()
        project_repo.find_by_organization_id = AsyncMock(return_value=[project])
        use_case = DeactivateOrgProviderApiKey(
            org_credential_repository=cred_repo,
            organization_member_repository=member_repo,
            project_repository=project_repo,
        )

        # When / Then
        with pytest.raises(OrgCredentialInUseError):
            await use_case.execute(
                credential_id=credential_id, organization_id=org_id, user_id=uuid4()
            )
