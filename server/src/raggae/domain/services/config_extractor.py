from raggae.domain.entities.agent_configuration import AgentConfiguration
from raggae.domain.value_objects.resolved_agent_configuration import ResolvedAgentConfiguration


class ConfigExtractor:
    """Domain service: resolves effective configuration by cascading through the hierarchy.

    Cascade order: project ?? parent (ORGA or USER) ?? app ?? None.
    """

    @staticmethod
    def resolve(
        project: AgentConfiguration,
        parent: AgentConfiguration | None,
        app: AgentConfiguration | None,
    ) -> ResolvedAgentConfiguration:
        def pick(field: str) -> object:
            for cfg in (project, parent, app):
                if cfg is not None:
                    value = getattr(cfg, field)
                    if value is not None:
                        return value
            return None

        return ResolvedAgentConfiguration(
            embedding_backend=pick("embedding_backend"),  # type: ignore[arg-type]
            embedding_model=pick("embedding_model"),  # type: ignore[arg-type]
            embedding_api_key_credential_id=pick("embedding_api_key_credential_id"),  # type: ignore[arg-type]
            llm_backend=pick("llm_backend"),  # type: ignore[arg-type]
            llm_model=pick("llm_model"),  # type: ignore[arg-type]
            llm_api_key_credential_id=pick("llm_api_key_credential_id"),  # type: ignore[arg-type]
            chunking_strategy=pick("chunking_strategy"),  # type: ignore[arg-type]
            parent_child_chunking=pick("parent_child_chunking"),  # type: ignore[arg-type]
            retrieval_strategy=pick("retrieval_strategy"),  # type: ignore[arg-type]
            retrieval_top_k=pick("retrieval_top_k"),  # type: ignore[arg-type]
            retrieval_min_score=pick("retrieval_min_score"),  # type: ignore[arg-type]
            reranking_enabled=pick("reranking_enabled"),  # type: ignore[arg-type]
            reranker_backend=pick("reranker_backend"),  # type: ignore[arg-type]
            reranker_model=pick("reranker_model"),  # type: ignore[arg-type]
            reranker_candidate_multiplier=pick("reranker_candidate_multiplier"),  # type: ignore[arg-type]
            chat_history_window_size=pick("chat_history_window_size"),  # type: ignore[arg-type]
            chat_history_max_chars=pick("chat_history_max_chars"),  # type: ignore[arg-type]
        )
