import os

import pytest
from httpx import ASGITransport, AsyncClient


def pytest_configure(config: pytest.Config) -> None:
    """Set in-memory backends before any module is imported during collection."""
    os.environ.setdefault("STORAGE_BACKEND", "inmemory")
    os.environ.setdefault("PERSISTENCE_BACKEND", "inmemory")
    os.environ.setdefault("PROCESSING_MODE", "off")
    os.environ.setdefault("DEFAULT_EMBEDDING_PROVIDER", "inmemory")
    os.environ.setdefault("DEFAULT_LLM_PROVIDER", "inmemory")


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
    if hasattr(dependencies, "_organization_repository") and hasattr(
        dependencies._organization_repository, "_organizations"
    ):
        dependencies._organization_repository._organizations.clear()
    if hasattr(dependencies, "_organization_member_repository") and hasattr(
        dependencies._organization_member_repository, "_members"
    ):
        dependencies._organization_member_repository._members.clear()
    if hasattr(dependencies, "_organization_invitation_repository") and hasattr(
        dependencies._organization_invitation_repository, "_invitations"
    ):
        dependencies._organization_invitation_repository._invitations.clear()


@pytest.fixture
async def client() -> AsyncClient:
    """Async HTTP client for testing the FastAPI app."""
    os.environ["STORAGE_BACKEND"] = "inmemory"
    os.environ["PERSISTENCE_BACKEND"] = "inmemory"
    os.environ["PROCESSING_MODE"] = "off"
    os.environ["DEFAULT_EMBEDDING_PROVIDER"] = "inmemory"
    os.environ["DEFAULT_LLM_PROVIDER"] = "inmemory"
    from raggae.presentation.main import app

    _reset_repositories()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
