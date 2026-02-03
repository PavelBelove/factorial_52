# План создания веб-интерфейса PlexMem

## Текущее состояние

### Что уже есть (можно использовать как есть)
- **FastAPI бэкенд** - полностью функциональный REST API
- **База данных** - SQLAlchemy ORM, SQLite (легко мигрировать на PostgreSQL)
- **Игровая логика** - оркестратор, агенты, механики карт/боя
- **Система миров** - 8 миров с Jinja2 шаблонами
- **Система сохранений** - 5 слотов на пользователя
- **Локализация** - ru/en

### Чего нет
- Аутентификация (сейчас только Telegram ID)
- Система платежей/биллинга
- Веб-интерфейс
- Rate limiting
- Мультиплатформенная синхронизация

---

## Архитектура решения

```
┌─────────────────────────────────────────────────────────────┐
│                        КЛИЕНТЫ                               │
├─────────────────────┬───────────────────────────────────────┤
│   Telegram Bot      │           PWA (Web)                    │
│   (aiogram)         │    React/Next.js + TailwindCSS        │
│   Бесплатный режим  │    Полный функционал + платежи        │
└─────────┬───────────┴───────────────┬───────────────────────┘
          │                           │
          └───────────┬───────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                    API Gateway                               │
│              (FastAPI + Auth Middleware)                     │
├─────────────────────────────────────────────────────────────┤
│  JWT Auth │ Rate Limiting │ CORS │ Request Validation        │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                  CORE BACKEND                                │
│            (существующий код)                                │
├─────────────────────────────────────────────────────────────┤
│  Orchestrator │ Agents │ Managers │ Mechanics                │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                   ДАННЫЕ                                     │
├──────────────┬──────────────┬───────────────────────────────┤
│  PostgreSQL  │    Redis     │         OpenRouter            │
│  (основная)  │  (сессии,    │         (LLM API)             │
│              │   кэш)       │                               │
└──────────────┴──────────────┴───────────────────────────────┘
```

---

## Стек технологий

### Backend (расширение существующего)
| Компонент | Технология | Причина |
|-----------|------------|---------|
| API Framework | FastAPI (уже есть) | Async, OpenAPI docs |
| База данных | PostgreSQL | Production-ready, JSON support |
| Кэш/сессии | Redis | JWT blacklist, rate limiting |
| Auth | JWT + OAuth2 | Стандарт индустрии |
| Миграции | Alembic | SQLAlchemy интеграция |

### Frontend (новый)
| Компонент | Технология | Причина |
|-----------|------------|---------|
| Framework | Next.js 14+ (App Router) | SSR, PWA support, SEO |
| UI | TailwindCSS + shadcn/ui | Быстрая разработка, ChatGPT-like |
| State | Zustand или TanStack Query | Простота, кэширование |
| PWA | next-pwa | Service worker, offline |
| Markdown | react-markdown | Рендер ответов AI |

### Платежи
| Провайдер | Для кого | Комиссия |
|-----------|----------|----------|
| ЮKassa | Россия | ~3.5% |
| Stripe | Мир | ~2.9% + $0.30 |
| CloudPayments | Россия | ~2.7% |

### Аутентификация OAuth
| Провайдер | Библиотека |
|-----------|------------|
| Telegram | aiogram + login widget |
| VK ID | vk-openapi |
| Яндекс ID | yandex-oauth |
| Email/Password | Собственная |

---

## Модули разработки

### Модуль 1: База и аутентификация

