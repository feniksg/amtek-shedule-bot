Запуск:

celery -A backend.celery_app worker --loglevel=info
celery -A backend.celery_app beat --loglevel=info
celery -A backend.celery_app flower
python run.py