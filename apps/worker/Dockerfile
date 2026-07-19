FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends git \
  && rm -rf /var/lib/apt/lists/*

COPY apps/api /opt/codeintel/api
COPY apps/worker /opt/codeintel/worker

RUN pip install --no-cache-dir -e /opt/codeintel/api -e /opt/codeintel/worker

WORKDIR /opt/codeintel/worker
ENV PYTHONPATH=/opt/codeintel/api
CMD ["python", "-m", "worker"]
