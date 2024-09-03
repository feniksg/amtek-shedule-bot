from celery import shared_task
from .utils import *
from settings import logger
import os

@shared_task
def notificate_update(msg=""):
    logger.info(msg)

@shared_task
def check_for_changes():
    week_dates = get_dates_this_week()
    for date in week_dates:
        if not os.path.exists(f'files/imgs/{date}.jpg'):
            if getTimeTable(date):
                cropTimeTable(date)
                notificate_update.delay(f"Появилось расписание на {date}")
        else:
            if getTempTimeTable(date):
                if not are_images_identical(f'files/imgs/{date}.jpg', 'files/imgs/temp.jpg'):
                    cropTimeTable(date, postfix="updated")
                    changed = check_changes_current(date, postfix="updated")
                    if changed:
                        for cls in changed:
                            notificate_update.delay(f"Для класса {cls} обновлено расписание на {date}")


        

