import logging
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from raggae.application.dto.org_mcp_server_dto import OrgMcpServerDTO
from raggae.application.use_cases.project_mcp.activate_project_mcp import ActivateProjectMcp
from raggae.application.use_cases.project_mcp.deactivate_project_mcp import DeactivateProjectMcp
from raggae.application.use_cases.project_mcp.list_project_mcp_activations import (
    ListProjectMcpActivations,
)
from raggae.domain.exceptions.mcp_exceptions import (
    McpAccessDeniedError,
    McpServerNotFoundError,
)
from raggae.domain.exceptions.project_exceptions import ProjectNotFoundError
from raggae.presentation.api.dependencies import (
    get_activate_project_mcp_use_case,
    get_current_user_id,
    get_deactivate_project_mcp_use_case,
    get_list_project_mcp_activations_use_case,
)
from raggae.presentation.api.v1.schemas.org_mcp_server_schemas import (
    McpToolSnapshotResponse,
    OrgMcpServerResponse,
)
from raggae.presentation.api.v1.schemas.project_mcp_activation_schemas import (
    ProjectMcpActivationViewResponse,
)

router = APIRouter(
    prefix="/projects/{project_id}/mcp-activations",
    tags=["project-mcp-activations"],
    dependencies=[Depends(get_current_user_id)],
)
logger = logging.getLogger(__name__)


def _server_dto_to_response(dto: OrgMcpServerDTO) -> OrgMcpServerResponse:
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


@router.get("")
async def list_project_mcp_activations(
    project_id: UUID,
    user_id: Annotated[UUID, Depends(get_current_user_id)],
    use_case: Annotated[ListProjectMcpActivations, Depends(get_list_project_mcp_activations_use_case)],
) -> list[ProjectMcpActivationViewResponse]:
    try:
        views = await use_case.execute(project_id=project_id, user_id=user_id)
    except ProjectNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found") from exc
    return [
        ProjectMcpActivationViewResponse(
            org_mcp_server=_server_dto_to_response(view.org_mcp_server),
            is_activated=view.is_activated,
        )
        for view in views
    ]


@router.post("/{mcp_server_id}", status_code=status.HTTP_204_NO_CONTENT)
async def activate_project_mcp(
    project_id: UUID,
    mcp_server_id: UUID,
    user_id: Annotated[UUID, Depends(get_current_user_id)],
    use_case: Annotated[ActivateProjectMcp, Depends(get_activate_project_mcp_use_case)],
) -> None:
    try:
        await use_case.execute(project_id=project_id, mcp_server_id=mcp_server_id, user_id=user_id)
    except ProjectNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found") from exc
    except McpServerNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="MCP server not found") from exc
    except McpAccessDeniedError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
    logger.info(
        "project_mcp_activated",
        extra={
            "project_id": str(project_id),
            "mcp_server_id": str(mcp_server_id),
            "user_id": str(user_id),
        },
    )


@router.delete("/{mcp_server_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deactivate_project_mcp(
    project_id: UUID,
    mcp_server_id: UUID,
    user_id: Annotated[UUID, Depends(get_current_user_id)],
    use_case: Annotated[DeactivateProjectMcp, Depends(get_deactivate_project_mcp_use_case)],
) -> None:
    try:
        await use_case.execute(project_id=project_id, mcp_server_id=mcp_server_id, user_id=user_id)
    except ProjectNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found") from exc
    except McpServerNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="MCP server not found") from exc
    except McpAccessDeniedError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
