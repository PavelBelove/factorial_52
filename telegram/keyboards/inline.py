"""
Inline keyboards for Telegram bot.
All keyboard builders for menu navigation.
"""
from typing import List, Dict
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_language_keyboard() -> InlineKeyboardMarkup:
    """Language selection keyboard."""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang:ru")],
        [InlineKeyboardButton(text="🇬🇧 English", callback_data="lang:en")]
    ])
    return keyboard


def get_main_menu_keyboard(has_active_game: bool = False, loc=None) -> InlineKeyboardMarkup:
    """
    Main menu keyboard.
    
    Args:
        has_active_game: If True, shows "Continue" button
        loc: Localization object
    """
    if loc is None:
        from core.config import get_localization
        loc = get_localization("ru")
    
    button_labels = loc.get_main_menu_buttons()
    buttons = []
    
    if has_active_game:
        buttons.append([InlineKeyboardButton(text=button_labels["continue"], callback_data="continue")])
    
    buttons.extend([
        [InlineKeyboardButton(text=button_labels["new_game"], callback_data="new_game")],
        [InlineKeyboardButton(text=button_labels["load"], callback_data="load")],
        [InlineKeyboardButton(text=button_labels["save"], callback_data="save")],
        [InlineKeyboardButton(text=button_labels["settings"], callback_data="settings")],
        [InlineKeyboardButton(text=button_labels["help"], callback_data="help")]
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_world_selection_keyboard(worlds: List[Dict], loc=None) -> InlineKeyboardMarkup:
    """
    World selection keyboard.
    
    Args:
        worlds: List of world dicts with keys: id, name, icon, description
        loc: Localization object
    """
    if loc is None:
        from core.config import get_localization
        loc = get_localization("ru")
    
    buttons = []
    
    for world in worlds:
        icon = world.get('icon', '🌍')
        name = world.get('name', world['id'])
        callback = f"world:{world['id']}"
        
        buttons.append([InlineKeyboardButton(text=f"{icon} {name}", callback_data=callback)])
    
    # Back button
    buttons.append([InlineKeyboardButton(text=loc.get_back_button(), callback_data="back_to_menu")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_world_description_keyboard(world_id: str, loc=None) -> InlineKeyboardMarkup:
    """
    Keyboard for world description screen.
    Shows "Start game" and "Back" buttons.
    
    Args:
        world_id: ID of the world
        loc: Localization object
    """
    if loc is None:
        from core.config import get_localization
        loc = get_localization("ru")
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=loc.get_world_start_button(), callback_data=f"start:{world_id}")],
        [InlineKeyboardButton(text=loc.get_back_button(), callback_data="back_to_worlds")]
    ])
    return keyboard


def get_save_slots_keyboard(saved_sessions: List[Dict], loc=None) -> InlineKeyboardMarkup:
    """
    Save slots keyboard.
    
    Args:
        saved_sessions: List of saved session dicts with keys: slot_number, world_id, saved_at
        loc: Localization object (optional, defaults to Russian)
    """
    if loc is None:
        from core.config import get_localization
        loc = get_localization("ru")
    
    buttons = []
    
    # Create dict of occupied slots
    occupied = {s['slot_number']: s for s in saved_sessions}
    
    # Show all 5 slots
    for slot in range(1, 6):
        if slot in occupied:
            session = occupied[slot]
            world = session.get('world_id', '?')
            # Show occupied slot
            text = f"💾 {loc.get_slot_label(slot)}: {world}"
        else:
            # Show empty slot
            text = f"📭 {loc.get_slot_label(slot)}: {loc.get_empty_slot_label()}"
        
        buttons.append([InlineKeyboardButton(text=text, callback_data=f"save_slot:{slot}")])
    
    # Back button
    buttons.append([InlineKeyboardButton(text=loc.get_back_button(), callback_data="back_to_menu")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_load_slots_keyboard(saved_sessions: List[Dict], loc=None) -> InlineKeyboardMarkup:
    """
    Load slots keyboard (only shows occupied slots).
    
    Args:
        saved_sessions: List of saved session dicts
        loc: Localization object (optional, defaults to Russian)
    """
    if loc is None:
        from core.config import get_localization
        loc = get_localization("ru")
    
    buttons = []
    
    if not saved_sessions:
        # No saves - just back button
        buttons.append([InlineKeyboardButton(text=loc.get_back_button(), callback_data="back_to_menu")])
        return InlineKeyboardMarkup(inline_keyboard=buttons)
    
    for session in saved_sessions:
        slot = session.get('slot_number', '?')
        world = session.get('world_id', '?')
        saved_at = session.get('saved_at', '')
        
        # Format date if available
        if saved_at:
            try:
                from datetime import datetime
                dt = datetime.fromisoformat(saved_at.replace('Z', '+00:00'))
                date_str = dt.strftime('%d.%m %H:%M')
            except:
                date_str = ''
        else:
            date_str = ''
        
        text = f"📂 {loc.get_slot_label(slot)}: {world}"
        if date_str:
            text += f" ({date_str})"
        
        buttons.append([InlineKeyboardButton(text=text, callback_data=f"load_slot:{session['id']}")])
    
    # Back button
    buttons.append([InlineKeyboardButton(text=loc.get_back_button(), callback_data="back_to_menu")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_settings_keyboard(current_settings: dict = None, loc=None) -> InlineKeyboardMarkup:
    """Settings menu keyboard with current values."""
    if loc is None:
        from core.config import get_localization
        loc = get_localization("ru")
    
    if not current_settings:
        current_settings = {"language": "ru", "difficulty": "normal", "content_filter": "safe", "genre_prism": "balanced"}

    # Format current values
    lang_map = {"ru": "🇷🇺 RU", "en": "🇬🇧 EN"}
    
    lang_val = lang_map.get(current_settings.get("language", "ru"), "🇷🇺 RU")
    diff_val = loc.get_difficulty_label(current_settings.get("difficulty", "normal"))
    filter_val = loc.get_content_filter_label(current_settings.get("content_filter", "safe"))
    
    # Get prism emoji and name
    from core.genre_prisms import get_prism_info
    language = current_settings.get("language", "ru")
    prism_info = get_prism_info(current_settings.get("genre_prism", "balanced"), language)
    prism_val = f"{prism_info['emoji']} {prism_info['name']}"
    
    buttons = loc.get_settings_buttons()

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"{buttons['language']}: {lang_val}", callback_data="settings:language")],
        [InlineKeyboardButton(text=f"{buttons['difficulty']}: {diff_val}", callback_data="settings:difficulty")],
        [InlineKeyboardButton(text=f"{buttons['content']}: {filter_val}", callback_data="settings:content")],
        [InlineKeyboardButton(text=f"🎭 {'Жанровые призмы' if loc.language == 'ru' else 'Genre Prisms'}: {prism_val}", callback_data="settings:prism")],
        [InlineKeyboardButton(text=loc.get_back_button(), callback_data="back_to_menu")]
    ])
    return keyboard


