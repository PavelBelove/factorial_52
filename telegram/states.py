"""
FSM States for Telegram bot navigation.
Defines all possible states for conversation flow.
"""
from aiogram.fsm.state import State, StatesGroup


class GameStates(StatesGroup):
    """FSM states for game navigation and menu."""
    
    # Initial state for new users
    LANGUAGE_SELECTION = State()  # Choose language (only for new users)
    
    # Main menu
    MAIN_MENU = State()  # Main menu with options
    
    # World selection flow
    WORLD_SELECTION = State()  # Choose world for new game
    WORLD_DESCRIPTION = State()  # View world description before starting
    
    # In-game state
    IN_GAME = State()  # Active game session
    
    # Save/Load flow
    SAVE_MENU = State()  # Save game menu (choose slot)
    LOAD_MENU = State()  # Load game menu (choose saved game)
    
    # Settings
    SETTINGS_MENU = State()  # Settings menu
    LANGUAGE_SETTINGS = State()  # Language selection in settings
    
    # Help
    HELP = State()  # Help/info screen

