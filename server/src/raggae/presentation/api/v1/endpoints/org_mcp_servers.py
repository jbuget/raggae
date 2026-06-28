import logging
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from raggae.application.dto.org_mcp_server_dto import OrgMcpServerDTO
from raggae.application.use_cases.org_mcp.activate_org_mcp_server import ActivateOrgMcpServer
from raggae.application.use_cases.org_mcp.deactivate_org_mcp_server import DeactivateOrgMcpServer
from raggae.application.use_cases.org_mcp.declare_org_mcp_server import DeclareOrgMcpServer
from raggae.application.use_cases.org_mcp.delete_org_mcp_server import DeleteOrgMcpServer
from raggae.application.use_cases.org_mcp.list_org_mcp_servers import ListOrgMcpServers
from raggae.application.use_cases.org_mcp.refresh_org_mcp_tools import RefreshOrgMcpTools
from raggae.application.use_cases.org_mcp.update_org_mcp_server import UpdateOrgMcpServer
from raggae.domain.exceptions.mcp_exceptions import (
    McpHandshakeError,
    McpServerNotFoundError,
    McpUrlForbiddenError,
)
from raggae.domain.exceptions.organization_exceptions import OrganizationAccessDeniedError
from raggae.presentation.api.dependencies import (
    get_activate_org_mcp_server_use_case,
    get_current_user_id,
    get_deactivate_org_mcp_server_use_case,
    get_declare_org_mcp_server_use_case,
    get_delete_org_mcp_server_use_case,
    get_list_org_mcp_servers_use_case,
    get_refresh_org_mcp_tools_use_case,
    get_update_org_mcp_server_use_case,
)
from raggae.presentation.api.v1.schemas.org_mcp_server_schemas import (
    DeclareOrgMcpServerRequest,
    McpToolSnapshotResponse,
    OrgMcpServerResponse,
    UpdateOrgMcpServerRequest,
)

router = APIRouter(
    prefix="/organizations/{organization_id}/mcp-servers",
    tags=["org-mcp-servers"],
    dependencies=[Depends(get_current_user_id)],
)
logger = logging.getLogger(__name__)


def _to_response(dto: OrgMcpServerDTO) -> OrgMcpServerResponse:
    return OrgMcpServerResponse(
        id=dto.id,
        organization_id=dto.organization_id,
        name=dto.name,
        slug=dto.slug,
        url=dto.url,
        auth_type=dto.auth_type,
        masked_token=dto.masked_token,
        is_active=dto.is_active,
        tools_snapshot=[
            McpToolSnapshotResponse(
                name=t.name,
                description=t.description,
                input_schema=t.input_schema,
            )
            for t in dto.tools_snapshot
        ],
        tools_snapshot_at=dto.tools_snapshot_at,
        timeout_seconds=dto.timeout_seconds,
        created_at=dto.created_at,
        updated_at=dto.updated_at,
    )


def _raise_access_denied() -> HTTPException:
    return HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")


def _raise_not_found() -> HTTPException:
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="MCP server not found")


def _raise_url_forbidden(message: str) -> HTTPException:
    return HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=message)


def _raise_handshake_error(message: str) -> HTTPException:
    return HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=message)


@router.post("", status_code=status.HTTP_201_CREATED)
async def declare_org_mcp_server(
    organization_id: UUID,
    data: DeclareOrgMcpServerRequest,
    user_id: Annotated[UUID, Depends(get_current_user_id)],
    use_case: Annotated[DeclareOrgMcpServer, Depends(get_declare_org_mcp_server_use_case)],
) -> OrgMcpServerResponse:
    try:
        server = await use_case.execute(
            organization_id=organization_id,
            user_id=user_id,
            name=data.name,
            url=data.url,
            auth_type=data.auth_type,
            bearer_token=data.bearer_token,
            timeout_seconds=data.timeout_seconds,
        )
    except OrganizationAccessDeniedError as exc:
        raise _raise_access_denied() from exc
    except McpUrlForbiddenError as exc:
        raise _raise_url_forbidden(str(exc)) from exc
    except McpHandshakeError as exc:
        raise _raise_handshake_error(str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(exc)) from exc

    logger.info(
        "org_mcp_server_declared",
        extra={
            "organization_id": str(organization_id),
            "user_id": str(user_id),
            "mcp_server_id": str(server.id),
            "slug": server.slug,
        },
    )
    return _to_response(server)