def get_difficulty_keyboard(current: str = "normal", loc=None) -> InlineKeyboardMarkup:
    """Difficulty selection keyboard."""
    if loc is None:
        from core.config import get_localization
        loc = get_localization("ru")
    
    buttons = []

    options = ["easy", "normal", "hard"]

    for value in options:
        marker = "✅ " if value == current else ""
        label = loc.get_difficulty_label(value)
        buttons.append([InlineKeyboardButton(
            text=f"{marker}{label}",
            callback_data=f"set_difficulty:{value}"
        )])

    buttons.append([InlineKeyboardButton(text=loc.get_back_button(), callback_data="settings")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_content_filter_keyboard(current: str = "safe", loc=None) -> InlineKeyboardMarkup:
    """Content filter selection keyboard."""
    if loc is None:
        from core.config import get_localization
        loc = get_localization("ru")
    
    buttons = []

    options = ["safe", "romantic", "adult"]

    for value in options:
        marker = "✅ " if value == current else ""
        label = loc.get_content_filter_label(value)
        buttons.append([InlineKeyboardButton(
            text=f"{marker}{label}",
            callback_data=f"set_content:{value}"
        )])

    buttons.append([InlineKeyboardButton(text=loc.get_back_button(), callback_data="settings")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_adult_consent_keyboard(loc=None) -> InlineKeyboardMarkup:
    """Adult content consent confirmation keyboard."""
    if loc is None:
        from core.config import get_localization
        loc = get_localization("ru")
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=loc.get_confirm_button(), callback_data="confirm_adult:yes")],
        [InlineKeyboardButton(text=loc.get_cancel_button(), callback_data="confirm_adult:no")]
    ])
    return keyboard


def get_genre_prism_keyboard(current: str = "balanced", loc=None) -> InlineKeyboardMarkup:
    """Genre prism selection keyboard - 2 columns."""
    if loc is None:
        from core.config import get_localization
        loc = get_localization("ru")
    
    from core.genre_prisms import get_all_prisms
    prisms = get_all_prisms(loc.language)
    
    buttons = []
    row = []
    
    for prism in prisms:
        marker = "✅ " if prism["id"] == current else ""
        button_text = f"{marker}{prism['emoji']} {prism['name']}"
        
        row.append(InlineKeyboardButton(
            text=button_text,
            callback_data=f"prism:{prism['id']}"
        ))
        
        # 2 columns
        if len(row) == 2:
            buttons.append(row)
            row = []
    
    # Add remaining button if odd number
    if row:
        buttons.append(row)
    
    # Back button
    buttons.append([InlineKeyboardButton(
        text=loc.get_back_button(),
        callback_data="settings"
    )])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_prism_description_keyboard(prism_id: str, loc=None) -> InlineKeyboardMarkup:
    """Keyboard for prism description page with select/back buttons."""
    if loc is None:
        from core.config import get_localization
        loc = get_localization("ru")
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=loc.get_select_button() if hasattr(loc, 'get_select_button') else "✅ Выбрать" if loc.language == "ru" else "✅ Select",
            callback_data=f"select_prism:{prism_id}"
        )],
        [InlineKeyboardButton(
            text=loc.get_back_button(),
            callback_data="settings:prism"
        )]
    ])
    return keyboard


def get_back_to_menu_keyboard(loc=None) -> InlineKeyboardMarkup:
    """Simple back to menu keyboard."""
    if loc is None:
        from core.config import get_localization
        loc = get_localization("ru")
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=loc.get_back_button(), callback_data="back_to_menu")]
    ])
    return keyboard


def get_help_keyboard(current_page: int = 1, loc=None) -> InlineKeyboardMarkup:
    """
    Help keyboard with page navigation.
    
    Args:
        current_page: Current page number (1-4)
        loc: Localization object
    """
    if loc is None:
        from core.config import get_localization
        loc = get_localization("ru")
    
    buttons = []
    
    # Navigation buttons
    nav_buttons = []
    if current_page > 1:
        nav_buttons.append(InlineKeyboardButton(text=loc.get_back_page_button(), callback_data=f"help:page:{current_page - 1}"))
    if current_page < 4:
        nav_buttons.append(InlineKeyboardButton(text=loc.get_forward_page_button(), callback_data=f"help:page:{current_page + 1}"))
    
    if nav_buttons:
        buttons.append(nav_buttons)
    
    # Back to menu
    buttons.append([InlineKeyboardButton(text=loc.get_back_button(), callback_data="back_to_menu")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

