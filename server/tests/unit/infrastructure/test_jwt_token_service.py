from uuid import uuid4

from raggae.infrastructure.services.jwt_token_service import JwtTokenService


class TestJwtTokenService:
    def test_create_and_verify_token(self) -> None:
        # Given
        service = JwtTokenService(secret_key="test-secret", algorithm="HS256")
        user_id = uuid4()

        # When
        token = service.create_access_token(user_id)
        result = service.verify_token(token)

        # Then
        assert result == user_id

    def test_verify_invalid_token_returns_none(self) -> None:
        # Given
        service = JwtTokenService(secret_key="test-secret", algorithm="HS256")

        # When
        result = service.verify_token("invalid-token")

        # Then
        assert result is None

    def test_verify_token_wrong_secret_returns_none(self) -> None:
        # Given
        service1 = JwtTokenService(secret_key="secret-1", algorithm="HS256")
        service2 = JwtTokenService(secret_key="secret-2", algorithm="HS256")
        user_id = uuid4()

        # When
        token = service1.create_access_token(user_id)
        result = service2.verify_token(token)

        # Then
        assert result is None
