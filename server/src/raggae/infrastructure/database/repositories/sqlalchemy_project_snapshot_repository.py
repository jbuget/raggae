from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from raggae.domain.entities.project_snapshot import ProjectSnapshot
from raggae.domain.value_objects.chunking_strategy import ChunkingStrategy
from raggae.infrastructure.database.models.project_snapshot_model import ProjectSnapshotModel


class SQLAlchemyProjectSnapshotRepository:
    """PostgreSQL project snapshot repository using SQLAlchemy async sessions."""

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory

    async def save(self, snapshot: ProjectSnapshot) -> None:
        async with self._session_factory() as session:
            model = ProjectSnapshotModel(
                id=snapshot.id,
                project_id=snapshot.project_id,
                version_number=snapshot.version_number,
                label=snapshot.label,
                created_at=snapshot.created_at,
                created_by_user_id=snapshot.created_by_user_id,
                name=snapshot.name,
                description=snapshot.description,
                system_prompt=snapshot.system_prompt,
                is_published=snapshot.is_published,
                chunking_strategy=snapshot.chunking_strategy.value,
                parent_child_chunking=snapshot.parent_child_chunking,
                organization_id=snapshot.organization_id,
                embedding_backend=snapshot.embedding_backend,
                embedding_model=snapshot.embedding_model,
                embedding_api_key_credential_id=snapshot.embedding_api_key_credential_id,
                org_embedding_api_key_credential_id=snapshot.org_embedding_api_key_credential_id,
                llm_backend=snapshot.llm_backend,
                llm_model=snapshot.llm_model,
                llm_api_key_credential_id=snapshot.llm_api_key_credential_id,
                org_llm_api_key_credential_id=snapshot.org_llm_api_key_credential_id,
                retrieval_strategy=snapshot.retrieval_strategy,
                retrieval_top_k=snapshot.retrieval_top_k,
                retrieval_min_score=snapshot.retrieval_min_score,
                chat_history_window_size=snapshot.chat_history_window_size,
                chat_history_max_chars=snapshot.chat_history_max_chars,
                reranking_enabled=snapshot.reranking_enabled,
                reranker_backend=snapshot.reranker_backend,
                reranker_model=snapshot.reranker_model,
                reranker_candidate_multiplier=snapshot.reranker_candidate_multiplier,
                restored_from_version=snapshot.restored_from_version,
            )
            session.add(model)
            await session.commit()

    async def find_by_project_and_version(
        self,
        project_id: UUID,
        version_number: int,
    ) -> ProjectSnapshot | None:
        async with self._session_factory() as session:
            result = await session.execute(
                select(ProjectSnapshotModel).where(
                    ProjectSnapshotModel.project_id == project_id,
                    ProjectSnapshotModel.version_number == version_number,
                )
            )
            model = result.scalar_one_or_none()
            if model is None:
                return None
            return self._to_entity(model)

    async def find_by_project_id(
        self,
        project_id: UUID,
        limit: int = 20,
        offset: int = 0,
    ) -> list[ProjectSnapshot]:
        async with self._session_factory() as session:
            result = await session.execute(
                select(ProjectSnapshotModel)
                .where(ProjectSnapshotModel.project_id == project_id)
                .order_by(ProjectSnapshotModel.version_number.desc())
                .limit(limit)
                .offset(offset)
            )
            models = result.scalars().all()
            return [self._to_entity(m) for m in models]

    async def count_by_project_id(self, project_id: UUID) -> int:
        async with self._session_factory() as session:
            result = await session.execute(
                select(func.count()).where(ProjectSnapshotModel.project_id == project_id)
            )
            return result.scalar_one()

    async def get_next_version_number(self, project_id: UUID) -> int:
        async with self._session_factory() as session:
            result = await session.execute(
                select(func.max(ProjectSnapshotModel.version_number)).where(
                    ProjectSnapshotModel.project_id == project_id
                )
            )
            max_version = result.scalar_one_or_none()
            if max_version is None:
                return 1
            return max_version + 1

    def _to_entity(self, model: ProjectSnapshotModel) -> ProjectSnapshot:
        return ProjectSnapshot(
            id=model.id,
            project_id=model.project_id,
            version_number=model.version_number,
            label=model.label,
            created_at=model.created_at,
            created_by_user_id=model.created_by_user_id,
            name=model.name,
            description=model.description,
            system_prompt=model.system_prompt,
            is_published=model.is_published,
            chunking_strategy=ChunkingStrategy(model.chunking_strategy),
            parent_child_chunking=model.parent_child_chunking,
            organization_id=model.organization_id,
            embedding_backend=model.embedding_backend,
            embedding_model=model.embedding_model,
            embedding_api_key_credential_id=model.embedding_api_key_credential_id,
            org_embedding_api_key_credential_id=model.org_embedding_api_key_credential_id,
            llm_backend=model.llm_backend,
            llm_model=model.llm_model,
            llm_api_key_credential_id=model.llm_api_key_credential_id,
            org_llm_api_key_credential_id=model.org_llm_api_key_credential_id,
            retrieval_strategy=model.retrieval_strategy,
            retrieval_top_k=model.retrieval_top_k,
            retrieval_min_score=model.retrieval_min_score,
            chat_history_window_size=model.chat_history_window_size,
            chat_history_max_chars=model.chat_history_max_chars,
            reranking_enabled=model.reranking_enabled,
            reranker_backend=model.reranker_backend,
            reranker_model=model.reranker_model,
            reranker_candidate_multiplier=model.reranker_candidate_multiplier,
            restored_from_version=model.restored_from_version,
        )
