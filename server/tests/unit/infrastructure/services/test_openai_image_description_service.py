import base64
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from raggae.infrastructure.services.openai_image_description_service import (
    OpenAIImageDescriptionService,
)

_VISION_MODELS = ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-4-vision-preview"]
_NON_VISION_MODELS = ["gpt-3.5-turbo", "gpt-3.5-turbo-16k", "gpt-4"]


class TestOpenAIImageDescriptionService:
    @pytest.mark.parametrize("model", _VISION_MODELS)
    def test_supports_vision_for_vision_models(self, model: str) -> None:
        service = OpenAIImageDescriptionService(api_key="key", model=model)
        assert service.supports_vision() is True

    @pytest.mark.parametrize("model", _NON_VISION_MODELS)
    def test_supports_vision_false_for_non_vision_models(self, model: str) -> None:
        service = OpenAIImageDescriptionService(api_key="key", model=model)
        assert service.supports_vision() is False

    async def test_describe_image_calls_api_with_base64_content(self) -> None:
        # Given
        service = OpenAIImageDescriptionService(api_key="key", model="gpt-4o")
        service._client = AsyncMock()  # type: ignore[attr-defined]
        service._client.chat.completions.create.return_value = SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content="A diagram."))]
        )
        image_bytes = b"\xff\xd8\xff"

        # When
        result = await service.describe_image(image_bytes, "image/jpeg")

        # Then
        assert result == "A diagram."
        call_args = service._client.chat.completions.create.call_args
        messages = call_args.kwargs["messages"]
        image_content = messages[0]["content"][0]
        assert image_content["type"] == "image_url"
        expected_b64 = base64.b64encode(image_bytes).decode()
        assert expected_b64 in image_content["image_url"]["url"]

    async def test_describe_image_returns_empty_string_on_null_response(self) -> None:
        # Given
        service = OpenAIImageDescriptionService(api_key="key", model="gpt-4o")
        service._client = AsyncMock()  # type: ignore[attr-defined]
        service._client.chat.completions.create.return_value = SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content=None))]
        )

        # When
        result = await service.describe_image(b"data", "image/png")

        # Then
        assert result == ""
