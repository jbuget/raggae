from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from raggae.domain.value_objects.chunking_strategy import ChunkingStrategy


class CreateProjectRequest(BaseModel):
    name: str = Field(..., min_length=1)
    description: str = ""
    system_prompt: str = ""


class UpdateProjectRequest(BaseModel):
    name: str = Field(..., min_length=1)
    description: str = ""
    system_prompt: str = ""
    chunking_strategy: ChunkingStrategy | None = None
    parent_child_chunking: bool | None = None


class ProjectResponse(BaseModel):
    id: UUID
    user_id: UUID
    name: str
    description: str
    system_prompt: str
    is_published: bool
    created_at: datetime
    chunking_strategy: ChunkingStrategy
    parent_child_chunking: bool
    reindex_status: str
    reindex_progress: int
    reindex_total: int
