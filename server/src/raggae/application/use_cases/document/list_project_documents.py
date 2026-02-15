from uuid import UUID

from raggae.application.dto.document_dto import DocumentDTO
from raggae.application.interfaces.repositories.document_repository import DocumentRepository
from raggae.application.interfaces.repositories.project_repository import ProjectRepository
from raggae.domain.exceptions.project_exceptions import ProjectNotFoundError


class ListProjectDocuments:
    """Use Case: List documents attached to a project."""

    def __init__(
        self,
        document_repository: DocumentRepository,
        project_repository: ProjectRepository,
    ) -> None:
        self._document_repository = document_repository
        self._project_repository = project_repository

    async def execute(self, project_id: UUID, user_id: UUID) -> list[DocumentDTO]:
        project = await self._project_repository.find_by_id(project_id)
        if project is None or project.user_id != user_id:
            raise ProjectNotFoundError(f"Project {project_id} not found")

        documents = await self._document_repository.find_by_project_id(project_id)
        return [DocumentDTO.from_entity(document) for document in documents]
