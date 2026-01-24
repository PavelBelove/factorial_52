# План миграции функционала из старого бота

## Исходные материалы

### Старый проект (изучен в `old_archive_version/plexmem_bot-main/`)
- ✅ `quantum_rpg_bot/handlers/menu_handlers.py` - обработчики меню, выбор языка, выбор мира, сохранение/загрузка
- ✅ `quantum_rpg_bot/localization/` - система локализации (base.py, ru.py, en.py, es.py, ar.py, hi.py, pt.py)
- ✅ `quantum_rpg_bot/prompts/worlds/` - конфигурация миров в JSON (isekai.json, garmonia.json, slavic.json, cyberpunk.json, steampunk.json, magic_academy.json, rebirth.json)
- ✅ `quantum_rpg_bot/database.py` - работа с сохранениями, слотами, играми
- ✅ `quantum_rpg_bot/config.py` - конфигурация с языками и мирами

### Текущий проект
- ✅ Современная архитектура с квантовой памятью (core/)
- ✅ API-based подход (FastAPI)
- ✅ Простой Telegram бот (telegram/bot.py)
- ✅ Улучшенная система памяти с квантами
- ✅ Игровая механика (карты, характеристики, инвентарь)

---

## Общая стратегия

1. **Не трогать ядро** - система памяти (Quantizer, Summarizer, MemoryManager) работает отлично
2. **Расширить конфигурацию** - добавить поддержку миров и языков
3. **Переработать Telegram бот** - добавить меню, FSM-состояния, локализацию
4. **Создать структуру миров** - каждый мир = отдельная папка с конфигом
5. **Реализовать систему сохранений** - слоты, загрузка/сохранение игр

---

## Этап 1: Подготовка структуры проекта

### 1.1 Создать систему локализации
**Референс:** `old_archive_version/plexmem_bot-main/quantum_rpg_bot/localization/`

**Файлы для создания:**
```
core/localization/
├── __init__.py
├── base.py          # Базовый класс локализации (как в старом проекте)
└── ru.py            # Русская локализация (копировать структуру из старого)
```

**Содержимое:**
- `base.py` - абстрактный класс с методами для всех текстов интерфейса
- `ru.py` - реализация на русском языке (пока единственная)
- Заглушки для других языков (en.py, es.py и т.д.) создать ПУСТЫМИ

**Методы локализации (из старого проекта):**
- `get_language_selection_message()` - выбор языка
- `get_main_menu()` - главное меню
- `get_world_selection_message()` - выбор мира
- `get_world_buttons()` - кнопки миров
- `get_world_descriptions()` - описания миров
- `get_save_game()` - меню сохранения
- `get_load_game()` - меню загрузки
- `get_error_messages()` - сообщения об ошибках
- `get_confirmation_messages()` - подтверждения
- И т.д. (см. `old_archive_version/.../localization/base.py`)

---

### 1.2 Создать структуру миров
**Референс:** `old_archive_version/plexmem_bot-main/quantum_rpg_bot/prompts/worlds/`

**Структура:**
```
data/worlds/
├── isekai/                      # Исекай мир (единственный заполненный)
│   ├── config.json              # Конфигурация мира
│   ├── initial_quants.json      # Стартовые кванты
│   ├── initial_summary.md       # Стартовая сводка
│   └── quantizer_instructions.md # Специфичные инструкции для Quantizer
│
├── cyberpunk/                   # Заглушки для других миров
│   ├── config.json              # Минимальная конфигурация
│   ├── initial_quants.json      # ПУСТОЙ - TODO
│   ├── initial_summary.md       # ПУСТОЙ - TODO
│   └── quantizer_instructions.md # ПУСТОЙ - TODO
├── steampunk/
│   ├── config.json
│   ├── initial_quants.json      # ПУСТОЙ
│   ├── initial_summary.md       # ПУСТОЙ
│   └── quantizer_instructions.md # ПУСТОЙ
├── magic_academy/
│   ├── config.json
│   ├── initial_quants.json      # ПУСТОЙ
│   ├── initial_summary.md       # ПУСТОЙ
│   └── quantizer_instructions.md # ПУСТОЙ
├── slavic/
│   ├── config.json
│   ├── initial_quants.json      # ПУСТОЙ
│   ├── initial_summary.md       # ПУСТОЙ
│   └── quantizer_instructions.md # ПУСТОЙ
└── fallout/                     # Постапокалипсис вместо гармонии
    ├── config.json
    ├── initial_quants.json      # ПУСТОЙ
    ├── initial_summary.md       # ПУСТОЙ
    └── quantizer_instructions.md # ПУСТОЙ
```

