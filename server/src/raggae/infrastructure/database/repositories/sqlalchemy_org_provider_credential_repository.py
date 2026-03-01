from uuid import UUID

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from raggae.domain.entities.org_model_provider_credential import OrgModelProviderCredential
from raggae.domain.value_objects.model_provider import ModelProvider
from raggae.infrastructure.database.models.org_model_provider_credential_model import (
    OrgModelProviderCredentialModel,
)


class SQLAlchemyOrgProviderCredentialRepository:
    """PostgreSQL org provider credential repository using SQLAlchemy async sessions."""

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory

    async def save(self, credential: OrgModelProviderCredential) -> None:
        async with self._session_factory() as session:
            model = await session.get(OrgModelProviderCredentialModel, credential.id)
            if model is None:
                model = OrgModelProviderCredentialModel(
                    id=credential.id,
                    organization_id=credential.organization_id,
                    provider=credential.provider.value,
                    encrypted_api_key=credential.encrypted_api_key,
                    key_fingerprint=credential.key_fingerprint,
                    key_suffix=credential.key_suffix,
                    is_active=credential.is_active,
                    created_at=credential.created_at,
                    updated_at=credential.updated_at,
                )
                session.add(model)
            else:
                model.encrypted_api_key = credential.encrypted_api_key
                model.key_fingerprint = credential.key_fingerprint
                model.key_suffix = credential.key_suffix
                model.is_active = credential.is_active
                model.updated_at = credential.updated_at
            await session.commit()

    async def list_by_org_id(self, organization_id: UUID) -> list[OrgModelProviderCredential]:
        async with self._session_factory() as session:
            result = await session.execute(
                select(OrgModelProviderCredentialModel).where(
                    OrgModelProviderCredentialModel.organization_id == organization_id
                )
            )
            return [self._to_domain(m) for m in result.scalars().all()]

    async def list_by_org_id_and_provider(
        self,
        organization_id: UUID,
        provider: ModelProvider,
    ) -> list[OrgModelProviderCredential]:
        async with self._session_factory() as session:
            result = await session.execute(
                select(OrgModelProviderCredentialModel).where(
                    OrgModelProviderCredentialModel.organization_id == organization_id,
                    OrgModelProviderCredentialModel.provider == provider.value,
                )
            )
            return [self._to_domain(m) for m in result.scalars().all()]

    async def set_active(self, credential_id: UUID, organization_id: UUID) -> None:
        async with self._session_factory() as session:
            target = await session.get(OrgModelProviderCredentialModel, credential_id)
            if target is None or target.organization_id != organization_id:
                await session.commit()
                return
            await session.execute(
                update(OrgModelProviderCredentialModel)
                .where(OrgModelProviderCredentialModel.id == credential_id)
                .values(is_active=True)
            )
            await session.commit()

    async def set_inactive(self, credential_id: UUID, organization_id: UUID) -> None:
        async with self._session_factory() as session:
            target = await session.get(OrgModelProviderCredentialModel, credential_id)
            if target is None or target.organization_id != organization_id:
                await session.commit()
                return
            await session.execute(
                update(OrgModelProviderCredentialModel)
                .where(OrgModelProviderCredentialModel.id == credential_id)
                .values(is_active=False)
            )
            await session.commit()

    async def delete(self, credential_id: UUID, organization_id: UUID) -> None:
        async with self._session_factory() as session:
            await session.execute(
                delete(OrgModelProviderCredentialModel).where(
                    OrgModelProviderCredentialModel.id == credential_id,
                    OrgModelProviderCredentialModel.organization_id == organization_id,
                )
            )
            await session.commit()

    def _to_domain(self, model: OrgModelProviderCredentialModel) -> OrgModelProviderCredential:
        return OrgModelProviderCredential(
            id=model.id,
            organization_id=model.organization_id,
            provider=ModelProvider(model.provider),
            encrypted_api_key=model.encrypted_api_key,
            key_fingerprint=model.key_fingerprint,
            key_suffix=model.key_suffix,
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
