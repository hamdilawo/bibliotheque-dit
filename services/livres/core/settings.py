"""
Configuration centralisée du service Livres.
Toutes les variables d'environnement sont lues ici.
"""
from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # ─── Application ─────────────────────────────────────────
    app_name: str = "Service Livres API"
    app_version: str = "2.0.0"
    debug: bool = True

    # ─── Base de données PostgreSQL ───────────────────────────
    db_host: str = "db"
    db_port: int = 5432
    db_name: str = "livres_db"
    db_user: str = "postgres"
    db_password: str = "postgres"

    # ─── CORS ────────────────────────────────────────────────
    cors_allow_origins: list[str] = ["http://localhost:3000"]

    # ─── MinIO ───────────────────────────────────────────────
    minio_endpoint: str = "minio:9000"
    minio_access_key: str = "minioadmin"
    minio_secret_key: str = "minioadmin123"
    minio_bucket_couvertures: str = "couvertures"
    minio_use_ssl: bool = False
    minio_public_url: str = "http://localhost:9000"

    @property
    def db_url(self) -> str:
        return (
            f"postgresql://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


@lru_cache
def get_settings() -> Settings:
    """Retourne les settings (mis en cache)."""
    return Settings()
