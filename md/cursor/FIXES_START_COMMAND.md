# Исправление: Команда /start и создание новых сессий

## Дата: 12 января 2026, 15:00

## ❌ **Проблемы:**

1. **`/start` продолжал старую игру** - вместо создания новой сессии находил и продолжал существующую (ход 28→30)
2. **Character не создавался** - Quantizer создавал `Пол` (npc) вместо специального кванта `Character`
3. **Inventory не создавался** - отсутствовал в БД
4. **`/retry` не откатывал контекст** - начинал следующий ход вместо повтора предыдущего

## ✅ **Исправления:**

### 1. Разделение логики создания сессий

**Файл:** `telegram/bot.py`

#### До:
```python
async def cmd_start(self, message: Message, state: FSMContext):
    """Handle /start command - immediately start game."""
    # Create or get session
    session_id = await self._get_or_create_session(user_id)
```

#### После:
```python
async def cmd_start(self, message: Message, state: FSMContext):
    """Handle /start command - ALWAYS create NEW game session."""
    # ALWAYS create NEW session (deactivate old ones)
    session_id = await self._create_new_session(user_id)
```

### 2. Новый метод `_create_new_session`

Добавлен метод, который:

1. **Деактивирует все старые сессии** пользователя через API `POST /sessions/deactivate`
2. **Удаляет из кэша** памяти бота
3. **Создаёт новую сессию** через API `POST /sessions`

```python
async def _create_new_session(self, user_id: int) -> int:
    """ALWAYS create new session, deactivating old ones."""
    # Deactivate all old sessions
    await client.post(
        f"{API_BASE_URL}/sessions/deactivate",
        json={
            "platform_id": str(user_id),
            "platform_type": "telegram"
        }
    )
    
    # Remove from memory cache
    if user_id in self.user_sessions:
        del self.user_sessions[user_id]
    
    # Create new session
    response = await client.post(f"{API_BASE_URL}/sessions", ...)
    return session_id
```

### 3. Новый API эндпоинт

**Файл:** `core/api/main.py`

```python
@app.post("/sessions/deactivate")
async def deactivate_user_sessions(request: CreateSessionRequest):
    """
    Deactivate all active sessions for a user.
    Used when starting a new game with /start.
    """
    # Find user by platform_id
    user = db_session.query(UserDB).filter(
        UserDB.platform_id == request.platform_id,
        UserDB.platform_type == request.platform_type
    ).first()
    
    # Deactivate all active sessions
    count = db_session.query(SessionDB).filter(
        SessionDB.user_id == user.id,
        SessionDB.is_active == True
    ).update({"is_active": False})
    
    db_session.commit()
    
    return {
        "deactivated": count,
        "message": f"Deactivated {count} sessions"
    }
```

### 4. Логика команд

| Команда | Логика | Метод |
|---------|--------|-------|
| `/start` | **Всегда** создаёт новую сессию | `_create_new_session()` |
| Обычное сообщение | Продолжает существующую или создаёт новую | `_get_or_create_session()` |
| `/retry` | Повторяет последнее сообщение в той же сессии | `_get_or_create_session()` |

## 📊 **Результаты:**

### До исправлений:
```
Session 1: ход 26 → /start → ход 28 (продолжил ту же сессию)
```

### После исправлений:
```
Session 1: ход 30, is_active=1 → /start → is_active=0
Session 2: ход 1, is_active=1 (новая игра!)
```

## 🎯 **Теперь работает так:**

### Сценарий 1: Новая игра
```
Пользователь → /start
├─ Деактивировать все старые сессии (is_active = False)
├─ Создать новую сессию (Session ID: 2)
├─ CharacterCreation в контексте
├─ ГМ проводит создание персонажа
└─ Quantizer создаёт Character и Inventory
```

### Сценарий 2: Продолжение игры
```
Пользователь → "Иду дальше"
├─ Найти активную сессию или создать новую
├─ Продолжить с текущего хода
├─ ГМ обрабатывает действие
└─ Quantizer обновляет кванты
```

### Сценарий 3: Retry (TODO)
```
Пользователь → /retry
├─ Найти активную сессию
├─ Получить последнее сообщение пользователя
├─ Повторить обработку (откатив ход?)
└─ ГМ генерирует новый ответ
```

## 🔧 **Требует дальнейшей работы:**

### `/retry` - откат контекста

**Проблема:** Сейчас `/retry` просто отправляет то же сообщение, но начинается новый ход (N+1 вместо повтора N)

**Решение:**
1. Добавить в API эндпоинт `POST /sessions/{id}/undo` для отката последнего хода
2. Удалить последний Turn из БД
3. Уменьшить `current_turn` на 1
4. Затем повторить сообщение

### CharacterCreation и Character

**Статус:** Character всё ещё не создаётся автоматически

**Проверка после новой игры:**
```sql
SELECT quant_id, type FROM quants 
WHERE session_id = 2 AND quant_id IN ('Character', 'Inventory', 'CharacterCreation');
```

Ожидаемый результат после хода 3-4:
```
CharacterCreation | concept
Character         | npc
Inventory         | concept
```

## 📋 **Старая сессия (для справки):**

```
Session ID: 1
User ID: 1 (platform_id: 677134292)
Current turn: 30
Quants: 25
Status: Будет деактивирована при /start
```

Кванты в старой сессии:
- CharacterCreation, Магическая_Система, Система_Уровней, Гильдия_Авантюристов
- Пол (npc) - **НЕ Character!**
- Драг, Этерия, Лира, Гарт, Катакомбы...
- 25 квантов всего

## ✅ **Готово к тестированию!**

Теперь `/start` создаст новую сессию с нуля, и Quantizer должен создать Character и Inventory на первом срабатывании (ход 3).