#### 1.1 Расширение БД
```sql
-- Новые таблицы
CREATE TABLE accounts (
    id UUID PRIMARY KEY,
    email VARCHAR(255) UNIQUE,
    password_hash VARCHAR(255),
    email_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP,
    last_login TIMESTAMP
);

CREATE TABLE oauth_connections (
    id UUID PRIMARY KEY,
    account_id UUID REFERENCES accounts,
    provider VARCHAR(50),  -- telegram, vk, yandex
    provider_user_id VARCHAR(255),
    access_token TEXT,
    refresh_token TEXT,
    UNIQUE(provider, provider_user_id)
);

CREATE TABLE subscriptions (
    id UUID PRIMARY KEY,
    account_id UUID REFERENCES accounts,
    plan VARCHAR(50),  -- free, basic, premium
    tokens_balance INT DEFAULT 0,
    tokens_used INT DEFAULT 0,
    expires_at TIMESTAMP,
    auto_renew BOOLEAN DEFAULT TRUE
);

CREATE TABLE payments (
    id UUID PRIMARY KEY,
    account_id UUID REFERENCES accounts,
    amount DECIMAL(10,2),
    currency VARCHAR(3),
    provider VARCHAR(50),  -- yookassa, stripe
    provider_payment_id VARCHAR(255),
    status VARCHAR(50),
    created_at TIMESTAMP
);

-- Миграция существующей таблицы users
ALTER TABLE users ADD COLUMN account_id UUID REFERENCES accounts;
```

#### 1.2 Auth Middleware
- JWT access tokens (15 min TTL)
- Refresh tokens (30 days, stored in Redis)
- OAuth2 flow для всех провайдеров
- Rate limiting: 60 req/min для бесплатных, 300 для платных

#### 1.3 Связь Telegram ↔ Web
```python
# При входе через Telegram в боте:
# 1. Генерируем одноразовый код
# 2. Пользователь вводит код на сайте
# 3. Связываем telegram user с web account

# Или через Telegram Login Widget на сайте
```

### Модуль 2: Биллинг

#### 2.1 Модель монетизации
```
FREE (бот):
- Чтение купленных глав
- Ограниченная генерация (5 ходов/день?)
- Нет сохранений

BASIC (500₽/мес или 100 токенов):
- ~500 ходов/месяц
- 3 слота сохранений
- Все миры

PREMIUM (1500₽/мес или 500 токенов):
- Безлимит ходов
- 5 слотов сохранений
- Приоритетная генерация
- Эксклюзивные миры

PAY-AS-YOU-GO:
- Пакеты токенов: 100₽ = 50 ходов
```

#### 2.2 Интеграция ЮKassa
```python
from yookassa import Payment, Configuration

Configuration.account_id = "..."
Configuration.secret_key = "..."

async def create_payment(account_id: str, amount: float):
    payment = Payment.create({
        "amount": {"value": str(amount), "currency": "RUB"},
        "confirmation": {"type": "redirect", "return_url": "..."},
        "capture": True,
        "metadata": {"account_id": account_id}
    })
    return payment.confirmation.confirmation_url
```

### Модуль 3: Фронтенд

#### 3.1 Структура страниц
```
/                   - Landing page
/login              - Вход (OAuth кнопки + email)
/register           - Регистрация
/app                - Главное приложение (чат)
/app/worlds         - Выбор мира
/app/saves          - Сохранения
/app/character      - Лист персонажа
/app/settings       - Настройки
/app/billing        - Подписка и платежи
/app/profile        - Профиль аккаунта
```

#### 3.2 Компоненты чата (ChatGPT-like)
```tsx
// Основной layout
<div className="flex h-screen">
  <Sidebar />           {/* Миры, сохранения, настройки */}
  <main className="flex-1 flex flex-col">
    <Header />          {/* Название мира, персонаж */}
    <MessageList />     {/* История сообщений */}
    <InputArea />       {/* Ввод + action buttons */}
  </main>
  <CharacterPanel />    {/* Статы, инвентарь (collapsible) */}
</div>
```

#### 3.3 PWA манифест
```json
{
  "name": "PlexMem - Интерактивные истории",
  "short_name": "PlexMem",
  "start_url": "/app",
  "display": "standalone",
  "theme_color": "#1a1a2e",
  "background_color": "#0f0f1a"
}
```

### Модуль 4: Синхронизация Bot ↔ Web

