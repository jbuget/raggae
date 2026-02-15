from fastapi import FastAPI

app = FastAPI(
    title="Raggae",
    description="RAG Generator Agent Expert",
    version="0.1.0",
)


@app.get("/health")
async def health() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok"}
