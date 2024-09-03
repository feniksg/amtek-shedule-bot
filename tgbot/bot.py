from telebot import TeleBot
import settings

bot = TeleBot(settings.TOKEN)









def run_bot():
    settings.logger.info("Бот запущен")
    bot.infinity_polling()