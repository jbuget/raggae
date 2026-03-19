from datetime import UTC, datetime, timedelta

import pytest

from raggae.application.config.entra_config import EntraConfig


class TestEntraConfig:
    def test_create_entra_config_with_required_fields(self) -> None:
        # Given / When
        config = EntraConfig(
            client_id="client-id",
            client_secret="client-secret",
            tenant_id="tenant-id",
            redirect_uri="https://app.example.com/api/v1/auth/entra/callback",
            allowed_domains=[],
        )

        # Then
        assert config.client_id == "client-id"
        assert config.client_secret == "client-secret"
        assert config.tenant_id == "tenant-id"
        assert config.redirect_uri == "https://app.example.com/api/v1/auth/entra/callback"
        assert config.allowed_domains == []

    def test_create_entra_config_has_single_logout_false_by_default(self) -> None:
        # Given / When
        config = EntraConfig(
            client_id="client-id",
            client_secret="client-secret",
            tenant_id="tenant-id",
            redirect_uri="https://app.example.com/api/v1/auth/entra/callback",
            allowed_domains=[],
        )

        # Then
        assert config.single_logout is False

    def test_create_entra_config_has_no_secret_expiry_by_default(self) -> None:
        # Given / When
        config = EntraConfig(
            client_id="client-id",
            client_secret="client-secret",
            tenant_id="tenant-id",
            redirect_uri="https://app.example.com/api/v1/auth/entra/callback",
            allowed_domains=[],
        )

        # Then
        assert config.client_secret_expires_at is None

    def test_is_secret_expiring_soon_returns_false_when_no_expiry_set(self) -> None:
        # Given
        config = EntraConfig(
            client_id="client-id",
            client_secret="client-secret",
            tenant_id="tenant-id",
            redirect_uri="https://app.example.com/api/v1/auth/entra/callback",
            allowed_domains=[],
        )

        # When / Then
        assert config.is_secret_expiring_soon() is False

    def test_is_secret_expiring_soon_returns_true_when_expiry_within_threshold(self) -> None:
        # Given
        expires_soon = datetime.now(UTC) + timedelta(days=10)
        config = EntraConfig(
            client_id="client-id",
            client_secret="client-secret",
            tenant_id="tenant-id",
            redirect_uri="https://app.example.com/api/v1/auth/entra/callback",
            allowed_domains=[],
            client_secret_expires_at=expires_soon,
        )

        # When / Then
        assert config.is_secret_expiring_soon(threshold_days=30) is True

    def test_is_secret_expiring_soon_returns_false_when_expiry_beyond_threshold(self) -> None:
        # Given
        expires_later = datetime.now(UTC) + timedelta(days=60)
        config = EntraConfig(
            client_id="client-id",
            client_secret="client-secret",
            tenant_id="tenant-id",
            redirect_uri="https://app.example.com/api/v1/auth/entra/callback",
            allowed_domains=[],
            client_secret_expires_at=expires_later,
        )

        # When / Then
        assert config.is_secret_expiring_soon(threshold_days=30) is False

    def test_is_secret_expiring_soon_returns_true_when_already_expired(self) -> None:
        # Given
        already_expired = datetime.now(UTC) - timedelta(days=1)
        config = EntraConfig(
            client_id="client-id",
            client_secret="client-secret",
            tenant_id="tenant-id",
            redirect_uri="https://app.example.com/api/v1/auth/entra/callback",
            allowed_domains=[],
            client_secret_expires_at=already_expired,
        )

        # When / Then
        assert config.is_secret_expiring_soon() is True

    def test_is_domain_allowed_returns_true_when_no_restriction(self) -> None:
        # Given — liste vide = aucune restriction
        config = EntraConfig(
            client_id="client-id",
            client_secret="client-secret",
            tenant_id="tenant-id",
            redirect_uri="https://app.example.com/api/v1/auth/entra/callback",
            allowed_domains=[],
        )

        # When / Then
        assert config.is_domain_allowed("anyone@anydomain.com") is True

    def test_is_domain_allowed_returns_true_for_matching_domain(self) -> None:
        # Given
        config = EntraConfig(
            client_id="client-id",
            client_secret="client-secret",
            tenant_id="tenant-id",
            redirect_uri="https://app.example.com/api/v1/auth/entra/callback",
            allowed_domains=["waat.fr"],
        )

        # When / Then
        assert config.is_domain_allowed("j.buget.ext@waat.fr") is True

    def test_is_domain_allowed_returns_false_for_non_matching_domain(self) -> None:
        # Given
        config = EntraConfig(
            client_id="client-id",
            client_secret="client-secret",
            tenant_id="tenant-id",
            redirect_uri="https://app.example.com/api/v1/auth/entra/callback",
            allowed_domains=["waat.fr"],
        )

        # When / Then
        assert config.is_domain_allowed("j.buget@pix.fr") is False

    def test_is_domain_allowed_supports_multiple_domains(self) -> None:
        # Given
        config = EntraConfig(
            client_id="client-id",
            client_secret="client-secret",
            tenant_id="tenant-id",
            redirect_uri="https://app.example.com/api/v1/auth/entra/callback",
            allowed_domains=["waat.fr", "client.com"],
        )

        # When / Then
        assert config.is_domain_allowed("user@waat.fr") is True
        assert config.is_domain_allowed("user@client.com") is True
        assert config.is_domain_allowed("user@other.com") is False
