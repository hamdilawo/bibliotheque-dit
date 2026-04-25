# ── Dockerfile — Service Livres ──────────────────────────────
FROM python:3.11-slim AS base

# Utilisateur non-root (bonne pratique sécurité)
RUN groupadd -r appuser && useradd -r -g appuser appuser

WORKDIR /app

# Dépendances système
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev gcc \
    && rm -rf /var/lib/apt/lists/*

# Dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Code source
COPY . .

# Permissions
RUN chown -R appuser:appuser /app
USER appuser

EXPOSE 8001

CMD ["python", "-m", "gunicorn", "livres_service.wsgi:application", \
     "--bind", "0.0.0.0:8001", "--workers", "2", "--timeout", "60"]
