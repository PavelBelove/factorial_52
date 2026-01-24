"""
Russian localization for PlexMem RPG Bot.
"""
from typing import Dict
from .base import BaseLocalization


class RussianLocalization(BaseLocalization):
    """Russian language implementation."""
    
    def get_language_code(self) -> str:
        return "ru"
    
    def get_language_name(self) -> str:
        return "Русский"
    
    # Language selection
    def get_language_selection_message(self) -> str:
        return "Выберите язык / Choose your language:"
    
    def get_available_languages(self) -> Dict[str, str]:
        return {
            "ru": "🇷🇺 Русский",
            "en": "🇬🇧 English"
        }
    
    # Main menu
    def get_main_menu_message(self) -> str:
        return "🎮 <b>Главное меню</b>\n\nВыберите действие:"
    
    def get_main_menu_buttons(self) -> Dict[str, str]:
        return {
            "continue": "▶️ Продолжить игру",
            "new_game": "🆕 Новая игра",
            "load": "📂 Загрузить игру",
            "save": "💾 Сохранить игру",
            "settings": "⚙️ Настройки",
            "help": "❓ Помощь"
        }
    
    # World selection
    def get_world_selection_message(self) -> str:
        return (
            "🌍 <b>Выбор мира</b>\n\n"
            "Выберите мир для вашего приключения.\n"
            "Каждый мир уникален и предлагает свою атмосферу!"
        )
    
    def get_world_start_button(self) -> str:
        return "🚀 Начать игру"
    
    # Save/Load
    def get_save_menu_message(self) -> str:
        return "💾 <b>Сохранить игру</b>\n\nВыберите слот для сохранения:"
    
    def get_load_menu_message(self) -> str:
        return "📂 <b>Загрузить игру</b>\n\nВыберите сохранение для загрузки:"
    
    def get_slot_label(self, slot: int) -> str:
        return f"Слот {slot}"
    
    def get_empty_slot_label(self) -> str:
        return "📭 Пусто"
    
    def get_no_saves_message(self) -> str:
        return "❌ У вас нет сохраненных игр.\nНачните новую игру из главного меню."
    
    # Game messages
    def get_game_started_message(self, slot: int) -> str:
        return f"✅ Игра создана и сохранена в слот {slot}"
    
    def get_game_saved_message(self, slot: int) -> str:
        return f"✅ Игра сохранена в слот {slot}"
    
    def get_game_loaded_message(self, slot: int) -> str:
        return f"✅ Игра загружена из слота {slot}\n\nМожете продолжить свое приключение!"
    
    def get_creating_world_message(self) -> str:
        return "⏳ Создаю ваш уникальный игровой мир...\nЭто может занять минуту."
    
    # Error messages
    def get_no_active_game_message(self) -> str:
        return "❌ Нет активной игры.\nИспользуйте /start или загрузите сохранение."
    
    def get_error_message(self) -> str:
        return "❌ Произошла ошибка. Попробуйте еще раз."
    
    def get_save_error_message(self) -> str:
        return "❌ Не удалось сохранить игру. Попробуйте еще раз."
    
    def get_load_error_message(self) -> str:
        return "❌ Не удалось загрузить игру. Возможно, сохранение повреждено."
    
    # Navigation
    def get_back_button(self) -> str:
        return "◀️ Назад"
    
    def get_cancel_button(self) -> str:
        return "❌ Отмена"
    
    # Settings
    def get_settings_menu_message(self) -> str:
        return (
            "⚙️ <b>Настройки</b>\n\n"
            "Здесь можно настроить параметры игры."
        )
    
    def get_settings_buttons(self) -> Dict[str, str]:
        return {
            "language": "🌐 Язык",
            "difficulty": "⚔️ Сложность",
            "content": "🔞 Контент"
        }
    
    # Help
    def get_help_message(self) -> str:
        return (
            "❓ <b>Помощь</b>\n\n"
            "<b>Что такое PlexMem RPG?</b>\n"
            "Это текстовая ролевая игра с ИИ-Гейм-Мастером, который создает уникальную историю специально для вас.\n\n"
            
            "<b>Как играть?</b>\n"
            "1. Выберите мир\n"
            "2. Создайте персонажа\n"
            "3. Пишите свои действия обычным текстом\n"
            "4. ГМ опишет результаты и развитие сюжета\n\n"
            
            "<b>Команды:</b>\n"
            "/start - Главное меню\n"
            "/stats - Характеристики персонажа\n"
            "/inventory - Инвентарь\n"
            "/undo - Отменить последний ход\n"
            "/retry - Повторить последний ход\n"
            "/help - Эта справка\n\n"
            
            "<b>Система памяти:</b>\n"
            "ИИ помнит все события, персонажей, места и ваши решения благодаря квантовой системе памяти.\n\n"
            
            "<b>Сохранения:</b>\n"
            "У вас есть 5 слотов для сохранения разных игр. Игра автоматически сохраняется при создании."
        )

