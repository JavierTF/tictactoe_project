"""
URL configuration for game app.
"""
from django.urls import path

from .views import SimpleGameView

app_name = 'game'

urlpatterns = [
    # Simple local game (NO LOGIN REQUIRED)
    path('', SimpleGameView.as_view(), name='simple-game'),
]