from dataclasses import FrozenInstanceError
from datetime import UTC, datetime
from uuid import uuid4

import pytest

from raggae.domain.entities.organization_default_config import OrganizationDefaultConfig
from raggae.domain.value_objects.chunking_strategy import ChunkingStrategy


class TestOrganizationDefaultConfig:
    def _make_config(self, **kwargs) -> OrganizationDefaultConfig:  # type: ignore[no-untyped-def]
        defaults = {
            "id": uuid4(),
            "organization_id": uuid4(),
            "embedding_backend": None,
            "llm_backend": None,
            "chunking_strategy": None,
            "retrieval_strategy": None,
            "retrieval_top_k": None,
            "retrieval_min_score": None,
            "reranking_enabled": None,
            "reranker_backend": None,
            "org_embedding_api_key_credential_id": None,
            "org_llm_api_key_credential_id": None,
            "updated_at": datetime.now(UTC),
        }
        defaults.update(kwargs)
        return OrganizationDefaultConfig(**defaults)

    def test_create_minimal_config(self) -> None:
        # Given / When
        config = self._make_config()

        # Then
        assert config.embedding_backend is None
        assert config.llm_backend is None
        assert config.chunking_strategy is None

    def test_create_config_with_all_fields(self) -> None:
        org_id = uuid4()
        emb_cred_id = uuid4()
        llm_cred_id = uuid4()
        now = datetime.now(UTC)

        config = self._make_config(
            organization_id=org_id,
            embedding_backend="openai",
            llm_backend="openai",
            chunking_strategy=ChunkingStrategy.PARAGRAPH,
            retrieval_strategy="hybrid",
            retrieval_top_k=10,
            retrieval_min_score=0.5,
            reranking_enabled=True,
            reranker_backend="cross_encoder",
            org_embedding_api_key_credential_id=emb_cred_id,
            org_llm_api_key_credential_id=llm_cred_id,
            updated_at=now,
        )

        assert config.organization_id == org_id
        assert config.embedding_backend == "openai"
        assert config.llm_backend == "openai"
        assert config.chunking_strategy == ChunkingStrategy.PARAGRAPH
        assert config.retrieval_strategy == "hybrid"
        assert config.retrieval_top_k == 10
        assert config.retrieval_min_score == 0.5
        assert config.reranking_enabled is True
        assert config.reranker_backend == "cross_encoder"
        assert config.org_embedding_api_key_credential_id == emb_cred_id
        assert config.org_llm_api_key_credential_id == llm_cred_id
        assert config.updated_at == now

    def test_config_is_immutable(self) -> None:
        config = self._make_config()

        with pytest.raises(FrozenInstanceError):
            config.embedding_backend = "openai"  # type: ignore[misc]

    def test_update_returns_new_instance_with_changed_fields(self) -> None:
        now = datetime.now(UTC)
        config = self._make_config(embedding_backend=None, llm_backend=None)

        updated = config.update(
            embedding_backend="openai",
            llm_backend="openai",
            chunking_strategy=ChunkingStrategy.FIXED_WINDOW,
            retrieval_strategy="vector",
            retrieval_top_k=5,
            retrieval_min_score=0.2,
            reranking_enabled=False,
            reranker_backend=None,
            org_embedding_api_key_credential_id=None,
            org_llm_api_key_credential_id=None,
            updated_at=now,
        )

        assert updated.embedding_backend == "openai"
        assert updated.llm_backend == "openai"
        assert updated.chunking_strategy == ChunkingStrategy.FIXED_WINDOW
        assert updated.retrieval_strategy == "vector"
        assert updated.retrieval_top_k == 5
        assert updated.updated_at == now
        # original untouched
        assert config.embedding_backend is None

    def test_update_does_not_change_id_or_organization_id(self) -> None:
        config = self._make_config()
        now = datetime.now(UTC)

        updated = config.update(
            embedding_backend="gemini",
            llm_backend=None,
            chunking_strategy=None,
            retrieval_strategy=None,
            retrieval_top_k=None,
            retrieval_min_score=None,
            reranking_enabled=None,
            reranker_backend=None,
            org_embedding_api_key_credential_id=None,
            org_llm_api_key_credential_id=None,
            updated_at=now,
        )

        assert updated.id == config.id
        assert updated.organization_id == config.organization_id
