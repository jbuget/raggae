from dataclasses import dataclass
from io import BytesIO


@dataclass(frozen=True)
class DocxImageData:
    data: bytes
    image_index: int
    content_type: str


class DocxImageExtractor:
    """Extract inline images from DOCX documents using python-docx."""

    async def extract(self, content: bytes) -> list[DocxImageData]:
        from docx import Document as DocxDocument

        doc = DocxDocument(BytesIO(content))
        result: list[DocxImageData] = []
        for index, shape in enumerate(doc.inline_shapes):
            img = shape.image
            result.append(
                DocxImageData(
                    data=img.blob,
                    image_index=index,
                    content_type=img.content_type,
                )
            )
        return result
