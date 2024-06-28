import telebot
import threading
import cryptocurrency_handler, graph_handler, news_handler, setalert_handler, help_handler
import price_alerts
from api_tokens import TELEBOT_TOKEN

bot = telebot.TeleBot(TELEBOT_TOKEN)

@bot.message_handler(commands=['cryptocurrency'])
def handle_cryptocurrency(message):
    cryptocurrency_handler.handle_cryptocurrency_command(bot, message)

@bot.message_handler(commands=['graph'])
def handle_graph(message):
    graph_handler.handle_graph_command(bot, message)

@bot.message_handler(commands=['news'])
def handle_news(message):
    news_handler.handle_news_command(bot, message)

@bot.message_handler(commands=['setalert'])
def handle_setalert(message):
    setalert_handler.handle_setalert_command(bot, message)

@bot.message_handler(commands=['help'])
def handle_help(message):
    help_handler.handle_help_command(bot, message)

if __name__ == '__main__':
    bot.polling()

    # Start thread for checking price alerts
    alert_thread = threading.Thread(target=price_alerts.check_price_alerts, args=(bot,))
    alert_thread.daemon = True
    alert_thread.start()