**Формат config.json для мира:**
```json
{
  "id": "isekai",
  "name": {
    "ru": "Исекай",
    "en": "Isekai"
  },
  "description": {
    "ru": "Типичный мир аниме-исекай с магией, гильдией авантюристов и системой уровней",
    "en": "Typical anime-isekai world with magic, adventurer's guild and level system"
  },
  "icon": "🌟",
  "enabled": true,
  "has_content": true
}
```

**Для других миров has_content: false**

**ВАЖНО:** Список миров должен быть расширяемым. WorldManager должен сканировать папку `data/worlds/` и динамически загружать все найденные миры по их config.json. Это позволит добавлять новые миры просто создав новую папку.

---

### 1.3 Расширить конфигурацию
**Файл:** `core/config.py`

**Добавить:**
```python
class Settings(BaseSettings):
    # ... существующие настройки ...
    
    # Локализация
    default_language: str = "ru"
    available_languages: list[str] = ["ru"]  # Пока только русский
    
    # Миры
    worlds_directory: Path = DATA_DIR / "worlds"
    default_world: str = "isekai"
    
    # Сохранения
    max_save_slots: int = 5
    
    # Telegram FSM
    fsm_ttl_seconds: int = 3600  # Время жизни состояния FSM
    
    # Шаблонизация промптов (задел на будущее)
    # Это позволит настраивать геймплей через переменные в промптах
    prompt_use_templates: bool = True  # Включить шаблонизацию
```

**ВАЖНО - Шаблонизация промптов:**

Промпты будут использовать шаблонизатор (например, Jinja2) для подстановки настроек пользователя.

**Примеры переменных для будущего:**
- `{difficulty}` - блок с инструкциями по сложности
- `{content_policy}` - блок с политикой контента (18+)
- `{game_style}` - стиль ведения игры
- `{world_setting}` - сеттинг мира

**Пример шаблона (пока не реализуем, но структура должна это поддерживать):**
```markdown
# GM System Prompt

You are Game Master...

## Difficulty Mode
{{ difficulty_instructions }}

## Content Policy
{{ content_policy }}

## World Setting
{{ world_setting }}
```

**Значения переменных:**
```python
# difficulty_instructions:
"easy": "Create interesting narrative, help player succeed"
"hard": "Don't help player, constantly create challenges, make game extremely difficult"

# content_policy:
"safe": "Avoid erotic scenes, user may be a child"
"adult": "User gave informed consent for sexual and erotic content"
```

**Пока:**
- Создаем структуру для поддержки шаблонов
- Используем дефолтные значения
- В будущем добавим UI для настройки

---

## Этап 2: Расширение базы данных

### 2.1 Пересоздать базу данных с новыми моделями
**ВАЖНО:** База не ценна, проще пересоздать с нуля чем мигрировать.

**Файл:** `core/database/models.py`

**Изменения в моделях:**
```python
# users уже есть, расширить:
class User:
    # ... существующие поля ...
    language: str = "ru"           # Язык пользователя
    current_world: str = "isekai"  # Текущий мир
    
# sessions уже есть, расширить:
class Session:
    # ... существующие поля ...
    world_id: str                  # Мир этой сессии
    slot_number: int = None        # Слот сохранения (1-5, None если не сохранена)
    is_saved: bool = False         # Сохранена ли игра
    saved_at: datetime = None      # Когда сохранена
```

**Важно:** Сессия теперь привязана к миру. При создании новой игры указывается `world_id`.

---

### 2.2 Добавить методы для работы с сохранениями
**Файл:** `core/database/db_manager.py`

