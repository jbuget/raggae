from raggae.domain.value_objects.chunking_strategy import ChunkingStrategy


class ParagraphTextChunkerService:
    """Groups paragraphs into chunks while preserving paragraph boundaries."""

    def __init__(self, chunk_size: int) -> None:
        self._chunk_size = chunk_size

    async def chunk_text(
        self,
        text: str,
        strategy: ChunkingStrategy = ChunkingStrategy.PARAGRAPH,
    ) -> list[str]:
        del strategy
        normalized = text.strip()
        if not normalized:
            return []

        paragraphs = [
            paragraph.strip() for paragraph in normalized.split("\n\n") if paragraph.strip()
        ]
        if not paragraphs:
            return []

        chunks: list[str] = []
        current = paragraphs[0]
        for paragraph in paragraphs[1:]:
            candidate = f"{current}\n\n{paragraph}"
            if len(candidate) <= self._chunk_size:
                current = candidate
                continue
            chunks.append(current)
            current = paragraph
        chunks.append(current)
        return chunks
