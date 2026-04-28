from raggae.domain.exceptions.document_exceptions import VisionNotSupportedError


class NoopImageDescriptionService:
    """No-op implementation for providers without vision support."""

    def supports_vision(self) -> bool:
        return False

    async def describe_image(self, image_bytes: bytes, content_type: str) -> str:
        raise VisionNotSupportedError("This provider does not support vision capabilities.")
