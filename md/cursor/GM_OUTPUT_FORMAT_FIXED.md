# 🔧 Исправление формата вывода ГМ

**Дата:** 2026-01-19 12:43  
**Проблема:** ГМ возвращал пустые `quant_requests: []` и короткие ответы

---

## 📋 Проблемы

### 1. ❌ ГМ не запрашивал кванты
**Логи показывают:**
```
GM response generated. Requested quants: []
```

**Причина:** В промпте не было ТРЕБОВАНИЯ возвращать кванты, только рекомендация.

---

### 2. ❌ Ответ не парсился
**Бот получал:**
```python
{'narrative': '...', 'response_data': {...}, 'quant_requests': [...]}
```

Вместо форматированного текста.

---

### 3. ❌ ГМ не видел кванты в контексте
**Логи:**
```
Context built with 14 messages
```

Но не видно "Active quants" или "Synopsis".

---

## ✅ Решения

### 1. Добавлен раздел OUTPUT FORMAT

**Файл:** `prompts/gm_system_prolog.md`

```prolog
% CRITICAL: You MUST return JSON with specific structure
output_format :- json_object_only.

output_structure :-
{
  "narrative": "Your story response in Russian",
  "response_data": {...},
  "quant_requests": ["Quant1", "Quant2", ...]  // 5-10 items
}

% CRITICAL RULES:
output_rules :-
    always_return_json,
    always_include_quant_requests,
    quant_requests_must_not_be_empty,
    quant_requests_5_to_10_items,
    quant_names_without_markers.
```

---

### 2. Увеличено количество квантов

**Было:** 3-7 квантов  
**Стало:** 5-10 квантов  

```prolog
quant_request_requirement :-
    minimum(5),
    maximum(10),
    must_not_be_empty.
```

---

### 3. Добавлены примеры вывода

**Правильный пример:**
```json
{
  "narrative": "Ты входишь в =Таверна=. =Марта= машет тебе...",
  "response_data": {"gold": -5},
  "quant_requests": ["Марта", "Таверна_Атарикс", "Рендал", "Лира", "Квест_Лес"]
}
```

**Неправильные примеры:**
```json
// ❌ Wrong 1: Empty quants
{"narrative": "...", "quant_requests": []}

// ❌ Wrong 2: With markers
{"quant_requests": ["=Марта=", "=Таверна="]}

// ❌ Wrong 3: Plain text instead of JSON
"Ты входишь в таверну..."
```

---

## 🧪 Что проверить

После перезапуска проверь логи:

```bash
tail -f logs/plexmem_20260119.log | grep "Requested quants"
```

**Ожидаем:**
```
GM response generated. Requested quants: ['Лира', 'Академия', 'Квест', ...]
```

Не: `Requested quants: []`

---

## 🔍 Отладка контекста

Нужно также проверить что ГМ получает кванты. Добавь логирование:

```python
# В context_manager.py, метод build_context
logger.info(f"Active quants in context: {[q.quant_id for q in active_quants]}")
```

Это покажет какие кванты попадают в контекст ГМ.

---

## 📊 Ожидаемый результат

### До:
```
Requested quants: []
Ответ: {'narrative': '...', ...}  (сырой JSON в боте)
```

### После:
```
Requested quants: ['Лира', 'Академия_Рендала', 'Квест_Лес', ...]  (5-10 items)
Ответ: (форматированный текст в Telegram)
```

---

**Статус:** ✅ Исправлено, требуется тестирование

