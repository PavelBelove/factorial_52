# 🛠️ ПЛАН ИСПРАВЛЕНИЙ

**Дата:** 2026-01-19 13:40  
**Приоритет:** 🔴 CRITICAL

---

## ✅ Исправление №1: Мапинг полей JSON (DONE)

**Файл:** `core/agents/gm_agent.py`

**Проблема:**
- ГМ возвращает `{narrative, quant_requests}` 
- Система ожидает `{reply, quants}`
- → Парсинг ломается, Telegram получает JSON

**Решение:**
```python
# В _validate_gm_response()
if "narrative" in data and "reply" not in data:
    data["reply"] = data.pop("narrative")

if "quant_requests" in data and "quants" not in data:
    data["quants"] = data.pop("quant_requests")
```

**Статус:** ✅ Код исправлен, требуется перезапуск

---

## 🔄 Исправление №2: Active quants пустые

**Проблема:**
- ГМ НЕ получает полные кванты в контексте
- Видит только список имен в synopsis
- active_quants = []

**Корневые причины:**

### 2.1. Маркеры = в БД (старые ходы)
**Симптом:**
```sql
requested_quants = '["=Лира=", "=Элина="]'  -- С маркерами
```

**Когда:** На следующем ходу:
```python
quants = memory_manager.get_quants_by_names(
    quant_names=["=Лира=", "=Элина="]  # НЕ найдет!
)
```

**Решение A:** Миграция БД (очистить старые requested_quants)
```sql
UPDATE turns 
SET requested_quants = REPLACE(REPLACE(requested_quants, '=', ''), '""', '"')
WHERE requested_quants LIKE '%=%';
```

**Решение B:** Очистка при загрузке
```python
# В orchestrator._get_active_quants()
requested_names = recent_turns[0].requested_quants
# Clean markers from loaded names
import re
requested_names = [re.sub(r'^=+|=+$', '', name) for name in requested_names]
```

---

### 2.2. ГМ запрашивает несуществующие кванты

**Симптом:**
```json
"quant_requests": ["Элина", "Кири", "Тренировочный_полигон"]
```

**Проблема:**
- Элина и Кири - НПЦ которых ГМ ТОЛЬКО ЧТО представил
- Их квантов ЕЩЕ НЕТ в БД (Quantizer не обработал)
- `get_quants_by_names()` не находит → active_quants = []

**Почему так происходит:**
- ГМ НЕ следует правилам промпта
- Должен запрашивать ТОЛЬКО из:
  - Active quants (текущие)
  - Synopsis list (существующие)
  - Linked quants (связанные)

**Решение:**
1. ✅ Промпт уже обновлен с строгими правилами
2. ⚠️ Но модель их игнорирует

**Дополнительная мера:**
```python
# В orchestrator._get_active_quants()
# После получения квантов
if len(quants) == 0 and len(requested_names) > 0:
    logger.warning(
        f"⚠️ Could not find any of requested quants: {requested_names}. "
        f"GM may be requesting non-existent quants!"
    )
```

---

## 🔍 Исправление №3: Синопсисы бесполезны

**Текущий формат (из терминала):**
```
- **Гильдия_Авантюристов**: [concept]
- **Лира**: [npc]
```

**Должно быть:**
```
- **Лира**: [npc] Магистр академии =Академия_Рендала= город =Рендал= отец =Отец_Лиры=
- **Гильдия_Авантюристов**: [concept] Главная гильдия =Рендал= лидер =Торгард= ранг =Серебро=
```

**Проверка:**
```sql
SELECT quant_id, synopsis FROM quants LIMIT 10;
```

**Если synopsis NULL или пусто:**
- Квантователь НЕ заполняет поле
- Промпт квантователя не работает

**Решение:**
Проверить `quantizer_agent.py` - создается ли synopsis при создании/обновлении квантов.

---

## 📝 Исправление №4: Суммаризатор не работает

**Проверка:**
```bash
grep "Running Summarizer" logs/plexmem_*.log
```

**Если нет:**
- Проверить trigger logic в `orchestrator.py`
- Проверить `should_trigger_summarization()`

---

## 🎯 Порядок действий:

### Шаг 1: Перезапуск (URGENT)
```bash
pkill -9 -f "python.*run"
fuser -k 8000/tcp
cd /home/pavel/dev/plexmem
python run_api.py &
sleep 3
python run_bot.py &
```

**Тест:** Сделать 1 ход и проверить:
- ✅ Ответ парсится (не JSON)
- ✅ Маркеры = удалены из quant_requests

---

### Шаг 2: Миграция БД (очистить старые маркеры)
```sql
UPDATE turns 
SET requested_quants = json_extract(
    json_replace(requested_quants, '$', 
        json_array(...cleaned...)), 
    '$'
)
WHERE requested_quants LIKE '%=%';
```

Или проще - добавить очистку при загрузке в orchestrator.

---

### Шаг 3: Проверить синопсисы
```sql
SELECT quant_id, synopsis FROM quants WHERE session_id = 29 LIMIT 20;
```

Если пусто → исправить quantizer.

---

### Шаг 4: Сравнить с master
```bash
git diff master feature/game-mechanics -- prompts/gm_system.md
```

Возможно старый промпт работал лучше.

---

## ❓ Вопросы Pavel:

1. **Можем перезапустить сейчас?**
   - Первый фикс готов (мапинг полей)

2. **Откатиться на master или чинить текущую ветку?**
   - Master работает стабильно?
   - Или нужны игровые механики?

3. **Синопсисы заполнены в БД?**
   ```bash
   sqlite3 plexmem.db "SELECT quant_id, synopsis FROM quants LIMIT 5;"
   ```

---

**Текущий статус:** 🟡 Первый фикс готов, требуется перезапуск и тестирование

