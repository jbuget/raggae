from dataclasses import dataclass
from uuid import UUID

from raggae.application.dto.project_dto import ProjectDTO


@dataclass
class OrganizationSectionDTO:
    """Section de projets d'une organisation avec les droits d'édition de l'utilisateur."""

    organization_id: UUID
    organization_name: str
    projects: list[ProjectDTO]
    can_edit: bool


@dataclass
class AccessibleProjectsDTO:
    """Ensemble des projets accessibles à un utilisateur, regroupés par origine."""

    personal_projects: list[ProjectDTO]
    organization_sections: list[OrganizationSectionDTO]
