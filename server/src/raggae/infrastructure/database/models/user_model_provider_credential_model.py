from datetime import datetime
from uuid import UUID

from sqlalchemy import Boolean, DateTime, Index, String, Text, text
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from raggae.infrastructure.database.models.base import Base


class UserModelProviderCredentialModel(Base):
    __tablename__ = "user_model_provider_credentials"
    __table_args__ = (
        Index(
            "uq_user_provider_active_credential",
            "user_id",
            "provider",
            unique=True,
            postgresql_where=text("is_active = true"),
        ),
    )

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True)
    user_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), nullable=False, index=True)
    provider: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    encrypted_api_key: Mapped[str] = mapped_column(Text(), nullable=False)
    key_fingerprint: Mapped[str] = mapped_column(String(128), nullable=False)
    key_suffix: Mapped[str] = mapped_column(String(16), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean(), nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
