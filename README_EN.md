# Countdown

⏳ **Telegram bot for creating countdowns to important events with daily reminders**

![Python](https://img.shields.io/badge/Python-3.11+-blue) ![Aiogram](https://img.shields.io/badge/Aiogram-3.0+-green) ![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0+-red) ![License](https://img.shields.io/badge/License-MIT-purple)

[English](README_EN.md) • [Русский](README.md)

---

## Description

Countdown is a convenient Telegram bot for creating countdowns to important events: birthdays, vacations, movie premieres and more. The bot sends daily reminders at your chosen time to help you remember upcoming events.

## Features

- 🎉 **Create countdowns** — add events with dates and emojis
- 🔔 **Personal notifications** — choose when to receive daily reminders
- 📅 **Interactive calendar** — convenient date selection via buttons
- 🎨 **Beautiful interface** — inline buttons for all actions
- 🔁 **Recurring events** — configure countdowns to repeat annually
- 💾 **Save progress** — countdowns are stored between sessions
- ⚙️ **Full personalization** — flexible settings for each user

## Quick Start

### Requirements

- Python 3.11 or higher
- PostgreSQL 12+
- Telegram Bot Token

### Installation

1. Clone the repository:
```bash
git clone https://github.com/Mukller/countdown-bot.git
cd countdown-bot
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file with required variables:
```
BOT_TOKEN=your_telegram_bot_token
DATABASE_URL=postgresql+asyncpg://user:password@localhost/countdown_bot
```

4. Run database migrations:
```bash
alembic upgrade head
```

5. Run the bot:
```bash
python -m app.main
```

## Usage

### Main Commands

| Command | Description |
|---------|-------------|
| `/start` | Start the bot and show main menu |

### Main Menu

- **➕ Create countdown** — start creating a new countdown
- **📋 My countdowns** — view list of all countdowns
- **⚙️ Settings** — change notification time

### Creating a Countdown

1. Choose from suggested templates or create your own
2. Enter the name (e.g., "Birthday")
3. Select emoji from the provided options
4. Specify the event date using the interactive calendar
5. Choose if you need yearly repetition
6. Done! Your countdown is created and reminders will start

### Notifications

The bot sends daily reminders at your chosen time. By default, reminders arrive at 09:00. You can change this in settings:

1. Go to **⚙️ Settings**
2. Select **🔔 Notification time**
3. Choose a preset time or enter your own (in HH:MM format)

## Architecture

The project uses a modern technology stack:

- **Aiogram 3** — asynchronous Telegram bot framework
- **SQLAlchemy 2** — ORM for database operations
- **AsyncIO** — asynchronous programming
- **APScheduler** — scheduler for sending notifications
- **PostgreSQL** — reliable data storage

### Project Structure

```
app/
├── bot/
│   ├── handlers/      # Command and callback handlers
│   ├── states.py      # FSM states
│   └── middleware.py  # Database middleware
├── ui/
│   └── keyboards/     # Keyboards and buttons
├── services/          # Business logic
├── repositories/      # Data access
├── db/
│   ├── models/        # SQLAlchemy models
│   ├── migrations/    # Alembic migrations
│   └── session.py     # Session management
├── scheduler/         # APScheduler jobs
├── core/
│   ├── config.py      # Configuration
│   ├── logger.py      # Logging
│   └── constants.py   # Constants
└── main.py            # Entry point
```

## Contributing

You can help improve the project! To do this:

1. Fork the repository
2. Create a branch for your feature (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License — see [LICENSE.md](LICENSE.md) file for details.