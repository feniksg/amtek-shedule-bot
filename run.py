from multiprocessing import Process
from backend.celery_app import app
from tgbot.bot import bot
from settings import logger


def start_worker():
    logger.info("Воркер запущен")
    worker = app.Worker(loglevel='info')
    worker.start()

def start_beat():
    logger.info("Беат запущен")
    beat = app.Beat(loglevel='info')
    beat.run()

def start_bot():
    logger.info("Бот запущен")
    bot.infinity_polling()

if __name__ == '__main__':
    ...