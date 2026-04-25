# ── Dockerfile — Service Recommandation (multi-stage) ────────
# Stage 1 : builder — installe les dépendances lourdes (sklearn, numpy)
FROM python:3.11-slim AS builder

WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Stage 2 : runtime — image finale légère
FROM python:3.11-slim AS runtime

# Utilisateur non-root
RUN groupadd -r appuser && useradd -r -g appuser appuser

WORKDIR /app

# Copier uniquement les packages installés depuis le builder
COPY --from=builder /install /usr/local

# Code source
COPY . .

# Dossiers pour les données et le modèle
RUN mkdir -p /app/data /app/model && \
    chown -R appuser:appuser /app

USER appuser

EXPOSE 8004

# Uvicorn avec 1 worker (modèle en mémoire partagée)
CMD ["uvicorn", "app.main:app", \
     "--host", "0.0.0.0", \
     "--port", "8004", \
     "--workers", "1", \
     "--log-level", "info"]
