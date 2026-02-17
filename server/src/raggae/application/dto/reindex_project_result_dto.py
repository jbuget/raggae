from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class ReindexProjectResultDTO:
    """Result payload for project-wide reindex operation."""

    project_id: UUID
    total_documents: int
    indexed_documents: int
    failed_documents: int
