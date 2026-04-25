import logging
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from raggae.infrastructure.services.mailgun_invitation_email_service import (
    MailgunInvitationEmailService,
    _obfuscate_email,
)


class TestObfuscateEmail:
    def test_obfuscate_standard_email(self) -> None:
        # Given / When / Then
        assert _obfuscate_email("john@gmail.com") == "j***@g****.com"

    def test_obfuscate_single_char_local(self) -> None:
        # Given / When / Then
        assert _obfuscate_email("j@example.com") == "j*@e******.com"

    def test_obfuscate_long_local_and_domain(self) -> None:
        # Given
        result = _obfuscate_email("jeremy.buget@waat.fr")
        # When / Then
        assert result.startswith("j")
        assert "@" in result
        assert result.endswith(".fr")
        assert "jeremy" not in result
        assert "waat" not in result

    def test_obfuscate_no_at_sign_returns_placeholder(self) -> None:
        # Given / When / Then
        assert _obfuscate_email("notanemail") == "***"

    def test_obfuscate_domain_without_tld(self) -> None:
        # Given / When / Then
        result = _obfuscate_email("user@localhost")
        assert result.startswith("u")
        assert "@" in result
        assert "localhost" not in result


class TestMailgunInvitationEmailServiceLogging:
    @pytest.fixture
    def service(self) -> MailgunInvitationEmailService:
        return MailgunInvitationEmailService(
            api_key="test-key",
            domain="sandbox.mailgun.net",
            from_email="noreply@example.com",
            frontend_url="http://localhost:3000",
            app_name="Raggae",
        )

    async def test_send_invitation_email_logs_obfuscated_email(
        self, service: MailgunInvitationEmailService, caplog: pytest.LogCaptureFixture
    ) -> None:
        # Given
        mock_response = MagicMock()
        mock_response.is_success = True
        mock_response.raise_for_status = MagicMock()

        mock_client = AsyncMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        mock_client.post = AsyncMock(return_value=mock_response)

        # When
        with patch("httpx.AsyncClient", return_value=mock_client):
            with caplog.at_level(logging.INFO):
                await service.send_invitation_email(
                    to_email="john@gmail.com",
                    organization_name="Acme Corp",
                    inviter_name="Jane Doe",
                    invitation_token="tok-abc",
                    expires_at=datetime(2026, 5, 1, 12, 0, tzinfo=UTC),
                )

        # Then
        sending_logs = [r for r in caplog.records if "invitation_email_sending" in r.message]
        sent_logs = [r for r in caplog.records if "invitation_email_sent" in r.message]
        assert len(sending_logs) == 1
        assert len(sent_logs) == 1
        assert "j***@g****.com" in sending_logs[0].message
        assert "Acme Corp" in sending_logs[0].message
        assert "j***@g****.com" in sent_logs[0].message
        assert "john@gmail.com" not in sending_logs[0].message
        assert "john@gmail.com" not in sent_logs[0].message
