"""
Configuration de l'authentification dans la documentation Swagger.
Permet de tester les endpoints protégés directement depuis /schema/swagger.
"""
from litestar.openapi.spec import Components, SecurityScheme, Tag


# ─── Schéma de sécurité JWT pour Swagger ─────────────────────
SECURITY_COMPONENTS = Components(
    security_schemes={
        "BearerToken": SecurityScheme(
            type="http",
            scheme="bearer",
            bearer_format="JWT",
            description="Token JWT obtenu via le service Utilisateurs (/api/auth/login)",
        )
    }
)

# ─── Tags pour organiser la documentation ────────────────────
TAGS = [
    Tag(name="livres",     description="Gestion du catalogue de livres"),
    Tag(name="categories", description="Gestion des catégories de livres"),
    Tag(name="health",     description="Santé du service"),
]