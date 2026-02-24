from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from raggae.domain.entities.organization_member import OrganizationMember
from raggae.domain.value_objects.organization_member_role import OrganizationMemberRole
from raggae.infrastructure.database.models.organization_member_model import OrganizationMemberModel


class SQLAlchemyOrganizationMemberRepository:
    """PostgreSQL organization member repository using SQLAlchemy async sessions."""

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory

    async def save(self, member: OrganizationMember) -> None:
        async with self._session_factory() as session:
            model = await session.get(OrganizationMemberModel, member.id)
            if model is None:
                model = OrganizationMemberModel(
                    id=member.id,
                    organization_id=member.organization_id,
                    user_id=member.user_id,
                    role=member.role.value,
                    joined_at=member.joined_at,
                )
                session.add(model)
            else:
                model.role = member.role.value
            await session.commit()

    async def find_by_id(self, member_id: UUID) -> OrganizationMember | None:
        async with self._session_factory() as session:
            model = await session.get(OrganizationMemberModel, member_id)
            if model is None:
                return None
            return self._to_entity(model)

    async def find_by_organization_id(self, organization_id: UUID) -> list[OrganizationMember]:
        async with self._session_factory() as session:
            result = await session.execute(
                select(OrganizationMemberModel).where(
                    OrganizationMemberModel.organization_id == organization_id
                )
            )
            return [self._to_entity(model) for model in result.scalars().all()]

    async def find_by_organization_and_user(
        self, organization_id: UUID, user_id: UUID
    ) -> OrganizationMember | None:
        async with self._session_factory() as session:
            result = await session.execute(
                select(OrganizationMemberModel).where(
                    OrganizationMemberModel.organization_id == organization_id,
                    OrganizationMemberModel.user_id == user_id,
                )
            )
            model = result.scalars().first()
            return self._to_entity(model) if model is not None else None

    async def delete(self, member_id: UUID) -> None:
        async with self._session_factory() as session:
            await session.execute(
                delete(OrganizationMemberModel).where(OrganizationMemberModel.id == member_id)
            )
            await session.commit()

    @staticmethod
    def _to_entity(model: OrganizationMemberModel) -> OrganizationMember:
        return OrganizationMember(
            id=model.id,
            organization_id=model.organization_id,
            user_id=model.user_id,
            role=OrganizationMemberRole(model.role),
            joined_at=model.joined_at,
        )
