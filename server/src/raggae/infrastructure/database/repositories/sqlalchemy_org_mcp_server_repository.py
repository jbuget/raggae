from typing import Any
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from raggae.domain.entities.org_mcp_server import OrgMcpServer
from raggae.domain.value_objects.mcp_auth_type import McpAuthType
from raggae.domain.value_objects.mcp_tool_snapshot import McpToolSnapshot
from raggae.infrastructure.database.models.org_mcp_server_model import OrgMcpServerModel


class SQLAlchemyOrgMcpServerRepository:
    """PostgreSQL repository for organization MCP servers."""

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory

    async def save(self, server: OrgMcpServer) -> None:
        async with self._session_factory() as session:
            model = await session.get(OrgMcpServerModel, server.id)
            if model is None:
                model = OrgMcpServerModel(
                    id=server.id,
                    organization_id=server.organization_id,
                    name=server.name,
                    slug=server.slug,
                    url=server.url,
                    auth_type=server.auth_type.value,
                    encrypted_bearer_token=server.encrypted_bearer_token,
                    token_fingerprint=server.token_fingerprint,
                    token_suffix=server.token_suffix,
                    is_active=server.is_active,
                    tools_snapshot=_tools_to_json(server.tools_snapshot),
                    tools_snapshot_at=server.tools_snapshot_at,
                    timeout_seconds=server.timeout_seconds,
                    created_by_user_id=server.created_by_user_id,
                    created_at=server.created_at,
                    updated_at=server.updated_at,
                )
                session.add(model)
            else:
                model.name = server.name
                model.url = server.url
                model.auth_type = server.auth_type.value
                model.encrypted_bearer_token = server.encrypted_bearer_token
                model.token_fingerprint = server.token_fingerprint
                model.token_suffix = server.token_suffix
                model.is_active = server.is_active
                model.tools_snapshot = _tools_to_json(server.tools_snapshot)
                model.tools_snapshot_at = server.tools_snapshot_at
                model.timeout_seconds = server.timeout_seconds
                model.updated_at = server.updated_at
            await session.commit()

    async def find_by_id(self, server_id: UUID, organization_id: UUID) -> OrgMcpServer | None:
        async with self._session_factory() as session:
            result = await session.execute(
                select(OrgMcpServerModel).where(
                    OrgMcpServerModel.id == server_id,
                    OrgMcpServerModel.organization_id == organization_id,
                )
            )
            model = result.scalar_one_or_none()
            return _to_domain(model) if model is not None else None

    async def find_by_slug(self, organization_id: UUID, slug: str) -> OrgMcpServer | None:
        async with self._session_factory() as session:
            result = await session.execute(
                select(OrgMcpServerModel).where(
                    OrgMcpServerModel.organization_id == organization_id,
                    OrgMcpServerModel.slug == slug,
                )
            )
            model = result.scalar_one_or_none()
            return _to_domain(model) if model is not None else None

    async def list_by_org_id(self, organization_id: UUID) -> list[OrgMcpServer]:
        async with self._session_factory() as session:
            result = await session.execute(
                select(OrgMcpServerModel)
                .where(OrgMcpServerModel.organization_id == organization_id)
                .order_by(OrgMcpServerModel.created_at)
            )
            return [_to_domain(m) for m in result.scalars().all()]

    async def delete(self, server_id: UUID, organization_id: UUID) -> None:
        async with self._session_factory() as session:
            await session.execute(
                delete(OrgMcpServerModel).where(
                    OrgMcpServerModel.id == server_id,
                    OrgMcpServerModel.organization_id == organization_id,
                )
            )
            await session.commit()


def _tools_to_json(tools: list[McpToolSnapshot]) -> list[dict[str, Any]]:
    return [{"name": t.name, "description": t.description, "input_schema": t.input_schema} for t in tools]


def _tools_from_json(payload: list[dict[str, Any]] | None) -> list[McpToolSnapshot]:
    if not payload:
        return []
    snapshots: list[McpToolSnapshot] = []
    for item in payload:
        raw_schema = item.get("input_schema")
        input_schema: dict[str, Any] = dict(raw_schema) if isinstance(raw_schema, dict) else {}
        snapshots.append(
            McpToolSnapshot(
                name=str(item.get("name", "")),
                description=str(item.get("description", "")),
                input_schema=input_schema,
            )
        )
    return snapshots


def _to_domain(model: OrgMcpServerModel) -> OrgMcpServer:
    return OrgMcpServer(
        id=model.id,
        organization_id=model.organization_id,
        name=model.name,
        slug=model.slug,
        url=model.url,
        auth_type=McpAuthType(model.auth_type),
        encrypted_bearer_token=model.encrypted_bearer_token,
        token_fingerprint=model.token_fingerprint,
        token_suffix=model.token_suffix,
        is_active=model.is_active,
        tools_snapshot=_tools_from_json(model.tools_snapshot),
        tools_snapshot_at=model.tools_snapshot_at,
        timeout_seconds=model.timeout_seconds,
        created_by_user_id=model.created_by_user_id,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )
