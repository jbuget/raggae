from unittest.mock import patch

from raggae.infrastructure.config.settings import Settings


class TestUserProviderKeysEnabled:
    def test_user_provider_keys_enabled_defaults_to_true(self) -> None:
        # Given / When
        s = Settings()

        # Then
        assert s.user_provider_keys_enabled is True

    def test_user_provider_keys_enabled_when_env_set_uses_env_value(self) -> None:
        # Given
        env = {"USER_PROVIDER_KEYS_ENABLED": "false"}

        # When
        with patch.dict("os.environ", env):
            s = Settings()

        # Then
        assert s.user_provider_keys_enabled is False
