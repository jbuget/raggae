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
                    name=project.name,
                    description=project.description,
                    system_prompt=project.system_prompt,
                    is_published=project.is_published,
                    created_at=project.created_at,
                )
                session.add(model)
            else:
                model.user_id = project.user_id
                model.name = project.name
                model.description = project.description
                model.system_prompt = project.system_prompt
                model.is_published = project.is_published
            await session.commit()

    async def find_by_id(self, project_id: UUID) -> Project | None:
        async with self._session_factory() as session:
            model = await session.get(ProjectModel, project_id)
            if model is None:
                return None
            return Project(
                id=model.id,
                user_id=model.user_id,
                name=model.name,
                description=model.description,
                system_prompt=model.system_prompt,
                is_published=model.is_published,
                created_at=model.created_at,
            )

    async def find_by_user_id(self, user_id: UUID) -> list[Project]:
        async with self._session_factory() as session:
            result = await session.execute(
                select(ProjectModel).where(ProjectModel.user_id == user_id)
            )
            models = result.scalars().all()
            return [
                Project(
                    id=model.id,
                    user_id=model.user_id,
                    name=model.name,
                    description=model.description,
                    system_prompt=model.system_prompt,
                    is_published=model.is_published,
                    created_at=model.created_at,
                )
                for model in models
            ]

    async def delete(self, project_id: UUID) -> None:
        async with self._session_factory() as session:
            await session.execute(delete(ProjectModel).where(ProjectModel.id == project_id))
            await session.commit()
