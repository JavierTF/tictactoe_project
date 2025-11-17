"""
Database models for TicTacToe game.
"""
import uuid
from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from .managers import GameManager, MoveManager
from .validators import validate_board_position, validate_board_state


class Game(models.Model):
    """
    Represents a TicTacToe game.
    """
    
    class Status(models.TextChoices):
        WAITING = 'waiting', 'Waiting for players'
        IN_PROGRESS = 'in_progress', 'In Progress'
        FINISHED = 'finished', 'Finished'
        DRAW = 'draw', 'Draw'
    
    # Use UUID for public identification
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Players
    player1 = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='games_as_player1',
        help_text='Player X (starts first)'
    )
    player2 = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='games_as_player2',
        null=True,
        blank=True,
        help_text='Player O'
    )
    
    # Game state
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.WAITING,
        db_index=True
    )
    
    # Board state: list of 9 elements [None, 'X', 'O', ...]
    board = models.JSONField(
        default=list,
        validators=[validate_board_state],
        help_text='Board state as a list of 9 positions'
    )
    
    # Current turn (who should play next)
    current_turn = models.CharField(
        max_length=1,
        choices=[('X', 'Player X'), ('O', 'Player O')],
        default='X'
    )
    
    # Winner
    winner = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='games_won',
        null=True,
        blank=True
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    
    # Custom manager
    objects = GameManager()
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['status']),
        ]
        verbose_name = 'Game'
        verbose_name_plural = 'Games'
    
    def __str__(self):
        if self.player2:
            return f"Game {self.id}: {self.player1.username} vs {self.player2.username}"
        return f"Game {self.id}: {self.player1.username} (waiting for opponent)"
    
    def save(self, *args, **kwargs):
        """Initialize board if empty."""
        if not self.board:
            self.board = [None] * 9
        super().save(*args, **kwargs)
    
    def get_player_symbol(self, user):
        """Return 'X' or 'O' for the given player."""
        if user == self.player1:
            return 'X'
        elif user == self.player2:
            return 'O'
        return None
    
    def is_player_turn(self, user):
        """Check if it's the given player's turn."""
        return self.get_player_symbol(user) == self.current_turn
    
    def get_available_positions(self):
        """Return list of available (empty) positions."""
        return [i for i, cell in enumerate(self.board) if cell is None]
    
    def is_position_available(self, position):
        """Check if a position is available."""
        return 0 <= position <= 8 and self.board[position] is None


class Move(models.Model):
    """
    Represents a single move in a game.
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    game = models.ForeignKey(
        Game,
        on_delete=models.CASCADE,
        related_name='moves'
    )
    
    player = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='moves'
    )
    
    position = models.IntegerField(
        validators=[validate_board_position],
        help_text='Position on the board (0-8)'
    )
    
    symbol = models.CharField(
        max_length=1,
        choices=[('X', 'X'), ('O', 'O')]
    )
    
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    
    # Custom manager
    objects = MoveManager()
    
    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['game', 'created_at']),
        ]
        verbose_name = 'Move'
        verbose_name_plural = 'Moves'
    
    def __str__(self):
        return f"{self.player.username} ({self.symbol}) -> Position {self.position}"
    
    def clean(self):
        """Validate move before saving."""
        if not self.game.is_position_available(self.position):
            raise ValidationError(f'Position {self.position} is not available.')
        
        if not self.game.is_player_turn(self.player):
            raise ValidationError('It is not your turn.')