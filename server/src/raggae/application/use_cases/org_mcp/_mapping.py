"""Internal mapping helpers shared across org_mcp use cases."""

from raggae.application.dto.org_mcp_server_dto import McpToolSnapshotDTO, OrgMcpServerDTO
from raggae.domain.entities.org_mcp_server import OrgMcpServer


def to_dto(server: OrgMcpServer) -> OrgMcpServerDTO:
    return OrgMcpServerDTO(
        id=server.id,
        organization_id=server.organization_id,
        name=server.name,
        slug=server.slug,
        url=server.url,
        auth_type=server.auth_type.value,
        masked_token=server.masked_token,
        is_active=server.is_active,
        tools_snapshot=[
            McpToolSnapshotDTO(
                name=t.name,
                description=t.description,
                input_schema=t.input_schema,
            )
            for t in server.tools_snapshot
        ],
        tools_snapshot_at=server.tools_snapshot_at,
        timeout_seconds=server.timeout_seconds,
        created_at=server.created_at,
        updated_at=server.updated_at,
    )
