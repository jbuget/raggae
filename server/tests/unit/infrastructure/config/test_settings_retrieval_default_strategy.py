from unittest.mock import patch

from raggae.infrastructure.config.settings import Settings


class TestRetrievalDefaultStrategy:
    def test_retrieval_default_strategy_defaults_to_hybrid(self) -> None:
        # Given / When
        s = Settings()

        # Then
        assert s.retrieval_default_strategy == "hybrid"

    def test_retrieval_default_strategy_when_env_set_uses_env_value(self) -> None:
        # Given
        env = {"RETRIEVAL_DEFAULT_STRATEGY": "vector"}

        # When
        with patch.dict("os.environ", env):
            s = Settings()

        # Then
        assert s.retrieval_default_strategy == "vector"
