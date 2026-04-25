from datetime import datetime


class NoopInvitationEmailService:
    """No-op email service for development and testing."""

    async def send_invitation_email(
        self,
        to_email: str,
        organization_name: str,
        inviter_name: str,
        invitation_token: str,
        expires_at: datetime,
        locale: str = "fr",
    ) -> None:
        pass
