from raggae.presentation.api.v1.endpoints.auth import router as auth_router
from raggae.presentation.api.v1.endpoints.chat import router as chat_router
from raggae.presentation.api.v1.endpoints.documents import router as documents_router
from raggae.presentation.api.v1.endpoints.model_credentials import (
    router as model_credentials_router,
)
from raggae.presentation.api.v1.endpoints.model_catalog import router as model_catalog_router
from raggae.presentation.api.v1.endpoints.projects import router as projects_router

__all__ = [
    "auth_router",
    "chat_router",
    "documents_router",
    "model_catalog_router",
    "model_credentials_router",
    "projects_router",
]
