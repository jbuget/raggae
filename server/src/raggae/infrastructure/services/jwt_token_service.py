from typing import Any, cast
from uuid import UUID

from jose import JWTError, jwt


class JwtTokenService:
    """JWT token service implementation using python-jose."""

    def __init__(self, secret_key: str, algorithm: str = "HS256") -> None:
        self._secret_key = secret_key
        self._algorithm = algorithm

    def create_access_token(self, user_id: UUID) -> str:
        payload = {"sub": str(user_id)}
        return cast(str, jwt.encode(payload, self._secret_key, algorithm=self._algorithm))

    def verify_token(self, token: str) -> UUID | None:
        try:
            payload = cast(
                dict[str, Any],
                jwt.decode(token, self._secret_key, algorithms=[self._algorithm]),
            )
            sub = payload.get("sub")
            if sub is None:
                return None
            return UUID(sub)
        except (JWTError, ValueError):
            return None
