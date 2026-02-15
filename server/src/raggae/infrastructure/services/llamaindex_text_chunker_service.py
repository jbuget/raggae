import importlib
from collections.abc import Callable
from typing import Protocol, cast

from raggae.domain.value_objects.chunking_strategy import ChunkingStrategy


class _TextSplitter(Protocol):
    def split_text(self, text: str) -> list[str]: ...


class LlamaIndexTextChunkerService:
    """Text chunker powered by LlamaIndex with automatic splitter selection."""

    def __init__(
        self,
        chunk_size: int,
        chunk_overlap: int,
        sentence_splitter_factory: Callable[[int, int], _TextSplitter] | None = None,
        token_splitter_factory: Callable[[int, int], _TextSplitter] | None = None,
        code_splitter_factory: Callable[[int, int], _TextSplitter] | None = None,
    ) -> None:
        self._chunk_size = chunk_size
        self._chunk_overlap = chunk_overlap
        self._sentence_splitter_factory = sentence_splitter_factory
        self._token_splitter_factory = token_splitter_factory
        self._code_splitter_factory = code_splitter_factory

    async def chunk_text(
        self,
        text: str,
        strategy: ChunkingStrategy = ChunkingStrategy.FIXED_WINDOW,
    ) -> list[str]:
        del strategy
        normalized = text.strip()
        if not normalized:
            return []

        splitter = self._build_splitter(normalized)
        return [chunk.strip() for chunk in splitter.split_text(normalized) if chunk.strip()]

    def _build_splitter(self, text: str) -> _TextSplitter:
        if self._looks_like_code(text):
            return self._build_code_splitter()
        if self._looks_like_long_unstructured_text(text):
            return self._build_token_splitter()
        return self._build_sentence_splitter()

    def _build_sentence_splitter(self) -> _TextSplitter:
        if self._sentence_splitter_factory is not None:
            return self._sentence_splitter_factory(self._chunk_size, self._chunk_overlap)

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

    def _build_token_splitter(self) -> _TextSplitter:
        if self._token_splitter_factory is not None:
            return self._token_splitter_factory(self._chunk_size, self._chunk_overlap)
        return self._build_sentence_splitter()

    def _build_code_splitter(self) -> _TextSplitter:
        if self._code_splitter_factory is not None:
            return self._code_splitter_factory(self._chunk_size, self._chunk_overlap)
        return self._build_sentence_splitter()

    def _looks_like_code(self, text: str) -> bool:
        if "```" in text:
            return True
        code_markers = ("def ", "class ", "import ", "function ", "{", "}", ";")
        score = sum(1 for marker in code_markers if marker in text)
        return score >= 2

    def _looks_like_long_unstructured_text(self, text: str) -> bool:
        if len(text) < self._chunk_size * 2:
            return False
        punctuation_count = sum(1 for char in text if char in ".!?")
        punctuation_density = punctuation_count / max(1, len(text))
        return punctuation_density < 0.005
