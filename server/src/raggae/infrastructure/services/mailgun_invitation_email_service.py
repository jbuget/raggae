import logging
from datetime import datetime

import httpx

logger = logging.getLogger(__name__)

_STRINGS: dict[str, dict[str, str]] = {
    "fr": {
        "subject": "Invitation à rejoindre {organization_name}",
        "heading": "Vous avez été invité(e) à rejoindre {organization_name}",
        "body": "{inviter_name} vous invite à rejoindre {organization_name} sur {app_name}.",
        "cta": "Accepter l'invitation",
        "expires": "Ce lien expire le {expires_str}.",
        "ignore": "Si vous ne souhaitez pas rejoindre cette organisation, ignorez ce message.",
        "direct_link": "Lien direct :",
        "expires_format": "%d/%m/%Y à %H:%M UTC",
    },
    "en": {
        "subject": "You've been invited to join {organization_name}",
        "heading": "You've been invited to join {organization_name}",
        "body": "{inviter_name} has invited you to join {organization_name} on {app_name}.",
        "cta": "Accept invitation",
        "expires": "This link expires on {expires_str}.",
        "ignore": "If you don't want to join this organization, simply ignore this email.",
        "direct_link": "Direct link:",
        "expires_format": "%m/%d/%Y at %H:%M UTC",
    },
}
_FALLBACK_LOCALE = "fr"


class MailgunInvitationEmailService:
    def __init__(
        self,
        api_key: str,
        domain: str,
        from_email: str,
        frontend_url: str,
        app_name: str,
        api_base: str = "https://api.mailgun.net/v3",
    ) -> None:
        self._api_key = api_key
        self._domain = domain
        self._from_email = from_email
        self._frontend_url = frontend_url
        self._app_name = app_name
        self._api_base = api_base

    async def send_invitation_email(
        self,
        to_email: str,
        organization_name: str,
        inviter_name: str,
        invitation_token: str,
        expires_at: datetime,
        locale: str = "fr",
    ) -> None:
        strings = _STRINGS.get(locale, _STRINGS[_FALLBACK_LOCALE])
        acceptance_url = f"{self._frontend_url}/invitations/accept?token={invitation_token}"
        expires_str = expires_at.strftime(strings["expires_format"])
        subject = strings["subject"].format(organization_name=organization_name)
        html_body = self._html(
            strings, organization_name, inviter_name, acceptance_url, expires_str, self._app_name
        )
        text_body = self._text(
            strings, organization_name, inviter_name, acceptance_url, expires_str, self._app_name
        )
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
        strings: dict[str, str],
        organization_name: str,
        inviter_name: str,
        acceptance_url: str,
        expires_str: str,
        app_name: str,
    ) -> str:
        heading = strings["heading"].format(organization_name=organization_name)
        body = strings["body"].format(
            inviter_name=inviter_name,
            organization_name=organization_name,
            app_name=app_name,
        )
        expires = strings["expires"].format(expires_str=expires_str)
        return (
            "<!DOCTYPE html>"
            "<html>"
            '<head><meta charset="UTF-8"><title>Invitation</title></head>'
            '<body style="font-family:sans-serif;max-width:600px;margin:0 auto;padding:24px;color:#1a1a1a">'
            f"  <h2>{heading}</h2>"
            f"  <p>{body}</p>"
            '  <p style="margin:32px 0">'
            f'    <a href="{acceptance_url}"'
            '       style="background:#4f46e5;color:#fff;padding:12px 24px;'
            'border-radius:6px;text-decoration:none;font-weight:600">'
            f"      {strings['cta']}"
            "    </a>"
            "  </p>"
            f'  <p style="font-size:13px;color:#6b7280">{expires}</p>'
            '  <hr style="border:none;border-top:1px solid #e5e7eb;margin:24px 0">'
            '  <p style="font-size:12px;color:#9ca3af">'
            f"    {strings['ignore']}<br>"
            f"    {strings['direct_link']} {acceptance_url}"
            "  </p>"
            "</body>"
            "</html>"
        )

    @staticmethod
    def _text(
        strings: dict[str, str],
        organization_name: str,
        inviter_name: str,
        acceptance_url: str,
        expires_str: str,
        app_name: str,
    ) -> str:
        body = strings["body"].format(
            inviter_name=inviter_name,
            organization_name=organization_name,
            app_name=app_name,
        )
        expires = strings["expires"].format(expires_str=expires_str)
        return f"{body}\n\n{strings['cta']}: {acceptance_url}\n\n{expires}\n\n{strings['ignore']}"
