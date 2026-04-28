import sys
import types
from io import BytesIO

import pytest
from docx import Document as DocxDocument
from docx.shared import Inches

from raggae.infrastructure.services.docx_image_extractor import DocxImageExtractor


class TestDocxImageExtractor:
    @pytest.fixture
    def extractor(self) -> DocxImageExtractor:
        return DocxImageExtractor()

    def _make_docx_bytes(self) -> bytes:
        doc = DocxDocument()
        doc.add_paragraph("Some text")
        buf = BytesIO()
        doc.save(buf)
        return buf.getvalue()

    async def test_docx_without_images_returns_empty_list(
        self, extractor: DocxImageExtractor
    ) -> None:
        # Given
        content = self._make_docx_bytes()

        # When
        result = await extractor.extract(content)

        # Then
        assert result == []

    async def test_docx_with_inline_images_returns_image_data(
        self, extractor: DocxImageExtractor, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # Given: mock python-docx to simulate 2 inline images
        fake_image1 = types.SimpleNamespace(
            blob=b"img_data_1",
            content_type="image/jpeg",
        )
        fake_image2 = types.SimpleNamespace(
            blob=b"img_data_2",
            content_type="image/png",
        )

        fake_shape1 = types.SimpleNamespace(image=fake_image1)
        fake_shape2 = types.SimpleNamespace(image=fake_image2)

        class FakeDoc:
            inline_shapes = [fake_shape1, fake_shape2]

        fake_docx = types.SimpleNamespace(Document=lambda buf: FakeDoc())
        monkeypatch.setitem(sys.modules, "docx", fake_docx)

        # When
        result = await extractor.extract(b"PK...")

        # Then
        assert len(result) == 2
        assert result[0].data == b"img_data_1"
        assert result[0].content_type == "image/jpeg"
        assert result[0].image_index == 0
        assert result[1].data == b"img_data_2"
        assert result[1].content_type == "image/png"
        assert result[1].image_index == 1
