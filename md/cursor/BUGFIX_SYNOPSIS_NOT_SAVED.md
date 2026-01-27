# 🐛 BUGFIX: Synopsis и Aliases не сохранялись в БД

**Дата:** 2026-01-21  
**Статус:** ✅ Исправлено, требуется пересоздание квантов

---

## ❌ Проблема #1: Synopsis пустые

### Симптомы:
```
# Доступные кванты (последние обновления)

- **Гильдия_Авантюристов**: [concept]
- **UMP45**: [item]
- **Пол**: [npc]
```

**Что не так:**
- Вместо семантического описания - только тип `[npc]`
- Никаких =маркеров= для навигации
- ГМ не понимает что это за сущности

### Что должно быть:
```
# Доступные кванты (последние обновления)

- **Пол**: Исекай-герой, призыватель земного оружия в =Лесной_лагерь_лисиц=, спутник =Драг=
- **UMP45**: Призванный пистолет-пулемёт .45 калибра =Пола=, магические пули
- **Гильдия_Авантюристов**: организация в =Рендал=, регистрация =Пол= на ранг D
```

---

## 🔍 Диагностика:

### 1. Проверка БД:
```bash
sqlite3 data/plexmem.db "SELECT quant_id, type, synopsis FROM quants LIMIT 5;"
```

**Результат:**
```
Пол|npc|
Драг|npc|
UMP45|item|
```

❌ **synopsis = NULL** для всех квантов!

### 2. Проверка промпта квантователя:
```markdown
### 🔴 КРИТИЧНО: Synopsis - обязательное поле!

**Synopsis ДОЛЖЕН:**
1. Быть заполнен ВСЕГДА (не пусто, не null)
2. Содержать МАКСИМУМ маркеров на другие кванты
```

✅ Промпт правильный!

### 3. Проверка модели Quant:
```python
class Quant(BaseModel):
    synopsis: Optional[str] = Field(...)
    aliases: List[str] = Field(...)
```

✅ Модель имеет поля!

### 4. Проверка memory_manager:
```python
quant = Quant(
    id=quant_id,
    type=QuantType(data.get("type", "other")),
    synopsis=data.get("synopsis"),  # ✅ Передаётся
    ...
)
```

✅ Synopsis передаётся!

### 5. Проверка db_manager.create_quant():
```python
db_quant = QuantDB(
    session_id=session_id,
    quant_id=quant.id,
    type=quant.type.value,
    body=quant.body,
    links=quant.links,
    # ❌ synopsis=??? ОТСУТСТВУЕТ!
    # ❌ aliases=??? ОТСУТСТВУЕТ!
)
```

🔴 **ВОТ ПРОБЛЕМА!** Synopsis не записывается в БД!

---

## ✅ Исправление:

**Файл:** `core/database/db_manager.py`

**Было:**
```python
def create_quant(self, session_id: int, quant: Quant) -> QuantDB:
    db_quant = QuantDB(
        session_id=session_id,
        quant_id=quant.id,
        type=quant.type.value,
        body=quant.body,
        links=quant.links,
        # synopsis и aliases отсутствуют!
        created_at=quant.created_at,
        updated_at=quant.updated_at,
        is_game=quant.is_game
    )
```

**Стало:**
```python
def create_quant(self, session_id: int, quant: Quant) -> QuantDB:
    db_quant = QuantDB(
        session_id=session_id,
        quant_id=quant.id,
        type=quant.type.value,
        synopsis=quant.synopsis,  # ✅ Добавлено!
        body=quant.body,
        links=quant.links,
        aliases=quant.aliases,  # ✅ Добавлено!
        created_at=quant.created_at,
        updated_at=quant.updated_at,
        is_game=quant.is_game
    )
```

---

## ❌ Проблема #2: Summary не обновляется

### Диагностика:
```
2026-01-21 00:05:50 - core.orchestrator - INFO - Running Summarizer agent
2026-01-21 00:05:50 - core.orchestrator - INFO - Summarizer: not needed yet
```

**Проверка БД:**
```bash
sqlite3 data/plexmem.db "SELECT session_id, COUNT(*) FROM turns GROUP BY session_id;"
```

**Результат:**
```
1|4
2|5
```

**Причина:** Только 4-5 ходов, а `raw_turns_max = 7`  
**Вывод:** Суммаризатор не запускается, потому что ходов недостаточно.  
**Статус:** Это не баг, система работает как задумано.

---

## 🔧 Что делать дальше:

### 1. ✅ Перезапустить систему
Чтобы новый код начал работать.

### 2. ⚠️ Пересоздать кванты
**Два варианта:**

#### Вариант A: Удалить все кванты (начать игру заново)
```bash
sqlite3 data/plexmem.db "DELETE FROM quants WHERE session_id IN (1, 2);"
```

Квантователь создаст новые кванты с синопсисами при следующих ходах.

#### Вариант B: Обновить существующие кванты
Написать скрипт который:
1. Достанет все кванты из БД
2. Вызовет квантователь для генерации синопсисов
3. Обновит БД

---

## 📊 Ожидаемый результат:

После исправления ГМ будет видеть:

```markdown
# Доступные кванты (последние обновления)

- **Пол**: Исекай-герой 16 лет, призыватель =UMP45= и =Desert_Eagle=, спутник =Драг=, 
  спаситель =Рина= и =Лара=, гость =Лесной_лагерь_лисиц=
- **Драг**: Маленький дракончик-напарник =Пола=, телепатическая связь, советчик
- **UMP45**: Призванный пистолет-пулемёт .45 калибра =Пола=, магические пули, 
  использован против =Тролль_у_ручья=
- **Рина**: Рыжая лисья охотница из =Лесной_лагерь_лисиц=, сестра =Лара=, 
  любовница =Пол=, дочь =Эльза=
```

Теперь ГМ понимает:
- Кто такой Пол и какие у него способности
- Как связаны персонажи между собой
- Где происходят события

**🎮 Игра станет более связной и осмысленной!**

