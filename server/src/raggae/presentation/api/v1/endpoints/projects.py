from typing import Annotated, Literal, cast
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from raggae.application.use_cases.chat.query_relevant_chunks import QueryRelevantChunks
from raggae.application.use_cases.project.create_project import CreateProject
from raggae.application.use_cases.project.delete_project import DeleteProject
from raggae.application.use_cases.project.get_project import GetProject
from raggae.application.use_cases.project.list_projects import ListProjects
from raggae.application.use_cases.project.reindex_project import ReindexProject
from raggae.application.use_cases.project.update_project import UpdateProject
from raggae.domain.exceptions.project_exceptions import (
    InvalidProjectChatHistoryMaxCharsError,
    InvalidProjectChatHistoryWindowSizeError,
    InvalidProjectRetrievalMinScoreError,
    InvalidProjectRetrievalStrategyError,
    InvalidProjectRetrievalTopKError,
    ProjectAPIKeyNotOwnedError,
    ProjectNotFoundError,
    ProjectReindexInProgressError,
    ProjectSystemPromptTooLongError,
)
from raggae.presentation.api.dependencies import (
    get_create_project_use_case,
    get_current_user_id,
    get_delete_project_use_case,
    get_get_project_use_case,
    get_list_projects_use_case,
    get_query_relevant_chunks_use_case,
    get_reindex_project_use_case,
    get_update_project_use_case,
)
from raggae.presentation.api.v1.schemas.project_schemas import (
    CreateProjectRequest,
    ProjectResponse,
    ReindexProjectResponse,
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

ProjectRetrievalStrategy = Literal["vector", "fulltext", "hybrid"]


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_project(
    user_id: Annotated[UUID, Depends(get_current_user_id)],
    data: CreateProjectRequest,
    use_case: Annotated[CreateProject, Depends(get_create_project_use_case)],
) -> ProjectResponse:
    try:
        project_dto = await use_case.execute(
            user_id=user_id,
            name=data.name,
            description=data.description,
            system_prompt=data.system_prompt,
            chunking_strategy=data.chunking_strategy,
            parent_child_chunking=data.parent_child_chunking,
            embedding_backend=data.embedding_backend,
            embedding_model=data.embedding_model,
            embedding_api_key=data.embedding_api_key,
            embedding_api_key_credential_id=data.embedding_api_key_credential_id,
            llm_backend=data.llm_backend,
            llm_model=data.llm_model,
            llm_api_key=data.llm_api_key,
            llm_api_key_credential_id=data.llm_api_key_credential_id,
            retrieval_strategy=data.retrieval_strategy,
            retrieval_top_k=data.retrieval_top_k,
            retrieval_min_score=data.retrieval_min_score,
            chat_history_window_size=data.chat_history_window_size,
            chat_history_max_chars=data.chat_history_max_chars,
        )
    except ProjectSystemPromptTooLongError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(exc),
        ) from None
    except ProjectAPIKeyNotOwnedError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(exc),
        ) from None
    except InvalidProjectRetrievalStrategyError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(exc),
        ) from None
    except InvalidProjectRetrievalTopKError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(exc),
        ) from None
    except InvalidProjectRetrievalMinScoreError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(exc),
        ) from None
    except InvalidProjectChatHistoryWindowSizeError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(exc),
        ) from None
    except InvalidProjectChatHistoryMaxCharsError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(exc),
        ) from None
    return ProjectResponse(
        id=project_dto.id,
        user_id=project_dto.user_id,
        name=project_dto.name,
        description=project_dto.description,
        system_prompt=project_dto.system_prompt,
        is_published=project_dto.is_published,
        created_at=project_dto.created_at,
        chunking_strategy=project_dto.chunking_strategy,
        parent_child_chunking=project_dto.parent_child_chunking,
        reindex_status=project_dto.reindex_status,
        reindex_progress=project_dto.reindex_progress,
        reindex_total=project_dto.reindex_total,
        embedding_backend=project_dto.embedding_backend,
        embedding_model=project_dto.embedding_model,
        embedding_api_key_masked=project_dto.embedding_api_key_masked,
        embedding_api_key_credential_id=project_dto.embedding_api_key_credential_id,
        llm_backend=project_dto.llm_backend,
        llm_model=project_dto.llm_model,
        llm_api_key_masked=project_dto.llm_api_key_masked,
        llm_api_key_credential_id=project_dto.llm_api_key_credential_id,
        retrieval_strategy=cast(ProjectRetrievalStrategy, project_dto.retrieval_strategy),
        retrieval_top_k=project_dto.retrieval_top_k,
        retrieval_min_score=project_dto.retrieval_min_score,
        chat_history_window_size=project_dto.chat_history_window_size,
        chat_history_max_chars=project_dto.chat_history_max_chars,
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
        chunking_strategy=project_dto.chunking_strategy,
        parent_child_chunking=project_dto.parent_child_chunking,
        reindex_status=project_dto.reindex_status,
        reindex_progress=project_dto.reindex_progress,
        reindex_total=project_dto.reindex_total,
        embedding_backend=project_dto.embedding_backend,
        embedding_model=project_dto.embedding_model,
        embedding_api_key_masked=project_dto.embedding_api_key_masked,
        embedding_api_key_credential_id=project_dto.embedding_api_key_credential_id,
        llm_backend=project_dto.llm_backend,
        llm_model=project_dto.llm_model,
        llm_api_key_masked=project_dto.llm_api_key_masked,
        llm_api_key_credential_id=project_dto.llm_api_key_credential_id,
        retrieval_strategy=cast(ProjectRetrievalStrategy, project_dto.retrieval_strategy),
        retrieval_top_k=project_dto.retrieval_top_k,
        retrieval_min_score=project_dto.retrieval_min_score,
        chat_history_window_size=project_dto.chat_history_window_size,
        chat_history_max_chars=project_dto.chat_history_max_chars,
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
            chunking_strategy=p.chunking_strategy,
            parent_child_chunking=p.parent_child_chunking,
            reindex_status=p.reindex_status,
            reindex_progress=p.reindex_progress,
            reindex_total=p.reindex_total,
            embedding_backend=p.embedding_backend,
            embedding_model=p.embedding_model,
            embedding_api_key_masked=p.embedding_api_key_masked,
            embedding_api_key_credential_id=p.embedding_api_key_credential_id,
            llm_backend=p.llm_backend,
            llm_model=p.llm_model,
            llm_api_key_masked=p.llm_api_key_masked,
            llm_api_key_credential_id=p.llm_api_key_credential_id,
            retrieval_strategy=cast(ProjectRetrievalStrategy, p.retrieval_strategy),
            retrieval_top_k=p.retrieval_top_k,
            retrieval_min_score=p.retrieval_min_score,
            chat_history_window_size=p.chat_history_window_size,
            chat_history_max_chars=p.chat_history_max_chars,
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
            chunking_strategy=data.chunking_strategy,
            parent_child_chunking=data.parent_child_chunking,
            embedding_backend=data.embedding_backend,
            embedding_model=data.embedding_model,
            embedding_api_key=data.embedding_api_key,
            embedding_api_key_credential_id=data.embedding_api_key_credential_id,
            llm_backend=data.llm_backend,
            llm_model=data.llm_model,
            llm_api_key=data.llm_api_key,
            llm_api_key_credential_id=data.llm_api_key_credential_id,
            retrieval_strategy=data.retrieval_strategy,
            retrieval_top_k=data.retrieval_top_k,
            retrieval_min_score=data.retrieval_min_score,
            chat_history_window_size=data.chat_history_window_size,
            chat_history_max_chars=data.chat_history_max_chars,
        )
    except ProjectNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        ) from None
    except ProjectSystemPromptTooLongError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(exc),
        ) from None
    except ProjectAPIKeyNotOwnedError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(exc),
        ) from None
    except InvalidProjectRetrievalStrategyError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(exc),
        ) from None
    except InvalidProjectRetrievalTopKError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(exc),
        ) from None
    except InvalidProjectRetrievalMinScoreError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(exc),
        ) from None
    except InvalidProjectChatHistoryWindowSizeError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(exc),
        ) from None
    except InvalidProjectChatHistoryMaxCharsError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(exc),
        ) from None
    return ProjectResponse(
        id=project_dto.id,
        user_id=project_dto.user_id,
        name=project_dto.name,
        description=project_dto.description,
        system_prompt=project_dto.system_prompt,
        is_published=project_dto.is_published,
        created_at=project_dto.created_at,
        chunking_strategy=project_dto.chunking_strategy,
        parent_child_chunking=project_dto.parent_child_chunking,
        reindex_status=project_dto.reindex_status,
        reindex_progress=project_dto.reindex_progress,
        reindex_total=project_dto.reindex_total,
        embedding_backend=project_dto.embedding_backend,
        embedding_model=project_dto.embedding_model,
        embedding_api_key_masked=project_dto.embedding_api_key_masked,
        embedding_api_key_credential_id=project_dto.embedding_api_key_credential_id,
        llm_backend=project_dto.llm_backend,
        llm_model=project_dto.llm_model,
        llm_api_key_masked=project_dto.llm_api_key_masked,
        llm_api_key_credential_id=project_dto.llm_api_key_credential_id,
        retrieval_strategy=cast(ProjectRetrievalStrategy, project_dto.retrieval_strategy),
        retrieval_top_k=project_dto.retrieval_top_k,
        retrieval_min_score=project_dto.retrieval_min_score,
        chat_history_window_size=project_dto.chat_history_window_size,
        chat_history_max_chars=project_dto.chat_history_max_chars,
    )


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
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        ) from None

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
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        ) from None
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
