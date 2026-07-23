#!/usr/bin/env python3
"""Live Azure OpenAI embedding smoke test (one short input). Opt-in only.

Uses Azure OpenAI resource endpoints (*.openai.azure.com) via AzureOpenAI client.
Does not migrate the DB, re-index, or use the production embedding provider.

Usage:
  cd apps/api
  RUN_AZURE_INTEGRATION_TESTS=true .venv/bin/python scripts/test_azure_embedding.py

Requires apps/api/.env with Azure embedding settings and EMBEDDING_DIMENSIONS.
Never prints API keys or embedding vectors.
"""

from __future__ import annotations

import math
import os
import time
from pathlib import Path
from urllib.parse import urlparse


INPUT_TEXT = "Find authentication middleware"
OPT_IN_FLAG = "RUN_AZURE_INTEGRATION_TESTS"


def _load_dotenv(path: Path) -> None:
    """Load KEY=VALUE into os.environ if not already set (no overrides)."""
    if not path.is_file():
        return
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def _endpoint_hostname(endpoint: str) -> str:
    parsed = urlparse(endpoint if "://" in endpoint else f"https://{endpoint}")
    return parsed.hostname or endpoint


def _endpoint_type(endpoint: str) -> str:
    host = _endpoint_hostname(endpoint).lower()
    if host.endswith("services.ai.azure.com"):
        return "foundry_v1"
    if host.endswith("openai.azure.com"):
        return "legacy_azure_openai"
    return "unknown"


def _normalize_azure_resource_endpoint(endpoint: str) -> str:
    raw = (endpoint or "").strip()
    if not raw:
        return raw
    parsed = urlparse(raw if "://" in raw else f"https://{raw}")
    host = (parsed.hostname or "").lower()
    if host.endswith("openai.azure.com") and parsed.scheme and parsed.netloc:
        return f"{parsed.scheme}://{parsed.netloc}"
    return raw.rstrip("/")


def _azure_error_code(exc: BaseException) -> str:
    body = getattr(exc, "body", None)
    if isinstance(body, dict):
        err = body.get("error") if isinstance(body.get("error"), dict) else body
        if isinstance(err, dict) and err.get("code"):
            return str(err["code"])
    return ""


def _fail(category: str, detail: str = "") -> int:
    print("AZURE_EMBEDDING_SMOKE_TEST=FAIL", flush=True)
    print(f"error_category={category}", flush=True)
    if detail:
        print(f"error_detail={detail[:200]}", flush=True)
    return 1


def _fail_from_exception(exc: BaseException) -> int:
    category, detail = _categorize_exception(exc)
    print("AZURE_EMBEDDING_SMOKE_TEST=FAIL", flush=True)
    print(f"error_category={category}", flush=True)
    if detail:
        print(f"error_detail={detail[:200]}", flush=True)
    status = getattr(exc, "status_code", None)
    if status is not None:
        print(f"http_status={status}", flush=True)
    azure_code = _azure_error_code(exc)
    if azure_code:
        print(f"azure_error_code={azure_code}", flush=True)
    elif detail and detail != type(exc).__name__:
        print(f"azure_error_code={detail}", flush=True)
    return 1


def _print_pre_request_diagnostics(
    *,
    endpoint: str,
    api_version: str,
    deployment: str,
    dimensions: int,
    openai_version: str,
) -> None:
    print(f"endpoint_hostname={_endpoint_hostname(endpoint)}", flush=True)
    print(f"endpoint_type={_endpoint_type(endpoint)}", flush=True)
    print(f"azure_endpoint={endpoint.rstrip('/')}/", flush=True)
    print(f"api_version={api_version}", flush=True)
    print(f"model={deployment}", flush=True)
    print(f"openai_sdk_version={openai_version}", flush=True)
    print("dimensions_sent=true", flush=True)
    print(f"dimensions_value={dimensions}", flush=True)


def _categorize_exception(exc: BaseException) -> tuple[str, str]:
    """Return (category, sanitized_extra_detail)."""
    name = type(exc).__name__
    msg = str(exc).lower()
    azure_code = _azure_error_code(exc)

    if azure_code in {"DeploymentNotFound", "unknown_model"} or "deploymentnotfound" in msg:
        return "deployment_not_found", azure_code or name
    if "authentication" in msg or "unauthorized" in msg or "401" in msg:
        return "authentication_failed", azure_code or name
    if "api version" in msg or ("version" in msg and "400" in msg):
        return "invalid_api_version", azure_code or name
    if "429" in msg or ("rate" in msg and "limit" in msg):
        return "rate_limited", azure_code or name
    if "timeout" in msg or "connection" in msg or "network" in msg:
        return "network_error", azure_code or name
    if name in {"APIConnectionError", "APITimeoutError"}:
        return "network_error", azure_code or name
    if name in {"AuthenticationError", "PermissionDeniedError"}:
        return "authentication_failed", azure_code or name
    if name in {"NotFoundError"}:
        return "deployment_not_found", azure_code or name
    if name in {"RateLimitError"}:
        return "rate_limited", azure_code or name
    return "unknown_error", azure_code or name


