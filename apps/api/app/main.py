from fastapi import FastAPI

from app.api.routes import router
from app.core.config import settings


def create_app() -> FastAPI:
    application = FastAPI(
        title="Codebase Intelligence API",
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )
    application.include_router(router)
    return application


app = create_app()


@app.get("/")
def root() -> dict[str, str]:
    return {"service": "codeintel-api", "env": settings.app_env}
