from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from raggae.domain.entities.project_snapshot import ProjectSnapshot
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
                organization_id=snapshot.organization_id,
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
            return int(result.scalar_one())

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
            return int(max_version) + 1

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
            organization_id=model.organization_id,
            restored_from_version=model.restored_from_version,
        )
