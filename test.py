import aiofiles.os
import asyncio, requests
from tgbot.bot import bot
from settings import ADMIN, TOKEN

def send_message(token, chat_id, text):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {
        'chat_id': chat_id,
        'text': text
    }
    response = requests.post(url, data=data)
    return response.json()

if __name__ == "__main__":
    send_message(TOKEN,ADMIN, 'hello')