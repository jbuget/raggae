from raggae.infrastructure.services.fernet_mcp_bearer_token_crypto_service import (
    FernetMcpBearerTokenCryptoService,
)
from raggae.infrastructure.services.fernet_provider_api_key_crypto_service import (
    FernetProviderApiKeyCryptoService,
)


def _make_service() -> FernetMcpBearerTokenCryptoService:
    # Static key for reproducible tests (Fernet keys are 32 url-safe base64 bytes)
    test_key = "Z3JhdmlsZW8tdGVzdC1mZXJuZXQta2V5LXNlY3JldHM="
    inner = FernetProviderApiKeyCryptoService(encryption_key=test_key)
    return FernetMcpBearerTokenCryptoService(inner=inner)


def test_encrypt_then_decrypt_returns_original_token() -> None:
    service = _make_service()
    token = "ghp_abcdefghij1234567890"

    encrypted = service.encrypt(token)
    decrypted = service.decrypt(encrypted)

    assert encrypted != token
    assert decrypted == token


def test_fingerprint_is_stable() -> None:
    service = _make_service()

    assert service.fingerprint("same") == service.fingerprint("same")
    assert service.fingerprint("same") != service.fingerprint("other")
