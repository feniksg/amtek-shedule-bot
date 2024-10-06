import requests, hashlib, os, json
from requests import get
from PIL import Image, ImageDraw
from os import path, mkdir, rmdir, remove, listdir
from datetime import datetime, timedelta
import settings
from bs4 import BeautifulSoup

#region CONSTS

CLASS_LIST = ['5А', '5Б', '5В', '5Г', '6А', '6Б', '6В', '6Г', '7А', '7Б', '7В', '7Г', 
'8А', '8Б', '8В', '8Г', '9А', '9Б', '9В', '9Г', '10А', '10Б', '10В', '10Г', 
'11А', '11Б', '11В', '11Г']

PIXEL_MAP_LONG = {
    '5А': (57,   286, 937,  953   ),
    '5Б': (937,  286, 1817, 953   ),
    '5В': (1817, 286, 2697, 953   ),
    '5Г': (2697, 286, 3577, 953   ), 
    '6А': (57,   1020, 937,  1687 ),
    '6Б': (937,  1020, 1817, 1687 ),
    '6В': (1817, 1020, 2697, 1687 ),
    '6Г': (2697, 1020, 3577, 1687 ), 
    '7А': (57,   1754, 937,  2421 ),
    '7Б': (937,  1754, 1817, 2421 ),
    '7В': (1817, 1754, 2697, 2421 ),
    '7Г': (2697, 1754, 3577, 2421 ), 
    '8А': (57,   2488, 937,  3230 ),
    '8Б': (937,  2488, 1817, 3230 ),
    '8В': (1817, 2488, 2697, 3230 ),
    '8Г': (2697, 2488, 3577, 3230 ),
    '9А': (57,   3297, 937,  4039 ),
    '9Б': (937,  3297, 1817, 4039 ),
    '9В': (1817, 3297, 2697, 4039 ),
    '9Г': (2697, 3297, 3577, 4039 ),
    '10А':(57,   4106, 937,  4847 ),
    '10Б':(937,  4106, 1817, 4847 ),
    '10В':(1817, 4106, 2697, 4847 ),
    '10Г':(2697, 4106, 3577, 4847 ),
    '11А':(57,   4914, 937,  5656 ),
    '11Б':(937,  4914, 1817, 5656 ),
    '11В':(1817, 4914, 2697, 5656 ),
    '11Г':(2697, 4914, 3577, 5656 ),
}

PIXEL_MAP = {
    '5А': (57,   286, 937,  953   ),
    '5Б': (937,  286, 1817, 953   ),
    '5В': (1817, 286, 2697, 953   ),
    '5Г': (2697, 286, 3577, 953   ), 
    '6А': (57,   1020, 937,  1687 ),
    '6Б': (937,  1020, 1817, 1687 ),
    '6В': (1817, 1020, 2697, 1687 ),
    '6Г': (2697, 1020, 3577, 1687 ), 
    '7А': (57,   1754, 937,  2421 ),
    '7Б': (937,  1754, 1817, 2421 ),
    '7В': (1817, 1754, 2697, 2421 ),
    '7Г': (2697, 1754, 3577, 2421 ), 
    '8А': (57,   2488, 937,  3155 ),
    '8Б': (937,  2488, 1817, 3155 ),
    '8В': (1817, 2488, 2697, 3155 ),
    '8Г': (2697, 2488, 3577, 3155 ),
    '9А': (57,   3222, 937,  3963 ),
    '9Б': (937,  3222, 1817, 3963 ),
    '9В': (1817, 3222, 2697, 3963 ),
    '9Г': (2697, 3222, 3577, 3963 ),
    '10А':(57,   4031, 937,  4772 ),
    '10Б':(937,  4031, 1817, 4772 ),
    '10В':(1817, 4031, 2697, 4772 ),
    '10Г':(2697, 4031, 3577, 4772 ),
    '11А':(57,   4839, 937,  5580 ),
    '11Б':(937,  4839, 1817, 5580 ),
    '11В':(1817, 4839, 2697, 5580 ),
    '11Г':(2697, 4839, 3577, 5580 ),
}

ERROR_CLASS_TEMPLATE = ["11А", "11Б", "11В"]

#endregion 

#region FolderFuncs
def createDir(keyDate:str): #создаёт папку
    if not path.exists(keyDate):
        mkdir(keyDate)

def clearDir(keyDate:str): #очищает папку (удаляет все файлы внутри)
    dir = f'{keyDate}/'
    for f in listdir(dir):
        remove(path.join(dir, f))

