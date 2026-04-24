import logging
from datetime import datetime

import httpx

logger = logging.getLogger(__name__)


class MailgunInvitationEmailService:
    def __init__(
        self,
        api_key: str,
        domain: str,
        from_email: str,
        frontend_url: str,
        api_base: str = "https://api.mailgun.net/v3",
    ) -> None:
        self._api_key = api_key
        self._domain = domain
        self._from_email = from_email
        self._frontend_url = frontend_url
        self._api_base = api_base
        self._app_name = domain

    async def send_invitation_email(
        self,
        to_email: str,
        organization_name: str,
        inviter_name: str,
        invitation_token: str,
        expires_at: datetime,
    ) -> None:
        acceptance_url = f"{self._frontend_url}/invitations/accept?token={invitation_token}"
        expires_str = expires_at.strftime("%d/%m/%Y à %H:%M UTC")
        subject = f"Invitation à rejoindre {organization_name}"
        html_body = self._html(organization_name, inviter_name, acceptance_url, expires_str, self._app_name)
        text_body = self._text(organization_name, inviter_name, acceptance_url, expires_str, self._app_name)
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self._api_base}/{self._domain}/messages",
                auth=("api", self._api_key),
                data={
                    "from": self._from_email,
                    "to": to_email,
                    "subject": subject,
                    "html": html_body,
                    "text": text_body,
                },
            )
            if not response.is_success:
                logger.error(
                    "mailgun_api_error status=%s body=%s",
                    response.status_code,
                    response.text,
                )
            response.raise_for_status()

    @staticmethod
    def _html(
        organization_name: str,
        inviter_name: str,
        acceptance_url: str,
        expires_str: str,
        app_name: str,
    ) -> str:
        return (
            "<!DOCTYPE html>"
            '<html lang="fr">'
            '<head><meta charset="UTF-8"><title>Invitation</title></head>'
            '<body style="font-family:sans-serif;max-width:600px;margin:0 auto;padding:24px;color:#1a1a1a">'
            f"  <h2>Vous avez été invité(e) à rejoindre <strong>{organization_name}</strong></h2>"
            f"  <p><strong>{inviter_name}</strong> vous invite à rejoindre"
            f" <strong>{organization_name}</strong> sur {app_name}.</p>"
            '  <p style="margin:32px 0">'
            f'    <a href="{acceptance_url}"'
            '       style="background:#4f46e5;color:#fff;padding:12px 24px;'
            'border-radius:6px;text-decoration:none;font-weight:600">'
            "      Accepter l'invitation"
            "    </a>"
            "  </p>"
            f'  <p style="font-size:13px;color:#6b7280">Ce lien expire le {expires_str}.</p>'
            '  <hr style="border:none;border-top:1px solid #e5e7eb;margin:24px 0">'
            '  <p style="font-size:12px;color:#9ca3af">'
            "    Si vous ne souhaitez pas rejoindre cette organisation, ignorez ce message.<br>"
            f"    Lien direct : {acceptance_url}"
            "  </p>"
            "</body>"
            "</html>"
        )

    @staticmethod
    def _text(
        organization_name: str,
        inviter_name: str,
        acceptance_url: str,
        expires_str: str,
        app_name: str,
    ) -> str:
        return (
            f"{inviter_name} vous invite à rejoindre {organization_name} sur {app_name}.\n\n"
            f"Accepter l'invitation : {acceptance_url}\n\n"
            f"Ce lien expire le {expires_str}.\n\n"
            "Si vous ne souhaitez pas rejoindre cette organisation, ignorez ce message."
        )
