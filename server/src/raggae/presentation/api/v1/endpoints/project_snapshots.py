from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from raggae.application.use_cases.project_snapshot.get_project_snapshot import GetProjectSnapshot
from raggae.application.use_cases.project_snapshot.list_project_snapshots import ListProjectSnapshots
from raggae.application.use_cases.project_snapshot.restore_project_snapshot import (
    RestoreProjectSnapshot,
)
from raggae.domain.exceptions.project_exceptions import ProjectNotFoundError
from raggae.domain.exceptions.project_snapshot_exceptions import ProjectSnapshotNotFoundError
from raggae.presentation.api.dependencies import (
    get_current_user_id,
    get_get_project_snapshot_use_case,
    get_list_project_snapshots_use_case,
    get_restore_project_snapshot_use_case,
)
from raggae.presentation.api.v1.schemas.project_schemas import ProjectResponse
from raggae.presentation.api.v1.schemas.project_snapshot_schemas import (
    ProjectSnapshotListResponse,
    ProjectSnapshotResponse,
)

router = APIRouter(
    prefix="/projects/{project_id}/snapshots",
    tags=["project-snapshots"],
    dependencies=[Depends(get_current_user_id)],
)


def _dto_to_response(s: object) -> ProjectSnapshotResponse:
    return ProjectSnapshotResponse.model_validate(s, from_attributes=True)


@router.get("", response_model=ProjectSnapshotListResponse)
async def list_project_snapshots(
    project_id: UUID,
    user_id: Annotated[UUID, Depends(get_current_user_id)],
    use_case: Annotated[ListProjectSnapshots, Depends(get_list_project_snapshots_use_case)],
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> ProjectSnapshotListResponse:
    try:
        snapshot_dtos, total = await use_case.execute(
            project_id=project_id,
            user_id=user_id,
            limit=limit,
            offset=offset,
        )
    except ProjectNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        ) from None

    return ProjectSnapshotListResponse(
        snapshots=[_dto_to_response(s) for s in snapshot_dtos],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/{version_number}", response_model=ProjectSnapshotResponse)
async def get_project_snapshot(
    project_id: UUID,
    version_number: int,
    user_id: Annotated[UUID, Depends(get_current_user_id)],
    use_case: Annotated[GetProjectSnapshot, Depends(get_get_project_snapshot_use_case)],
) -> ProjectSnapshotResponse:
    try:
        snapshot_dto = await use_case.execute(
            project_id=project_id,
            version_number=version_number,
            user_id=user_id,
        )
    except ProjectNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        ) from None
    except ProjectSnapshotNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Snapshot not found",
        ) from None

    return _dto_to_response(snapshot_dto)


@router.post("/{version_number}/restore", status_code=status.HTTP_200_OK)
async def restore_project_snapshot(
    project_id: UUID,
    version_number: int,
    user_id: Annotated[UUID, Depends(get_current_user_id)],
    use_case: Annotated[RestoreProjectSnapshot, Depends(get_restore_project_snapshot_use_case)],
) -> ProjectResponse:
    try:
        project_dto = await use_case.execute(
            project_id=project_id,
            version_number=version_number,
            user_id=user_id,
        )
    except ProjectNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        ) from None
    except ProjectSnapshotNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Snapshot not found",
        ) from None

    return ProjectResponse.from_dto(project_dto)
