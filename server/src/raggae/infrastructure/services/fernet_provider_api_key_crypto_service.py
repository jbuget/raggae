import hashlib

from cryptography.fernet import Fernet


class FernetProviderApiKeyCryptoService:
    """Encrypt/decrypt provider API keys using Fernet symmetric crypto."""

    def __init__(self, encryption_key: str) -> None:
        self._fernet = Fernet(encryption_key.encode("utf-8"))

    def encrypt(self, raw_api_key: str) -> str:
        encrypted = self._fernet.encrypt(raw_api_key.encode("utf-8"))
        return encrypted.decode("utf-8")

    def decrypt(self, encrypted_api_key: str) -> str:
        decrypted = self._fernet.decrypt(encrypted_api_key.encode("utf-8"))
        return decrypted.decode("utf-8")

    def fingerprint(self, raw_api_key: str) -> str:
        return hashlib.sha256(raw_api_key.encode("utf-8")).hexdigest()
