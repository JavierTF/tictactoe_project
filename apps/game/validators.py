"""
Custom validators for Game app.
"""
from django.core.exceptions import ValidationError


def validate_board_position(value):
    """
    Validate that board position is between 0 and 8.
    Board positions:
    0 | 1 | 2
    ---------
    3 | 4 | 5
    ---------
    6 | 7 | 8
    """
    if not isinstance(value, int):
        raise ValidationError('Position must be an integer.')
    
    if value < 0 or value > 8:
        raise ValidationError('Position must be between 0 and 8.')


def validate_board_state(value):
    """
    Validate board state is a list of 9 elements.
    Each element can be: None, 'X', or 'O'
    """
    if not isinstance(value, list):
        raise ValidationError('Board state must be a list.')
    
    if len(value) != 9:
        raise ValidationError('Board state must have exactly 9 positions.')
    
    valid_values = [None, 'X', 'O']
    for position in value:
        if position not in valid_values:
            raise ValidationError(
                f'Invalid board value: {position}. Must be None, "X", or "O".'
            )