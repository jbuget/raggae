from datetime import UTC, datetime
from uuid import uuid4

import pytest

from raggae.domain.entities.user_model_provider_credential import UserModelProviderCredential
from raggae.domain.exceptions.provider_credential_exceptions import (
    MultipleActiveProviderCredentialsError,
)
from raggae.domain.value_objects.model_provider import ModelProvider


def test_masked_key_with_last_four_should_return_masked_value() -> None:
    # Given
    credential = UserModelProviderCredential(
        id=uuid4(),
        user_id=uuid4(),
        provider=ModelProvider("openai"),
        encrypted_api_key="encrypted-value",
        key_fingerprint="f0f1f2f3",
        key_suffix="abcd",
        is_active=True,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )

    # When
    masked_key = credential.masked_key

    # Then
    assert masked_key == "...abcd"


def test_validate_single_active_credentials_with_multiple_active_should_raise_error() -> None:
    # Given
    user_id = uuid4()
    provider = ModelProvider("gemini")
    now = datetime.now(UTC)
    credentials = [
        UserModelProviderCredential(
            id=uuid4(),
            user_id=user_id,
            provider=provider,
            encrypted_api_key="enc-1",
            key_fingerprint="aa11",
            key_suffix="1111",
            is_active=True,
            created_at=now,
            updated_at=now,
        ),
        UserModelProviderCredential(
            id=uuid4(),
            user_id=user_id,
            provider=provider,
            encrypted_api_key="enc-2",
            key_fingerprint="bb22",
            key_suffix="2222",
            is_active=True,
            created_at=now,
            updated_at=now,
        ),
    ]

    # When / Then
    with pytest.raises(MultipleActiveProviderCredentialsError):
        UserModelProviderCredential.validate_single_active_for_user_and_provider(credentials)
