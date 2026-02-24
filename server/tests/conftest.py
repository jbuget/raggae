import os

import pytest
from httpx import ASGITransport, AsyncClient


def pytest_configure(config: pytest.Config) -> None:
    """Set in-memory backends before any module is imported during collection."""
    os.environ.setdefault("STORAGE_BACKEND", "inmemory")
    os.environ.setdefault("PERSISTENCE_BACKEND", "inmemory")
    os.environ.setdefault("PROCESSING_MODE", "off")
    os.environ.setdefault("EMBEDDING_BACKEND", "inmemory")
    os.environ.setdefault("LLM_BACKEND", "inmemory")


def _reset_repositories() -> None:
    """Clear all in-memory repository singletons to ensure test isolation."""
    from raggae.presentation.api import dependencies

    if hasattr(dependencies._user_repository, "_users"):
        dependencies._user_repository._users.clear()
    if hasattr(dependencies._project_repository, "_projects"):
        dependencies._project_repository._projects.clear()
    if hasattr(dependencies._document_repository, "_documents"):
        dependencies._document_repository._documents.clear()
    if hasattr(dependencies._document_chunk_repository, "_chunks"):
        dependencies._document_chunk_repository._chunks.clear()
    if hasattr(dependencies._conversation_repository, "_conversations"):
        dependencies._conversation_repository._conversations.clear()
    if hasattr(dependencies._message_repository, "_messages"):
        dependencies._message_repository._messages.clear()
    if hasattr(dependencies._provider_credential_repository, "_credentials"):
        dependencies._provider_credential_repository._credentials.clear()


@pytest.fixture
async def client() -> AsyncClient:
    """Async HTTP client for testing the FastAPI app."""
    os.environ["STORAGE_BACKEND"] = "inmemory"
    os.environ["PERSISTENCE_BACKEND"] = "inmemory"
    os.environ["PROCESSING_MODE"] = "off"
    os.environ["EMBEDDING_BACKEND"] = "inmemory"
    os.environ["LLM_BACKEND"] = "inmemory"
    from raggae.presentation.main import app

    _reset_repositories()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
