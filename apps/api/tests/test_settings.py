from app.core.config import Settings


def test_cors_origin_list_parsing() -> None:
    settings = Settings(cors_origins="http://localhost:5173, http://127.0.0.1:5173")
    assert settings.cors_origin_list == [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]
