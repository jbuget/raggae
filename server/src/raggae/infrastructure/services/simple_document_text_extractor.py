class SimpleDocumentTextExtractor:
    """Best-effort text extractor for MVP processing."""

    async def extract_text(self, file_name: str, content: bytes, content_type: str) -> str:
        try:
            return content.decode("utf-8")
        except UnicodeDecodeError:
            return content.decode("utf-8", errors="ignore")
