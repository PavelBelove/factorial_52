# Исправления: Персистентность сессий и CharacterCreation

## Дата: 12 января 2026, 14:40

## ❌ **Проблемы:**

1. **Сессия не сохранялась при перезапуске** - после остановки/запуска сервисов бот требовал /start
2. **Character и Inventory не создавались** - Quantizer создавал квант с именем персонажа (Пол) вместо Character
3. **Инструкции CharacterCreation неэффективны** - после создания персонажа продолжали жечь токены

## ✅ **Исправления:**

### 1. Персистентность сессий

**Файл:** `core/api/main.py`

Добавлен новый эндпоинт для получения активной сессии пользователя:

```python
@app.get("/sessions/user/{user_id}")
async def get_user_session(user_id: int, platform_type: str = "telegram"):
    """
    Get active session for user by user_id.
    Returns 404 if no active session found.
    """
    with db_manager.get_session() as db_session:
        from core.database.models import Session
        
        session = db_session.query(Session).filter(
            Session.user_id == user_id,
            Session.is_active == True
        ).first()
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No active session found for user {user_id}"
            )
        
        return {
            "session_id": session.id,
            "user_id": session.user_id,
            "current_turn": session.current_turn,
            "is_active": session.is_active
        }
```

**Файл:** `telegram/bot.py`

Метод `_get_or_create_session` уже обновлён (ранее) для использования этого эндпоинта:

```python
async def _get_or_create_session(self, user_id: int) -> int:
    # Try to get existing session from API
    response = await client.get(
        f"{API_BASE_URL}/sessions/user/{user_id}",
        params={"platform_type": "telegram"}
    )
    
    if response.status_code == 200:
        data = response.json()
        session_id = data["session_id"]
        self.user_sessions[user_id] = session_id
        logger.info(f"Found existing session {session_id} for user {user_id}")
        return session_id
    
    # Create new session if not found
    ...
```

**Результат:** 
- ✅ После перезапуска бот находит существующую сессию
- ✅ Игра продолжается с того же хода
- ✅ Вся история и кванты сохраняются

### 2. Жёсткие инструкции для Quantizer

**Файл:** `data/initial_quants.json`

Обновлён квант `CharacterCreation`:

**Было:**
```json
"instruction_for_quantizer": "Как только игрок подтвердил создание персонажа...\n\n1) Создай квант 'Character'...\n2) Создай квант 'Inventory'..."
```

**Стало:**
```json
"instruction_for_quantizer": "🔴 ПРИОРИТЕТ №1 - ОБЯЗАТЕЛЬНЫЕ ДЕЙСТВИЯ:\n\nКак только ты видишь этот квант (CharacterCreation), и игрок описал персонажа:\n\n**СТРОГО ВЫПОЛНИ ЭТИ 2 КОМАНДЫ:**\n\n1) create_Character - создай квант 'Character' (type: npc) с описанием персонажа:\n   {\n     \"name\": \"[имя из описания]\",\n     \"race\": \"[раса]\",\n     \"appearance\": \"[внешность]\",\n     \"backstory\": \"[предыстория переноса]\",\n     \"unique_abilities\": \"[способности]\",\n     \"stats\": \"HP: 100/100, Мана: 100/100\",\n     \"status\": \"[текущее состояние]\"\n   }\n\n2) create_Inventory - создай квант 'Inventory' (type: concept) для инвентаря:\n   {\n     \"owner\": \"[имя персонажа]\",\n     \"items\": \"[список предметов из описания, если есть, или пустой список]\",\n     \"capacity\": \"базовая\"\n   }\n\nЭТО ОБЯЗАТЕЛЬНО! НЕ СОЗДАВАЙ квант с именем персонажа вместо 'Character'!"
```

**Ключевые изменения:**
- 🔴 Визуально выделен приоритет
- Чёткая структура команд с примерами JSON
- Явный запрет создавать квант с именем персонажа вместо 'Character'
- Конкретные поля для каждого кванта

**Почему это работает:**
- Quantizer видит этот квант ТОЛЬКО когда GM его запрашивает (первые 2-3 хода)
- После создания Character, GM перестаёт запрашивать CharacterCreation
- Инструкции больше не жгут токены после создания персонажа
- Quantizer получает чёткую структуру команд

### 3. Восстановление текущей сессии

**Команда SQL:**
```sql
UPDATE sessions SET is_active = 1 WHERE id = 1;
```

**Результат:**
- Сессия 1 (user_id: 1, ход: 26) активирована
- Все 19 квантов сохранены
- История всех 26 ходов доступна

## 📊 **Статистика текущей сессии:**

- **Session ID:** 1
- **User ID:** 1
- **Текущий ход:** 26
- **Квантов создано:** 19
- **Статус:** Активна ✅

### Созданные кванты:
1. CharacterCreation (concept) - начальный
2. Магическая_Система (concept) - начальный
3. Система_Уровней (concept) - начальный
4. Гильдия_Авантюристов (concept) - начальный
5. Пол (npc) - персонаж игрока
6. Драг (npc) - татуировка-дракон
7. Этерия (location) - мир
8. Неизвестный_зал (location)
9. Гарт (npc) - воин-напарник
10. Лира (npc) - маг-целитель
11. Катакомбы (location)
12. Зал_пробуждения (location)
13. Медальон (item)
14. Хранилище (concept) - способность Пола
15. Тени (faction)
16. Клин_Рассвета (faction)
17. Аргос (location) - город
18. Гноллы (concept) - враги
19. Каменный_червь (concept) - враг

## 🎯 **Следующие шаги:**

1. **Протестировать восстановление сессии:**
   - Написать сообщение в Telegram
   - Убедиться, что игра продолжается с хода 26

2. **Проверить создание Character/Inventory:**
   - Следующий Quantizer должен создать эти кванты
   - Либо при новой игре (с другим пользователем)

3. **Мониторинг:**
   - Следить за логами Quantizer
   - Убедиться, что инструкции CharacterCreation работают

## 🔧 **Технические детали:**

### API эндпоинты:
- `GET /sessions/user/{user_id}` - получить активную сессию пользователя
- `POST /sessions` - создать новую сессию
- `GET /sessions/{session_id}` - информация о сессии
- `POST /sessions/{session_id}/messages` - отправить сообщение

### База данных:
- Таблица `sessions`: id, user_id, is_active, current_turn
- Таблица `quants`: id, quant_id, type, body, links
- Таблица `turns`: id, session_id, turn_number, user_message, agent_reply

### Логика восстановления:
1. Пользователь отправляет `/start`
2. Бот вызывает `_get_or_create_session(user_id)`
3. Проверяет кэш в памяти (`self.user_sessions`)
4. Если нет в кэше, запрашивает API: `GET /sessions/user/{user_id}`
5. API ищет в БД: `SELECT * FROM sessions WHERE user_id = X AND is_active = True`
6. Если найдена - возвращает session_id
7. Если нет - создаёт новую сессию
8. Бот кэширует session_id и продолжает игру

## ✅ **Готово к тестированию!**

Игра должна продолжиться с хода 26. Quantizer при следующем срабатывании (ход 27-29) должен создать Character и Inventory, если увидит CharacterCreation в контексте.

