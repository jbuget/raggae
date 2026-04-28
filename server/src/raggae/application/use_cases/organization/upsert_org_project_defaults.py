from dataclasses import replace
from uuid import UUID

from raggae.application.dto.org_project_defaults_dto import OrgProjectDefaultsDTO
from raggae.application.interfaces.repositories.org_project_defaults_repository import (
    OrgProjectDefaultsRepository,
)
from raggae.application.interfaces.repositories.organization_member_repository import (
    OrganizationMemberRepository,
)
from raggae.application.interfaces.repositories.organization_repository import (
    OrganizationRepository,
)
from raggae.domain.entities.organization_project_defaults import OrganizationProjectDefaults
from raggae.domain.exceptions.organization_exceptions import (
    OrganizationAccessDeniedError,
    OrganizationNotFoundError,
)
from raggae.domain.value_objects.organization_member_role import OrganizationMemberRole


class UpsertOrganizationProjectDefaults:
    """Use Case: Create or replace project defaults for an organization (owner only)."""

    def __init__(
        self,
        organization_repository: OrganizationRepository,
        organization_member_repository: OrganizationMemberRepository,
        org_project_defaults_repository: OrgProjectDefaultsRepository,
    ) -> None:
        self._organization_repository = organization_repository
        self._organization_member_repository = organization_member_repository
        self._org_project_defaults_repository = org_project_defaults_repository

    async def execute(
        self,
        organization_id: UUID,
        user_id: UUID,
        embedding_backend: str | None = None,
        embedding_model: str | None = None,
        embedding_api_key_credential_id: UUID | None = None,
        llm_backend: str | None = None,
        llm_model: str | None = None,
        llm_api_key_credential_id: UUID | None = None,
        chunking_strategy: str | None = None,
        parent_child_chunking: bool | None = None,
        retrieval_strategy: str | None = None,
        retrieval_top_k: int | None = None,
        retrieval_min_score: float | None = None,
        reranking_enabled: bool | None = None,
        reranker_backend: str | None = None,
        reranker_model: str | None = None,
        reranker_candidate_multiplier: int | None = None,
        chat_history_window_size: int | None = None,
        chat_history_max_chars: int | None = None,
    ) -> OrgProjectDefaultsDTO:
        organization = await self._organization_repository.find_by_id(organization_id)
        if organization is None:
            raise OrganizationNotFoundError(f"Organization {organization_id} not found")
        member = await self._organization_member_repository.find_by_organization_and_user(
            organization_id=organization_id,
            user_id=user_id,
        )
        if member is None or member.role != OrganizationMemberRole.OWNER:
            raise OrganizationAccessDeniedError(
                f"User {user_id} must be an owner to configure project defaults"
            )

        existing = await self._org_project_defaults_repository.find_by_organization_id(organization_id)
        base = existing or OrganizationProjectDefaults(organization_id=organization_id)
        defaults = replace(
            base,
            embedding_backend=embedding_backend,
            embedding_model=embedding_model,
            embedding_api_key_credential_id=embedding_api_key_credential_id,
            llm_backend=llm_backend,
            llm_model=llm_model,
            llm_api_key_credential_id=llm_api_key_credential_id,
            chunking_strategy=chunking_strategy,
            parent_child_chunking=parent_child_chunking,
            retrieval_strategy=retrieval_strategy,
            retrieval_top_k=retrieval_top_k,
            retrieval_min_score=retrieval_min_score,
            reranking_enabled=reranking_enabled,
            reranker_backend=reranker_backend,
            reranker_model=reranker_model,
            reranker_candidate_multiplier=reranker_candidate_multiplier,
            chat_history_window_size=chat_history_window_size,
            chat_history_max_chars=chat_history_max_chars,
        )
        await self._org_project_defaults_repository.save(defaults)
        return OrgProjectDefaultsDTO.from_entity(defaults)
