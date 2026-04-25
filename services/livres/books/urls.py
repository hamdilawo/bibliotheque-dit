from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LivreViewSet, CategorieViewSet

router = DefaultRouter()
router.register(r'livres', LivreViewSet, basename='livre')
router.register(r'categories', CategorieViewSet, basename='categorie')

urlpatterns = [
    path('', include(router.urls)),
]
