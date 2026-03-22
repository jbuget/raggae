from datetime import UTC, datetime
from uuid import uuid4

import pytest

from raggae.application.use_cases.organization.get_organization_default_config import (
    GetOrganizationDefaultConfig,
)
from raggae.application.use_cases.organization.upsert_organization_default_config import (
    UpsertOrganizationDefaultConfig,
)
from raggae.domain.entities.organization import Organization
from raggae.domain.entities.organization_default_config import OrganizationDefaultConfig
from raggae.domain.entities.organization_member import OrganizationMember
from raggae.domain.exceptions.organization_exceptions import (
    OrganizationAccessDeniedError,
    OrganizationNotFoundError,
)
from raggae.domain.value_objects.chunking_strategy import ChunkingStrategy
from raggae.domain.value_objects.organization_member_role import OrganizationMemberRole
from raggae.infrastructure.database.repositories.in_memory_organization_default_config_repository import (
    InMemoryOrganizationDefaultConfigRepository,
)
from raggae.infrastructure.database.repositories.in_memory_organization_member_repository import (
    InMemoryOrganizationMemberRepository,
)
from raggae.infrastructure.database.repositories.in_memory_organization_repository import (
    InMemoryOrganizationRepository,
)


def _make_org(user_id=None):  # type: ignore[no-untyped-def]
    now = datetime.now(UTC)
    return Organization(
        id=uuid4(),
        name="Acme",
        slug=None,
        description=None,
        logo_url=None,
        created_by_user_id=user_id or uuid4(),
        created_at=now,
        updated_at=now,
    )


def _make_member(org_id, user_id, role=OrganizationMemberRole.OWNER):  # type: ignore[no-untyped-def]
    return OrganizationMember(
        id=uuid4(),
        organization_id=org_id,
        user_id=user_id,
        role=role,
        joined_at=datetime.now(UTC),
    )


class TestGetOrganizationDefaultConfig:
    @pytest.fixture
    def repos(self):  # type: ignore[no-untyped-def]
        return (
            InMemoryOrganizationRepository(),
            InMemoryOrganizationMemberRepository(),
            InMemoryOrganizationDefaultConfigRepository(),
        )

    async def test_returns_none_when_no_config_exists(self, repos) -> None:  # type: ignore[no-untyped-def]
        org_repo, member_repo, config_repo = repos
        user_id = uuid4()
        org = _make_org(user_id)
        await org_repo.save(org)
        await member_repo.save(_make_member(org.id, user_id))
        use_case = GetOrganizationDefaultConfig(org_repo, member_repo, config_repo)

        result = await use_case.execute(organization_id=org.id, user_id=user_id)

        assert result is None

    async def test_returns_config_when_exists(self, repos) -> None:  # type: ignore[no-untyped-def]
        org_repo, member_repo, config_repo = repos
        user_id = uuid4()
        org = _make_org(user_id)
        await org_repo.save(org)
        await member_repo.save(_make_member(org.id, user_id))
        config = OrganizationDefaultConfig(
            id=uuid4(),
            organization_id=org.id,
            embedding_backend="openai",
            llm_backend="openai",
            chunking_strategy=ChunkingStrategy.PARAGRAPH,
            retrieval_strategy="hybrid",
            retrieval_top_k=8,
            retrieval_min_score=0.3,
            reranking_enabled=False,
            reranker_backend=None,
            org_embedding_api_key_credential_id=None,
            org_llm_api_key_credential_id=None,
            updated_at=datetime.now(UTC),
        )
        await config_repo.save(config)
        use_case = GetOrganizationDefaultConfig(org_repo, member_repo, config_repo)

        result = await use_case.execute(organization_id=org.id, user_id=user_id)

        assert result is not None
        assert result.embedding_backend == "openai"
        assert result.organization_id == org.id

    async def test_raises_when_org_not_found(self, repos) -> None:  # type: ignore[no-untyped-def]
        org_repo, member_repo, config_repo = repos
        use_case = GetOrganizationDefaultConfig(org_repo, member_repo, config_repo)

        with pytest.raises(OrganizationNotFoundError):
            await use_case.execute(organization_id=uuid4(), user_id=uuid4())

    async def test_raises_when_user_has_role_user(self, repos) -> None:  # type: ignore[no-untyped-def]
        org_repo, member_repo, config_repo = repos
        user_id = uuid4()
        org = _make_org()
        await org_repo.save(org)
        await member_repo.save(_make_member(org.id, user_id, OrganizationMemberRole.USER))
        use_case = GetOrganizationDefaultConfig(org_repo, member_repo, config_repo)

        with pytest.raises(OrganizationAccessDeniedError):
            await use_case.execute(organization_id=org.id, user_id=user_id)

    async def test_maker_can_access_config(self, repos) -> None:  # type: ignore[no-untyped-def]
        org_repo, member_repo, config_repo = repos
        user_id = uuid4()
        org = _make_org()
        await org_repo.save(org)
        await member_repo.save(_make_member(org.id, user_id, OrganizationMemberRole.MAKER))
        use_case = GetOrganizationDefaultConfig(org_repo, member_repo, config_repo)

        result = await use_case.execute(organization_id=org.id, user_id=user_id)

        assert result is None


