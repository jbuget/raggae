from uuid import UUID

from raggae.application.dto.document_dto import DocumentDTO
from raggae.application.interfaces.repositories.document_repository import DocumentRepository
from raggae.application.interfaces.repositories.organization_member_repository import (
    OrganizationMemberRepository,
)
from raggae.application.interfaces.repositories.project_repository import ProjectRepository
from raggae.domain.exceptions.project_exceptions import ProjectNotFoundError
from raggae.domain.value_objects.organization_member_role import OrganizationMemberRole


class ListProjectDocuments:
    """Use Case: List documents attached to a project."""

    def __init__(
        self,
        document_repository: DocumentRepository,
        project_repository: ProjectRepository,
        organization_member_repository: OrganizationMemberRepository | None = None,
    ) -> None:
        self._document_repository = document_repository
        self._project_repository = project_repository
        self._organization_member_repository = organization_member_repository

    async def execute(self, project_id: UUID, user_id: UUID) -> list[DocumentDTO]:
        project = await self._project_repository.find_by_id(project_id)
        if project is None:
            raise ProjectNotFoundError(f"Project {project_id} not found")
        if project.user_id != user_id:
            if project.organization_id is None or self._organization_member_repository is None:
                raise ProjectNotFoundError(f"Project {project_id} not found")
            member = await self._organization_member_repository.find_by_organization_and_user(
                organization_id=project.organization_id,
                user_id=user_id,
            )
            if member is None or member.role not in {
                OrganizationMemberRole.OWNER,
                OrganizationMemberRole.MAKER,
            }:
                raise ProjectNotFoundError(f"Project {project_id} not found")

        documents = await self._document_repository.find_by_project_id(project_id)
        return [DocumentDTO.from_entity(document) for document in documents]
