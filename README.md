# AMTEK Schedule Bot

Telegram bot for working with school schedules and automated schedule notifications.

The bot allows students to select their class, view their schedule and configure automatic delivery of schedule information.

## Features

### Schedule

- Schedule for today
- Schedule for tomorrow
- Schedule for a selected date
- Class selection
- Automatic schedule delivery
- Multiple configurable delivery times
- Ability to receive today's or tomorrow's schedule automatically

### Notifications

- Enable / disable notifications
- Scheduled background tasks
- Automatic schedule processing

### Support

- Built-in support request command
- Forwarding user reports to the administrator

### Administration

- User statistics
- Notification statistics
- User list
- Broadcast messages
- Broadcast photos and videos
- Direct messages to individual users

## Tech Stack

- Python
- aiogram 3
- asyncio
- Celery
- Celery Beat
- Redis
- Flower
- BeautifulSoup
- Requests
- Pydantic
- python-dotenv

## Environment Variables

Create a .env file in the project root:

DEBUG=TRUE
DEV_TOKEN=your_development_bot_token
TOKEN=your_production_bot_token
ADMIN=your_telegram_user_id

Do not commit .env files or bot tokens to the repository.

## Installation

Create a virtual environment:

python -m venv venv

Activate it and install dependencies:

pip install -r req.txt

Redis must be available before starting Celery.

## Running

Start Celery worker:

celery -A backend.celery_app worker --loglevel=info

Start Celery Beat:

celery -A backend.celery_app beat --loglevel=info

Optional Flower monitoring:

celery -A backend.celery_app flower

Start the Telegram bot:

python run.py

## Status

The project was developed as a Telegram-based schedule automation system.
