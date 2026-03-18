import pytest

from raggae.domain.value_objects.locale import Locale


@pytest.mark.unit
class TestLocale:
    def test_locale_en_has_value_en(self) -> None:
        assert Locale.EN == "en"

    def test_locale_fr_has_value_fr(self) -> None:
        assert Locale.FR == "fr"

    def test_locale_default_returns_en(self) -> None:
        assert Locale.default() == Locale.EN

    def test_locale_from_string_en_succeeds(self) -> None:
        assert Locale("en") == Locale.EN

    def test_locale_from_string_fr_succeeds(self) -> None:
        assert Locale("fr") == Locale.FR

    def test_locale_from_invalid_string_raises_value_error(self) -> None:
        with pytest.raises(ValueError):
            Locale("de")
