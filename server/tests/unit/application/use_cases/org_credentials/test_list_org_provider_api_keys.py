from datetime import UTC, datetime
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from raggae.application.use_cases.org_credentials.list_org_provider_api_keys import (
    ListOrgProviderApiKeys,
)
from raggae.domain.entities.org_model_provider_credential import OrgModelProviderCredential
from raggae.domain.exceptions.organization_exceptions import OrganizationAccessDeniedError
from raggae.domain.value_objects.model_provider import ModelProvider
from raggae.domain.value_objects.organization_member_role import OrganizationMemberRole


def _make_member(role: OrganizationMemberRole) -> object:
    return type("Member", (), {"role": role})()


def _make_credential(org_id: object) -> OrgModelProviderCredential:
    now = datetime.now(UTC)
    return OrgModelProviderCredential(
        id=uuid4(),
        organization_id=org_id,
        provider=ModelProvider("openai"),
        encrypted_api_key="enc",
        key_fingerprint="fp",
        key_suffix="abcd",
        is_active=True,
        created_at=now,
        updated_at=now,
    )


class TestListOrgProviderApiKeys:
    async def test_list_org_provider_api_keys_returns_masked_credentials(self) -> None:
        # Given
        org_id = uuid4()
        member_repo = AsyncMock()
        member_repo.find_by_organization_and_user = AsyncMock(
            return_value=_make_member(OrganizationMemberRole.OWNER)
        )
        cred_repo = AsyncMock()
        cred_repo.list_by_org_id = AsyncMock(return_value=[_make_credential(org_id)])
        use_case = ListOrgProviderApiKeys(
            org_credential_repository=cred_repo,
            organization_member_repository=member_repo,
        )

        # When
        result = await use_case.execute(organization_id=org_id, user_id=uuid4())

        # Then
        assert len(result) == 1
        assert result[0].masked_key == "...abcd"
        assert result[0].provider == "openai"

    async def test_list_org_provider_api_keys_accessible_by_maker(self) -> None:
        # Given
        member_repo = AsyncMock()
        member_repo.find_by_organization_and_user = AsyncMock(
            return_value=_make_member(OrganizationMemberRole.MAKER)
        )
        cred_repo = AsyncMock()
        cred_repo.list_by_org_id = AsyncMock(return_value=[])
        use_case = ListOrgProviderApiKeys(
            org_credential_repository=cred_repo,
            organization_member_repository=member_repo,
        )

        # When
        result = await use_case.execute(organization_id=uuid4(), user_id=uuid4())

        # Then
        assert result == []

    async def test_list_org_provider_api_keys_accessible_by_user_role(self) -> None:
        # Given
        member_repo = AsyncMock()
        member_repo.find_by_organization_and_user = AsyncMock(
            return_value=_make_member(OrganizationMemberRole.USER)
        )
        cred_repo = AsyncMock()
        cred_repo.list_by_org_id = AsyncMock(return_value=[])
        use_case = ListOrgProviderApiKeys(
            org_credential_repository=cred_repo,
            organization_member_repository=member_repo,
        )

        # When
        result = await use_case.execute(organization_id=uuid4(), user_id=uuid4())

        # Then
        assert result == []

    async def test_list_org_provider_api_keys_access_denied_for_non_member(self) -> None:
        # Given
        member_repo = AsyncMock()
        member_repo.find_by_organization_and_user = AsyncMock(return_value=None)
        use_case = ListOrgProviderApiKeys(
            org_credential_repository=AsyncMock(),
            organization_member_repository=member_repo,
        )

        # When / Then
        with pytest.raises(OrganizationAccessDeniedError):
            await use_case.execute(organization_id=uuid4(), user_id=uuid4())
