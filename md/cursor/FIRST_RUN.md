# PlexMem - Первый запуск

## Что готово

✅ Полное ядро системы памяти
✅ База данных (SQLite, готова к миграции на PostgreSQL)
✅ Три агента: ГМ, Квантователь, Суммаризатор
✅ Два менеджера: Память, Контекст
✅ FastAPI REST API
✅ Логирование и отладка
✅ Тестовый скрипт

## Что нужно для запуска

### 1. API ключ OpenRouter

Получите ключ на https://openrouter.ai/

### 2. Установка зависимостей

```bash
# Активируйте venv (если ещё не активирован)
source venv/bin/activate  # Linux/Mac

# Установите пакеты
pip install -r requirements.txt
```

### 3. Конфигурация

Откройте `.env` и укажите:

```bash
OPENROUTER_API_KEY=sk-or-v1-ваш-ключ-здесь
OPENROUTER_MODEL=x-ai/grok-2-1212
```

**Важно:** Модель должна поддерживать JSON mode или уметь генерировать структурированный JSON.

Рекомендуемые модели:
- `x-ai/grok-2-1212` (быстрая, хорошее качество)
- `anthropic/claude-3-sonnet` (высокое качество)
- `openai/gpt-4-turbo` (стабильная)

## Запуск системы

### Шаг 1: Запустить API сервер

```bash
python run_api.py
```

Вы должны увидеть:
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Шаг 2: Проверить работу

Откройте в браузере: http://localhost:8000/docs

Вы увидите Swagger UI с документацией API.

### Шаг 3: Первый тест

В **другом терминале**:

```bash
# Активируйте тот же venv
source venv/bin/activate

# Запустите тест
python test_api.py
```

Тест создаст сессию и проведёт несколько ходов диалога.

## Что происходит при первом запуске

1. **Создаётся БД**: `data/plexmem.db`
2. **Создаются таблицы**: users, sessions, quants, turns, summaries
3. **Запускается API сервер**: готов принимать запросы
4. **Логи**: `logs/plexmem_YYYYMMDD.log`

## Проверка работы

### Тест 1: Health check

```bash
curl http://localhost:8000/
```

Ожидается:
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "database": "connected"
}
```

### Тест 2: Создать сессию

```bash
curl -X POST http://localhost:8000/sessions \
  -H "Content-Type: application/json" \
  -d '{"platform_id": "test_user", "session_type": "game"}'
```

Ожидается:
```json
{
  "session_id": 1,
  "user_id": 1,
  "session_type": "game",
  "message": "Session created successfully"
}
```

### Тест 3: Первый ход

```bash
curl -X POST http://localhost:8000/sessions/1/messages \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": 1,
    "message": "Привет! Я просыпаюсь в незнакомом месте. Что вижу?"
  }'
```

Ожидается JSON с полями:
- `reply` - ответ ГМ
- `turn_number` - номер хода
- `quants_requested` - запрошенные кванты

## Проверка логов

```bash
# Смотреть логи в реальном времени
tail -f logs/plexmem_*.log

# Последние 50 строк
tail -50 logs/plexmem_*.log
```

В режиме DEBUG вы увидите:
- Полные запросы к LLM
- Полные ответы LLM
- Процесс обработки квантов
- Работу суммаризатора

## Типичные проблемы

### Ошибка: "OpenRouter API key not set"

**Решение:** Укажите ключ в `.env`:
```
OPENROUTER_API_KEY=sk-or-v1-...
```

### Ошибка: "Module 'core' not found"

**Решение:** Запускайте из корня проекта:
```bash
cd /home/pavel/dev/plexmem
python run_api.py
```

### ГМ не отвечает валидным JSON

**Это нормально на старте!** Система устойчива к ошибкам парсинга.

**Что делать:**
1. Проверьте логи - там будет raw ответ
2. Попробуйте другую модель
3. Модель "учится" на примерах в промпте

### База данных "locked"

SQLite не поддерживает высокую конкурентность.

**Решение:**
- Для тестов - перезапустите API
- Для продакшена - мигрируйте на PostgreSQL

## Следующие шаги

### 1. Понаблюдать за работой

Сделайте 10-15 ходов диалога, наблюдая за логами:
- Как ГМ запрашивает кванты
- Как квантователь создаёт память
- Как работает суммаризатор

### 2. Посмотреть созданные кванты

```bash
curl http://localhost:8000/sessions/1/quants | jq
```

Вы увидите структуру квантов, их связи, типы.

### 3. Настроить промпты

Отредактируйте `core/managers/context_manager.py` → `_default_base_prompt()`

Измените под ваш сценарий:
- Стиль повествования
- Правила игры
- Формат ответов

### 4. Экспериментировать с конфигом

В `.env` измените:
- `RAW_TURNS_MAX` - сколько сырых ходов держать
- `QUANTIZER_TRIGGER_TURNS` - как часто обновлять память
- `SUMMARY_SIZE_THRESHOLD` - когда переписывать сводку

### 5. Telegram бот (Фаза 2)

После проверки ядра можно добавить Telegram интерфейс.

## Полезные команды

### Очистить базу данных
```bash
rm data/plexmem.db
# При следующем запуске создастся новая
```

### Смотреть структуру БД
```bash
sqlite3 data/plexmem.db
.schema
.quit
```

### Экспорт квантов в JSON
```bash
curl http://localhost:8000/sessions/1/quants > quants_backup.json
```

### Мониторинг API
```bash
# Логи uvicorn в реальном времени
python run_api.py  # смотрите консоль
```

## Документация

- `README.md` - общий обзор
- `QUICKSTART.md` - быстрый старт
- `ARCHITECTURE.md` - детали архитектуры
- `md/concept.md` - теоретическая база
- API Docs: http://localhost:8000/docs

## Готово к разработке!

Ядро системы полностью функционально. Можно:
- Тестировать через API
- Настраивать промпты
- Добавлять модули
- Разрабатывать Telegram бот

**Удачи с PlexMem! 🚀**

