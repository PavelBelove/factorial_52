# План реализации Streaming для PlexMem RPG Bot

## 📋 Обзор проблемы

**Текущая ситуация:**
- Пользователь отправляет действие
- Видит "🎲 Ход обрабатывается..." 10-20+ секунд
- Получает полный ответ ГМ сразу

**Желаемая ситуация:**
- Пользователь отправляет действие
- Видит "🎲 Ход обрабатывается..." ~2-5 секунд (пока модель начнет генерировать)
- Текст появляется постепенно, обновляясь батчами (эффект "печатания")
- Более живой и отзывчивый UX

---

## 🔍 Технические возможности

### 1. Поддержка Streaming в моделях

**OpenRouter API:**
- ✅ **Поддерживает SSE (Server-Sent Events) streaming**
- Включается параметром `"stream": true`
- Возвращает delta chunks в формате:
```
data: {"id":"...","choices":[{"delta":{"content":"текст"}}]}
```

**Используемые модели:**
- ✅ `deepseek/deepseek-v3.2` (GM) - поддерживает streaming
- ✅ `x-ai/grok-2-1212` (Quantizer, Summarizer) - поддерживает streaming
- ✅ `x-ai/grok-4.1-fast` (Translator) - поддерживает streaming

**Вывод:** Все модели поддерживают streaming! ✅

---

### 2. Лимиты Telegram Bot API

**editMessageText:**
- **Rate limit:** ~30 запросов/сек для одного чата
- **Safe limit:** 1 запрос каждые **2-3 секунды** (безопасно)
- **Минимальный интервал:** 1 секунда
- **Рекомендация:** 2-3 секунды между обновлениями

**Ограничения:**
- Максимум 4096 символов на сообщение (уже учтено в коде)
- Нельзя редактировать сообщения старше 48 часов (не актуально)
- Одинаковый текст игнорируется (API не обновит если текст идентичен)

**Вывод:** Можно безопасно обновлять каждые **2-3 секунды** ✅

---

## 🏗️ Архитектура решения

### Проблема: Парсинг JSON "на лету"

GM отвечает в формате JSON:
```json
{
  "reply": "Большой текст нарратива...",
  "mechanics": {...},
  "quant_commands": [...]
}
```

**Задача:**
1. Парсить поле `"reply"` по мере поступления токенов
2. Отправлять только текст нарратива пользователю
3. Завершить обработку когда JSON полностью получен

**Подход:**
- Начинаем читать stream после `"reply": "`
- Копим текст, следя за экранированием (`\"` vs `"}`)
- Обрезаем по последнему пробелу/переносу (не рвём слова)
- Обновляем Telegram сообщение каждые N секунд
- Когда видим `"}` (неэкранированную) - конец нарратива
- Дожидаемся полного JSON для mechanics и quant_commands

---

## 📝 Детальный план реализации

### Фаза 1: Инфраструктура streaming

#### 1.1. Создать `StreamingGMClient` в `core/llm_client.py`

```python
class StreamingGMClient:
    """Handles streaming responses from GM agent"""
    
    async def stream_completion(
        self,
        messages: List[dict],
        model: str,
        on_narrative_chunk: Callable[[str], Awaitable[None]]
    ) -> dict:
        """
        Stream GM response, calling callback for narrative updates
        
        Args:
            messages: Chat history
            model: Model name
            on_narrative_chunk: Async callback(full_text_so_far)
        
        Returns:
            Complete GM response dict
        """
```

**Логика:**
1. Открыть streaming connection к OpenRouter
2. Парсить SSE chunks
3. Искать начало `"reply": "`
4. Копить narrative text, вызывая callback
5. Детектировать конец reply (unescaped `"}`)
6. Продолжать получать остальной JSON
7. Вернуть полный ответ

#### 1.2. Парсер для "неполного" JSON

```python
class PartialJSONParser:
    """Parse narrative from incomplete JSON stream"""
    
    STATE_SEARCHING = "searching"    # Looking for "reply":"
    STATE_IN_NARRATIVE = "narrative" # Reading narrative
    STATE_COMPLETE = "complete"      # Found end of narrative
    
    def feed_chunk(self, chunk: str) -> Optional[str]:
        """
        Feed a new chunk, returns narrative update if available
        
        Returns:
            New text to display (or None if no update)
        """
```

**Функции:**
- `_is_escaped(position)` - проверка экранирования
- `_find_narrative_start()` - найти `"reply": "`
- `_find_narrative_end()` - найти неэкранированную `"}`,
- `_clean_for_display()` - обрезать по последнему пробелу

---

### Фаза 2: Telegram streaming handler

#### 2.1. Создать `StreamingMessageUpdater` в `telegram/streaming.py`

