import re
from math import sqrt

from raggae.application.interfaces.services.embedding_service import EmbeddingService
from raggae.domain.value_objects.chunking_strategy import ChunkingStrategy

_SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+|\n+")


class SemanticTextChunkerService:
    """Chunk text around semantic breaks inferred from sentence embeddings."""

    def __init__(
        self,
        embedding_service: EmbeddingService,
        chunk_size: int,
        chunk_overlap: int,
        similarity_threshold: float = 0.65,
    ) -> None:
        self._embedding_service = embedding_service
        self._chunk_size = max(1, chunk_size)
        self._chunk_overlap = max(0, min(chunk_overlap, self._chunk_size - 1))
        self._similarity_threshold = min(max(similarity_threshold, 0.0), 1.0)

    async def chunk_text(
        self,
        text: str,
        strategy: ChunkingStrategy = ChunkingStrategy.SEMANTIC,
        embedding_service: EmbeddingService | None = None,
    ) -> list[str]:
        del strategy
        effective_embedding_service = embedding_service or self._embedding_service
        normalized = text.strip()
        if not normalized:
            return []

        sentences = [part.strip() for part in _SENTENCE_SPLIT_RE.split(normalized) if part.strip()]
        if not sentences:
            return []
        if len(sentences) == 1:
            return self._split_large_chunk(sentences[0])

        embeddings = await effective_embedding_service.embed_texts(sentences)

        chunks: list[str] = []
        current_sentences: list[str] = []
        current_len = 0
        for index, sentence in enumerate(sentences):
            sentence_len = len(sentence)
            if current_sentences and current_len + 1 + sentence_len > self._chunk_size:
                chunks.extend(self._split_large_chunk(" ".join(current_sentences)))
                current_sentences = []
                current_len = 0

            if current_sentences:
                prev_embedding = embeddings[index - 1]
                curr_embedding = embeddings[index]
                similarity = _cosine_similarity(prev_embedding, curr_embedding)
                if similarity < self._similarity_threshold:
                    chunks.extend(self._split_large_chunk(" ".join(current_sentences)))
                    current_sentences = []
                    current_len = 0

            current_sentences.append(sentence)
            current_len = sentence_len if current_len == 0 else current_len + 1 + sentence_len

        if current_sentences:
            chunks.extend(self._split_large_chunk(" ".join(current_sentences)))

        return [chunk for chunk in chunks if chunk.strip()]

    def _split_large_chunk(self, chunk: str) -> list[str]:
        normalized = chunk.strip()
        if len(normalized) <= self._chunk_size:
            return [normalized] if normalized else []

        parts: list[str] = []
        start = 0
        while start < len(normalized):
            end = min(start + self._chunk_size, len(normalized))
            piece = normalized[start:end].strip()
            if piece:
                parts.append(piece)
            if end == len(normalized):
                break
            start = max(0, end - self._chunk_overlap)
            if start == end:
                break
        return parts


def _cosine_similarity(left: list[float], right: list[float]) -> float:
    if not left or not right or len(left) != len(right):
        return 0.0
    dot = sum(a * b for a, b in zip(left, right, strict=False))
    left_norm = sqrt(sum(value * value for value in left))
    right_norm = sqrt(sum(value * value for value in right))
    if left_norm == 0.0 or right_norm == 0.0:
        return 0.0
    return dot / (left_norm * right_norm)
