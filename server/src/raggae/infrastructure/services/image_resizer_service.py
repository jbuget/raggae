import logging
from io import BytesIO

logger = logging.getLogger(__name__)

_TIFF_CONTENT_TYPES = {"image/tiff", "image/tiff-fx"}


class ImageResizerService:
    """Resize images exceeding max_bytes, converting TIFF to PNG."""

    def __init__(self, max_bytes: int = 4_194_304) -> None:
        self._max_bytes = max_bytes

    async def resize_if_needed(self, image_bytes: bytes, content_type: str) -> bytes:
        if len(image_bytes) <= self._max_bytes:
            return image_bytes

        try:
            from PIL import Image
        except ModuleNotFoundError:  # pragma: no cover
            logger.warning("Pillow is not installed; image resizing skipped.")
            return image_bytes

        logger.warning(
            "image_resized",
            extra={"original_size": len(image_bytes), "max_bytes": self._max_bytes},
        )

        with Image.open(BytesIO(image_bytes)) as img:
            is_tiff = content_type in _TIFF_CONTENT_TYPES or (img.format or "").upper() == "TIFF"
            output_format = "PNG" if is_tiff else (img.format or "JPEG")
            scale = (self._max_bytes / len(image_bytes)) ** 0.5
            new_size = (max(1, int(img.size[0] * scale)), max(1, int(img.size[1] * scale)))
            resized = img.resize(new_size)
            buf = BytesIO()
            resized.save(buf, format=output_format)
            return buf.getvalue()
