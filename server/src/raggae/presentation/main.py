from fastapi import FastAPI

from raggae.presentation.api.v1.endpoints.auth import router as auth_router

app = FastAPI(
    title="Raggae",
    description="RAG Generator Agent Expert",
    version="0.1.0",
)

app.include_router(auth_router, prefix="/api/v1")


@app.get("/health")
async def health() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok"}
