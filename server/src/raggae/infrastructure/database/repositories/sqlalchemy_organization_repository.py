from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from raggae.domain.entities.organization import Organization
from raggae.infrastructure.database.models.organization_model import OrganizationModel


class SQLAlchemyOrganizationRepository:
    """PostgreSQL organization repository using SQLAlchemy async sessions."""

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory

    async def save(self, organization: Organization) -> None:
        async with self._session_factory() as session:
            model = await session.get(OrganizationModel, organization.id)
            if model is None:
                model = OrganizationModel(
                    id=organization.id,
                    name=organization.name,
                    slug=organization.slug,
                    description=organization.description,
                    logo_url=organization.logo_url,
                    created_by_user_id=organization.created_by_user_id,
                    created_at=organization.created_at,
                    updated_at=organization.updated_at,
                )
                session.add(model)
            else:
                model.name = organization.name
                model.slug = organization.slug
                model.description = organization.description
                model.logo_url = organization.logo_url
                model.created_by_user_id = organization.created_by_user_id
                model.updated_at = organization.updated_at
            await session.commit()

    async def find_by_id(self, organization_id: UUID) -> Organization | None:
        async with self._session_factory() as session:
            model = await session.get(OrganizationModel, organization_id)
            if model is None:
                return None
            return self._to_entity(model)

    async def find_by_user_id(self, user_id: UUID) -> list[Organization]:
        async with self._session_factory() as session:
            result = await session.execute(
                select(OrganizationModel).where(OrganizationModel.created_by_user_id == user_id)
            )
            return [self._to_entity(model) for model in result.scalars().all()]

    async def find_by_slug(self, slug: str) -> Organization | None:
        async with self._session_factory() as session:
            result = await session.execute(
                select(OrganizationModel).where(OrganizationModel.slug == slug)
            )
            model = result.scalar_one_or_none()
            if model is None:
                return None
            return self._to_entity(model)

    async def delete(self, organization_id: UUID) -> None:
        async with self._session_factory() as session:
            await session.execute(delete(OrganizationModel).where(OrganizationModel.id == organization_id))
            await session.commit()

    @staticmethod
    def _to_entity(model: OrganizationModel) -> Organization:
        return Organization(
            id=model.id,
            name=model.name,
            slug=model.slug,
            description=model.description,
            logo_url=model.logo_url,
            created_by_user_id=model.created_by_user_id,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
