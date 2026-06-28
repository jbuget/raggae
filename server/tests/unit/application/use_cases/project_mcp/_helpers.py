"""Shared test helpers for project_mcp use cases."""

from datetime import UTC, datetime
from uuid import UUID, uuid4

from raggae.domain.entities.org_mcp_server import OrgMcpServer
from raggae.domain.entities.project import Project
from raggae.domain.entities.project_mcp_activation import ProjectMcpActivation
from raggae.domain.value_objects.mcp_auth_type import McpAuthType


def make_project(
    *,
    project_id: UUID | None = None,
    user_id: UUID | None = None,
    organization_id: UUID | None = None,
) -> Project:
    return Project(
        id=project_id or uuid4(),
        user_id=user_id or uuid4(),
        name="P",
        description="",
        system_prompt="",
        is_published=False,
        created_at=datetime.now(UTC),
        organization_id=organization_id,
    )


def make_member(role: str) -> object:
    return type("Member", (), {"role": role})()


def make_server(
    *,
    server_id: UUID | None = None,
    organization_id: UUID | None = None,
    slug: str = "notion",
    is_active: bool = True,
) -> OrgMcpServer:
    now = datetime.now(UTC)
    return OrgMcpServer(
        id=server_id or uuid4(),
        organization_id=organization_id or uuid4(),
        name=slug.capitalize(),
        slug=slug,
        url="https://mcp.example.com",
        auth_type=McpAuthType.NONE,
        encrypted_bearer_token=None,
        token_fingerprint=None,
        token_suffix=None,
        is_active=is_active,
        tools_snapshot=[],
        tools_snapshot_at=now,
        timeout_seconds=30,
        created_at=now,
        updated_at=now,
        created_by_user_id=uuid4(),
    )


def make_activation(
    *,
    project_id: UUID,
    server_id: UUID,
    is_active: bool = True,
) -> ProjectMcpActivation:
    return ProjectMcpActivation(
        project_id=project_id,
        org_mcp_server_id=server_id,
        is_active=is_active,
        activated_at=datetime.now(UTC),
        activated_by_user_id=uuid4(),
    )
