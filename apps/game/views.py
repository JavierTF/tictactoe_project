"""
Views for TicTacToe game.
"""
from django.views.generic import TemplateView


class SimpleGameView(TemplateView):
    """Simple local TicTacToe game without authentication."""
    
    template_name = 'game/simple_game.html'