```python
class StreamingMessageUpdater:
    """
    Updates Telegram message at safe intervals
    """
    
    def __init__(
        self,
        bot: Bot,
        chat_id: int,
        message_id: int,
        update_interval: float = 2.5  # seconds
    ):
        self.bot = bot
        self.chat_id = chat_id
        self.message_id = message_id
        self.update_interval = update_interval
        
        self.last_update_time = 0
        self.last_sent_text = ""
        self.pending_text = ""
        
        self._update_task: Optional[asyncio.Task] = None
    
    async def schedule_update(self, new_text: str):
        """Schedule text update (respects rate limits)"""
        self.pending_text = new_text
        
        # If enough time passed since last update, send now
        now = time.time()
        if now - self.last_update_time >= self.update_interval:
            await self._send_update()
    
    async def force_update(self):
        """Force immediate update (for final message)"""
        await self._send_update()
    
    async def _send_update(self):
        """Actually send the update to Telegram"""
        if self.pending_text == self.last_sent_text:
            return  # No changes
        
        try:
            await self.bot.edit_message_text(
                chat_id=self.chat_id,
                message_id=self.message_id,
                text=self.pending_text,
                parse_mode=None  # Plain text for stability
            )
            self.last_sent_text = self.pending_text
            self.last_update_time = time.time()
        except TelegramBadRequest as e:
            if "message is not modified" in str(e).lower():
                pass  # Ignore
            else:
                raise
```

---

### Фаза 3: Интеграция в Orchestrator

#### 3.1. Обновить `core/orchestrator.py`

**Текущий flow:**
```python
# Single call, wait for complete response
gm_response = await self.gm_agent.run(...)
# Show complete response
```

**Новый flow:**
```python
# 1. Create streaming updater
updater = StreamingMessageUpdater(
    bot=bot,
    chat_id=chat_id,
    message_id=loading_message_id,
    update_interval=2.5
)

# 2. Stream GM response
async def on_narrative_chunk(narrative: str):
    formatted = format_gm_response(narrative, mechanics=None)
    await updater.schedule_update(formatted)

gm_response = await self.gm_agent.stream_run(
    ...,
    on_narrative_chunk=on_narrative_chunk
)

# 3. Force final update with mechanics
final_text = format_gm_response(
    gm_response["reply"],
    gm_response.get("mechanics")
)
await updater.force_update(final_text)

# 4. Continue with Quantizer, etc.
```

---

### Фаза 4: Обработка ошибок

#### Сценарии сбоев:

**1. Модель вернула невалидный JSON:**
- Детектировать после timeout (30 сек без новых chunks)
- Показать последний валидный нарратив
- Логировать ошибку
- Попробовать re-parse полного ответа

**2. Telegram API rate limit:**
- Автоматически увеличить `update_interval`
- Показать финальный текст после завершения

**3. Connection drop во время streaming:**
- Fallback на обычный non-streaming запрос
- Показать результат как обычно

**4. Incomplete JSON (stream closed early):**
- Сохранить что успели получить
- Показать пользователю warning
- Предложить переиграть ход

---

## 🎯 План внедрения (пошагово)

### Этап 1: Прототип streaming (3-4 часа)
- [ ] Создать `PartialJSONParser` с юнит-тестами
- [ ] Создать `StreamingGMClient` в `llm_client.py`
- [ ] Добавить debug mode для тестирования
- [ ] Тест: вывод chunks в консоль

### Этап 2: Telegram integration (2-3 часа)
- [ ] Создать `StreamingMessageUpdater`
- [ ] Добавить в `core/orchestrator.py`
- [ ] Тест: обновление сообщения каждые 2.5 сек

### Этап 3: Интеграция с GM Agent (2 часа)
- [ ] Обновить `GMAgent` для поддержки streaming
- [ ] Сохранить совместимость (можно включать/выключать)
- [ ] Тест: полный цикл хода со streaming

### Этап 4: Error handling (1-2 часа)
- [ ] Обработать все edge cases
- [ ] Добавить fallback на non-streaming
- [ ] Логирование проблем

### Этап 5: Тестирование (2-3 часа)
- [ ] Тест с разными длинами ответов
- [ ] Тест с эмодзи, спецсимволами
- [ ] Тест с очень быстрой генерацией
- [ ] Тест с медленной генерацией
- [ ] Проверка rate limits

### Этап 6: Production (1 час)
- [ ] Добавить feature flag `enable_streaming: bool` в config
- [ ] Deploy на сервер
- [ ] Мониторинг first 100 ходов

**Общее время: ~12-15 часов разработки**

---

## ⚙️ Конфигурация

### Добавить в `core/config.py`:

```python
class Settings(BaseSettings):
    # ... existing settings ...
    
    # Streaming settings
    enable_streaming: bool = True
    streaming_update_interval: float = 2.5  # seconds
    streaming_min_chars_for_update: int = 100  # don't update for tiny chunks
    streaming_timeout: int = 30  # seconds
```

---

## 🧪 Тестовые сценарии

### 1. Короткий ответ (<200 символов)
**Ожидание:** Одно обновление или вообще без streaming

