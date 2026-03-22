from typing import Annotated, Literal, cast
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

ProjectRetrievalStrategy = Literal["vector", "fulltext", "hybrid"]
ProjectRerankerBackend = Literal["none", "cross_encoder", "inmemory", "mmr"]


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

    snapshots = [
        ProjectSnapshotResponse(
            id=s.id,
            project_id=s.project_id,
            version_number=s.version_number,
            label=s.label,
            created_at=s.created_at,
            created_by_user_id=s.created_by_user_id,
            name=s.name,
            description=s.description,
            system_prompt=s.system_prompt,
            is_published=s.is_published,
            chunking_strategy=s.chunking_strategy,
            parent_child_chunking=s.parent_child_chunking,
            organization_id=s.organization_id,
            embedding_backend=s.embedding_backend,
            embedding_model=s.embedding_model,
            embedding_api_key_credential_id=s.embedding_api_key_credential_id,
            org_embedding_api_key_credential_id=s.org_embedding_api_key_credential_id,
            llm_backend=s.llm_backend,
            llm_model=s.llm_model,
            llm_api_key_credential_id=s.llm_api_key_credential_id,
            org_llm_api_key_credential_id=s.org_llm_api_key_credential_id,
            retrieval_strategy=cast(ProjectRetrievalStrategy, s.retrieval_strategy),
            retrieval_top_k=s.retrieval_top_k,
            retrieval_min_score=s.retrieval_min_score,
            chat_history_window_size=s.chat_history_window_size,
            chat_history_max_chars=s.chat_history_max_chars,
            reranking_enabled=s.reranking_enabled,
            reranker_backend=cast(ProjectRerankerBackend | None, s.reranker_backend),
            reranker_model=s.reranker_model,
            reranker_candidate_multiplier=s.reranker_candidate_multiplier,
            restored_from_version=s.restored_from_version,
        )
        for s in snapshot_dtos
    ]

    return ProjectSnapshotListResponse(
        snapshots=snapshots,
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

    return ProjectSnapshotResponse(
        id=snapshot_dto.id,
        project_id=snapshot_dto.project_id,
        version_number=snapshot_dto.version_number,
        label=snapshot_dto.label,
        created_at=snapshot_dto.created_at,
        created_by_user_id=snapshot_dto.created_by_user_id,
        name=snapshot_dto.name,
        description=snapshot_dto.description,
        system_prompt=snapshot_dto.system_prompt,
        is_published=snapshot_dto.is_published,
        chunking_strategy=snapshot_dto.chunking_strategy,
        parent_child_chunking=snapshot_dto.parent_child_chunking,
        organization_id=snapshot_dto.organization_id,
        embedding_backend=snapshot_dto.embedding_backend,
        embedding_model=snapshot_dto.embedding_model,
        embedding_api_key_credential_id=snapshot_dto.embedding_api_key_credential_id,
        org_embedding_api_key_credential_id=snapshot_dto.org_embedding_api_key_credential_id,
        llm_backend=snapshot_dto.llm_backend,
        llm_model=snapshot_dto.llm_model,
        llm_api_key_credential_id=snapshot_dto.llm_api_key_credential_id,
        org_llm_api_key_credential_id=snapshot_dto.org_llm_api_key_credential_id,
        retrieval_strategy=cast(ProjectRetrievalStrategy, snapshot_dto.retrieval_strategy),
        retrieval_top_k=snapshot_dto.retrieval_top_k,
        retrieval_min_score=snapshot_dto.retrieval_min_score,
        chat_history_window_size=snapshot_dto.chat_history_window_size,
        chat_history_max_chars=snapshot_dto.chat_history_max_chars,
        reranking_enabled=snapshot_dto.reranking_enabled,
        reranker_backend=cast(ProjectRerankerBackend | None, snapshot_dto.reranker_backend),
        reranker_model=snapshot_dto.reranker_model,
        reranker_candidate_multiplier=snapshot_dto.reranker_candidate_multiplier,
        restored_from_version=snapshot_dto.restored_from_version,
    )


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

    return ProjectResponse(
        id=project_dto.id,
        user_id=project_dto.user_id,
        organization_id=project_dto.organization_id,
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
        org_embedding_api_key_credential_id=project_dto.org_embedding_api_key_credential_id,
        llm_backend=project_dto.llm_backend,
        llm_model=project_dto.llm_model,
        llm_api_key_masked=project_dto.llm_api_key_masked,
        llm_api_key_credential_id=project_dto.llm_api_key_credential_id,
        org_llm_api_key_credential_id=project_dto.org_llm_api_key_credential_id,
        retrieval_strategy=cast(ProjectRetrievalStrategy, project_dto.retrieval_strategy),
        retrieval_top_k=project_dto.retrieval_top_k,
        retrieval_min_score=project_dto.retrieval_min_score,
        chat_history_window_size=project_dto.chat_history_window_size,
        chat_history_max_chars=project_dto.chat_history_max_chars,
        reranking_enabled=project_dto.reranking_enabled,
        reranker_backend=cast(ProjectRerankerBackend | None, project_dto.reranker_backend),
        reranker_model=project_dto.reranker_model,
        reranker_candidate_multiplier=project_dto.reranker_candidate_multiplier,
    )
