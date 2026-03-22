from datetime import UTC, datetime
from uuid import UUID, uuid4

from raggae.application.dto.organization_default_config_dto import OrganizationDefaultConfigDTO
from raggae.application.interfaces.repositories.organization_default_config_repository import (
    OrganizationDefaultConfigRepository,
)
from raggae.application.interfaces.repositories.organization_member_repository import (
    OrganizationMemberRepository,
)
from raggae.application.interfaces.repositories.organization_repository import (
    OrganizationRepository,
)
from raggae.domain.entities.organization_default_config import OrganizationDefaultConfig
from raggae.domain.exceptions.organization_exceptions import (
    OrganizationAccessDeniedError,
    OrganizationNotFoundError,
)
from raggae.domain.value_objects.chunking_strategy import ChunkingStrategy
from raggae.domain.value_objects.organization_member_role import OrganizationMemberRole


class UpsertOrganizationDefaultConfig:
    """Use Case: Create or update default assistant config for an organization (OWNER or MAKER)."""

    def __init__(
        self,
        organization_repository: OrganizationRepository,
        organization_member_repository: OrganizationMemberRepository,
        organization_default_config_repository: OrganizationDefaultConfigRepository,
    ) -> None:
        self._organization_repository = organization_repository
        self._organization_member_repository = organization_member_repository
        self._organization_default_config_repository = organization_default_config_repository

    async def execute(  # noqa: PLR0913
        self,
        organization_id: UUID,
        user_id: UUID,
        embedding_backend: str | None,
        embedding_model: str | None,
        llm_backend: str | None,
        llm_model: str | None,
        chunking_strategy: ChunkingStrategy | None,
        parent_child_chunking: bool | None,
        retrieval_strategy: str | None,
        retrieval_top_k: int | None,
        retrieval_min_score: float | None,
        reranking_enabled: bool | None,
        reranker_backend: str | None,
        reranker_model: str | None,
        reranker_candidate_multiplier: int | None,
        org_embedding_api_key_credential_id: UUID | None,
        org_llm_api_key_credential_id: UUID | None,
    ) -> OrganizationDefaultConfigDTO:
        organization = await self._organization_repository.find_by_id(organization_id)
        if organization is None:
            raise OrganizationNotFoundError(f"Organization {organization_id} not found")
        member = await self._organization_member_repository.find_by_organization_and_user(
            organization_id=organization_id,
            user_id=user_id,
        )
        if member is None or member.role == OrganizationMemberRole.USER:
            raise OrganizationAccessDeniedError(
                f"User {user_id} cannot update config for organization {organization_id}"
            )

        now = datetime.now(UTC)
        existing = await self._organization_default_config_repository.find_by_organization_id(organization_id)
        if existing is None:
            config = OrganizationDefaultConfig(
                id=uuid4(),
                organization_id=organization_id,
                embedding_backend=embedding_backend,
                embedding_model=embedding_model,
                llm_backend=llm_backend,
                llm_model=llm_model,
                chunking_strategy=chunking_strategy,
                parent_child_chunking=parent_child_chunking,
                retrieval_strategy=retrieval_strategy,
                retrieval_top_k=retrieval_top_k,
                retrieval_min_score=retrieval_min_score,
                reranking_enabled=reranking_enabled,
                reranker_backend=reranker_backend,
                reranker_model=reranker_model,
                reranker_candidate_multiplier=reranker_candidate_multiplier,
                org_embedding_api_key_credential_id=org_embedding_api_key_credential_id,
                org_llm_api_key_credential_id=org_llm_api_key_credential_id,
                updated_at=now,
            )
        else:
            config = existing.update(
                embedding_backend=embedding_backend,
                embedding_model=embedding_model,
                llm_backend=llm_backend,
                llm_model=llm_model,
                chunking_strategy=chunking_strategy,
                parent_child_chunking=parent_child_chunking,
                retrieval_strategy=retrieval_strategy,
                retrieval_top_k=retrieval_top_k,
                retrieval_min_score=retrieval_min_score,
                reranking_enabled=reranking_enabled,
                reranker_backend=reranker_backend,
                reranker_model=reranker_model,
                reranker_candidate_multiplier=reranker_candidate_multiplier,
                org_embedding_api_key_credential_id=org_embedding_api_key_credential_id,
                org_llm_api_key_credential_id=org_llm_api_key_credential_id,
                updated_at=now,
            )

        await self._organization_default_config_repository.save(config)
        return OrganizationDefaultConfigDTO.from_entity(config)
