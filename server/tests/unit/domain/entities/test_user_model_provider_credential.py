from datetime import UTC, datetime
from uuid import uuid4

from raggae.domain.entities.user_model_provider_credential import UserModelProviderCredential
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
