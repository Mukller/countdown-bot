# Countdown Bot 🎯

Telegram-бот для персонального отсчёта дней до событий.

## Features

- ✨ Создание countdown до важных дат
- 📅 Ежедневные напоминания
- 🔁 Поддержка ежегодно повторяющихся событий
- 📱 Полностью кнопочный интерфейс
- 🌍 Русский язык

## Tech Stack

- **Bot Framework**: aiogram 3
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy 2.x
- **Scheduler**: APScheduler
- **Config**: Pydantic Settings
- **Containerization**: Docker

## Setup

### 1. Clone и зависимости

```bash
pip install -r requirements.txt
```

### 2. .env файл

```bash
cp .env.example .env
```

Отредактируйте `.env`:
```env
BOT_TOKEN=your_bot_token
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/countdown
LOG_LEVEL=INFO
```

### 3. Docker Compose

```bash
docker-compose up
```

### 4. Миграции (если нужны)

```bash
alembic upgrade head
```

## Project Structure

```
app/
├── bot/          # Handlers, FSM, middlewares
├── ui/           # Keyboards, calendar, messages
├── services/     # Business logic
├── repositories/ # Data access
├── db/           # Models, migrations, session
├── scheduler/    # APScheduler jobs
├── core/         # Config, logger, constants
└── main.py       # Bot entry point
```

## Development

### Run locally

```bash
python -m app.main
```

### Create migration

```bash
alembic revision --autogenerate -m "description"
```

## Phases

- ✅ Phase 1: Core Infrastructure
- ✅ Phase 2: User System
- ✅ Phase 3: Countdown Management
- ✅ Phase 4: Calendar Component
- ✅ Phase 5: Notifications
- ✅ Phase 6: Production (logging, error handling, deployment)
