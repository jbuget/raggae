from enum import StrEnum


class Locale(StrEnum):
    """Supported UI locales."""

    EN = "en"
    FR = "fr"

    @classmethod
    def default(cls) -> "Locale":
        return cls.EN
