from typing import Protocol


class FileStorageService(Protocol):
    """Interface for object storage operations."""

    async def upload_file(self, storage_key: str, content: bytes, content_type: str) -> None: ...

    async def delete_file(self, storage_key: str) -> None: ...
