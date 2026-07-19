from fastapi import APIRouter

from app.api.v1 import router as v1_router
from app.db.session import check_database

router = APIRouter()
router.include_router(v1_router)


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
