from decouple import config

SECRET_KEY = config(
    'SECRET_KEY', default='django-insecure-emprunts-service-key')
# DEBUG = config('DEBUG', default=True, cast=bool)
DEBUG = True
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='*').split(',')

INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'rest_framework',
    'corsheaders',
    'drf_spectacular',
    'loans',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    "loans.adapters.middlewares.jwt_auth.JWTAuthMiddleware",
]

ROOT_URLCONF = 'drf.urls'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'emprunts_db',
        'USER': 'postgres',
        'PASSWORD': config('DB_PASSWORD', default='postgres'),  # <-- Force le ici
        'HOST': '127.0.0.1',
        'PORT': 25432,
    }
}

REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],

    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    "DEFAULT_AUTHENTICATION_CLASSES": [],
    "DEFAULT_PERMISSION_CLASSES": [],
    "UNAUTHENTICATED_USER": None
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'Service Emprunts API',
    'DESCRIPTION': 'API de gestion des emprunts — Bibliothèque DIT',
    'VERSION': '1.0.0',
}


# URLs des autres microservices
SERVICE_LIVRES_URL = config('SERVICE_LIVRES_URL', default='http://livres:8001')
SERVICE_UTILISATEURS_URL = config(
    'SERVICE_UTILISATEURS_URL', default='http://utilisateurs:8002')

CORS_ALLOW_ALL_ORIGINS = True
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
LANGUAGE_CODE = 'fr-fr'
TIME_ZONE = 'Africa/Dakar'
USE_TZ = True

# Models/Migrations
MIGRATION_MODULES = {
    'loans': 'loans.adapters.database.migrations',
}


# JWT Settings
JWT_SECRET_KEY = config(
    "JWT_SECRET_KEYs", "a-string-secret-at-least-256-bits-long")
JWT_ALGORITHM = "HS256"
JWT_COOKIE_NAME = "access_token"
