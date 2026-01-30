# Настройки пользователя в PlexMem

## Обзор

PlexMem поддерживает персонализированные настройки для каждого пользователя:
- **Язык интерфейса и игры**
- **Сложность игры** (пороги проверок)
- **Фильтр контента** (уровень взрослого контента)

Все настройки сохраняются в базе данных и применяются автоматически.

---

## 1. Сложность игры (Difficulty)

### Уровни сложности:
- **😊 Лёгкая (easy)** — пороги проверок снижены (100/140/180/220)
- **⚔️ Обычная (normal)** — стандартный баланс (100/150/200/250) ✅ *по умолчанию*
- **💀 Сложная (hard)** — пороги повышены (140/180/220/260)

### Как это работает:

1. **Настройка сохранена в БД**: `UserDB.difficulty`
2. **Извлекается в orchestrator**: `user_settings = self.db.get_user_settings(db_session.user_id)`
3. **Передается в механику карт**:
   ```python
   difficulty = user_settings.get("difficulty", "normal")
   thresholds = self.mechanics_manager.calculate_thresholds(session_id, difficulty)
   ```
4. **Применяется к проверкам**: базовые пороги изменяются согласно выбранной сложности

### Формула порогов:
```
Threshold = Base_Threshold + Average_Character_Stat
```

**Пример** (персонаж со средней характеристикой 50):
- **Лёгкая**: Easy=150, Normal=190, Hard=230, Very Hard=270
- **Обычная**: Easy=150, Normal=200, Hard=250, Very Hard=300
- **Сложная**: Easy=190, Normal=230, Hard=270, Very Hard=310

---

## 2. Фильтр контента (Content Filter)

### Уровни фильтрации:
- **🛡️ Безопасный (safe)** — без NSFW контента ✅ *по умолчанию*
- **💕 16+ (romantic)** — лёгкая романтика и эротика
- **🔞 18+ (adult)** — взрослый контент без ограничений (требует согласия)

### Как это работает:

1. **Настройка сохранена в БД**: `UserDB.content_filter`
2. **Извлекается в orchestrator**: `user_settings = self.db.get_user_settings(db_session.user_id)`
3. **Передается в контекст-менеджер**:
   ```python
   context_messages = self.context_manager.build_context(
       ...,
       user_settings=user_settings
   )
   ```
4. **Применяется к промптам ГМ**: используется Jinja2 для подстановки нужных инструкций

### Промпты с Jinja2-блоками:

Все промпты миров содержат условные блоки:

```jinja2
{% if content_filter == "safe" %}
**Content Guidelines**: Underage users may be present. Avoid NSFW content and explicit romance. 
Keep intimate moments tasteful and fade to black when needed, without breaking narrative flow.
{% elif content_filter == "romantic" %}
**Content Guidelines**: Romantic and light erotic content is permitted. Avoid explicit sexual 
descriptions and graphic intimate scenes. Suggest rather than describe.
{% elif content_filter == "adult" %}
**Content Guidelines**: User has given informed consent for NSFW content. Detailed erotic and 
sexual scenes are permitted when the narrative calls for them. Maintain literary quality.
{% endif %}
```

### Обновлённые миры:
- ✅ `magic_academy` — литературная магическая академия
- ✅ `fallout` — постапокалипсис
- ✅ `cyberpunk` — киберпанк noir
- ✅ `isekai` — фэнтези исекай
- ✅ `slavic` — славянская тёмная фэнтези
- ✅ `space` — космоопера
- ✅ `magic_academy_game` — игровая академия магии

---

## 3. Язык (Language)

### Поддерживаемые языки:
- 🇷🇺 Русский (ru) ✅ *по умолчанию*
- 🇬🇧 Английский (en)

### Как это работает:

1. **Настройка сохранена в БД**: `UserDB.language`
2. **Применяется к промптам**: `{{language}}` в Jinja2-шаблонах
3. **Влияет на интерфейс бота**: локализация меню и сообщений

---

## Изменение настроек

### Через меню бота:
1. `/menu` → **⚙️ Настройки**
2. Выбрать нужную настройку:
   - **🌐 Язык** → выбрать из списка
   - **🎮 Сложность** → выбрать уровень
   - **🔒 Фильтр контента** → выбрать уровень (18+ требует подтверждения)

### Через базу данных (для разработки):
```python
db.set_user_difficulty(user_id, "hard")
db.set_user_content_filter(user_id, "romantic")
db.set_user_language(user_id, "en")
```

---

## Архитектурная схема

```
Пользователь
    ↓ устанавливает настройки через меню
Database (UserDB)
    ├── difficulty: "normal"
    ├── content_filter: "safe"
    └── language: "ru"
    ↓
Orchestrator (process_turn)
    ├── user_settings = db.get_user_settings(user_id)
    ↓
    ├─→ MechanicsManager.calculate_thresholds(difficulty)
    │       └── применяет DIFFICULTY_PRESETS[difficulty]
    │
    └─→ ContextManager.build_context(user_settings)
            └─→ WorldManager.get_gm_system_prompt(content_filter, language)
                    └── рендерит Jinja2-шаблон с переменными
```

---

## Дефолтные значения

Если пользователь новый или настройки не заданы:
```python
{
    "language": "ru",
    "difficulty": "normal",
    "content_filter": "safe",
    "current_world": "isekai"
}
```

---

## Примечания для разработчиков

1. **Сложность работает автоматически** — не требует изменений в логике
2. **Фильтр контента через Jinja2** — добавлен во все 7 миров
3. **Язык влияет на промпты и UI** — локализация работает end-to-end
4. **Настройки персистентны** — хранятся в SQLite/PostgreSQL

---

## Тестирование

### Сложность:
1. Создать персонажа с разными сложностями
2. Сравнить пороги проверок в Game Mechanics блоке
3. Ожидаемые отличия: ±40-50 в порогах

### Фильтр контента:
1. Начать игру с разными фильтрами
2. Проверить первое сообщение ГМ на соответствие guidelines
3. Проверить логи: `Loaded GM prompt for {world_id} (lang=Russian, filter={content_filter})`

### Язык:
1. Переключить язык в настройках
2. Проверить UI бота на правильную локализацию
3. Проверить ответ ГМ на соответствие выбранному языку