def removeDir(keyDate:str): #удаляет папку
    if path.exists(keyDate):
        clearDir(keyDate)
        rmdir(keyDate)

#endregion

#region PillowFuncs

def getTimeTable(date: str) -> bool:
    response = requests.get(
        url=settings.URL.format(date),
    )
    if response.status_code == 200:
        with open(f"files/imgs/{date}.jpg", 'wb') as file:
            file.write(response.content)
        return True
    else:
        settings.logger.error(f"{response.status_code} - {response.text}")
        return False
    
def cropTimeTable(date: str, postfix=""):
    if postfix == "":
        image = Image.open(f"files/imgs/{date}.jpg")
    else:
        image = Image.open(f"files/imgs/temp.jpg")
    my_path = f"files/imgs/croped_{date}{postfix}"
    
    if path.exists(my_path):
        removeDir(my_path)
        createDir(my_path)
    else:
        createDir(my_path)
    if image.height >= 5650: #Примерная высота
        pixel_map = PIXEL_MAP_LONG
        tech_short = image.crop((0, 286, 57, 953))
        tech_long = image.crop((0, 3297, 57, 4039))
    else:
        pixel_map = PIXEL_MAP
        tech_short = image.crop((0, 286, 57, 953))
        tech_long = image.crop((0, 3222, 57, 3963))
    for cls in CLASS_LIST:
        iCrop = image.crop(pixel_map[cls])
        if int(cls[:-1]) < 9:
            result_image = add_numbers_inner(iCrop, tech_short, is_short=True)
        else:
            result_image = add_numbers_inner(iCrop, tech_long, is_short=False)
        result_image.save(f'{my_path}/{date}_{cls}.png')

def add_numbers_inner(iCrop, tech: Image, is_short=True):
    if is_short:
        toRet = Image.new('RGBA', (880+57,667))
    else:
        toRet = Image.new('RGBA', (880+57,741))
    toRet.paste(tech, (0,0))
    toRet.paste(iCrop, (56,0))
    idraw = ImageDraw.Draw(toRet)
    if is_short:
        idraw.rectangle((55,0,56,666), fill="black")
    else:
        idraw.rectangle((55,0,56,741), fill="black")
    return toRet

def getTempTimeTable(date: str) -> bool:
    response = requests.get(
        url=settings.URL.format(date),
    )
    if response.status_code == 200:
        with open(f"files/imgs/temp.jpg", 'wb') as file:
            file.write(response.content)
        return True
    else:
        settings.logger.error(f"{response.status_code} - {response.text}")
        return False

def image_hash(image_path):
    try:
        with Image.open(image_path) as img:
            # Приводим изображение к формату, удобному для хэширования
            img = img.convert('RGB')
            # Преобразуем изображение в байты
            img_bytes = img.tobytes()
            # Создаем хэш изображения
            return hashlib.md5(img_bytes).hexdigest()
    except FileNotFoundError:
        print(f"Ошибка: Файл {image_path} не найден.")
        return None
    except IOError as e:
        print(f"Ошибка при открытии файла {image_path}: {e}")
        return None

def are_images_identical(image1_path, image2_path):
    # Получаем хэши изображений
    hash1 = image_hash(image1_path)
    hash2 = image_hash(image2_path)
    
    # Если одно из изображений не удалось открыть, считаем их различными
    if hash1 is None or hash2 is None:
        return False
    
    # Сравниваем хэши
    return hash1 == hash2

def check_changes_current(date, postfix="") -> list:
    path_to_updated = f"files/imgs/croped_{date}{postfix}"
    path_to_now = f"files/imgs/croped_{date}"
    res = []
    for cls in CLASS_LIST:
        if os.path.exists(f'{path_to_now}/{date}_{cls}.png'):
            if not are_images_identical(f'{path_to_now}/{date}_{cls}.png', f'{path_to_updated}/{date}_{cls}.png',):
                res.append(cls)
    return res
#endregion

#region Other
def get_dates_this_week():
    today = datetime.now().date()
    week_dates = [(today + timedelta(days=i)).strftime("%d.%m.%Y") for i in range(7)]
    return week_dates



