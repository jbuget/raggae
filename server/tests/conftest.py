import os

import pytest
from httpx import ASGITransport, AsyncClient


@pytest.fixture
async def client() -> AsyncClient:
    """Async HTTP client for testing the FastAPI app."""
    os.environ.setdefault("STORAGE_BACKEND", "inmemory")
    os.environ.setdefault("PERSISTENCE_BACKEND", "inmemory")
    os.environ.setdefault("PROCESSING_MODE", "off")
    os.environ.setdefault("EMBEDDING_BACKEND", "inmemory")
    os.environ.setdefault("LLM_BACKEND", "inmemory")
    from raggae.presentation.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
