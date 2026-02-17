from typing import Protocol

from raggae.domain.value_objects.model_provider import ModelProvider


class ProviderApiKeyValidator(Protocol):
    """Interface for provider API key format validation."""

    def validate(self, provider: ModelProvider, api_key: str) -> None: ...
