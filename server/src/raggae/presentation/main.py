import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import UTC, datetime

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from raggae.infrastructure.config.settings import settings
from raggae.presentation.api.dependencies import get_query_relevant_chunks_use_case
from raggae.presentation.api.v1.endpoints.auth import router as auth_router
from raggae.presentation.api.v1.endpoints.chat import router as chat_router
from raggae.presentation.api.v1.endpoints.documents import router as documents_router
from raggae.presentation.api.v1.endpoints.entra import router as entra_router
from raggae.presentation.api.v1.endpoints.model_catalog import router as model_catalog_router
from raggae.presentation.api.v1.endpoints.model_credentials import (
    router as model_credentials_router,
)
from raggae.presentation.api.v1.endpoints.org_model_credentials import (
    router as org_model_credentials_router,
)
from raggae.presentation.api.v1.endpoints.organizations import router as organizations_router
from raggae.presentation.api.v1.endpoints.project_snapshots import (
    router as project_snapshots_router,
)
from raggae.presentation.api.v1.endpoints.projects import router as projects_router

logging.getLogger("raggae").setLevel(logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    """Warm up heavy retrieval dependencies at startup."""
    get_query_relevant_chunks_use_case()
    _warn_if_entra_secret_expiring()
    yield


def _warn_if_entra_secret_expiring() -> None:
    if not settings.entra_enabled or settings.entra_client_secret_expires_at is None:
        return
    expires_at = settings.entra_client_secret_expires_at
    days_remaining = (expires_at - datetime.now(UTC)).days
    if days_remaining <= 30:
        logger.warning(
            "Entra client secret is expiring soon",
            extra={
                "event": "entra_secret_expiring_soon",
                "expires_at": expires_at.isoformat(),
                "days_remaining": days_remaining,
            },
        )


app = FastAPI(
    title="Raggae",
    description="RAG Generator Agent Expert",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api/v1")
app.include_router(entra_router, prefix="/api/v1")
app.include_router(projects_router, prefix="/api/v1")
app.include_router(project_snapshots_router, prefix="/api/v1")
app.include_router(organizations_router, prefix="/api/v1")
app.include_router(documents_router, prefix="/api/v1")
app.include_router(chat_router, prefix="/api/v1")
app.include_router(model_catalog_router, prefix="/api/v1")
app.include_router(model_credentials_router, prefix="/api/v1")
app.include_router(org_model_credentials_router, prefix="/api/v1")


@app.get("/health")
async def health() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok"}
