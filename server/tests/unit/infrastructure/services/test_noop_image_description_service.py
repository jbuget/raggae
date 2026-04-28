import pytest

from raggae.domain.exceptions.document_exceptions import VisionNotSupportedError
from raggae.infrastructure.services.noop_image_description_service import NoopImageDescriptionService


class TestNoopImageDescriptionService:
    @pytest.fixture
    def service(self) -> NoopImageDescriptionService:
        return NoopImageDescriptionService()

    def test_supports_vision_returns_false(self, service: NoopImageDescriptionService) -> None:
        assert service.supports_vision() is False

    async def test_describe_image_raises_vision_not_supported_error(
        self, service: NoopImageDescriptionService
    ) -> None:
        with pytest.raises(VisionNotSupportedError):
            await service.describe_image(b"\xff\xd8\xff", "image/jpeg")
