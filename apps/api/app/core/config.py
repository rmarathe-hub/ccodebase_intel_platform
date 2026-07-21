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

    # Discovery (Week 3)
    discovery_max_file_bytes: int = 1_048_576  # 1 MiB per file
    discovery_max_files: int = 50_000
    discovery_binary_sample_bytes: int = 8192

    # Optional LLM enrichment — disabled by default; CI must keep off.
    # Primary provider when enabled: azure_openai (LangChain thin adapter / direct SDK).
    llm_enrichment_enabled: bool = False
    llm_provider: str = "none"  # none | azure_openai | openai | anthropic | ollama
    llm_model: str = ""
    llm_api_key: str = ""
    llm_api_base: str = ""
    llm_temperature: float = 0.0
    llm_timeout_seconds: float = 60.0
    llm_max_retries: int = 2
    llm_prompt_version: str = "1"
    llm_max_requests_per_job: int = 50
    llm_max_tokens_per_file: int = 4_000
    llm_max_tokens_per_repository: int = 100_000
    llm_max_tokens_per_job: int = 80_000
    llm_max_estimated_cost_usd_per_job: float = 0.50
    llm_daily_budget_usd: float = 5.0
    llm_kill_switch: bool = False
    # Batching: never default to one call per chunk.
    llm_max_chunks_per_request: int = 12
    llm_orchestration: str = "auto"  # auto | langchain | direct_sdk

    # Azure OpenAI (when llm_provider=azure_openai)
    azure_openai_endpoint: str = ""
    azure_openai_api_key: str = ""
    azure_openai_api_version: str = "2024-10-21"
    azure_openai_deployment: str = ""
    azure_openai_embedding_deployment: str = ""

    # Embeddings (Week 9) — local deterministic provider by default; CI-safe.
    embeddings_enabled: bool = True
    embedding_provider: str = "local"  # local | azure_openai | none
    embedding_model: str = "local-hash-v1"
    embedding_version: str = "9.2"
    embedding_dimensions: int = 1536
    embedding_batch_size: int = 32
    # Hybrid fusion weights (must sum to ~1.0 aside from path boost).
    hybrid_w_exact: float = 0.50
    hybrid_w_semantic: float = 0.50

    # Week 10 Ask/RAG candidate retrieval + rerank (Days 1–2).
    ask_candidate_exact_limit: int = 30
    ask_candidate_semantic_limit: int = 30
    ask_rrf_k: int = 60
    ask_rerank_enabled: bool = True
    ask_rerank_max_candidates: int = 40
    ask_rerank_prompt_version: str = "10.1"
    # CI/default: deterministic mock rerank unless Azure chat deployment is configured
    # and ask_rerank_use_mock is explicitly false.
    ask_rerank_use_mock: bool = True

    # Week 10 Days 3–4: query rewrite + context expansion.
    ask_query_rewrite_enabled: bool = True
    ask_query_max_rewrites: int = 4
    ask_context_token_budget: int = 6000
    ask_expand_seed_limit: int = 5
    ask_expand_neighbor_limit: int = 2
    ask_expand_relation_limit: int = 4
    ask_expand_low_confidence_score: float = 0.02

    # Week 10 Day 5: grounded Ask endpoint (opt-in; mock by default for CI).
    ask_enabled: bool = True
    ask_use_mock: bool = True
    ask_prompt_version: str = "10.5"
    ask_cache_enabled: bool = True
    ask_max_requests_per_call: int = 2
    ask_max_tokens_per_call: int = 16_000
    ask_max_estimated_cost_usd: float = 0.10

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def llm_enrichment_active(self) -> bool:
        """True only when explicitly enabled and not killed."""
        return (
            self.llm_enrichment_enabled
            and not self.llm_kill_switch
            and self.llm_provider not in {"", "none"}
        )

    @property
    def embeddings_active(self) -> bool:
        """True when embedding stage should persist vectors."""
        return (
            self.embeddings_enabled
            and self.embedding_provider not in {"", "none"}
        )

    @property
    def azure_openai_configured(self) -> bool:
        return bool(
            self.azure_openai_endpoint.strip()
            and (self.azure_openai_api_key.strip() or self.llm_api_key.strip())
            and self.azure_openai_deployment.strip()
        )

    @property
    def azure_openai_embeddings_configured(self) -> bool:
        return bool(
            self.azure_openai_endpoint.strip()
            and (self.azure_openai_api_key.strip() or self.llm_api_key.strip())
            and self.azure_openai_embedding_deployment.strip()
        )


settings = Settings()
