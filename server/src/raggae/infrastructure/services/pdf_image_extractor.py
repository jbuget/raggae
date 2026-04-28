from dataclasses import dataclass
from io import BytesIO

_EXTENSION_TO_CONTENT_TYPE: dict[str, str] = {
    "jpg": "image/jpeg",
    "jpeg": "image/jpeg",
    "png": "image/png",
    "webp": "image/webp",
    "tiff": "image/tiff",
    "tif": "image/tiff",
    "gif": "image/gif",
}


@dataclass(frozen=True)
class ImageData:
    data: bytes
    page_number: int
    image_index: int
    content_type: str


class PdfImageExtractor:
    """Extract embedded images from PDF pages using pypdf."""

    async def extract(self, content: bytes) -> list[ImageData]:
        from pypdf import PdfReader

        reader = PdfReader(BytesIO(content))
        result: list[ImageData] = []
        for page_index, page in enumerate(reader.pages):
            for img_index, img in enumerate(page.images):
                ext = img.name.rsplit(".", 1)[-1].lower() if "." in img.name else ""
                content_type = _EXTENSION_TO_CONTENT_TYPE.get(ext, "application/octet-stream")
                result.append(
                    ImageData(
                        data=img.data,
                        page_number=page_index + 1,
                        image_index=img_index,
                        content_type=content_type,
                    )
                )
        return result
