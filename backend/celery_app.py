from celery import Celery
from celery.schedules import crontab

# Создаем приложение Celery
app = Celery('my_celery_project', broker='redis://localhost:6379/0')

# Настройки Celery
app.conf.update(
    result_backend='redis://localhost:6379/0',
    timezone='Europe/Moscow',  
    beat_schedule={
        'check-and-download-file-every-hour': {
            'task': 'tasks.check_for_changes',
            'schedule': crontab(minute=0, hour='*/1'),  # Запуск каждый час
        },
    }
)

app.autodiscover_tasks(['tasks'])

