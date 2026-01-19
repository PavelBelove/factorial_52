# 🐛 BUGFIX: Telegram Long Messages + httpx Exception

**Дата:** 2026-01-19 23:20  
**Статус:** ✅ Исправлено

---

## Проблемы:

### 1. Message too long (4098 > 4096)
```
TelegramBadRequest: message is too long
Sending to Telegram: 4098 chars
```

**Причина:** ГМ написал 4098 символов, Telegram лимит - 4096

### 2. Wrong httpx exception
```
AttributeError: module 'httpx' has no attribute 'TimeoutError'
```

**Причина:** Использовали `httpx.TimeoutError`, но правильно `httpx.TimeoutException`

---

## Решения:

### 1. ✅ Split Long Messages

**Файл:** `telegram/bot.py`

**Логика:**
```python
if len(reply) > 4000:
    # Split into chunks of 3900 chars (safety margin)
    chunks = []
    for i in range(0, len(content), chunk_size):
        chunk = content[i:i + chunk_size]
        if i == 0:
            chunks.append(header + chunk)  # Header only in first
        else:
            chunks.append(chunk)
    
    # Send chunks with 0.5s delay
    for idx, chunk in enumerate(chunks):
        await message.answer(chunk, parse_mode=None)
        if idx < len(chunks) - 1:
            await asyncio.sleep(0.5)
else:
    # Send normally
    await message.answer(reply, parse_mode=None)
```

**Зачем 3900 а не 4096:**
- Оставить запас для header (`🎲 Ход #N\n\n`)
- Безопасность от граничных случаев
- Unicode characters могут занимать больше байтов

### 2. ✅ Fix httpx Exception

**Было:**
```python
except httpx.TimeoutError:
```

**Стало:**
```python
except httpx.TimeoutException:
```

---

## ✅ Результат:

- Бот может обрабатывать длинные ответы ГМ (3000+ символов)
- Сообщения разбиваются на части автоматически
- Timeout exceptions обрабатываются корректно
- Система работает стабильно

---

## 🎮 Теперь можно играть!

ГМ может писать детальные ответы любой длины - бот автоматически разобьёт их на части.

