from datetime import UTC, datetime
from uuid import uuid4

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from raggae.domain.entities.org_mcp_server import OrgMcpServer
from raggae.domain.entities.organization import Organization
from raggae.domain.value_objects.mcp_auth_type import McpAuthType
from raggae.domain.value_objects.mcp_tool_snapshot import McpToolSnapshot
from raggae.infrastructure.database.models import Base
from raggae.infrastructure.database.repositories.sqlalchemy_org_mcp_server_repository import (
    SQLAlchemyOrgMcpServerRepository,
)
from raggae.infrastructure.database.repositories.sqlalchemy_organization_repository import (
    SQLAlchemyOrganizationRepository,
)


class TestSQLAlchemyOrgMcpServerRepository:
    @pytest.fixture
    async def session_factory(self) -> async_sessionmaker[AsyncSession]:
        engine = create_async_engine(
            "postgresql+asyncpg://test:test@localhost:5433/raggae_test",
            echo=False,
        )
        try:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.drop_all)
                await conn.run_sync(Base.metadata.create_all)
        except Exception as exc:  # pragma: no cover - environment dependent
            pytest.skip(f"PostgreSQL test database is not reachable: {exc}")

        factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        yield factory

        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        await engine.dispose()

    async def _seed_organization(self, session_factory: async_sessionmaker[AsyncSession]) -> Organization:
        now = datetime.now(UTC)
        org = Organization(
            id=uuid4(),
            name="Acme",
            slug="acme",
            description=None,
            logo_url=None,
            created_by_user_id=uuid4(),
            created_at=now,
            updated_at=now,
        )
        await SQLAlchemyOrganizationRepository(session_factory=session_factory).save(org)
        return org

    def _make_server(
        self,
        *,
        organization_id,
        slug: str = "notion",
        name: str = "Notion",
        auth_type: McpAuthType = McpAuthType.NONE,
        tools: list[McpToolSnapshot] | None = None,
    ) -> OrgMcpServer:
        now = datetime.now(UTC)
        return OrgMcpServer(
            id=uuid4(),
            organization_id=organization_id,
            name=name,
            slug=slug,
            url="https://mcp.example.com",
            auth_type=auth_type,
            encrypted_bearer_token="enc" if auth_type == McpAuthType.BEARER else None,
            token_fingerprint="fp" if auth_type == McpAuthType.BEARER else None,
            token_suffix="abcd" if auth_type == McpAuthType.BEARER else None,
            is_active=True,
            tools_snapshot=tools or [],
            tools_snapshot_at=now,
            timeout_seconds=30,
            created_at=now,
            updated_at=now,
            created_by_user_id=uuid4(),
        )

    @pytest.mark.integration
    async def test_integration_save_find_list_and_delete(
        self,
        session_factory: async_sessionmaker[AsyncSession],
    ) -> None:
        # Given
        org = await self._seed_organization(session_factory)
        repo = SQLAlchemyOrgMcpServerRepository(session_factory=session_factory)
        tools = [McpToolSnapshot(name="search", description="Search docs", input_schema={"type": "object"})]
        server = self._make_server(organization_id=org.id, tools=tools)

        # When
        await repo.save(server)
        found_by_id = await repo.find_by_id(server.id, org.id)
        found_by_slug = await repo.find_by_slug(org.id, "notion")
        listed = await repo.list_by_org_id(org.id)
        await repo.delete(server.id, org.id)
        after_delete = await repo.list_by_org_id(org.id)

        # Then
        assert found_by_id is not None
        assert found_by_id.name == "Notion"
        assert found_by_id.tools_snapshot[0].name == "search"
        assert found_by_slug is not None and found_by_slug.id == server.id
        assert len(listed) == 1
        assert after_delete == []

    @pytest.mark.integration
    async def test_integration_save_upserts_existing_server(
        self,
        session_factory: async_sessionmaker[AsyncSession],
    ) -> None:
        # Given
        org = await self._seed_organization(session_factory)
        repo = SQLAlchemyOrgMcpServerRepository(session_factory=session_factory)
        server = self._make_server(organization_id=org.id)
        await repo.save(server)

        # When — modify and save again
        updated_server = server.with_updated_settings(
            name="Notion v2",
            url="https://new.example.com",
            timeout_seconds=15,
            updated_at=datetime.now(UTC),
        ).deactivate()
        await repo.save(updated_server)

        # Then
        reloaded = await repo.find_by_id(server.id, org.id)
        assert reloaded is not None
        assert reloaded.name == "Notion v2"
        assert reloaded.url == "https://new.example.com"
        assert reloaded.timeout_seconds == 15
        assert reloaded.is_active is False

    @pytest.mark.integration
    async def test_integration_unique_constraint_on_org_slug(
        self,
        session_factory: async_sessionmaker[AsyncSession],
    ) -> None:
        # Given
        org = await self._seed_organization(session_factory)
        repo = SQLAlchemyOrgMcpServerRepository(session_factory=session_factory)
        first = self._make_server(organization_id=org.id, slug="duplicate")
        second = self._make_server(organization_id=org.id, slug="duplicate")
        await repo.save(first)

        # When / Then
        with pytest.raises(IntegrityError):
            await repo.save(second)

    @pytest.mark.integration
    async def test_integration_find_by_id_scoped_to_org(
        self,
        session_factory: async_sessionmaker[AsyncSession],
    ) -> None:
        # Given
        org_a = await self._seed_organization(session_factory)
        repo = SQLAlchemyOrgMcpServerRepository(session_factory=session_factory)
        server = self._make_server(organization_id=org_a.id)
        await repo.save(server)

        # When / Then — looking up with a different org id must return None
        other_org_id = uuid4()
        assert await repo.find_by_id(server.id, other_org_id) is None
