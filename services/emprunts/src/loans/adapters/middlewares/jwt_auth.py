import jwt
from django.conf import settings
from django.http import JsonResponse

from src.loans.app.domain.user import User


class JWTAuthMiddleware:
    """
    Middleware DRF — lit le JWT depuis un cookie HttpOnly,
    injecte user_id, user_email, user_role dans la request.
    """

    EXCLUDED_PATHS = ["/", "/api/docs/", "/api/schema/"]

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path in self.EXCLUDED_PATHS:
            return self.get_response(request)

        token = request.COOKIES.get(settings.JWT_COOKIE_NAME)

        if not token:
            auth_header = request.headers.get("Authorization", "")
            if auth_header.startswith("Bearer "):
                token = auth_header.removeprefix("Bearer ").strip()

        if not token:
            return JsonResponse(
                {"error": "Authentification requise (cookie ou header Authorization)."},
                status=401,
            )

        try:
            payload = jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM],
            )
        except jwt.ExpiredSignatureError:
            return JsonResponse({"error": "Token expiré."}, status=401)
        except jwt.InvalidTokenError as exc:
            return JsonResponse({"error": f"Token invalide : {exc}"}, status=401)

        try:
            user = User(
                id=str(payload["user_id"]),
                name=payload.get("full_name", "Unknown"),
                email=payload["email"],
                role=payload["role"],
            )
            request.authenticated_user = user
        except KeyError as exc:
            return JsonResponse({"error": f"Payload JWT manquant la clé : {exc}"}, status=401)

        return self.get_response(request)
