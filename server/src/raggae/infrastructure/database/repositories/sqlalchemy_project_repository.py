from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from raggae.domain.entities.project import Project
from raggae.domain.value_objects.chunking_strategy import ChunkingStrategy
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
                    chunking_strategy=project.chunking_strategy.value,
                    parent_child_chunking=project.parent_child_chunking,
                    reindex_status=project.reindex_status,
                    reindex_progress=project.reindex_progress,
                    reindex_total=project.reindex_total,
                    embedding_backend=project.embedding_backend,
                    embedding_model=project.embedding_model,
                    embedding_api_key_encrypted=project.embedding_api_key_encrypted,
                    embedding_api_key_credential_id=project.embedding_api_key_credential_id,
                    llm_backend=project.llm_backend,
                    llm_model=project.llm_model,
                    llm_api_key_encrypted=project.llm_api_key_encrypted,
                    llm_api_key_credential_id=project.llm_api_key_credential_id,
                    created_at=project.created_at,
                )
                session.add(model)
            else:
                model.user_id = project.user_id
                model.name = project.name
                model.description = project.description
                model.system_prompt = project.system_prompt
                model.is_published = project.is_published
                model.chunking_strategy = project.chunking_strategy.value
                model.parent_child_chunking = project.parent_child_chunking
                model.reindex_status = project.reindex_status
                model.reindex_progress = project.reindex_progress
                model.reindex_total = project.reindex_total
                model.embedding_backend = project.embedding_backend
                model.embedding_model = project.embedding_model
                model.embedding_api_key_encrypted = project.embedding_api_key_encrypted
                model.embedding_api_key_credential_id = project.embedding_api_key_credential_id
                model.llm_backend = project.llm_backend
                model.llm_model = project.llm_model
                model.llm_api_key_encrypted = project.llm_api_key_encrypted
                model.llm_api_key_credential_id = project.llm_api_key_credential_id
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
                chunking_strategy=ChunkingStrategy(model.chunking_strategy),
                parent_child_chunking=model.parent_child_chunking,
                reindex_status=model.reindex_status,
                reindex_progress=model.reindex_progress,
                reindex_total=model.reindex_total,
                embedding_backend=model.embedding_backend,
                embedding_model=model.embedding_model,
                embedding_api_key_encrypted=model.embedding_api_key_encrypted,
                embedding_api_key_credential_id=model.embedding_api_key_credential_id,
                llm_backend=model.llm_backend,
                llm_model=model.llm_model,
                llm_api_key_encrypted=model.llm_api_key_encrypted,
                llm_api_key_credential_id=model.llm_api_key_credential_id,
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
                    chunking_strategy=ChunkingStrategy(model.chunking_strategy),
                    parent_child_chunking=model.parent_child_chunking,
                    reindex_status=model.reindex_status,
                    reindex_progress=model.reindex_progress,
                    reindex_total=model.reindex_total,
                    embedding_backend=model.embedding_backend,
                    embedding_model=model.embedding_model,
                    embedding_api_key_encrypted=model.embedding_api_key_encrypted,
                    embedding_api_key_credential_id=model.embedding_api_key_credential_id,
                    llm_backend=model.llm_backend,
                    llm_model=model.llm_model,
                    llm_api_key_encrypted=model.llm_api_key_encrypted,
                    llm_api_key_credential_id=model.llm_api_key_credential_id,
                    created_at=model.created_at,
                )
                for model in models
            ]

    async def delete(self, project_id: UUID) -> None:
        async with self._session_factory() as session:
            await session.execute(delete(ProjectModel).where(ProjectModel.id == project_id))
            await session.commit()
