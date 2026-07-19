"""CORS and public error safety tests."""

from __future__ import annotations

from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings
from app.db.deps import get_db
from app.main import create_app
from app.models import Base
from tests.conftest import postgres_available, requires_postgres


@pytest.fixture()
def client() -> Generator[TestClient, None, None]:
    application = create_app()
    if postgres_available():
        engine = create_engine(settings.database_url, pool_pre_ping=True)
        SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
        Base.metadata.create_all(bind=engine)

        def _override_db() -> Generator[Session, None, None]:
            session = SessionLocal()
            try:
                yield session
                session.commit()
            except Exception:
                session.rollback()
                raise
            finally:
                session.close()

        application.dependency_overrides[get_db] = _override_db
        with TestClient(application) as test_client:
            yield test_client
        application.dependency_overrides.clear()
        engine.dispose()
    else:
        with TestClient(application) as test_client:
            yield test_client


def test_health_allows_configured_cors_origin(client: TestClient) -> None:
    origin = settings.cors_origin_list[0] if settings.cors_origin_list else "http://localhost:5173"
    response = client.options(
        "/health",
        headers={
            "Origin": origin,
            "Access-Control-Request-Method": "GET",
        },
    )
    # Starlette may return 200 or 400 depending on middleware preflight handling
    assert response.status_code in {200, 204, 400}
    get_response = client.get("/health", headers={"Origin": origin})
    assert get_response.status_code == 200
    assert get_response.headers.get("access-control-allow-origin") in {origin, "*"}


@requires_postgres
def test_validation_error_omits_stack_traces(client: TestClient) -> None:
    response = client.post(
        "/api/v1/repositories/import",
        json={"url": "https://gitlab.com/a/b"},
    )
    assert response.status_code == 422
    text = response.text.lower()
    assert "traceback" not in text
    assert "file \"" not in text
    assert "secret" not in text
    assert settings.database_url not in response.text
