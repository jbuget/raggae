from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class OrganizationProjectDefaults:
    """Default advanced settings for projects created within an organization."""

    organization_id: UUID
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

    def has_models_defaults(self) -> bool:
        return any(
            f is not None
            for f in [
                self.embedding_backend,
                self.embedding_model,
                self.embedding_api_key_credential_id,
                self.llm_backend,
                self.llm_model,
                self.llm_api_key_credential_id,
            ]
        )

    def has_indexing_defaults(self) -> bool:
        return any(f is not None for f in [self.chunking_strategy, self.parent_child_chunking])

    def has_retrieval_defaults(self) -> bool:
        return any(
            f is not None for f in [self.retrieval_strategy, self.retrieval_top_k, self.retrieval_min_score]
        )

    def has_reranking_defaults(self) -> bool:
        return any(
            f is not None
            for f in [
                self.reranking_enabled,
                self.reranker_backend,
                self.reranker_model,
                self.reranker_candidate_multiplier,
            ]
        )

    def has_chat_history_defaults(self) -> bool:
        return any(f is not None for f in [self.chat_history_window_size, self.chat_history_max_chars])
