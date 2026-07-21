FROM python:3.12-slim AS base
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

FROM base AS runtime
COPY . .
CMD ["python", "main.py"]
