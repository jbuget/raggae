from datetime import UTC, datetime
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from raggae.application.use_cases.org_credentials.activate_org_provider_api_key import (
    ActivateOrgProviderApiKey,
)
from raggae.domain.entities.org_model_provider_credential import OrgModelProviderCredential
from raggae.domain.exceptions.organization_exceptions import OrganizationAccessDeniedError
from raggae.domain.exceptions.provider_credential_exceptions import OrgCredentialNotFoundError
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
        is_active=False,
        created_at=now,
        updated_at=now,
    )


class TestActivateOrgProviderApiKey:
    async def test_activate_org_provider_api_key_success(self) -> None:
        # Given
        org_id = uuid4()
        credential_id = uuid4()
        member_repo = AsyncMock()
        member_repo.find_by_organization_and_user = AsyncMock(
            return_value=_make_member(OrganizationMemberRole.OWNER)
        )
        cred_repo = AsyncMock()
        cred_repo.list_by_org_id = AsyncMock(return_value=[_make_credential(org_id, credential_id)])
        use_case = ActivateOrgProviderApiKey(
            org_credential_repository=cred_repo,
            organization_member_repository=member_repo,
        )

        # When
        await use_case.execute(credential_id=credential_id, organization_id=org_id, user_id=uuid4())

        # Then
        cred_repo.set_active.assert_awaited_once_with(credential_id, org_id)

    async def test_activate_org_provider_api_key_does_not_deactivate_others(self) -> None:
        # Given — deux credentials pour le même provider
        org_id = uuid4()
        credential_id = uuid4()
        other_id = uuid4()
        now = datetime.now(UTC)
        other = OrgModelProviderCredential(
            id=other_id,
            organization_id=org_id,
            provider=ModelProvider("openai"),
            encrypted_api_key="enc2",
            key_fingerprint="fp2",
            key_suffix="5678",
            is_active=True,
            created_at=now,
            updated_at=now,
        )
        member_repo = AsyncMock()
        member_repo.find_by_organization_and_user = AsyncMock(
            return_value=_make_member(OrganizationMemberRole.OWNER)
        )
        cred_repo = AsyncMock()
        cred_repo.list_by_org_id = AsyncMock(
            return_value=[_make_credential(org_id, credential_id), other]
        )
        use_case = ActivateOrgProviderApiKey(
            org_credential_repository=cred_repo,
            organization_member_repository=member_repo,
        )

        # When
        await use_case.execute(credential_id=credential_id, organization_id=org_id, user_id=uuid4())

        # Then — les autres ne sont PAS désactivées
        cred_repo.set_active.assert_awaited_once_with(credential_id, org_id)
        cred_repo.set_inactive.assert_not_awaited()

    async def test_activate_org_provider_api_key_not_found_raises_error(self) -> None:
        # Given
        member_repo = AsyncMock()
        member_repo.find_by_organization_and_user = AsyncMock(
            return_value=_make_member(OrganizationMemberRole.OWNER)
        )
        cred_repo = AsyncMock()
        cred_repo.list_by_org_id = AsyncMock(return_value=[])
        use_case = ActivateOrgProviderApiKey(
            org_credential_repository=cred_repo,
            organization_member_repository=member_repo,
        )

        # When / Then
        with pytest.raises(OrgCredentialNotFoundError):
            await use_case.execute(credential_id=uuid4(), organization_id=uuid4(), user_id=uuid4())

    async def test_activate_org_provider_api_key_access_denied(self) -> None:
        # Given
        member_repo = AsyncMock()
        member_repo.find_by_organization_and_user = AsyncMock(
            return_value=_make_member(OrganizationMemberRole.USER)
        )
        use_case = ActivateOrgProviderApiKey(
            org_credential_repository=AsyncMock(),
            organization_member_repository=member_repo,
        )

        # When / Then
        with pytest.raises(OrganizationAccessDeniedError):
            await use_case.execute(credential_id=uuid4(), organization_id=uuid4(), user_id=uuid4())
