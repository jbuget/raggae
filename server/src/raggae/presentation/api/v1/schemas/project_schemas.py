from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class CreateProjectRequest(BaseModel):
    name: str = Field(..., min_length=1)
    description: str = ""
    system_prompt: str = ""


class UpdateProjectRequest(BaseModel):
    name: str = Field(..., min_length=1)
    description: str = ""
    system_prompt: str = ""


class ProjectResponse(BaseModel):
    id: UUID
    user_id: UUID
    name: str
    description: str
    system_prompt: str
    is_published: bool
    created_at: datetime