**Методы для добавления:**
```python
class DatabaseManager:
    # Сохранения
    async def get_user_saved_sessions(self, user_id: int) -> List[Session]:
        """Получить все сохраненные сессии пользователя"""
        
    async def save_session_to_slot(self, session_id: int, slot: int) -> bool:
        """Сохранить сессию в слот (1-5)"""
        
    async def get_session_in_slot(self, user_id: int, slot: int) -> Optional[Session]:
        """Получить сессию в слоте"""
        
    async def delete_session_from_slot(self, session_id: int) -> bool:
        """Удалить сессию из слота (deactivate)"""
    
    # Языки и миры
    async def set_user_language(self, user_id: int, language: str):
        """Установить язык пользователя"""
        
    async def get_user_language(self, user_id: int) -> str:
        """Получить язык пользователя"""
```

---

## Этап 3: Система миров (WorldManager)

### 3.1 Создать менеджер миров
**Новый файл:** `core/managers/world_manager.py`

**Функционал:**
```python
class WorldManager:
    """Управление мирами игры"""
    
    def __init__(self, worlds_dir: Path):
        self.worlds_dir = worlds_dir
        self._worlds_cache = {}  # Кэш загруженных миров
    
    async def scan_worlds(self) -> List[str]:
        """Сканировать папку worlds/ и найти все доступные миры"""
        # Пройти по всем подпапкам data/worlds/
        # Для каждой проверить наличие config.json
        # Вернуть список world_id
    
    async def get_available_worlds(self, language: str = "ru") -> List[Dict]:
        """Получить список доступных миров (enabled=True, has_content=True)"""
        # Сканировать data/worlds/, читать config.json
        # Фильтровать по enabled=True и has_content=True
        # Вернуть список с name, description, icon
    
    async def get_world_config(self, world_id: str) -> Dict:
        """Получить полную конфигурацию мира"""
        # Читать config.json из data/worlds/{world_id}/
    
    async def load_world_initial_data(self, world_id: str, language: str = "ru") -> Dict:
        """Загрузить начальные данные мира для новой игры"""
        # Вернуть:
        # - initial_quants: List[Dict] (из initial_quants.json)
        # - initial_summary: str (из initial_summary.md)
        # - quantizer_instructions: str (из quantizer_instructions.md)
    
    async def get_quantizer_instructions(self, world_id: str) -> str:
        """Получить специфичные инструкции для Quantizer для данного мира"""
        # Читать data/worlds/{world_id}/quantizer_instructions.md
        # Это будет добавляться к базовому промпту Quantizer
```

**ВАЖНО - Промпты агентов:**

1. **GM Agent:** Промпт НЕ зависит от мира (базовый `prompts/gm_system_ru.md`)
2. **Quantizer Agent:** Промпт = базовый + специфичные инструкции для мира
   - Базовый: `prompts/quantizer_system_ru.md`
   - Добавка: `data/worlds/{world_id}/quantizer_instructions.md`
3. **Summarizer Agent:** Промпт не зависит от мира (как есть)

**Структура инструкций Quantizer для мира:**
```markdown
# World-specific instructions for Quantizer: Isekai

## Key concepts for this world
- Magic system and mana
- Level system and stats
- Adventurer guild and quests
- Multiple races (humans, elves, beastfolk, etc)

## Typical quants to create
- NPCs with race and class
- Locations (towns, dungeons, guild halls)
- Quest items and artifacts
- Monster types

## World-specific rules
- Track character level progression
- Manage guild rank (F to S)
- Handle magic schools and spells
```

---

## Этап 4: Переработка Telegram бота

### 4.1 Добавить FSM (Finite State Machine)
**Референс:** `old_archive_version/plexmem_bot-main/quantum_rpg_bot/handlers/menu_handlers.py`

**Файл:** `telegram/states.py` (новый)

**Состояния:**
```python
from aiogram.fsm.state import State, StatesGroup

class GameStates(StatesGroup):
    """Состояния игры"""
    
    # Выбор языка (только для новых пользователей)
    LANGUAGE_SELECTION = State()
    
    # Главное меню
    MAIN_MENU = State()
    
    # Выбор мира
    WORLD_SELECTION = State()
    WORLD_DESCRIPTION = State()  # Показ описания мира перед началом
    
    # В игре
    IN_GAME = State()
    
    # Сохранение/загрузка
    SAVE_GAME = State()
    LOAD_GAME = State()
    
    # Настройки
    SETTINGS = State()
```

---

### 4.2 Переработать бот с меню
**Файл:** `telegram/bot.py`

**Изменения:**
1. **Добавить FSM Storage:**
```python
from aiogram.fsm.storage.memory import MemoryStorage

self.storage = MemoryStorage()  # Уже есть
```

