"""
Localization system for PlexMem RPG Bot.
"""
from .base import BaseLocalization
from .ru import RussianLocalization
from .en import EnglishLocalization


__all__ = [
    'BaseLocalization',
    'RussianLocalization',
    'EnglishLocalization',
    'get_localization'
]


# Available localizations
_LOCALIZATIONS = {
    'ru': RussianLocalization(),
    'en': EnglishLocalization(),
}


def get_localization(language_code: str = 'ru') -> BaseLocalization:
    """
    Get localization instance for given language code.
    Falls back to Russian if language not found.
    
    Args:
        language_code: Language code ('ru', 'en', etc.)
        
    Returns:
        Localization instance
    """
    return _LOCALIZATIONS.get(language_code, _LOCALIZATIONS['ru'])


def get_available_languages() -> dict[str, str]:
    """
    Get dict of available language codes to names.
    
    Returns:
        Dict like {'ru': '🇷🇺 Русский', 'en': '🇬🇧 English'}
    """
    # Use Russian localization to get the list (it has all language names)
    return _LOCALIZATIONS['ru'].get_available_languages()

