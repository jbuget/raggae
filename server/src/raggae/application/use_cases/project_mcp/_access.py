"""Shared project-access checks for project_mcp use cases."""

from uuid import UUID

from raggae.application.interfaces.repositories.organization_member_repository import (
    OrganizationMemberRepository,
)
from raggae.application.interfaces.repositories.project_repository import ProjectRepository
from raggae.domain.entities.project import Project
from raggae.domain.exceptions.project_exceptions import ProjectNotFoundError


async def load_project_for_user(
    *,
    project_id: UUID,
    user_id: UUID,
    project_repository: ProjectRepository,
    organization_member_repository: OrganizationMemberRepository,
) -> Project:
    """Load a project and ensure the user can access it.

    Access rules (V1, MCP activations):
    - The user is the owner of a user-owned project, or
    - The project is org-owned and the user is a member of that organization (any role).

    Raises `ProjectNotFoundError` to avoid leaking the existence of inaccessible projects.
    """
    project = await project_repository.find_by_id(project_id)
    if project is None:
        raise ProjectNotFoundError(f"Project {project_id} not found")
    if project.user_id == user_id:
        return project
    if project.organization_id is None:
        raise ProjectNotFoundError(f"Project {project_id} not found")
    member = await organization_member_repository.find_by_organization_and_user(
        organization_id=project.organization_id,
        user_id=user_id,
    )
    if member is None:
        raise ProjectNotFoundError(f"Project {project_id} not found")
    return project
