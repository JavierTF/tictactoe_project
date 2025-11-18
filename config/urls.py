"""
URL configuration for TicTacToe project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # Game (simple version only)
    path('', include('apps.game.urls')),
]

# Debug Toolbar (solo en desarrollo)
if settings.DEBUG:
    urlpatterns += [
        path('__debug__/', include('debug_toolbar.urls')),
    ]