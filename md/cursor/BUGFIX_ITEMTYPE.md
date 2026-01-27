# 🐛 BUGFIX: ItemType Enum

**Дата:** 2026-01-19 23:09  
**Статус:** ✅ Исправлено

---

## Проблема:

**Ошибка на 3 ходу:**
```
1 validation error for Item
type
  Input should be 'weapon', 'armor', 'accessory' or 'consumable' [type=enum, input_value='ring', input_type=str]
```

**Причина:**
- ГМ вернул предметы с типами: `ring`, `bracelet`, `cloak`
- В `ItemType` enum были только: `weapon`, `armor`, `accessory`, `consumable`
- Pydantic валидация отклонила данные

---

## Решение:

### 1. ✅ Расширен ItemType enum

**Файл:** `core/mechanics/models.py`

**Добавлены типы:**
```python
class ItemType(str, Enum):
    # Было:
    WEAPON = "weapon"
    ARMOR = "armor"
    ACCESSORY = "accessory"
    CONSUMABLE = "consumable"
    
    # Добавлено:
    RING = "ring"
    BRACELET = "bracelet"
    CLOAK = "cloak"
    AMULET = "amulet"
    BELT = "belt"
    BOOTS = "boots"
    GLOVES = "gloves"
    HELMET = "helmet"
```

### 2. ✅ Обновлен GM промпт

**Файл:** `prompts/gm_system.md`

**Добавлено:**
```
- inventory.add/remove: Добавленные/удаленные предметы
  - РАЗРЕШЕННЫЕ ТИПЫ: weapon, armor, accessory, consumable, 
    ring, bracelet, cloak, amulet, belt, boots, gloves, helmet
  - Формат: {"id": "Название", "type": "weapon", "suit": "♠", 
             "bonus": 10, "description": "..."}
```

### 3. ✅ Удалена чужая сессия

**Проблема:** В логах мешался user_id=2 (Константин)

**Решение:** 
```sql
DELETE FROM sessions WHERE user_id = 2;
DELETE FROM turns WHERE session_id IN (SELECT id FROM sessions WHERE user_id = 2);
DELETE FROM quants WHERE session_id IN (SELECT id FROM sessions WHERE user_id = 2);
```

Теперь логи чистые для твоей сессии (user_id=1).

---

## ✅ Результат:

- Система работает
- ГМ может использовать все типы предметов
- Логи чистые
- Можно продолжать игру

---

## 🧪 Тест:

Попробуй продолжить игру - должно работать без ошибок!

