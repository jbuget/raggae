from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass
class ProviderCredentialDTO:
    id: UUID
    provider: str
    masked_key: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