def prepare_data(cls, day):
    with open(f'files/json/{day}_converted.json', mode='r', encoding='utf-8') as file:
        data = json.load(file)
    cls_data = data.get(cls, None)
    if cls:
        result = ""
        for item in cls_data.items():
            lesson_data = item[1].split("&")
            result+=f'{item[0]}. '
            if lesson_data[0] == '-':
                result+="⬜\n"
            else:
                result+=lesson_data[0] + ' '
                if lesson_data[1] != '-' and lesson_data[2] == '-':
                    result+=lesson_data[1]+'\n'
                elif lesson_data[1] != '-' and lesson_data[2] != '-':
                    result+=lesson_data[1]+'/'+lesson_data[2]+"\n"
                else:
                    result+='\n'                    
        return result
    return ""


def send_photo(token, chat_id, photo_path, caption=None):
    url = f"https://api.telegram.org/bot{token}/sendPhoto"
    files = {'photo': open(photo_path, 'rb')}
    data = {'chat_id': chat_id}
    if caption:
        data['caption'] = caption
    
    response = requests.post(url, files=files, data=data)
    return response.json()

def send_message(token, chat_id, text, parse_mode=""):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {
        'chat_id': chat_id,
        'text': text
    }
    if parse_mode:
        data['parse_mode'] = parse_mode
    response = requests.post(url, data=data)
    return response.json()

def get_today_photo(user_id):
    users = get_users()
    user = users[str(user_id)]
    cls = user.get('class', None)
    if cls:
        day = datetime.now().astimezone(settings.TZ_MOSCOW)
        day = day.strftime("%d.%m.%Y")
        if os.path.exists(f'files/json/{day}_converted.json'):
            return prepare_data(cls, day)
        return None
    return None

def get_tomorrow_photo(user_id):
    users = get_users()
    user = users[str(user_id)]
    cls = user.get('class', None)
    if cls:
        day = datetime.now().astimezone(settings.TZ_MOSCOW) + timedelta(days=1)
        day = day.strftime("%d.%m.%Y")
        if os.path.exists(f'files/json/{day}_converted.json'):
            return prepare_data(cls, day)
        return None
    return None

def get_users():
    with open('files/json/users.json', 'r', encoding='utf-8') as file:
        users = json.load(file)
    return users

#endregion

#region HTM processing

def get_avaible_files():
    response = get(url=settings.SCHEDULE_URL)
    if response.status_code == 200:
        a_links = []
        html = response.text
        soup = BeautifulSoup(html, 'lxml')
        table = soup.find("table")
        rows = table.find_all('tr')
        for row in rows:
            cells = row.find_all('td')
            for cell in cells:
                links = cell.find_all('a')
                for link in links:
                    href = link.get('href')
                    if href != "/":
                        a_links.append(href)
        return a_links
    return []
        
def get_file_by_name(name: str):
    if '.' in name:
        if name.split('.')[-1] == 'htm':
            html = get(url=f"{settings.SCHEDULE_URL}{name}").text
            return process_htm_file(html, name)
        if name.split('.')[-1] == 'jpg':
            ...

def process_htm_file(html, name):
    data = {}
    soup = BeautifulSoup(html, 'html.parser')
    table = soup.find("table")
    rows = table.find_all('tr')[5:]
    current_classes = []
    for row in rows:
        cells = row.find_all("td")
        match len(cells):
            case 6 | 8:
                current_classes = []
                for cell in cells:
                    value = cell.get_text().strip()
                    if value:
                        current_classes.append(value)
                        data[value] = {}
            case 14:
                if current_classes == ERROR_CLASS_TEMPLATE:
                    current_classes.append('11Г')
                    data['11Г'] = {}
                lesson_number = cells[0].get_text().strip()
                if lesson_number:
                    for cls in current_classes:
                        data[cls][lesson_number] = ""
                    clear_lesson_data = cells[1:-1]
                    for i in range(len(clear_lesson_data)):
                        current_class_index = i // 3
                        if current_class_index <= len(current_classes)-1:
                            text = clear_lesson_data[i].get_text().strip().replace('\r\n ', '')
                            text.replace('\r\n', '')
                            if text == "":
                                text = "-"
                            if data[current_classes[current_class_index]][lesson_number] != "":
                                data[current_classes[current_class_index]][lesson_number] += "&" + f'{text}'
                            else:
                                data[current_classes[current_class_index]][lesson_number] += f'{text}'


    # with open(f'files/json/{name[:-4]}_converted.json', 'w+', encoding='utf-8') as file:
    #     json.dump(data, file, ensure_ascii=False, indent=2)
    return data, name[:-4]


#endregion

if __name__ == "__main__":
    ...