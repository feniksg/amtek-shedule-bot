import os, json, asyncio, aiofiles
import aiofiles.os
from datetime import datetime, timedelta
from aiogram.types import Message, FSInputFile
import settings

USERS_PATH='files/json/users.json'

lock = asyncio.Lock()

def escape_markdown(text: str) -> str:
    """
    Экранирует специальные символы в тексте для использования в Markdown.
    """
    markdown_special_chars = r'\_*[]()~`>#+-=|{}.!'
    for char in markdown_special_chars:
        text = text.replace(char, f'\\{char}')
    return text

#region GET USERS

async def users_get_or_create() -> dict:
    """
    Возвращает или создаёт словарь с пользователями. ID пользователя - ключ
    """
    if not await check_file(USERS_PATH):
        async with lock:
            async with aiofiles.open(USERS_PATH, mode='w+', encoding="utf-8") as file:
                await file.write(json.dumps({}, ensure_ascii=False, indent=4))
                return {}
    else:
        async with aiofiles.open(USERS_PATH, mode="r", encoding="utf-8") as file:
            content = await file.read()
            return json.loads(content)

#region File

async def check_file(filename):
    """
    Ассинхронная проверка - есть ли файл
    """
    return await aiofiles.os.path.exists(filename)

async def check_user(id):
    """
    Проверяет есть ли пользователь в системе
    """
    users = await users_get_or_create()
    if str(id) in users.keys():
        return True
    else:
        return False
    
async def users_save(data):
    """
    Сохраняет словарь с пользователями
    """
    async with lock:
        async with aiofiles.open(USERS_PATH, mode="w+", encoding="utf-8") as file:
            await file.write(json.dumps(data, ensure_ascii=False, indent=4))

async def add_user(message:Message):
    users = await users_get_or_create()
    new_user = {
        'username': message.from_user.username,
        'first_name': message.from_user.first_name,
        'last_name': message.from_user.last_name,
        'class': None,
        'update_notifications': False,
        'auto_schedule': [],
    }
    users[message.from_user.id] = new_user
    await users_save(users)

async def set_class(id, class_name):
    users = await users_get_or_create()
    users[str(id)]['class'] = class_name
    await users_save(users)

async def toggle_notifications(id):
    users = await users_get_or_create()
    users[str(id)]['update_notifications'] = not users[str(id)]['update_notifications']
    await users_save(users)
    return users[str(id)]['update_notifications']

async def get_today_schedule(user_id):
    users = await users_get_or_create()
    user = users[str(user_id)]
    cls = user.get('class', None)
    if cls:
        today = datetime.now().astimezone(settings.TZ_MOSCOW)
        if today.weekday() == 6:
            return 'sunday'
        today = today.strftime("%d.%m.%Y")
        if await aiofiles.os.path.exists(f'files/imgs/croped_{today}/{today}_{cls}.png'):
            return FSInputFile(f'files/imgs/croped_{today}/{today}_{cls}.png')
        return 'no-data'
    return None

async def get_tomorrow_schedule(user_id):
    users = await users_get_or_create()
    user = users[str(user_id)]
    cls = user.get('class', None)
    if cls:
        tomorrow = datetime.now().astimezone(settings.TZ_MOSCOW) + timedelta(days=1) 
        if tomorrow.weekday() == 6:
            return 'sunday'
        tomorrow = tomorrow.strftime("%d.%m.%Y")
        if await check_file(f'files/imgs/croped_{tomorrow}/{tomorrow}_{cls}.png'):
            return FSInputFile(f'files/imgs/croped_{tomorrow}/{tomorrow}_{cls}.png')
        return 'no-data'
    return None

async def get_schedule_by_date(date, user_id):
    users = await users_get_or_create()
    user = users[str(user_id)]
    cls = user.get('class', None)
    if cls:
        if await check_file(f"files/imgs/croped_{date}/{date}_{cls}.png"):
            return FSInputFile(f'files/imgs/croped_{date}/{date}_{cls}.png')
        return 'no-data'
    return None

async def get_available_dates():
    dirs = await aiofiles.os.listdir('files/imgs/')
    res = []
    for dir in dirs:
        if dir.startswith("croped_"):
            if not 'updated' in dir:
                res.append(str(dir))
    for item in res:
        res[res.index(item)] = item.replace("croped_", "")
    res = sorted(res)

    for item in res:
        str_weekday = ''
        date = datetime.strptime(item, "%d.%m.%Y")
        match date.weekday():
            case 0:
                str_weekday = "Понедельник"
            case 1:
                str_weekday = "Вторник"
            case 2:
                str_weekday = "Среда"
            case 3:
                str_weekday = "Четверг"
            case 4:
                str_weekday = "Пятница"
            case 5:
                str_weekday = "Суббота"
            case 6:
                str_weekday = "Воскресенье"
        res[res.index(item)] = (item, str_weekday)
    return res

async def get_times_by_user(user_id):
    users = await users_get_or_create()
    user = users[str(user_id)]
    auto_schedule = user.get('auto_schedule', [])
    return auto_schedule

async def write_auto_schedule(data:dict, user_id):
    users = await users_get_or_create()
    user = users[str(user_id)]
    auto_schedule = user.get('auto_schedule', [])
    auto_schedule.append(data)
    users[str(user_id)]['auto_schedule'] = auto_schedule
    await users_save(users)

async def delete_time_by_index(user_id, index_to_delete):
    users = await users_get_or_create()
    user = users[str(user_id)]
    auto_schedule = user.get("auto_schedule", [])
    if len(auto_schedule) >= index_to_delete+1:
        del users[str(user_id)]['auto_schedule'][index_to_delete]
    await users_save(users)

async def get_stats():
    users = await users_get_or_create()
    users_count = len(users.keys())
    notifications_count = 0
    for key in users.keys():
        if users[key]['update_notifications']:
            notifications_count+=1
    
    class_count = {}

    users_list = []

    for user_id, user_data in users.items():
        class_name = user_data.get("class")
        username = user_data.get("username")
        first_name = user_data.get("first_name")
        users_list.append((username, first_name))
        if class_name:
            # Проверяем, подходит ли класс под нужный диапазон (5-11 классы, А-Г буквы)
            grade = class_name[:-1]
            letter = class_name[-1]
            if grade.isdigit() and 5 <= int(grade) <= 11 and letter in "АБВГ":
                if class_name in class_count:
                    class_count[class_name] += 1
                else:
                    class_count[class_name] = 1

    sorted_class_count = dict(sorted(class_count.items(), key=lambda item: item[1], reverse=True))
    return {
        "count": users_count,
        "notification": notifications_count,
        "persent": round(notifications_count/users_count*100, 2),
        "class_count": sorted_class_count,
        "users_list": users_list
    }

async def get_users_for_broadcast():
    users = await users_get_or_create()
    return list(users.keys())