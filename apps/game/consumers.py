"""
WebSocket consumers for real-time game updates.
"""
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from .models import Game, Move
from .services import GameService


class GameConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for game updates.
    
    Handles real-time communication between players.
    """
    
    async def connect(self):
        """Handle WebSocket connection."""
        self.game_id = self.scope['url_route']['kwargs']['game_id']
        self.game_group_name = f'game_{self.game_id}'
        self.user = self.scope['user']
        
        # Verify user is authenticated
        if not self.user.is_authenticated:
            await self.close(code=4001)
            return
        
        # Verify game exists and user is a player
        try:
            game = await self.get_game()
            if not await self.is_player(game):
                await self.close(code=4003)
                return
        except Game.DoesNotExist:
            await self.close(code=4004)
            return
        
        # Join game group
        await self.channel_layer.group_add(
            self.game_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Send current game state
        game_state = await self.get_game_state(game)
        await self.send(text_data=json.dumps({
            'type': 'game_state',
            'data': game_state
        }))
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnection."""
        # Leave game group
        await self.channel_layer.group_discard(
            self.game_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        """
        Receive message from WebSocket.
        
        Expected message types:
        - move: Make a move
        - get_state: Get current game state
        """
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            if message_type == 'move':
                await self.handle_move(data)
            elif message_type == 'get_state':
                await self.handle_get_state()
            else:
                await self.send_error('Unknown message type')
        
        except json.JSONDecodeError:
            await self.send_error('Invalid JSON')
        except Exception as e:
            await self.send_error(str(e))
    
    async def handle_move(self, data):
        """Handle move request."""
        position = data.get('position')
        
        if position is None:
            await self.send_error('Position is required')
            return
        
        try:
            # Make the move
            game = await self.get_game()
            move, game_state = await self.make_move(game, position)
            
            # Broadcast to all players in the game
            await self.channel_layer.group_send(
                self.game_group_name,
                {
                    'type': 'game_update',
                    'data': game_state
                }
            )
        
        except ValidationError as e:
            await self.send_error(str(e))
        except Exception as e:
            await self.send_error(f'Error making move: {str(e)}')
    
    async def handle_get_state(self):
        """Handle get state request."""
        try:
            game = await self.get_game()
            game_state = await self.get_game_state(game)
            
            await self.send(text_data=json.dumps({
                'type': 'game_state',
                'data': game_state
            }))
        
        except Exception as e:
            await self.send_error(f'Error getting state: {str(e)}')
    
    async def game_update(self, event):
        """
        Receive game update from channel layer.
        Send to WebSocket.
        """
        await self.send(text_data=json.dumps({
            'type': 'game_update',
            'data': event['data']
        }))
    
    async def send_error(self, message):
        """Send error message to client."""
        await self.send(text_data=json.dumps({
            'type': 'error',
            'message': message
        }))
    
    # Database operations (sync to async)
    
    @database_sync_to_async
    def get_game(self):
        """Get game from database."""
        return Game.objects.select_related(
            'player1', 'player2', 'winner'
        ).get(id=self.game_id)
    
    @database_sync_to_async
    def is_player(self, game):
        """Check if user is a player in the game."""
        return self.user in [game.player1, game.player2]
    
    @database_sync_to_async
    def make_move(self, game, position):
        """Make a move in the game."""
        return GameService.make_move(
            game=game,
            player=self.user,
            position=position
        )
    
    @database_sync_to_async
    def get_game_state(self, game):
        """Get current game state."""
        return GameService.get_game_state(game)