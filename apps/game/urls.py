"""
URL configuration for game app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import GameViewSet, MoveViewSet

app_name = 'game'

# API Router
router = DefaultRouter()
router.register(r'games', GameViewSet, basename='game')
router.register(r'moves', MoveViewSet, basename='move')

urlpatterns = [
    path('api/v1/', include(router.urls)),
]