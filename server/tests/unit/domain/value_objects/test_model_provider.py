import pytest

from raggae.domain.exceptions.validation_errors import InvalidModelProviderError
from raggae.domain.value_objects.model_provider import ModelProvider


def test_create_model_provider_with_supported_value_should_succeed() -> None:
    # Given
    provider = "openai"

    # When
    model_provider = ModelProvider(provider)

    # Then
    assert model_provider.value == "openai"


@pytest.mark.parametrize("provider", ["", "azure-openai", "mistral", "OPENAI"])
def test_create_model_provider_with_unsupported_value_should_raise_error(
    provider: str,
) -> None:
    # Given / When / Then
    with pytest.raises(InvalidModelProviderError):
        ModelProvider(provider)
