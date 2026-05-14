from django.urls import path, include
from src.loans.adapters.scalar.scalar import urlpatterns_scalar

urlpatterns = [
    path('api/', include('loans.adapters.http.urls')),
] + urlpatterns_scalar
