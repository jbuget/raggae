from typing import Protocol
from uuid import UUID


class ProviderApiKeyResolver(Protocol):
    """Resolve the effective provider API key for a user."""

    async def resolve(self, user_id: UUID, provider: str) -> str | None: ...
