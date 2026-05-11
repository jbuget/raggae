from dataclasses import FrozenInstanceError
from uuid import uuid4

import pytest

from raggae.domain.entities.agent_configuration import SYSTEM_OWNER_ID, AgentConfiguration
from raggae.domain.value_objects.agent_configuration_type import AgentConfigurationType


def _make(owner_type: AgentConfigurationType = AgentConfigurationType.USER, **kwargs) -> AgentConfiguration:
    return AgentConfiguration(id=uuid4(), owner_id=uuid4(), owner_type=owner_type, **kwargs)


class TestAgentConfiguration:
    def test_all_config_fields_none_by_default(self) -> None:
        cfg = _make()

        assert cfg.embedding_backend is None
        assert cfg.embedding_model is None
        assert cfg.embedding_api_key_credential_id is None
        assert cfg.llm_backend is None
        assert cfg.llm_model is None
        assert cfg.llm_api_key_credential_id is None
        assert cfg.chunking_strategy is None
        assert cfg.parent_child_chunking is None
        assert cfg.retrieval_strategy is None
        assert cfg.retrieval_top_k is None
        assert cfg.retrieval_min_score is None
        assert cfg.reranking_enabled is None
        assert cfg.reranker_backend is None
        assert cfg.reranker_model is None
        assert cfg.reranker_candidate_multiplier is None
        assert cfg.chat_history_window_size is None
        assert cfg.chat_history_max_chars is None

    def test_type_user(self) -> None:
        assert _make(AgentConfigurationType.USER).owner_type == AgentConfigurationType.USER

    def test_type_orga(self) -> None:
        assert _make(AgentConfigurationType.ORGA).owner_type == AgentConfigurationType.ORGA

    def test_type_project(self) -> None:
        assert _make(AgentConfigurationType.PROJECT).owner_type == AgentConfigurationType.PROJECT

    def test_type_app(self) -> None:
        cfg = AgentConfiguration(id=uuid4(), owner_id=SYSTEM_OWNER_ID, owner_type=AgentConfigurationType.APP)
        assert cfg.owner_type == AgentConfigurationType.APP

    def test_system_owner_id_is_sentinel(self) -> None:
        assert str(SYSTEM_OWNER_ID) == "00000000-0000-0000-0000-000000000001"

    def test_config_fields_stored(self) -> None:
        cfg = _make(
            embedding_backend="openai",
            llm_backend="ollama",
            retrieval_top_k=10,
            reranking_enabled=True,
        )
        assert cfg.embedding_backend == "openai"
        assert cfg.llm_backend == "ollama"
        assert cfg.retrieval_top_k == 10
        assert cfg.reranking_enabled is True

    def test_is_immutable(self) -> None:
        cfg = _make()
        with pytest.raises(FrozenInstanceError):
            cfg.embedding_backend = "openai"  # type: ignore[misc]