2. **Добавить обработчики меню:**
- `/start` - теперь показывает главное меню (или выбор языка для новых)
- Inline-кнопки для навигации
- Callback-обработчики для каждой кнопки

3. **Разбить на модули:**
```
telegram/
├── bot.py              # Главный файл, инициализация
├── states.py           # FSM-состояния
├── handlers/
│   ├── __init__.py
│   ├── menu.py         # Обработчики меню
│   ├── game.py         # Обработчики игры
│   ├── saves.py        # Сохранение/загрузка
│   └── settings.py     # Настройки
└── keyboards/
    ├── __init__.py
    └── inline.py       # Inline-клавиатуры
```

---

### 4.3 Создать клавиатуры
**Файл:** `telegram/keyboards/inline.py`

**Клавиатуры:**
```python
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_language_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура выбора языка"""
    # Пока только "🇷🇺 Русский"

def get_main_menu_keyboard(has_active_game: bool) -> InlineKeyboardMarkup:
    """Главное меню"""
    # Кнопки: Новая игра, Загрузить, Сохранить (если есть активная), Настройки

def get_world_selection_keyboard(worlds: List[Dict]) -> InlineKeyboardMarkup:
    """Выбор мира"""
    # Кнопки для каждого доступного мира

def get_world_description_keyboard(world_id: str) -> InlineKeyboardMarkup:
    """Описание мира с кнопками начать/назад"""

def get_save_slots_keyboard(saves: List[Session]) -> InlineKeyboardMarkup:
    """Слоты сохранения (1-5)"""
    # Показывать какие заняты, какие пусты

def get_load_slots_keyboard(saves: List[Session]) -> InlineKeyboardMarkup:
    """Слоты загрузки (только занятые)"""
```

---

### 4.4 Обработчики меню
**Файл:** `telegram/handlers/menu.py`

**Функции:**
```python
async def cmd_start(message: Message, state: FSMContext):
    """
    Команда /start
    - Для нового пользователя: выбор языка
    - Для существующего: главное меню
    """

async def show_main_menu(callback: CallbackQuery, state: FSMContext):
    """Показать главное меню"""

async def show_world_selection(callback: CallbackQuery, state: FSMContext):
    """Показать выбор мира"""

async def show_world_description(callback: CallbackQuery, state: FSMContext):
    """Показать описание выбранного мира"""
    # callback.data = "world:isekai"

async def start_new_game(callback: CallbackQuery, state: FSMContext):
    """Начать новую игру в выбранном мире"""
    # callback.data = "start_game:isekai"
    # 1. Создать сессию с world_id через API
    # 2. Загрузить начальные данные мира
    # 3. Отправить начальное сообщение
    # 4. Перейти в состояние IN_GAME

async def back_to_main_menu(callback: CallbackQuery, state: FSMContext):
    """Вернуться в главное меню"""
```

---

### 4.5 Обработчики сохранений
**Файл:** `telegram/handlers/saves.py`

**Функции:**
```python
async def show_save_menu(callback: CallbackQuery, state: FSMContext):
    """Показать меню сохранения (выбор слота)"""

async def save_to_slot(callback: CallbackQuery, state: FSMContext):
    """Сохранить игру в слот"""
    # callback.data = "save_slot:1"

async def show_load_menu(callback: CallbackQuery, state: FSMContext):
    """Показать меню загрузки"""

async def load_from_slot(callback: CallbackQuery, state: FSMContext):
    """Загрузить игру из слота"""
    # callback.data = "load_slot:2"
```

---

## Этап 5: Интеграция с API

### 5.1 Расширить API endpoints
**Файл:** `core/api/routes.py`

