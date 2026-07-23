# Architecture

## Pipeline

1. Ingestion loads BTS flights and METAR weather
2. Airflow orchestrates daily loads
3. dbt builds staging → intermediate → marts
4. Dashboard reads marts for delay risk views

## Key models

- `int_flights__weather_at_departure` — nearest weather at origin departure
- `fct_flights` — analysis grain

## Not in scope yet

Kubernetes and Redis are not part of this repository.
