from unittest.mock import Mock

import pytest

from raggae.infrastructure.services.llamaindex_text_chunker_service import (
    LlamaIndexTextChunkerService,
)


class TestLlamaIndexTextChunkerService:
    async def test_chunk_text_uses_splitter_factory(self) -> None:
        # Given
        splitter = Mock()
        splitter.split_text.return_value = ["alpha", "beta"]
        service = LlamaIndexTextChunkerService(
            chunk_size=100,
            chunk_overlap=10,
            splitter_factory=lambda _size, _overlap: splitter,
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
            splitter_factory=lambda _size, _overlap: Mock(),
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
