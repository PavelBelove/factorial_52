# ✅ ПЕРВОЕ ИСПРАВЛЕНИЕ ПРИМЕНЕНО

**Дата:** 2026-01-19 13:50  
**Статус:** 🟢 Система работает, первый фикс активен

---

## ✅ Что исправлено:

### 1. Мапинг полей JSON (CRITICAL)

**Файл:** `core/agents/gm_agent.py` → `_validate_gm_response()`

**До:**
```python
# ГМ возвращает: {narrative, quant_requests, response_data}
# Система ожидает: {reply, quants, response_data}
# Результат: reply = str(entire_json) → JSON в Telegram ❌
```

**После:**
```python
# Автоматический мапинг:
if "narrative" in data and "reply" not in data:
    data["reply"] = data.pop("narrative")  

if "quant_requests" in data and "quants" not in data:
    data["quants"] = data.pop("quant_requests")

# Результат: reply = "Твои слова..." → Текст в Telegram ✅
```

---

### 2. Очистка маркеров =

**До:**
```python
# Очистка применялась к data["quants"]
# Но поле называлось data["quant_requests"]!
# Результат: маркеры не удалялись ❌
```

**После:**
```python
# 1. Сначала маппинг quant_requests → quants
# 2. Потом очистка маркеров из data["quants"]
# Результат: ['=Лира='] → ['Лира'] ✅
```

---

## 🧪 Что нужно протестировать:

### Тест 1: Парсинг ответа
**Ожидаемое:** Telegram показывает текст narrative, НЕ JSON

**Проверка:**
```
Напиши в бота → проверь ответ
```

---

### Тест 2: Очистка маркеров
**Ожидаемое:** В БД сохранятся чистые имена

**Проверка логов:**
```bash
grep "✅ Cleaned quants" logs/plexmem_20260119.log | tail -5
```

Должно быть:
```
✅ Cleaned quants (5): ['Лира', 'Академия_Рендала', ...]
```

НЕ:
```
['=Лира=', '=Академия_Рендала=', ...]
```

---

## ⚠️ Оставшиеся проблемы:

### Проблема 1: Active quants пустые

**Почему:**
- В БД старые ходы с маркерами: `['=Лира=', '=Элина=']`
- `get_quants_by_names(['=Лира='])` → не находит
- → active_quants = []
- → ГМ не видит полные кванты

**Решение:**
```python
# В orchestrator._get_active_quants()
requested_names = recent_turns[0].requested_quants
# Clean markers when loading
import re
requested_names = [re.sub(r'^=+|=+$', '', n) for n in requested_names]
```

---

### Проблема 2: ГМ запрашивает несуществующие кванты

**Пример:**
```json
"quant_requests": ["Элина", "Кири"]
// Но Элина и Кири только что представлены, их квантов нет!
```

**Почему:**
- ГМ не следует правилам промпта
- Должен запрашивать ТОЛЬКО существующие (из synopsis)

**Решение:**
- Возможно Prolog-промпт слишком сложный
- Рассмотреть откат на старый промпт
- Или добавить валидацию requested_quants

---

### Проблема 3: Синопсисы пустые

**Текущее:**
```
- **Лира**: [npc]
```

**Должно:**
```
- **Лира**: [npc] Магистр академии =Академия_Рендала= отец =Отец_Лиры=
```

**Проверка БД:**
```sql
SELECT quant_id, synopsis FROM quants LIMIT 10;
```

Если `synopsis = NULL` → Quantizer не заполняет.

---

## 📋 Следующие шаги:

### Шаг 1: Тестирование (Pavel)
Сделай 2-3 хода и проверь:
1. ✅ Ответ в Telegram - текст (не JSON)?
2. ✅ Логи: маркеры очищены?
3. ❌ ГМ видит полные кванты?

---

### Шаг 2: Если active_quants пустые
Применить фикс для очистки при загрузке:

```python
# core/orchestrator.py, метод _get_active_quants()
# После строки 228
requested_names = recent_turns[0].requested_quants
# ADD THIS:
import re
requested_names = [re.sub(r'^=+|=+$', '', n) for n in requested_names]
logger.info(f"Cleaned requested names: {requested_names}")
```

---

### Шаг 3: Проверить синопсисы
```bash
sqlite3 plexmem.db "SELECT quant_id, synopsis FROM quants WHERE session_id = 29 LIMIT 10;"
```

Если пусто → исправить Quantizer.

---

### Шаг 4: Сравнить промпты
```bash
git show master:prompts/gm_system.md > /tmp/master_gm.md
git show HEAD:prompts/gm_system.md > /tmp/current_gm.md
diff /tmp/master_gm.md /tmp/current_gm.md | head -100
```

Возможно старый промпт работал лучше.

---

## 🎯 Готово к тестированию!

**Система запущена:**
- ✅ API: http://localhost:8000 (healthy)
- ✅ Bot: работает

**Первый фикс активен:**
- ✅ Мапинг narrative → reply
- ✅ Очистка маркеров =

**Жду фидбека от Pavel!** 🚀

