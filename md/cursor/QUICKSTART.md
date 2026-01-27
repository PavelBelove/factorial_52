# PlexMem - Быстрый старт

## Установка

### 1. Установить зависимости

```bash
# Создать виртуальное окружение
python -m venv venv

# Активировать
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate  # Windows

# Установить пакеты
pip install -r requirements.txt
```

### 2. Настроить конфигурацию

```bash
# Скопировать пример конфигурации
cp .env.example .env

# Отредактировать .env
nano .env  # или любой редактор
```

**Обязательно укажите:**
- `OPENROUTER_API_KEY` - ваш API ключ OpenRouter

### 3. Проверить установку

```bash
# Структура должна выглядеть так:
plexmem/
├── core/           # Ядро системы
├── data/           # БД (создастся автоматически)
├── logs/           # Логи
├── .env            # Ваша конфигурация
└── requirements.txt
```

## Запуск

### Вариант 1: Только API (для тестирования)

```bash
# Запустить API сервер
python run_api.py
```

Сервер запустится на `http://localhost:8000`

Документация API: `http://localhost:8000/docs`

### Вариант 2: Тест через скрипт

```bash
# В первом терминале запустить API
python run_api.py

# Во втором терминале запустить тест
python test_api.py
```

Тестовый скрипт создаст сессию и проведёт несколько ходов диалога.

## Пример использования API

### Создать сессию

```bash
curl -X POST http://localhost:8000/sessions \
  -H "Content-Type: application/json" \
  -d '{
    "platform_id": "user_123",
    "platform_type": "telegram",
    "session_type": "game"
  }'
```

Ответ:
```json
{
  "session_id": 1,
  "user_id": 1,
  "session_type": "game",
  "message": "Session created successfully"
}
```

### Отправить сообщение

```bash
curl -X POST http://localhost:8000/sessions/1/messages \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": 1,
    "message": "Привет! Я просыпаюсь в незнакомом месте."
  }'
```

Ответ:
```json
{
  "reply": "Ты открываешь глаза...",
  "turn_number": 1,
  "quants_used": [],
  "quants_requested": ["Локация_Старт", "Игрок"]
}
```

### Получить информацию о сессии

```bash
curl http://localhost:8000/sessions/1
```

### Получить кванты

```bash
curl http://localhost:8000/sessions/1/quants
```

### Получить историю

```bash
curl http://localhost:8000/sessions/1/history?limit=10
```

## Структура системы

```
┌─────────────┐
│   User      │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────┐
│       FastAPI Endpoint          │
└───────────┬─────────────────────┘
            │
            ▼
┌─────────────────────────────────┐
│     Turn Orchestrator           │
│  (координирует весь цикл)       │
└───┬─────────────────────────┬───┘
    │                         │
    ▼                         ▼
┌────────────┐         ┌──────────────┐
│ Context    │         │  Memory      │
│ Manager    │         │  Manager     │
└─────┬──────┘         └──────┬───────┘
      │                       │
      │    ┌──────────────────┤
      │    │                  │
      ▼    ▼                  ▼
┌─────────────┐      ┌─────────────┐
│  GM Agent   │      │  Database   │
│  (главный)  │      │  (SQLite)   │
└─────────────┘      └─────────────┘
      │
      │ (фоновые задачи)
      ▼
┌──────────────────┐  ┌──────────────┐
│  Quantizer       │  │ Summarizer   │
│  (кванты)        │  │ (история)    │
└──────────────────┘  └──────────────┘
```

## Логи

Логи сохраняются в папке `logs/`:
- Консоль: краткие сообщения
- Файл: полные логи, включая запросы/ответы LLM

## Troubleshooting

### Ошибка: "OpenRouter API key not set"
Проверьте, что в `.env` указан `OPENROUTER_API_KEY`

### Ошибка: "Module not found"
Установите зависимости: `pip install -r requirements.txt`

### База данных не создаётся
Проверьте права на запись в папку `data/`

### LLM не отвечает правильным JSON
Это нормально на старте. Система устойчива к ошибкам парсинга.
Проверьте логи для отладки.

## Следующие шаги

1. **Telegram бот** (фаза 2): интерфейс для общения через Telegram
2. **Модули**: игровая механика, эмоциональный слой
3. **Улучшение промптов**: настройка под конкретные сценарии

## Поддержка

Вопросы и баги: GitHub Issues

