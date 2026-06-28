from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from raggae.domain.entities.project_mcp_activation import ProjectMcpActivation
from raggae.infrastructure.database.models.project_mcp_activation_model import (
    ProjectMcpActivationModel,
)


class SQLAlchemyProjectMcpActivationRepository:
    """PostgreSQL repository for project ↔ MCP server activations."""

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory

    async def save(self, activation: ProjectMcpActivation) -> None:
        async with self._session_factory() as session:
            existing = await session.get(
                ProjectMcpActivationModel,
                (activation.project_id, activation.org_mcp_server_id),
            )
            if existing is None:
                session.add(
                    ProjectMcpActivationModel(
                        project_id=activation.project_id,
                        org_mcp_server_id=activation.org_mcp_server_id,
                        is_active=activation.is_active,
                        activated_at=activation.activated_at,
                        activated_by_user_id=activation.activated_by_user_id,
                    )
                )
            else:
                existing.is_active = activation.is_active
                existing.activated_at = activation.activated_at
                existing.activated_by_user_id = activation.activated_by_user_id
            await session.commit()

    async def find(self, project_id: UUID, org_mcp_server_id: UUID) -> ProjectMcpActivation | None:
        async with self._session_factory() as session:
            model = await session.get(ProjectMcpActivationModel, (project_id, org_mcp_server_id))
            return _to_domain(model) if model is not None else None

    async def list_by_project_id(self, project_id: UUID) -> list[ProjectMcpActivation]:
        async with self._session_factory() as session:
            result = await session.execute(
                select(ProjectMcpActivationModel).where(ProjectMcpActivationModel.project_id == project_id)
            )
            return [_to_domain(m) for m in result.scalars().all()]

    async def list_by_org_mcp_server_id(self, org_mcp_server_id: UUID) -> list[ProjectMcpActivation]:
        async with self._session_factory() as session:
            result = await session.execute(
                select(ProjectMcpActivationModel).where(
                    ProjectMcpActivationModel.org_mcp_server_id == org_mcp_server_id
                )
            )
            return [_to_domain(m) for m in result.scalars().all()]

    async def delete(self, project_id: UUID, org_mcp_server_id: UUID) -> None:
        async with self._session_factory() as session:
            await session.execute(
                delete(ProjectMcpActivationModel).where(
                    ProjectMcpActivationModel.project_id == project_id,
                    ProjectMcpActivationModel.org_mcp_server_id == org_mcp_server_id,
                )
            )
            await session.commit()

    async def delete_by_org_mcp_server_id(self, org_mcp_server_id: UUID) -> None:
        async with self._session_factory() as session:
            await session.execute(
                delete(ProjectMcpActivationModel).where(
                    ProjectMcpActivationModel.org_mcp_server_id == org_mcp_server_id
                )
            )
            await session.commit()

    async def count_active_activations(self) -> int:
        from sqlalchemy import func
        from sqlalchemy import select as sa_select

        async with self._session_factory() as session:
            result = await session.execute(
                sa_select(func.count())
                .select_from(ProjectMcpActivationModel)
                .where(ProjectMcpActivationModel.is_active.is_(True))
            )
            return int(result.scalar_one() or 0)

    async def count_distinct_active_projects(self) -> int:
        from sqlalchemy import func
        from sqlalchemy import select as sa_select

        async with self._session_factory() as session:
            result = await session.execute(
                sa_select(func.count(func.distinct(ProjectMcpActivationModel.project_id))).where(
                    ProjectMcpActivationModel.is_active.is_(True)
                )
            )
            return int(result.scalar_one() or 0)


def _to_domain(model: ProjectMcpActivationModel) -> ProjectMcpActivation:
    return ProjectMcpActivation(
        project_id=model.project_id,
        org_mcp_server_id=model.org_mcp_server_id,
        is_active=model.is_active,
        activated_at=model.activated_at,
        activated_by_user_id=model.activated_by_user_id,
    )
