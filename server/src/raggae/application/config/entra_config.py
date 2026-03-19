from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta


@dataclass
class EntraConfig:
    """Configuration for Microsoft Entra ID OAuth provider.

    Injected as a parameter into use cases and infrastructure services
    to allow future per-organization configuration without refactoring.
    """

    client_id: str
    client_secret: str
    tenant_id: str
    redirect_uri: str
    allowed_domains: list[str]
    single_logout: bool = field(default=False)
    client_secret_expires_at: datetime | None = field(default=None)

    def is_secret_expiring_soon(self, threshold_days: int = 30) -> bool:
        """Return True if the client secret expires within threshold_days."""
        if self.client_secret_expires_at is None:
            return False
        return self.client_secret_expires_at <= datetime.now(UTC) + timedelta(days=threshold_days)

    def is_domain_allowed(self, email: str) -> bool:
        """Return True if the email domain is in the allowed list.

        An empty allowed_domains list means no restriction.
        """
        if not self.allowed_domains:
            return True
        domain = email.split("@")[-1]
        return domain in self.allowed_domains
