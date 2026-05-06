from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from raggae.application.use_cases.chat.query_relevant_chunks import QueryRelevantChunks
from raggae.application.use_cases.project.create_project import CreateProject
from raggae.application.use_cases.project.delete_project import DeleteProject
from raggae.application.use_cases.project.get_project import GetProject
from raggae.application.use_cases.project.get_project_configuration import GetProjectConfiguration
from raggae.application.use_cases.project.list_accessible_projects import ListAccessibleProjects
from raggae.application.use_cases.project.list_projects import ListProjects
from raggae.application.use_cases.project.publish_project import PublishProject
from raggae.application.use_cases.project.reindex_project import ReindexProject
from raggae.application.use_cases.project.unpublish_project import UnpublishProject
from raggae.application.use_cases.project.update_project import UpdateProject
from raggae.application.use_cases.project.update_project_configuration import UpdateProjectConfiguration
from raggae.domain.exceptions.organization_exceptions import OrganizationAccessDeniedError
from raggae.domain.exceptions.project_exceptions import (
    InvalidProjectEmbeddingBackendError,
    InvalidProjectLLMBackendError,
    InvalidProjectRerankerBackendError,
    InvalidProjectRetrievalStrategyError,
    ProjectAlreadyPublishedError,
    ProjectNotFoundError,
    ProjectNotPublishedError,
    ProjectReindexInProgressError,
    ProjectSystemPromptTooLongError,
)
from raggae.presentation.api.dependencies import (
    get_create_project_use_case,
    get_current_user_id,
    get_delete_project_use_case,
    get_get_project_configuration_use_case,
    get_get_project_use_case,
    get_list_accessible_projects_use_case,
    get_list_projects_use_case,
    get_publish_project_use_case,
    get_query_relevant_chunks_use_case,
    get_reindex_project_use_case,
    get_unpublish_project_use_case,
    get_update_project_configuration_use_case,
    get_update_project_use_case,
)
from raggae.presentation.api.v1.schemas.project_schemas import (
    AccessibleProjectsResponse,
    AgentConfigurationResponse,
    CreateProjectRequest,
    OrganizationSectionResponse,
    ProjectResponse,
    ReindexProjectResponse,
    UpdateAgentConfigurationRequest,
    UpdateProjectRequest,
)
from raggae.presentation.api.v1.schemas.query_schemas import (
    QueryProjectRequest,
    QueryProjectResponse,
    RetrievedChunkResponse,
)

router = APIRouter(
    prefix="/projects",
    tags=["projects"],
    dependencies=[Depends(get_current_user_id)],
)


def _config_error_handler(exc: Exception) -> None:
    raise HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail=str(exc),
    ) from None


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_project(
    user_id: Annotated[UUID, Depends(get_current_user_id)],
    data: CreateProjectRequest,
    use_case: Annotated[CreateProject, Depends(get_create_project_use_case)],
) -> ProjectResponse:
    try:
        project_dto = await use_case.execute(
            user_id=user_id,
            organization_id=data.organization_id,
            name=data.name,
            description=data.description,
            system_prompt=data.system_prompt,
        )
    except ProjectSystemPromptTooLongError as exc:
        _config_error_handler(exc)
    except OrganizationAccessDeniedError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from None
    return ProjectResponse.from_dto(project_dto)


@router.get("/accessible")
async def list_accessible_projects(
    user_id: Annotated[UUID, Depends(get_current_user_id)],
    use_case: Annotated[ListAccessibleProjects, Depends(get_list_accessible_projects_use_case)],
) -> AccessibleProjectsResponse:
    result = await use_case.execute(user_id=user_id)
    return AccessibleProjectsResponse(
        personal_projects=[ProjectResponse.from_dto(p) for p in result.personal_projects],
        organization_sections=[
            OrganizationSectionResponse(
                organization_id=section.organization_id,
                organization_name=section.organization_name,
                projects=[ProjectResponse.from_dto(p) for p in section.projects],
                can_edit=section.can_edit,
            )
            for section in result.organization_sections
        ],
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
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found") from None
    return ProjectResponse.from_dto(project_dto)


@router.get("")
async def list_projects(
    user_id: Annotated[UUID, Depends(get_current_user_id)],
    use_case: Annotated[ListProjects, Depends(get_list_projects_use_case)],
) -> list[ProjectResponse]:
    project_dtos = await use_case.execute(user_id=user_id)
    return [ProjectResponse.from_dto(p) for p in project_dtos]


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: UUID,
    user_id: Annotated[UUID, Depends(get_current_user_id)],
    use_case: Annotated[DeleteProject, Depends(get_delete_project_use_case)],
) -> None:
    try:
        await use_case.execute(project_id=project_id, user_id=user_id)
    except ProjectNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found") from None


