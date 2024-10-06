from requests import get
from bs4 import BeautifulSoup
import json

MAIN_URL = 'https://xn--d1auh.xn----8sbnlgibn8c8a2f.xn--p1ai/shedule/'

error_class_map = ["11А", "11Б", "11В"]



def get_avaible_files():
    response = get(url=MAIN_URL)
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
            html = get(url=f"{MAIN_URL}{name}").text
            process_htm_file(html, name)
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
                if current_classes == error_class_map:
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


    with open(f'files/json/{name[:-4]}_converted.json', 'w+', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=2)



if __name__ == "__main__":
    a_links = get_avaible_files()
    for link in a_links:
        get_file_by_name(link)
