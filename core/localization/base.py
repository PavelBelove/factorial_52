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
    
    @abstractmethod
    def get_difficulty_settings_message(self) -> str:
        """Difficulty settings message."""
        pass
    
    @abstractmethod
    def get_content_filter_settings_message(self) -> str:
        """Content filter settings message."""
        pass
    
    @abstractmethod
    def get_genre_prism_settings_message(self) -> str:
        """Genre prism settings message."""
        pass
    
    @abstractmethod
    def get_genre_prism_description(self, prism_id: str) -> str:
        """Get genre prism detailed description for selection screen."""
        pass
    
    # Keyboard labels
    @abstractmethod
    def get_difficulty_label(self, difficulty: str) -> str:
        """Get difficulty label (easy/normal/hard)."""
        pass
    
    @abstractmethod
    def get_content_filter_label(self, filter_type: str) -> str:
        """Get content filter label (safe/romantic/adult)."""
        pass
    
    @abstractmethod
    def get_confirm_button(self) -> str:
        """'Confirm' button text."""
        pass
    
    @abstractmethod
    def get_back_page_button(self) -> str:
        """'Back' navigation button text."""
        pass
    
    @abstractmethod
    def get_forward_page_button(self) -> str:
        """'Forward' navigation button text."""
        pass
    
    @abstractmethod
    def get_adult_content_consent_message(self) -> str:
        """Adult content consent confirmation message."""
        pass
    
    # Help
    @abstractmethod
    def get_help_message(self) -> str:
        """Help/info message."""
        pass
    
    @abstractmethod
    def get_help_page(self, page: int) -> str:
        """Get help page by number (1-4)."""
        pass
    
    @abstractmethod
    def get_help_about_book(self) -> str:
        """Help page 1: About 52! World."""
        pass
    
    @abstractmethod
    def get_help_bot_control(self) -> str:
        """Help page 2: Bot control."""
        pass
    
    @abstractmethod
    def get_help_genre_prisms(self) -> str:
        """Help page 3: Genre prisms."""
        pass
    
    @abstractmethod
    def get_help_character_creation(self) -> str:
        """Help page 4: Character creation."""
        pass
    
    @abstractmethod
    def get_help_mechanics(self) -> str:
        """Help page 5: Game mechanics."""
        pass
    
    # Additional game messages
    @abstractmethod
    def get_initial_game_message(self, world_id: str) -> str:
        """Message shown when starting a new game."""
        pass
    
    @abstractmethod
    def get_story_started_header(self) -> str:
        """'Story started' header for new game."""
        pass
    
    @abstractmethod
    def get_story_continues_header(self) -> str:
        """'Story continues' header for continuing game."""
        pass
    
    @abstractmethod
    def get_chapter_label(self, chapter_num: int) -> str:
        """'Chapter #' label for turn number."""
        pass
    
    @abstractmethod
    def get_last_chapter_label(self, chapter_num: int) -> str:
        """'Last chapter #' label."""
        pass
    
    @abstractmethod
    def get_undo_success(self, current_chapter: int) -> str:
        """Message when undo is successful."""
        pass
    
    @abstractmethod
    def get_undo_nothing_to_undo(self) -> str:
        """Message when there's nothing to undo."""
        pass
    
    @abstractmethod
    def get_error_message(self) -> str:
        """Generic error message."""
        pass
    
    @abstractmethod
    def get_creating_world_message(self) -> str:
        """'Creating world' message."""
        pass
    
    @abstractmethod
    def get_empty_inventory_message(self) -> str:
        """'Inventory is empty' message."""
        pass
    
    @abstractmethod
    def get_continue_game_message(self) -> str:
        """Message shown when continuing a game."""
        pass
    
    @abstractmethod
    def get_game_rules(self) -> str:
        """Game rules message."""
        pass
    
    # Loading indicators
    @abstractmethod
    def get_thinking_message(self) -> str:
        """'Thinking...' message for LLM response loading."""
        pass
    
    @abstractmethod
    def get_creating_story_message(self) -> str:
        """'Creating story...' message for world creation."""
        pass
    
    @abstractmethod
    def get_retrying_message(self) -> str:
        """'Model overloaded, retrying...' message."""
        pass


