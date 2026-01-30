# Краткая сводка миграции

## Что изучено

### Старый проект (`old_archive_version/plexmem_bot-main/`)
✅ **Мультиязычность**: 
- Система локализации через абстрактные классы (base.py)
- 6 языков: ru, en, es, ar, pt, hi
- Методы для всех текстов интерфейса

✅ **Система миров**:
- JSON-конфиги для 7 миров (isekai, garmonia, cyberpunk, steampunk, magic_academy, slavic, rebirth)
- Каждый мир содержит: world, plot, available_characters, quanta
- Стартовые инструкции для GM и Summarizer

✅ **Меню и навигация**:
- FSM-состояния (aiogram)
- Inline-клавиатуры для выбора языка, мира, сохранения
- Система слотов (1-5) для сохранений
- Обработчики: новая игра, загрузка, сохранение, настройки

✅ **База данных**:
- Таблица games с world_id и slot
- Методы для работы с сохранениями
- Привязка пользователя к языку

### Текущий проект
✅ **Сильные стороны** (оставляем как есть):
- Квантовая память (MemoryManager)
- Предиктивная активация квантов
- Три агента (GM, Quantizer, Summarizer)
- Игровая механика (карты, характеристики, инвентарь)
- API-based архитектура

## Что будем делать

### 1. Система локализации
```
core/localization/
├── base.py     # Абстрактный класс
├── ru.py       # Полная реализация
└── en.py       # Пустая заглушка
```

### 2. Структура миров
```
data/worlds/
├── isekai/              # ЕДИНСТВЕННЫЙ заполненный
│   ├── config.json
│   ├── initial_quants.json
│   ├── initial_summary.md
│   └── gm_system_ru.md
├── cyberpunk/           # Остальные - только config.json
├── steampunk/
├── magic_academy/
├── slavic/
├── rebirth/
└── garmonia/
```

### 3. WorldManager
Новый менеджер для работы с мирами:
- Загрузка конфигов
- Получение списка доступных миров
- Загрузка начальных данных (quants, summary, prompt)

### 4. Telegram бот с меню
- FSM-состояния (выбор языка, главное меню, выбор мира, игра, сохранение, загрузка)
- Inline-клавиатуры
- Обработчики меню (menu.py, saves.py)

### 5. Расширение API
Новые endpoints:
- `/worlds` - список миров
- `/sessions` (расширен) - создание с world_id
- `/sessions/{id}/save` - сохранение в слот
- `/users/{id}/saves` - список сохранений

### 6. Расширение БД
```sql
-- User
+ language: str
+ current_world: str

-- Session
+ world_id: str
+ slot_number: int
+ is_saved: bool
+ saved_at: datetime
```

## Ключевые решения

✅ **Пока только русский язык** - остальные языки создаем пустыми  
✅ **Только мир "isekai" заполнен** - остальные только config.json  
✅ **Не трогаем ядро** - агенты и память работают отлично  
✅ **Обратная совместимость** - старые сессии автоматически = "isekai"  

## Файлы для изучения (референсы)

**Обязательно:**
1. `old_archive_version/.../handlers/menu_handlers.py` - вся логика меню
2. `old_archive_version/.../localization/ru.py` - все тексты
3. `old_archive_version/.../prompts/worlds/old/isekai.json` - структура мира
4. `old_archive_version/.../database.py` - работа с сохранениями

## Этапы (по порядку)

1. ✅ Структура локализации
2. ✅ Структура миров
3. ✅ WorldManager
4. ✅ Расширение БД
5. ✅ FSM и клавиатуры
6. ✅ Обработчики меню
7. ✅ API endpoints
8. ✅ Контент для isekai
9. ✅ Тестирование

**Оценка:** ~13-15 часов

## Готово к старту!

См. полный план в `MIGRATION_PLAN.md`

