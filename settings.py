import logging, os
from logging.handlers import RotatingFileHandler
from datetime import datetime
from dotenv import load_dotenv
from datetime import timezone, timedelta
load_dotenv()

DEBUG = os.getenv("DEBUG")=="TRUE"
if DEBUG:
    TOKEN = os.getenv("DEV_TOKEN")
else:
    TOKEN = os.getenv("TOKEN")
ADMIN = os.getenv("ADMIN")
TZ_MOSCOW = timezone(timedelta(hours=3))
URL = 'https://xn--d1auh.xn----8sbnlgibn8c8a2f.xn--p1ai/shedule/{}.png'


#region Logger

log_filename = datetime.now().astimezone(TZ_MOSCOW).strftime("files/logs/amtek_%Y-%m-%d.log")

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

handler = RotatingFileHandler(
    log_filename,  # Имя файла лога
    maxBytes=10485760,  # Максимальный размер файла в байтах (10 МБ)
    backupCount=7,  # Количество резервных файлов для хранения
    encoding='utf-8'  # Кодировка файла
)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

logger.addHandler(handler)

#endregion