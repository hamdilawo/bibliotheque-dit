from django.urls import path, include
from rest_framework.routers import DefaultRouter
from loans.adapters.scalar.scalar import urlpatterns_scalar
from .views import EmpruntViewSet

router = DefaultRouter()
router.register(r'emprunts', EmpruntViewSet, basename='emprunt')

urlpatterns = [
    path('', include(router.urls)),
] + urlpatterns_scalar
