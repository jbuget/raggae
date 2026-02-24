from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest
from raggae.domain.entities.organization import Organization
from raggae.domain.entities.organization_invitation import OrganizationInvitation
from raggae.domain.entities.organization_member import OrganizationMember
from raggae.domain.value_objects.organization_invitation_status import (
    OrganizationInvitationStatus,
)
from raggae.domain.value_objects.organization_member_role import OrganizationMemberRole
from raggae.infrastructure.database.models import Base
from raggae.infrastructure.database.models.user_model import UserModel
from raggae.infrastructure.database.repositories.sqlalchemy_organization_invitation_repository import (
    SQLAlchemyOrganizationInvitationRepository,
)
from raggae.infrastructure.database.repositories.sqlalchemy_organization_member_repository import (
    SQLAlchemyOrganizationMemberRepository,
)
from raggae.infrastructure.database.repositories.sqlalchemy_organization_repository import (
    SQLAlchemyOrganizationRepository,
)
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine


class TestSQLAlchemyOrganizationRepositories:
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

    async def _create_user(self, session_factory: async_sessionmaker[AsyncSession], email: str):
        user_id = uuid4()
        async with session_factory() as session:
            session.add(
                UserModel(
                    id=user_id,
                    email=email,
                    hashed_password="hashed",
                    full_name="User",
                    is_active=True,
                    created_at=datetime.now(UTC),
                )
            )
            await session.commit()
        return user_id

    @pytest.mark.integration
    async def test_integration_organization_repository(
        self, session_factory: async_sessionmaker[AsyncSession]
    ) -> None:
        user_id = await self._create_user(session_factory, "owner@example.com")
        repo = SQLAlchemyOrganizationRepository(session_factory=session_factory)
        now = datetime.now(UTC)
        org = Organization(
            id=uuid4(),
            name="Org",
            description="desc",
            logo_url=None,
            created_by_user_id=user_id,
            created_at=now,
            updated_at=now,
        )

        await repo.save(org)
        found = await repo.find_by_id(org.id)
        user_orgs = await repo.find_by_user_id(user_id)

        assert found is not None
        assert found.name == "Org"
        assert len(user_orgs) == 1

    @pytest.mark.integration
    async def test_integration_member_and_invitation_repositories(
        self, session_factory: async_sessionmaker[AsyncSession]
    ) -> None:
        owner_user_id = await self._create_user(session_factory, "owner2@example.com")
        invited_user_id = await self._create_user(session_factory, "member@example.com")
        org_repo = SQLAlchemyOrganizationRepository(session_factory=session_factory)
        member_repo = SQLAlchemyOrganizationMemberRepository(session_factory=session_factory)
        invitation_repo = SQLAlchemyOrganizationInvitationRepository(session_factory=session_factory)
        now = datetime.now(UTC)

        organization = Organization(
            id=uuid4(),
            name="Org 2",
            description=None,
            logo_url=None,
            created_by_user_id=owner_user_id,
            created_at=now,
            updated_at=now,
        )
        await org_repo.save(organization)

        member = OrganizationMember(
            id=uuid4(),
            organization_id=organization.id,
            user_id=invited_user_id,
            role=OrganizationMemberRole.MAKER,
            joined_at=now,
        )
        await member_repo.save(member)

        invitation = OrganizationInvitation(
            id=uuid4(),
            organization_id=organization.id,
            email="invitee@example.com",
            role=OrganizationMemberRole.USER,
            status=OrganizationInvitationStatus.PENDING,
            invited_by_user_id=owner_user_id,
            token_hash="hash-1",
            expires_at=now + timedelta(days=7),
            created_at=now,
            updated_at=now,
        )
        await invitation_repo.save(invitation)

        found_member = await member_repo.find_by_organization_and_user(
            organization.id, invited_user_id
        )
        found_pending = await invitation_repo.find_pending_by_organization_and_email(
            organization.id, "invitee@example.com"
        )
        found_by_token = await invitation_repo.find_by_token_hash("hash-1")
        org_members = await member_repo.find_by_organization_id(organization.id)
        org_invitations = await invitation_repo.find_by_organization_id(organization.id)

        assert found_member is not None
        assert found_member.role == OrganizationMemberRole.MAKER
        assert found_pending is not None
        assert found_by_token is not None
        assert len(org_members) == 1
        assert len(org_invitations) == 1
