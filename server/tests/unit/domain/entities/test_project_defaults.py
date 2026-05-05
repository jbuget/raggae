from dataclasses import FrozenInstanceError
from uuid import uuid4

import pytest

from raggae.domain.entities.project_defaults import ProjectDefaults
from raggae.domain.value_objects.project_defaults_owner_type import ProjectDefaultsOwnerType


def _make_user_defaults(**kwargs) -> ProjectDefaults:
    return ProjectDefaults(owner_id=uuid4(), owner_type=ProjectDefaultsOwnerType.USER, **kwargs)


def _make_org_defaults(**kwargs) -> ProjectDefaults:
    return ProjectDefaults(owner_id=uuid4(), owner_type=ProjectDefaultsOwnerType.ORGA, **kwargs)


class TestProjectDefaults:
    def test_all_fields_none_by_default(self) -> None:
        defaults = _make_user_defaults()

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

    def test_owner_type_user(self) -> None:
        defaults = _make_user_defaults()
        assert defaults.owner_type == ProjectDefaultsOwnerType.USER

    def test_owner_type_orga(self) -> None:
        defaults = _make_org_defaults()
        assert defaults.owner_type == ProjectDefaultsOwnerType.ORGA

    def test_has_models_defaults_when_embedding_backend_set(self) -> None:
        defaults = _make_user_defaults(embedding_backend="openai")
        assert defaults.has_models_defaults() is True

    def test_has_models_defaults_false_when_all_none(self) -> None:
        assert _make_user_defaults().has_models_defaults() is False

    def test_has_indexing_defaults_when_chunking_strategy_set(self) -> None:
        assert _make_user_defaults(chunking_strategy="fixed").has_indexing_defaults() is True

    def test_has_indexing_defaults_false_when_all_none(self) -> None:
        assert _make_user_defaults().has_indexing_defaults() is False

    def test_has_retrieval_defaults_when_strategy_set(self) -> None:
        assert _make_user_defaults(retrieval_strategy="vector").has_retrieval_defaults() is True

    def test_has_retrieval_defaults_false_when_all_none(self) -> None:
        assert _make_user_defaults().has_retrieval_defaults() is False

    def test_has_reranking_defaults_when_enabled_set(self) -> None:
        assert _make_user_defaults(reranking_enabled=True).has_reranking_defaults() is True

    def test_has_reranking_defaults_false_when_all_none(self) -> None:
        assert _make_user_defaults().has_reranking_defaults() is False

    def test_has_chat_history_defaults_when_window_size_set(self) -> None:
        assert _make_user_defaults(chat_history_window_size=5).has_chat_history_defaults() is True

    def test_has_chat_history_defaults_false_when_all_none(self) -> None:
        assert _make_user_defaults().has_chat_history_defaults() is False

    def test_is_immutable(self) -> None:
        defaults = _make_user_defaults()
        with pytest.raises(FrozenInstanceError):
            defaults.embedding_backend = "openai"  # type: ignore[misc]

    def test_org_defaults_has_models_defaults(self) -> None:
        defaults = _make_org_defaults(llm_backend="anthropic")
        assert defaults.has_models_defaults() is True
