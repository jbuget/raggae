from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from raggae.application.use_cases.document.delete_document import DeleteDocument
from raggae.application.use_cases.document.list_document_chunks import ListDocumentChunks
from raggae.application.use_cases.document.list_project_documents import ListProjectDocuments
from raggae.application.use_cases.document.upload_document import UploadDocument
from raggae.domain.exceptions.document_exceptions import (
    DocumentExtractionError,
    DocumentNotFoundError,
    DocumentTooLargeError,
    EmbeddingGenerationError,
    InvalidDocumentTypeError,
)
from raggae.domain.exceptions.project_exceptions import ProjectNotFoundError
from raggae.presentation.api.dependencies import (
    get_current_user_id,
    get_delete_document_use_case,
    get_list_document_chunks_use_case,
    get_list_project_documents_use_case,
    get_upload_document_use_case,
)
from raggae.presentation.api.v1.schemas.document_schemas import (
    DocumentChunkResponse,
    DocumentChunksResponse,
    DocumentResponse,
)

router = APIRouter(
    prefix="/projects/{project_id}/documents",
    tags=["documents"],
    dependencies=[Depends(get_current_user_id)],
)


@router.post("", status_code=status.HTTP_201_CREATED)
async def upload_document(
    project_id: UUID,
    file: Annotated[UploadFile, File(...)],
    user_id: Annotated[UUID, Depends(get_current_user_id)],
    use_case: Annotated[UploadDocument, Depends(get_upload_document_use_case)],
) -> DocumentResponse:
    try:
        file_content = await file.read()
        document_dto = await use_case.execute(
            project_id=project_id,
            user_id=user_id,
            file_name=file.filename or "file",
            file_content=file_content,
            content_type=file.content_type or "application/octet-stream",
        )
    except ProjectNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        ) from None
    except InvalidDocumentTypeError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from None
    except DocumentTooLargeError:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Document exceeds maximum allowed size",
        ) from None
    except DocumentExtractionError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(exc),
        ) from None
    except EmbeddingGenerationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(exc),
        ) from None

    return DocumentResponse(
        id=document_dto.id,
        project_id=document_dto.project_id,
        file_name=document_dto.file_name,
        content_type=document_dto.content_type,
        file_size=document_dto.file_size,
        created_at=document_dto.created_at,
        processing_strategy=document_dto.processing_strategy,
    )


@router.get("")
async def list_project_documents(
    project_id: UUID,
    user_id: Annotated[UUID, Depends(get_current_user_id)],
    use_case: Annotated[ListProjectDocuments, Depends(get_list_project_documents_use_case)],
) -> list[DocumentResponse]:
    try:
        document_dtos = await use_case.execute(project_id=project_id, user_id=user_id)
    except ProjectNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        ) from None

    return [
        DocumentResponse(
            id=doc.id,
            project_id=doc.project_id,
            file_name=doc.file_name,
            content_type=doc.content_type,
            file_size=doc.file_size,
            created_at=doc.created_at,
            processing_strategy=doc.processing_strategy,
        )
        for doc in document_dtos
    ]


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    project_id: UUID,
    document_id: UUID,
    user_id: Annotated[UUID, Depends(get_current_user_id)],
    use_case: Annotated[DeleteDocument, Depends(get_delete_document_use_case)],
) -> None:
    try:
        await use_case.execute(
            project_id=project_id,
            document_id=document_id,
            user_id=user_id,
        )
    except ProjectNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        ) from None
    except DocumentNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        ) from None


@router.get("/{document_id}/chunks")
async def list_document_chunks(
    project_id: UUID,
    document_id: UUID,
    user_id: Annotated[UUID, Depends(get_current_user_id)],
    use_case: Annotated[ListDocumentChunks, Depends(get_list_document_chunks_use_case)],
) -> DocumentChunksResponse:
    try:
        chunks_dto = await use_case.execute(
            project_id=project_id,
            document_id=document_id,
            user_id=user_id,
        )
    except ProjectNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        ) from None
    except DocumentNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        ) from None

    return DocumentChunksResponse(
        document_id=chunks_dto.document_id,
        processing_strategy=chunks_dto.processing_strategy,
        chunks=[
            DocumentChunkResponse(
                id=chunk.id,
                document_id=chunk.document_id,
                chunk_index=chunk.chunk_index,
                content=chunk.content,
                created_at=chunk.created_at,
                metadata_json=chunk.metadata_json,
            )
            for chunk in chunks_dto.chunks
        ],
    )
