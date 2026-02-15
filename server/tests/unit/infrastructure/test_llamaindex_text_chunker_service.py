from unittest.mock import Mock

import pytest

from raggae.infrastructure.services.llamaindex_text_chunker_service import (
    LlamaIndexTextChunkerService,
)


class TestLlamaIndexTextChunkerService:
    async def test_chunk_text_uses_sentence_splitter_for_default_text(self) -> None:
        # Given
        splitter = Mock()
        splitter.split_text.return_value = ["alpha", "beta"]
        service = LlamaIndexTextChunkerService(
            chunk_size=100,
            chunk_overlap=10,
            sentence_splitter_factory=lambda _size, _overlap: splitter,
        )

        # When
        chunks = await service.chunk_text("alpha beta")

        # Then
        assert chunks == ["alpha", "beta"]
        splitter.split_text.assert_called_once_with("alpha beta")

    async def test_chunk_text_empty_text_returns_empty_list(self) -> None:
        # Given
        service = LlamaIndexTextChunkerService(
            chunk_size=100,
            chunk_overlap=10,
            sentence_splitter_factory=lambda _size, _overlap: Mock(),
        )

        # When
        chunks = await service.chunk_text("   ")

        # Then
        assert chunks == []

    async def test_chunk_text_without_llamaindex_dependency_raises_runtime_error(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        # Given
        service = LlamaIndexTextChunkerService(chunk_size=100, chunk_overlap=10)

        def raise_module_not_found(_name: str) -> None:
            raise ModuleNotFoundError

        monkeypatch.setattr(
            "raggae.infrastructure.services.llamaindex_text_chunker_service.importlib.import_module",
            raise_module_not_found,
        )

        # When / Then
        with pytest.raises(RuntimeError):
            await service.chunk_text("content")

    async def test_chunk_text_uses_code_splitter_when_code_detected(self) -> None:
        # Given
        sentence_splitter = Mock()
        code_splitter = Mock()
        code_splitter.split_text.return_value = ["code chunk"]
        service = LlamaIndexTextChunkerService(
            chunk_size=100,
            chunk_overlap=10,
            sentence_splitter_factory=lambda _size, _overlap: sentence_splitter,
            code_splitter_factory=lambda _size, _overlap: code_splitter,
        )

        # When
        chunks = await service.chunk_text("```python\ndef foo():\n    return 1\n```")

        # Then
        assert chunks == ["code chunk"]
        code_splitter.split_text.assert_called_once()
        sentence_splitter.split_text.assert_not_called()

    async def test_chunk_text_uses_token_splitter_for_long_unstructured_text(self) -> None:
        # Given
        sentence_splitter = Mock()
        token_splitter = Mock()
        token_splitter.split_text.return_value = ["token chunk"]
        service = LlamaIndexTextChunkerService(
            chunk_size=50,
            chunk_overlap=10,
            sentence_splitter_factory=lambda _size, _overlap: sentence_splitter,
            token_splitter_factory=lambda _size, _overlap: token_splitter,
        )
        text = "word " * 140

        # When
        chunks = await service.chunk_text(text)

        # Then
        assert chunks == ["token chunk"]
        token_splitter.split_text.assert_called_once()
        sentence_splitter.split_text.assert_not_called()
