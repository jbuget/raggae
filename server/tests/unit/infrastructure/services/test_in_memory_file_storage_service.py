import pytest

from raggae.infrastructure.services.in_memory_file_storage_service import (
    InMemoryFileStorageService,
)


class TestInMemoryFileStorageService:
    async def test_download_file_returns_uploaded_content_and_content_type(self) -> None:
        service = InMemoryFileStorageService()

        await service.upload_file("documents/a.txt", b"hello", "text/plain")

        content, content_type = await service.download_file("documents/a.txt")

        assert content == b"hello"
        assert content_type == "text/plain"

    async def test_download_file_raises_when_not_found(self) -> None:
        service = InMemoryFileStorageService()

        with pytest.raises(FileNotFoundError):
            await service.download_file("documents/missing.txt")
