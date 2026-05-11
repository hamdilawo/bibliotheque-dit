from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework_simplejwt.views import TokenRefreshView
#from users.views import CustomTokenObtainPairView, LoginView  #  LoginView ajouté
from users.views import LoginView  #  LoginView ajouté
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin  # import admin

urlpatterns = [
    path('admin/',                  admin.site.urls),                                  
    path('api/',                    include('users.urls')),
    # Puisque LoginView fait tout mieux(Validation custom , Message erreur custom), /api/auth/token/ est redondant.
    #path('api/auth/token/',         CustomTokenObtainPairView.as_view(),               name='token_obtain_pair'),
    path('api/auth/token/refresh/', TokenRefreshView.as_view(),                        name='token_refresh'),
    path('api/auth/login/',         LoginView.as_view(),                               name='login'),
    path('api/schema/',             SpectacularAPIView.as_view(),                      name='schema'),
    path('',                        SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)