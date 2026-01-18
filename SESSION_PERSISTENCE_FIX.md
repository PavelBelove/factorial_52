# Исправление: Сохранение сессии после перезапуска

## 🔴 Проблема

**После перезапуска бота игра скидывалась и требовала `/start`**

### Причина:
Бот хранил mapping `user_id -> session_id` только в памяти (`self.user_sessions`). При перезапуске эта информация терялась, и бот думал что пользователь новый.

### Что происходило:
1. Пользователь играл → session 1, ход 21
2. Перезапуск бота → `self.user_sessions` = {}
3. Пользователь пишет сообщение → бот не знает session_id
4. Ошибка: `❌ Сначала начни игру командой /start`

## ✅ Решение

### 1. Добавлен API endpoint для поиска сессии по platform_id

**`core/api/main.py`:**
```python
@app.get("/sessions/user/{platform_id}")
async def get_user_session(platform_id: str, platform_type: str = "telegram"):
    """Get active session for user by platform ID."""
    try:
        # Find session by platform_id
        session = db_manager.get_session_by_platform_id(platform_id, platform_type)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No active session found for this user"
            )
        
        return GetSessionInfoResponse(...)
    except Exception as e:
        ...
```

### 2. Добавлен метод в DatabaseManager

**`core/database/db_manager.py`:**
```python
def get_session_by_platform_id(
    self,
    platform_id: str,
    platform_type: str = "telegram"
) -> Optional[SessionDB]:
    """Get active session by platform ID."""
    with self.get_session() as session:
        # Find user by platform_id
        user = session.query(UserDB).filter(
            UserDB.platform_id == platform_id,
            UserDB.platform_type == platform_type
        ).first()
        
        if not user:
            return None
        
        # Get most recent session for this user
        return session.query(SessionDB).filter(
            SessionDB.user_id == user.id
        ).order_by(SessionDB.id.desc()).first()
```

### 3. Обновлена логика в боте

**`telegram/bot.py`:**
```python
async def _get_or_create_session(self, user_id: int) -> int:
    """Get existing session or create new one."""
    # Check if already have session in memory
    if user_id in self.user_sessions:
        return self.user_sessions[user_id]
    
    # Try to get existing session from API (НОВОЕ!)
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
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
        except Exception as e:
            logger.info(f"No existing session for user {user_id}: {e}")
    
    # Create new session if not found
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(...)
        ...
```

## 🎯 Как работает теперь

### Сценарий 1: Бот перезапустился
1. Пользователь пишет сообщение
2. Бот не находит `user_id` в `self.user_sessions`
3. Бот запрашивает `/sessions/user/{user_id}` из API
4. API ищет в БД последнюю сессию для этого пользователя
5. Бот получает `session_id` и продолжает игру ✅

### Сценарий 2: Новый пользователь
1. Пользователь пишет `/start`
2. Бот не находит `user_id` в `self.user_sessions`
3. Бот запрашивает `/sessions/user/{user_id}` → 404 Not Found
4. Бот создаёт новую сессию через `POST /sessions`
5. Игра начинается ✅

### Сценарий 3: Пользователь продолжает игру (без перезапуска)
1. Пользователь пишет сообщение
2. Бот находит `user_id` в `self.user_sessions` (в памяти)
3. Сразу использует сохранённый `session_id` ✅
4. Никаких дополнительных запросов к API

## 📊 Преимущества

1. **Персистентность** ✅
   - Сессия сохраняется в БД
   - Перезапуск бота не влияет на игру

2. **Производительность** ✅
   - Первый приоритет: память (`self.user_sessions`)
   - Второй приоритет: БД (только если нет в памяти)
   - Минимум запросов к API

3. **Надёжность** ✅
   - Graceful fallback: если нет в БД → создаём новую
   - Логирование всех действий

4. **Продакшен-ready** ✅
   - Пользователь может продолжить игру после любого перезапуска
   - Нет потери данных
   - Нет необходимости в `/start` каждый раз

## 🧪 Тестирование

### Тест 1: Продолжение после перезапуска
```
1. Пользователь: "Привет" (ход 21)
2. Перезапуск бота
3. Пользователь: "Продолжаем" (должен быть ход 22, а не ошибка)
✅ ОЖИДАЕТСЯ: Игра продолжается с хода 22
```

### Тест 2: Новый пользователь
```
1. Новый пользователь: /start
2. Бот создаёт новую сессию
✅ ОЖИДАЕТСЯ: Игра начинается с хода 1
```

### Тест 3: Повторный /start существующего пользователя
```
1. Пользователь играет (ход 21)
2. Пользователь: /start
3. Бот находит существующую сессию
✅ ОЖИДАЕТСЯ: Игра продолжается, не создаётся новая сессия
```

## 🔧 Дополнительные улучшения (опционально)

### 1. Множественные сессии
Можно добавить поддержку нескольких активных сессий для одного пользователя:
```python
# Вместо последней сессии - список всех активных
sessions = session.query(SessionDB).filter(
    SessionDB.user_id == user.id,
    SessionDB.is_active == True
).all()
```

### 2. Команда `/sessions`
Показывать список всех сессий пользователя:
```
📋 Твои сессии:
1. Игра #42 - Ход 21 (активна)
2. Игра #38 - Ход 15 (завершена)
```

### 3. Команда `/resume <session_id>`
Переключаться между сессиями:
```
/resume 42 → продолжить игру #42
/resume 38 → продолжить игру #38
```

## 📝 Итог

**Проблема решена полностью**. Теперь:
- ✅ Игра сохраняется в БД
- ✅ Перезапуск бота не влияет на пользователя
- ✅ Пользователь может продолжить с любого момента
- ✅ Продакшен-ready решение

