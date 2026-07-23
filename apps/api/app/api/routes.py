from fastapi import APIRouter

from app.api.v1 import router as v1_router
from app.db.session import check_database
from app.services.index_pipeline import (
    current_index_pipeline_version,
    resolve_build_identity,
)

router = APIRouter()
router.include_router(v1_router)


@router.get("/health")
def health() -> dict[str, str]:
    return {
        "status": "ok",
        "index_pipeline_version": current_index_pipeline_version(),
        "build": resolve_build_identity(),
    }


@router.get("/ready")
def ready() -> dict[str, str | bool]:
    db_ok = check_database()
    return {
        "status": "ready" if db_ok else "not_ready",
        "database": db_ok,
        "index_pipeline_version": current_index_pipeline_version(),
        "build": resolve_build_identity(),
    }
