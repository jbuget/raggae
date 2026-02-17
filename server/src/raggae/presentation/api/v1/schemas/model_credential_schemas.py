from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class SaveModelCredentialRequest(BaseModel):
    provider: str = Field(min_length=1, max_length=32)
    api_key: str = Field(min_length=4, max_length=512)


class ModelCredentialResponse(BaseModel):
    id: UUID
    provider: str
    masked_key: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
