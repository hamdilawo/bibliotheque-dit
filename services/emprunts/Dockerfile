# ───────────────────────────────────────────
# Stage 1 — Builder
# ───────────────────────────────────────────
FROM python:3.14-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev gcc \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:0.6.14 /uv /usr/local/bin/uv

COPY pyproject.toml uv.lock ./

RUN uv sync --frozen --no-install-project --no-dev

COPY src ./src
COPY manage.py ./

RUN uv sync --frozen --no-dev


# ───────────────────────────────────────────
# Stage 2 — Runtime
# ───────────────────────────────────────────
FROM python:3.14-slim AS runtime

ENV UV_CACHE_DIR=/tmp/uv-cache
ENV PYTHONPATH=/app/src
ENV HOME=/tmp


RUN groupadd -r appuser && useradd -r -g appuser appuser

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*


COPY --from=ghcr.io/astral-sh/uv:0.6.14 /uv /usr/local/bin/uv

COPY --from=builder /app/.venv /app/.venv

COPY src ./src
COPY manage.py ./
COPY entrypoint.sh /entrypoint.sh

RUN chmod +x /entrypoint.sh && chown appuser:appuser /entrypoint.sh


RUN chown -R appuser:appuser /app
USER appuser

EXPOSE 8000
CMD ["uv", "run", "python", "manage.py", "runserver", "0.0.0.0:8000"]

