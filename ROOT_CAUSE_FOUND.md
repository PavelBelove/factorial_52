# 🔴 КОРНЕВАЯ ПРИЧИНА НАЙДЕНА

**Дата:** 2026-01-19 13:30  
**Статус:** ✅ Проблема идентифицирована

---

## 🎯 Проблема: Несовпадение имен полей JSON

### Что ГМ возвращает (по новому Prolog-промпту):

```json
{
  "narrative": "Твои слова заставляют студенток...",
  "response_data": {"checks_used": []},
  "quant_requests": ["=Элина=", "=Кири=", "=Лира="]
}
```

### Что ожидает `_validate_gm_response()` в `gm_agent.py`:

```python
if "reply" not in data:  # ❌ Ищет "reply", а не "narrative"
if "quants" not in data:  # ❌ Ищет "quants", а не "quant_requests"
```

---

## ❌ Последствия:

### 1. Парсинг ломается:
```python
# _validate_gm_response() строка 210-212
if "reply" not in data:
    logger.warning("GM response missing 'reply' field")
    data["reply"] = str(data)  # ❌ Возвращает весь JSON как строку!
```

**Результат:** Telegram получает `str({'narrative': '...', ...})` вместо текста!

---

### 2. Маркеры = не удаляются:
```python
# _validate_gm_response() строка 221-231
for q in data["quants"]:  # ❌ Но поле называется "quant_requests"!
    cleaned = re.sub(r'^=+|=+$', '', str(q).strip())
```

**Результат:** Очистка НЕ применяется к `quant_requests`!

---

### 3. response_data теряется:
```python
# orchestrator.py строка 150
response_data = gm_response.get("response_data", {})
```

**Проблема:** `gm_response` после `_validate_gm_response()` содержит только `reply` и `quants`. Поле `response_data` теряется!

---

## ✅ Решение:

### Вариант 1: Изменить промпт ГМ (BAD)
- Вернуть поля `reply` и `quants`
- Но это ломает логику игровых механик

### Вариант 2: Исправить `_validate_gm_response()` (GOOD)

```python
def _validate_gm_response(self, data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate and normalize GM response."""
    if not isinstance(data, dict):
        raise ValueError("GM response must be a dict")
    
    # MAP fields: narrative -> reply, quant_requests -> quants
    if "narrative" in data and "reply" not in data:
        data["reply"] = data.pop("narrative")
    
    if "quant_requests" in data and "quants" not in data:
        data["quants"] = data.pop("quant_requests")
    
    # Ensure required fields
    if "reply" not in data:
        logger.warning("GM response missing 'reply' field")
        data["reply"] = str(data)
    
    if "quants" not in data:
        data["quants"] = []
    
    # Ensure quants is a list
    if not isinstance(data["quants"], list):
        data["quants"] = []
    
    # Clean markers from quants
    import re
    cleaned_quants = []
    for q in data["quants"]:
        if q and str(q).strip():
            # Remove = markers if present (e.g. "=Name=" → "Name")
            cleaned = re.sub(r'^=+|=+$', '', str(q).strip())
            if cleaned:
                cleaned_quants.append(cleaned)
    
    data["quants"] = cleaned_quants
    
    # Preserve response_data if present
    # (already in data, just pass through)
    
    return data
```

---

## 🔍 Другие проблемы (требуют отдельного анализа):

### 1. ГМ не получает полные кванты
- Проверить `_format_quants()` в `context_manager.py`
- Проверить что передается в `active_quants`

### 2. Синопсисы пустые
- Проверить БД: заполнено ли поле `synopsis`?
- Проверить `get_recent_quants_synopsis()`

### 3. Суммаризатор не работает
- Проверить логи: вызывается ли?
- Проверить trigger logic в `orchestrator.py`

---

## 📋 План действий:

1. ✅ Исправить `_validate_gm_response()` - маппинг полей
2. ⏳ Проверить `_format_quants()` - почему не показываются полные кванты
3. ⏳ Проверить БД - есть ли синопсисы
4. ⏳ Проверить суммаризатор
5. ⏳ Сравнить с master веткой

---

**Статус:** 🟡 Начинаем исправление