@router.get("")
async def list_org_mcp_servers(
    organization_id: UUID,
    user_id: Annotated[UUID, Depends(get_current_user_id)],
    use_case: Annotated[ListOrgMcpServers, Depends(get_list_org_mcp_servers_use_case)],
) -> list[OrgMcpServerResponse]:
    try:
        servers = await use_case.execute(organization_id=organization_id, user_id=user_id)
    except OrganizationAccessDeniedError as exc:
        raise _raise_access_denied() from exc
    return [_to_response(server) for server in servers]


@router.patch("/{mcp_server_id}")
async def update_org_mcp_server(
    organization_id: UUID,
    mcp_server_id: UUID,
    data: UpdateOrgMcpServerRequest,
    user_id: Annotated[UUID, Depends(get_current_user_id)],
    use_case: Annotated[UpdateOrgMcpServer, Depends(get_update_org_mcp_server_use_case)],
) -> OrgMcpServerResponse:
    try:
        server = await use_case.execute(
            server_id=mcp_server_id,
            organization_id=organization_id,
            user_id=user_id,
            name=data.name,
            url=data.url,
            timeout_seconds=data.timeout_seconds,
            auth_type=data.auth_type,
            bearer_token=data.bearer_token,
        )
    except OrganizationAccessDeniedError as exc:
        raise _raise_access_denied() from exc
    except McpServerNotFoundError as exc:
        raise _raise_not_found() from exc
    except McpUrlForbiddenError as exc:
        raise _raise_url_forbidden(str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(exc)) from exc
    return _to_response(server)


@router.post("/{mcp_server_id}/refresh")
async def refresh_org_mcp_tools(
    organization_id: UUID,
    mcp_server_id: UUID,
    user_id: Annotated[UUID, Depends(get_current_user_id)],
    use_case: Annotated[RefreshOrgMcpTools, Depends(get_refresh_org_mcp_tools_use_case)],
) -> OrgMcpServerResponse:
    try:
        server = await use_case.execute(
            server_id=mcp_server_id,
            organization_id=organization_id,
            user_id=user_id,
        )
    except OrganizationAccessDeniedError as exc:
        raise _raise_access_denied() from exc
    except McpServerNotFoundError as exc:
        raise _raise_not_found() from exc
    except McpHandshakeError as exc:
        raise _raise_handshake_error(str(exc)) from exc
    return _to_response(server)


@router.patch("/{mcp_server_id}/activate", status_code=status.HTTP_204_NO_CONTENT)
async def activate_org_mcp_server(
    organization_id: UUID,
    mcp_server_id: UUID,
    user_id: Annotated[UUID, Depends(get_current_user_id)],
    use_case: Annotated[ActivateOrgMcpServer, Depends(get_activate_org_mcp_server_use_case)],
) -> None:
    try:
        await use_case.execute(
            server_id=mcp_server_id,
            organization_id=organization_id,
            user_id=user_id,
        )
    except OrganizationAccessDeniedError as exc:
        raise _raise_access_denied() from exc
    except McpServerNotFoundError as exc:
        raise _raise_not_found() from exc


@router.patch("/{mcp_server_id}/deactivate", status_code=status.HTTP_204_NO_CONTENT)
async def deactivate_org_mcp_server(
    organization_id: UUID,
    mcp_server_id: UUID,
    user_id: Annotated[UUID, Depends(get_current_user_id)],
    use_case: Annotated[DeactivateOrgMcpServer, Depends(get_deactivate_org_mcp_server_use_case)],
) -> None:
    try:
        await use_case.execute(
            server_id=mcp_server_id,
            organization_id=organization_id,
            user_id=user_id,
        )
    except OrganizationAccessDeniedError as exc:
        raise _raise_access_denied() from exc
    except McpServerNotFoundError as exc:
        raise _raise_not_found() from exc


@router.delete("/{mcp_server_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_org_mcp_server(
    organization_id: UUID,
    mcp_server_id: UUID,
    user_id: Annotated[UUID, Depends(get_current_user_id)],
    use_case: Annotated[DeleteOrgMcpServer, Depends(get_delete_org_mcp_server_use_case)],
) -> None:
    try:
        await use_case.execute(
            server_id=mcp_server_id,
            organization_id=organization_id,
            user_id=user_id,
        )
    except OrganizationAccessDeniedError as exc:
        raise _raise_access_denied() from exc
    except McpServerNotFoundError as exc:
        raise _raise_not_found() from exc
