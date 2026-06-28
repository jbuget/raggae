from datetime import UTC, datetime
from uuid import UUID, uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from raggae.domain.entities.org_mcp_server import OrgMcpServer
from raggae.domain.entities.organization import Organization
from raggae.domain.entities.project import Project
from raggae.domain.entities.project_mcp_activation import ProjectMcpActivation
from raggae.domain.entities.user import User
from raggae.domain.value_objects.mcp_auth_type import McpAuthType
from raggae.infrastructure.database.models import Base
from raggae.infrastructure.database.repositories.sqlalchemy_org_mcp_server_repository import (
    SQLAlchemyOrgMcpServerRepository,
)
from raggae.infrastructure.database.repositories.sqlalchemy_organization_repository import (
    SQLAlchemyOrganizationRepository,
)
from raggae.infrastructure.database.repositories.sqlalchemy_project_mcp_activation_repository import (
    SQLAlchemyProjectMcpActivationRepository,
)
from raggae.infrastructure.database.repositories.sqlalchemy_project_repository import (
    SQLAlchemyProjectRepository,
)
from raggae.infrastructure.database.repositories.sqlalchemy_user_repository import (
    SQLAlchemyUserRepository,
)


class TestSQLAlchemyProjectMcpActivationRepository:
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
        except Exception as exc:  # pragma: no cover
            pytest.skip(f"PostgreSQL test database is not reachable: {exc}")

        factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        yield factory

        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        await engine.dispose()

    async def _seed_user_org_project_and_server(
        self,
        session_factory: async_sessionmaker[AsyncSession],
    ) -> tuple[UUID, UUID, UUID, UUID]:
        now = datetime.now(UTC)
        user_id = uuid4()
        await SQLAlchemyUserRepository(session_factory=session_factory).save(
            User(
                id=user_id,
                email="mcp-activation@example.com",
                hashed_password="hashed",
                full_name="MCP User",
                is_active=True,
                created_at=now,
            )
        )
        org = Organization(
            id=uuid4(),
            name="Acme",
            slug="acme",
            description=None,
            logo_url=None,
            created_by_user_id=user_id,
            created_at=now,
            updated_at=now,
        )
        await SQLAlchemyOrganizationRepository(session_factory=session_factory).save(org)

        project = Project(
            id=uuid4(),
            user_id=user_id,
            name="P",
            description="",
            system_prompt="",
            is_published=False,
            created_at=now,
            organization_id=org.id,
        )
        await SQLAlchemyProjectRepository(session_factory=session_factory).save(project)

        server = OrgMcpServer(
            id=uuid4(),
            organization_id=org.id,
            name="Notion",
            slug="notion",
            url="https://mcp.example.com",
            auth_type=McpAuthType.NONE,
            encrypted_bearer_token=None,
            token_fingerprint=None,
            token_suffix=None,
            is_active=True,
            tools_snapshot=[],
            tools_snapshot_at=now,
            timeout_seconds=30,
            created_at=now,
            updated_at=now,
            created_by_user_id=user_id,
        )
        await SQLAlchemyOrgMcpServerRepository(session_factory=session_factory).save(server)
        return user_id, org.id, project.id, server.id

    @pytest.mark.integration
    async def test_integration_save_find_list_and_delete(
        self,
        session_factory: async_sessionmaker[AsyncSession],
    ) -> None:
        # Given
        user_id, _org_id, project_id, server_id = await self._seed_user_org_project_and_server(
            session_factory
        )
        repo = SQLAlchemyProjectMcpActivationRepository(session_factory=session_factory)
        activation = ProjectMcpActivation(
            project_id=project_id,
            org_mcp_server_id=server_id,
            is_active=True,
            activated_at=datetime.now(UTC),
            activated_by_user_id=user_id,
        )

        # When
        await repo.save(activation)
        found = await repo.find(project_id, server_id)
        by_project = await repo.list_by_project_id(project_id)
        by_server = await repo.list_by_org_mcp_server_id(server_id)
        await repo.delete(project_id, server_id)
        after = await repo.find(project_id, server_id)

        # Then
        assert found is not None and found.is_active is True
        assert len(by_project) == 1
        assert len(by_server) == 1
        assert after is None

    @pytest.mark.integration
    async def test_integration_save_upserts_existing_activation(
        self,
        session_factory: async_sessionmaker[AsyncSession],
    ) -> None:
        # Given
        user_id, _, project_id, server_id = await self._seed_user_org_project_and_server(session_factory)
        repo = SQLAlchemyProjectMcpActivationRepository(session_factory=session_factory)
        await repo.save(
            ProjectMcpActivation(
                project_id=project_id,
                org_mcp_server_id=server_id,
                is_active=True,
                activated_at=datetime.now(UTC),
                activated_by_user_id=user_id,
            )
        )

        # When
        await repo.save(
            ProjectMcpActivation(
                project_id=project_id,
                org_mcp_server_id=server_id,
                is_active=False,
                activated_at=datetime.now(UTC),
                activated_by_user_id=user_id,
            )
        )

        # Then
        reloaded = await repo.find(project_id, server_id)
        assert reloaded is not None
        assert reloaded.is_active is False

    @pytest.mark.integration
    async def test_integration_delete_by_server_id_cascades(
        self,
        session_factory: async_sessionmaker[AsyncSession],
    ) -> None:
        # Given
        user_id, _, project_id, server_id = await self._seed_user_org_project_and_server(session_factory)
        repo = SQLAlchemyProjectMcpActivationRepository(session_factory=session_factory)
        await repo.save(
            ProjectMcpActivation(
                project_id=project_id,
                org_mcp_server_id=server_id,
                is_active=True,
                activated_at=datetime.now(UTC),
                activated_by_user_id=user_id,
            )
        )

        # When
        await repo.delete_by_org_mcp_server_id(server_id)

        # Then
        assert await repo.list_by_org_mcp_server_id(server_id) == []

    @pytest.mark.integration
    async def test_integration_fk_cascade_on_server_delete(
        self,
        session_factory: async_sessionmaker[AsyncSession],
    ) -> None:
        # Given
        user_id, org_id, project_id, server_id = await self._seed_user_org_project_and_server(session_factory)
        activation_repo = SQLAlchemyProjectMcpActivationRepository(session_factory=session_factory)
        server_repo = SQLAlchemyOrgMcpServerRepository(session_factory=session_factory)
        await activation_repo.save(
            ProjectMcpActivation(
                project_id=project_id,
                org_mcp_server_id=server_id,
                is_active=True,
                activated_at=datetime.now(UTC),
                activated_by_user_id=user_id,
            )
        )

        # When — supprimer le serveur déclenche le ON DELETE CASCADE en base
        await server_repo.delete(server_id, org_id)

        # Then
        assert await activation_repo.find(project_id, server_id) is None
