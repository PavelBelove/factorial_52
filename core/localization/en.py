"""
English localization stub for PlexMem RPG Bot.
TODO: Translation needed.
"""
from typing import Dict
from .base import BaseLocalization


class EnglishLocalization(BaseLocalization):
    """English language implementation - STUB, needs translation."""
    
    def get_language_code(self) -> str:
        return "en"
    
    def get_language_name(self) -> str:
        return "English"
    
    # TODO: Translate all methods below
    
    def get_language_selection_message(self) -> str:
        return "Choose your language:"
    
    def get_available_languages(self) -> Dict[str, str]:
        return {
            "ru": "🇷🇺 Русский",
            "en": "🇬🇧 English"
        }
    
    def get_main_menu_message(self) -> str:
        return "TODO: Translation needed"
    
    def get_main_menu_buttons(self) -> Dict[str, str]:
        return {
            "continue": "TODO",
            "new_game": "TODO",
            "load": "TODO",
            "save": "TODO",
            "settings": "TODO",
            "help": "TODO"
        }
    
    def get_world_selection_message(self) -> str:
        return "TODO: Translation needed"
    
    def get_world_start_button(self) -> str:
        return "TODO"
    
    def get_save_menu_message(self) -> str:
        return "TODO"
    
    def get_load_menu_message(self) -> str:
        return "TODO"
    
    def get_slot_label(self, slot: int) -> str:
        return f"TODO {slot}"
    
    def get_empty_slot_label(self) -> str:
        return "TODO"
    
    def get_no_saves_message(self) -> str:
        return "TODO"
    
    def get_game_started_message(self, slot: int) -> str:
        return "TODO"
    
    def get_game_saved_message(self, slot: int) -> str:
        return "TODO"
    
    def get_game_loaded_message(self, slot: int) -> str:
        return "TODO"
    
    def get_creating_world_message(self) -> str:
        return "TODO"
    
    def get_no_active_game_message(self) -> str:
        return "TODO"
    
    def get_error_message(self) -> str:
        return "TODO"
    
    def get_save_error_message(self) -> str:
        return "TODO"
    
    def get_load_error_message(self) -> str:
        return "TODO"
    
    def get_back_button(self) -> str:
        return "TODO"
    
    def get_cancel_button(self) -> str:
        return "TODO"
    
    def get_settings_menu_message(self) -> str:
        return "TODO"
    
    def get_settings_buttons(self) -> Dict[str, str]:
        return {
            "language": "TODO",
            "difficulty": "TODO",
            "content": "TODO"
        }
    
    def get_help_message(self) -> str:
        return "TODO: Translation needed"

