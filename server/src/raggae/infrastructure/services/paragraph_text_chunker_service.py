from raggae.application.interfaces.services.embedding_service import EmbeddingService
from raggae.domain.value_objects.chunking_strategy import ChunkingStrategy

import re

_SENTENCE_END_RE = re.compile(r"(?<=[.!?;:])\s+")


class ParagraphTextChunkerService:
    """Groups paragraphs into chunks while preserving paragraph boundaries.

    Improvements over baseline:
    - Splits oversized paragraphs at sentence boundaries to reduce chunk_size_std
    - Merges tiny chunks into neighbours to eliminate single_word_chunks
    """

    def __init__(self, chunk_size: int, min_chunk_size: int = 50) -> None:
        self._chunk_size = chunk_size
        self._min_chunk_size = max(0, min(min_chunk_size, chunk_size // 2))

    async def chunk_text(
        self,
        text: str,
        strategy: ChunkingStrategy = ChunkingStrategy.PARAGRAPH,
        embedding_service: EmbeddingService | None = None,
    ) -> list[str]:
        del embedding_service
        del strategy
        normalized = text.strip()
        if not normalized:
            return []

        paragraphs = [
            paragraph.strip() for paragraph in normalized.split("\n\n") if paragraph.strip()
        ]
        if not paragraphs:
            return []

        # Split oversized paragraphs at sentence boundaries
        split_paragraphs: list[str] = []
        for paragraph in paragraphs:
            if len(paragraph) <= self._chunk_size:
                split_paragraphs.append(paragraph)
            else:
                split_paragraphs.extend(self._split_at_sentences(paragraph))

        # Group into chunks
        chunks: list[str] = []
        current = split_paragraphs[0]
        for paragraph in split_paragraphs[1:]:
            candidate = f"{current}\n\n{paragraph}"
            if len(candidate) <= self._chunk_size:
                current = candidate
                continue
            chunks.append(current)
            current = paragraph
        chunks.append(current)

        # Merge tiny chunks
        return self._merge_small_chunks(chunks)

    def _split_at_sentences(self, text: str) -> list[str]:
        """Split a large paragraph at sentence boundaries."""
        sentences = _SENTENCE_END_RE.split(text)
        if len(sentences) <= 1:
            # No sentence boundaries, hard split
            parts: list[str] = []
            start = 0
            while start < len(text):
                end = min(start + self._chunk_size, len(text))
                piece = text[start:end].strip()
                if piece:
                    parts.append(piece)
                start = end
            return parts if parts else [text]

        result: list[str] = []
        current = sentences[0]
        for sentence in sentences[1:]:
            candidate = f"{current} {sentence}"
            if len(candidate) <= self._chunk_size:
                current = candidate
            else:
                if current.strip():
                    result.append(current.strip())
                current = sentence
        if current.strip():
            result.append(current.strip())
        return result if result else [text]

    def _merge_small_chunks(self, chunks: list[str]) -> list[str]:
        """Merge chunks smaller than min_chunk_size into neighbours."""
        if self._min_chunk_size <= 0 or len(chunks) <= 1:
            return chunks

        merged: list[str] = []
        for chunk in chunks:
            if merged and len(chunk) < self._min_chunk_size:
                merged[-1] = f"{merged[-1]}\n\n{chunk}"
            elif not merged and len(chunk) < self._min_chunk_size:
                merged.append(chunk)
            else:
                if merged and len(merged[-1]) < self._min_chunk_size:
                    merged[-1] = f"{merged[-1]}\n\n{chunk}"
                else:
                    merged.append(chunk)
        return [c for c in merged if c.strip()]

