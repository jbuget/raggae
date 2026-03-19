from raggae.application.interfaces.services.oauth_provider import OAuthUserInfo


class TestOAuthUserInfo:
    def test_create_oauth_user_info_with_all_fields(self) -> None:
        # Given / When
        info = OAuthUserInfo(
            provider_id="oid-abc-123",
            email="j.buget@waat.fr",
            full_name="Jérémy Buget",
            provider="entra",
        )

        # Then
        assert info.provider_id == "oid-abc-123"
        assert info.email == "j.buget@waat.fr"
        assert info.full_name == "Jérémy Buget"
        assert info.provider == "entra"
