import re

from raggae.application.interfaces.services.text_chunker_service import TextChunkerService
from raggae.domain.value_objects.chunking_strategy import ChunkingStrategy

_HEADING_RE = re.compile(r"^\s{0,3}#{1,6}\s+\S|^\s*\d+(?:\.\d+)*[.)]?\s+\S")


class HeadingSectionTextChunkerService:
    """Splits text by heading sections, then falls back to fixed windows when needed."""

    def __init__(self, fallback_chunker: TextChunkerService) -> None:
        self._fallback_chunker = fallback_chunker

    async def chunk_text(
        self,
        text: str,
        strategy: ChunkingStrategy = ChunkingStrategy.HEADING_SECTION,
        embedding_service=None,
    ) -> list[str]:
        del embedding_service
        del strategy
        normalized = text.strip()
        if not normalized:
            return []

        sections: list[str] = []
        current_lines: list[str] = []
        for line in normalized.splitlines():
            if _HEADING_RE.match(line.strip()) and current_lines:
                section = "\n".join(current_lines).strip()
                if section:
                    sections.append(section)
                current_lines = [line]
            else:
                current_lines.append(line)

        last_section = "\n".join(current_lines).strip()
        if last_section:
            sections.append(last_section)

        chunks: list[str] = []
        for section in sections:
            fallback_chunks = await self._fallback_chunker.chunk_text(section)
            chunks.extend(fallback_chunks if fallback_chunks else [section])
        return chunks
