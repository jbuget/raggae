from enum import StrEnum


class ChunkLevel(StrEnum):
    """Chunk hierarchy level for parent-child chunking."""

    STANDARD = "standard"
    PARENT = "parent"
    CHILD = "child"