class TestUpsertOrganizationDefaultConfig:
    @pytest.fixture
    def repos(self):  # type: ignore[no-untyped-def]
        return (
            InMemoryOrganizationRepository(),
            InMemoryOrganizationMemberRepository(),
            InMemoryOrganizationDefaultConfigRepository(),
        )

    def _use_case(self, repos):  # type: ignore[no-untyped-def]
        org_repo, member_repo, config_repo = repos
        return UpsertOrganizationDefaultConfig(org_repo, member_repo, config_repo), config_repo

    async def test_creates_config_when_none_exists(self, repos) -> None:  # type: ignore[no-untyped-def]
        org_repo, member_repo, config_repo = repos
        user_id = uuid4()
        org = _make_org(user_id)
        await org_repo.save(org)
        await member_repo.save(_make_member(org.id, user_id))
        use_case, _ = self._use_case(repos)

        result = await use_case.execute(
            organization_id=org.id,
            user_id=user_id,
            embedding_backend="openai",
            llm_backend="openai",
            chunking_strategy=ChunkingStrategy.PARAGRAPH,
            retrieval_strategy="hybrid",
            retrieval_top_k=8,
            retrieval_min_score=0.3,
            reranking_enabled=False,
            reranker_backend=None,
            org_embedding_api_key_credential_id=None,
            org_llm_api_key_credential_id=None,
        )

        assert result.embedding_backend == "openai"
        assert result.organization_id == org.id
        assert result.id is not None

    async def test_updates_existing_config(self, repos) -> None:  # type: ignore[no-untyped-def]
        org_repo, member_repo, config_repo = repos
        user_id = uuid4()
        org = _make_org(user_id)
        await org_repo.save(org)
        await member_repo.save(_make_member(org.id, user_id))
        use_case, _ = self._use_case(repos)

        first = await use_case.execute(
            organization_id=org.id,
            user_id=user_id,
            embedding_backend="openai",
            llm_backend=None,
            chunking_strategy=None,
            retrieval_strategy=None,
            retrieval_top_k=None,
            retrieval_min_score=None,
            reranking_enabled=None,
            reranker_backend=None,
            org_embedding_api_key_credential_id=None,
            org_llm_api_key_credential_id=None,
        )
        second = await use_case.execute(
            organization_id=org.id,
            user_id=user_id,
            embedding_backend="gemini",
            llm_backend="gemini",
            chunking_strategy=ChunkingStrategy.FIXED_WINDOW,
            retrieval_strategy="vector",
            retrieval_top_k=5,
            retrieval_min_score=0.2,
            reranking_enabled=True,
            reranker_backend="cross_encoder",
            org_embedding_api_key_credential_id=None,
            org_llm_api_key_credential_id=None,
        )

        assert second.id == first.id
        assert second.embedding_backend == "gemini"
        assert second.chunking_strategy == ChunkingStrategy.FIXED_WINDOW

    async def test_raises_when_org_not_found(self, repos) -> None:  # type: ignore[no-untyped-def]
        use_case, _ = self._use_case(repos)

        with pytest.raises(OrganizationNotFoundError):
            await use_case.execute(
                organization_id=uuid4(),
                user_id=uuid4(),
                embedding_backend=None,
                llm_backend=None,
                chunking_strategy=None,
                retrieval_strategy=None,
                retrieval_top_k=None,
                retrieval_min_score=None,
                reranking_enabled=None,
                reranker_backend=None,
                org_embedding_api_key_credential_id=None,
                org_llm_api_key_credential_id=None,
            )

    async def test_raises_when_user_has_role_user(self, repos) -> None:  # type: ignore[no-untyped-def]
        org_repo, member_repo, _ = repos
        user_id = uuid4()
        org = _make_org()
        await org_repo.save(org)
        await member_repo.save(_make_member(org.id, user_id, OrganizationMemberRole.USER))
        use_case, _ = self._use_case(repos)

        with pytest.raises(OrganizationAccessDeniedError):
            await use_case.execute(
                organization_id=org.id,
                user_id=user_id,
                embedding_backend=None,
                llm_backend=None,
                chunking_strategy=None,
                retrieval_strategy=None,
                retrieval_top_k=None,
                retrieval_min_score=None,
                reranking_enabled=None,
                reranker_backend=None,
                org_embedding_api_key_credential_id=None,
                org_llm_api_key_credential_id=None,
            )

    async def test_maker_can_upsert_config(self, repos) -> None:  # type: ignore[no-untyped-def]
        org_repo, member_repo, _ = repos
        user_id = uuid4()
        org = _make_org()
        await org_repo.save(org)
        await member_repo.save(_make_member(org.id, user_id, OrganizationMemberRole.MAKER))
        use_case, _ = self._use_case(repos)

        result = await use_case.execute(
            organization_id=org.id,
            user_id=user_id,
            embedding_backend="openai",
            llm_backend=None,
            chunking_strategy=None,
            retrieval_strategy=None,
            retrieval_top_k=None,
            retrieval_min_score=None,
            reranking_enabled=None,
            reranker_backend=None,
            org_embedding_api_key_credential_id=None,
            org_llm_api_key_credential_id=None,
        )

        assert result.embedding_backend == "openai"
