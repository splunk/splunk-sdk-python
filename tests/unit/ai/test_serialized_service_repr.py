from splunklib.ai.serialized_service import SerializedService


class TestSerializedServiceRepr:
    def test_repr_excludes_password(self) -> None:
        s = SerializedService(password="super_secret_password")
        assert "super_secret_password" not in repr(s)

    def test_repr_excludes_token(self) -> None:
        s = SerializedService(token="tok_abc123")
        assert "tok_abc123" not in repr(s)

    def test_repr_excludes_bearer_token(self) -> None:
        s = SerializedService(bearer_token="bearer_xyz789")
        assert "bearer_xyz789" not in repr(s)

    def test_repr_excludes_auth_cookies(self) -> None:
        s = SerializedService(auth_cookies={"session": "cookie_secret"})
        assert "cookie_secret" not in repr(s)

    def test_str_excludes_credentials(self) -> None:
        s = SerializedService(
            password="secret_pw",
            token="secret_tok",
            bearer_token="secret_bearer",
            auth_cookies={"key": "secret_cookie"},
        )
        text = str(s)
        assert "secret_pw" not in text
        assert "secret_tok" not in text
        assert "secret_bearer" not in text
        assert "secret_cookie" not in text

    def test_repr_includes_non_sensitive_fields(self) -> None:
        s = SerializedService(
            management_url="https://localhost:8089",
            username="admin",
        )
        text = repr(s)
        assert "https://localhost:8089" in text
        assert "admin" in text