**Новые endpoints:**
```python
# Миры
@router.get("/worlds")
async def get_available_worlds(language: str = "ru"):
    """Получить список доступных миров"""

@router.get("/worlds/{world_id}")
async def get_world_info(world_id: str, language: str = "ru"):
    """Получить информацию о мире"""

# Создание сессии с миром
@router.post("/sessions")
async def create_session(
    platform_id: str,
    platform_type: str,
    world_id: str,  # Новый параметр
    language: str = "ru"
):
    """Создать новую сессию в указанном мире"""
    # 1. Загрузить initial data через WorldManager
    # 2. Создать сессию с world_id
    # 3. Записать initial_quants и initial_summary

# Сохранения
@router.post("/sessions/{session_id}/save")
async def save_session(session_id: int, slot: int):
    """Сохранить сессию в слот"""

@router.get("/users/{user_id}/saves")
async def get_user_saves(user_id: int):
    """Получить все сохранения пользователя"""

@router.post("/sessions/{session_id}/load")
async def load_session(session_id: int):
    """Активировать сохраненную сессию"""

# Язык пользователя
@router.post("/users/{user_id}/language")
async def set_user_language(user_id: int, language: str):
    """Установить язык пользователя"""

@router.get("/users/{user_id}/language")
async def get_user_language(user_id: int):
    """Получить язык пользователя"""
```

---

## Этап 6: Адаптация миров

### 6.1 Создать контент для мира "isekai"
**Референс:** 
- `old_archive_version/.../prompts/worlds/old/isekai.json`
- Текущие `data/initial_quants.json` и `data/initial_summary.md`

**Файлы для создания:**

**1. `data/worlds/isekai/config.json`**
```json
{
  "id": "isekai",
  "name": {
    "ru": "Исекай",
    "en": "Isekai"
  },
  "description": {
    "ru": "Типичный мир аниме-исекай. Фэнтези-мир с магией, гильдией авантюристов, системой уровней. Классическое перерождение в новом мире с уникальными способностями.",
    "en": "Typical anime-isekai world. Fantasy world with magic, adventurer's guild, level system. Classic rebirth in new world with unique abilities."
  },
  "icon": "🌟",
  "enabled": true,
  "has_content": true,
  "features": {
    "magic_system": true,
    "level_system": true,
    "guilds": true,
    "multiple_races": true
  }
}
```

**2. `data/worlds/isekai/initial_quants.json`**
Скопировать из текущего `data/initial_quants.json` (он уже для исекая)

**3. `data/worlds/isekai/initial_summary.md`**
Скопировать из текущего `data/initial_summary.md`

**5. `data/worlds/isekai/quantizer_instructions.md`**
Специфичные инструкции для Quantizer в мире isekai:
```markdown
# Quantizer Instructions: Isekai World

## Key concepts for this world
- **Magic System**: Magic works through mana (internal energy). Track mana reserves.
- **Level System**: Heroes gain XP, level up, improve stats (HP, MP, STR, AGI, INT, VIT).
- **Adventurer Guild**: Main quest hub. Track adventurer rank (F, E, D, C, B, A, S).
- **Multiple Races**: Humans, elves, dwarves, beastfolk, demons. Each has unique traits.

## Typical quants to create
- **NPCs**: Include race, class, level, personality, motivations
- **Locations**: Towns, dungeons, guild halls, shops, inns
- **Quest Items**: Magical artifacts, weapons, armor with enchantments
- **Monsters**: Type, habitat, threat level, drops
- **Abilities**: Player's unique skills from previous world or gained in isekai

## World-specific rules
- Always track character level and experience
- Manage guild rank progression
- Handle magic schools and spell learning
- Create meaningful connections between characters
- Remember previous world knowledge (if player uses it)

## Examples of good quants
- NPC: "Мастер_Гильдии_Рейнард" (Receptionist, knows all adventurers, helpful)
- Location: "Таверна_Золотой_Дракон" (Popular spot, quest board, rumors)
- Item: "Меч_Призывателя" (Legendary weapon, +5 STR, summons spectral blade)
- Monster: "Лесной_Тролль" (Mid-level threat, forest habitat, drops troll hide)
```

**6. Пустые файлы для других языков:**
Создать ПУСТЫЕ файлы:
- `data/worlds/isekai/initial_quants_en.json` (TODO: Translation needed)
- `data/worlds/isekai/initial_summary_en.md` (TODO: Translation needed)
- `data/worlds/isekai/quantizer_instructions_en.md` (TODO: Translation needed)

---

### 6.2 Создать заглушки для других миров
**Для каждого мира:** cyberpunk, steampunk, magic_academy, slavic, fallout

**Создать структуру файлов:**

**1. config.json с базовой информацией**

