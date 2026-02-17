from dataclasses import dataclass

from raggae.domain.exceptions.validation_errors import InvalidModelProviderError

_SUPPORTED_MODEL_PROVIDERS = {"openai", "gemini", "anthropic"}


@dataclass(frozen=True)
class ModelProvider:
    """Value object for supported model providers."""

    value: str

    def __post_init__(self) -> None:
        if self.value not in _SUPPORTED_MODEL_PROVIDERS:
            raise InvalidModelProviderError(
                f"Unsupported model provider: {self.value}",
            )