@router.patch("/{project_id}")
async def update_project(
    project_id: UUID,
    data: UpdateProjectRequest,
    user_id: Annotated[UUID, Depends(get_current_user_id)],
    use_case: Annotated[UpdateProject, Depends(get_update_project_use_case)],
) -> ProjectResponse:
    try:
        project_dto = await use_case.execute(
            project_id=project_id,
            user_id=user_id,
            name=data.name,
            description=data.description,
            system_prompt=data.system_prompt,
        )
    except ProjectNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found") from None
    except ProjectSystemPromptTooLongError as exc:
        _config_error_handler(exc)
    return ProjectResponse.from_dto(project_dto)


@router.get("/{project_id}/configuration")
async def get_project_configuration(
    project_id: UUID,
    user_id: Annotated[UUID, Depends(get_current_user_id)],
    use_case: Annotated[GetProjectConfiguration, Depends(get_get_project_configuration_use_case)],
) -> AgentConfigurationResponse | None:
    try:
        result = await use_case.execute(project_id=project_id, user_id=user_id)
    except ProjectNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found") from None
    if result is None:
        return None
    return AgentConfigurationResponse.from_dto(result)


@router.put("/{project_id}/configuration")
async def update_project_configuration(
    project_id: UUID,
    data: UpdateAgentConfigurationRequest,
    user_id: Annotated[UUID, Depends(get_current_user_id)],
    use_case: Annotated[UpdateProjectConfiguration, Depends(get_update_project_configuration_use_case)],
) -> AgentConfigurationResponse:
    try:
        result = await use_case.execute(
            project_id=project_id,
            user_id=user_id,
            **data.model_dump(),
        )
    except ProjectNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found") from None
    except (
        InvalidProjectEmbeddingBackendError,
        InvalidProjectLLMBackendError,
        InvalidProjectRetrievalStrategyError,
        InvalidProjectRerankerBackendError,
    ) as exc:
        _config_error_handler(exc)
    return AgentConfigurationResponse.from_dto(result)


@router.post("/{project_id}/query")
async def query_project_chunks(
    project_id: UUID,
    data: QueryProjectRequest,
    user_id: Annotated[UUID, Depends(get_current_user_id)],
    use_case: Annotated[QueryRelevantChunks, Depends(get_query_relevant_chunks_use_case)],
) -> QueryProjectResponse:
    try:
        result = await use_case.execute(
            project_id=project_id,
            user_id=user_id,
            query=data.query,
            limit=data.limit,
        )
    except ProjectNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found") from None

    return QueryProjectResponse(
        project_id=project_id,
        query=data.query,
        chunks=[
            RetrievedChunkResponse(
                chunk_id=chunk.chunk_id,
                document_id=chunk.document_id,
                document_file_name=chunk.document_file_name,
                content=chunk.content,
                score=chunk.score,
                vector_score=chunk.vector_score,
                fulltext_score=chunk.fulltext_score,
            )
            for chunk in result.chunks
        ],
    )


@router.post("/{project_id}/reindex", status_code=status.HTTP_200_OK)
async def reindex_project(
    project_id: UUID,
    user_id: Annotated[UUID, Depends(get_current_user_id)],
    use_case: Annotated[ReindexProject, Depends(get_reindex_project_use_case)],
) -> ReindexProjectResponse:
    try:
        result = await use_case.execute(project_id=project_id, user_id=user_id)
    except ProjectNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found") from None
    except ProjectReindexInProgressError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Project reindex already in progress",
        ) from None

    return ReindexProjectResponse(
        project_id=result.project_id,
        total_documents=result.total_documents,
        indexed_documents=result.indexed_documents,
        failed_documents=result.failed_documents,
    )


@router.post("/{project_id}/publish", status_code=status.HTTP_200_OK)
async def publish_project(
    project_id: UUID,
    user_id: Annotated[UUID, Depends(get_current_user_id)],
    use_case: Annotated[PublishProject, Depends(get_publish_project_use_case)],
) -> ProjectResponse:
    try:
        project_dto = await use_case.execute(project_id=project_id, user_id=user_id)
    except ProjectNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found") from None
    except ProjectAlreadyPublishedError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Project is already published") from None
    return ProjectResponse.from_dto(project_dto)


@router.post("/{project_id}/unpublish", status_code=status.HTTP_200_OK)
async def unpublish_project(
    project_id: UUID,
    user_id: Annotated[UUID, Depends(get_current_user_id)],
    use_case: Annotated[UnpublishProject, Depends(get_unpublish_project_use_case)],
) -> ProjectResponse:
    try:
        project_dto = await use_case.execute(project_id=project_id, user_id=user_id)
    except ProjectNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found") from None
    except ProjectNotPublishedError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Project is not published") from None
    return ProjectResponse.from_dto(project_dto)
