"""
Django Admin configuration for Game app.
"""
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe

from .models import Game, Move


class MoveInline(admin.TabularInline):
    """Inline admin for moves within a game."""
    
    model = Move
    extra = 0
    readonly_fields = ['player', 'position', 'symbol', 'created_at']
    can_delete = False
    
    def has_add_permission(self, request, obj=None):
        """Disable adding moves through admin."""
        return False


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    """Admin configuration for Game model."""
    
    list_display = [
        'id',
        'player1_link',
        'player2_link',
        'status_badge',
        'current_turn',
        'winner_link',
        'created_at',
        'finished_at'
    ]
    
    list_filter = ['status', 'created_at', 'finished_at']
    
    search_fields = [
        'player1__username',
        'player2__username',
        'winner__username',
        'id'
    ]
    
    readonly_fields = [
        'id',
        'board_display',
        'created_at',
        'updated_at',
        'finished_at'
    ]
    
    fieldsets = (
        ('Game Information', {
            'fields': ('id', 'status', 'board_display')
        }),
        ('Players', {
            'fields': ('player1', 'player2', 'winner')
        }),
        ('Game State', {
            'fields': ('current_turn', 'board')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'finished_at'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [MoveInline]
    
    def player1_link(self, obj):
        """Link to player1's user page."""
        url = reverse('admin:auth_user_change', args=[obj.player1.id])
        return format_html('<a href="{}">{}</a>', url, obj.player1.username)
    player1_link.short_description = 'Player 1 (X)'
    
    def player2_link(self, obj):
        """Link to player2's user page."""
        if obj.player2:
            url = reverse('admin:auth_user_change', args=[obj.player2.id])
            return format_html('<a href="{}">{}</a>', url, obj.player2.username)
        return format_html('<span style="color: #999;">Waiting...</span>')
    player2_link.short_description = 'Player 2 (O)'
    
    def winner_link(self, obj):
        """Link to winner's user page."""
        if obj.winner:
            url = reverse('admin:auth_user_change', args=[obj.winner.id])
            symbol = 'X' if obj.winner == obj.player1 else 'O'
            return format_html(
                '<a href="{}">{} ({})</a>',
                url,
                obj.winner.username,
                symbol
            )
        return '-'
    winner_link.short_description = 'Winner'
    
    def status_badge(self, obj):
        """Display status with color badge."""
        colors = {
            'waiting': '#FFA500',      # Orange
            'in_progress': '#007BFF',  # Blue
            'finished': '#28A745',     # Green
            'draw': '#6C757D',         # Gray
        }
        color = colors.get(obj.status, '#000')
        return format_html(
            '<span style="background-color: {}; color: white; '
            'padding: 3px 10px; border-radius: 3px; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def board_display(self, obj):
        """Display the game board visually."""
        if not obj.board:
            return "Empty board"
        
        # Create HTML table for board
        html = '<table style="border-collapse: collapse; margin: 10px 0;">'
        
        for row in range(3):
            html += '<tr>'
            for col in range(3):
                index = row * 3 + col
                cell = obj.board[index] or '&nbsp;'
                
                # Style based on cell content
                if cell == 'X':
                    style = 'background-color: #E3F2FD; color: #1976D2; font-weight: bold;'
                elif cell == 'O':
                    style = 'background-color: #FFF3E0; color: #F57C00; font-weight: bold;'
                else:
                    style = 'background-color: #F5F5F5; color: #999;'
                
                html += (
                    f'<td style="border: 2px solid #333; width: 60px; height: 60px; '
                    f'text-align: center; font-size: 24px; {style}">'
                    f'{cell}</td>'
                )
            html += '</tr>'
        
        html += '</table>'
        html += f'<p style="color: #666; font-size: 12px;">Current turn: <strong>{obj.current_turn}</strong></p>'
        
        return mark_safe(html)
    board_display.short_description = 'Board'
    
    def has_add_permission(self, request):
        """Disable adding games through admin."""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Only allow deleting finished games."""
        if obj and obj.status in ['finished', 'draw']:
            return True
        return False


@admin.register(Move)
class MoveAdmin(admin.ModelAdmin):
    """Admin configuration for Move model."""
    
    list_display = [
        'id',
        'game_link',
        'player_link',
        'symbol_badge',
        'position',
        'created_at'
    ]
    
    list_filter = ['symbol', 'created_at']
    
    search_fields = [
        'game__id',
        'player__username',
        'id'
    ]
    
    readonly_fields = [
        'id',
        'game',
        'player',
        'position',
        'symbol',
        'created_at'
    ]
    
    fieldsets = (
        ('Move Information', {
            'fields': ('id', 'game', 'player', 'position', 'symbol')
        }),
        ('Timestamp', {
            'fields': ('created_at',)
        }),
    )
    
    def game_link(self, obj):
        """Link to game's detail page."""
        url = reverse('admin:game_game_change', args=[obj.game.id])
        return format_html('<a href="{}">{}</a>', url, str(obj.game.id)[:8])
    game_link.short_description = 'Game'
    
    def player_link(self, obj):
        """Link to player's user page."""
        url = reverse('admin:auth_user_change', args=[obj.player.id])
        return format_html('<a href="{}">{}</a>', url, obj.player.username)
    player_link.short_description = 'Player'
    
    def symbol_badge(self, obj):
        """Display symbol with color badge."""
        color = '#1976D2' if obj.symbol == 'X' else '#F57C00'
        return format_html(
            '<span style="background-color: {}; color: white; '
            'padding: 3px 10px; border-radius: 3px; font-weight: bold;">{}</span>',
            color,
            obj.symbol
        )
    symbol_badge.short_description = 'Symbol'
    
    def has_add_permission(self, request):
        """Disable adding moves through admin."""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Disable deleting moves through admin."""
        return False


# Customize admin site header and title
admin.site.site_header = 'TicTacToe Administration'
admin.site.site_title = 'TicTacToe Admin'
admin.site.index_title = 'Game Management'