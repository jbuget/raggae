from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from raggae.domain.exceptions.provider_credential_exceptions import (
    MultipleActiveProviderCredentialsError,
)
from raggae.domain.value_objects.model_provider import ModelProvider


@dataclass(frozen=True)
class UserModelProviderCredential:
    """User API credential for a model provider."""

    id: UUID
    user_id: UUID
    provider: ModelProvider
    encrypted_api_key: str
    key_fingerprint: str
    key_suffix: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    @property
    def masked_key(self) -> str:
        return f"...{self.key_suffix}"

    @staticmethod
    def validate_single_active_for_user_and_provider(
        credentials: list["UserModelProviderCredential"],
    ) -> None:
        active_count = sum(1 for credential in credentials if credential.is_active)
        if active_count > 1:
            raise MultipleActiveProviderCredentialsError()
