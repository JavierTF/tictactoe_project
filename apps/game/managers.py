"""
Custom model managers for Game app.
"""
from django.db import models


class GameManager(models.Manager):
    """Custom manager for Game model."""

    def active_games(self):
        """Return games that are not finished."""
        return self.filter(status='in_progress')

    def finished_games(self):
        """Return finished games."""
        return self.filter(status__in=['finished', 'draw'])

    def waiting_games(self):
        """Return games waiting for a second player."""
        return self.filter(status='waiting', player2__isnull=True)


class MoveManager(models.Manager):
    """Custom manager for Move model."""

    def for_game(self, game):
        """Return all moves for a specific game."""
        return self.filter(game=game).order_by('created_at')

    def by_player(self, player):
        """Return all moves made by a specific player."""
        return self.filter(player=player).order_by('-created_at')