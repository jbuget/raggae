from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field

from raggae.application.constants import (
    MAX_PROJECT_RETRIEVAL_TOP_K,
    MAX_PROJECT_SYSTEM_PROMPT_LENGTH,
    MIN_PROJECT_RETRIEVAL_TOP_K,
)
from raggae.domain.value_objects.chunking_strategy import ChunkingStrategy


class CreateProjectRequest(BaseModel):
    name: str = Field(..., min_length=1)
    description: str = ""
    system_prompt: str = Field(default="", max_length=MAX_PROJECT_SYSTEM_PROMPT_LENGTH)
    chunking_strategy: ChunkingStrategy | None = None
    parent_child_chunking: bool | None = None
    embedding_backend: str | None = None
    embedding_model: str | None = None
    embedding_api_key: str | None = None
    embedding_api_key_credential_id: UUID | None = None
    llm_backend: str | None = None
    llm_model: str | None = None
    llm_api_key: str | None = None
    llm_api_key_credential_id: UUID | None = None
    retrieval_strategy: Literal["vector", "fulltext", "hybrid"] | None = None
    retrieval_top_k: int | None = Field(
        default=None,
        ge=MIN_PROJECT_RETRIEVAL_TOP_K,
        le=MAX_PROJECT_RETRIEVAL_TOP_K,
    )


class UpdateProjectRequest(BaseModel):
    name: str = Field(..., min_length=1)
    description: str = ""
    system_prompt: str = Field(default="", max_length=MAX_PROJECT_SYSTEM_PROMPT_LENGTH)
    chunking_strategy: ChunkingStrategy | None = None
    parent_child_chunking: bool | None = None
    embedding_backend: str | None = None
    embedding_model: str | None = None
    embedding_api_key: str | None = None
    embedding_api_key_credential_id: UUID | None = None
    llm_backend: str | None = None
    llm_model: str | None = None
    llm_api_key: str | None = None
    llm_api_key_credential_id: UUID | None = None
    retrieval_strategy: Literal["vector", "fulltext", "hybrid"] | None = None
    retrieval_top_k: int | None = Field(
        default=None,
        ge=MIN_PROJECT_RETRIEVAL_TOP_K,
        le=MAX_PROJECT_RETRIEVAL_TOP_K,
    )


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
    embedding_backend: str | None
    embedding_model: str | None
    embedding_api_key_masked: str | None
    embedding_api_key_credential_id: UUID | None
    llm_backend: str | None
    llm_model: str | None
    llm_api_key_masked: str | None
    llm_api_key_credential_id: UUID | None
    retrieval_strategy: Literal["vector", "fulltext", "hybrid"]
    retrieval_top_k: int


class ReindexProjectResponse(BaseModel):
    project_id: UUID
    total_documents: int
    indexed_documents: int
    failed_documents: int
