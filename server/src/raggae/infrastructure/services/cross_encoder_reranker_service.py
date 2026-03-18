import asyncio
from dataclasses import replace
from typing import Protocol, cast

from raggae.application.dto.retrieved_chunk_dto import RetrievedChunkDTO


class _CrossEncoderModel(Protocol):
    def predict(self, sentences: list[tuple[str, str]]) -> object: ...


class CrossEncoderRerankerService:
    """Reranker using a sentence-transformers CrossEncoder model.

    The model is loaded lazily on first call to avoid startup overhead.
    Inference runs in a thread pool since it is synchronous.
    """

    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2") -> None:
        self._model_name = model_name
        self._model: _CrossEncoderModel | None = None

    def _get_model(self) -> _CrossEncoderModel:
        if self._model is None:
            from sentence_transformers import CrossEncoder

            self._model = cast(_CrossEncoderModel, CrossEncoder(self._model_name))
        return self._model

    def _predict_sync(
        self, query: str, chunks: list[RetrievedChunkDTO], top_k: int
    ) -> list[RetrievedChunkDTO]:
        model = self._get_model()
        pairs = [(query, chunk.content) for chunk in chunks]
        raw_scores = model.predict(pairs)
        scores = [float(score) for score in cast(list[float], raw_scores)]
        scored_chunks = [
            replace(chunk, score=float(score)) for chunk, score in zip(chunks, scores, strict=True)
        ]
        scored_chunks.sort(key=lambda c: c.score, reverse=True)
        return scored_chunks[:top_k]

    async def rerank(
        self,
        query: str,
        chunks: list[RetrievedChunkDTO],
        top_k: int,
        query_embedding: list[float] | None = None,
    ) -> list[RetrievedChunkDTO]:
        if not chunks:
            return []
        return await asyncio.to_thread(self._predict_sync, query, chunks, top_k)
