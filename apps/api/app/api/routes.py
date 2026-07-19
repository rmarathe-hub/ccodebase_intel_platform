from fastapi import APIRouter

from app.db.session import check_database

router = APIRouter()


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/ready")
def ready() -> dict[str, str | bool]:
    db_ok = check_database()
    return {
        "status": "ready" if db_ok else "not_ready",
        "database": db_ok,
    }
