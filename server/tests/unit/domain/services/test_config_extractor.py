from uuid import uuid4

from raggae.domain.entities.agent_configuration import SYSTEM_OWNER_ID, AgentConfiguration
from raggae.domain.services.config_extractor import ConfigExtractor
from raggae.domain.value_objects.agent_configuration_type import AgentConfigurationType
from raggae.domain.value_objects.resolved_agent_configuration import ResolvedAgentConfiguration


def _project(**kwargs) -> AgentConfiguration:
    return AgentConfiguration(id=uuid4(), owner_id=uuid4(), type=AgentConfigurationType.PROJECT, **kwargs)


def _parent(**kwargs) -> AgentConfiguration:
    return AgentConfiguration(id=uuid4(), owner_id=uuid4(), type=AgentConfigurationType.ORGA, **kwargs)


def _app(**kwargs) -> AgentConfiguration:
    return AgentConfiguration(id=uuid4(), owner_id=SYSTEM_OWNER_ID, type=AgentConfigurationType.APP, **kwargs)


class TestConfigExtractor:
    def test_project_field_wins_over_parent_and_app(self) -> None:
        result = ConfigExtractor.resolve(
            project=_project(llm_backend="project-llm"),
            parent=_parent(llm_backend="parent-llm"),
            app=_app(llm_backend="app-llm"),
        )

        assert result.llm_backend == "project-llm"

    def test_parent_field_used_when_project_is_none(self) -> None:
        result = ConfigExtractor.resolve(
            project=_project(llm_backend=None),
            parent=_parent(llm_backend="parent-llm"),
            app=_app(llm_backend="app-llm"),
        )

        assert result.llm_backend == "parent-llm"

    def test_app_field_used_when_project_and_parent_are_none(self) -> None:
        result = ConfigExtractor.resolve(
            project=_project(retrieval_top_k=None),
            parent=_parent(retrieval_top_k=None),
            app=_app(retrieval_top_k=20),
        )

        assert result.retrieval_top_k == 20

    def test_none_when_all_levels_are_none(self) -> None:
        result = ConfigExtractor.resolve(
            project=_project(),
            parent=_parent(),
            app=_app(),
        )

        assert result.embedding_backend is None
        assert result.llm_backend is None
        assert result.retrieval_top_k is None

    def test_parent_none_falls_through_to_app(self) -> None:
        result = ConfigExtractor.resolve(
            project=_project(embedding_model=None),
            parent=None,
            app=_app(embedding_model="text-embedding-3-small"),
        )

        assert result.embedding_model == "text-embedding-3-small"

    def test_parent_none_project_value_used(self) -> None:
        result = ConfigExtractor.resolve(
            project=_project(embedding_model="custom-model"),
            parent=None,
            app=_app(embedding_model="text-embedding-3-small"),
        )

        assert result.embedding_model == "custom-model"

    def test_app_none_uses_project_value(self) -> None:
        result = ConfigExtractor.resolve(
            project=_project(chunking_strategy="fixed"),
            parent=_parent(),
            app=None,
        )

        assert result.chunking_strategy == "fixed"

    def test_app_none_no_fallback_gives_none(self) -> None:
        result = ConfigExtractor.resolve(
            project=_project(),
            parent=_parent(),
            app=None,
        )

        assert result.chunking_strategy is None

    def test_mixed_fields_resolved_from_different_levels(self) -> None:
        result = ConfigExtractor.resolve(
            project=_project(llm_backend="ollama", llm_model=None),
            parent=_parent(llm_model="mistral", retrieval_top_k=None),
            app=_app(retrieval_top_k=5),
        )

        assert result.llm_backend == "ollama"
        assert result.llm_model == "mistral"
        assert result.retrieval_top_k == 5

    def test_returns_resolved_agent_configuration(self) -> None:
        result = ConfigExtractor.resolve(
            project=_project(),
            parent=None,
            app=None,
        )

        assert isinstance(result, ResolvedAgentConfiguration)

    def test_all_fields_resolved(self) -> None:
        cred_id = uuid4()
        result = ConfigExtractor.resolve(
            project=_project(
                embedding_backend="openai",
                embedding_model="text-embedding-3-small",
                embedding_api_key_credential_id=cred_id,
                llm_backend="openai",
                llm_model="gpt-4o",
                llm_api_key_credential_id=cred_id,
                chunking_strategy="fixed",
                parent_child_chunking=True,
                retrieval_strategy="hybrid",
                retrieval_top_k=10,
                retrieval_min_score=0.5,
                reranking_enabled=True,
                reranker_backend="cross_encoder",
                reranker_model="bge-reranker",
                reranker_candidate_multiplier=3,
                chat_history_window_size=10,
                chat_history_max_chars=4000,
            ),
            parent=None,
            app=None,
        )

        assert result.embedding_backend == "openai"
        assert result.embedding_model == "text-embedding-3-small"
        assert result.embedding_api_key_credential_id == cred_id
        assert result.llm_backend == "openai"
        assert result.llm_model == "gpt-4o"
        assert result.llm_api_key_credential_id == cred_id
        assert result.chunking_strategy == "fixed"
        assert result.parent_child_chunking is True
        assert result.retrieval_strategy == "hybrid"
        assert result.retrieval_top_k == 10
        assert result.retrieval_min_score == 0.5
        assert result.reranking_enabled is True
        assert result.reranker_backend == "cross_encoder"
        assert result.reranker_model == "bge-reranker"
        assert result.reranker_candidate_multiplier == 3
        assert result.chat_history_window_size == 10
        assert result.chat_history_max_chars == 4000
