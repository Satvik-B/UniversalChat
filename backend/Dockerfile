# Stage 1: Build
FROM python:3.10-slim as builder
WORKDIR /app
COPY pyproject.toml .
RUN pip install poetry
RUN poetry config virtualenvs.create false && poetry install --no-dev

# Stage 2: Production
FROM python:3.10-slim
WORKDIR /app
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
