from raggae.application.interfaces.services.file_metadata_extractor import FileMetadata


class InMemoryFileMetadataExtractor:
    """Deterministic file metadata extractor for tests."""

    def __init__(self, metadata: FileMetadata | None = None) -> None:
        self._metadata = metadata or FileMetadata()

    async def extract_metadata(
        self,
        file_name: str,
        content: bytes,
        content_type: str,
    ) -> FileMetadata:
        del file_name, content, content_type
        return self._metadata
