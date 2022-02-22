import telebot
from decouple import config
from botrequests.bestdeal import bestdeal, best
from botrequests.highprice import highprice
from botrequests.lowprice import lowprice
from botrequests.history import history


token_bot: object = config('telegram_bot_token')
bot = telebot.TeleBot(token_bot)


user_dict = {}


class User:
    def __init__(self, name):
        self.name = name


# Handle '/help'
@bot.message_handler(content_types=['text'])
def send_welcome(message):
    if message.text == 'help':
        msg = bot.send_message(message.from_user.id, "Выберите команду (bestdeal, highprice, lowprice, history): ")
        bot.register_next_step_handler(msg, first)
    else:
        bot.send_message(message.from_user.id, 'Я тебя не понимаю. Напиши "help".')


def first(message):
    try:
        chat_id = message.chat.id
        name = message.from_user.username
        user = User(name)
        user_dict[chat_id] = user

        if message.text == 'bestdeal':
            msg_best = ' '.join(('Поздравляю', name, bestdeal()))
            msg = bot.send_message(chat_id, msg_best)
            bot.register_next_step_handler(msg, second)

        elif message.text == 'highprice':
            bot.send_message(chat_id, highprice())

        elif message.text == 'lowprice':
            bot.send_message(chat_id, lowprice())

        elif message.text == 'history':
            msg = ' '.join((history(), user_dict[message.chat.id].name))
            bot.send_message(chat_id, msg)

    except Exception as e:
        bot.send_message(message.from_user.id, str(e))


def second(message):
    if message.text == 'best':
        msg = best()
        bot.send_message(message.chat.id, msg)
    else:
        msg = 'Что-то'
        bot.send_message(message.chat.id, msg)


bot.infinity_polling()
