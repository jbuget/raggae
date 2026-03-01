from datetime import UTC, datetime
from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest

from raggae.application.use_cases.org_credentials.save_org_provider_api_key import (
    SaveOrgProviderApiKey,
)
from raggae.domain.entities.org_model_provider_credential import OrgModelProviderCredential
from raggae.domain.exceptions.organization_exceptions import OrganizationAccessDeniedError
from raggae.domain.exceptions.provider_credential_exceptions import OrgDuplicateCredentialError
from raggae.domain.exceptions.validation_errors import InvalidModelProviderError
from raggae.domain.value_objects.model_provider import ModelProvider
from raggae.domain.value_objects.organization_member_role import OrganizationMemberRole


def _make_member(role: OrganizationMemberRole) -> object:
    return type("Member", (), {"role": role})()


def _make_existing_credential(org_id: object, fingerprint: str) -> OrgModelProviderCredential:
    now = datetime.now(UTC)
    return OrgModelProviderCredential(
        id=uuid4(),
        organization_id=org_id,
        provider=ModelProvider("openai"),
        encrypted_api_key="enc",
        key_fingerprint=fingerprint,
        key_suffix="1111",
        is_active=True,
        created_at=now,
        updated_at=now,
    )


class TestSaveOrgProviderApiKey:
    async def test_save_org_provider_api_key_success_as_owner(self) -> None:
        # Given
        org_id = uuid4()
        user_id = uuid4()
        member_repo = AsyncMock()
        member_repo.find_by_organization_and_user = AsyncMock(
            return_value=_make_member(OrganizationMemberRole.OWNER)
        )
        cred_repo = AsyncMock()
        cred_repo.list_by_org_id_and_provider = AsyncMock(return_value=[])
        crypto = Mock()
        crypto.fingerprint.return_value = "fp-new"
        crypto.encrypt.return_value = "encrypted"
        use_case = SaveOrgProviderApiKey(
            org_credential_repository=cred_repo,
            organization_member_repository=member_repo,
            provider_api_key_validator=Mock(),
            provider_api_key_crypto_service=crypto,
        )

        # When
        result = await use_case.execute(
            organization_id=org_id, user_id=user_id, provider="openai", api_key="sk-test-abcd"
        )

        # Then
        assert result.provider == "openai"
        assert result.masked_key == "...abcd"
        assert result.is_active is True
        cred_repo.save.assert_awaited_once()

    async def test_save_org_provider_api_key_success_as_maker(self) -> None:
        # Given
        member_repo = AsyncMock()
        member_repo.find_by_organization_and_user = AsyncMock(
            return_value=_make_member(OrganizationMemberRole.MAKER)
        )
        cred_repo = AsyncMock()
        cred_repo.list_by_org_id_and_provider = AsyncMock(return_value=[])
        crypto = Mock()
        crypto.fingerprint.return_value = "fp-new"
        crypto.encrypt.return_value = "encrypted"
        use_case = SaveOrgProviderApiKey(
            org_credential_repository=cred_repo,
            organization_member_repository=member_repo,
            provider_api_key_validator=Mock(),
            provider_api_key_crypto_service=crypto,
        )

        # When
        result = await use_case.execute(
            organization_id=uuid4(), user_id=uuid4(), provider="gemini", api_key="AIza-test-1234"
        )

        # Then
        assert result.is_active is True

    async def test_save_org_provider_api_key_access_denied_for_user_role(self) -> None:
        # Given
        member_repo = AsyncMock()
        member_repo.find_by_organization_and_user = AsyncMock(
            return_value=_make_member(OrganizationMemberRole.USER)
        )
        use_case = SaveOrgProviderApiKey(
            org_credential_repository=AsyncMock(),
            organization_member_repository=member_repo,
            provider_api_key_validator=Mock(),
            provider_api_key_crypto_service=Mock(),
        )

        # When / Then
        with pytest.raises(OrganizationAccessDeniedError):
            await use_case.execute(
                organization_id=uuid4(), user_id=uuid4(), provider="openai", api_key="sk-test"
            )

    async def test_save_org_provider_api_key_access_denied_for_non_member(self) -> None:
        # Given
        member_repo = AsyncMock()
        member_repo.find_by_organization_and_user = AsyncMock(return_value=None)
        use_case = SaveOrgProviderApiKey(
            org_credential_repository=AsyncMock(),
            organization_member_repository=member_repo,
            provider_api_key_validator=Mock(),
            provider_api_key_crypto_service=Mock(),
        )

        # When / Then
        with pytest.raises(OrganizationAccessDeniedError):
            await use_case.execute(
                organization_id=uuid4(), user_id=uuid4(), provider="openai", api_key="sk-test"
            )

    async def test_save_org_provider_api_key_duplicate_fingerprint_raises_error(self) -> None:
        # Given
        org_id = uuid4()
        member_repo = AsyncMock()
        member_repo.find_by_organization_and_user = AsyncMock(
            return_value=_make_member(OrganizationMemberRole.OWNER)
        )
        existing = _make_existing_credential(org_id, fingerprint="same-fp")
        cred_repo = AsyncMock()
        cred_repo.list_by_org_id_and_provider = AsyncMock(return_value=[existing])
        crypto = Mock()
        crypto.fingerprint.return_value = "same-fp"
        use_case = SaveOrgProviderApiKey(
            org_credential_repository=cred_repo,
            organization_member_repository=member_repo,
            provider_api_key_validator=Mock(),
            provider_api_key_crypto_service=crypto,
        )

        # When / Then
        with pytest.raises(OrgDuplicateCredentialError):
            await use_case.execute(
                organization_id=org_id, user_id=uuid4(), provider="openai", api_key="sk-test-xxxx"
            )

    async def test_save_org_provider_api_key_does_not_deactivate_existing(self) -> None:
        # Given
        org_id = uuid4()
        member_repo = AsyncMock()
        member_repo.find_by_organization_and_user = AsyncMock(
            return_value=_make_member(OrganizationMemberRole.OWNER)
        )
        existing = _make_existing_credential(org_id, fingerprint="other-fp")
        cred_repo = AsyncMock()
        cred_repo.list_by_org_id_and_provider = AsyncMock(return_value=[existing])
        crypto = Mock()
        crypto.fingerprint.return_value = "new-fp"
        crypto.encrypt.return_value = "encrypted"
        use_case = SaveOrgProviderApiKey(
            org_credential_repository=cred_repo,
            organization_member_repository=member_repo,
            provider_api_key_validator=Mock(),
            provider_api_key_crypto_service=crypto,
        )

        # When
        await use_case.execute(
            organization_id=org_id, user_id=uuid4(), provider="openai", api_key="sk-test-xxxx"
        )

        # Then — les credentials existantes ne sont PAS désactivées
        cred_repo.set_inactive.assert_not_awaited()

    async def test_save_org_provider_api_key_invalid_provider_raises_error(self) -> None:
        # Given
        use_case = SaveOrgProviderApiKey(
            org_credential_repository=AsyncMock(),
            organization_member_repository=AsyncMock(),
            provider_api_key_validator=Mock(),
            provider_api_key_crypto_service=Mock(),
        )

        # When / Then
        with pytest.raises(InvalidModelProviderError):
            await use_case.execute(
                organization_id=uuid4(), user_id=uuid4(), provider="mistral", api_key="invalid"
            )
