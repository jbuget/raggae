from datetime import UTC, datetime, timedelta

import pytest

from raggae.application.use_cases.user.handle_oauth_callback import OAuthLoginResult
from raggae.infrastructure.cache.oauth_code_store import InMemoryOAuthCodeStore


@pytest.fixture
def store() -> InMemoryOAuthCodeStore:
    return InMemoryOAuthCodeStore()


def make_result(token: str = "jwt-token") -> OAuthLoginResult:
    return OAuthLoginResult(access_token=token)


class TestInMemoryOAuthCodeStore:
    async def test_consume_returns_result_for_stored_code(self, store: InMemoryOAuthCodeStore) -> None:
        # Given
        result = make_result()
        await store.store("code-abc", result, ttl_seconds=30)

        # When
        consumed = await store.consume("code-abc")

        # Then
        assert consumed is not None
        assert consumed.access_token == "jwt-token"

    async def test_consume_removes_code_after_first_use(self, store: InMemoryOAuthCodeStore) -> None:
        # Given
        await store.store("code-abc", make_result(), ttl_seconds=30)
        await store.consume("code-abc")

        # When
        second = await store.consume("code-abc")

        # Then — code already consumed
        assert second is None

    async def test_consume_returns_none_for_unknown_code(self, store: InMemoryOAuthCodeStore) -> None:
        # When
        result = await store.consume("unknown-code")

        # Then
        assert result is None

    async def test_consume_returns_none_for_expired_code(self, store: InMemoryOAuthCodeStore) -> None:
        # Given — store with already-expired entry
        result = make_result()
        store._codes["expired-code"] = (
            result,
            datetime.now(UTC) - timedelta(seconds=1),
        )

        # When
        consumed = await store.consume("expired-code")

        # Then
        assert consumed is None

    async def test_store_multiple_codes_independently(self, store: InMemoryOAuthCodeStore) -> None:
        # Given
        await store.store("code-1", make_result("token-1"), ttl_seconds=30)
        await store.store("code-2", make_result("token-2"), ttl_seconds=30)

        # When
        r1 = await store.consume("code-1")
        r2 = await store.consume("code-2")

        # Then
        assert r1 is not None and r1.access_token == "token-1"
        assert r2 is not None and r2.access_token == "token-2"
