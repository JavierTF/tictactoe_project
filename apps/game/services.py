"""
Business logic for TicTacToe game.
Separation of concerns: services handle game logic, views handle HTTP.
"""
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db import models
from typing import Optional, List, Tuple

from .models import Game, Move



class GameService:
    """Service class for Game-related operations."""
    
    # Winning combinations (board positions)
    WINNING_COMBINATIONS = [
        [0, 1, 2],  # Top row
        [3, 4, 5],  # Middle row
        [6, 7, 8],  # Bottom row
        [0, 3, 6],  # Left column
        [1, 4, 7],  # Middle column
        [2, 5, 8],  # Right column
        [0, 4, 8],  # Diagonal \
        [2, 4, 6],  # Diagonal /
    ]
    
    @staticmethod
    def create_game(player1: User, player2: Optional[User] = None) -> Game:
        """
        Create a new game.
        
        Args:
            player1: First player (plays as X)
            player2: Second player (plays as O), optional
        
        Returns:
            Created Game instance
        """
        game = Game.objects.create(
            player1=player1,
            player2=player2,
            status=Game.Status.WAITING if not player2 else Game.Status.IN_PROGRESS,
            board=[None] * 9,
            current_turn='X'
        )
        return game
    
    @staticmethod
    def join_game(game: Game, player2: User) -> Game:
        """
        Join an existing game as player2.
        
        Args:
            game: Game to join
            player2: User joining the game
        
        Returns:
            Updated Game instance
        
        Raises:
            ValidationError: If game is not available to join
        """
        if game.status != Game.Status.WAITING:
            raise ValidationError('This game is not available to join.')
        
        if game.player1 == player2:
            raise ValidationError('You cannot play against yourself.')
        
        if game.player2 is not None:
            raise ValidationError('This game already has two players.')
        
        game.player2 = player2
        game.status = Game.Status.IN_PROGRESS
        game.save()
        
        return game
    
    @staticmethod
    def make_move(game: Game, player: User, position: int) -> Tuple[Move, dict]:
        """
        Make a move in the game.
        
        Args:
            game: Game instance
            player: User making the move
            position: Board position (0-8)
        
        Returns:
            Tuple of (Move instance, game_state dict)
        
        Raises:
            ValidationError: If move is invalid
        """
        # Validations
        if game.status != Game.Status.IN_PROGRESS:
            raise ValidationError('Game is not in progress.')
        
        if player not in [game.player1, game.player2]:
            raise ValidationError('You are not a player in this game.')
        
        if not game.is_player_turn(player):
            raise ValidationError('It is not your turn.')
        
        if not game.is_position_available(position):
            raise ValidationError(f'Position {position} is not available.')
        
        # Get player symbol
        symbol = game.get_player_symbol(player)
        
        # Update board
        game.board[position] = symbol
        
        # Create move record
        move = Move.objects.create(
            game=game,
            player=player,
            position=position,
            symbol=symbol
        )
        
        # Check for winner
        winner = GameService._check_winner(game.board)
        
        if winner:
            game.status = Game.Status.FINISHED
            game.winner = game.player1 if winner == 'X' else game.player2
            game.finished_at = timezone.now()
        elif GameService._is_board_full(game.board):
            game.status = Game.Status.DRAW
            game.finished_at = timezone.now()
        else:
            # Switch turn
            game.current_turn = 'O' if game.current_turn == 'X' else 'X'
        
        game.save()
        
        # Prepare game state for response
        game_state = {
            'game_id': str(game.id),
            'board': game.board,
            'status': game.status,
            'current_turn': game.current_turn,
            'winner': game.winner.username if game.winner else None,
            'last_move': {
                'player': player.username,
                'position': position,
                'symbol': symbol
            }
        }
        
        return move, game_state
    
    @staticmethod
    def _check_winner(board: List) -> Optional[str]:
        """
        Check if there's a winner on the board.
        
        Args:
            board: List of 9 positions
        
        Returns:
            'X' if X wins, 'O' if O wins, None if no winner
        """
        for combo in GameService.WINNING_COMBINATIONS:
            if (board[combo[0]] is not None and
                board[combo[0]] == board[combo[1]] == board[combo[2]]):
                return board[combo[0]]
        return None
    
    @staticmethod
    def _is_board_full(board: List) -> bool:
        """
        Check if the board is full (all positions occupied).
        
        Args:
            board: List of 9 positions
        
        Returns:
            True if board is full, False otherwise
        """
        return None not in board
    
    @staticmethod
    def get_game_state(game: Game) -> dict:
        """
        Get current game state as a dictionary.
        
        Args:
            game: Game instance
        
        Returns:
            Dictionary with game state
        """
        return {
            'game_id': str(game.id),
            'status': game.status,
            'board': game.board,
            'current_turn': game.current_turn,
            'player1': {
                'username': game.player1.username,
                'symbol': 'X'
            },
            'player2': {
                'username': game.player2.username if game.player2 else None,
                'symbol': 'O'
            } if game.player2 else None,
            'winner': game.winner.username if game.winner else None,
            'available_positions': game.get_available_positions(),
            'created_at': game.created_at.isoformat(),
            'finished_at': game.finished_at.isoformat() if game.finished_at else None,
        }
    
    @staticmethod
    def get_player_games(player: User, status: Optional[str] = None) -> List[Game]:
        """
        Get all games for a player, optionally filtered by status.
        
        Args:
            player: User instance
            status: Optional game status to filter by
        
        Returns:
            List of Game instances
        """
        games = Game.objects.filter(
            models.Q(player1=player) | models.Q(player2=player)
        )
        
        if status:
            games = games.filter(status=status)
        
        return games.order_by('-created_at')