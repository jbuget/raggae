import hashlib

from raggae.infrastructure.services.fernet_provider_api_key_crypto_service import (
    FernetProviderApiKeyCryptoService,
)


def test_encrypt_and_decrypt_should_return_original_api_key() -> None:
    # Given
    service = FernetProviderApiKeyCryptoService(
        encryption_key="MDEyMzQ1Njc4OWFiY2RlZjAxMjM0NTY3ODlhYmNkZWY="
    )
    api_key = "sk-test-secret"

    # When
    encrypted = service.encrypt(api_key)
    decrypted = service.decrypt(encrypted)

    # Then
    assert encrypted != api_key
    assert decrypted == api_key


def test_fingerprint_should_match_sha256_hex_digest() -> None:
    # Given
    service = FernetProviderApiKeyCryptoService(
        encryption_key="MDEyMzQ1Njc4OWFiY2RlZjAxMjM0NTY3ODlhYmNkZWY="
    )
    api_key = "AIza-test-secret"

    # When
    fingerprint = service.fingerprint(api_key)

    # Then
    assert fingerprint == hashlib.sha256(api_key.encode("utf-8")).hexdigest()
