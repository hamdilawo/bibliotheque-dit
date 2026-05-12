"""
Point d'entrée Litestar — Service Livres.
"""
from litestar import Litestar
from litestar.config.cors import CORSConfig
from litestar.openapi import OpenAPIConfig
from litestar.openapi.plugins import ScalarRenderPlugin

from core.settings import get_settings
from core.docs_auth import SECURITY_COMPONENTS, TAGS
from features.books.controller import LivreController, CategorieController, health_check

settings = get_settings()

# ─── CORS ────────────────────────────────────────────────────
cors_config = CORSConfig(
    allow_origins=settings.cors_allow_origins,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["Content-Type", "Authorization"],
)

# ─── OpenAPI / Scalar ────────────────────────────────────────
openapi_config = OpenAPIConfig(
    title=settings.app_name,
    version=settings.app_version,
    description="API de gestion des livres — Bibliothèque Numérique DIT",
    components=SECURITY_COMPONENTS,
    tags=TAGS,
    render_plugins=[ScalarRenderPlugin(path="/scalar")],
)


# ─── Lifecycle ───────────────────────────────────────────────
async def on_startup() -> None:
    """Vérification des connexions DB et MinIO au démarrage."""
    from features.books.tables import Livre
    from core.storage import get_minio_client, _ensure_bucket

    try:
        await Livre.count()
        print("✓ Connexion PostgreSQL OK")
    except Exception as e:
        print(f"✗ Erreur DB : {e}")

    try:
        _ensure_bucket(settings.minio_bucket_couvertures)
        print(f"✓ MinIO OK — bucket '{settings.minio_bucket_couvertures}' prêt")
    except Exception as e:
        print(f"✗ Erreur MinIO : {e}")


# ─── Application ─────────────────────────────────────────────
app = Litestar(
    route_handlers=[
        health_check,
        LivreController,
        CategorieController,
    ],
    cors_config=cors_config,
    openapi_config=openapi_config,
    on_startup=[on_startup],
    debug=settings.debug,
)
