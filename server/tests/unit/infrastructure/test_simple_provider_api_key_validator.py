import pytest

from raggae.domain.exceptions.validation_errors import InvalidProviderApiKeyError
from raggae.domain.value_objects.model_provider import ModelProvider
from raggae.infrastructure.services.simple_provider_api_key_validator import (
    SimpleProviderApiKeyValidator,
)


class TestSimpleProviderApiKeyValidator:
    def test_validate_with_short_key_raises_error(self) -> None:
        # Given
        validator = SimpleProviderApiKeyValidator()

        # When / Then
        with pytest.raises(InvalidProviderApiKeyError):
            validator.validate(ModelProvider("openai"), "abc")

    def test_validate_with_valid_key_succeeds(self) -> None:
        # Given
        validator = SimpleProviderApiKeyValidator()

        # When
        validator.validate(ModelProvider("gemini"), "AIza-test-1234")

        # Then
        assert True

    def test_validate_with_invalid_provider_prefix_raises_error(self) -> None:
        # Given
        validator = SimpleProviderApiKeyValidator()

        # When / Then
        with pytest.raises(InvalidProviderApiKeyError):
            validator.validate(ModelProvider("openai"), "bad-prefix-1234")
