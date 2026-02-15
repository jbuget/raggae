from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from raggae.application.use_cases.project.create_project import CreateProject
from raggae.application.use_cases.project.delete_project import DeleteProject
from raggae.application.use_cases.project.get_project import GetProject
from raggae.application.use_cases.project.list_projects import ListProjects
from raggae.domain.exceptions.project_exceptions import ProjectNotFoundError
from raggae.presentation.api.dependencies import (
    get_create_project_use_case,
    get_current_user_id,
    get_delete_project_use_case,
    get_get_project_use_case,
    get_list_projects_use_case,
)
from raggae.presentation.api.v1.schemas.project_schemas import (
    CreateProjectRequest,
    ProjectResponse,
)

router = APIRouter(
    prefix="/projects",
    tags=["projects"],
    dependencies=[Depends(get_current_user_id)],
)


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_project(
    user_id: Annotated[UUID, Depends(get_current_user_id)],
    data: CreateProjectRequest,
    use_case: Annotated[CreateProject, Depends(get_create_project_use_case)],
) -> ProjectResponse:
    project_dto = await use_case.execute(
        user_id=user_id,
        name=data.name,
        description=data.description,
        system_prompt=data.system_prompt,
    )
    return ProjectResponse(
        id=project_dto.id,
        user_id=project_dto.user_id,
        name=project_dto.name,
        description=project_dto.description,
        system_prompt=project_dto.system_prompt,
        is_published=project_dto.is_published,
        created_at=project_dto.created_at,
    )


@router.get("/{project_id}")
async def get_project(
    project_id: UUID,
    user_id: Annotated[UUID, Depends(get_current_user_id)],
    use_case: Annotated[GetProject, Depends(get_get_project_use_case)],
) -> ProjectResponse:
    try:
        project_dto = await use_case.execute(project_id=project_id, user_id=user_id)
    except ProjectNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        ) from None
    return ProjectResponse(
        id=project_dto.id,
        user_id=project_dto.user_id,
        name=project_dto.name,
        description=project_dto.description,
        system_prompt=project_dto.system_prompt,
        is_published=project_dto.is_published,
        created_at=project_dto.created_at,
    )


@router.get("")
async def list_projects(
    user_id: Annotated[UUID, Depends(get_current_user_id)],
    use_case: Annotated[ListProjects, Depends(get_list_projects_use_case)],
) -> list[ProjectResponse]:
    project_dtos = await use_case.execute(user_id=user_id)
    return [
        ProjectResponse(
            id=p.id,
            user_id=p.user_id,
            name=p.name,
            description=p.description,
            system_prompt=p.system_prompt,
            is_published=p.is_published,
            created_at=p.created_at,
        )
        for p in project_dtos
    ]


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: UUID,
    user_id: Annotated[UUID, Depends(get_current_user_id)],
    use_case: Annotated[DeleteProject, Depends(get_delete_project_use_case)],
) -> None:
    try:
        await use_case.execute(project_id=project_id, user_id=user_id)
    except ProjectNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        ) from None
