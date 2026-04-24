from datetime import datetime
from typing import Protocol


class InvitationEmailService(Protocol):
    async def send_invitation_email(
        self,
        to_email: str,
        organization_name: str,
        inviter_name: str,
        invitation_token: str,
        expires_at: datetime,
    ) -> None: ...
