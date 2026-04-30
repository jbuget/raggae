from uuid import uuid4

from raggae.domain.entities.user_project_defaults import UserProjectDefaults


class TestUserProjectDefaults:
    def test_all_defaults_are_none(self) -> None:
        defaults = UserProjectDefaults(user_id=uuid4())

        assert defaults.embedding_backend is None
        assert defaults.embedding_model is None
        assert defaults.embedding_api_key_credential_id is None
        assert defaults.llm_backend is None
        assert defaults.llm_model is None
        assert defaults.llm_api_key_credential_id is None
        assert defaults.chunking_strategy is None
        assert defaults.parent_child_chunking is None
        assert defaults.retrieval_strategy is None
        assert defaults.retrieval_top_k is None
        assert defaults.retrieval_min_score is None
        assert defaults.reranking_enabled is None
        assert defaults.reranker_backend is None
        assert defaults.reranker_model is None
        assert defaults.reranker_candidate_multiplier is None
        assert defaults.chat_history_window_size is None
        assert defaults.chat_history_max_chars is None

    def test_has_models_defaults_when_embedding_backend_set(self) -> None:
        defaults = UserProjectDefaults(user_id=uuid4(), embedding_backend="openai")
        assert defaults.has_models_defaults() is True

    def test_has_models_defaults_false_when_all_none(self) -> None:
        defaults = UserProjectDefaults(user_id=uuid4())
        assert defaults.has_models_defaults() is False

    def test_has_indexing_defaults_when_chunking_strategy_set(self) -> None:
        defaults = UserProjectDefaults(user_id=uuid4(), chunking_strategy="fixed")
        assert defaults.has_indexing_defaults() is True

    def test_has_indexing_defaults_false_when_all_none(self) -> None:
        defaults = UserProjectDefaults(user_id=uuid4())
        assert defaults.has_indexing_defaults() is False

    def test_has_retrieval_defaults_when_strategy_set(self) -> None:
        defaults = UserProjectDefaults(user_id=uuid4(), retrieval_strategy="vector")
        assert defaults.has_retrieval_defaults() is True

    def test_has_retrieval_defaults_false_when_all_none(self) -> None:
        defaults = UserProjectDefaults(user_id=uuid4())
        assert defaults.has_retrieval_defaults() is False

    def test_has_reranking_defaults_when_enabled_set(self) -> None:
        defaults = UserProjectDefaults(user_id=uuid4(), reranking_enabled=True)
        assert defaults.has_reranking_defaults() is True

    def test_has_reranking_defaults_false_when_all_none(self) -> None:
        defaults = UserProjectDefaults(user_id=uuid4())
        assert defaults.has_reranking_defaults() is False

    def test_has_chat_history_defaults_when_window_size_set(self) -> None:
        defaults = UserProjectDefaults(user_id=uuid4(), chat_history_window_size=5)
        assert defaults.has_chat_history_defaults() is True

    def test_has_chat_history_defaults_false_when_all_none(self) -> None:
        defaults = UserProjectDefaults(user_id=uuid4())
        assert defaults.has_chat_history_defaults() is False

    def test_is_immutable(self) -> None:
        from dataclasses import FrozenInstanceError

        import pytest

        defaults = UserProjectDefaults(user_id=uuid4())
        with pytest.raises(FrozenInstanceError):
            defaults.embedding_backend = "openai"  # type: ignore[misc]
