import os

import pytest

from raggae.infrastructure.services.openai_embedding_service import OpenAIEmbeddingService


class TestOpenAIEmbeddingService:
    @pytest.mark.integration
    async def test_integration_embed_texts(self) -> None:
        api_key = os.getenv("OPENAI_API_KEY", "")
        run_live = os.getenv("RUN_OPENAI_INTEGRATION", "0") == "1"
        if not run_live:
            pytest.skip("Set RUN_OPENAI_INTEGRATION=1 to run live OpenAI integration test")
        if not api_key.startswith("sk-"):
            pytest.skip("OPENAI_API_KEY is not configured for live integration test")

        service = OpenAIEmbeddingService(
            api_key=api_key,
            model="text-embedding-3-small",
        )
        vectors = await service.embed_texts(["hello raggae"])

        assert len(vectors) == 1
        assert len(vectors[0]) > 100
