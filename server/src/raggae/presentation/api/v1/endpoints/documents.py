import urllib.parse
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import Response

from raggae.application.use_cases.document.delete_document import DeleteDocument
from raggae.application.use_cases.document.get_document_file import GetDocumentFile
from raggae.application.use_cases.document.list_document_chunks import ListDocumentChunks
from raggae.application.use_cases.document.list_project_documents import ListProjectDocuments
from raggae.application.use_cases.document.upload_document import (
    UploadDocument,
    UploadDocumentItem,
)
from raggae.domain.exceptions.document_exceptions import (
    DocumentNotFoundError,
)
from raggae.domain.exceptions.project_exceptions import ProjectNotFoundError
from raggae.presentation.api.dependencies import (
    get_current_user_id,
    get_delete_document_use_case,
    get_get_document_file_use_case,
    get_list_document_chunks_use_case,
    get_list_project_documents_use_case,
    get_upload_document_use_case,
)
from raggae.presentation.api.v1.schemas.document_schemas import (
    DocumentChunkResponse,
    DocumentChunksResponse,
    DocumentResponse,
    UploadDocumentsResponse,
)

router = APIRouter(
    prefix="/projects/{project_id}/documents",
    tags=["documents"],
    dependencies=[Depends(get_current_user_id)],
)


MAX_UPLOAD_FILES_PER_REQUEST = 10


@router.post("", status_code=status.HTTP_200_OK)
async def upload_document(
    project_id: UUID,
    files: Annotated[list[UploadFile], File(...)],
    user_id: Annotated[UUID, Depends(get_current_user_id)],
    use_case: Annotated[UploadDocument, Depends(get_upload_document_use_case)],
) -> UploadDocumentsResponse:
    if not files:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one file is required",
        )
    if len(files) > MAX_UPLOAD_FILES_PER_REQUEST:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Maximum {MAX_UPLOAD_FILES_PER_REQUEST} files are allowed per request",
        )

    try:
        upload_items = []
        for upload in files:
            upload_items.append(
                UploadDocumentItem(
                    file_name=upload.filename or "file",
                    file_content=await upload.read(),
                    content_type=upload.content_type or "application/octet-stream",
                )
            )
        result = await use_case.execute_many(
            project_id=project_id,
            user_id=user_id,
            files=upload_items,
        )
    except ProjectNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        ) from None

    return UploadDocumentsResponse(
        total=result.total,
        succeeded=result.succeeded,
        failed=result.failed,
        created=[
            {
                "original_filename": item.original_filename,
                "stored_filename": item.stored_filename,
                "document_id": item.document_id,
            }
            for item in result.created
        ],
        errors=[
            {
                "filename": error.filename,
                "code": error.code,
                "message": error.message,
            }
            for error in result.errors
        ],
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


@router.get("/{document_id}/file")
async def get_document_file(
    project_id: UUID,
    document_id: UUID,
    user_id: Annotated[UUID, Depends(get_current_user_id)],
    use_case: Annotated[GetDocumentFile, Depends(get_get_document_file_use_case)],
) -> Response:
    try:
        document_file = await use_case.execute(
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

    ascii_name = document_file.file_name.encode("ascii", errors="replace").decode("ascii")
    utf8_name = urllib.parse.quote(document_file.file_name)
    return Response(
        content=document_file.content,
        media_type=document_file.content_type,
        headers={
            "Content-Disposition": (
                f'inline; filename="{ascii_name}"; filename*=UTF-8\'\'{utf8_name}'
            ),
        },
    )
