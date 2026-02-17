from raggae.domain.exceptions.validation_errors import InvalidProviderApiKeyError
from raggae.domain.value_objects.model_provider import ModelProvider


class SimpleProviderApiKeyValidator:
    """Basic provider API key format validator."""

    def validate(self, provider: ModelProvider, api_key: str) -> None:
        normalized = api_key.strip()
        if len(normalized) < 4:
            raise InvalidProviderApiKeyError("Invalid API key format")
        expected_prefix_by_provider = {
            "openai": "sk-",
            "gemini": "AIza",
            "anthropic": "sk-ant-",
        }
        expected_prefix = expected_prefix_by_provider.get(provider.value)
        if expected_prefix is not None and not normalized.startswith(expected_prefix):
            raise InvalidProviderApiKeyError("Invalid API key format")
