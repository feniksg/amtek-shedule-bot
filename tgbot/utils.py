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

async def users_get_or_create() -> dict:
    if not await check_file(USERS_PATH):
        async with lock:
            async with aiofiles.open(USERS_PATH, mode='w+', encoding="utf-8") as file:
                await file.write(json.dumps({}, ensure_ascii=False, indent=4))
                return {}
    else:
        async with aiofiles.open(USERS_PATH, mode="r", encoding="utf-8") as file:
            content = await file.read()
            return json.loads(content)

async def check_file(filename):
    return await aiofiles.os.path.exists(filename)

async def check_user(id):
    users = await users_get_or_create()
    if str(id) in users.keys():
        return True
    else:
        return False
    
async def users_save(data):
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
