import importlib
from collections.abc import Callable
from typing import Protocol, cast

from raggae.domain.value_objects.chunking_strategy import ChunkingStrategy


class _TextSplitter(Protocol):
    def split_text(self, text: str) -> list[str]: ...


class LlamaIndexTextChunkerService:
    """Text chunker powered by LlamaIndex SentenceSplitter."""

    def __init__(
        self,
        chunk_size: int,
        chunk_overlap: int,
        splitter_factory: Callable[[int, int], _TextSplitter] | None = None,
    ) -> None:
        self._chunk_size = chunk_size
        self._chunk_overlap = chunk_overlap
        self._splitter_factory = splitter_factory

    async def chunk_text(
        self,
        text: str,
        strategy: ChunkingStrategy = ChunkingStrategy.FIXED_WINDOW,
    ) -> list[str]:
        del strategy
        normalized = text.strip()
        if not normalized:
            return []

        splitter = self._build_splitter()
        return [chunk.strip() for chunk in splitter.split_text(normalized) if chunk.strip()]

    def _build_splitter(self) -> _TextSplitter:
        if self._splitter_factory is not None:
            return self._splitter_factory(self._chunk_size, self._chunk_overlap)

        try:
            module = importlib.import_module("llama_index.core.node_parser")
        except ModuleNotFoundError as exc:
            raise RuntimeError(
                "llama-index-core is required when TEXT_CHUNKER_BACKEND=llamaindex"
            ) from exc

        sentence_splitter = module.SentenceSplitter
        return cast(
            _TextSplitter,
            sentence_splitter(
                chunk_size=self._chunk_size,
                chunk_overlap=self._chunk_overlap,
            ),
        )
