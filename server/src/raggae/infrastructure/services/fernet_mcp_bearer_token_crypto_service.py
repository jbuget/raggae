from raggae.application.interfaces.services.provider_api_key_crypto_service import (
    ProviderApiKeyCryptoService,
)


class FernetMcpBearerTokenCryptoService:
    """Adapter exposing the MCP bearer token crypto port via the existing Fernet service.

    Reuses the same encryption key and algorithm as provider API keys, but keeps the
    application port `McpBearerTokenCryptoService` semantically distinct.
    """

    def __init__(self, inner: ProviderApiKeyCryptoService) -> None:
        self._inner = inner

    def encrypt(self, raw_token: str) -> str:
        return self._inner.encrypt(raw_token)

    def decrypt(self, encrypted_token: str) -> str:
        return self._inner.decrypt(encrypted_token)

    def fingerprint(self, raw_token: str) -> str:
        return self._inner.fingerprint(raw_token)
