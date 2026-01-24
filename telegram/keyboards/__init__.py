"""Keyboards module initialization."""
from .inline import (
    get_language_keyboard,
    get_main_menu_keyboard,
    get_world_selection_keyboard,
    get_world_description_keyboard,
    get_save_slots_keyboard,
    get_load_slots_keyboard,
    get_settings_keyboard,
    get_back_to_menu_keyboard
)

__all__ = [
    'get_language_keyboard',
    'get_main_menu_keyboard',
    'get_world_selection_keyboard',
    'get_world_description_keyboard',
    'get_save_slots_keyboard',
    'get_load_slots_keyboard',
    'get_settings_keyboard',
    'get_back_to_menu_keyboard'
]

