from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from raggae.presentation.api.v1.endpoints.auth import router as auth_router
from raggae.presentation.api.v1.endpoints.chat import router as chat_router
from raggae.presentation.api.v1.endpoints.documents import router as documents_router
from raggae.presentation.api.v1.endpoints.model_catalog import router as model_catalog_router
from raggae.presentation.api.v1.endpoints.model_credentials import (
    router as model_credentials_router,
)
from raggae.presentation.api.v1.endpoints.org_model_credentials import (
    router as org_model_credentials_router,
)
from raggae.presentation.api.v1.endpoints.organizations import router as organizations_router
from raggae.presentation.api.v1.endpoints.projects import router as projects_router
from raggae.presentation.api.dependencies import get_query_relevant_chunks_use_case


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    """Warm up heavy retrieval dependencies at startup."""
    get_query_relevant_chunks_use_case()
    yield


app = FastAPI(
    title="Raggae",
    description="RAG Generator Agent Expert",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(auth_router, prefix="/api/v1")
app.include_router(projects_router, prefix="/api/v1")
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
