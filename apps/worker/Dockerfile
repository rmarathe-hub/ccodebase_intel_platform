FROM python:3.12-slim

WORKDIR /app

COPY apps/worker/pyproject.toml ./
COPY apps/worker/worker ./worker

RUN pip install --no-cache-dir -e .

CMD ["python", "-m", "worker"]
