"""Airflow DAG entrypoint for BTS + weather ingest."""


def create_etl_dag():
    return {"dag_id": "aerodelay_etl", "schedule": "@daily"}
