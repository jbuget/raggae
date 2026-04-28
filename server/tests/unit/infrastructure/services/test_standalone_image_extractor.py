from unittest.mock import AsyncMock, MagicMock

import pytest

from raggae.infrastructure.services.noop_image_description_service import NoopImageDescriptionService
from raggae.infrastructure.services.standalone_image_document_text_extractor import (
    StandaloneImageDocumentTextExtractor,
)


class TestStandaloneImageDocumentTextExtractor:
    @pytest.fixture
    def mock_description_service(self) -> AsyncMock:
        svc = AsyncMock()
        svc.supports_vision.return_value = True
        svc.describe_image.return_value = "A bar chart showing Q1 results."
        return svc

    @pytest.fixture
    def mock_resizer(self) -> AsyncMock:
        resizer = AsyncMock()
        resizer.resize_if_needed.side_effect = lambda data, ct: data
        return resizer

    async def test_returns_image_chunk_with_description(
        self, mock_description_service: AsyncMock, mock_resizer: AsyncMock
    ) -> None:
        # Given
        extractor = StandaloneImageDocumentTextExtractor(mock_description_service, mock_resizer)

        # When
        result = await extractor.extract(b"\xff\xd8\xff", "image/jpeg")

        # Then
        assert result.startswith("[IMAGE]")
        assert "A bar chart showing Q1 results." in result

    async def test_resizer_called_before_description(
        self, mock_description_service: AsyncMock, mock_resizer: AsyncMock
    ) -> None:
        # Given
        extractor = StandaloneImageDocumentTextExtractor(mock_description_service, mock_resizer)

        # When
        await extractor.extract(b"\xff\xd8\xff", "image/jpeg")

        # Then
        mock_resizer.resize_if_needed.assert_called_once_with(b"\xff\xd8\xff", "image/jpeg")

    async def test_no_vision_returns_empty_string(self, mock_resizer: AsyncMock) -> None:
        # Given
        noop = NoopImageDescriptionService()
        extractor = StandaloneImageDocumentTextExtractor(noop, mock_resizer)

        # When
        result = await extractor.extract(b"\xff\xd8\xff", "image/jpeg")

        # Then
        assert result == ""
