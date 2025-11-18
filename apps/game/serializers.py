"""
Serializers for Game API.
Convert models to/from JSON for REST API.
"""
from rest_framework import serializers
from django.contrib.auth.models import User

from .models import Game, Move


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model."""
    
    class Meta:
        model = User
        fields = ['id', 'username']
        read_only_fields = ['id', 'username']


class MoveSerializer(serializers.ModelSerializer):
    """Serializer for Move model."""
    
    player = UserSerializer(read_only=True)
    
    class Meta:
        model = Move
        fields = ['id', 'player', 'position', 'symbol', 'created_at']
        read_only_fields = ['id', 'player', 'symbol', 'created_at']


class GameListSerializer(serializers.ModelSerializer):
    """
    Serializer for Game list view.
    Lighter version without full details.
    """
    
    player1 = UserSerializer(read_only=True)
    player2 = UserSerializer(read_only=True)
    winner = UserSerializer(read_only=True)
    
    class Meta:
        model = Game
        fields = [
            'id',
            'player1',
            'player2',
            'status',
            'current_turn',
            'winner',
            'created_at',
            'updated_at',
            'finished_at'
        ]
        read_only_fields = fields


class GameDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for Game detail view.
    Includes full game state and moves.
    """
    
    player1 = UserSerializer(read_only=True)
    player2 = UserSerializer(read_only=True)
    winner = UserSerializer(read_only=True)
    moves = MoveSerializer(many=True, read_only=True)
    available_positions = serializers.SerializerMethodField()
    is_my_turn = serializers.SerializerMethodField()
    my_symbol = serializers.SerializerMethodField()
    
    class Meta:
        model = Game
        fields = [
            'id',
            'player1',
            'player2',
            'status',
            'board',
            'current_turn',
            'winner',
            'moves',
            'available_positions',
            'is_my_turn',
            'my_symbol',
            'created_at',
            'updated_at',
            'finished_at'
        ]
        read_only_fields = fields
    
    def get_available_positions(self, obj):
        """Get list of available positions."""
        return obj.get_available_positions()
    
    def get_is_my_turn(self, obj):
        """Check if it's current user's turn."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.is_player_turn(request.user)
        return False
    
    def get_my_symbol(self, obj):
        """Get current user's symbol (X or O)."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.get_player_symbol(request.user)
        return None


class GameCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a new game.
    """
    
    player2_username = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text='Username of second player (optional)'
    )
    
    class Meta:
        model = Game
        fields = ['player2_username']
    
    def validate_player2_username(self, value):
        """Validate player2 username if provided."""
        if value:
            try:
                User.objects.get(username=value)
            except User.DoesNotExist:
                raise serializers.ValidationError(
                    f'User "{value}" does not exist.'
                )
        return value
    
    def create(self, validated_data):
        """Create a new game."""
        request = self.context.get('request')
        player1 = request.user
        
        player2 = None
        player2_username = validated_data.get('player2_username')
        
        if player2_username:
            player2 = User.objects.get(username=player2_username)
            
            if player1 == player2:
                raise serializers.ValidationError(
                    'You cannot play against yourself.'
                )
        
        game = Game.objects.create(
            player1=player1,
            player2=player2,
            status=Game.Status.WAITING if not player2 else Game.Status.IN_PROGRESS,
            board=[None] * 9,
            current_turn='X'
        )
        
        return game


class JoinGameSerializer(serializers.Serializer):
    """
    Serializer for joining an existing game.
    """
    
    def validate(self, attrs):
        """Validate join game request."""
        game = self.context.get('game')
        request = self.context.get('request')
        user = request.user
        
        if game.status != Game.Status.WAITING:
            raise serializers.ValidationError(
                'This game is not available to join.'
            )
        
        if game.player1 == user:
            raise serializers.ValidationError(
                'You cannot play against yourself.'
            )
        
        if game.player2 is not None:
            raise serializers.ValidationError(
                'This game already has two players.'
            )
        
        return attrs
    
    def save(self):
        """Join the game."""
        game = self.context.get('game')
        request = self.context.get('request')
        
        game.player2 = request.user
        game.status = Game.Status.IN_PROGRESS
        game.save()
        
        return game


class MakeMoveSerializer(serializers.Serializer):
    """
    Serializer for making a move.
    """
    
    position = serializers.IntegerField(
        min_value=0,
        max_value=8,
        help_text='Position on the board (0-8)'
    )
    
    def validate(self, attrs):
        """Validate move."""
        game = self.context.get('game')
        request = self.context.get('request')
        user = request.user
        position = attrs['position']
        
        if game.status != Game.Status.IN_PROGRESS:
            raise serializers.ValidationError('Game is not in progress.')
        
        if user not in [game.player1, game.player2]:
            raise serializers.ValidationError(
                'You are not a player in this game.'
            )
        
        if not game.is_player_turn(user):
            raise serializers.ValidationError('It is not your turn.')
        
        if not game.is_position_available(position):
            raise serializers.ValidationError(
                f'Position {position} is not available.'
            )
        
        return attrs