**Cyberpunk:**
```json
{
  "id": "cyberpunk",
  "name": {
    "ru": "Киберпанк",
    "en": "Cyberpunk"
  },
  "description": {
    "ru": "Мрачное будущее с высокими технологиями и низким уровнем жизни. Мегакорпорации, киберпротезы, нейронные интерфейсы.",
    "en": "Dark future with high tech and low life. Megacorporations, cyberware, neural interfaces."
  },
  "icon": "🤖",
  "enabled": false,
  "has_content": false
}
```

**Steampunk:**
```json
{
  "id": "steampunk",
  "name": {
    "ru": "Стимпанк",
    "en": "Steampunk"
  },
  "description": {
    "ru": "Эпоха пара и механизмов. Воздушные корабли, паровые машины, викторианская эстетика.",
    "en": "Age of steam and mechanisms. Airships, steam engines, Victorian aesthetics."
  },
  "icon": "🎩",
  "enabled": false,
  "has_content": false
}
```

**Magic Academy:**
```json
{
  "id": "magic_academy",
  "name": {
    "ru": "Магическая Академия",
    "en": "Magic Academy"
  },
  "description": {
    "ru": "Престижная школа магии. Обучение заклинаниям, магические турниры, тайны академии.",
    "en": "Prestigious magic school. Spell learning, magical tournaments, academy secrets."
  },
  "icon": "🏫",
  "enabled": false,
  "has_content": false
}
```

**Slavic:**
```json
{
  "id": "slavic",
  "name": {
    "ru": "Славянское Фэнтези",
    "en": "Slavic Fantasy"
  },
  "description": {
    "ru": "Мир, пропитанный славянской мифологией. Волхвы, лесные духи, древние боги, богатыри.",
    "en": "World steeped in Slavic mythology. Sorcerers, forest spirits, ancient gods, bogatyrs."
  },
  "icon": "🐻",
  "enabled": false,
  "has_content": false
}
```

**Fallout:**
```json
{
  "id": "fallout",
  "name": {
    "ru": "Пустошь",
    "en": "Wasteland"
  },
  "description": {
    "ru": "Постапокалиптический мир после ядерной войны. Радиация, мутанты, борьба за выживание.",
    "en": "Post-apocalyptic world after nuclear war. Radiation, mutants, struggle for survival."
  },
  "icon": "☢️",
  "enabled": false,
  "has_content": false
}
```

**2. Для каждого мира создать ПУСТЫЕ файлы с TODO:**

- `initial_quants.json` → `[]` (пустой массив + комментарий "TODO: Fill with initial quants")
- `initial_summary.md` → `# TODO: World description needed`
- `quantizer_instructions.md` → `# TODO: Quantizer instructions for this world`

---

## Этап 7: Тестирование

### 7.1 Ручное тестирование
**Тест-кейсы:**

1. **Новый пользователь:**
   - /start → выбор языка
   - Выбрать русский → главное меню
   - Новая игра → выбор мира
   - Выбрать Исекай → описание
   - Начать игру → создание персонажа

2. **Сохранение:**
   - Играть несколько ходов
   - Главное меню → Сохранить
   - Выбрать слот 1 → подтверждение

3. **Загрузка:**
   - Главное меню → Загрузить
   - Выбрать слот 1 → игра продолжается

4. **Множественные сохранения:**
   - Начать новую игру в другом слоте
   - Проверить что старая не затерта
   - Переключаться между слотами

5. **Существующий пользователь:**
   - /start → сразу главное меню (не выбор языка)

---

## Детальный чеклист по файлам

### Создать новые файлы:

**Локализация:**
- [ ] `core/localization/__init__.py`
- [ ] `core/localization/base.py`
- [ ] `core/localization/ru.py`
- [ ] `core/localization/en.py` (пустой заглушка)

**Менеджеры:**
- [ ] `core/managers/world_manager.py`
- [ ] `core/utils/prompt_templates.py` (для Jinja2 шаблонов)

**Telegram бот:**
- [ ] `telegram/states.py`
- [ ] `telegram/handlers/__init__.py`
- [ ] `telegram/handlers/menu.py`
- [ ] `telegram/handlers/saves.py`
- [ ] `telegram/keyboards/__init__.py`
- [ ] `telegram/keyboards/inline.py`

**Мир: Isekai (полностью заполненный):**
- [ ] `data/worlds/isekai/config.json`
- [ ] `data/worlds/isekai/initial_quants.json`
- [ ] `data/worlds/isekai/initial_summary.md`
- [ ] `data/worlds/isekai/quantizer_instructions.md`

