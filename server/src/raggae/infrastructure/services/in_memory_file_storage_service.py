class InMemoryFileStorageService:
    """In-memory object storage for testing."""

    def __init__(self) -> None:
        self._files: dict[str, tuple[bytes, str]] = {}

    async def upload_file(self, storage_key: str, content: bytes, content_type: str) -> None:
        self._files[storage_key] = (content, content_type)

    async def delete_file(self, storage_key: str) -> None:
        self._files.pop(storage_key, None)
