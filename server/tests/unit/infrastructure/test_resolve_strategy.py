"""Tests for _resolve_strategy across all three copies."""

import pytest
from raggae.application.use_cases.chat.query_relevant_chunks import (
    _resolve_strategy as resolve_strategy_use_case,
)
from raggae.infrastructure.services.in_memory_chunk_retrieval_service import (
    _resolve_strategy as resolve_strategy_inmemory,
)
from raggae.infrastructure.services.sqlalchemy_chunk_retrieval_service import (
    _resolve_strategy as resolve_strategy_sqlalchemy,
)

_ALL_RESOLVE_STRATEGIES = [
    resolve_strategy_use_case,
    resolve_strategy_inmemory,
    resolve_strategy_sqlalchemy,
]


@pytest.mark.parametrize("resolve_strategy", _ALL_RESOLVE_STRATEGIES)
class TestResolveStrategy:
    """Shared tests executed against every copy of _resolve_strategy."""

    def test_explicit_strategy_returned_as_is(self, resolve_strategy: type) -> None:
        """Given an explicit strategy, it should be returned unchanged."""
        assert resolve_strategy("hybrid", "any query") == "hybrid"
        assert resolve_strategy("vector", "any query") == "vector"
        assert resolve_strategy("fulltext", "any query") == "fulltext"

    def test_auto_french_apostrophes_resolve_to_hybrid(self, resolve_strategy: type) -> None:
        """Given a French query with apostrophes in auto mode, it should resolve to hybrid."""
        # Given
        french_queries = [
            "en tant qu'alternant, ai-je droit à des congés pour les examens ?",
            "l'entreprise doit-elle fournir un équipement ?",
            "j'ai besoin d'un justificatif d'absence",
        ]
        # When / Then
        for query in french_queries:
            result = resolve_strategy("auto", query)
            assert result == "hybrid", (
                f"Expected 'hybrid' for French query '{query}', got '{result}'"
            )

    def test_auto_double_quotes_resolve_to_fulltext(self, resolve_strategy: type) -> None:
        """Given a query with double quotes in auto mode, it should resolve to fulltext."""
        result = resolve_strategy("auto", '"congés exceptionnels"')
        assert result == "fulltext"

    def test_auto_short_technical_query_resolves_to_fulltext(self, resolve_strategy: type) -> None:
        """Given a short technical query in auto mode, it should resolve to fulltext."""
        result = resolve_strategy("auto", "HTTP_PROXY config")
        assert result == "fulltext"

    def test_auto_long_natural_query_resolves_to_hybrid(self, resolve_strategy: type) -> None:
        """Given a long natural language query in auto mode, it should resolve to hybrid."""
        result = resolve_strategy("auto", "how do I configure the proxy settings")
        assert result == "hybrid"
