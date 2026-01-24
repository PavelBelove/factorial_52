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


def get_main_menu_keyboard(has_active_game: bool = False) -> InlineKeyboardMarkup:
    """
    Main menu keyboard.
    
    Args:
        has_active_game: If True, shows "Continue" button
    """
    buttons = []
    
    if has_active_game:
        buttons.append([InlineKeyboardButton(text="▶️ Продолжить игру", callback_data="continue")])
    
    buttons.extend([
        [InlineKeyboardButton(text="🆕 Новая игра", callback_data="new_game")],
        [InlineKeyboardButton(text="📂 Загрузить игру", callback_data="load")],
        [InlineKeyboardButton(text="💾 Сохранить игру", callback_data="save")],
        [InlineKeyboardButton(text="⚙️ Настройки", callback_data="settings")],
        [InlineKeyboardButton(text="❓ Помощь", callback_data="help")]
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_world_selection_keyboard(worlds: List[Dict]) -> InlineKeyboardMarkup:
    """
    World selection keyboard.
    
    Args:
        worlds: List of world dicts with keys: id, name, icon, description
    """
    buttons = []
    
    for world in worlds:
        icon = world.get('icon', '🌍')
        name = world.get('name', world['id'])
        callback = f"world:{world['id']}"
        
        buttons.append([InlineKeyboardButton(text=f"{icon} {name}", callback_data=callback)])
    
    # Back button
    buttons.append([InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_menu")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_world_description_keyboard(world_id: str) -> InlineKeyboardMarkup:
    """
    Keyboard for world description screen.
    Shows "Start game" and "Back" buttons.
    
    Args:
        world_id: ID of the world
    """
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🚀 Начать игру", callback_data=f"start:{world_id}")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_worlds")]
    ])
    return keyboard


def get_save_slots_keyboard(saved_sessions: List[Dict]) -> InlineKeyboardMarkup:
    """
    Save slots keyboard.
    
    Args:
        saved_sessions: List of saved session dicts with keys: slot_number, world_id, saved_at
    """
    buttons = []
    
    # Create dict of occupied slots
    occupied = {s['slot_number']: s for s in saved_sessions}
    
    # Show all 5 slots
    for slot in range(1, 6):
        if slot in occupied:
            session = occupied[slot]
            world = session.get('world_id', '?')
            # Show occupied slot
            text = f"💾 Слот {slot}: {world}"
        else:
            # Show empty slot
            text = f"📭 Слот {slot}: Пусто"
        
        buttons.append([InlineKeyboardButton(text=text, callback_data=f"save_slot:{slot}")])
    
    # Back button
    buttons.append([InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_menu")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_load_slots_keyboard(saved_sessions: List[Dict]) -> InlineKeyboardMarkup:
    """
    Load slots keyboard (only shows occupied slots).
    
    Args:
        saved_sessions: List of saved session dicts
    """
    buttons = []
    
    if not saved_sessions:
        # No saves - just back button
        buttons.append([InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_menu")])
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
        
        text = f"📂 Слот {slot}: {world}"
        if date_str:
            text += f" ({date_str})"
        
        buttons.append([InlineKeyboardButton(text=text, callback_data=f"load_slot:{session['id']}")])
    
    # Back button
    buttons.append([InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_menu")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_settings_keyboard() -> InlineKeyboardMarkup:
    """Settings menu keyboard."""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🌐 Язык", callback_data="settings:language")],
        [InlineKeyboardButton(text="◀️ Назад", callback_data="back_to_menu")]
    ])
    return keyboard


def get_back_to_menu_keyboard() -> InlineKeyboardMarkup:
    """Simple back to menu keyboard."""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ В главное меню", callback_data="back_to_menu")]
    ])
    return keyboard

