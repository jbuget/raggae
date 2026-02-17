from fastapi import FastAPI

from raggae.presentation.api.v1.endpoints.auth import router as auth_router
from raggae.presentation.api.v1.endpoints.chat import router as chat_router
from raggae.presentation.api.v1.endpoints.documents import router as documents_router
from raggae.presentation.api.v1.endpoints.model_catalog import router as model_catalog_router
from raggae.presentation.api.v1.endpoints.model_credentials import (
    router as model_credentials_router,
)
from raggae.presentation.api.v1.endpoints.projects import router as projects_router

app = FastAPI(
    title="Raggae",
    description="RAG Generator Agent Expert",
    version="0.1.0",
)

app.include_router(auth_router, prefix="/api/v1")
app.include_router(projects_router, prefix="/api/v1")
app.include_router(documents_router, prefix="/api/v1")
app.include_router(chat_router, prefix="/api/v1")
app.include_router(model_catalog_router, prefix="/api/v1")
app.include_router(model_credentials_router, prefix="/api/v1")


@app.get("/health")
async def health() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok"}
