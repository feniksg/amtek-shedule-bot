from celery import shared_task
from .utils import *
from settings import logger
import os, json, asyncio

@shared_task
def notificate_update(cls, date):
    with open("files/json/users.json", mode='r', encoding="utf-8") as file:
        users:dict = json.load(file)
    for user in users.items():
        user_id = int(user[0])
        curr_cls = user[1].get("class", None)
        update_notifications = user[1].get("update_notifications", None)
        if curr_cls == cls and update_notifications:
            send_notification_task.delay(user_id, f'Обновлено расписание на {date}!')
    
@shared_task
def notificate_add(date):
    with open("files/json/users.json", mode='r', encoding="utf-8") as file:
        users:dict = json.load(file)
    for user in users.items():
        user_id = int(user[0])
        update_notifications = user[1].get("update_notifications", None)
        if update_notifications:
            send_notification_task.delay(user_id, f'Добавлено расписание на {date}!')

@shared_task
def check_for_changes():
    week_dates = get_dates_this_week()
    for date in week_dates:
        if not os.path.exists(f'files/imgs/{date}.jpg'):
            if getTimeTable(date):
                cropTimeTable(date)
                notificate_add.delay(date)
        else:
            if getTempTimeTable(date):
                if not are_images_identical(f'files/imgs/{date}.jpg', 'files/imgs/temp.jpg'):
                    cropTimeTable(date, postfix="updated")
                    changed = check_changes_current(date, postfix="updated")
                    if changed:
                        for cls in changed:
                            notificate_update.delay(cls, date)
                    removeDir(f"files/imgs/croped_{date}")
                    os.rename(f"files/imgs/croped_{date}updated", f"files/imgs/croped_{date}")
                    os.remove(f'files/imgs/{date}.jpg')
                    os.rename(f'files/imgs/temp.jpg', f'files/imgs/{date}.jpg')

@shared_task
def send_notification_task(user_id, text):
    send_message(settings.TOKEN, user_id, text)

@shared_task
def send_timetable_task(user_id, mode):
    if mode == "today":
        photo = get_today_photo(user_id)
        date = datetime.now()
        weekday = date.weekday()
        date = date.strftime("%d.%m.%Y")
        match weekday:
            case 0:
                weekday = "Понедельник"
            case 1:
                weekday = "Вторник"
            case 2:
                weekday = "Среда"
            case 3:
                weekday = "Четверг"
            case 4:
                weekday = "Пятница"
            case 5:
                weekday = "Суббота"
            case 6:
                weekday = "Воскресенье"
        if photo:
            send_photo(settings.TOKEN, chat_id=user_id, photo_path=photo, caption=f"Расписание на сегодня. {date} ({weekday})")
    elif mode == "tomorrow":
        photo = get_tomorrow_photo(user_id)
        date = datetime.now() + timedelta(days=1)
        weekday = date.weekday()
        date = date.strftime("%d.%m.%Y")
        match weekday:
            case 0:
                weekday = "Понедельник"
            case 1:
                weekday = "Вторник"
            case 2:
                weekday = "Среда"
            case 3:
                weekday = "Четверг"
            case 4:
                weekday = "Пятница"
            case 5:
                weekday = "Суббота"
            case 6:
                weekday = "Воскресенье"
        if photo:
            send_photo(settings.TOKEN, chat_id=user_id, photo_path=photo, caption=f"Расписание на завтра. {date} ({weekday})")

@shared_task
def check_auto_schedule():
    time = datetime.now().astimezone(tz=settings.TZ_MOSCOW).strftime("%H:%M")
    with open("files/json/users.json", mode='r', encoding="utf-8") as file:
        users:dict = json.load(file)
    
    for user in users.items():
        user_id = int(user[0])
        auto_schedule = user[1].get("auto_schedule", [])
        if auto_schedule:
            for item in auto_schedule:
                value = item.get('value', None)
                if value == time:
                    mode = item.get('mode', None)
                    send_timetable_task.delay(user_id, mode)
        else:
            continue

@shared_task
def clean_old_day():
    yesterday = datetime.now().astimezone(settings.TZ_MOSCOW) - timedelta(days=1)
    yesterday = yesterday.strftime("%d.%m.%Y")
    removeDir(f"files/imgs/croped_{yesterday}")
    os.remove(f'files/imgs/{yesterday}.jpg')
        

