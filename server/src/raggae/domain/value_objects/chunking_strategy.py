from enum import StrEnum


class ChunkingStrategy(StrEnum):
    """Supported chunking strategies."""

    AUTO = "auto"
    FIXED_WINDOW = "fixed_window"
    PARAGRAPH = "paragraph"
    HEADING_SECTION = "heading_section"
    SEMANTIC = "semantic"
