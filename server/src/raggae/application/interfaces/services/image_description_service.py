from typing import Protocol


class ImageDescriptionService(Protocol):
    def supports_vision(self) -> bool: ...

    async def describe_image(self, image_bytes: bytes, content_type: str) -> str: ...
