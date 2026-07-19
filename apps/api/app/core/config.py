from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = "local"
    database_url: str = "postgresql+psycopg://codeintel:codeintel@localhost:5434/codeintel"
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    # Job queue
    worker_id: str = "worker-local"
    job_lease_seconds: int = 60
    job_retry_delay_seconds: int = 30
    worker_poll_interval_seconds: float = 2.0

    # Secure clone
    git_clone_timeout_seconds: int = 120
    git_clone_max_bytes: int = 50 * 1024 * 1024
    git_clone_base_dir: str = "/tmp/codeintel-clones"

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


settings = Settings()
