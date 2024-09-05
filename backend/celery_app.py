from celery import Celery
from celery.schedules import crontab
import sys
import os

# Создаем приложение Celery
app = Celery('amtek-schedule-bot', broker='redis://localhost:6379/0')

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# Настройки Celery
app.conf.update(
    result_backend='redis://localhost:6379/0',
    timezone='Europe/Moscow',  
    beat_schedule={
        'check-and-download-file-every-10-minutes': {
            'task': 'backend.tasks.check_for_changes',
            'schedule': crontab(minute='*/10'),  # Запуск каждые 10 минут
        },
        'check-auto-schedule-every-minute': {
            'task': 'backend.tasks.check_auto_schedule',
            'schedule': crontab(minute='*'),  # Запуск каждую минуту
        },
    }
)

app.autodiscover_tasks(['backend'])