### 2. Средний ответ (500-1000 символов)
**Ожидание:** 2-4 обновления, плавное появление текста

### 3. Длинный ответ (2000+ символов)
**Ожидание:** 5-10 обновлений, но не превышение Telegram limits

### 4. Ответ с эмодзи и спецсимволами
**Ожидание:** Корректное экранирование, без артефактов

### 5. Модель молчит 10 секунд, потом отвечает
**Ожидание:** Loading spinner до начала генерации, потом streaming

### 6. JSON с экранированными кавычками в нарративе
**Пример:** `"reply": "Он сказал: \"Привет!\""`
**Ожидание:** Корректный парсинг, не останавливается на `\"`

---

## 📊 Метрики для мониторинга

После внедрения tracking:

1. **Среднее время до первого обновления**
   - Цель: <5 секунд
   
2. **Количество обновлений на ход**
   - Цель: 2-6 для средних ответов
   
3. **Частота Telegram API errors**
   - Цель: <1% ходов
   
4. **Процент fallback на non-streaming**
   - Цель: <5%

5. **User feedback** (опционально)
   - Кнопка "Слишком быстро/медленно" после хода

---

## 🚀 Преимущества

1. **Лучший UX:**
   - Пользователь видит что система работает
   - Может начать читать раньше
   - Ощущение живого диалога

2. **Perceived performance:**
   - 20 секунд со streaming ощущаются как 10-12
   - Уменьшает abandonment rate

3. **Отладка:**
   - Видно если модель "зависла"
   - Легче отследить некорректный output

---

## ⚠️ Риски и ограничения

### Потенциальные проблемы:

1. **Сложность парсинга:**
   - JSON может быть невалидным на любом этапе
   - Нужен robust parser с fallback

2. **Telegram rate limits:**
   - Нельзя слишком часто обновлять
   - Баланс между плавностью и limits

3. **Дополнительная сложность кода:**
   - Больше мест для багов
   - Нужно тщательное тестирование

4. **Не работает для Quantizer/Summarizer:**
   - Они не возвращают user-facing текст
   - Streaming только для GM

### Митигация:

- ✅ Feature flag для быстрого отключения
- ✅ Fallback на non-streaming при ошибках
- ✅ Comprehensive logging
- ✅ Graceful degradation

---

## 💡 Будущие улучшения

После успешного внедрения:

### 1. Typing indicator
Показывать "ГМ печатает..." пока нет первого chunk

### 2. Adaptive update interval
Замедлять при быстрой генерации, ускорять при медленной

### 3. Progress indicator
Показывать примерный прогресс (на основе средней длины ответов)

### 4. Streaming для длинных Quantizer logs
В debug mode показывать streaming создания квантов

### 5. User preference
Позволить пользователю выключить streaming: `/settings streaming off`

---

## 📚 Технические детали

### OpenRouter Streaming API

**Request:**
```python
response = await httpx.AsyncClient().stream(
    "POST",
    "https://openrouter.ai/api/v1/chat/completions",
    headers={
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    },
    json={
        "model": "deepseek/deepseek-v3.2",
        "messages": [...],
        "stream": True  # Enable streaming
    },
    timeout=60.0
)

async with response as stream:
    async for line in stream.aiter_lines():
        if line.startswith("data: "):
            data = line[6:]  # Remove "data: " prefix
            if data == "[DONE]":
                break
            chunk = json.loads(data)
            delta = chunk["choices"][0]["delta"].get("content", "")
            # Process delta...
```

### Telegram editMessageText

**Rate limiting strategy:**
```python
import time
from collections import deque

class TelegramRateLimiter:
    def __init__(self, max_per_second: int = 1):
        self.max_per_second = max_per_second
        self.timestamps = deque(maxlen=max_per_second)
    
    async def wait_if_needed(self):
        now = time.time()
        if len(self.timestamps) >= self.max_per_second:
            oldest = self.timestamps[0]
            wait_time = 1.0 - (now - oldest)
            if wait_time > 0:
                await asyncio.sleep(wait_time)
        self.timestamps.append(now)
```

---

## 🎬 Заключение

**Это значительное улучшение UX, которое стоит реализовать!**

**Плюсы:**
- ✅ Все модели поддерживают streaming
- ✅ Telegram API позволяет безопасные обновления
- ✅ Улучшит perceived performance на 30-50%
- ✅ Можно легко отключить если что-то пойдет не так

**Минусы:**
- ⚠️ Требует аккуратной реализации парсинга
- ⚠️ Усложняет error handling
- ⚠️ Дополнительно ~12-15 часов разработки

**Рекомендация:** Начать с прототипа (Этап 1-2), протестировать, и если всё работает стабильно - внедрять в production постепенно с feature flag.

---

**Создано:** 2026-02-03
**Статус:** 📋 Plan ready for implementation
**Ориентировочное время:** 12-15 часов