#### 4.1 Общий account_id
```python
# В таблице users добавляем account_id
# При связывании Telegram с Web:

def link_telegram_to_account(telegram_user_id: str, account_id: str):
    user = db.get_user_by_platform("telegram", telegram_user_id)
    user.account_id = account_id
    db.commit()
```

#### 4.2 Логика доступа в боте
```python
async def check_access(user: User) -> bool:
    if not user.account_id:
        return False  # Не привязан к аккаунту

    account = db.get_account(user.account_id)
    subscription = db.get_subscription(account.id)

    # Бесплатный режим: только чтение
    if subscription.plan == "free":
        return False  # Нельзя генерировать

    return subscription.tokens_balance > 0 or subscription.plan == "premium"
```

---

## Оценка трудозатрат (в человеко-неделях)

| Модуль | Описание | Оценка |
|--------|----------|--------|
| **1. База** | PostgreSQL миграция, Alembic, Redis | 1 неделя |
| **2. Auth** | JWT, OAuth (4 провайдера), middleware | 2 недели |
| **3. Биллинг** | ЮKassa/Stripe, подписки, токены | 2 недели |
| **4. API расширение** | Новые endpoints, rate limiting | 1 неделя |
| **5. Frontend base** | Next.js, layout, routing, auth UI | 2 недели |
| **6. Чат UI** | Сообщения, ввод, markdown, loading | 2 недели |
| **7. Панели** | Персонаж, инвентарь, сохранения | 1 неделя |
| **8. PWA** | Service worker, offline, install | 0.5 недели |
| **9. Биллинг UI** | Страницы оплаты, история | 1 неделя |
| **10. Тестирование** | E2E, интеграция, багфиксы | 2 недели |
| **11. Деплой** | CI/CD, Docker, production | 1 неделя |

**Итого: ~15-16 недель** при работе одного разработчика full-stack.

При распараллеливании (frontend + backend отдельно): **~8-10 недель**.

---

## Приоритеты (MVP → Full)

### MVP (8 недель)
1. Auth через email + Telegram Login Widget
2. Базовый чат интерфейс
3. Выбор мира
4. Интеграция ЮKassa (разовые платежи)
5. Синхронизация сохранений

### V1.0 (+4 недели)
1. VK ID, Яндекс ID
2. Подписки (recurring)
3. PWA полноценная
4. Лист персонажа
5. Responsive mobile

### V1.5 (+4 недели)
1. Stripe для международных
2. Расширенная аналитика
3. Реферальная программа
4. Push уведомления
5. Темы оформления

---

## Риски и решения

| Риск | Вероятность | Решение |
|------|-------------|---------|
| OAuth отказы (VK/Яндекс) | Средняя | Fallback на email |
| ЮKassa блокировка | Низкая | CloudPayments как backup |
| Высокая нагрузка LLM | Средняя | Rate limiting + очереди |
| Синхронизация конфликтов | Низкая | Last-write-wins + версионирование |

---

## Инфраструктура для production

```yaml
# docker-compose.yml
services:
  api:
    build: ./backend
    ports: ["8000:8000"]
    depends_on: [db, redis]

  web:
    build: ./frontend
    ports: ["3000:3000"]

  bot:
    build: ./telegram
    depends_on: [api]

  db:
    image: postgres:16
    volumes: [pgdata:/var/lib/postgresql/data]

  redis:
    image: redis:7-alpine

  nginx:
    image: nginx:alpine
    ports: ["80:80", "443:443"]
```

**Хостинг варианты:**
- VPS (Timeweb/Selectel): от 500₽/мес
- Managed (Yandex Cloud): от 3000₽/мес
- Vercel (frontend) + Railway (backend): ~$20/мес

---

## Следующие шаги

1. **Решить по стеку фронтенда** - Next.js vs Nuxt vs SvelteKit
2. **Выбрать платежную систему** - ЮKassa vs CloudPayments
3. **Определить модель монетизации** - подписки vs токены vs гибрид
4. **Создать репозиторий** для веб-части или монорепо
5. **Начать с Auth модуля** - фундамент для всего остального
