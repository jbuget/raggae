from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from raggae.domain.value_objects.model_provider import ModelProvider


@dataclass(frozen=True)
class OrgModelProviderCredential:
    """Organization API credential for a model provider."""

    id: UUID
    organization_id: UUID
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
