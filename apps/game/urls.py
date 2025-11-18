"""
URL configuration for game app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import GameViewSet, MoveViewSet, GameListView, GameDetailView, SimpleGameView  

app_name = 'game'

# API Router
router = DefaultRouter()
router.register(r'games', GameViewSet, basename='game')
router.register(r'moves', MoveViewSet, basename='move')

urlpatterns = [
    # Simple local game (NO LOGIN REQUIRED)
    path('play/', SimpleGameView.as_view(), name='simple-game'),

    # HTML Pages
    path('', GameListView.as_view(), name='game-list'),
    path('game/<uuid:game_id>/', GameDetailView.as_view(), name='game-detail'),
    
    # API
    path('api/v1/', include(router.urls)),
]