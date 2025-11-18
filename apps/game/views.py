"""
API Views for TicTacToe game.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db import models
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from .models import Game, Move
from .serializers import (
    GameListSerializer,
    GameDetailSerializer,
    GameCreateSerializer,
    JoinGameSerializer,
    MakeMoveSerializer,
    MoveSerializer
)
from .services import GameService
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin


class GameViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Game CRUD operations.
    
    Endpoints:
    - GET /api/v1/games/ - List all games
    - POST /api/v1/games/ - Create a new game
    - GET /api/v1/games/{id}/ - Get game details
    - POST /api/v1/games/{id}/join/ - Join a game
    - POST /api/v1/games/{id}/move/ - Make a move
    - GET /api/v1/games/my-games/ - Get current user's games
    - GET /api/v1/games/waiting/ - Get games waiting for players
    """
    
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Get queryset based on action."""
        user = self.request.user
        
        if self.action == 'waiting':
            return Game.objects.waiting_games()
        elif self.action == 'my_games':
            return Game.objects.filter(
                models.Q(player1=user) | models.Q(player2=user)
            ).order_by('-created_at')
        else:
            # All games (can be filtered by query params)
            return Game.objects.all().order_by('-created_at')
    
    def get_serializer_class(self):
        """Return appropriate serializer class."""
        if self.action == 'list':
            return GameListSerializer
        elif self.action == 'create':
            return GameCreateSerializer
        elif self.action == 'join':
            return JoinGameSerializer
        elif self.action == 'move':
            return MakeMoveSerializer
        else:
            return GameDetailSerializer
    
    @extend_schema(
        summary="List all games",
        description="Get a list of all games. Can be filtered by status.",
        parameters=[
            OpenApiParameter(
                name='status',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Filter by game status (waiting, in_progress, finished, draw)',
                required=False
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        """List games with optional status filter."""
        queryset = self.get_queryset()
        
        # Filter by status if provided
        status_filter = request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @extend_schema(
        summary="Create a new game",
        description="Create a new TicTacToe game. Optionally specify player2.",
        request=GameCreateSerializer,
        responses={201: GameDetailSerializer}
    )
    def create(self, request, *args, **kwargs):
        """Create a new game."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        game = serializer.save()
        
        # Return full game details
        detail_serializer = GameDetailSerializer(
            game,
            context={'request': request}
        )
        return Response(
            detail_serializer.data,
            status=status.HTTP_201_CREATED
        )
    
    @extend_schema(
        summary="Get game details",
        description="Get detailed information about a specific game.",
        responses={200: GameDetailSerializer}
    )
    def retrieve(self, request, *args, **kwargs):
        """Get game details."""
        return super().retrieve(request, *args, **kwargs)
    
    @extend_schema(
        summary="Join a game",
        description="Join an existing game as player2.",
        request=JoinGameSerializer,
        responses={200: GameDetailSerializer}
    )
    @action(detail=True, methods=['post'])
    def join(self, request, pk=None):
        """Join an existing game."""
        game = self.get_object()
        
        serializer = self.get_serializer(
            data={},
            context={'game': game, 'request': request}
        )
        serializer.is_valid(raise_exception=True)
        game = serializer.save()
        
        # Return updated game details
        detail_serializer = GameDetailSerializer(
            game,
            context={'request': request}
        )
        return Response(detail_serializer.data)
    
    @extend_schema(
        summary="Make a move",
        description="Make a move in the game by specifying a position (0-8).",
        request=MakeMoveSerializer,
        responses={200: GameDetailSerializer}
    )
    @action(detail=True, methods=['post'])
    def move(self, request, pk=None):
        """Make a move in the game."""
        game = self.get_object()
        
        serializer = self.get_serializer(
            data=request.data,
            context={'game': game, 'request': request}
        )
        serializer.is_valid(raise_exception=True)
        
        # Use GameService to make the move
        position = serializer.validated_data['position']
        move, game_state = GameService.make_move(
            game=game,
            player=request.user,
            position=position
        )
        
        # Return updated game details
        game.refresh_from_db()
        detail_serializer = GameDetailSerializer(
            game,
            context={'request': request}
        )
        return Response(detail_serializer.data)
    
    @extend_schema(
        summary="Get my games",
        description="Get all games for the authenticated user.",
        responses={200: GameListSerializer(many=True)}
    )
    @action(detail=False, methods=['get'])
    def my_games(self, request):
        """Get all games for current user."""
        queryset = self.get_queryset()
        serializer = GameListSerializer(queryset, many=True)
        return Response(serializer.data)
    
    @extend_schema(
        summary="Get waiting games",
        description="Get all games waiting for a second player.",
        responses={200: GameListSerializer(many=True)}
    )
    @action(detail=False, methods=['get'])
    def waiting(self, request):
        """Get games waiting for players."""
        queryset = self.get_queryset()
        serializer = GameListSerializer(queryset, many=True)
        return Response(serializer.data)


class MoveViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for Move read operations.
    
    Endpoints:
    - GET /api/v1/moves/ - List all moves
    - GET /api/v1/moves/{id}/ - Get move details
    """
    
    queryset = Move.objects.all().select_related('game', 'player')
    serializer_class = MoveSerializer
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        summary="List all moves",
        description="Get a list of all moves.",
        parameters=[
            OpenApiParameter(
                name='game',
                type=OpenApiTypes.UUID,
                location=OpenApiParameter.QUERY,
                description='Filter moves by game ID',
                required=False
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        """List moves with optional game filter."""
        queryset = self.get_queryset()
        
        # Filter by game if provided
        game_id = request.query_params.get('game')
        if game_id:
            queryset = queryset.filter(game_id=game_id)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
class GameListView(TemplateView):
    """View for game list page."""
    
    template_name = 'game/game_list.html'
    
    def get(self, request, *args, **kwargs):
        print("=" * 50)
        print("GameListView.get() called")
        print(f"Template: {self.template_name}")
        print(f"User: {request.user}")
        print("=" * 50)
        return super().get(request, *args, **kwargs)


class GameDetailView(LoginRequiredMixin, TemplateView):
    """View for game detail/board page."""
    
    template_name = 'game/game_detail.html'
    login_url = '/admin/login/'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['game_id'] = kwargs.get('game_id')
        return context

class SimpleGameView(TemplateView):
    """Simple local TicTacToe game without authentication."""
    
    template_name = 'game/simple_game.html'