**Мир: Cyberpunk (заглушки):**
- [ ] `data/worlds/cyberpunk/config.json`
- [ ] `data/worlds/cyberpunk/initial_quants.json` (пустой)
- [ ] `data/worlds/cyberpunk/initial_summary.md` (пустой)
- [ ] `data/worlds/cyberpunk/quantizer_instructions.md` (пустой)

**Мир: Steampunk (заглушки):**
- [ ] `data/worlds/steampunk/config.json`
- [ ] `data/worlds/steampunk/initial_quants.json` (пустой)
- [ ] `data/worlds/steampunk/initial_summary.md` (пустой)
- [ ] `data/worlds/steampunk/quantizer_instructions.md` (пустой)

**Мир: Magic Academy (заглушки):**
- [ ] `data/worlds/magic_academy/config.json`
- [ ] `data/worlds/magic_academy/initial_quants.json` (пустой)
- [ ] `data/worlds/magic_academy/initial_summary.md` (пустой)
- [ ] `data/worlds/magic_academy/quantizer_instructions.md` (пустой)

**Мир: Slavic (заглушки):**
- [ ] `data/worlds/slavic/config.json`
- [ ] `data/worlds/slavic/initial_quants.json` (пустой)
- [ ] `data/worlds/slavic/initial_summary.md` (пустой)
- [ ] `data/worlds/slavic/quantizer_instructions.md` (пустой)

**Мир: Fallout (заглушки):**
- [ ] `data/worlds/fallout/config.json`
- [ ] `data/worlds/fallout/initial_quants.json` (пустой)
- [ ] `data/worlds/fallout/initial_summary.md` (пустой)
- [ ] `data/worlds/fallout/quantizer_instructions.md` (пустой)

### Изменить существующие файлы:
- [ ] `core/config.py` - добавить настройки локализации, миров, шаблонов
- [ ] `core/database/models.py` - расширить User и Session
- [ ] `core/database/db_manager.py` - добавить методы для сохранений
- [ ] `core/api/routes.py` - добавить endpoints для миров и сохранений
- [ ] `core/agents/quantizer_agent.py` - добавить загрузку world-specific инструкций
- [ ] `core/orchestrator.py` - учитывать world_id при создании сессии
- [ ] `telegram/bot.py` - переработать с FSM и меню
- [ ] `requirements.txt` - добавить jinja2 для шаблонов

### Переместить/удалить:
- [ ] `data/initial_quants.json` → `data/worlds/isekai/initial_quants.json`
- [ ] `data/initial_summary.md` → `data/worlds/isekai/initial_summary.md`
- [ ] Удалить старые `data/initial_quants_ru.json` и `initial_summary_ru.md` после переноса

### Пересоздать БД:
- [ ] Удалить старую `data/plexmem.db`
- [ ] Создать новую с обновленными моделями

---

## Приоритеты

### Критически важно (MVP):
1. ✅ Структура миров (`data/worlds/`)
2. ✅ WorldManager для загрузки миров
3. ✅ FSM-состояния в боте
4. ✅ Главное меню и выбор мира
5. ✅ Создание игры в выбранном мире
6. ✅ Система сохранений (слоты)

### Важно (Phase 2):
7. ✅ Локализация (пока только русский)
8. ✅ Полное меню настроек
9. ✅ Улучшенные клавиатуры

### Можно позже:
10. Другие языки интерфейса
11. Контент для других миров
12. Расширенные настройки (цензура, сложность)

---

## Особенности реализации

### Важные моменты:

1. **Не дублировать промпты**
   - Базовый промпт ГМ в `prompts/gm_system_ru.md`
   - Специфика мира в `data/worlds/{world}/gm_system_ru.md`
   - При запросе склеивать: базовый + специфика мира

2. **Кэширование миров**
   - WorldManager должен кэшировать загруженные config.json
   - Перечитывать только при изменении файла

3. **Обратная совместимость**
   - Если world_id не указан - использовать default_world="isekai"
   - Старые сессии без world_id считаются "isekai"

4. **FSM хранение**
   - Использовать MemoryStorage (достаточно для начала)
   - Позже можно мигрировать на Redis если нужно

