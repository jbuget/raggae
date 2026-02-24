from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from raggae.domain.entities.organization_invitation import OrganizationInvitation
from raggae.domain.value_objects.organization_invitation_status import (
    OrganizationInvitationStatus,
)
from raggae.domain.value_objects.organization_member_role import OrganizationMemberRole
from raggae.infrastructure.database.models.organization_invitation_model import (
    OrganizationInvitationModel,
)


class SQLAlchemyOrganizationInvitationRepository:
    """PostgreSQL organization invitation repository using SQLAlchemy async sessions."""

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory

    async def save(self, invitation: OrganizationInvitation) -> None:
        async with self._session_factory() as session:
            model = await session.get(OrganizationInvitationModel, invitation.id)
            if model is None:
                model = OrganizationInvitationModel(
                    id=invitation.id,
                    organization_id=invitation.organization_id,
                    email=invitation.email,
                    role=invitation.role.value,
                    status=invitation.status.value,
                    invited_by_user_id=invitation.invited_by_user_id,
                    token_hash=invitation.token_hash,
                    expires_at=invitation.expires_at,
                    created_at=invitation.created_at,
                    updated_at=invitation.updated_at,
                )
                session.add(model)
            else:
                model.email = invitation.email
                model.role = invitation.role.value
                model.status = invitation.status.value
                model.token_hash = invitation.token_hash
                model.expires_at = invitation.expires_at
                model.updated_at = invitation.updated_at
            await session.commit()

    async def find_by_id(self, invitation_id: UUID) -> OrganizationInvitation | None:
        async with self._session_factory() as session:
            model = await session.get(OrganizationInvitationModel, invitation_id)
            if model is None:
                return None
            return self._to_entity(model)

    async def find_by_token_hash(self, token_hash: str) -> OrganizationInvitation | None:
        async with self._session_factory() as session:
            result = await session.execute(
                select(OrganizationInvitationModel).where(
                    OrganizationInvitationModel.token_hash == token_hash
                )
            )
            model = result.scalars().first()
            return self._to_entity(model) if model is not None else None

    async def find_pending_by_organization_and_email(
        self, organization_id: UUID, email: str
    ) -> OrganizationInvitation | None:
        async with self._session_factory() as session:
            result = await session.execute(
                select(OrganizationInvitationModel).where(
                    OrganizationInvitationModel.organization_id == organization_id,
                    OrganizationInvitationModel.email == email,
                    OrganizationInvitationModel.status
                    == OrganizationInvitationStatus.PENDING.value,
                )
            )
            model = result.scalars().first()
            return self._to_entity(model) if model is not None else None

    async def find_by_organization_id(self, organization_id: UUID) -> list[OrganizationInvitation]:
        async with self._session_factory() as session:
            result = await session.execute(
                select(OrganizationInvitationModel).where(
                    OrganizationInvitationModel.organization_id == organization_id
                )
            )
            return [self._to_entity(model) for model in result.scalars().all()]

    async def delete_by_organization_id(self, organization_id: UUID) -> None:
        async with self._session_factory() as session:
            await session.execute(
                delete(OrganizationInvitationModel).where(
                    OrganizationInvitationModel.organization_id == organization_id
                )
            )
            await session.commit()

    @staticmethod
    def _to_entity(model: OrganizationInvitationModel) -> OrganizationInvitation:
        return OrganizationInvitation(
            id=model.id,
            organization_id=model.organization_id,
            email=model.email,
            role=OrganizationMemberRole(model.role),
            status=OrganizationInvitationStatus(model.status),
            invited_by_user_id=model.invited_by_user_id,
            token_hash=model.token_hash,
            expires_at=model.expires_at,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
