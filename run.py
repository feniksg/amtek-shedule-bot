from tgbot.bot import dp, bot
from settings import logger, ADMIN
import asyncio
from time import sleep

async def start_bot():
    logger.info("Бот запущен")
    print('Бот запущен')
    await dp.start_polling(bot)



if __name__ == '__main__':
    asyncio.run(start_bot())