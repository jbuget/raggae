import sys
import types
from dataclasses import dataclass

import pytest

from raggae.infrastructure.services.pdf_image_extractor import PdfImageExtractor


@dataclass
class _FakeImage:
    data: bytes
    name: str = "image0.jpg"


class _FakePageWithImages:
    def __init__(self, images: list[_FakeImage]) -> None:
        self.images = images


class _FakePageWithoutImages:
    def __init__(self) -> None:
        self.images: list[_FakeImage] = []


class _FakeReader:
    def __init__(self, pages: list[object]) -> None:
        self.pages = pages


class TestPdfImageExtractor:
    @pytest.fixture(autouse=True)
    def patch_pypdf(self, monkeypatch: pytest.MonkeyPatch) -> None:
        fake_module = types.SimpleNamespace(PdfReader=lambda buf: _FakeReader([]))
        monkeypatch.setitem(sys.modules, "pypdf", fake_module)

    @pytest.fixture
    def extractor(self) -> PdfImageExtractor:
        return PdfImageExtractor()

    async def test_pdf_without_images_returns_empty_list(
        self, extractor: PdfImageExtractor, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # Given: PDF with no images
        fake_module = types.SimpleNamespace(PdfReader=lambda buf: _FakeReader([_FakePageWithoutImages()]))
        monkeypatch.setitem(sys.modules, "pypdf", fake_module)

        # When
        result = await extractor.extract(b"%PDF-1.7")

        # Then
        assert result == []

    async def test_pdf_with_images_returns_image_data(
        self, extractor: PdfImageExtractor, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # Given: PDF with 2 images on page 1 and 1 image on page 2
        page1 = _FakePageWithImages([_FakeImage(b"img1", "img1.jpg"), _FakeImage(b"img2", "img2.png")])
        page2 = _FakePageWithImages([_FakeImage(b"img3", "img3.jpeg")])
        fake_module = types.SimpleNamespace(PdfReader=lambda buf: _FakeReader([page1, page2]))
        monkeypatch.setitem(sys.modules, "pypdf", fake_module)

        # When
        result = await extractor.extract(b"%PDF-1.7")

        # Then
        assert len(result) == 3
        assert result[0].page_number == 1
        assert result[0].image_index == 0
        assert result[1].image_index == 1
        assert result[2].page_number == 2

    async def test_image_data_content_type_jpeg(
        self, extractor: PdfImageExtractor, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # Given: image with jpg extension
        page = _FakePageWithImages([_FakeImage(b"data", "photo.jpg")])
        fake_module = types.SimpleNamespace(PdfReader=lambda buf: _FakeReader([page]))
        monkeypatch.setitem(sys.modules, "pypdf", fake_module)

        # When
        result = await extractor.extract(b"%PDF-1.7")

        # Then
        assert result[0].content_type == "image/jpeg"

    async def test_image_data_content_type_png(
        self, extractor: PdfImageExtractor, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # Given: image with png extension
        page = _FakePageWithImages([_FakeImage(b"data", "diagram.png")])
        fake_module = types.SimpleNamespace(PdfReader=lambda buf: _FakeReader([page]))
        monkeypatch.setitem(sys.modules, "pypdf", fake_module)

        # When
        result = await extractor.extract(b"%PDF-1.7")

        # Then
        assert result[0].content_type == "image/png"
