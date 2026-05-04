"""
Connexion à PostgreSQL via Piccolo ORM.
"""
from piccolo.engine.postgres import PostgresEngine
from core.settings import get_settings

settings = get_settings()

# ─── Moteur Piccolo ───────────────────────────────────────────
DB = PostgresEngine(
    config={
        "host":     settings.db_host,
        "port":     settings.db_port,
        "database": settings.db_name,
        "user":     settings.db_user,
        "password": settings.db_password,
    }
)