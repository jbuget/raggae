import pytest
from raggae.domain.value_objects.chunk_level import ChunkLevel


class TestChunkLevel:
    def test_has_standard_value(self) -> None:
        assert ChunkLevel.STANDARD == "standard"

    def test_has_parent_value(self) -> None:
        assert ChunkLevel.PARENT == "parent"

    def test_has_child_value(self) -> None:
        assert ChunkLevel.CHILD == "child"

    def test_has_exactly_three_members(self) -> None:
        assert len(ChunkLevel) == 3

    def test_can_be_created_from_string(self) -> None:
        assert ChunkLevel("standard") is ChunkLevel.STANDARD

    def test_invalid_string_raises_value_error(self) -> None:
        with pytest.raises(ValueError):
            ChunkLevel("invalid")
