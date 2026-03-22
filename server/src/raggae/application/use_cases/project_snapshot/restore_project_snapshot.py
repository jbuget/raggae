from dataclasses import replace
from uuid import UUID

from raggae.application.dto.project_dto import ProjectDTO
from raggae.application.interfaces.repositories.organization_member_repository import (
    OrganizationMemberRepository,
)
from raggae.application.interfaces.repositories.project_repository import ProjectRepository
from raggae.application.interfaces.repositories.project_snapshot_repository import (
    ProjectSnapshotRepository,
)
from raggae.domain.entities.project_snapshot import ProjectSnapshot
from raggae.domain.exceptions.project_exceptions import ProjectNotFoundError
from raggae.domain.exceptions.project_snapshot_exceptions import ProjectSnapshotNotFoundError
from raggae.domain.value_objects.organization_member_role import OrganizationMemberRole


class RestoreProjectSnapshot:
    """Use Case: Restore a project to a previous snapshot version.

    Applies the snapshot's configuration fields to the project and creates
    a new snapshot recording the restore operation.
    """

    def __init__(
        self,
        project_repository: ProjectRepository,
        snapshot_repository: ProjectSnapshotRepository,
        organization_member_repository: OrganizationMemberRepository | None = None,
    ) -> None:
        self._project_repository = project_repository
        self._snapshot_repository = snapshot_repository
        self._organization_member_repository = organization_member_repository

    async def execute(
        self,
        project_id: UUID,
        version_number: int,
        user_id: UUID,
    ) -> ProjectDTO:
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
            if member is None:
                raise ProjectNotFoundError(f"Project {project_id} not found")
            # Restore is a write operation — only OWNER and MAKER are allowed
            if member.role not in {OrganizationMemberRole.OWNER, OrganizationMemberRole.MAKER}:
                raise ProjectNotFoundError(f"Project {project_id} not found")

        snapshot = await self._snapshot_repository.find_by_project_and_version(
            project_id=project_id,
            version_number=version_number,
        )
        if snapshot is None:
            raise ProjectSnapshotNotFoundError(
                f"Snapshot version {version_number} not found for project {project_id}"
            )

        # Apply snapshot fields to the project (exclude transient and encrypted fields)
        restored_project = replace(
            project,
            name=snapshot.name,
            description=snapshot.description,
            system_prompt=snapshot.system_prompt,
            is_published=snapshot.is_published,
            chunking_strategy=snapshot.chunking_strategy,
            parent_child_chunking=snapshot.parent_child_chunking,
            embedding_backend=snapshot.embedding_backend,
            embedding_model=snapshot.embedding_model,
            embedding_api_key_credential_id=snapshot.embedding_api_key_credential_id,
            org_embedding_api_key_credential_id=snapshot.org_embedding_api_key_credential_id,
            llm_backend=snapshot.llm_backend,
            llm_model=snapshot.llm_model,
            llm_api_key_credential_id=snapshot.llm_api_key_credential_id,
            org_llm_api_key_credential_id=snapshot.org_llm_api_key_credential_id,
            retrieval_strategy=snapshot.retrieval_strategy,
            retrieval_top_k=snapshot.retrieval_top_k,
            retrieval_min_score=snapshot.retrieval_min_score,
            chat_history_window_size=snapshot.chat_history_window_size,
            chat_history_max_chars=snapshot.chat_history_max_chars,
            reranking_enabled=snapshot.reranking_enabled,
            reranker_backend=snapshot.reranker_backend,
            reranker_model=snapshot.reranker_model,
            reranker_candidate_multiplier=snapshot.reranker_candidate_multiplier,
        )

        await self._project_repository.save(restored_project)

        # Create a new snapshot recording this restore
        next_version = await self._snapshot_repository.get_next_version_number(project_id)
        restore_snapshot = ProjectSnapshot.from_project(
            project=restored_project,
            version_number=next_version,
            created_by_user_id=user_id,
            restored_from_version=version_number,
        )
        await self._snapshot_repository.save(restore_snapshot)

        return ProjectDTO.from_entity(restored_project)
