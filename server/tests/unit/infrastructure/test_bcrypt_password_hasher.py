from raggae.infrastructure.services.bcrypt_password_hasher import BcryptPasswordHasher


class TestBcryptPasswordHasher:
    def test_hash_returns_different_string(self) -> None:
        # Given
        hasher = BcryptPasswordHasher()

        # When
        hashed = hasher.hash("SecurePass123!")

        # Then
        assert hashed != "SecurePass123!"
        assert len(hashed) > 0

    def test_verify_correct_password(self) -> None:
        # Given
        hasher = BcryptPasswordHasher()
        hashed = hasher.hash("SecurePass123!")

        # When / Then
        assert hasher.verify("SecurePass123!", hashed) is True

    def test_verify_wrong_password(self) -> None:
        # Given
        hasher = BcryptPasswordHasher()
        hashed = hasher.hash("SecurePass123!")

        # When / Then
        assert hasher.verify("WrongPass456!", hashed) is False
