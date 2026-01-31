"""
Russian localization for PlexMem RPG Bot.
"""
from typing import Dict
from .base import BaseLocalization


class RussianLocalization(BaseLocalization):
    """Russian language implementation."""
    
    language = "ru"  # Add language attribute
    
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
        return (
            "📖 <b>52! Wor‌ld — Бесконечная Книга</b>\n\n"
            "Здесь рождаются истории, которые никогда не повторятся.\n"
            "Каждая тасовка колоды — новая судьба. Каждое решение — новый поворот сюжета.\n\n"
            "Выберите действие:"
        )
    
    def get_main_menu_buttons(self) -> Dict[str, str]:
        return {
            "continue": "📖 Продолжить читать",
            "new_game": "✨ Новое приключение",
            "load": "📚 Из библиотеки",
            "save": "🔖 Положить закладку",
            "settings": "⚙️ Настройки",
            "help": "❓ О книге"
        }
    
    # World selection
    def get_world_selection_message(self) -> str:
        return (
            "🌍 <b>Выбор мира</b>\n\n"
            "В какой книге разворачивается ваша история?\n"
            "Каждый мир уникален и дышит своей атмосферой."
        )
    
    def get_world_start_button(self) -> str:
        return "📖 Начать историю"
    
    # Save/Load
    def get_save_menu_message(self) -> str:
        return "🔖 <b>Положить закладку</b>\n\nВ какую книгу поместить закладку?"
    
    def get_load_menu_message(self) -> str:
        return "📚 <b>Библиотека</b>\n\nКакую книгу открыть?"
    
    def get_slot_label(self, slot: int) -> str:
        return f"Книга {slot}"
    
    def get_empty_slot_label(self) -> str:
        return "📭 Пусто"
    
    def get_no_saves_message(self) -> str:
        return "❌ В библиотеке пусто.\nНачните новое приключение из главного меню."
    
    # Game messages
    def get_game_started_message(self, slot: int) -> str:
        return f"✅ История началась. Закладка в книге {slot}"
    
    def get_game_saved_message(self, slot: int) -> str:
        return f"✅ Закладка помещена в книгу {slot}"
    
    def get_game_loaded_message(self, slot: int) -> str:
        return f"✅ Книга {slot} открыта\n\nМожете продолжить читать!"
    
    def get_creating_world_message(self) -> str:
        return "⏳ Рассказчик готовит вашу уникальную историю...\nЭто может занять минуту."
    
    # Error messages
    def get_no_active_game_message(self) -> str:
        return "❌ Нет открытой книги.\nИспользуйте /menu чтобы начать историю или открыть из библиотеки."
    
    def get_error_message(self) -> str:
        return "❌ Произошла ошибка. Попробуйте еще раз."
    
    def get_save_error_message(self) -> str:
        return "❌ Не удалось поместить закладку. Попробуйте еще раз."
    
    def get_load_error_message(self) -> str:
        return "❌ Не удалось открыть книгу. Возможно, закладка повреждена."
    
    # Navigation
    def get_back_button(self) -> str:
        return "◀️ Назад"
    
    def get_cancel_button(self) -> str:
        return "❌ Отмена"
    
    # Settings
    def get_settings_menu_message(self) -> str:
        return (
            "⚙️ <b>Настройки</b>\n\n"
            "Здесь можно настроить параметры истории."
        )
    
    def get_settings_buttons(self) -> Dict[str, str]:
        return {
            "language": "🌐 Язык",
            "difficulty": "⚔️ Сложность",
            "content": "🔞 Контент"
        }
    
    def get_difficulty_settings_message(self) -> str:
        return (
            "🎮 <b>Сложность</b>\n\n"
            "Влияет на пороги проверок:\n"
            "• 😊 Лёгкая — пороги снижены\n"
            "• ⚔️ Обычная — стандартный баланс\n"
            "• 💀 Сложная — пороги повышены"
        )
    
    def get_content_filter_settings_message(self) -> str:
        return (
            "🔒 <b>Фильтр контента</b>\n\n"
            "Определяет уровень взрослого контента:\n"
            "• 🛡️ Безопасный — без эротики\n"
            "• 💕 16+ — лёгкая романтика\n"
            "• 🔞 18+ — взрослый контент"
        )
    
    def get_genre_prism_settings_message(self) -> str:
        return (
            "🎭 <b>Жанровые призмы</b>\n\n"
            "Выбор призмы меняет угол зрения рассказчика. Мир и судьба остаются теми же, "
            "но акценты смещаются. Призму можно менять в любой момент истории.\n\n"
            "⚠️ — для продвинутых читателей"
        )
    
    def get_genre_prism_description(self, prism_id: str) -> str:
        """Get detailed description for prism selection."""
        from core.genre_prisms import get_prism_info
        info = get_prism_info(prism_id, "ru")
        
        warning = "\n\n⚠️ <i>Для продвинутых: требует вдумчивого участия</i>" if info["advanced"] else ""
        
        return (
            f"{info['emoji']} <b>{info['name']}</b>\n\n"
            f"{info['description']}\n\n"
            f"<b>Примеры:</b>\n{info['examples']}"
            f"{warning}"
        )
    
    # Keyboard labels
    def get_difficulty_label(self, difficulty: str) -> str:
        labels = {
            "easy": "😊 Лёгкая",
            "normal": "⚔️ Обычная",
            "hard": "💀 Сложная"
        }
        return labels.get(difficulty, difficulty)
    
    def get_content_filter_label(self, filter_type: str) -> str:
        labels = {
            "safe": "🛡️ Безопасный",
            "romantic": "💕 16+",
            "adult": "🔞 18+"
        }
        return labels.get(filter_type, filter_type)
    
    def get_confirm_button(self) -> str:
        return "✅ Подтверждаю"
    
    def get_back_page_button(self) -> str:
        return "⬅️ Назад"
    
    def get_forward_page_button(self) -> str:
        return "Вперёд ➡️"
    
    def get_adult_content_consent_message(self) -> str:
        return (
            "⚠️ <b>ВНИМАНИЕ: Взрослый контент (18+)</b>\n\n"
            "Нажимая «Подтверждаю», вы подтверждаете что:\n\n"
            "• Вам исполнилось 18 лет\n"
            "• Просмотр такого контента легален в вашей юрисдикции\n"
            "• Вы добровольно и осознанно снимаете ограничение на эротический контент\n"
            "• Вы понимаете, что история может содержать откровенные сексуальные сцены\n\n"
            "<b>Это решение можно изменить в настройках в любой момент.</b>"
        )
    
    # Help
    def get_help_message(self) -> str:
        """Deprecated - use get_help_page instead."""
        return self.get_help_page(1)
    
    def get_help_page(self, page: int = 1) -> str:
        """Get help page by number."""
        if page == 1:
            return self.get_help_about_book()
        elif page == 2:
            return self.get_help_bot_control()
        elif page == 3:
            return self.get_help_genre_prisms()
        elif page == 4:
            return self.get_help_character_creation()
        elif page == 5:
            return self.get_help_mechanics()
        return self.get_help_about_book()
    
    def get_help_about_book(self) -> str:
        """Help page 1: About 52! World."""
        return (
            "📖 <b>52! Wor‌ld — Бесконечная Книга</b>\n\n"
            
            "<b>Что это?</b>\n"
            "<b>Живая книга</b>, что пишется для вас и вместе с вами. "
            "Искусственный интеллект выступает Рассказчиком, который творит уникальную историю, "
            "реагирующую на каждое ваше решение.\n\n"
            
            "<b>Почему «52!»?</b>\n"
            "Число уникальных тасовок колоды из 52 карт (52!) больше, чем атомов во Вселенной. "
            "Каждая история в каждом мире — <b>абсолютно уникальна</b>. Ваша книга никогда не повторится.\n\n"
            "Карты — источник <b>случайности и сюжетных поворотов</b>, чтобы история не стала пресной. "
            "Рассказчик не знает результата заранее — он узнаёт его вместе с вами.\n\n"
            
            "<b>Адаптивная память</b>\n"
            "Система запоминает всё: ваши решения, диалоги, союзников и врагов. "
            "Персонажи не забывают ваши поступки, а прошлые выборы влияют на будущие главы. \n"
            "Эта история помнит вас — даже через сотни страниц.\n\n"
            
            "<i>Страница 1 из 4</i>"
        )
    
    def get_help_character_creation(self) -> str:
        """Help page 3: Character creation."""
        return (
            "✨ <b>Создание героя</b>\n\n"
            
            "<b>Начало истории:</b>\n"
            "При создании персонажа вы вытягиваете 5 карт для определения характеристик. \n "
            "Худшая отбрасывается, остальные влияют на характеристики. Распределите сами, или доверьте рассказчику.\n"
            "Но это лишь основа — <b>опишите своего героя!</b>\n\n"
            
            "<b>Что можно описать:</b>\n"
            "• <b>Внешность</b> — как выглядит ваш герой?\n"
            "• <b>Историю</b> — откуда он пришёл? Что пережил?\n"
            "• <b>Характер</b> — смелый? Осторожный? Циничный?\n"
            "• <b>Уникальные черты</b> — которые делают его особенным\n"
            "• <b>Предпочтения</b> — что вы хотите видеть в истории?\n"
            "• <b>Все что угодно!</b> — Хотите радужных единорогов? Самое время рассказать о них.\n\n"

            "<b>Рассказчик запомнит всё:</b>\n"
            "Всё, что вы опишете, станет частью вашей книги. Перонажи будут реагировать на внешность героя, "
            "его прошлое повлияет на сюжет, а предпочтения помогут Рассказчику создать идеальную историю.\n\n"
            
            "<b>Четыре характеристики:</b>\n"
            "♠ <b>Сила</b> — ближний бой, воля, запугивание\n"
            "♥ <b>Магия</b> — колдовство, мудрость, общение\n"
            "♦ <b>Стойкость</b> — защита, выносливость, торговля\n"
            "♣ <b>Ловкость</b> — дальний бой, акробатика, скрытность\n\n"
            
            "<i>Страница 4 из 5</i>"
        )
    
    def get_help_mechanics(self) -> str:
        """Help page 4: Game mechanics (based on real code)."""
        return (
            "🎴 <b>Механики Factorial 52!</b>\n\n"
            
            "<b>Проверки (вне боя):</b>\n"
            "Рассказчик тянет 2 карты. Формула:\n"
            "<code>Результат = (карта1×10 + бонус1) + (карта2×10 + бонус2) + характеристика</code>\n\n"
            
            "<b>Бонусы карт:</b>\n"
            "• Масть совпадает с проверкой: <b>+20</b>\n"
            "• Цвет совпадает (нет совпадения масти): <b>+10</b>\n"
            "• Нет совпадений: <b>0</b>\n\n"
            
            "<b>Пример:</b> Акробатика (♣)\n"
            "Выпали 8♥ и К♣\n"
            "• 8♥: 80 + 0 (красная) = 80\n"
            "• К♣: 130 + 20 (масть!) = 150\n"
            "• + 60 (ловкость) = <b>290</b>\n\n"
            
            "<b>Пороги сложности:</b>\n"
            "Лёгкая | Средняя | Сложная | Очень сложная\n"
            "Уровень сложности задается в настройках\n\n"
            
            "<b>Особые комбинации (Влияют на сюжет, только вне боя):</b>\n"
            "<b>J</b> - Валет: Вносит неожиданный сюжетный поворот\n"
            "<b>Q</b> - Дама: Влияние женского персонажа/энергии\n"
            "<b>K</b> - Король: Влияние мужского персонажа/энергии\n"
            "🃏🃏 Два туза — божественный успех\n"
            "🂢🂢 Две двойки — катастрофа\n\n"
            
            "<b>Развитие:</b>\n"
            "За успешную проверку +1 XP к характеристике. "
            "При 10 XP: +1 к характеристике, +1 к HP и мане.\n\n"
            
            "<i>Страница 5 из 5</i>"
        )
    
    def get_help_bot_control(self) -> str:
        """Help page 2: Bot control."""
        return (
            "🎮 <b>Управление книгой</b>\n\n"
            
            "<b>Команды:</b>\n"
            "/menu — главное меню\n"
            "/stats — характеристики героя\n"
            "/inventory — инвентарь\n"
            "/undo — отменить последнюю страницу\n"
            "/retry — переписать последнюю страницу\n"
            "/session — статистика истории\n"
            "/help — эта справка\n\n"
            
            "<b>Как взаимодействовать:</b>\n"
            "Просто пишите свои действия. "
            "Рассказчик опишет результаты и развитие истории.\n\n"
            
            "<b>Прямая речь с Рассказчиком:</b>\n"
            "Сообщение [в квадратных скобках] — это обращение напрямую к Рассказчику, вне истории. "
            "Используйте для описания предпочтений, исправления ошибок или уточнений.\n\n"
            
            "<b>⚠️ Об отменах и повторах:</b>\n"
            "/undo и /retry — для исправления технических сбоев и галлюцинаций ИИ, "
            "а не для «перематывания» неудачных моментов. Неудачи — часть истории!\n\n"
            
            "<b>Сохранения:</b>\n"
            "Используйте закладки (до 5 книг одновременно) "
            "для переключения между разными историями.\n\n"
            
            "<i>Страница 2 из 5</i>"
        )
    
    def get_help_genre_prisms(self) -> str:
        """Help page 3: Genre prisms."""
        return (
            "🎭 <b>Жанровые призмы</b>\n\n"
            
            "<b>Что это?</b>\n"
            "«Призма» — это <b>угол зрения Рассказчика</b>. Она меняет <b>тон повествования</b>, "
            "не меняя сам мир или события.\n\n"
            
            "<b>Как работает?</b>\n"
            "• <b>Мир остаётся тем же</b> — киберпанк останется киберпанком\n"
            "• <b>Меняются акценты</b> — что выходит на первый план\n"
            "• <b>Можно менять в любой момент</b> через ⚙️ Настройки → Жанровые призмы\n\n"
            
            "<b>Примеры:</b>\n"
            "🔥 Экшен — больше боёв и погонь\n"
            "🕸 Интриги — скрытые мотивы и манипуляции\n"
            "❤️ Романтика — чувства на первом плане\n"
            "👁 Хоррор — гнетущая атмосфера\n"
            "🧠 Психология — сложные отношения\n\n"
            
            "<b>Комбинации работают!</b>\n"
            "Киберпанк-романтика, исекай-хоррор — <b>не баг, а фича</b>.\n\n"
            
            "<b>⚠️ Продвинутые призмы:</b>\n"
            "Призмы с символом ⚠️ (Сюрреализм, Временные петли) требуют вдумчивого участия. "
            "Круто, но нужно активнее направлять сюжет, иначе может выйти из-под контроля.\n\n"
            
            "<b>Игровой эффект:</b>\n"
            "Призмы могут сделать историю более игровой (Level Up, Выживание) или наоборот, "
            "глубокой и философской.\n\n"
            
            "<i>Страница 3 из 5</i>"
        )
    
    # Additional game messages
    def get_initial_game_message(self, world_id: str) -> str:
        return (
            f"📖 <b>Книга открывается...</b>\n\n"
            f"Ваша история начинается.\n\n"
            f"Опишите своего героя или напишите первое действие!"
        )
    
    def get_story_started_header(self) -> str:
        return "📖 <b>История началась!</b>\n\n"
    
    def get_story_continues_header(self) -> str:
        return "▶️ <b>История продолжается</b>\n\n"
    
    def get_chapter_label(self, chapter_num: int) -> str:
        return f"📖 Глава #{chapter_num}"
    
    def get_last_chapter_label(self, chapter_num: int) -> str:
        return f"<b>📝 Последняя глава #{chapter_num}:</b>\n\n"
    
    def get_undo_success(self, current_chapter: int) -> str:
        return f"✅ Глава отменена. Теперь глава #{current_chapter}\n"
    
    def get_undo_nothing_to_undo(self) -> str:
        return "❌ Нечего отменять (история только началась)"
    
    def get_error_message(self) -> str:
        return "❌ Ошибка"
    
    def get_creating_world_message(self) -> str:
        return (
            "⏳ Создаю новый мир и готовлю приключение...\n\n"
            "Это может занять минуту."
        )
    
    def get_empty_inventory_message(self) -> str:
        return "🎒 Инвентарь пуст"
    
    def get_continue_game_message(self) -> str:
        return (
            "📖 <b>Продолжаем читать</b>\n\n"
            "Что делает ваш герой?"
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