5. **Языковые файлы пустые**
   - Создать структуру, но оставить пустыми (TODO)
   - Пользователь заполнит сам переводами

---

## Миграция данных

### Существующие пользователи:
- Автоматически назначить `language="ru"` и `world="isekai"`
- Существующие сессии привязать к `world_id="isekai"`

### SQL миграция:
```sql
-- Добавить колонки
ALTER TABLE users ADD COLUMN language TEXT DEFAULT 'ru';
ALTER TABLE sessions ADD COLUMN world_id TEXT DEFAULT 'isekai';
ALTER TABLE sessions ADD COLUMN slot_number INTEGER;
ALTER TABLE sessions ADD COLUMN is_saved BOOLEAN DEFAULT FALSE;
ALTER TABLE sessions ADD COLUMN saved_at TIMESTAMP;

-- Обновить существующие записи
UPDATE users SET language = 'ru' WHERE language IS NULL;
UPDATE sessions SET world_id = 'isekai' WHERE world_id IS NULL;
```

---

## Итоговая структура проекта (после миграции)

```
plexmem/
├── core/
│   ├── localization/          # Новое
│   │   ├── base.py
│   │   ├── ru.py
│   │   └── en.py (пустой)
│   ├── managers/
│   │   ├── memory_manager.py
│   │   ├── context_manager.py
│   │   └── world_manager.py   # Новое
│   ├── database/
│   │   ├── models.py          # Расширено
│   │   └── db_manager.py      # Расширено
│   └── api/
│       └── routes.py          # Расширено
├── telegram/
│   ├── bot.py                 # Переработано
│   ├── states.py              # Новое
│   ├── handlers/              # Новое
│   │   ├── menu.py
│   │   ├── game.py
│   │   └── saves.py
│   └── keyboards/             # Новое
│       └── inline.py
├── data/
│   └── worlds/                # Новое
│       ├── isekai/
│       │   ├── config.json
│       │   ├── initial_quants.json
│       │   ├── initial_summary.md
│       │   ├── gm_system_ru.md
│       │   └── gm_system_en.md (пустой)
│       ├── cyberpunk/
│       │   └── config.json
│       └── ... (другие миры)
└── prompts/
    ├── gm_system_ru.md        # Базовый промпт (общий)
    ├── quantizer_system_ru.md
    └── summarizer_*.md
```

---

## Оценка времени

**MVP (основной функционал):**
- Этап 1: Структура проекта - 1-2 часа
- Этап 2: Расширение БД - 1 час
- Этап 3: WorldManager - 2 часа
- Этап 4: Переработка бота - 4-5 часов
- Этап 5: API интеграция - 2 часа
- Этап 6: Контент для isekai - 1 час
- Этап 7: Тестирование - 2 часа

**Итого: ~13-15 часов работы**

---

## Референсы для реализации

### Обязательно изучить:
1. `old_archive_version/.../handlers/menu_handlers.py` - логика меню, FSM, callbacks
2. `old_archive_version/.../localization/ru.py` - все тексты интерфейса
3. `old_archive_version/.../prompts/worlds/old/isekai.json` - структура мира исекай
4. `old_archive_version/.../database.py` - методы работы с сохранениями, слотами

### Использовать как есть (не менять):
- `core/agents/` - агенты работают отлично
- `core/managers/memory_manager.py` - квантовая память работает
- `core/orchestrator.py` - оркестратор работает (минимальные изменения)
- `core/mechanics/` - игровая механика отличная

---

## Что НЕ делать

❌ **Не создавать:**
- Контент для других миров (кроме isekai)
- Переводы интерфейса (кроме русского)
- Промпты для других миров
- Описания персонажей для других миров

✅ **Создавать:**
- Только структуру (папки, config.json)
- Заглушки с минимальной информацией
- Комментарии "TODO: User will fill"

---

## Следующие шаги после завершения

1. Пользователь самостоятельно заполнит:
   - Переводы на другие языки
   - Контент для других миров
   - Промпты и стартовые кванты

2. Возможные улучшения:
   - Редактор миров в админ-панели
   - Импорт/экспорт миров
   - Шаринг миров между пользователями
   - Пользовательские миры

---

## Готово к реализации!

Этот план описывает все аспекты миграции. Можно начинать поэтапно, начиная с Этапа 1.

