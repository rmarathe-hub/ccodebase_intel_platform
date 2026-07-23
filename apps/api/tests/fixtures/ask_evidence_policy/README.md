# AeroDelay Intelligence Pipeline (fixture)

Production-style **ELT pipeline** that joins flight on-time performance with
airport weather to analyze **delay risk**.

## Start here

1. Read this README
2. Read `docs/ARCHITECTURE.md`
3. Inspect `docker-compose.yml` and Airflow DAGs
4. Review dbt models under `dbt/models/`

## Stack

Airflow · Postgres · dbt · Docker · Streamlit

## Data engineering core

Implemented ingestion, weather join, and marts. ML classifier work is optional
and partially planned — do not treat proposed ML docs as shipped features.
