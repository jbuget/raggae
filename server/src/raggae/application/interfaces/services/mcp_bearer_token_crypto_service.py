from typing import Protocol


class McpBearerTokenCryptoService(Protocol):
    """Interface for MCP bearer token encryption/decryption.

    Mirrors `ProviderApiKeyCryptoService` semantically; kept as a separate port to avoid
    coupling two unrelated secret domains. Implementations may delegate to the same backend.
    """

    def encrypt(self, raw_token: str) -> str: ...

    def decrypt(self, encrypted_token: str) -> str: ...

    def fingerprint(self, raw_token: str) -> str: ...
