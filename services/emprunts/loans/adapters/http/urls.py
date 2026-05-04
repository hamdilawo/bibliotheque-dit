from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EmpruntViewSet

router = DefaultRouter()
router.register(r'emprunts', EmpruntViewSet, basename='emprunt')

urlpatterns = [
    path('', include(router.urls)),
]
