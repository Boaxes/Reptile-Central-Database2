from backend import db


def test_bot_connection_config_uses_ai_credentials(monkeypatch):
    class NoSecrets:
        def get(self, _key):
            raise RuntimeError("No test secrets")

    monkeypatch.setattr(db.st, "secrets", NoSecrets())
    monkeypatch.setenv("MYSQL_HOST", "127.0.0.1")
    monkeypatch.setenv("MYSQL_PORT", "3306")
    monkeypatch.setenv("MYSQL_DATABASE", "sql3817488")
    monkeypatch.setenv("MYSQL_USER", "app_user")
    monkeypatch.setenv("MYSQL_PASSWORD", "app_password")
    monkeypatch.setenv("AI_MYSQL_USER", "BOT")
    monkeypatch.setenv("AI_MYSQL_PASSWORD", "bot_password")
    monkeypatch.delenv("CLOUD_SQL_CONNECTION_NAME", raising=False)

    config = db._bot_connection_config()

    assert config["user"] == "BOT"
    assert config["password"] == "bot_password"
