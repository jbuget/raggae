from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from raggae.domain.entities.project import Project
from raggae.infrastructure.database.models.project_model import ProjectModel


class SQLAlchemyProjectRepository:
    """PostgreSQL project repository using SQLAlchemy async sessions."""

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory

    async def save(self, project: Project) -> None:
        async with self._session_factory() as session:
            model = await session.get(ProjectModel, project.id)
            if model is None:
                model = ProjectModel(
                    id=project.id,
                    user_id=project.user_id,
                    organization_id=project.organization_id,
                    name=project.name,
                    description=project.description,
                    system_prompt=project.system_prompt,
                    is_published=project.is_published,
                    reindex_status=project.reindex_status,
                    reindex_progress=project.reindex_progress,
                    reindex_total=project.reindex_total,
                    created_at=project.created_at,
                )
                session.add(model)
            else:
                model.user_id = project.user_id
                model.organization_id = project.organization_id
                model.name = project.name
                model.description = project.description
                model.system_prompt = project.system_prompt
                model.is_published = project.is_published
                model.reindex_status = project.reindex_status
                model.reindex_progress = project.reindex_progress
                model.reindex_total = project.reindex_total
            await session.commit()

    def _to_entity(self, model: ProjectModel) -> Project:
        return Project(
            id=model.id,
            user_id=model.user_id,
            organization_id=model.organization_id,
            name=model.name,
            description=model.description,
            system_prompt=model.system_prompt,
            is_published=model.is_published,
            reindex_status=model.reindex_status,
            reindex_progress=model.reindex_progress,
            reindex_total=model.reindex_total,
            created_at=model.created_at,
        )

    async def find_by_id(self, project_id: UUID) -> Project | None:
        async with self._session_factory() as session:
            model = await session.get(ProjectModel, project_id)
            if model is None:
                return None
            return self._to_entity(model)

    async def find_by_user_id(self, user_id: UUID) -> list[Project]:
        async with self._session_factory() as session:
            result = await session.execute(select(ProjectModel).where(ProjectModel.user_id == user_id))
            return [self._to_entity(m) for m in result.scalars().all()]

    async def find_by_organization_id(self, organization_id: UUID) -> list[Project]:
        async with self._session_factory() as session:
            result = await session.execute(
                select(ProjectModel).where(ProjectModel.organization_id == organization_id)
            )
            return [self._to_entity(m) for m in result.scalars().all()]

    async def find_by_organization_ids(self, organization_ids: list[UUID]) -> list[Project]:
        if not organization_ids:
            return []
        async with self._session_factory() as session:
            result = await session.execute(
                select(ProjectModel).where(ProjectModel.organization_id.in_(organization_ids))
            )
            return [self._to_entity(m) for m in result.scalars().all()]

    async def delete(self, project_id: UUID) -> None:
        async with self._session_factory() as session:
            await session.execute(delete(ProjectModel).where(ProjectModel.id == project_id))
            await session.commit()
