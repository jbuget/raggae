from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from raggae.application.constants import MAX_PROJECT_SYSTEM_PROMPT_LENGTH
from raggae.application.dto.agent_configuration_dto import AgentConfigurationDTO
from raggae.application.dto.project_dto import ProjectDTO


class CreateProjectRequest(BaseModel):
    name: str = Field(..., min_length=1)
    organization_id: UUID | None = None
    description: str = ""
    system_prompt: str = Field(default="", max_length=MAX_PROJECT_SYSTEM_PROMPT_LENGTH)


class UpdateProjectRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1)
    description: str | None = None
    system_prompt: str | None = Field(default=None, max_length=MAX_PROJECT_SYSTEM_PROMPT_LENGTH)


class AgentConfigurationResponse(BaseModel):
    owner_id: UUID
    # Models
    embedding_backend: str | None
    embedding_model: str | None
    embedding_api_key_credential_id: UUID | None
    llm_backend: str | None
    llm_model: str | None
    llm_api_key_credential_id: UUID | None
    # Indexing
    chunking_strategy: str | None
    parent_child_chunking: bool | None
    # Retrieval
    retrieval_strategy: str | None
    retrieval_top_k: int | None
    retrieval_min_score: float | None
    # Reranking
    reranking_enabled: bool | None
    reranker_backend: str | None
    reranker_model: str | None
    reranker_candidate_multiplier: int | None
    # Chat history
    chat_history_window_size: int | None
    chat_history_max_chars: int | None

    @classmethod
    def from_dto(cls, dto: AgentConfigurationDTO) -> "AgentConfigurationResponse":
        return cls(
            owner_id=dto.owner_id,
            embedding_backend=dto.embedding_backend,
            embedding_model=dto.embedding_model,
            embedding_api_key_credential_id=dto.embedding_api_key_credential_id,
            llm_backend=dto.llm_backend,
            llm_model=dto.llm_model,
            llm_api_key_credential_id=dto.llm_api_key_credential_id,
            chunking_strategy=dto.chunking_strategy,
            parent_child_chunking=dto.parent_child_chunking,
            retrieval_strategy=dto.retrieval_strategy,
            retrieval_top_k=dto.retrieval_top_k,
            retrieval_min_score=dto.retrieval_min_score,
            reranking_enabled=dto.reranking_enabled,
            reranker_backend=dto.reranker_backend,
            reranker_model=dto.reranker_model,
            reranker_candidate_multiplier=dto.reranker_candidate_multiplier,
            chat_history_window_size=dto.chat_history_window_size,
            chat_history_max_chars=dto.chat_history_max_chars,
        )


class UpdateAgentConfigurationRequest(BaseModel):
    embedding_backend: str | None = None
    embedding_model: str | None = None
    embedding_api_key_credential_id: UUID | None = None
    llm_backend: str | None = None
    llm_model: str | None = None
    llm_api_key_credential_id: UUID | None = None
    chunking_strategy: str | None = None
    parent_child_chunking: bool | None = None
    retrieval_strategy: str | None = None
    retrieval_top_k: int | None = None
    retrieval_min_score: float | None = None
    reranking_enabled: bool | None = None
    reranker_backend: str | None = None
    reranker_model: str | None = None
    reranker_candidate_multiplier: int | None = None
    chat_history_window_size: int | None = None
    chat_history_max_chars: int | None = None


class ProjectResponse(BaseModel):
    id: UUID
    user_id: UUID
    organization_id: UUID | None
    name: str
    description: str
    system_prompt: str
    is_published: bool
    created_at: datetime
    reindex_status: str
    reindex_progress: int
    reindex_total: int

    @classmethod
    def from_dto(cls, dto: ProjectDTO) -> "ProjectResponse":
        return cls(
            id=dto.id,
            user_id=dto.user_id,
            organization_id=dto.organization_id,
            name=dto.name,
            description=dto.description,
            system_prompt=dto.system_prompt,
            is_published=dto.is_published,
            created_at=dto.created_at,
            reindex_status=dto.reindex_status,
            reindex_progress=dto.reindex_progress,
            reindex_total=dto.reindex_total,
        )


class ReindexProjectResponse(BaseModel):
    project_id: UUID
    total_documents: int
    indexed_documents: int
    failed_documents: int


class OrganizationSectionResponse(BaseModel):
    organization_id: UUID
    organization_name: str
    projects: list[ProjectResponse]
    can_edit: bool


class AccessibleProjectsResponse(BaseModel):
    personal_projects: list[ProjectResponse]
    organization_sections: list[OrganizationSectionResponse]
