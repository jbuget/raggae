from typing import Protocol


class ProviderApiKeyCryptoService(Protocol):
    """Interface for provider API key encryption/decryption."""

    def encrypt(self, raw_api_key: str) -> str: ...

    def decrypt(self, encrypted_api_key: str) -> str: ...

    def fingerprint(self, raw_api_key: str) -> str: ...
