from dataclasses import dataclass
from uuid import UUID

from raggae.domain.value_objects.agent_configuration_type import AgentConfigurationType

SYSTEM_OWNER_ID = UUID("00000000-0000-0000-0000-000000000001")


@dataclass(frozen=True)
class AgentConfiguration:
    """Configuration entry for an agent hierarchy level (APP / USER / ORGA / PROJECT)."""

    id: UUID
    owner_id: UUID
    type: AgentConfigurationType
    # Models
    embedding_backend: str | None = None
    embedding_model: str | None = None
    embedding_api_key_credential_id: UUID | None = None
    llm_backend: str | None = None
    llm_model: str | None = None
    llm_api_key_credential_id: UUID | None = None
    # Indexing
    chunking_strategy: str | None = None
    parent_child_chunking: bool | None = None
    # Retrieval
    retrieval_strategy: str | None = None
    retrieval_top_k: int | None = None
    retrieval_min_score: float | None = None
    # Reranking
    reranking_enabled: bool | None = None
    reranker_backend: str | None = None
    reranker_model: str | None = None
    reranker_candidate_multiplier: int | None = None
    # Chat history
    chat_history_window_size: int | None = None
    chat_history_max_chars: int | None = None
