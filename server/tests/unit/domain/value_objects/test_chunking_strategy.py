import pytest

from raggae.domain.value_objects.chunking_strategy import ChunkingStrategy


class TestChunkingStrategy:
    def test_has_auto_value(self) -> None:
        assert ChunkingStrategy.AUTO == "auto"

    def test_has_fixed_window_value(self) -> None:
        assert ChunkingStrategy.FIXED_WINDOW == "fixed_window"

    def test_has_paragraph_value(self) -> None:
        assert ChunkingStrategy.PARAGRAPH == "paragraph"

    def test_has_heading_section_value(self) -> None:
        assert ChunkingStrategy.HEADING_SECTION == "heading_section"

    def test_has_semantic_value(self) -> None:
        assert ChunkingStrategy.SEMANTIC == "semantic"

    def test_has_tabular_value(self) -> None:
        assert ChunkingStrategy.TABULAR == "tabular"

    def test_can_be_created_from_tabular_string(self) -> None:
        # Ensures legacy documents with processing_strategy='tabular' load without error
        assert ChunkingStrategy("tabular") is ChunkingStrategy.TABULAR

    @pytest.mark.parametrize(
        "value",
        ["auto", "fixed_window", "paragraph", "heading_section", "semantic", "tabular"],
    )
    def test_can_be_created_from_all_valid_strings(self, value: str) -> None:
        assert ChunkingStrategy(value).value == value

    def test_invalid_string_raises_value_error(self) -> None:
        with pytest.raises(ValueError):
            ChunkingStrategy("unknown_strategy")
