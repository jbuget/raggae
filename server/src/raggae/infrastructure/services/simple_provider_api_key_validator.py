from raggae.domain.value_objects.model_provider import ModelProvider


class SimpleProviderApiKeyValidator:
    """Basic provider API key format validator."""

    def validate(self, provider: ModelProvider, api_key: str) -> None:
        _ = provider
        if len(api_key.strip()) < 4:
            raise ValueError("API key is too short")
