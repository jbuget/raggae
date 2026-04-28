from io import BytesIO

import pytest
from PIL import Image

from raggae.infrastructure.services.image_resizer_service import ImageResizerService


def _make_image_bytes(width: int, height: int, fmt: str = "JPEG") -> bytes:
    img = Image.new("RGB", (width, height), color=(128, 64, 32))
    buf = BytesIO()
    img.save(buf, format=fmt)
    return buf.getvalue()


class TestImageResizerService:
    async def test_small_image_returned_unchanged(self) -> None:
        # Given: image below max_bytes threshold
        content = _make_image_bytes(10, 10)
        service = ImageResizerService(max_bytes=len(content) + 1)

        # When
        result = await service.resize_if_needed(content, "image/jpeg")

        # Then
        assert result == content

    async def test_large_image_is_resized(self) -> None:
        # Given: image above threshold
        content = _make_image_bytes(500, 500)
        service = ImageResizerService(max_bytes=len(content) // 2)

        # When
        result = await service.resize_if_needed(content, "image/jpeg")

        # Then: result is smaller than original
        assert len(result) < len(content)

    async def test_large_image_result_is_valid_image(self) -> None:
        # Given
        content = _make_image_bytes(500, 500)
        service = ImageResizerService(max_bytes=len(content) // 2)

        # When
        result = await service.resize_if_needed(content, "image/jpeg")

        # Then: result can be opened by Pillow
        img = Image.open(BytesIO(result))
        assert img.size[0] > 0

    async def test_tiff_image_converted_to_png(self) -> None:
        # Given: a TIFF image larger than threshold
        content = _make_image_bytes(500, 500, fmt="TIFF")
        service = ImageResizerService(max_bytes=len(content) // 2)

        # When
        result = await service.resize_if_needed(content, "image/tiff")

        # Then: output format is PNG
        img = Image.open(BytesIO(result))
        assert img.format == "PNG"
