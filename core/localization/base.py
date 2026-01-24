"""
Localization system for PlexMem RPG Bot.
Base abstract class for all language implementations.
"""
from abc import ABC, abstractmethod
from typing import Dict, List


class BaseLocalization(ABC):
    """Base localization class that defines interface for all language implementations."""
    
    @abstractmethod
    def get_language_code(self) -> str:
        """Return language code (e.g., 'ru', 'en')."""
        pass
    
    @abstractmethod
    def get_language_name(self) -> str:
        """Return language name in this language (e.g., 'Русский', 'English')."""
        pass
    
    # Language selection
    @abstractmethod
    def get_language_selection_message(self) -> str:
        """Message shown when selecting language."""
        pass
    
    @abstractmethod
    def get_available_languages(self) -> Dict[str, str]:
        """Return dict of available language codes to names with flags."""
        pass
    
    # Main menu
    @abstractmethod
    def get_main_menu_message(self) -> str:
        """Main menu message."""
        pass
    
    @abstractmethod
    def get_main_menu_buttons(self) -> Dict[str, str]:
        """Main menu button labels."""
        pass
    
    # World selection
    @abstractmethod
    def get_world_selection_message(self) -> str:
        """World selection message."""
        pass
    
    @abstractmethod
    def get_world_start_button(self) -> str:
        """'Start game' button text."""
        pass
    
    # Save/Load
    @abstractmethod
    def get_save_menu_message(self) -> str:
        """Save menu message."""
        pass
    
    @abstractmethod
    def get_load_menu_message(self) -> str:
        """Load menu message."""
        pass
    
    @abstractmethod
    def get_slot_label(self, slot: int) -> str:
        """Slot label (e.g., 'Slot 1')."""
        pass
    
    @abstractmethod
    def get_empty_slot_label(self) -> str:
        """Empty slot label."""
        pass
    
    @abstractmethod
    def get_no_saves_message(self) -> str:
        """Message when no saves available."""
        pass
    
    # Game messages
    @abstractmethod
    def get_game_started_message(self, slot: int) -> str:
        """Message when game starts."""
        pass
    
    @abstractmethod
    def get_game_saved_message(self, slot: int) -> str:
        """Message when game is saved."""
        pass
    
    @abstractmethod
    def get_game_loaded_message(self, slot: int) -> str:
        """Message when game is loaded."""
        pass
    
    @abstractmethod
    def get_creating_world_message(self) -> str:
        """'Creating your unique world...' message."""
        pass
    
    # Error messages
    @abstractmethod
    def get_no_active_game_message(self) -> str:
        """No active game error."""
        pass
    
    @abstractmethod
    def get_error_message(self) -> str:
        """Generic error message."""
        pass
    
    @abstractmethod
    def get_save_error_message(self) -> str:
        """Save error message."""
        pass
    
    @abstractmethod
    def get_load_error_message(self) -> str:
        """Load error message."""
        pass
    
    # Navigation
    @abstractmethod
    def get_back_button(self) -> str:
        """'Back' button text."""
        pass
    
    @abstractmethod
    def get_cancel_button(self) -> str:
        """'Cancel' button text."""
        pass
    
    # Settings
    @abstractmethod
    def get_settings_menu_message(self) -> str:
        """Settings menu message."""
        pass
    
    @abstractmethod
    def get_settings_buttons(self) -> Dict[str, str]:
        """Settings menu button labels."""
        pass
    
    # Help
    @abstractmethod
    def get_help_message(self) -> str:
        """Help/info message."""
        pass

