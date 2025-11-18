"""
URL configuration for TicTacToe project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.views.generic import RedirectView

from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView
)

urlpatterns = [
    # Redirect root to simple game
    path('', RedirectView.as_view(url='/play/', permanent=False), name='home'),

    # Admin
    path('admin/', admin.site.urls),
    
    # Game app (includes both HTML pages and API)
    path('', include('apps.game.urls')),
    
    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

# Debug Toolbar (solo en desarrollo)
if settings.DEBUG:
    urlpatterns += [
        path('__debug__/', include('debug_toolbar.urls')),
    ]