def main() -> int:
    if os.environ.get(OPT_IN_FLAG, "").strip().lower() not in {"1", "true", "yes"}:
        print(
            f"Skipped: set {OPT_IN_FLAG}=true to run the live Azure embedding smoke test.",
            flush=True,
        )
        return 0

    api_root = Path(__file__).resolve().parents[1]
    _load_dotenv(api_root / ".env")

    endpoint = _normalize_azure_resource_endpoint(
        os.environ.get("AZURE_OPENAI_ENDPOINT", "").strip()
    )
    api_key = os.environ.get("AZURE_OPENAI_API_KEY", "").strip() or os.environ.get(
        "LLM_API_KEY", ""
    ).strip()
    api_version = os.environ.get("AZURE_OPENAI_API_VERSION", "").strip()
    deployment = os.environ.get("AZURE_OPENAI_EMBEDDING_DEPLOYMENT", "").strip()
    dims_raw = os.environ.get("EMBEDDING_DIMENSIONS", "").strip()

    missing = [
        name
        for name, val in (
            ("AZURE_OPENAI_ENDPOINT", endpoint),
            ("AZURE_OPENAI_API_KEY", api_key),
            ("AZURE_OPENAI_API_VERSION", api_version),
            ("AZURE_OPENAI_EMBEDDING_DEPLOYMENT", deployment),
            ("EMBEDDING_DIMENSIONS", dims_raw),
        )
        if not val
    ]
    if missing:
        return _fail("missing_configuration", ",".join(missing))

    try:
        dimensions = int(dims_raw)
    except ValueError:
        return _fail("missing_configuration", "EMBEDDING_DIMENSIONS_not_int")

    if dimensions < 1:
        return _fail("missing_configuration", "EMBEDDING_DIMENSIONS_invalid")

    try:
        import openai
        from openai import AzureOpenAI
    except ImportError:
        return _fail(
            "missing_configuration",
            "openai_package_missing_install_apps_api_llm_extras",
        )

    _print_pre_request_diagnostics(
        endpoint=endpoint,
        api_version=api_version,
        deployment=deployment,
        dimensions=dimensions,
        openai_version=getattr(openai, "__version__", "unknown"),
    )

    client = AzureOpenAI(
        api_key=api_key,
        azure_endpoint=endpoint.rstrip("/") + "/",
        api_version=api_version,
        timeout=60.0,
        max_retries=0,
    )

    t0 = time.perf_counter()
    try:
        response = client.embeddings.create(
            model=deployment,
            input=[INPUT_TEXT],
            dimensions=dimensions,
        )
    except Exception as exc:  # noqa: BLE001 — classified then sanitized
        return _fail_from_exception(exc)

    elapsed_ms = int((time.perf_counter() - t0) * 1000)

    data = getattr(response, "data", None)
    if not data or len(data) != 1:
        return _fail("invalid_response", f"embedding_count={0 if not data else len(data)}")

    vector = getattr(data[0], "embedding", None)
    if not isinstance(vector, list) or not vector:
        return _fail("invalid_response", "embedding_not_list_or_empty")

    if len(vector) != dimensions:
        return _fail(
            "dimension_mismatch",
            f"got={len(vector)}_expected={dimensions}",
        )

    numeric = all(isinstance(x, (int, float)) for x in vector)
    if not numeric:
        return _fail("invalid_response", "non_numeric_values")

    finite = all(math.isfinite(float(x)) for x in vector)
    if not finite:
        return _fail("invalid_response", "non_finite_values")

    nonzero = any(float(x) != 0.0 for x in vector)
    if not nonzero:
        return _fail("invalid_response", "all_zero_vector")

    usage = getattr(response, "usage", None)
    input_tokens: str | int = "unavailable"
    if usage is not None:
        prompt_tokens = getattr(usage, "prompt_tokens", None)
        total_tokens = getattr(usage, "total_tokens", None)
        if prompt_tokens is not None:
            input_tokens = int(prompt_tokens)
        elif total_tokens is not None:
            input_tokens = int(total_tokens)

    print("http_status=200", flush=True)
    print("AZURE_EMBEDDING_SMOKE_TEST=PASS", flush=True)
    print("provider=azure_openai", flush=True)
    print(f"endpoint_type={_endpoint_type(endpoint)}", flush=True)
    print(f"deployment={deployment}", flush=True)
    print(f"dimensions={dimensions}", flush=True)
    print("input_count=1", flush=True)
    print(f"input_tokens={input_tokens}", flush=True)
    print("vector_numeric=true", flush=True)
    print("vector_finite=true", flush=True)
    print("vector_nonzero=true", flush=True)
    print(f"elapsed_ms={elapsed_ms}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
