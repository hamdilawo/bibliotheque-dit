"""
Guards Litestar — protection JWT pour les endpoints d'écriture.
"""
import jwt
from litestar.connection import ASGIConnection
from litestar.exceptions import NotAuthorizedException
from litestar.handlers import BaseRouteHandler

from core.settings import get_settings


async def jwt_guard(connection: ASGIConnection, handler: BaseRouteHandler) -> None:
    """Vérifie le JWT dans le header Authorization. Réservé aux admins (STAFF)."""
    auth_header = connection.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise NotAuthorizedException("Token d'authentification manquant.")

    token = auth_header.removeprefix("Bearer ").strip()
    settings = get_settings()

    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        raise NotAuthorizedException("Token expiré.")
    except jwt.InvalidTokenError:
        raise NotAuthorizedException("Token invalide.")

    role = payload.get("role", "")
    if role != "STAFF":
        raise NotAuthorizedException("Accès réservé au personnel DIT (STAFF).")
