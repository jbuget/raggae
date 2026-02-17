from uuid import UUID

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from raggae.domain.entities.user_model_provider_credential import UserModelProviderCredential
from raggae.domain.value_objects.model_provider import ModelProvider
from raggae.infrastructure.database.models.user_model_provider_credential_model import (
    UserModelProviderCredentialModel,
)


class SQLAlchemyProviderCredentialRepository:
    """PostgreSQL provider credential repository using SQLAlchemy async sessions."""

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory

    async def save(self, credential: UserModelProviderCredential) -> None:
        async with self._session_factory() as session:
            model = await session.get(UserModelProviderCredentialModel, credential.id)
            if model is None:
                model = UserModelProviderCredentialModel(
                    id=credential.id,
                    user_id=credential.user_id,
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

    async def list_by_user_id(self, user_id: UUID) -> list[UserModelProviderCredential]:
        async with self._session_factory() as session:
            result = await session.execute(
                select(UserModelProviderCredentialModel).where(
                    UserModelProviderCredentialModel.user_id == user_id
                )
            )
            models = result.scalars().all()
            return [self._to_domain(model) for model in models]

    async def list_by_user_id_and_provider(
        self,
        user_id: UUID,
        provider: ModelProvider,
    ) -> list[UserModelProviderCredential]:
        async with self._session_factory() as session:
            result = await session.execute(
                select(UserModelProviderCredentialModel).where(
                    UserModelProviderCredentialModel.user_id == user_id,
                    UserModelProviderCredentialModel.provider == provider.value,
                )
            )
            models = result.scalars().all()
            return [self._to_domain(model) for model in models]

    async def set_active(self, credential_id: UUID, user_id: UUID) -> None:
        async with self._session_factory() as session:
            target = await session.get(UserModelProviderCredentialModel, credential_id)
            if target is None or target.user_id != user_id:
                await session.commit()
                return

            await session.execute(
                update(UserModelProviderCredentialModel)
                .where(
                    UserModelProviderCredentialModel.user_id == user_id,
                    UserModelProviderCredentialModel.provider == target.provider,
                )
                .values(is_active=False)
            )
            await session.execute(
                update(UserModelProviderCredentialModel)
                .where(UserModelProviderCredentialModel.id == credential_id)
                .values(is_active=True)
            )
            await session.commit()

    async def delete(self, credential_id: UUID, user_id: UUID) -> None:
        async with self._session_factory() as session:
            await session.execute(
                delete(UserModelProviderCredentialModel).where(
                    UserModelProviderCredentialModel.id == credential_id,
                    UserModelProviderCredentialModel.user_id == user_id,
                )
            )
            await session.commit()

    def _to_domain(
        self,
        model: UserModelProviderCredentialModel,
    ) -> UserModelProviderCredential:
        return UserModelProviderCredential(
            id=model.id,
            user_id=model.user_id,
            provider=ModelProvider(model.provider),
            encrypted_api_key=model.encrypted_api_key,
            key_fingerprint=model.key_fingerprint,
            key_suffix=model.key_suffix,
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
