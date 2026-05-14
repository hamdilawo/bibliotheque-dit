
FROM python:3.12-slim

RUN groupadd -r appuser && useradd -r -g appuser appuser

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt


COPY . .
COPY entrypoint.sh /entrypoint.sh

RUN chown -R appuser:appuser /app

RUN chmod +x /entrypoint.sh && chown appuser:appuser /entrypoint.sh

USER appuser


EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
