from decouple import config

SECRET_KEY = config(
    'SECRET_KEY', default='django-insecure-emprunts-service-key')
# DEBUG = config('DEBUG', default=True, cast=bool)
DEBUG = True
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='*').split(',')

INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'rest_framework',
    'corsheaders',
    'drf_spectacular',
    'loans',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
]

ROOT_URLCONF = 'emprunts_service.urls'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME', default='emprunts_db'),
        'USER': config('DB_USER', default='postgres'),
        'PASSWORD': config('DB_PASSWORD', default='postgres'),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='25432'),
    }
}

REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],

    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
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
