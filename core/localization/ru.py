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
        """Deprecated - use get_help_page instead."""
        return self.get_help_page(1)
    
    def get_help_page(self, page: int = 1) -> str:
        """Get help page by number."""
        if page == 1:
            return self.get_help_about_game()
        elif page == 2:
            return self.get_help_bot_control()
        elif page == 3:
            return self.get_help_game_rules()
        return self.get_help_about_game()
    
    def get_help_about_game(self) -> str:
        """Help page 1: About the game."""
        return (
            "🎮 <b>О игре PlexMem RPG</b>\n\n"
            
            "<b>Что это?</b>\n"
            "Текстовая ролевая игра с ИИ-Гейм-Мастером, который создаёт уникальную историю специально для вас.\n\n"
            
            "<b>Преимущества:</b>\n"
            "• <b>Долгие сессии без протухания</b> - можете играть месяцами, сюжет не развалится\n"
            "• <b>Живой мир</b> - NPC обладают характерами, интересами и памятью о ваших действиях\n"
            "• <b>Книга-игра на лету</b> - история пишется в реальном времени и реагирует на ваши решения\n"
            "• <b>Честный рандом</b> - механика основана на колоде из 52 карт, как магический покер\n"
            "• <b>RPG-элементы</b> - характеристики, инвентарь, прокачка персонажа\n"
            "• <b>Уникальность</b> - каждая игра абсолютно неповторима\n"
            "• <b>Выбор миров</b> - от исекай до киберпанка\n\n"
            
            "<i>Страница 1 из 3</i>"
        )
    
    def get_help_bot_control(self) -> str:
        """Help page 2: Bot control."""
        return (
            "🎮 <b>Управление ботом</b>\n\n"
            
            "<b>Основные команды:</b>\n"
            "/start или /menu - Главное меню\n"
            "/stats - Характеристики персонажа\n"
            "/inventory - Инвентарь\n"
            "/undo - Отменить последний ход\n"
            "/retry - Повторить последний ход\n"
            "/help - Эта справка\n\n"
            
            "<b>Как играть:</b>\n"
            "Просто пишите свои действия обычным текстом. ГМ опишет результаты и развитие сюжета.\n\n"
            
            "<b>Общение с ГМ:</b>\n"
            "Можете написать сообщение [в квадратных скобках] - так вы говорите напрямую с ГМ вне игры.\n"
            "Используйте это для описания предпочтений в игре, исправления ошибок или уточнений.\n\n"
            
            "<b>⚠️ Важно об отменах и повторах:</b>\n"
            "Команды /undo и /retry предназначены для исправления галлюцинаций ИИ и технических сбоев.\n"
            "Не злоупотребляйте ими для \"перематывания\" неудачных моментов - это часть игры!\n\n"
            
            "<i>Страница 2 из 3</i>"
        )
    
    def get_help_game_rules(self) -> str:
        """Help page 3: Game mechanics."""
        return (
            "🎮 <b>Правила игры (Факториал 52!)</b>\n\n"
            
            "<b>Характеристики:</b>\n"
            "♠ <b>Сила</b> - ближний бой, физическая сила, воля, запугивание\n"
            "♥ <b>Магия</b> - магическая защита, колдовство, мудрость, общение\n"
            "♦ <b>Стойкость</b> - физическая защита, выносливость, харизма, торговля\n"
            "♣ <b>Ловкость</b> - дальний бой, магические атаки, акробатика, скрытность\n\n"
            
            "<b>Проверки вне боя:</b>\n"
            "ГМ тянет 2 карты. Результат = (сумма номиналов × 10) + характеристика + бонусы\n"
            "• Карты одного цвета: +10 (красные) или -10 (черные)\n"
            "• Карты одной масти: +20 (красные) или -20 (черные)\n\n"
            
            "<b>Бой:</b>\n"
            "Используются 2 карты для каждого действия\n"
            "• Черные карты (♠♣) - атака\n"
            "• Красные карты (♥♦) - защита\n"
            "• Урон = атака - защита\n"
            "• Бонус за совпадение масти с характеристикой\n\n"
            
            "<b>Особые комбинации:</b>\n"
            "🃏🃏 Два туза - Невероятный успех!\n"
            "🂢🂢 Две двойки - Катастрофа!\n\n"
            
            "<b>Развитие:</b>\n"
            "За каждый успех +1 к соответствующей характеристике\n\n"
            
            "<i>Страница 3 из 3</i>"
        )
    
    # Additional game messages
    def get_initial_game_message(self, world_id: str) -> str:
        return (
            f"🎮 <b>Добро пожаловать в мир приключений!</b>\n\n"
            f"Ваше путешествие начинается...\n\n"
            f"Напишите свое первое действие, чтобы начать игру!"
        )
    
    def get_continue_game_message(self) -> str:
        return (
            "▶️ <b>Игра продолжается</b>\n\n"
            "Напишите свое действие, чтобы продолжить приключение!"
        )
    
    def get_game_rules(self) -> str:
        return (
            "📜 <b>Правила игры</b>\n\n"
            
            "<b>1. Свобода действий</b>\n"
            "Вы можете делать всё, что угодно. Пишите свои действия естественным языком.\n\n"
            
            "<b>2. Последствия</b>\n"
            "Каждое ваше действие имеет последствия. Думайте стратегически!\n\n"
            
            "<b>3. Система памяти</b>\n"
            "ИИ помнит всё: персонажей, события, ваши решения и их последствия.\n\n"
            
            "<b>4. Персонаж</b>\n"
            "У вашего персонажа есть характеристики, инвентарь и история.\n"
            "Используйте команды /stats и /inventory для просмотра.\n\n"
            
            "<b>5. Сохранения</b>\n"
            "Игра автоматически сохраняется. Вы можете иметь до 5 разных игр одновременно.\n\n"
            
            "<b>6. Отмена действий</b>\n"
            "Используйте /undo для отмены последнего хода и /retry для повтора с другим результатом.\n\n"
            
            "<b>Наслаждайтесь игрой! 🎭</b>"
        )


